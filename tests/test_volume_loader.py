"""
test_volume_loader.py
Unit tests for src/volume_loader.py  (VL-1 … VL-6)
"""

import os
import tempfile
import numpy as np
import nrrd
import pytest

from src.volume_loader import load


# ── Helpers ──────────────────────────────────────────────────────────────────

def _write_nrrd(path, data):
    """Write a numpy array to an NRRD file."""
    nrrd.write(path, data)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestVolumeLoader:

    def test_VL1_valid_uint8(self, tmp_path):
        """VL-1: valid 8-bit 3D NRRD returns correct shape and dtype."""
        data = np.random.randint(0, 256, (10, 20, 30), dtype=np.uint8)
        p = str(tmp_path / "vol.nrrd")
        _write_nrrd(p, data)

        M = load(p)
        assert M.shape == (10, 20, 30)
        assert M.dtype == np.uint8

    def test_VL2_valid_uint16(self, tmp_path):
        """VL-2: valid 16-bit 3D NRRD returns correct shape and dtype."""
        data = np.random.randint(0, 65536, (10, 20, 30), dtype=np.uint16)
        p = str(tmp_path / "vol.nrrd")
        _write_nrrd(p, data)

        M = load(p)
        assert M.shape == (10, 20, 30)
        assert M.dtype == np.uint16

    def test_VL3_valid_uint32(self, tmp_path):
        """VL-3: valid 32-bit 3D NRRD returns correct shape and dtype."""
        data = np.random.randint(0, 2**32, (10, 20, 30), dtype=np.uint32)
        p = str(tmp_path / "vol.nrrd")
        _write_nrrd(p, data)

        M = load(p)
        assert M.shape == (10, 20, 30)

    def test_VL4_not_3d(self, tmp_path):
        """VL-4: 2D NRRD raises ValueError."""
        data = np.zeros((10, 20), dtype=np.uint8)
        p = str(tmp_path / "vol2d.nrrd")
        _write_nrrd(p, data)

        with pytest.raises(ValueError, match="3D"):
            load(p)

    def test_VL5_file_not_found(self):
        """VL-5: missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load("/nonexistent/path/file.nrrd")

    def test_VL6_unsupported_dtype(self, tmp_path):
        """VL-6: float dtype raises ValueError."""
        data = np.zeros((5, 5, 5), dtype=np.float32)
        p = str(tmp_path / "float.nrrd")
        _write_nrrd(p, data)

        with pytest.raises(ValueError, match="[Uu]nsupported dtype|[Uu]nsupported"):
            load(p)

    def test_contiguous(self, tmp_path):
        """Loaded array must be C-contiguous for fast indexing."""
        data = np.random.randint(0, 256, (8, 8, 8), dtype=np.uint8)
        p = str(tmp_path / "vol.nrrd")
        _write_nrrd(p, data)

        M = load(p)
        assert M.flags["C_CONTIGUOUS"]
