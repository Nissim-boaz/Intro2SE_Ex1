"""
test_csv_parser.py
Unit tests for src/csv_parser.py  (CSV-1 … CSV-6)
"""

import pytest
from src.csv_parser import parse


def _write_csv(path, content: str):
    path.write_text(content, encoding="utf-8")


class TestCSVParser:

    def test_CSV1_three_point_plane(self, tmp_path):
        """CSV-1: valid row with 9 values returns one Plane."""
        f = tmp_path / "planes.csv"
        # isosceles triangle: a=(0,0,0), b=(1,0,0), c=(0,1,0)
        _write_csv(f, "0,0,0, 1,0,0, 0,1,0\n")
        planes = parse(str(f))
        assert len(planes) == 1

    def test_CSV2_four_point_plane(self, tmp_path):
        """CSV-2: valid row with 12 values returns one Plane."""
        f = tmp_path / "planes.csv"
        # isosceles trapezoid (rectangle): a1,a2,b,c all coplanar
        _write_csv(f, "0,1,0, 1,1,0, 0,0,0, 1,0,0\n")
        planes = parse(str(f))
        assert len(planes) == 1

    def test_CSV3_wrong_value_count(self, tmp_path, capsys):
        """CSV-3: row with wrong number of values is skipped with a warning."""
        f = tmp_path / "planes.csv"
        _write_csv(f, "1,2,3,4,5\n")          # 5 values → invalid
        planes = parse(str(f))
        assert len(planes) == 0
        captured = capsys.readouterr()
        assert "skipped" in captured.out.lower()

    def test_CSV4_non_numeric(self, tmp_path, capsys):
        """CSV-4: row with non-numeric text is skipped with a warning."""
        f = tmp_path / "planes.csv"
        _write_csv(f, "a,b,c,d,e,f,g,h,i\n")
        planes = parse(str(f))
        assert len(planes) == 0
        captured = capsys.readouterr()
        assert "skipped" in captured.out.lower()

    def test_CSV5_header_and_empty_lines(self, tmp_path):
        """CSV-5: header / empty lines are ignored silently."""
        f = tmp_path / "planes.csv"
        _write_csv(f, "x1,y1,z1,x2,y2,z2,x3,y3,z3\n\n0,0,0,1,0,0,0,1,0\n")
        planes = parse(str(f))
        assert len(planes) == 1   # only the valid data row

    def test_CSV6_all_invalid(self, tmp_path):
        """CSV-6: all rows invalid → empty list returned."""
        f = tmp_path / "planes.csv"
        _write_csv(f, "bad,row\nalso,bad\n")
        planes = parse(str(f))
        assert planes == []

    def test_file_not_found(self):
        """Missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse("/nonexistent/planes.csv")

    def test_multiple_valid_rows(self, tmp_path):
        """Multiple valid rows → multiple planes in CSV order."""
        f = tmp_path / "planes.csv"
        _write_csv(f,
            "0,0,0, 1,0,0, 0,1,0\n"
            "0,1,0, 1,1,0, 0,0,0, 1,0,0\n"
        )
        planes = parse(str(f))
        assert len(planes) == 2
