"""
csv_parser.py
Parses a CSV file of plane definitions into a list of Plane objects.

Each row must contain either 9 values (3 points) or 12 values (4 points),
where each point is given as x,y,z.
"""

import csv
import numpy as np
from src.plane import Plane


def parse(path: str) -> list[Plane]:
    """
    Read a CSV file and return a list of valid Plane objects.

    Invalid rows are skipped with a warning. An optional header row
    and empty lines are ignored automatically.

    Parameters
    ----------
    path : str
        Path to the .csv file.

    Returns
    -------
    list[Plane]
        Planes in CSV row order.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    try:
        f = open(path, newline="", encoding="utf-8-sig")
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")

    planes = []
    with f:
        reader = csv.reader(f)
        for row_num, row in enumerate(reader, start=1):
            # Skip empty rows
            if not row:
                continue

            # Clean and strip cells, filter out purely trailing empty strings
            cleaned_row = [cell.strip() for cell in row]

            # Try to parse numeric values, ignoring empty cells at the end
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
                print(f"[CSVParser] Row {row_num}: skipped (header or non-numeric values).")
                continue

            if not raw_floats:
                continue

            n = len(raw_floats)

            # Case A: Format with count column at start (3, x1, y1, z1, ..., or 4, ...)
            if n in (10, 13) and int(raw_floats[0]) in (3, 4):
                expected_points = int(raw_floats[0])
                coords = raw_floats[1:1 + expected_points * 3]
                pts = [np.array(coords[i*3:(i+1)*3]) for i in range(expected_points)]

            # Case B: Standard 9 (3 points) or 12 (4 points) coordinates directly
            elif n == 9:
                pts = [np.array(raw_floats[i*3:(i+1)*3]) for i in range(3)]
            elif n == 12:
                pts = [np.array(raw_floats[i*3:(i+1)*3]) for i in range(4)]
            else:
                print(
                    f"[CSVParser] Row {row_num}: skipped "
                    f"(expected 9, 10, 12, or 13 values, got {n})."
                )
                continue

            try:
                plane = Plane(pts)
                planes.append(plane)
            except ValueError as e:
                print(f"[CSVParser] Row {row_num}: skipped ({e})")

    return planes

