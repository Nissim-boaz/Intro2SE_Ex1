"""
test_csv_parser.py
Unit tests for src/csv_parser.py  (CSV-1 … CSV-6, plus edge cases).
Validates line parsing, coordinate extraction, error handling, and header skipping.
"""

import pytest
from src.csv_parser import parse


def _write_csv(path, content: str) -> None:
    """Helper to write CSV text directly to disk."""
    path.write_text(content, encoding="utf-8")


class TestCSVParser:

    def test_CSV1_three_point_plane(self, tmp_path):
        """
        CSV-1: Verify that a valid row containing 9 coordinates parses into an isosceles triangle.
        Tests 3-point plane definition without a leading point-count column.
        """
        f = tmp_path / "planes.csv"
        # Isosceles triangle: a=(0,0,0), b=(1,0,0), c=(0,1,0)
        _write_csv(f, "0,0,0, 1,0,0, 0,1,0\n")
        planes = parse(str(f))
        assert len(planes) == 1

    def test_CSV2_four_point_plane(self, tmp_path):
        """
        CSV-2: Verify that a valid row containing 12 coordinates parses into a 4-point trapezoid.
        Tests rectangular and trapezoidal plane definitions without crashing.
        """
        f = tmp_path / "planes.csv"
        # Isosceles trapezoid (rectangle): a1,a2,b,c all coplanar
        _write_csv(f, "0,1,0, 1,1,0, 0,0,0, 1,0,0\n")
        planes = parse(str(f))
        assert len(planes) == 1

    def test_CSV3_wrong_value_count(self, tmp_path, capsys):
        """
        CSV-3: Verify that rows with incorrect coordinate counts (e.g. 5 numbers) are skipped.
        Ensures that a warning is logged to stdout and no corrupt Plane object is generated.
        """
        f = tmp_path / "planes.csv"
        _write_csv(f, "1,2,3,4,5\n")          # 5 values → invalid
        planes = parse(str(f))
        assert len(planes) == 0
        captured = capsys.readouterr()
        assert "skipped" in captured.out.lower()

    def test_CSV4_non_numeric(self, tmp_path, capsys):
        """
        CSV-4: Verify that rows containing text strings instead of numbers are safely skipped.
        Prevents parser crashes when encountering non-numeric tokens or malformed cells.
        """
        f = tmp_path / "planes.csv"
        _write_csv(f, "a,b,c,d,e,f,g,h,i\n")
        planes = parse(str(f))
        assert len(planes) == 0
        captured = capsys.readouterr()
        assert "skipped" in captured.out.lower()

    def test_CSV5_header_and_empty_lines(self, tmp_path):
        """
        CSV-5: Verify that text headers and blank rows are gracefully ignored.
        Ensures only valid numeric data rows are converted into Plane instances.
        """
        f = tmp_path / "planes.csv"
        _write_csv(f, "x1,y1,z1,x2,y2,z2,x3,y3,z3\n\n0,0,0,1,0,0,0,1,0\n")
        planes = parse(str(f))
        assert len(planes) == 1   # Only the valid data row is returned

    def test_CSV6_all_invalid(self, tmp_path):
        """
        CSV-6: Verify that an entirely malformed CSV returns a safe empty list.
        Ensures the pipeline can handle zero valid planes without throwing unhandled exceptions.
        """
        f = tmp_path / "planes.csv"
        _write_csv(f, "bad,row\nalso,bad\n")
        planes = parse(str(f))
        assert planes == []

    def test_file_not_found(self):
        """
        Verify that attempting to parse a nonexistent file path raises FileNotFoundError.
        Provides clear and immediate feedback when file paths are mistyped.
        """
        with pytest.raises(FileNotFoundError):
            parse("/nonexistent/planes.csv")

    def test_multiple_valid_rows(self, tmp_path):
        """
        Verify that multiple valid rows in a CSV are parsed sequentially in exact line order.
        Confirms that both triangles and trapezoids can coexist within the same file.
        """
        f = tmp_path / "planes.csv"
        _write_csv(f,
            "0,0,0, 1,0,0, 0,1,0\n"
            "0,1,0, 1,1,0, 0,0,0, 1,0,0\n"
        )
        planes = parse(str(f))
        assert len(planes) == 2
