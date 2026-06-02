"""Render a contact sheet for final Humanoid100 selector representative videos."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "results" / "humanoid100_final_eval" / "final_selector" / "representative_cases.csv"
DEFAULT_VIDEO_DIR = ROOT / "results" / "humanoid100_final_eval" / "final_selector" / "representative_videos"
DEFAULT_OUT = ROOT / "results" / "humanoid100_final_eval" / "final_selector" / "representative_contact_sheet.jpg"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def read_frame(path: Path, frac: float = 0.45) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Could not open {path}")
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(n - 1, int(n * frac))))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise ValueError(f"Could not read frame from {path}")
    return frame


def put(img: np.ndarray, text: str, x: int, y: int, scale: float = 0.42) -> None:
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), 1, cv2.LINE_AA)


def tile_for(row: dict[str, str], video_dir: Path, width: int, height: int) -> np.ndarray:
    path = video_dir / f"{row['selected_reference']}.mp4"
    frame = read_frame(path)
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, 74), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.52, frame, 0.48, 0)
    put(frame, f"{row['bucket']} #{row['rank']}", 10, 22)
    put(frame, row["selected_reference"], 10, 45)
    delta = float(row["selected_minus_k1_track_seconds"])
    status = f"track {float(row['sonic_track_seconds']):.2f}s  dK1 {delta:+.2f}s  rmse {float(row['sonic_mean_tracking_rmse']):.2f}"
    put(frame, status, 10, 67, 0.37)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--video_dir", type=Path, default=DEFAULT_VIDEO_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--cols", type=int, default=3)
    parser.add_argument("--tile_width", type=int, default=480)
    parser.add_argument("--tile_height", type=int, default=180)
    args = parser.parse_args()

    rows = read_rows(args.cases)
    seen = set()
    unique = []
    for row in rows:
        ref = row["selected_reference"]
        if ref in seen:
            continue
        seen.add(ref)
        unique.append(row)

    tiles = [tile_for(row, args.video_dir, args.tile_width, args.tile_height) for row in unique]
    cols = args.cols
    rows_n = int(np.ceil(len(tiles) / cols))
    sheet = np.full((rows_n * args.tile_height, cols * args.tile_width, 3), 22, dtype=np.uint8)
    for i, tile in enumerate(tiles):
        r, c = divmod(i, cols)
        y = r * args.tile_height
        x = c * args.tile_width
        sheet[y:y + args.tile_height, x:x + args.tile_width] = tile
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.out), sheet)
    print(args.out)


if __name__ == "__main__":
    main()
