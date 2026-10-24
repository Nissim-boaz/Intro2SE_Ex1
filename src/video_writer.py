"""
video_writer.py
Collects 2D projection frames and writes them to an MP4 video file.

Voxel values are linearly scaled to 8-bit grayscale using the global
[min, max] range of the volume, so brightness is consistent across frames.
"""

import cv2
import numpy as np


def write(frames: list[np.ndarray], path: str, fps: int = 30,
          vmin: int = 0, vmax: int = 255) -> None:
    """
    Write a list of 2D frames to an MP4 video.

    All frames are padded with zeros (black) to the maximum width and
    height among all frames, so every frame has the same size.

    Parameters
    ----------
    frames : list of np.ndarray
        2D arrays (projection images). Any unsigned integer dtype.
    path : str
        Output .mp4 file path (overwritten if it exists).
    fps : int
        Video frame rate (default 30).
    vmin, vmax : int
        Value range used for linear normalization to 8-bit.
        Typically the global min/max of the volume.

    Raises
    ------
    ValueError
        If frames is empty.
    RuntimeError
        If the video writer cannot open the output path.
    """
    if not frames:
        raise ValueError("No frames to write.")

    # Determine output frame size (max width × height)
    max_rows = max(f.shape[0] for f in frames)
    max_cols = max(f.shape[1] for f in frames)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (max_cols, max_rows), isColor=False)

    if not writer.isOpened():
        raise RuntimeError(f"Cannot open video writer for path '{path}'.")

    scale = 255.0 / max(vmax - vmin, 1)

    for frame in frames:
        # Normalize to 8-bit
        normalized = np.clip((frame.astype(float) - vmin) * scale, 0, 255).astype(np.uint8)

        # Pad to (max_rows, max_cols) with zeros
        padded = np.zeros((max_rows, max_cols), dtype=np.uint8)
        r, c = normalized.shape
        padded[:r, :c] = normalized

        writer.write(padded)

    writer.release()
    print(f"[VideoWriter] Wrote {len(frames)} frames → '{path}' ({max_cols}×{max_rows} @ {fps} fps)")
