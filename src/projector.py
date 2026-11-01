"""
projector.py
Computes the 2D projection of a 3D volume onto a given plane.

The algorithm follows the pseudocode defined in docs/algorithm.md.
The scanline inner loop is vectorized with NumPy for high performance and stability,
using 1D coordinate vectors and contiguous flattened memory indexing.
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

    E = np.zeros((rows, cols), dtype=M.dtype)  # E[y][x]: y=row(Dab), x=col(Dbc)

    # Unit vectors along the two legs
    v_ab = (plane.b - plane.a1) / plane.Dab
    v_ac = (plane.c - plane.a2) / plane.Dab

    a1 = plane.a1.copy().astype(float)
    a2 = plane.a2.copy().astype(float)

    # 1D flattened view and stride multipliers for fast contiguous memory indexing
    M_flat = M.reshape(-1)
    sy_sz = sy * sz

    for y in range(rows):
        a1 += v_ab
        a2 += v_ac

        d12 = float(np.linalg.norm(a2 - a1))

        if d12 < 1e-9:
            # Apex row: single sample at center
            _write_sample(M, E, a1, y, cols // 2, sx, sy, sz)
            continue

        dp = (a2 - a1) / d12
        n_steps = round(d12)

        # Vectorized 1D coordinate arrays (avoids expensive 2D np.outer)
        t = np.arange(n_steps + 1, dtype=float)
        ix = np.round(a1[0] + t * dp[0]).astype(int)
        iy = np.round(a1[1] + t * dp[1]).astype(int)
        iz = np.round(a1[2] + t * dp[2]).astype(int)

        # x positions in E (centered), clipped to valid column range
        x_offset = round(cols / 2 - d12 / 2)
        x_indices = np.clip(x_offset + t.astype(int), 0, cols - 1)

        # Mask: only in-bounds voxels
        in_bounds = (
            (ix >= 0) & (ix < sx) &
            (iy >= 0) & (iy < sy) &
            (iz >= 0) & (iz < sz)
        )

        # Contiguous 1D flat indexing (eliminates 3D index tuples, np.clip and double copy)
        flat_idx = ix[in_bounds] * sy_sz + iy[in_bounds] * sz + iz[in_bounds]
        E[y, x_indices[in_bounds]] = M_flat[flat_idx]

    return E


def _write_sample(M, E, p, y, x, sx, sy, sz):
    """Write a single voxel sample into E at position (y, x)."""
    ix, iy, iz = round(p[0]), round(p[1]), round(p[2])
    if 0 <= ix < sx and 0 <= iy < sy and 0 <= iz < sz:
        E[y, x] = M[ix, iy, iz]
