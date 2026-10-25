"""
csv_parser.py
Parses a CSV file of plane definitions into a list of Plane objects.

Each row must contain either 9 values (3 points) or 12 values (4 points),
where each point is given as x,y,z.
"""

import csv
import numpy as np
from src.plane import Plane


def parse_entries(path: str) -> list[dict]:
    """
    Read a CSV file and return a list of entries with status.

    Returns
    -------
    list of dict
        Each dict has:
        - plane_idx : int (1-based counter among all plane rows)
        - row_num   : int (1-based CSV line number)
        - status    : 'valid' | 'invalid'
        - plane     : Plane object (if valid)
        - error     : error message string (if invalid)
    """
    try:
        f = open(path, newline="", encoding="utf-8-sig")
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")

    entries = []
    plane_counter = 0

    with f:
        reader = csv.reader(f)
        for row_num, row in enumerate(reader, start=1):
            if not row:
                continue

            cleaned_row = [cell.strip() for cell in row]

            raw_floats = []
            for cell in cleaned_row:
                if cell == "":
                    continue
                try:
                    raw_floats.append(float(cell))
                except ValueError:
                    raw_floats = None
                    break

            if raw_floats is None:
                # Header row or row with text
                print(f"[CSVParser] Row {row_num}: skipped (non-numeric values).")
                continue

            if not raw_floats:
                continue

            plane_counter += 1
            n = len(raw_floats)

            # Case A: 10 or 13 values (with count)
            if n in (10, 13) and int(raw_floats[0]) in (3, 4):
                expected_points = int(raw_floats[0])
                coords = raw_floats[1:1 + expected_points * 3]
                pts = [np.array(coords[i*3:(i+1)*3]) for i in range(expected_points)]
            elif n == 9:
                pts = [np.array(raw_floats[i*3:(i+1)*3]) for i in range(3)]
            elif n == 12:
                pts = [np.array(raw_floats[i*3:(i+1)*3]) for i in range(4)]
            else:
                err = f"skipped (expected 9, 10, 12, or 13 numbers, got {n})"
                print(f"[CSVParser] Row {row_num} (Plane {plane_counter}): {err}")
                entries.append({
                    "plane_idx": plane_counter,
                    "row_num": row_num,
                    "status": "invalid",
                    "error": err
                })
                continue

            try:
                plane = Plane(pts)
                entries.append({
                    "plane_idx": plane_counter,
                    "row_num": row_num,
                    "status": "valid",
                    "plane": plane
                })
            except ValueError as e:
                err = str(e)
                print(f"[CSVParser] Row {row_num} (Plane {plane_counter}): skipped ({err})")
                entries.append({
                    "plane_idx": plane_counter,
                    "row_num": row_num,
                    "status": "invalid",
                    "error": err
                })

    return entries


def parse(path: str) -> list[Plane]:
    """
    Read a CSV file and return only valid Plane objects (backward compatible).
    """
    entries = parse_entries(path)
    return [e["plane"] for e in entries if e["status"] == "valid"]


