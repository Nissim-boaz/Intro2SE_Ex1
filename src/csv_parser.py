"""
csv_parser.py
Parses a CSV file of plane definitions into structured records and Plane objects.
Handles missing headers, arbitrary point counts, and collects error descriptions.
"""

from __future__ import annotations

import csv
import numpy as np
from src.plane import Plane


def parse_entries(path: str) -> list[dict]:
    """
    Read a CSV file of plane coordinates and return a list of parsed entry records.
    Validates numerical values, coordinate counts, and geometric plane constraints.

    Algorithm:
        1. Open CSV file (utf-8-sig) and read lines sequentially.
        2. Filter empty cells and parse float values (skip non-numeric header lines).
        3. Match format: 10/13 values (declared point count) or 9/12 values.
        4. Group coordinates into 3D vectors [p1, p2, p3 (, p4)].
        5. Validate geometry via Plane(pts):
               Valid   -> record status='valid' and store Plane instance.
               Invalid -> record status='invalid' and capture exact error string.
        6. Return complete list of entry dictionaries.

    Parameters
    ----------
    path : str
        Path to the CSV file containing plane coordinates.

    Returns
    -------
    list of dict
        Each dict contains:
        - plane_idx : int (1-based counter among all plane rows)
        - row_num   : int (1-based CSV line number)
        - status    : 'valid' | 'invalid'
        - plane     : Plane instance (if valid)
        - error     : descriptive error message string (if invalid)
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

            # Parse numeric floats; None indicates a text header or non-numeric line
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
                print(f"[CSVParser] Row {row_num}: skipped (non-numeric values).")
                continue

            if not raw_floats:
                continue

            plane_counter += 1
            n = len(raw_floats)

            # Case A: 10 or 13 values (leading count column: 3 or 4)
            if n in (10, 13) and int(raw_floats[0]) in (3, 4):
                expected_points = int(raw_floats[0])
                coords = raw_floats[1:]
                if len(coords) < expected_points * 3:
                    err = (
                        f"declared {expected_points} points ({expected_points * 3} coordinates), "
                        f"but only {len(coords)} values provided"
                    )
                    print(f"[CSVParser] Row {row_num} (Plane {plane_counter}): skipped ({err})")
                    entries.append({
                        "plane_idx": plane_counter,
                        "row_num": row_num,
                        "status": "invalid",
                        "error": err
                    })
                    continue
                coords = coords[:expected_points * 3]
                pts = [np.array(coords[i*3:(i+1)*3]) for i in range(expected_points)]

            # Case B: 9 values (3 points without leading count)
            elif n == 9:
                pts = [np.array(raw_floats[i*3:(i+1)*3]) for i in range(3)]

            # Case C: 12 values (4 points without leading count)
            elif n == 12:
                pts = [np.array(raw_floats[i*3:(i+1)*3]) for i in range(4)]

            # Case D: Unexpected coordinate count
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

            # Validate geometric constraints via Plane initialization
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
    Read a CSV file and return only the valid Plane objects.
    Maintained for clean backward compatibility with previous test suites.
    """
    entries = parse_entries(path)
    return [e["plane"] for e in entries if e["status"] == "valid"]
