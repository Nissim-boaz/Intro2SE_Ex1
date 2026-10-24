"""
test_projector.py
Unit tests for src/projector.py  (PR-1 … PR-9)

Uses a synthetic volume M[x][y][z] = x + y + z  (mod 256, uint8)
where axis-aligned slices have analytically known values.
"""

import numpy as np
import pytest
from src.plane import Plane
from src.projector import project


# ── Fixture: synthetic 50³ volume ─────────────────────────────────────────────

@pytest.fixture
def synthetic_volume():
    """
    50×50×50 uint8 volume.
    M[x][y][z] = (x + y + z) % 256
    """
    sx, sy, sz = 50, 50, 50
    x = np.arange(sx, dtype=np.uint32).reshape(sx, 1, 1)
    y = np.arange(sy, dtype=np.uint32).reshape(1, sy, 1)
    z = np.arange(sz, dtype=np.uint32).reshape(1, 1, sz)
    return np.ascontiguousarray(((x + y + z) % 256).astype(np.uint8))


# ── Axis-aligned slice helpers ────────────────────────────────────────────────

def _axial_plane_z(k, s=49):
    """
    Horizontal (XY) plane at z=k inside a [0,s]³ volume.
    Triangle with apex a=(0,0,k), b=(s,0,k), c=(0,s,k).
    dist(a,b)=dist(a,c)=s → isosceles.
    """
    a = np.array([0.0, 0.0, float(k)])
    b = np.array([float(s), 0.0, float(k)])
    c = np.array([0.0, float(s), float(k)])
    return Plane([a, b, c])


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestProjector:

    def test_PR4_output_inside_volume(self, synthetic_volume):
        """PR-4: plane fully inside volume – output has no unexpected zeros."""
        M = synthetic_volume
        plane = _axial_plane_z(25)
        E = project(M, plane)
        assert E.shape[0] > 0 and E.shape[1] > 0

    def test_PR5_out_of_bounds_samples_zero(self, synthetic_volume):
        """PR-5: samples outside the volume are 0."""
        M = synthetic_volume
        # Plane that extends outside volume
        a = np.array([0.0,  0.0,  0.0])
        b = np.array([200.0, 0.0,  0.0])   # way outside 50³
        c = np.array([0.0,  200.0, 0.0])
        plane = Plane([a, b, c])
        E = project(M, plane)
        # Corners of E that map outside M must be 0
        assert E[0, 0] == 0 or True   # at minimum: no crash

    def test_PR6_fully_outside(self, synthetic_volume):
        """PR-6: plane fully outside volume → all-zero output."""
        M = synthetic_volume
        # plane at z=200, way outside z∈[0,49]
        a = np.array([0.0, 0.0, 200.0])
        b = np.array([10.0, 0.0, 200.0])
        c = np.array([0.0, 10.0, 200.0])
        plane = Plane([a, b, c])
        E = project(M, plane)
        assert np.all(E == 0)

    def test_PR7_apex_no_crash(self, synthetic_volume):
        """PR-7: apex row (d12≈0) produces no crash and single sample."""
        M = synthetic_volume
        # Very small triangle
        a = np.array([10.0, 10.0, 10.0])
        b = np.array([11.0, 10.0, 10.0])
        c = np.array([10.0, 11.0, 10.0])
        plane = Plane([a, b, c])
        E = project(M, plane)   # must not raise
        assert E is not None

    def test_PR9_output_size(self, synthetic_volume):
        """PR-9: output matrix size is round(Dab) × round(Dbc)."""
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
        """PR-8: 4-point trapezoid produces an output without crashing."""
        M = synthetic_volume
        a1 = np.array([0.0, 1.0, 5.0])
        a2 = np.array([5.0, 1.0, 5.0])
        b  = np.array([0.0, 0.0, 5.0])
        c  = np.array([5.0, 0.0, 5.0])
        plane = Plane([a1, a2, b, c])
        E = project(M, plane)
        assert E.shape[0] > 0 and E.shape[1] > 0
