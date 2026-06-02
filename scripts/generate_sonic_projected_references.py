#!/usr/bin/env python3
"""Project hard references onto the native SONIC controller manifold.

For each selected non-strict native rollout, this script extracts the actual
MuJoCo qpos executed during playback and exports it back into SONIC reference
CSV format.  This is a controller-distillation baseline: it tests whether the
remaining failures are solvable by replacing the kinematic target with a
physically executed trajectory.  It should not be reported as prompt-preserving
without visual/semantic audit.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from export_sonic_references import SONIC_FPS, export_clip
from render_sonic_actual_sim_examples import extract_actual_29dof_qpos, read_csv_array


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SELECTION = (
    ROOT
    / "results"
    / "ralphloop"
    / "20260529_191342"
    / "humanoid100_final_eval_k256"
    / "final_100_native_selection_ref_aware_k1024_targeted.csv"
)
DEFAULT_OUT = (
    ROOT
    / "results"
    / "ralphloop"
    / "20260530_003531"
    / "humanoid100_final_eval_k1024"
    / "sonic_projected_references"
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def job_dir_from_video(video: str) -> Path:
    video_path = Path(video)
    stem = video_path.name.removesuffix("_actual_sim_qpos.mp4")
    return video_path.parent / stem


def extract_playback_qpos(job_dir: Path) -> tuple[np.ndarray, float]:
    sim_log = job_dir / "sim_qpos.csv"
    playback_json = job_dir / "playback_window.json"
    if not sim_log.exists():
        raise FileNotFoundError(f"Missing simulator qpos log: {sim_log}")
    if not playback_json.exists():
        raise FileNotFoundError(f"Missing playback window: {playback_json}")
    playback = json.loads(playback_json.read_text())
    qpos_log = read_csv_array(sim_log)
    wall = qpos_log[:, 0]
    sim_qpos = qpos_log[:, 2:]
    start = float(playback["play_start_wall_time"])
    duration = float(playback["duration"])
    mask = (wall >= start) & (wall <= start + duration)
    if int(mask.sum()) < 20:
        raise ValueError(f"Only {int(mask.sum())} qpos rows during playback in {job_dir}")
    actual = extract_actual_29dof_qpos(sim_qpos[mask])
    fps = max(1.0, (len(actual) - 1) / duration)
    return actual, fps


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection_csv", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--failed_only", action="store_true", default=True)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    rows = read_rows(args.selection_csv)
    if args.failed_only and not args.all:
        rows = [row for row in rows if str(row.get("strict_tracking_pass", "")).lower() != "true"]

    qpos_dir = args.out_dir / "source_qpos"
    refs_dir = args.out_dir / "references"
    qpos_dir.mkdir(parents=True, exist_ok=True)
    refs_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    names: list[str] = []
    for row in rows:
        job_dir = job_dir_from_video(row["video"])
        actual_qpos, actual_fps = extract_playback_qpos(job_dir)
        name = f"{row['selected_reference']}_sonic_projected"
        qpos_path = qpos_dir / f"{name}.npy"
        np.save(qpos_path, actual_qpos)
        exported = export_clip(qpos_path, refs_dir / name, actual_fps, SONIC_FPS)
        exported.update(
            {
                "prompt_id": row["prompt_id"],
                "category": row["category"],
                "subcategory": row["subcategory"],
                "base_reference": row["selected_reference"],
                "base_video": row["video"],
                "source_job_dir": str(job_dir),
                "actual_fps": actual_fps,
                "base_rmse": row["mean_joint_rmse"],
                "base_root_xy": row["mean_root_xy_error"],
            }
        )
        manifest.append(exported)
        names.append(name)
        print(f"wrote {name} from {job_dir}")
    write_rows(args.out_dir / "manifest.csv", manifest)
    (args.out_dir / "motion_list.txt").write_text("\n".join(names) + "\n")
    print(f"Wrote {args.out_dir / 'manifest.csv'} ({len(manifest)} references)")


if __name__ == "__main__":
    main()
