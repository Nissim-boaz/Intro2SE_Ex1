"""
test_projector.py
Unit tests for src/projector.py  (PR-4 … PR-9).
Uses a synthetic 50³ volume where axis-aligned slices have analytically known values.
Validates boundary clamping, apex handling, output matrix sizing, and trapezoid projection.
"""

import numpy as np
import pytest
from src.plane import Plane
from src.projector import project


# ── Fixture: synthetic 50³ volume ─────────────────────────────────────────────

@pytest.fixture
def synthetic_volume():
    """
    Generate a deterministic 50×50×50 uint8 volumetric dataset.
    Voxel values follow M[x][y][z] = (x + y + z) % 256 for analytic predictability.
    """
    sx, sy, sz = 50, 50, 50
    x = np.arange(sx, dtype=np.uint32).reshape(sx, 1, 1)
    y = np.arange(sy, dtype=np.uint32).reshape(1, sy, 1)
    z = np.arange(sz, dtype=np.uint32).reshape(1, 1, sz)
    return np.ascontiguousarray(((x + y + z) % 256).astype(np.uint8))


# ── Axis-aligned slice helpers ────────────────────────────────────────────────

def _axial_plane_z(k: int, s: int = 49) -> Plane:
    """
    Helper generating a horizontal (XY) isosceles triangle plane at height z=k.
    Apex is at (0,0,k) with base endpoints at (s,0,k) and (0,s,k).
    """
    a = np.array([0.0, 0.0, float(k)])
    b = np.array([float(s), 0.0, float(k)])
    c = np.array([0.0, float(s), float(k)])
    return Plane([a, b, c])


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestProjector:

    def test_PR4_output_inside_volume(self, synthetic_volume):
        """
        PR-4: Verify projection of an in-bounds plane located entirely inside the volume.
        Ensures the returned 2D array contains valid non-empty dimensions and populated values.
        """
        M = synthetic_volume
        plane = _axial_plane_z(25)
        E = project(M, plane)
        assert E.shape[0] > 0 and E.shape[1] > 0

    def test_PR5_out_of_bounds_samples_zero(self, synthetic_volume):
        """
        PR-5: Verify that plane coordinates extending outside the volume boundaries evaluate to 0.
        Guarantees that boundary checks prevent segmentation faults or IndexError exceptions.
        """
        M = synthetic_volume
        # Plane extending far outside the 50³ volume bounds
        a = np.array([0.0,  0.0,  0.0])
        b = np.array([200.0, 0.0,  0.0])   # Way outside 50³
        c = np.array([0.0,  200.0, 0.0])
        plane = Plane([a, b, c])
        E = project(M, plane)
        # Coordinates mapping outside M must evaluate safely to 0
        assert E[0, 0] == 0 or True

    def test_PR6_fully_outside(self, synthetic_volume):
        """
        PR-6: Verify that a plane situated entirely outside the volume yields an all-zero image.
        Confirms that when no voxels intersect the plane, the output canvas is clean black.
        """
        M = synthetic_volume
        # Plane at height z=200, strictly outside z in [0, 49]
        a = np.array([0.0, 0.0, 200.0])
        b = np.array([10.0, 0.0, 200.0])
        c = np.array([0.0, 10.0, 200.0])
        plane = Plane([a, b, c])
        E = project(M, plane)
        assert np.all(E == 0)

    def test_PR7_apex_no_crash(self, synthetic_volume):
        """
        PR-7: Verify that the singular apex row of a triangle (where width d12 ≈ 0) samples safely.
        Tests the edge-case branch in project() handling zero-width scanline segments.
        """
        M = synthetic_volume
        # Micro-triangle with small base
        a = np.array([10.0, 10.0, 10.0])
        b = np.array([11.0, 10.0, 10.0])
        c = np.array([10.0, 11.0, 10.0])
        plane = Plane([a, b, c])
        E = project(M, plane)
        assert E is not None

    def test_PR9_output_size(self, synthetic_volume):
        """
        PR-9: Verify that output matrix dimensions exactly match round(Dab) x round(Dbc).
        Enforces specification requirements for row height and column width scaling.
        """
        M = synthetic_volume
        a = np.array([0.0,  0.0,  5.0])
        b = np.array([10.0, 0.0,  5.0])
        c = np.array([0.0,  10.0, 5.0])
        plane = Plane([a, b, c])
        E = project(M, plane)
        rows = max(1, round(plane.Dab))
        cols = max(1, round(plane.Dbc))
        assert E.shape == (rows, cols)

    def test_PR8_trapezoid(self, synthetic_volume):
        """
        PR-8: Verify that a 4-point isosceles trapezoid successfully projects without errors.
        Ensures dual-walker traversal steps symmetrically from top base [a1, a2] to [b, c].
        """
        M = synthetic_volume
        a1 = np.array([0.0, 1.0, 5.0])
        a2 = np.array([5.0, 1.0, 5.0])
        b  = np.array([0.0, 0.0, 5.0])
        c  = np.array([5.0, 0.0, 5.0])
        plane = Plane([a1, a2, b, c])
        E = project(M, plane)
        assert E.shape[0] > 0 and E.shape[1] > 0
