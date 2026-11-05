"""
volume_loader.py
Loads a 3D NRRD volumetric data file and returns it as a NumPy array M[x][y][z].
"""

from __future__ import annotations

import numpy as np
import nrrd

SUPPORTED_DTYPES = (
    np.uint8, np.uint16, np.uint32,
    np.int8, np.int16, np.int32
)
MAX_DIM = 1024  # Each dimension must be strictly less than 2^10 (1024)


def load(path: str) -> np.ndarray:
    """
    Load a 3D NRRD file into memory and validate its shape and integer data type.
    Ensures C-contiguous memory layout for optimal slice projection performance.

    Algorithm:
        1. Read NRRD file and extract header metadata.
        2. Verify volume is strictly 3-dimensional and within dimension limits (<1024).
        3. Validate supported integer data type (cast other integer widths to int32).
        4. Enforce C-contiguous memory layout and return ndarray M[x, y, z].

    Parameters
    ----------
    path : str
        Path to the 3D .nrrd volumetric file.

    Returns
    -------
    np.ndarray
        3D array with shape (sx, sy, sz) representing the volumetric density data.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the specified path.
    ValueError
        If the data is not 3D, dimensions exceed limits, or data type is unsupported.
    """
    try:
        data, header = nrrd.read(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"NRRD file not found: {path}")
    except Exception as e:
        raise ValueError(f"Failed to read NRRD file '{path}': {e}")

    # Validate volume dimensionality
    if data.ndim != 3:
        raise ValueError(
            f"Expected a 3D volume, got {data.ndim}D array in '{path}'."
        )

    # Validate volume coordinate bounds (< 2^10)
    sx, sy, sz = data.shape
    if not (1 <= sx < MAX_DIM and 1 <= sy < MAX_DIM and 1 <= sz < MAX_DIM):
        raise ValueError(
            f"Volume dimensions {data.shape} out of range [1, {MAX_DIM - 1}]."
        )

    # Validate data type (supported integers: uint8, uint16, uint32, int8, int16, int32)
    if data.dtype not in [np.dtype(t) for t in SUPPORTED_DTYPES]:
        if np.issubdtype(data.dtype, np.integer):
            data = data.astype(np.int32)
        else:
            raise ValueError(
                f"Unsupported dtype '{data.dtype}'. "
                f"Expected integer format (e.g. int16, uint16, uint8)."
            )

    # Enforce contiguous memory for high-speed linear index access
    data = np.ascontiguousarray(data)

    print(f"[VolumeLoader] Loaded '{path}': shape={data.shape}, dtype={data.dtype}")
    return data

