"""Create a contact sheet from MP4 videos for quick visual audit.

This is intentionally generic: point it at any folder of videos and it samples
several frames per clip, labels them, and writes one image. It is useful for
checking whether tracking videos are visually sane before making claims from
CSV metrics.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def sample_video(path: Path, samples: int, thumb_w: int) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count <= 0:
        raise ValueError(f"Video has no frames: {path}")
    idxs = np.linspace(0, frame_count - 1, samples, dtype=int)
    thumbs = []
    for idx in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if not ok:
            continue
        h, w = frame.shape[:2]
        thumb_h = max(1, round(h * thumb_w / w))
        thumbs.append(cv2.resize(frame, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA))
    cap.release()
    if not thumbs:
        raise ValueError(f"Could not sample frames from: {path}")
    row = np.concatenate(thumbs, axis=1)
    label_h = 34
    labeled = np.full((row.shape[0] + label_h, row.shape[1], 3), 245, dtype=np.uint8)
    labeled[label_h:] = row
    name = path.stem[:90]
    cv2.putText(labeled, name, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (20, 20, 20), 2, cv2.LINE_AA)
    return labeled


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--glob", default="*.mp4")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--samples", type=int, default=4)
    parser.add_argument("--thumb_width", type=int, default=220)
    args = parser.parse_args()

    videos = sorted(args.video_dir.glob(args.glob))
    if args.limit:
        videos = videos[: args.limit]
    if not videos:
        raise SystemExit(f"No videos matched {args.video_dir / args.glob}")

    rows = [sample_video(path, args.samples, args.thumb_width) for path in videos]
    width = max(row.shape[1] for row in rows)
    padded = []
    for row in rows:
        if row.shape[1] < width:
            pad = np.full((row.shape[0], width - row.shape[1], 3), 245, dtype=np.uint8)
            row = np.concatenate([row, pad], axis=1)
        padded.append(row)
    sheet = np.concatenate(padded, axis=0)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.out), sheet)
    print(f"Wrote {args.out} from {len(videos)} videos")


if __name__ == "__main__":
    main()
