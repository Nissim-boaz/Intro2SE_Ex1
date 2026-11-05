"""
gui.py - Graphical interface for the 3D plane projection tool.

Cross-platform desktop application using Python's built-in tkinter.
Allows selecting files via dialogs, tracking progress, and running projections.

Launch:
    python gui.py
"""

from __future__ import annotations

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Ensure src/ is importable from application directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.volume_loader import load
from src.csv_parser import parse_entries
from src.projector import project
from src.video_writer import write


class ProjectionApp:
    """Main application window for the 3D plane projection desktop tool."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize window geometry, style themes, and interactive UI controls."""
        self.root = root
        self.root.title("3D Plane Projection Tool")
        self.root.resizable(False, False)

        # -- File Path Variables --------------------------------------
        self.nrrd_path = tk.StringVar()
        self.csv_path = tk.StringVar()
        self.mp4_path = tk.StringVar()

        # -- UI Layout Configuration ----------------------------------
        pad = {"padx": 12, "pady": 6}

        # Header Title
        title = tk.Label(root, text="3D Plane Projection", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(16, 8))

        # NRRD file selection
        tk.Label(root, text="NRRD Volume File:").grid(row=1, column=0, sticky="w", **pad)
        tk.Entry(root, textvariable=self.nrrd_path, width=45).grid(row=1, column=1, **pad)
        tk.Button(root, text="Browse...", command=self._browse_nrrd).grid(row=1, column=2, **pad)

        # CSV file selection
        tk.Label(root, text="Planes CSV File:").grid(row=2, column=0, sticky="w", **pad)
        tk.Entry(root, textvariable=self.csv_path, width=45).grid(row=2, column=1, **pad)
        tk.Button(root, text="Browse...", command=self._browse_csv).grid(row=2, column=2, **pad)

        # Output MP4 destination
        tk.Label(root, text="Output Video (.mp4):").grid(row=3, column=0, sticky="w", **pad)
        tk.Entry(root, textvariable=self.mp4_path, width=45).grid(row=3, column=1, **pad)
        tk.Button(root, text="Save As...", command=self._browse_mp4).grid(row=3, column=2, **pad)

        # Separator Line
        ttk.Separator(root, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="ew", pady=8)

        # Progress bar
        self.progress = ttk.Progressbar(root, length=400, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, **pad)

        # Status label
        self.status_var = tk.StringVar(value="Ready. Select files and click Run.")
        tk.Label(root, textvariable=self.status_var, fg="gray").grid(row=6, column=0, columnspan=3, **pad)

        # Action Run button
        self.run_btn = tk.Button(
            root, text=">  Run Projection", font=("Helvetica", 13, "bold"),
            bg="#4CAF50", fg="white", command=self._start_run, height=2, width=20
        )
        self.run_btn.grid(row=7, column=0, columnspan=3, pady=(4, 16))

    # -- File Dialog Handlers -----------------------------------------

    def _browse_nrrd(self) -> None:
        """Open a file browser dialog to select an input .nrrd volume file."""
        path = filedialog.askopenfilename(
            title="Select NRRD Volume File",
            filetypes=[("NRRD files", "*.nrrd"), ("All files", "*.*")]
        )
        if path:
            self.nrrd_path.set(path)

    def _browse_csv(self) -> None:
        """Open a file browser dialog to select a plane definitions .csv file."""
        path = filedialog.askopenfilename(
            title="Select Planes CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            self.csv_path.set(path)

    def _browse_mp4(self) -> None:
        """Open a file save dialog to specify the target .mp4 video destination."""
        path = filedialog.asksaveasfilename(
            title="Save Output Video As",
            defaultextension=".mp4",
            filetypes=[("MP4 video", "*.mp4")]
        )
        if path:
            self.mp4_path.set(path)

    # -- Pipeline Execution -------------------------------------------

    def _start_run(self) -> None:
        """
        Validate file paths and launch the projection pipeline in a background thread.
        Keeps the UI responsive and animates the progress bar during computation.
        """
        nrrd = self.nrrd_path.get().strip()
        csv_f = self.csv_path.get().strip()
        mp4 = self.mp4_path.get().strip()

        if not nrrd:
            messagebox.showwarning("Missing File", "Please select an NRRD volume file.")
            return
        if not csv_f:
            messagebox.showwarning("Missing File", "Please select a CSV planes file.")
            return
        if not mp4:
            messagebox.showwarning("Missing File", "Please choose an output MP4 path.")
            return

        if not os.path.isfile(nrrd):
            messagebox.showerror("File Not Found", f"NRRD file not found:\n{nrrd}")
            return
        if not os.path.isfile(csv_f):
            messagebox.showerror("File Not Found", f"CSV file not found:\n{csv_f}")
            return

        # Disable button during execution
        self.run_btn.config(state="disabled")
        self.progress["value"] = 0

        # Run pipeline in a daemon background thread
        thread = threading.Thread(target=self._run_pipeline, args=(nrrd, csv_f, mp4), daemon=True)
        thread.start()

    def _run_pipeline(self, nrrd_path: str, csv_path: str, mp4_path: str) -> None:
        """
        Execute the full projection pipeline and update GUI progress asynchronously.

        Algorithm:
            1. Load 3D volume using load(nrrd_path) and extract min/max intensity range.
            2. Parse plane rows from CSV using parse_entries(csv_path).
            3. Project each plane onto 2D image via project() and update progress bar.
            4. Compile video with error slides and annotations via write().
            5. Display success dialog with throughput (FPS) and runtime metrics.
        """
        try:
            # Step 1: Load volume
            self._update_status("Loading NRRD volume...")
            M = load(nrrd_path)
            vmin, vmax = int(M.min()), int(M.max())
            self._update_progress(10)

            # Step 2: Parse CSV
            self._update_status("Parsing CSV planes...")
            entries = parse_entries(csv_path)
            if not entries:
                self._show_error("No plane rows found in the CSV file.")
                return
            self._update_progress(20)

            # Step 3: Project each plane
            total = len(entries)
            valid_count = sum(1 for e in entries if e["status"] == "valid")
            frames = []
            labels = []
            errors = []
            t_start = time.perf_counter()

            for i, entry in enumerate(entries):
                p_idx = entry["plane_idx"]
                r_num = entry["row_num"]

                if entry["status"] == "valid":
                    frame = project(M, entry["plane"])
                    frames.append(frame)
                    labels.append(f"Plane {p_idx} (Row {r_num})")
                    errors.append(None)
                else:
                    frames.append(None)
                    labels.append(f"Plane {p_idx} (Row {r_num})")
                    errors.append(entry.get("error"))

                pct = 20 + int(60 * (i + 1) / total)
                self._update_progress(pct)
                self._update_status(f"Processing plane {i+1}/{total}...")

            t_proj = time.perf_counter() - t_start
            fps = valid_count / t_proj if t_proj > 0 else float("inf")
            self._update_progress(85)

            # Step 4: Write video (smooth playback at 30 FPS)
            self._update_status("Writing MP4 video with annotations...")
            write(frames, mp4_path, fps=30, vmin=vmin, vmax=vmax, labels=labels, errors=errors)
            self._update_progress(100)

            # Display final success summary
            result = (
                f"Done!\n\n"
                f"Total rows in CSV: {total}\n"
                f"Valid planes: {valid_count}\n"
                f"Invalid planes: {total - valid_count}\n"
                f"Projection time: {t_proj:.3f} s\n"
                f"FPS: {fps:.1f}\n"
                f"{'[PASS] PASS' if fps >= 30 else '[FAIL] FAIL'} (requirement: >=30 FPS)\n\n"
                f"Video saved to:\n{mp4_path}"
            )
            self._update_status(f"[PASS] Done - {fps:.1f} FPS - {total} frames")
            self.root.after(0, lambda: messagebox.showinfo("Success", result))

        except Exception as e:
            self._show_error(str(e))

        finally:
            self.root.after(0, lambda: self.run_btn.config(state="normal"))

    # -- Thread-safe UI Helpers ---------------------------------------

    def _update_status(self, text: str) -> None:
        """Safely schedule a text update on the GUI status label."""
        self.root.after(0, lambda: self.status_var.set(text))

    def _update_progress(self, value: int) -> None:
        """Safely schedule a progress bar percentage update on the GUI."""
        self.root.after(0, lambda: self.progress.configure(value=value))

    def _show_error(self, msg: str) -> None:
        """Display an error dialog and reset the application state."""
        self.root.after(0, lambda: messagebox.showerror("Error", msg))
        self.root.after(0, lambda: self.status_var.set("Error occurred."))
        self.root.after(0, lambda: self.run_btn.config(state="normal"))


# -- Application Launch -----------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectionApp(root)
    root.mainloop()
