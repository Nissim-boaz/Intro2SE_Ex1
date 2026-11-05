"""
test_plane.py
Unit tests for src/plane.py  (PV-1 … PV-7, plus point count constraints).
Validates geometric rules for isosceles triangles and isosceles trapezoids.
"""

import numpy as np
import pytest
from src.plane import Plane


# ── Triangle tests ────────────────────────────────────────────────────────────

class TestTriangle:

    def test_PV1_valid_triangle(self):
        """
        PV-1: Verify that a valid isosceles triangle is successfully constructed.
        Checks that dist(a, b) == dist(a, c) within EPS and sets correct walker lengths.
        """
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        c = np.array([0.0, 1.0, 0.0])
        # dist(a,b)=1, dist(a,c)=1 → isosceles
        p = Plane([a, b, c])
        assert not p.is_trapezoid
        assert abs(p.Dab - 1.0) < 1e-6

    def test_PV2_not_isosceles(self):
        """
        PV-2: Verify rejection of triangles with unequal legs.
        Ensures a ValueError is raised when |dist(a,b) - dist(a,c)| exceeds tolerance EPS.
        """
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([2.0, 0.0, 0.0])   # dist(a,b)=2
        c = np.array([0.0, 1.0, 0.0])   # dist(a,c)=1
        with pytest.raises(ValueError, match="isosceles"):
            Plane([a, b, c])

    def test_PV3_collinear(self):
        """
        PV-3: Verify rejection of degenerate triangles where all 3 points lie on the same line.
        Asserts that collinear points fail the cross-product check and raise a ValueError.
        """
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        c = np.array([2.0, 0.0, 0.0])
        with pytest.raises(ValueError, match="[Cc]ollinear|[Dd]egenerate"):
            Plane([a, b, c])

    def test_PV4_zero_side(self):
        """
        PV-4: Verify rejection of degenerate triangles containing duplicate points (zero side length).
        Ensures that coincident vertices (e.g. a == b) immediately raise a ValueError.
        """
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([0.0, 0.0, 0.0])   # Same point as a
        c = np.array([1.0, 0.0, 0.0])
        with pytest.raises(ValueError, match="[Dd]egenerate|zero"):
            Plane([a, b, c])

    def test_wrong_point_count(self):
        """
        Verify that plane initialization with invalid point counts (e.g. 2 points) raises ValueError.
        Guarantees that planes can only be instantiated with exactly 3 or 4 vertices.
        """
        with pytest.raises(ValueError):
            Plane([np.zeros(3), np.ones(3)])


# ── Trapezoid tests ───────────────────────────────────────────────────────────

class TestTrapezoid:

    def _make_valid_trap(self):
        """
        Helper returning vertices for an axis-aligned isosceles trapezoid in the XY plane:
            a1=(0,1,0)  a2=(2,1,0)   (top side, length 2)
            b =(0,0,0)  c =(2,0,0)   (bottom side, length 2)
        Both legs have length 1, top <= bottom, and all points lie on z=0.
        """
        a1 = np.array([0.0, 1.0, 0.0])
        a2 = np.array([2.0, 1.0, 0.0])
        b  = np.array([0.0, 0.0, 0.0])
        c  = np.array([2.0, 0.0, 0.0])
        return a1, a2, b, c

    def test_PV5_valid_trapezoid(self):
        """
        PV-5: Verify that a valid isosceles trapezoid is successfully accepted.
        Confirms that equal legs and parallel coplanar bases correctly set is_trapezoid=True.
        """
        a1, a2, b, c = self._make_valid_trap()
        p = Plane([a1, a2, b, c])
        assert p.is_trapezoid

    def test_PV6_top_wider_than_bottom(self):
        """
        PV-6: Verify rejection of inverted trapezoids where top base is wider than bottom base.
        Asserts that dist(a1, a2) > dist(b, c) violates trapezoid constraints and raises ValueError.
        """
        a1 = np.array([0.0, 1.0, 0.0])
        a2 = np.array([5.0, 1.0, 0.0])   # top=5, bottom=2 → invalid
        b  = np.array([0.0, 0.0, 0.0])
        c  = np.array([2.0, 0.0, 0.0])
        with pytest.raises(ValueError):
            Plane([a1, a2, b, c])

    def test_PV7_not_coplanar(self):
        """
        PV-7: Verify rejection of 4-point sets that do not lie on a single 3D plane.
        Asserts that when a vertex is displaced out of the plane, coplanarity validation raises ValueError.
        """
        a1 = np.array([0.0, 1.0, 0.0])
        a2 = np.array([1.0, 1.0, 5.0])   # Lifted out of the XY plane (z=5)
        b  = np.array([0.0, 0.0, 0.0])
        c  = np.array([1.0, 0.0, 0.0])
        with pytest.raises(ValueError, match="[Cc]oplanar|isosceles"):
            Plane([a1, a2, b, c])
