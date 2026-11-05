"""
plane.py
Represents and validates a projection plane defined by 3 or 4 3D points.
Enforces geometric constraints for isosceles triangles and isosceles trapezoids.
"""

from __future__ import annotations

import numpy as np

EPS = 0.001  # Tolerance for distance comparisons and coplanarity checks


def _dist(p: np.ndarray, q: np.ndarray) -> float:
    """
    Calculate the Euclidean distance between two 3D coordinates.

    Args:
        p (np.ndarray): First 3D point (x, y, z).
        q (np.ndarray): Second 3D point (x, y, z).

    Returns:
        float: Euclidean distance ||p - q||.
    """
    return float(np.linalg.norm(p - q))


class Plane:
    """
    A geometric projection plane defined by an isosceles triangle (3 points)
    or an isosceles trapezoid (4 points).

    Triangle  : apex=a,  base endpoints b, c.   dist(a,b) == dist(a,c).
    Trapezoid : a1, a2 (top), b, c (bottom).    dist(a1,b) == dist(a2,c),
                dist(a1,a2) <= dist(b,c), all four points coplanar.
    """

    def __init__(self, points: list[np.ndarray]):
        """
        Initialize and validate a plane from a list of 3 or 4 3D points.
        Dispatches to triangle or trapezoid validation based on point count.

        Parameters
        ----------
        points : list of np.ndarray
            Either [a, b, c] or [a1, a2, b, c], each a 3-element float array.

        Raises
        ------
        ValueError
            If points do not form a valid isosceles triangle or trapezoid.
        """
        if len(points) == 3:
            self._init_triangle(points)
        elif len(points) == 4:
            self._init_trapezoid(points)
        else:
            raise ValueError(f"A plane needs 3 or 4 points, got {len(points)}.")

    # ------------------------------------------------------------------
    # Triangle Initialization & Validation
    # ------------------------------------------------------------------

    def _init_triangle(self, pts: list[np.ndarray]) -> None:
        """
        Validate and initialize an isosceles triangle plane from 3 points.

        Algorithm:
            1. Compute edge lengths: dab = dist(a,b), dac = dist(a,c), dbc = dist(b,c).
            2. Verify all edge lengths > EPS and points are not collinear.
            3. Verify isosceles condition: |dab - dac| < EPS.
            4. Set walker endpoints: a1=a, a2=a, b=b, c=c, Dab=dab, Dbc=dbc.

        Args:
            pts: List of 3 points [a, b, c] where a is the apex.
        """
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
        self.a2 = a          # Both walkers start at the apex for a triangle
        self.b = b
        self.c = c
        self.Dab = dab       # Leg length (= Dac)
        self.Dbc = dbc       # Base length
        self.is_trapezoid = False

    # ------------------------------------------------------------------
    # Trapezoid Initialization & Validation
    # ------------------------------------------------------------------

    def _init_trapezoid(self, pts: list[np.ndarray]) -> None:
        """
        Validate and initialize an isosceles trapezoid plane from 4 points.

        Algorithm:
            1. Compute leg lengths: da1b = dist(a1,b), da2c = dist(a2,c).
            2. Verify non-zero leg lengths.
            3. Verify equal legs (isosceles): |da1b - da2c| < EPS.
            4. Verify base constraint: dist(a1,a2) <= dist(b,c) + EPS.
            5. Verify 4-point coplanarity: normal(a1,b,c) dot (a2 - a1) < EPS.
            6. Set walker endpoints: a1, a2, b, c, Dab=da1b, Dbc=dist(b,c).

        Args:
            pts: List of 4 points [a1, a2, b, c] defining top base and bottom base.
        """
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
        self.Dab = da1b      # Leg length
        self.Dbc = dbc       # Bottom base width
        self.is_trapezoid = True

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a readable string representation of the plane parameters."""
        kind = "trapezoid" if self.is_trapezoid else "triangle"
        return (
            f"Plane({kind}, a1={self.a1}, a2={self.a2}, "
            f"b={self.b}, c={self.c}, Dab={self.Dab:.2f}, Dbc={self.Dbc:.2f})"
        )


# ----------------------------------------------------------------------
# Geometric Helper Functions
# ----------------------------------------------------------------------

def _are_collinear(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
    """
    Check if three 3D points lie on the same straight line.
    Evaluates whether the cross product of (b - a) and (c - a) is zero within EPS.
    """
    return float(np.linalg.norm(np.cross(b - a, c - a))) < EPS


def _are_coplanar(a1: np.ndarray, a2: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
    """
    Check if four 3D points lie on the exact same geometric plane.
    Computes unit normal from (a1, b, c) and checks distance of a2 to the plane.
    """
    n = np.cross(b - a1, c - a1)
    norm = np.linalg.norm(n)
    if norm < EPS:
        return False
    n /= norm
    # The fourth point (a2) must lie on the plane defined by a1, b, c
    return abs(float(np.dot(a2 - a1, n))) < EPS
