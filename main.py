"""
main.py - Minimal & Clean CLI for 3D Volume Plane Projection.

Usage:
    python main.py
    python main.py <file.nrrd> <file.csv> <file.mp4>
"""

from __future__ import annotations

import os
import sys
import glob
import time
import io
import contextlib
from typing import List

from src.volume_loader import load
from src.csv_parser import parse_entries
from src.projector import project
from src.video_writer import write


@contextlib.contextmanager
def silence_internal_logs():
    """Silences noisy background library prints to keep terminal output clean."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout


def choose_file(extension: str, default_keyword: str = "") -> str:
    """
    Finds all files of the given extension in data/ and current directory.
    If only 1 file exists, returns it immediately without prompting.
    If multiple files exist, asks the user in English to select one.
    """
    candidates: List[str] = list(dict.fromkeys(
        glob.glob(os.path.join("data", f"*.{extension}")) +
        glob.glob(f"*.{extension}")
    ))
    candidates = [c.replace("\\", "/") for c in candidates]

    if not candidates:
        raise FileNotFoundError(f"No .{extension} files found in project or data/ folder.")

    # Only 1 file of this type -> select automatically without asking
    if len(candidates) == 1:
        return candidates[0]

    # Multiple files -> sort so the preferred file is option [1]
    if default_keyword:
        candidates.sort(key=lambda x: (0 if default_keyword in x else 1, x))

    print(f"\nMultiple .{extension} files found:")
    for idx, path in enumerate(candidates, 1):
        tag = " (default)" if idx == 1 else ""
        print(f"  [{idx}] {path}{tag}")

    try:
        choice = input(f"Which .{extension} file would you like to use? [1]: ").strip()
        if not choice:
            return candidates[0]
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return candidates[int(choice) - 1]
        for c in candidates:
            if choice in c:
                return c
        return candidates[0]
    except (EOFError, KeyboardInterrupt):
        return candidates[0]


def run_projection(nrrd_path: str, csv_path: str, mp4_path: str) -> None:
    """Executes the projection pipeline with concise, focused console output."""
    print(f"\nUsing volume: {nrrd_path}")
    print(f"Using planes: {csv_path}")

    # Load volume and parse planes quietly
    with silence_internal_logs():
        M = load(nrrd_path)
        entries = parse_entries(csv_path)

    if not entries:
        print(f"[Error] No valid plane definitions found in: {csv_path}")
        return

    vmin = int(M.min())
    vmax = int(M.max())

    frames = []
    labels = []
    valid_count = sum(1 for e in entries if e["status"] == "valid")

    t_start = time.perf_counter()
    for entry in entries:
        if entry["status"] == "valid":
            frame = project(M, entry["plane"])
            frames.append(frame)
            labels.append(f"Plane {entry['plane_idx']}")
        else:
            frames.append(None)
            labels.append(f"Plane {entry['plane_idx']}")

    t_proj = time.perf_counter() - t_start
    fps = valid_count / t_proj if t_proj > 0 else float("inf")

    # Write video quietly
    with silence_internal_logs():
        write(frames, mp4_path, fps=30, vmin=vmin, vmax=vmax, seconds_per_frame=3.0, labels=labels)

    # Concise final report
    print(f"Speed: {fps:.1f} FPS")
    print(f"Video created successfully: {mp4_path}\n")


def main():
    args = sys.argv[1:]

    if len(args) == 3:
        nrrd_path, csv_path, mp4_path = args
    elif len(args) == 0:
        try:
            nrrd_path = choose_file("nrrd", default_keyword="MRHead")
            csv_path = choose_file("csv", default_keyword="professor_planes")

            prompt = "\nWhat would you like to name the output video? [default: output.mp4]: "
            user_choice = input(prompt).strip()
            if user_choice:
                mp4_path = user_choice if user_choice.endswith(".mp4") else user_choice + ".mp4"
            else:
                mp4_path = "output.mp4"
        except FileNotFoundError as fnf_err:
            print(f"[Error] {fnf_err}")
            print("Usage: python main.py <file.nrrd> <file.csv> <file.mp4>")
            sys.exit(1)
        except (EOFError, KeyboardInterrupt):
            mp4_path = "output.mp4"
            print()
    else:
        print("Usage:")
        print("  python main.py <file.nrrd> <file.csv> <file.mp4>")
        print("  python main.py  (interactive file selection)")
        sys.exit(1)

    try:
        run_projection(nrrd_path, csv_path, mp4_path)
    except Exception as e:
        print(f"[Error] Execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
