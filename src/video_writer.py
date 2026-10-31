"""
video_writer.py
Collects 2D projection frames and writes them to an MP4 video file.

Frames are dynamically contrast-enhanced to 8-bit grayscale for maximum
visual clarity, and centered within the video canvas.
"""

from __future__ import annotations

import cv2
import numpy as np


def write(frames: list[np.ndarray | None], path: str, fps: int = 30,
          vmin: int = 0, vmax: int = 255, seconds_per_frame: float = 3.0,
          labels: list[str] | None = None) -> None:
    """
    Write a list of 2D frames to an MP4 video with on-screen annotations.

    - Valid planes are centered within the canvas, contrast-enhanced, and display
      a discreet corner label.
    - Invalid planes display a centered explanatory slide.

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

    # Determine canvas dimensions based on largest frame
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

    repeat_count = max(1, int(round(fps * seconds_per_frame)))

    for i, frame in enumerate(frames):
        label = labels[i] if labels and i < len(labels) else f"Plane {i + 1}"

        if frame is None:
            # -- Invalid Plane: render centered explanatory slide -----------
            padded = np.zeros((max_rows, max_cols), dtype=np.uint8)

            inset = max(10, min(20, max_rows // 10, max_cols // 10))
            cv2.rectangle(padded, (inset, inset), (max_cols - inset, max_rows - inset), 160, 1)

            font = cv2.FONT_HERSHEY_SIMPLEX
            lines = [
                (label, 0.65, 255, 2),
                ("STATUS: INVALID PLANE", 0.55, 220, 1),
                ("No image displayed (skipped)", 0.45, 170, 1),
            ]
            line_spacing = 38
            total_h = len(lines) * line_spacing
            start_y = max(inset + 35, (max_rows - total_h) // 2 + 25)

            for idx, (txt, f_scale, color, thk) in enumerate(lines):
                (tw, th), _ = cv2.getTextSize(txt, font, f_scale, thk)
                tx = max(inset + 10, (max_cols - tw) // 2)
                ty = start_y + idx * line_spacing
                if 0 < ty < max_rows - inset:
                    cv2.putText(padded, txt, (tx, ty), font, f_scale, color, thk, cv2.LINE_AA)

        else:
            # -- Valid Plane: contrast enhancement, center padding, and corner label -
            # Enhanced per-frame contrast auto-leveling
            f_max = float(frame.max())
            f_min = float(frame.min())
            if f_max > f_min:
                normalized = np.clip((frame.astype(float) - f_min) / (f_max - f_min) * 255.0, 0, 255).astype(np.uint8)
                # Apply subtle unsharp masking to enhance micro-contrast and tissue edges
                if normalized.shape[0] > 10 and normalized.shape[1] > 10:
                    blur = cv2.GaussianBlur(normalized, (0, 0), sigmaX=1.0)
                    sharpened = cv2.addWeighted(normalized, 1.35, blur, -0.35, 0)
                    normalized = np.clip(sharpened, 0, 255).astype(np.uint8)
            else:
                normalized = np.zeros_like(frame, dtype=np.uint8)

            # Center the slice inside the video canvas
            padded = np.zeros((max_rows, max_cols), dtype=np.uint8)
            r, c = normalized.shape
            r_off = (max_rows - r) // 2
            c_off = (max_cols - c) // 2
            padded[r_off : r_off + r, c_off : c_off + c] = normalized

            # Small, discreet corner label tucked in the corner
            text = label
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.38
            thickness = 1
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)

            cv2.rectangle(padded, (4, 4), (4 + tw + 8, 4 + th + 6), 0, -1)
            cv2.putText(padded, text, (8, 4 + th + 2), font, font_scale, 220, thickness, cv2.LINE_AA)

        # Write frame repeated for seconds_per_frame
        for _ in range(repeat_count):
            writer.write(padded)

    writer.release()
    total_written = len(frames) * repeat_count
    print(f"[VideoWriter] Wrote {len(frames)} plane entries ({total_written} video frames) -> '{path}' ({max_cols}x{max_rows} @ {fps} fps)")
