"""
video_writer.py
Collects 2D projection frames and writes them to an MP4 video file.
Enhances contrast to 8-bit grayscale, centers frames, and renders error slides.
Groups consecutive identical errors into unified explanatory notices.
"""

from __future__ import annotations

import re
import cv2
import numpy as np


def classify_error(err: str | None) -> str:
    """
    Classify a raw error message into a concise, standardized category.
    Used for display on on-screen video error slides.

    Parameters
    ----------
    err : str or None
        Raw error message from the parser or plane validation.

    Returns
    -------
    str
        Human-readable category (e.g. 'Triangle Not Isosceles', 'Point Count Mismatch').
    """
    if not err:
        return "Invalid Plane Geometry"
    err_lower = err.lower()
    if "inf" in err_lower or "nan" in err_lower:
        return "Invalid Values (NaN / Inf)"
    if "collinear" in err_lower:
        return "Collinear Points (Degenerate)"
    if "zero length" in err_lower or "zero-length" in err_lower or "zero_side" in err_lower:
        return "Zero-Length Side (Degenerate)"
    if "not coplanar" in err_lower or "coplanar" in err_lower:
        return "Points Not Coplanar"
    if "triangle" in err_lower and "isosceles" in err_lower:
        return "Triangle Not Isosceles"
    if "trapezoid constraint" in err_lower or "wider" in err_lower or "dist(a1,a2)" in err_lower:
        return "Top Base Wider Than Bottom"
    if "trapezoid" in err_lower or "not isosceles" in err_lower:
        return "Trapezoid Not Isosceles"
    if "declared" in err_lower and ("provided" in err_lower or "points" in err_lower or "coords" in err_lower or "values" in err_lower):
        return "Point Count Mismatch"
    if "expected" in err_lower and ("numbers" in err_lower or "values" in err_lower or "got" in err_lower):
        return "Invalid Coordinate Count"
    if "non-numeric" in err_lower or "numeric" in err_lower:
        return "Non-Numeric Values"
    return "Invalid Plane Geometry"


def format_group_label(start_idx: int, end_idx: int, labels: list[str] | None) -> str:
    """
    Format an on-screen title for a single plane or a grouped range of consecutive planes.
    Extracts numerical indices and row references from label strings.

    Parameters
    ----------
    start_idx : int
        Starting index of the plane sequence.
    end_idx : int
        Ending index of the plane sequence (inclusive).
    labels : list of str, optional
        Pre-formatted per-plane labels.

    Returns
    -------
    str
        Formatted string (e.g. 'Plane 1', 'Planes: 1-25', or 'Planes: 1-25 (Rows 2-26)').
    """
    if start_idx == end_idx:
        return labels[start_idx] if labels and start_idx < len(labels) else f"Plane {start_idx + 1}"

    start_lbl = labels[start_idx] if labels and start_idx < len(labels) else f"Plane {start_idx + 1}"
    end_lbl = labels[end_idx] if labels and end_idx < len(labels) else f"Plane {end_idx + 1}"

    m_start_p = re.search(r"Plane\s+(\d+)", start_lbl, re.IGNORECASE)
    m_end_p = re.search(r"Plane\s+(\d+)", end_lbl, re.IGNORECASE)

    m_start_r = re.search(r"Row\s+(\d+)", start_lbl, re.IGNORECASE)
    m_end_r = re.search(r"Row\s+(\d+)", end_lbl, re.IGNORECASE)

    if m_start_p and m_end_p:
        p_text = f"Planes: {m_start_p.group(1)}-{m_end_p.group(1)}"
    else:
        p_text = f"Planes: {start_idx + 1}-{end_idx + 1}"

    if m_start_r and m_end_r:
        return f"{p_text} (Rows {m_start_r.group(1)}-{m_end_r.group(1)})"

    return p_text


