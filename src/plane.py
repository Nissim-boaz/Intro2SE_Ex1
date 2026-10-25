"""
plane.py
Represents and validates a projection plane defined by 3 or 4 3D points.
"""

from __future__ import annotations

import numpy as np

EPS = 0.001  # tolerance for distance comparisons


def _dist(p: np.ndarray, q: np.ndarray) -> float:
    return float(np.linalg.norm(p - q))


class Plane:
    """
    A projection plane defined by an isosceles triangle (3 points)
    or an isosceles trapezoid (4 points).

    Triangle  : apex=a,  base endpoints b, c.   dist(a,b) == dist(a,c).
    Trapezoid : a1, a2 (top), b, c (bottom).    dist(a1,b) == dist(a2,c),
                dist(a1,a2) <= dist(b,c), all four points coplanar.
    """

    def __init__(self, points: list[np.ndarray]):
        """
        Parameters
        ----------
        points : list of np.ndarray
            Either [a, b, c] or [a1, a2, b, c], each a 3-element float array.

        Raises
        ------
        ValueError
            If the points do not form a valid isosceles triangle / trapezoid.
        """
        if len(points) == 3:
            self._init_triangle(points)
        elif len(points) == 4:
            self._init_trapezoid(points)
        else:
            raise ValueError(f"A plane needs 3 or 4 points, got {len(points)}.")

    # ------------------------------------------------------------------
    # Triangle
    # ------------------------------------------------------------------

    def _init_triangle(self, pts):
        a, b, c = [np.asarray(p, dtype=float) for p in pts]

        dab = _dist(a, b)
        dac = _dist(a, c)
        dbc = _dist(b, c)

        if dab < EPS or dac < EPS or dbc < EPS:
            raise ValueError("Degenerate triangle: at least one side has zero length.")

        if _are_collinear(a, b, c):
            raise ValueError("Degenerate triangle: points are collinear.")

        if abs(dab - dac) >= EPS:
            raise ValueError(
                f"Not an isosceles triangle: dist(a,b)={dab:.4f}, dist(a,c)={dac:.4f}."
            )

        self.a1 = a
        self.a2 = a          # both walkers start at the apex
        self.b = b
        self.c = c
        self.Dab = dab       # leg length (= Dac)
        self.Dbc = dbc       # base length
        self.is_trapezoid = False

    # ------------------------------------------------------------------
    # Trapezoid
    # ------------------------------------------------------------------

    def _init_trapezoid(self, pts):
        a1, a2, b, c = [np.asarray(p, dtype=float) for p in pts]

        da1b = _dist(a1, b)
        da2c = _dist(a2, c)
        da1a2 = _dist(a1, a2)
        dbc = _dist(b, c)

        if da1b < EPS or da2c < EPS:
            raise ValueError("Degenerate trapezoid: at least one leg has zero length.")

        if abs(da1b - da2c) >= EPS:
            raise ValueError(
                f"Not isosceles: dist(a1,b)={da1b:.4f}, dist(a2,c)={da2c:.4f}."
            )

        if da1a2 > dbc + EPS:
            raise ValueError(
                f"Trapezoid constraint violated: dist(a1,a2)={da1a2:.4f} > dist(b,c)={dbc:.4f}."
            )

        if not _are_coplanar(a1, a2, b, c):
            raise ValueError("Trapezoid points are not coplanar.")

        self.a1 = a1
        self.a2 = a2
        self.b = b
        self.c = c
        self.Dab = da1b      # leg length
        self.Dbc = dbc       # bottom width
        self.is_trapezoid = True

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __repr__(self):
        kind = "trapezoid" if self.is_trapezoid else "triangle"
        return (
            f"Plane({kind}, a1={self.a1}, a2={self.a2}, "
            f"b={self.b}, c={self.c}, Dab={self.Dab:.2f}, Dbc={self.Dbc:.2f})"
        )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _are_collinear(a, b, c) -> bool:
    """Return True if a, b, c are collinear (cross product ≈ 0)."""
    return float(np.linalg.norm(np.cross(b - a, c - a))) < EPS


def _are_coplanar(a1, a2, b, c) -> bool:
    """Return True if four 3D points lie on the same plane."""
    n = np.cross(b - a1, c - a1)
    norm = np.linalg.norm(n)
    if norm < EPS:
        return False
    n /= norm
    # The fourth point (a2) must lie on the plane defined by a1, b, c
    return abs(float(np.dot(a2 - a1, n))) < EPS

