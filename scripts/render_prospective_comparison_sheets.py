"""Render paired baseline-vs-selector video sheets for prospective selection.

The prospective CSVs answer whether a selector improves native SONIC metrics.
These sheets answer the visual audit question: did the selected reference
actually look better than the baseline for the same mode/seed identity?
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing {path}; run analyze_prospective_native_selection.py first.")
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def sample_strip(path: Path, samples: int, thumb_w: int) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count <= 0:
        raise ValueError(f"Video has no frames: {path}")
    idxs = np.linspace(0, frame_count - 1, samples, dtype=int)
    frames = []
    for idx in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if not ok:
            continue
        h, w = frame.shape[:2]
        thumb_h = max(1, round(h * thumb_w / w))
        frames.append(cv2.resize(frame, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA))
    cap.release()
    if not frames:
        raise ValueError(f"Could not sample video: {path}")
    return np.concatenate(frames, axis=1)


def labeled_row(strip: np.ndarray, label: str, color: tuple[int, int, int]) -> np.ndarray:
    label_h = 46
    out = np.full((strip.shape[0] + label_h, strip.shape[1], 3), 245, dtype=np.uint8)
    out[label_h:] = strip
    short = label[:100]
    cv2.putText(out, short[:55], (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
    if len(short) > 55:
        cv2.putText(out, short[55:], (8, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
    return out


def case_panel(row: dict[str, str], samples: int, thumb_w: int) -> np.ndarray:
    baseline_video = Path(row["baseline_video"])
    selector_video = Path(row["selector_video"])
    baseline = labeled_row(
        sample_strip(baseline_video, samples, thumb_w),
        (
            f"baseline {row['baseline_motion']} strict={row['baseline_strict']} "
            f"rmse={float(row['baseline_rmse']):.3f}"
        ),
        (45, 45, 45),
    )
    selected = labeled_row(
        sample_strip(selector_video, samples, thumb_w),
        (
            f"{row['selector']} {row['selector_motion']} strict={row['selector_strict']} "
            f"rmse={float(row['selector_rmse']):.3f}"
        ),
        (30, 90, 55),
    )
    width = max(baseline.shape[1], selected.shape[1])
    padded = []
    for img in (baseline, selected):
        if img.shape[1] < width:
            pad = np.full((img.shape[0], width - img.shape[1], 3), 245, dtype=np.uint8)
            img = np.concatenate([img, pad], axis=1)
        padded.append(img)
    separator = np.full((8, width, 3), 210, dtype=np.uint8)
    return np.concatenate([padded[0], separator, padded[1]], axis=0)


def write_sheet(rows: list[dict[str, str]], out: Path, samples: int, thumb_w: int) -> None:
    panels = []
    for row in rows:
        try:
            panels.append(case_panel(row, samples, thumb_w))
        except ValueError as exc:
            print(f"[warn] {exc}")
    if not panels:
        return
    width = max(panel.shape[1] for panel in panels)
    padded = []
    for panel in panels:
        if panel.shape[1] < width:
            pad = np.full((panel.shape[0], width - panel.shape[1], 3), 245, dtype=np.uint8)
            panel = np.concatenate([panel, pad], axis=1)
        padded.append(panel)
        padded.append(np.full((16, width, 3), 255, dtype=np.uint8))
    sheet = np.concatenate(padded, axis=0)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), sheet)
    print(f"Wrote {out} from {len(panels)} paired cases")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prospective_dir", type=Path, required=True)
    parser.add_argument("--max_cases", type=int, default=12)
    parser.add_argument("--samples", type=int, default=4)
    parser.add_argument("--thumb_width", type=int, default=180)
    args = parser.parse_args()

    prospective_dir = args.prospective_dir.resolve()
    rows = read_rows(prospective_dir / "prospective_native_identity_outcomes.csv")
    out_dir = prospective_dir / "comparison_sheets"
    for outcome in ("rescued", "regressed", "both_failed"):
        subset = [
            row
            for row in rows
            if row["outcome_vs_baseline"] == outcome and Path(row["baseline_video"]).exists() and Path(row["selector_video"]).exists()
        ]
        subset = sorted(subset, key=lambda r: (r["selector"], r["mode"], int(r["seed_idx"])))[: args.max_cases]
        write_sheet(subset, out_dir / f"{outcome}_paired_sheet.jpg", args.samples, args.thumb_width)


if __name__ == "__main__":
    main()
