#!/usr/bin/env python3
"""Copy selected SONIC references and recompute body angular velocity."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

import numpy as np

from export_sonic_references import SONIC_FPS, angular_velocity_from_quat_wxyz


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
    / "angvel_corrected_nonstrict_sonic_references"
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def read_csv_array(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open(newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [[float(x) for x in row] for row in reader if row]
    return header, np.asarray(rows, dtype=np.float64)


def write_csv(path: Path, header: list[str], values: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(values)


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


def copy_with_angvel(src: Path, dst: Path, fps: float) -> dict[str, object]:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    quat_header, quat = read_csv_array(dst / "body_quat.csv")
    n_bodies = len(quat_header) // 4
    ang = angular_velocity_from_quat_wxyz(quat, fps)
    header = [
        f"body_{body}_angvel_{axis}"
        for body in range(n_bodies)
        for axis in ("x", "y", "z")
    ]
    write_csv(dst / "body_ang_vel.csv", header, ang)
    (dst / "info.txt").write_text(
        (dst / "info.txt").read_text() if (dst / "info.txt").exists() else ""
        + f"\nAngular velocity recomputed from body_quat at {fps} Hz.\n"
    )
    return {
        "motion": dst.name,
        "source_reference": str(src),
        "out_dir": str(dst),
        "frames": len(quat),
        "body_count": n_bodies,
        "max_ang_vel": float(np.max(np.abs(ang))) if len(ang) else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection_csv", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--failed_only", action="store_true", default=True)
    parser.add_argument("--all", action="store_true", help="Include strict-passing rows too.")
    parser.add_argument("--fps", type=float, default=SONIC_FPS)
    args = parser.parse_args()

    rows = read_rows(args.selection_csv)
    if args.failed_only and not args.all:
        rows = [row for row in rows if str(row.get("strict_tracking_pass", "")).lower() != "true"]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    names: list[str] = []
    for row in rows:
        src = Path(row["reference_root"]) / row["selected_reference"]
        name = f"{row['selected_reference']}_angvel"
        meta = copy_with_angvel(src, args.out_dir / name, args.fps)
        meta.update(
            {
                "prompt_id": row["prompt_id"],
                "category": row["category"],
                "subcategory": row["subcategory"],
                "base_reference": row["selected_reference"],
                "base_rmse": row["mean_joint_rmse"],
                "base_root_xy": row["mean_root_xy_error"],
            }
        )
        manifest.append(meta)
        names.append(name)
        print(f"wrote {name}")
    write_rows(args.out_dir / "manifest.csv", manifest)
    (args.out_dir / "motion_list.txt").write_text("\n".join(names) + "\n")
    print(f"Wrote {args.out_dir / 'manifest.csv'} ({len(manifest)} references)")


if __name__ == "__main__":
    main()
