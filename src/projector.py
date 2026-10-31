"""
projector.py
Computes the 2D projection of a 3D volume onto a given plane.

The algorithm follows the specification in docs/algorithm.md.
The projection is fully vectorized with NumPy for maximum performance.
"""

from __future__ import annotations

import numpy as np
from src.plane import Plane


def project(M: np.ndarray, plane: Plane) -> np.ndarray:
    """
    Project the 3D volume M onto the given plane and return a 2D image.

    Parameters
    ----------
    M : np.ndarray
        3D volume of shape (sx, sy, sz), integer dtype.
    plane : Plane
        A validated Plane object (triangle or trapezoid).

    Returns
    -------
    np.ndarray
        2D array of shape (rows, cols) = (round(Dab), round(Dbc)),
        same dtype as M. Out-of-bounds samples are 0.
    """
    sx, sy, sz = M.shape

    rows = max(1, round(plane.Dab))
    cols = max(1, round(plane.Dbc))

    E = np.zeros((rows, cols), dtype=M.dtype)

    v_ab = (plane.b - plane.a1) / plane.Dab
    dp = (plane.c - plane.b) / plane.Dbc

    d_top = 0.0 if not plane.is_trapezoid else float(np.linalg.norm(plane.a2 - plane.a1))
    step_slope = (plane.Dbc - d_top) / plane.Dab

    y_vals = np.arange(1, rows + 1, dtype=np.float64)
    d12 = d_top + y_vals * step_slope
    n_steps = np.round(d12).astype(np.int32)
    n_steps[d12 < 1e-9] = 0
    counts = n_steps + 1

    y_rep = np.repeat(np.arange(rows, dtype=np.int32), counts)

    ends = np.cumsum(counts)
    t = np.ones(len(y_rep), dtype=np.int32)
    t[0] = 0
    t[ends[:-1]] -= counts[:-1]
    np.cumsum(t, out=t)

    y_p1 = y_rep + 1
    ix = np.round(plane.a1[0] + y_p1 * v_ab[0] + t * dp[0]).astype(np.int32)
    iy = np.round(plane.a1[1] + y_p1 * v_ab[1] + t * dp[1]).astype(np.int32)
    iz = np.round(plane.a1[2] + y_p1 * v_ab[2] + t * dp[2]).astype(np.int32)

    x_offset = np.round(cols * 0.5 - d12 * 0.5).astype(np.int32)
    x_indices = np.clip(x_offset[y_rep] + t, 0, cols - 1)

    in_bounds = (
        (ix >= 0) & (ix < sx) &
        (iy >= 0) & (iy < sy) &
        (iz >= 0) & (iz < sz)
    )

    E[y_rep[in_bounds], x_indices[in_bounds]] = M[ix[in_bounds], iy[in_bounds], iz[in_bounds]]
    return E
