"""Overlay a clearly labeled synthetic dashboard on a video.

This utility is for visual prototyping only. It burns in the label
"simulated demo data" so the output is not confused with measured evidence.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import cv2
import numpy as np


LABEL = "simulated demo data"


def put_text(
    frame: np.ndarray,
    text: str,
    xy: tuple[int, int],
    scale: float,
    color: tuple[int, int, int] = (255, 255, 255),
    thickness: int = 1,
) -> None:
    x, y = xy
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 3, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def draw_plot(
    frame: np.ndarray,
    origin: tuple[int, int],
    size: tuple[int, int],
    values: list[float],
    title: str,
    color: tuple[int, int, int],
) -> None:
    x0, y0 = origin
    w, h = size
    cv2.rectangle(frame, (x0, y0), (x0 + w, y0 + h), (18, 18, 18), -1)
    cv2.rectangle(frame, (x0, y0), (x0 + w, y0 + h), (90, 90, 90), 1)
    put_text(frame, title, (x0 + 10, y0 + 22), 0.45, (230, 230, 230))

    pad_l, pad_r, pad_t, pad_b = 18, 10, 34, 16
    px0, py0 = x0 + pad_l, y0 + pad_t
    pw, ph = w - pad_l - pad_r, h - pad_t - pad_b
    for i in range(4):
        yy = py0 + int(ph * i / 3)
        cv2.line(frame, (px0, yy), (px0 + pw, yy), (48, 48, 48), 1)

    if len(values) < 2:
        return
    pts = []
    for i, v in enumerate(values):
        xx = px0 + int(pw * i / max(1, len(values) - 1))
        yy = py0 + int(ph * (1.0 - np.clip(v, 0.0, 1.0)))
        pts.append((xx, yy))
    cv2.polylines(frame, [np.array(pts, dtype=np.int32)], False, color, 2, cv2.LINE_AA)


def draw_gauge(
    frame: np.ndarray,
    center: tuple[int, int],
    radius: int,
    value: float,
    label: str,
    color: tuple[int, int, int],
) -> None:
    cx, cy = center
    cv2.circle(frame, center, radius, (22, 22, 22), -1)
    cv2.circle(frame, center, radius, (90, 90, 90), 1)
    start, end = 210, -30
    cv2.ellipse(frame, center, (radius - 12, radius - 12), 0, start, end, (55, 55, 55), 8, cv2.LINE_AA)
    angle = math.radians(start + (end - start) * np.clip(value, 0.0, 1.0))
    needle = (int(cx + math.cos(angle) * (radius - 22)), int(cy - math.sin(angle) * (radius - 22)))
    cv2.line(frame, center, needle, color, 3, cv2.LINE_AA)
    cv2.circle(frame, center, 5, color, -1)
    put_text(frame, label, (cx - radius + 12, cy + radius - 16), 0.42, (230, 230, 230))
    put_text(frame, f"{value * 100:04.1f}", (cx - 34, cy + 10), 0.55, color, 1)


def synthetic_values(frame_idx: int, fps: float, history: int) -> tuple[list[float], list[float], float, float]:
    t0 = frame_idx / max(fps, 1e-6)
    risk: list[float] = []
    energy: list[float] = []
    for i in range(history):
        t = t0 - (history - 1 - i) / max(fps, 1e-6)
        risk.append(0.48 + 0.28 * math.sin(1.7 * t) + 0.08 * math.sin(6.1 * t))
        energy.append(0.50 + 0.22 * math.cos(1.1 * t + 0.6) + 0.12 * math.sin(4.2 * t))
    balance = 0.55 + 0.35 * math.sin(0.8 * t0 + 1.1)
    contact = 0.45 + 0.40 * math.cos(0.9 * t0 + 0.2)
    return risk, energy, float(np.clip(balance, 0.0, 1.0)), float(np.clip(contact, 0.0, 1.0))


def overlay_dashboard(frame: np.ndarray, frame_idx: int, fps: float) -> np.ndarray:
    out = frame.copy()
    h, w = out.shape[:2]
    panel_w = min(max(360, w // 3), w - 30)
    panel_h = min(260, h - 30)
    x0, y0 = w - panel_w - 18, 18

    overlay = out.copy()
    cv2.rectangle(overlay, (x0, y0), (x0 + panel_w, y0 + panel_h), (8, 10, 12), -1)
    out = cv2.addWeighted(overlay, 0.72, out, 0.28, 0)
    cv2.rectangle(out, (x0, y0), (x0 + panel_w, y0 + panel_h), (120, 120, 120), 1)

    put_text(out, LABEL.upper(), (x0 + 14, y0 + 30), 0.58, (80, 220, 255), 2)
    put_text(out, "fictional overlay - not measured", (x0 + 14, y0 + 54), 0.43, (220, 220, 220), 1)

    risk, energy, balance, contact = synthetic_values(frame_idx, fps, history=72)
    plot_w = panel_w - 28
    draw_plot(out, (x0 + 14, y0 + 70), (plot_w, 70), risk, "demo risk trace", (60, 180, 255))
    draw_plot(out, (x0 + 14, y0 + 150), (plot_w, 70), energy, "demo energy trace", (80, 240, 160))

    gauge_y = y0 + panel_h - 32
    draw_gauge(out, (x0 + 72, gauge_y), 34, balance, "balance", (90, 210, 255))
    draw_gauge(out, (x0 + 172, gauge_y), 34, contact, "contact", (100, 245, 155))

    put_text(out, f"t={frame_idx / max(fps, 1e-6):05.2f}s", (x0 + panel_w - 112, y0 + panel_h - 16), 0.42, (220, 220, 220))
    return out


def process_video(input_path: Path, output_path: Path) -> None:
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open input video: {input_path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        cap.release()
        raise ValueError(f"Could not open output video writer: {output_path}")

    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(overlay_dashboard(frame, frame_idx, fps))
        frame_idx += 1

    cap.release()
    writer.release()
    if frame_idx == 0:
        raise ValueError(f"No frames were read from input video: {input_path}")
    print(f"Wrote {frame_idx} frames to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Input video path.")
    parser.add_argument("output", type=Path, help="Output MP4 path.")
    args = parser.parse_args()
    process_video(args.input, args.output)


if __name__ == "__main__":
    main()
