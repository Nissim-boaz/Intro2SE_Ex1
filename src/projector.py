"""
projector.py
Computes the 2D projection of a 3D volume onto a given plane.

The algorithm follows the pseudocode defined in docs/algorithm.md.
The inner loop is fully vectorized with NumPy for maximum performance.
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
        3D volume of shape (sx, sy, sz), unsigned integer dtype.
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
    v_ab = (plane.b  - plane.a1) / plane.Dab
    v_ac = (plane.c  - plane.a2) / plane.Dab

    a1 = plane.a1.copy().astype(float)
    a2 = plane.a2.copy().astype(float)

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

        # --- vectorized inner loop ---
        t = np.arange(n_steps + 1, dtype=float)          # shape (n_steps+1,)
        points = a1 + np.outer(t, dp)                    # shape (n_steps+1, 3)

        ix = np.round(points[:, 0]).astype(int)
        iy = np.round(points[:, 1]).astype(int)
        iz = np.round(points[:, 2]).astype(int)

        # x positions in E (centered), clipped to valid column range
        x_offset = round(cols / 2 - d12 / 2)
        x_indices = np.clip(x_offset + t.astype(int), 0, cols - 1)

        # mask: only in-bounds voxels
        in_bounds = (
            (ix >= 0) & (ix < sx) &
            (iy >= 0) & (iy < sy) &
            (iz >= 0) & (iz < sz)
        )

        # clamp indices for safe indexing (masked out later)
        ix_s = np.clip(ix, 0, sx - 1)
        iy_s = np.clip(iy, 0, sy - 1)
        iz_s = np.clip(iz, 0, sz - 1)

        values = M[ix_s, iy_s, iz_s]
        values[~in_bounds] = 0

        # E[y, x]: y = row (Dab direction), x = col (Dbc direction)
        E[y, x_indices] = values

    return E


def _write_sample(M, E, p, y, x, sx, sy, sz):
    """Write a single voxel sample into E at position (y, x)."""
    ix, iy, iz = round(p[0]), round(p[1]), round(p[2])
    if 0 <= ix < sx and 0 <= iy < sy and 0 <= iz < sz:
        E[y, x] = M[ix, iy, iz]

