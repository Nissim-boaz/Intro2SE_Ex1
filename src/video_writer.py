"""
video_writer.py
Collects 2D projection frames and writes them to an MP4 video file.

Voxel values are linearly scaled to 8-bit grayscale using the global
[min, max] range of the volume, so brightness is consistent across frames.
"""

import cv2
import numpy as np


def write(frames: list[np.ndarray | None], path: str, fps: int = 30,
          vmin: int = 0, vmax: int = 255, seconds_per_frame: float = 3.0,
          labels: list[str] | None = None) -> None:
    """
    Write a list of 2D frames to an MP4 video with on-screen annotations.

    - Valid planes display a discreet title overlay: e.g. "Plane 1 (Row 2)".
    - Invalid planes (represented by None in frames) display a prominent
      notice indicating the row is invalid and skipped.

    Parameters
    ----------
    frames : list of (np.ndarray or None)
        2D arrays (projection images), or None for invalid rows.
    path : str
        Output .mp4 file path.
    fps : int
        Video frame rate (default 30).
    vmin, vmax : int
        Value range for linear 8-bit normalization.
    seconds_per_frame : float
        Duration in seconds to display each frame (default 3.0).
    labels : list of str, optional
        Descriptive label for each entry in frames.
    """
    if not frames:
        raise ValueError("No frames to write.")

    # Determine output frame size based on valid frames (fallback to 400x400 if none)
    valid_frames = [f for f in frames if f is not None]
    if valid_frames:
        max_rows = max(f.shape[0] for f in valid_frames)
        max_cols = max(f.shape[1] for f in valid_frames)
    else:
        max_rows, max_cols = 400, 400

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (max_cols, max_rows), isColor=False)

    if not writer.isOpened():
        raise RuntimeError(f"Cannot open video writer for path '{path}'.")

    scale = 255.0 / max(vmax - vmin, 1)
    repeat_count = max(1, int(round(fps * seconds_per_frame)))

    for i, frame in enumerate(frames):
        label = labels[i] if labels and i < len(labels) else f"Plane {i + 1}"

        if frame is None:
            # ── Invalid Plane: render explanatory slide ──────────────────
            padded = np.zeros((max_rows, max_cols), dtype=np.uint8)

            # Draw warning box
            cv2.rectangle(padded, (20, 20), (max_cols - 20, max_rows - 20), 200, 2)

            font = cv2.FONT_HERSHEY_SIMPLEX
            # Header line
            cv2.putText(padded, label, (35, 70), font, 0.7, 255, 2, cv2.LINE_AA)
            cv2.putText(padded, "STATUS: INVALID PLANE", (35, 115), font, 0.65, 255, 2, cv2.LINE_AA)
            cv2.putText(padded, "No image displayed (skipped)", (35, 155), font, 0.55, 180, 1, cv2.LINE_AA)

        else:
            # ── Valid Plane: normalize, pad, and add clean title overlay ─
            normalized = np.clip((frame.astype(float) - vmin) * scale, 0, 255).astype(np.uint8)

            padded = np.zeros((max_rows, max_cols), dtype=np.uint8)
            r, c = normalized.shape
            padded[:r, :c] = normalized

            # Semi-dark label banner at the top-left for readability
            text = label
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 1
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)

            # Draw banner background
            cv2.rectangle(padded, (8, 8), (8 + tw + 14, 8 + th + 14), 0, -1)
            cv2.rectangle(padded, (8, 8), (8 + tw + 14, 8 + th + 14), 220, 1)
            cv2.putText(padded, text, (15, 8 + th + 5), font, font_scale, 255, thickness, cv2.LINE_AA)

        # Write frame repeated for seconds_per_frame
        for _ in range(repeat_count):
            writer.write(padded)

    writer.release()
    total_written = len(frames) * repeat_count
    print(f"[VideoWriter] Wrote {len(frames)} plane entries ({total_written} video frames) → '{path}' ({max_cols}×{max_rows} @ {fps} fps)")

