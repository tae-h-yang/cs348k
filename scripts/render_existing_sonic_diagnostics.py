"""Render diagnostic videos from an existing native SONIC batch.

This does not rerun the controller. It reuses each motion directory's saved
`sim_qpos.csv` plus the exported SONIC reference and renders clearer videos
with contact markers and a camera that tracks the robot.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from render_sonic_actual_sim_examples import (
    extract_actual_29dof_qpos,
    load_reference_qpos,
    read_csv_array,
    render_qpos_video,
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def render_existing(
    batch_dir: Path,
    motion: str,
    out_dir: Path,
    width: int,
    height: int,
    fps: float,
    align_mode: str,
) -> Path:
    job_dir = batch_dir / motion
    sim_log = job_dir / "sim_qpos.csv"
    playback_window = json.loads((job_dir / "playback_window.json").read_text())
    reference_root = batch_dir.parent / "sonic_references"
    ref_qpos = load_reference_qpos(reference_root / motion)

    qpos_log = read_csv_array(sim_log)
    wall = qpos_log[:, 0]
    sim_qpos = qpos_log[:, 2:]
    play_start = float(playback_window["play_start_wall_time"])
    duration = float(playback_window["duration"])
    mask = (wall >= play_start) & (wall <= play_start + duration)
    if mask.sum() < 20:
        raise ValueError(f"{motion}: only {mask.sum()} qpos rows during playback")
    actual = extract_actual_29dof_qpos(sim_qpos[mask])

    render_fps = fps if fps > 0 else (len(ref_qpos) - 1) / duration
    n = min(len(ref_qpos), int(duration * render_fps), len(actual))
    actual_idx = np.linspace(0, len(actual) - 1, num=n, dtype=np.int64)
    ref_idx = np.linspace(0, len(ref_qpos) - 1, num=n, dtype=np.int64)

    out_path = out_dir / f"{motion}_diagnostic_contacts.mp4"
    render_qpos_video(
        motion,
        ref_qpos[ref_idx],
        actual[actual_idx],
        out_path,
        fps=render_fps,
        width=width,
        height=height,
        align_mode=align_mode,
        contact_markers=True,
        camera_track=True,
    )
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_dir", type=Path, required=True)
    parser.add_argument("--motions", nargs="*", default=[])
    parser.add_argument("--all", action="store_true", help="Render every completed motion in batch_summary.csv.")
    parser.add_argument(
        "--mode_filters",
        nargs="*",
        default=[],
        help="Semantic mode names or substrings, e.g. walk_stealth walk_scared.",
    )
    parser.add_argument("--groups", nargs="*", choices=("fail", "strict_pass"), default=[])
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--out_dir", type=Path, default=None)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--align_mode", choices=("initial", "per_frame"), default="initial")
    args = parser.parse_args()

    batch_dir = args.batch_dir.resolve()
    out_dir = args.out_dir or (batch_dir / "diagnostic_contact_videos")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_rows(batch_dir / "batch_summary.csv")
    selected = list(args.motions)
    if args.all:
        selected.extend([r["motion"] for r in rows if r.get("status") == "completed"])
    if args.mode_filters:
        filters = tuple(args.mode_filters)
        mode_rows = [r for r in rows if any(token in r["motion"] for token in filters)]
        selected.extend([r["motion"] for r in mode_rows[: args.limit]])
    if "fail" in args.groups:
        fail_rows = [r for r in rows if r.get("fell") == "True"]
        if args.mode_filters:
            filters = tuple(args.mode_filters)
            fail_rows = [r for r in fail_rows if any(token in r["motion"] for token in filters)]
        selected.extend([r["motion"] for r in fail_rows[: args.limit]])
    if "strict_pass" in args.groups:
        strict = [
            r
            for r in rows
            if r.get("fell") == "False"
            and float(r["mean_joint_rmse"]) <= 0.20
            and float(r["mean_root_xy_error"]) <= 1.5
        ]
        if args.mode_filters:
            filters = tuple(args.mode_filters)
            strict = [r for r in strict if any(token in r["motion"] for token in filters)]
        selected.extend([r["motion"] for r in strict[: args.limit]])

    seen: set[str] = set()
    rendered = []
    for motion in selected:
        if motion in seen:
            continue
        seen.add(motion)
        try:
            path = render_existing(batch_dir, motion, out_dir, args.width, args.height, args.fps, args.align_mode)
        except (ValueError, RuntimeError) as exc:
            print(f"[warn] skipped {motion}: {exc}")
            continue
        rendered.append({"motion": motion, "diagnostic_video": str(path)})
        print(path)

    if rendered:
        with (out_dir / "diagnostic_manifest.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rendered[0].keys()))
            writer.writeheader()
            writer.writerows(rendered)


if __name__ == "__main__":
    main()
