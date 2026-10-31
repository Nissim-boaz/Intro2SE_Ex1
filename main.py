"""
main.py - CLI and Automated Entry Point for 3D Volume Plane Projection.

This module provides a headless command-line interface to execute 3D volume
plane projections without launching a graphical user interface (GUI).

Usage modes:
    1. Explicit Arguments (Instructor Standard):
       python main.py <volume.nrrd> <planes.csv> <output.mp4>

    2. Automated Discovery (Zero-Config Default):
       python main.py
       Automatically searches the project and data/ directory for .nrrd and .csv
       files, executes the projection pipeline, and generates output.mp4.
"""

from __future__ import annotations

import os
import sys
import glob
import time
from typing import Optional, Tuple

import numpy as np

from src.volume_loader import load
from src.csv_parser import parse_entries
from src.projector import project
from src.video_writer import write


class ProjectionPipeline:
    """Orchestrates loading, projecting, and video export for 3D volumetric data."""

    def __init__(self, nrrd_path: str, csv_path: str, mp4_path: str):
        self.nrrd_path = nrrd_path
        self.csv_path = csv_path
        self.mp4_path = mp4_path

    def run(self) -> float:
        """
        Executes the full projection pipeline.

        Returns
        -------
        float
            Measured processing performance in frames per second (FPS).
        """
        print(f"\n==================================================")
        print(f" 3D Volume Plane Projection - Execution Pipeline")
        print(f"==================================================")
        print(f"[Input NRRD] : {self.nrrd_path}")
        print(f"[Input CSV]  : {self.csv_path}")
        print(f"[Output MP4] : {self.mp4_path}")
        print(f"--------------------------------------------------")

        # 1. Load 3D Volume
        t0_load = time.perf_counter()
        M = load(self.nrrd_path)
        t_load = time.perf_counter() - t0_load
        print(f"[VolumeLoader] Loaded shape={M.shape}, dtype={M.dtype} in {t_load:.3f}s")

        vmin = int(M.min())
        vmax = int(M.max())

        # 2. Parse Plane Definitions from CSV
        entries = parse_entries(self.csv_path)
        if not entries:
            raise ValueError(f"No plane entries found in CSV file: '{self.csv_path}'")

        valid_count = sum(1 for e in entries if e["status"] == "valid")
        invalid_count = len(entries) - valid_count
        print(f"[CSVParser] Found {len(entries)} plane(s): {valid_count} valid, {invalid_count} invalid.")

        # 3. Warn on existing output
        if os.path.exists(self.mp4_path):
            print(f"[Warning] Output file '{self.mp4_path}' already exists and will be overwritten.")

        # 4. Compute Projections
        frames = []
        labels = []
        t_start = time.perf_counter()

        for entry in entries:
            p_idx = entry["plane_idx"]
            r_num = entry["row_num"]

            if entry["status"] == "valid":
                frame = project(M, entry["plane"])
                frames.append(frame)
                labels.append(f"Plane {p_idx} (Row {r_num})")
            else:
                frames.append(None)
                labels.append(f"Plane {p_idx} (Row {r_num})")

        t_proj = time.perf_counter() - t_start
        fps = valid_count / t_proj if t_proj > 0 else float("inf")

        # 5. Write Output MP4 Video
        write(frames, self.mp4_path, fps=30, vmin=vmin, vmax=vmax, seconds_per_frame=3.0, labels=labels)

        # 6. Display Execution Summary
        status_pass = "[PASS]" if fps >= 30 else "[FAIL]"
        print(f"\n-- Execution Summary -----------------------------")
        print(f"  Total Planes Processed : {len(entries)}")
        print(f"  Valid Projections      : {valid_count}")
        print(f"  Skipped / Invalid      : {invalid_count}")
        print(f"  Projection Runtime     : {t_proj:.4f} seconds")
        print(f"  Processing Speed       : {fps:.1f} FPS (Requirement: >=30 FPS) {status_pass}")
        print(f"--------------------------------------------------")
        print(f"[Success] Output video created successfully: '{self.mp4_path}'\n")

        return fps


def auto_detect_files() -> Tuple[Optional[str], Optional[str]]:
    """
    Attempts to locate default .nrrd and .csv files in data/ or project root.
    """
    # Priority for NRRD
    nrrd_candidates = [
        os.path.join("data", "MRHead_1.nrrd"),
        *glob.glob(os.path.join("data", "*.nrrd")),
        *glob.glob("*.nrrd"),
    ]
    nrrd_file = next((f for f in nrrd_candidates if os.path.isfile(f)), None)

    # Priority for CSV
    csv_candidates = [
        os.path.join("data", "professor_planes.csv"),
        os.path.join("data", "50_planes.csv"),
        *glob.glob(os.path.join("data", "*.csv")),
        *glob.glob("*.csv"),
    ]
    csv_file = next((f for f in csv_candidates if os.path.isfile(f)), None)

    return nrrd_file, csv_file


def main():
    """Entry point handling command-line arguments and auto-detection."""
    args = sys.argv[1:]

    if len(args) == 3:
        nrrd_path, csv_path, mp4_path = args
    elif len(args) == 0:
        print("[Info] No CLI arguments provided. Attempting automatic dataset discovery...")
        detected_nrrd, detected_csv = auto_detect_files()

        if not detected_nrrd or not detected_csv:
            print("[Error] Could not automatically locate required input files.")
            print("Please provide files explicitly using:")
            print("  python main.py <volume.nrrd> <planes.csv> <output.mp4>")
            sys.exit(1)

        nrrd_path = detected_nrrd
        csv_path = detected_csv
        mp4_path = "output.mp4"
        print(f"[AutoDetect] Found dataset: '{nrrd_path}' and '{csv_path}' -> Output: '{mp4_path}'")
    else:
        print("Usage:")
        print("  python main.py <volume.nrrd> <planes.csv> <output.mp4>")
        print("  python main.py  (auto-detects files from data/ directory)")
        sys.exit(1)

    try:
        pipeline = ProjectionPipeline(nrrd_path, csv_path, mp4_path)
        pipeline.run()
    except Exception as e:
        print(f"\n[Execution Error] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
