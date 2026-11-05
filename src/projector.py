"""
projector.py
Computes the 2D projection of a 3D volumetric array onto a geometric plane.
Implements vectorized scanline sampling with nearest-neighbor voxel interpolation.
"""

from __future__ import annotations

import numpy as np
from src.plane import Plane


def project(M: np.ndarray, plane: Plane) -> np.ndarray:
    """
    Project the 3D volume M onto the given plane and return a 2D density image.
    Follows vectorized scanline traversal along the plane legs and width segments.

    Algorithm:
        1. Allocate output 2D image E of shape (round(Dab), round(Dbc)).
        2. Compute unit step vectors v_ab and v_ac along the two plane legs.
        3. For each scanline row y in 0 .. rows-1:
               Advance edge walkers: a1 += v_ab, a2 += v_ac.
               Interpolate 3D points along segment [a1, a2] in 1.0 unit steps.
               Round coordinates (nearest-neighbor) to integer indices (ix, iy, iz).
               Filter in-bounds voxels and sample densities from M into centered E[y].
        4. Return 2D projection array E.

    Parameters
    ----------
    M : np.ndarray
        3D volume array of shape (sx, sy, sz) with integer densities.
    plane : Plane
        A validated Plane object (isosceles triangle or trapezoid).

    Returns
    -------
    np.ndarray
        2D array of shape (rows, cols) = (round(Dab), round(Dbc)),
        with the same data type as M. Out-of-bounds samples evaluate to 0.
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
            # Apex row (triangle top): single sample at center
            _write_sample(M, E, a1, y, cols // 2, sx, sy, sz)
            continue

        dp = (a2 - a1) / d12
        n_steps = round(d12)

        # Vectorized 1D coordinate arrays along the current scanline segment
        t = np.arange(n_steps + 1, dtype=float)
        ix = np.round(a1[0] + t * dp[0]).astype(int)
        iy = np.round(a1[1] + t * dp[1]).astype(int)
        iz = np.round(a1[2] + t * dp[2]).astype(int)

        # Centered horizontal x-coordinates in output canvas E
        x_offset = round(cols / 2 - d12 / 2)
        x_indices = np.clip(x_offset + t.astype(int), 0, cols - 1)

        # In-bounds boundary check for volume dimensions
        in_bounds = (
            (ix >= 0) & (ix < sx) &
            (iy >= 0) & (iy < sy) &
            (iz >= 0) & (iz < sz)
        )

        # Contiguous 1D flat memory indexing for maximum cache locality
        flat_idx = ix[in_bounds] * sy_sz + iy[in_bounds] * sz + iz[in_bounds]
        E[y, x_indices[in_bounds]] = M_flat[flat_idx]

    return E


def _write_sample(M: np.ndarray, E: np.ndarray, p: np.ndarray,
                  y: int, x: int, sx: int, sy: int, sz: int) -> None:
    """
    Sample a single voxel at coordinate p and store it in E[y, x] if inside bounds.
    Used for the single apex point at the top of triangle planes.
    """
    ix, iy, iz = round(p[0]), round(p[1]), round(p[2])
    if 0 <= ix < sx and 0 <= iy < sy and 0 <= iz < sz:
        E[y, x] = M[ix, iy, iz]
