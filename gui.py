"""
gui.py - Graphical interface for the 3D plane projection tool.

Cross-platform (macOS, Windows, Linux).
Uses tkinter which is built into Python - no extra installation needed.

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

# Ensure src/ is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.volume_loader import load
from src.csv_parser import parse_entries
from src.projector import project
from src.video_writer import write


class ProjectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Plane Projection Tool")
        self.root.resizable(False, False)

        # -- Variables ------------------------------------------------
        self.nrrd_path = tk.StringVar()
        self.csv_path = tk.StringVar()
        self.mp4_path = tk.StringVar()

        # -- Layout ---------------------------------------------------
        pad = {"padx": 12, "pady": 6}

        # Title
        title = tk.Label(root, text="3D Plane Projection", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(16, 8))

        # NRRD file
        tk.Label(root, text="NRRD Volume File:").grid(row=1, column=0, sticky="w", **pad)
        tk.Entry(root, textvariable=self.nrrd_path, width=45).grid(row=1, column=1, **pad)
        tk.Button(root, text="Browse...", command=self._browse_nrrd).grid(row=1, column=2, **pad)

        # CSV file
        tk.Label(root, text="Planes CSV File:").grid(row=2, column=0, sticky="w", **pad)
        tk.Entry(root, textvariable=self.csv_path, width=45).grid(row=2, column=1, **pad)
        tk.Button(root, text="Browse...", command=self._browse_csv).grid(row=2, column=2, **pad)

        # Output MP4
        tk.Label(root, text="Output Video (.mp4):").grid(row=3, column=0, sticky="w", **pad)
        tk.Entry(root, textvariable=self.mp4_path, width=45).grid(row=3, column=1, **pad)
        tk.Button(root, text="Save As...", command=self._browse_mp4).grid(row=3, column=2, **pad)

        # Separator
        ttk.Separator(root, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="ew", pady=8)

        # Progress bar
        self.progress = ttk.Progressbar(root, length=400, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, **pad)

        # Status label
        self.status_var = tk.StringVar(value="Ready. Select files and click Run.")
        tk.Label(root, textvariable=self.status_var, fg="gray").grid(row=6, column=0, columnspan=3, **pad)

        # Run button
        self.run_btn = tk.Button(
            root, text=">  Run Projection", font=("Helvetica", 13, "bold"),
            bg="#4CAF50", fg="white", command=self._start_run, height=2, width=20
        )
        self.run_btn.grid(row=7, column=0, columnspan=3, pady=(4, 16))

    # -- File dialogs -------------------------------------------------

    def _browse_nrrd(self):
        path = filedialog.askopenfilename(
            title="Select NRRD Volume File",
            filetypes=[("NRRD files", "*.nrrd"), ("All files", "*.*")]
        )
        if path:
            self.nrrd_path.set(path)

    def _browse_csv(self):
        path = filedialog.askopenfilename(
            title="Select Planes CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            self.csv_path.set(path)

    def _browse_mp4(self):
        path = filedialog.asksaveasfilename(
            title="Save Output Video As",
            defaultextension=".mp4",
            filetypes=[("MP4 video", "*.mp4")]
        )
        if path:
            self.mp4_path.set(path)

    # -- Run pipeline -------------------------------------------------

    def _start_run(self):
        """Validate inputs and launch the pipeline in a background thread."""
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

        # Disable button during run
        self.run_btn.config(state="disabled")
        self.progress["value"] = 0

        # Run in background thread so UI doesn't freeze
        thread = threading.Thread(target=self._run_pipeline, args=(nrrd, csv_f, mp4), daemon=True)
        thread.start()

    def _run_pipeline(self, nrrd_path, csv_path, mp4_path):
        """Execute the full projection pipeline (runs in background thread)."""
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
            t_start = time.perf_counter()

            for i, entry in enumerate(entries):
                p_idx = entry["plane_idx"]
                r_num = entry["row_num"]

                if entry["status"] == "valid":
                    frame = project(M, entry["plane"])
                    frames.append(frame)
                    labels.append(f"Plane {p_idx} (Row {r_num})")
                else:
                    frames.append(None)
                    labels.append(f"Plane {p_idx} (Row {r_num})")

                pct = 20 + int(60 * (i + 1) / total)
                self._update_progress(pct)
                self._update_status(f"Processing plane {i+1}/{total}...")

            t_proj = time.perf_counter() - t_start
            fps = valid_count / t_proj if t_proj > 0 else float("inf")
            self._update_progress(85)

            # Step 4: Write video
            self._update_status("Writing MP4 video with annotations...")
            write(frames, mp4_path, fps=30, vmin=vmin, vmax=vmax, seconds_per_frame=3.0, labels=labels)
            self._update_progress(100)

            # Done!
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

    # -- Thread-safe UI updates ---------------------------------------

    def _update_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))

    def _update_progress(self, value):
        self.root.after(0, lambda: self.progress.configure(value=value))

    def _show_error(self, msg):
        self.root.after(0, lambda: messagebox.showerror("Error", msg))
        self.root.after(0, lambda: self.status_var.set("Error occurred."))
        self.root.after(0, lambda: self.run_btn.config(state="normal"))


# -- Main -------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectionApp(root)
    root.mainloop()

