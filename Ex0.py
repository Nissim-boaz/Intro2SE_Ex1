"""
Ex0.py - CLI entry point for the 3D plane projection tool.

Usage:
    python Ex0.py file.nrrd file.csv file.mp4

Arguments:
    file.nrrd   3D volumetric data file in NRRD format
    file.csv    CSV file with one plane per row (3 or 4 points, x,y,z each)
    file.mp4    Output video file (one frame per valid plane, in CSV order)
"""

from __future__ import annotations

import sys
import os
import io
import time
import contextlib

from src.volume_loader import load
from src.csv_parser import parse_entries
from src.projector import project
from src.video_writer import write

USAGE = "Usage: python Ex0.py file.nrrd file.csv file.mp4"


@contextlib.contextmanager
def silence_internal_logs():
    """Suppresses noisy verbose stdout prints from internal modules."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout


def main(nrrd_path: str, csv_path: str, mp4_path: str) -> None:
    print(f"\nUsing volume: {nrrd_path}")
    print(f"Using planes: {csv_path}")

    # Load volume and parse planes quietly
    with silence_internal_logs():
        M = load(nrrd_path)
        entries = parse_entries(csv_path)

    if not entries:
        print(f"[Error] No valid plane definitions found in: {csv_path}")
        sys.exit(1)

    vmin = int(M.min())
    vmax = int(M.max())

    frames = []
    labels = []
    errors = []
    valid_count = sum(1 for e in entries if e["status"] == "valid")

    t_start = time.perf_counter()
    for entry in entries:
        if entry["status"] == "valid":
            frame = project(M, entry["plane"])
            frames.append(frame)
            labels.append(f"Plane {entry['plane_idx']}")
            errors.append(None)
        else:
            frames.append(None)
            labels.append(f"Plane {entry['plane_idx']}")
            errors.append(entry.get("error"))

    t_proj = time.perf_counter() - t_start
    fps = valid_count / t_proj if t_proj > 0 else float("inf")

    # Write video quietly (smooth playback at 30 FPS)
    with silence_internal_logs():
        write(frames, mp4_path, fps=30, vmin=vmin, vmax=vmax, labels=labels, errors=errors)

    # Concise final report
    print(f"Speed: {fps:.1f} FPS")
    print(f"Video created successfully: {mp4_path}\n")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(USAGE)
        sys.exit(1)

    try:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    except Exception as e:
        print(f"[Error] Execution failed: {e}")
        sys.exit(1)
