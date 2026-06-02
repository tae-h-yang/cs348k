"""Stitch K1 baseline and final selected overlay videos into comparison MP4s."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_INDEX = ROOT / "results" / "humanoid100_final_eval" / "k1_baseline_overlay_videos.csv"
DEFAULT_FINAL_INDEX = ROOT / "results" / "humanoid100_final_eval" / "final_100_selected_overlay_videos.csv"
DEFAULT_OUT_DIR = ROOT / "results" / "humanoid100_final_eval" / "before_after_overlay_videos"
DEFAULT_OUT_INDEX = ROOT / "results" / "humanoid100_final_eval" / "before_after_overlay_videos.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def put_banner(frame: np.ndarray, text: str, x: int, y: int, color: tuple[int, int, int]) -> None:
    cv2.rectangle(frame, (x, 0), (x + frame.shape[1] // 2, 30), (0, 0, 0), -1)
    cv2.putText(frame, text, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(frame, text, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.58, color, 1, cv2.LINE_AA)


def read_frame_or_last(cap: cv2.VideoCapture, last: np.ndarray | None) -> tuple[bool, np.ndarray | None]:
    ok, frame = cap.read()
    if ok:
        return True, frame
    return False, last


def stitch_pair(baseline: dict[str, str], final: dict[str, str], out_path: Path, fps: int) -> dict[str, object]:
    left_path = Path(baseline["video_path"])
    right_path = Path(final["video_path"])
    left = cv2.VideoCapture(str(left_path))
    right = cv2.VideoCapture(str(right_path))
    if not left.isOpened():
        raise ValueError(f"Could not open baseline video: {left_path}")
    if not right.isOpened():
        raise ValueError(f"Could not open final video: {right_path}")

    width = int(left.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(left.get(cv2.CAP_PROP_FRAME_HEIGHT))
    right_width = int(right.get(cv2.CAP_PROP_FRAME_WIDTH))
    right_height = int(right.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if (width, height) != (right_width, right_height):
        raise ValueError(f"Video size mismatch for {baseline['prompt_id']}: {(width, height)} vs {(right_width, right_height)}")

    left_frames = int(left.get(cv2.CAP_PROP_FRAME_COUNT))
    right_frames = int(right.get(cv2.CAP_PROP_FRAME_COUNT))
    total = max(left_frames, right_frames)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width * 2, height))
    last_left: np.ndarray | None = None
    last_right: np.ndarray | None = None
    written = 0
    for _ in range(total):
        _, last_left = read_frame_or_last(left, last_left)
        _, last_right = read_frame_or_last(right, last_right)
        if last_left is None or last_right is None:
            break
        combined = np.concatenate([last_left, last_right], axis=1)
        put_banner(combined, "K1 MotionBricks baseline", 0, 22, (230, 230, 230))
        put_banner(combined, f"Selected: {final['selected_method']}", width, 22, (180, 255, 190))
        writer.write(combined)
        written += 1

    writer.release()
    left.release()
    right.release()
    return {
        "prompt_id": final["prompt_id"],
        "subcategory": final["subcategory"],
        "baseline_video": str(left_path),
        "final_video": str(right_path),
        "comparison_video": str(out_path),
        "baseline_method": baseline["selected_method"],
        "final_method": final["selected_method"],
        "frames": written,
        "baseline_track_seconds": baseline["track_seconds"],
        "final_track_seconds": final["track_seconds"],
        "baseline_rmse": baseline["mean_tracking_rmse"],
        "final_rmse": final["mean_tracking_rmse"],
        "baseline_init_qpos_max_abs_error": baseline["initial_qpos_max_abs_error"],
        "final_init_qpos_max_abs_error": final["initial_qpos_max_abs_error"],
        "baseline_initial_qvel_norm": baseline["initial_qvel_norm"],
        "final_initial_qvel_norm": final["initial_qvel_norm"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline_index", type=Path, default=DEFAULT_BASELINE_INDEX)
    parser.add_argument("--final_index", type=Path, default=DEFAULT_FINAL_INDEX)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--out_index", type=Path, default=DEFAULT_OUT_INDEX)
    parser.add_argument("--fps", type=int, default=50)
    args = parser.parse_args()

    baseline = {row["prompt_id"]: row for row in read_rows(args.baseline_index)}
    final_rows = sorted(read_rows(args.final_index), key=lambda row: row["prompt_id"])
    outputs: list[dict[str, object]] = []
    for i, row in enumerate(final_rows, start=1):
        base = baseline[row["prompt_id"]]
        out = args.out_dir / f"{row['prompt_id']}_{row['subcategory']}_before_after.mp4"
        outputs.append(stitch_pair(base, row, out, args.fps))
        print(f"[{i:03d}/{len(final_rows):03d}] {out}")
    write_csv(args.out_index, outputs)
    print(f"Wrote {len(outputs)} before/after videos to {args.out_dir}")
    print(f"Index: {args.out_index}")


if __name__ == "__main__":
    main()
