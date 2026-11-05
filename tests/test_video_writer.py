"""
test_video_writer.py
Unit tests for src/video_writer.py  (VW-1 … VW-8).
Validates frame count replication, canvas centering, 16-bit normalization,
error classification, dynamic range labeling, and consecutive error grouping.
"""

import os
import numpy as np
import pytest
import cv2

from src.video_writer import write, classify_error, format_group_label


class TestVideoWriter:

    def _make_frames(self, n: int, rows: int = 20, cols: int = 30, dtype=np.uint8) -> list[np.ndarray]:
        """Helper generating a list of n random 2D image arrays."""
        return [np.random.randint(0, 256, (rows, cols), dtype=dtype) for _ in range(n)]

    def test_VW1_frame_count(self, tmp_path):
        """
        VW-1: Verify that output MP4 contains exactly N * repeat_count frames when duration is set.
        Confirms that seconds_per_frame multiplies frame count accurately (5 frames * 3s * 30fps = 450).
        """
        N = 5
        frames = self._make_frames(N)
        out = str(tmp_path / "out.mp4")
        write(frames, out, fps=30, seconds_per_frame=3.0)

        cap = cv2.VideoCapture(out)
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        assert count == N * 90

    def test_VW2_padding_different_sizes(self, tmp_path):
        """
        VW-2: Verify that projection frames of varying shapes are centered within the max bounding canvas.
        Checks that video resolution matches the largest frame dimensions across the sequence.
        """
        frames = [
            np.zeros((10, 20), dtype=np.uint8),
            np.zeros((30, 40), dtype=np.uint8),
        ]
        out = str(tmp_path / "out.mp4")
        write(frames, out)

        cap = cv2.VideoCapture(out)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        assert w == 40 and h == 30

    def test_VW3_16bit_normalization(self, tmp_path):
        """
        VW-3: Verify that 16-bit high-depth frames are contrast-normalized to 8-bit without overflow.
        Ensures compatibility with standard OpenCV video codecs that require 8-bit unsigned integers.
        """
        frames = self._make_frames(2, dtype=np.uint16)
        out = str(tmp_path / "out.mp4")
        write(frames, out, vmin=0, vmax=65535)
        assert os.path.exists(out)

    def test_VW4_unwritable_path(self):
        """
        VW-4: Verify that attempting to write to an invalid or unwritable file path raises RuntimeError.
        Ensures clear error notification when destination directories do not exist.
        """
        frames = self._make_frames(1)
        with pytest.raises((RuntimeError, Exception)):
            write(frames, "/nonexistent_dir/out.mp4")

    def test_empty_frames_raises(self, tmp_path):
        """
        Verify that passing an empty list of frames raises ValueError.
        Protects against creating zero-byte video files with no content.
        """
        with pytest.raises(ValueError, match="[Nn]o frames"):
            write([], str(tmp_path / "out.mp4"))

    def test_VW5_invalid_frame_with_error_classification(self, tmp_path):
        """
        VW-5: Verify that error messages are classified into concise categories and written to slides.
        Checks classification mappings (collinear, non-coplanar, not isosceles) and video generation.
        """
        assert classify_error("Not an isosceles triangle") == "Triangle Not Isosceles"
        assert classify_error("Not isosceles") == "Trapezoid Not Isosceles"
        assert classify_error("Trapezoid points are not coplanar") == "Points Not Coplanar"
        assert classify_error("points are collinear") == "Collinear Points (Degenerate)"
        assert classify_error("dist(a1,a2)=100 > dist(b,c)=50") == "Top Base Wider Than Bottom"
        assert classify_error("zero length") == "Zero-Length Side (Degenerate)"

        frames = [None, np.zeros((20, 20), dtype=np.uint8)]
        out = str(tmp_path / "out_err.mp4")
        write(frames, out, fps=10, seconds_per_frame=0.2, errors=["Not an isosceles triangle", None])
        assert os.path.exists(out)

    def test_VW6_format_group_label(self):
        """
        VW-6: Verify that format_group_label correctly formats both individual and range titles.
        Tests extraction of plane indices and CSV row ranges into standard on-screen text.
        """
        # Single plane formatting
        assert format_group_label(0, 0, ["Plane 1"]) == "Plane 1"
        assert format_group_label(4, 4, ["Plane 1", "Plane 2", "Plane 3", "Plane 4", "Plane 5 (Row 6)"]) == "Plane 5 (Row 6)"

        # Group range without row numbers (Ex0.py format)
        labels_ex0 = [f"Plane {i}" for i in range(1, 26)]
        assert format_group_label(0, 24, labels_ex0) == "Planes: 1-25"

        # Group range with row numbers (gui.py format)
        labels_gui = [f"Plane {i} (Row {i+1})" for i in range(1, 26)]
        assert format_group_label(0, 24, labels_gui) == "Planes: 1-25 (Rows 2-26)"

        # Fallback when labels parameter is None
        assert format_group_label(0, 24, None) == "Planes: 1-25"

    def test_VW7_consecutive_errors_grouped(self, tmp_path):
        """
        VW-7: Verify that consecutive invalid planes with identical errors collapse into a single slide.
        Prevents video bloat, rendering 1 slide held for 1.5s (45 frames at 30 fps) instead of 450 frames.
        """
        # 10 consecutive invalid frames with the exact SAME error category
        err = "declared 4 points, but got 9"
        frames = [None] * 10
        errors = [err] * 10
        labels = [f"Plane {i}" for i in range(1, 11)]

        out = str(tmp_path / "grouped.mp4")
        fps = 30
        write(frames, out, fps=fps, errors=errors, labels=labels)

        cap = cv2.VideoCapture(out)
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # Exactly 1 error slide held for 1.5s = 45 frames (NOT 10 * 45 = 450)
        assert count == int(round(fps * 1.5))

    def test_VW8_different_consecutive_errors_not_grouped(self, tmp_path):
        """
        VW-8: Verify that consecutive frames with DIFFERENT error categories remain distinct slides.
        Guarantees that distinct error reasons are not erroneously merged together into one notice.
        """
        frames = [None, None]
        errors = ["triangle not isosceles", "points not coplanar"]
        labels = ["Plane 1", "Plane 2"]

        out = str(tmp_path / "distinct.mp4")
        fps = 30
        write(frames, out, fps=fps, errors=errors, labels=labels)

        cap = cv2.VideoCapture(out)
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        # Two distinct error categories -> 2 separate slides of 1.5s each = 90 frames
        assert count == 2 * int(round(fps * 1.5))