def render_error_slide(max_rows: int, max_cols: int, label: str,
                       sub_category: str, is_group: bool = False) -> np.ndarray:
    """
    Render a centered explanatory error notice on a black video canvas.
    Automatically scales font sizes to ensure text never overflows canvas bounds.

    Parameters
    ----------
    max_rows, max_cols : int
        Dimensions of the video frame canvas.
    label : str
        Top header identifying the plane index or aggregated range.
    sub_category : str
        Classified error category explaining why the plane is invalid.
    is_group : bool
        True if the slide represents multiple consecutive planes.

    Returns
    -------
    np.ndarray
        8-bit grayscale image of shape (max_rows, max_cols).
    """
    padded = np.zeros((max_rows, max_cols), dtype=np.uint8)

    inset = max(10, min(20, max_rows // 10, max_cols // 10))
    cv2.rectangle(padded, (inset, inset), (max_cols - inset, max_rows - inset), 160, 1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    main_title = "ERROR: INVALID PLANES" if is_group else "ERROR: INVALID PLANE"
    subtitle = "No image displayed (skipped)"

    lines = [
        (label, 0.65, 255, 2),
        (main_title, 0.60, 220, 2),
        (sub_category, 0.50, 190, 1),
        (subtitle, 0.42, 140, 1),
    ]
    line_spacing = max(24, min(38, (max_rows - inset * 2) // (len(lines) + 2)))
    total_h = len(lines) * line_spacing
    start_y = max(inset + 25, (max_rows - total_h) // 2 + 20)

    for idx, (txt, f_scale, color, thk) in enumerate(lines):
        # Auto-scale font if text width exceeds canvas boundary
        (tw, th), _ = cv2.getTextSize(txt, font, f_scale, thk)
        max_avail_w = max_cols - (inset + 15) * 2
        if tw > max_avail_w and tw > 0:
            f_scale = f_scale * (max_avail_w / tw)
            (tw, th), _ = cv2.getTextSize(txt, font, f_scale, thk)

        tx = max(inset + 10, (max_cols - tw) // 2)
        ty = start_y + idx * line_spacing
        if 0 < ty < max_rows - inset:
            cv2.putText(padded, txt, (tx, ty), font, f_scale, color, thk, cv2.LINE_AA)

    return padded


def write(frames: list[np.ndarray | None], path: str, fps: int = 30,
          vmin: int = 0, vmax: int = 255, seconds_per_frame: float | None = None,
          labels: list[str] | None = None,
          errors: list[str | None] | None = None) -> None:
    """
    Write a list of 2D projection frames and error slides to an MP4 video file.
    Applies auto-contrast enhancement to valid slices and groups consecutive errors.

    Algorithm:
        1. Determine maximum canvas dimensions from valid frames (fallback 400x400).
        2. Initialize cv2.VideoWriter with mp4v codec.
        3. Loop over frame entries:
               If frame is valid:
                   Normalize contrast to 8-bit, center in canvas, overlay corner label.
                   Write frame to video (1 repeat for 30 FPS playback).
               If frame is invalid:
                   Group consecutive invalid frames with identical error category.
                   Render single error slide with range header (e.g. 'Planes: 1-25').
                   Hold slide for 1.5 seconds (~45 frames) and write to video.
        4. Release writer resource and output confirmation summary.

    Parameters
    ----------
    frames : list of (np.ndarray or None)
        2D projection slices, or None for invalid rows.
    path : str
        Output .mp4 video file path.
    fps : int
        Video playback frame rate (default 30).
    vmin, vmax : int
        Volumetric intensity range for normalization.
    seconds_per_frame : float, optional
        Custom display duration per frame (if None, defaults to 1 frame per slice).
    labels : list of str, optional
        Identifiers displayed on valid slices and error slides.
    errors : list of (str or None), optional
        Error descriptions for invalid planes, classified and shown on slides.
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

    if seconds_per_frame is None:
        repeat_count = 1
    else:
        repeat_count = max(1, int(round(fps * seconds_per_frame)))

    total_written = 0
    i = 0
    n = len(frames)

    while i < n:
        frame = frames[i]

        if frame is not None:
            # -- Valid Plane: contrast enhancement, center padding, and corner label -
            label = labels[i] if labels and i < len(labels) else f"Plane {i + 1}"

            # Enhanced per-frame contrast auto-leveling
            f_max = float(frame.max())
            f_min = float(frame.min())
            if f_max > f_min:
                normalized = np.clip((frame.astype(float) - f_min) / (f_max - f_min) * 255.0, 0, 255).astype(np.uint8)
                # Subtle unsharp masking for enhanced tissue and edge visibility
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

            # Small, discreet corner label tucked in the top-left
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.38
            thickness = 1
            (tw, th), baseline = cv2.getTextSize(label, font, font_scale, thickness)

            cv2.rectangle(padded, (4, 4), (4 + tw + 8, 4 + th + 6), 0, -1)
            cv2.putText(padded, label, (8, 4 + th + 2), font, font_scale, 220, thickness, cv2.LINE_AA)

            actual_repeat = repeat_count
            for _ in range(actual_repeat):
                writer.write(padded)
            total_written += actual_repeat
            i += 1

        else:
            # -- Invalid Plane(s): group consecutive planes with the same error --
            err_msg = errors[i] if errors and i < len(errors) else None
            sub_category = classify_error(err_msg)

            start_idx = i
            while i + 1 < n and frames[i + 1] is None:
                next_err = errors[i + 1] if errors and i + 1 < len(errors) else None
                if classify_error(next_err) == sub_category:
                    i += 1
                else:
                    break
            end_idx = i

            group_size = end_idx - start_idx + 1
            is_group = group_size > 1
            group_label = format_group_label(start_idx, end_idx, labels)

            padded = render_error_slide(max_rows, max_cols, group_label, sub_category, is_group=is_group)

            # Hold error slide for ~1.5s so humans can read it if video is running at high fps
            actual_repeat = max(repeat_count, int(round(fps * 1.5))) if repeat_count < fps else repeat_count
            for _ in range(actual_repeat):
                writer.write(padded)
            total_written += actual_repeat
            i += 1

    writer.release()
    print(f"[VideoWriter] Wrote {len(frames)} plane entries ({total_written} video frames) -> '{path}' ({max_cols}x{max_rows} @ {fps} fps)")
