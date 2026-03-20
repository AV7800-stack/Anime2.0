from __future__ import annotations

import cv2
import numpy as np
from pathlib import Path


def _ensure_even(x: int) -> int:
    return x if x % 2 == 0 else x + 1


def make_kenburns_video(
    *,
    image_path: Path,
    out_mp4: Path,
    duration_s: float,
    fps: int = 24,
    low_end: bool = False,
    zoom_strength: float | None = None,
) -> Path:
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Image not found or unreadable: {image_path}")

    h, w = img.shape[:2]
    # Reduce computation for low-end mode
    target_w = 768 if low_end else w
    scale = target_w / w
    target_h = int(h * scale)
    target_w = _ensure_even(int(target_w))
    target_h = _ensure_even(int(target_h))
    img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)

    total_frames = max(1, int(duration_s * fps))
    if zoom_strength is None:
        zoom_strength = 0.06 if low_end else 0.12

    # Start and end crop positions (normalized)
    # This creates a simple "pan + zoom" movement.
    x0, y0 = 0.35, 0.35
    x1, y1 = 0.65, 0.55

    # Zoom simulation by cropping around a center
    # At t=0: zoom=1.0 (full frame)
    # At t=1: zoom=1.0 + zoom_strength
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_mp4), fourcc, fps, (target_w, target_h))

    last_frame = None
    for i in range(total_frames):
        t = i / max(1, total_frames - 1)
        zoom = 1.0 + zoom_strength * t
        cx = (x0 + (x1 - x0) * t) * target_w
        cy = (y0 + (y1 - y0) * t) * target_h

        crop_w = int(target_w / zoom)
        crop_h = int(target_h / zoom)
        x_start = int(cx - crop_w / 2)
        y_start = int(cy - crop_h / 2)
        x_start = max(0, min(target_w - crop_w, x_start))
        y_start = max(0, min(target_h - crop_h, y_start))
        crop = img[y_start : y_start + crop_h, x_start : x_start + crop_w]
        frame = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

        # Add subtle motion blur by blending with previous frame
        if i >= 1 and last_frame is not None:
            alpha = 0.06 if not low_end else 0.03
            frame = cv2.addWeighted(frame, 1 - alpha, last_frame, alpha, 0)

        writer.write(frame)
        last_frame = frame

    writer.release()
    return out_mp4

