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
        f = open(path, newline="", encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")

    planes = []
    with f:
        reader = csv.reader(f)
        for row_num, row in enumerate(reader, start=1):
            # Skip empty rows
            if not row:
                continue

            # Try to parse all values as floats
            try:
                values = [float(v.strip()) for v in row]
            except ValueError:
                # Could be a header row or malformed data
                print(f"[CSVParser] Row {row_num}: skipped (non-numeric values).")
                continue

            n = len(values)
            if n == 9:
                pts = [np.array(values[i*3:(i+1)*3]) for i in range(3)]
            elif n == 12:
                pts = [np.array(values[i*3:(i+1)*3]) for i in range(4)]
            else:
                print(
                    f"[CSVParser] Row {row_num}: skipped "
                    f"(expected 9 or 12 values, got {n})."
                )
                continue

            try:
                plane = Plane(pts)
                planes.append(plane)
            except ValueError as e:
                print(f"[CSVParser] Row {row_num}: skipped ({e})")

    return planes
