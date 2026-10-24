"""
Ex0.py – CLI entry point for the 3D plane projection tool.

Usage:
    python Ex0.py file.nrrd file.csv file.mp4

Arguments:
    file.nrrd   3D volumetric data file in NRRD format
    file.csv    CSV file with one plane per row (3 or 4 points, x,y,z each)
    file.mp4    Output video file (one frame per valid plane, in CSV order)
"""

import sys
import os
import time
import numpy as np

from src.volume_loader import load
from src.csv_parser import parse
from src.projector import project
from src.video_writer import write

USAGE = "Usage: python Ex0.py file.nrrd file.csv file.mp4"


def main(nrrd_path: str, csv_path: str, mp4_path: str) -> None:

    # ── 1. Load volume ──────────────────────────────────────────────
    M = load(nrrd_path)

    vmin = int(M.min())
    vmax = int(M.max())

    # ── 2. Parse planes ─────────────────────────────────────────────
    planes = parse(csv_path)

    if not planes:
        print("[Error] No valid planes found in CSV. Exiting.")
        sys.exit(1)

    print(f"[Main] {len(planes)} valid plane(s) loaded.")

    # ── 3. Warn if output file already exists ───────────────────────
    if os.path.exists(mp4_path):
        print(f"[Warning] Output file '{mp4_path}' already exists and will be overwritten.")

    # ── 4. Project each plane ────────────────────────────────────────
    frames = []
    t_start = time.perf_counter()

    for i, plane in enumerate(planes):
        frame = project(M, plane)
        frames.append(frame)

    t_proj = time.perf_counter() - t_start
    fps = len(frames) / t_proj if t_proj > 0 else float("inf")

    # ── 5. Write video ───────────────────────────────────────────────
    write(frames, mp4_path, fps=30, vmin=vmin, vmax=vmax)

    # ── 6. Summary ───────────────────────────────────────────────────
    total_rows = len(planes)
    print(
        f"\n── Summary ──────────────────────────────\n"
        f"  Planes read:    {total_rows}\n"
        f"  Frames written: {len(frames)}\n"
        f"  Projection time:{t_proj:.3f} s\n"
        f"  Processing FPS: {fps:.1f}\n"
        f"  {'✅ PASS' if fps >= 30 else '❌ FAIL'} (target: ≥30 FPS)\n"
        f"─────────────────────────────────────────"
    )


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(USAGE)
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
