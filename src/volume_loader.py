"""
volume_loader.py
Loads a 3D NRRD file and returns it as a NumPy array M[x][y][z].
"""

import numpy as np
import nrrd


SUPPORTED_DTYPES = (np.uint8, np.uint16, np.uint32)
MAX_DIM = 1024  # each dimension must be < 2^10


def load(path: str) -> np.ndarray:
    """
    Read a 3D NRRD file and return a C-contiguous uint ndarray of shape (sx, sy, sz).

    Parameters
    ----------
    path : str
        Path to the .nrrd file.

    Returns
    -------
    np.ndarray
        3D array with shape (sx, sy, sz), dtype uint8 / uint16 / uint32.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file is not 3D, has wrong dimensions, or an unsupported dtype.
    """
    try:
        data, header = nrrd.read(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"NRRD file not found: {path}")
    except Exception as e:
        raise ValueError(f"Failed to read NRRD file '{path}': {e}")

    if data.ndim != 3:
        raise ValueError(
            f"Expected a 3D volume, got {data.ndim}D array in '{path}'."
        )

    sx, sy, sz = data.shape
    if not (1 <= sx < MAX_DIM and 1 <= sy < MAX_DIM and 1 <= sz < MAX_DIM):
        raise ValueError(
            f"Volume dimensions {data.shape} out of range [1, {MAX_DIM - 1}]."
        )

    if data.dtype not in [np.dtype(t) for t in SUPPORTED_DTYPES]:
        # Try to cast unsigned integers of other widths
        if np.issubdtype(data.dtype, np.unsignedinteger):
            data = data.astype(np.uint32)
        else:
            raise ValueError(
                f"Unsupported dtype '{data.dtype}'. "
                f"Expected unsigned integer (uint8, uint16, uint32)."
            )

    # Ensure C-contiguous layout for fast indexing
    data = np.ascontiguousarray(data)

    print(f"[VolumeLoader] Loaded '{path}': shape={data.shape}, dtype={data.dtype}")
    return data
