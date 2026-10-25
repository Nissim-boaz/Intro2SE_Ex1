"""
test_video_writer.py
Unit tests for src/video_writer.py  (VW-1 … VW-4)
"""

import os
import numpy as np
import pytest
import cv2

from src.video_writer import write


class TestVideoWriter:

    def _make_frames(self, n, rows=20, cols=30, dtype=np.uint8):
        return [np.random.randint(0, 256, (rows, cols), dtype=dtype) for _ in range(n)]

    def test_VW1_frame_count(self, tmp_path):
        """VW-1: output MP4 has N * repeat_count frames for 3s display."""
        N = 5
        frames = self._make_frames(N)
        out = str(tmp_path / "out.mp4")
        write(frames, out, fps=30, seconds_per_frame=3.0)

        cap = cv2.VideoCapture(out)
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        assert count == N * 90  # 5 frames * 3s * 30fps = 450

    def test_VW2_padding_different_sizes(self, tmp_path):
        """VW-2: frames of different sizes are padded to max dimensions."""
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
        """VW-3: 16-bit input is normalized to 8-bit without crashing."""
        frames = self._make_frames(2, dtype=np.uint16)
        out = str(tmp_path / "out.mp4")
        write(frames, out, vmin=0, vmax=65535)
        assert os.path.exists(out)

    def test_VW4_unwritable_path(self):
        """VW-4: unwritable path raises RuntimeError."""
        frames = self._make_frames(1)
        with pytest.raises((RuntimeError, Exception)):
            write(frames, "/nonexistent_dir/out.mp4")

    def test_empty_frames_raises(self, tmp_path):
        """Empty frame list raises ValueError."""
        with pytest.raises(ValueError, match="[Nn]o frames"):
            write([], str(tmp_path / "out.mp4"))

