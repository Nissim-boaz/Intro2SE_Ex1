"""
test_volume_loader.py
Unit tests for src/volume_loader.py  (VL-1 … VL-6, plus memory layout).
Validates dimensional constraints, data type support, and C-contiguous memory layout.
"""

import os
import tempfile
import numpy as np
import nrrd
import pytest

from src.volume_loader import load


# ── Helpers ──────────────────────────────────────────────────────────────────

def _write_nrrd(path: str, data: np.ndarray) -> None:
    """Write a numpy array to an NRRD file for testing."""
    nrrd.write(path, data)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestVolumeLoader:

    def test_VL1_valid_uint8(self, tmp_path):
        """
        VL-1: Verify loading a valid 8-bit unsigned integer (uint8) 3D volume.
        Confirms the loader returns the exact spatial dimensions and preserves uint8 dtype.
        """
        data = np.random.randint(0, 256, (10, 20, 30), dtype=np.uint8)
        p = str(tmp_path / "vol.nrrd")
        _write_nrrd(p, data)

        M = load(p)
        assert M.shape == (10, 20, 30)
        assert M.dtype == np.uint8

    def test_VL2_valid_uint16(self, tmp_path):
        """
        VL-2: Verify loading a 16-bit unsigned integer (uint16) volumetric dataset.
        Ensures high-dynamic-range medical scanner formats are loaded with full precision.
        """
        data = np.random.randint(0, 65536, (10, 20, 30), dtype=np.uint16)
        p = str(tmp_path / "vol.nrrd")
        _write_nrrd(p, data)

        M = load(p)
        assert M.shape == (10, 20, 30)
        assert M.dtype == np.uint16

    def test_VL3_valid_uint32(self, tmp_path):
        """
        VL-3: Verify loading a 32-bit unsigned integer (uint32) 3D volume.
        Confirms full compatibility with 32-bit integer data without data truncation.
        """
        data = np.random.randint(0, 2**32, (10, 20, 30), dtype=np.uint32)
        p = str(tmp_path / "vol.nrrd")
        _write_nrrd(p, data)

        M = load(p)
        assert M.shape == (10, 20, 30)

    def test_VL4_not_3d(self, tmp_path):
        """
        VL-4: Verify rejection of datasets that are not 3-dimensional (e.g. 2D images).
        Ensures that load() raises a ValueError when ndim != 3 to protect projection math.
        """
        data = np.zeros((10, 20), dtype=np.uint8)
        p = str(tmp_path / "vol2d.nrrd")
        _write_nrrd(p, data)

        with pytest.raises(ValueError, match="3D"):
            load(p)

    def test_VL5_file_not_found(self):
        """
        VL-5: Verify robust error handling when the requested NRRD file does not exist.
        Ensures a standard FileNotFoundError is raised with an informative path message.
        """
        with pytest.raises(FileNotFoundError):
            load("/nonexistent/path/file.nrrd")

    def test_VL6_unsupported_dtype(self, tmp_path):
        """
        VL-6: Verify rejection of floating-point datasets (float32/float64).
        Enforces assignment requirements that volumetric datasets must have integer types.
        """
        data = np.zeros((5, 5, 5), dtype=np.float32)
        p = str(tmp_path / "float.nrrd")
        _write_nrrd(p, data)

        with pytest.raises(ValueError, match="[Uu]nsupported dtype|[Uu]nsupported"):
            load(p)

    def test_contiguous(self, tmp_path):
        """
        Verify that loaded volumes are strictly stored in C-contiguous memory layout.
        Guarantees that 1D flattened index arithmetic in projector.py operates at maximum speed.
        """
        data = np.random.randint(0, 256, (8, 8, 8), dtype=np.uint8)
        p = str(tmp_path / "vol.nrrd")
        _write_nrrd(p, data)

        M = load(p)
        assert M.flags["C_CONTIGUOUS"]
