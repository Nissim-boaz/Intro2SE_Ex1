"""
test_plane.py
Unit tests for src/plane.py  (PV-1 … PV-7)
"""

import numpy as np
import pytest
from src.plane import Plane


# ── Triangle tests ────────────────────────────────────────────────────────────

class TestTriangle:

    def test_PV1_valid_triangle(self):
        """PV-1: valid isosceles triangle is accepted."""
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        c = np.array([0.0, 1.0, 0.0])
        # dist(a,b)=1, dist(a,c)=1 → isosceles
        p = Plane([a, b, c])
        assert not p.is_trapezoid
        assert abs(p.Dab - 1.0) < 1e-6

    def test_PV2_not_isosceles(self):
        """PV-2: non-isosceles triangle is rejected."""
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([2.0, 0.0, 0.0])   # dist(a,b)=2
        c = np.array([0.0, 1.0, 0.0])   # dist(a,c)=1
        with pytest.raises(ValueError, match="isosceles"):
            Plane([a, b, c])

    def test_PV3_collinear(self):
        """PV-3: collinear points are rejected."""
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        c = np.array([2.0, 0.0, 0.0])
        with pytest.raises(ValueError, match="[Cc]ollinear|[Dd]egenerate"):
            Plane([a, b, c])

    def test_PV4_zero_side(self):
        """PV-4: zero-length side is rejected."""
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([0.0, 0.0, 0.0])   # same as a
        c = np.array([1.0, 0.0, 0.0])
        with pytest.raises(ValueError, match="[Dd]egenerate|zero"):
            Plane([a, b, c])

    def test_wrong_point_count(self):
        """2 points should raise ValueError."""
        with pytest.raises(ValueError):
            Plane([np.zeros(3), np.ones(3)])


# ── Trapezoid tests ───────────────────────────────────────────────────────────

class TestTrapezoid:

    def _make_valid_trap(self):
        """
        Axis-aligned isosceles trapezoid in the XY plane:
            a1=(0,1,0)  a2=(2,1,0)   (top side, length 2)
            b =(0,0,0)  c =(2,0,0)   (bottom side, length 2)
        legs: dist(a1,b)=dist(a2,c)=1, top<=bottom OK.
        """
        a1 = np.array([0.0, 1.0, 0.0])
        a2 = np.array([2.0, 1.0, 0.0])
        b  = np.array([0.0, 0.0, 0.0])
        c  = np.array([2.0, 0.0, 0.0])
        return a1, a2, b, c

    def test_PV5_valid_trapezoid(self):
        """PV-5: valid isosceles trapezoid is accepted."""
        a1, a2, b, c = self._make_valid_trap()
        p = Plane([a1, a2, b, c])
        assert p.is_trapezoid

    def test_PV6_top_wider_than_bottom(self):
        """PV-6: dist(a1,a2) > dist(b,c) is rejected."""
        a1 = np.array([0.0, 1.0, 0.0])
        a2 = np.array([5.0, 1.0, 0.0])   # top=5, bottom=2 → invalid
        b  = np.array([0.0, 0.0, 0.0])
        c  = np.array([2.0, 0.0, 0.0])
        with pytest.raises(ValueError):
            Plane([a1, a2, b, c])

    def test_PV7_not_coplanar(self):
        """PV-7: non-coplanar points are rejected."""
        a1 = np.array([0.0, 1.0, 0.0])
        a2 = np.array([1.0, 1.0, 5.0])   # lifted out of the XY plane
        b  = np.array([0.0, 0.0, 0.0])
        c  = np.array([1.0, 0.0, 0.0])
        with pytest.raises(ValueError, match="[Cc]oplanar|isosceles"):
            Plane([a1, a2, b, c])
