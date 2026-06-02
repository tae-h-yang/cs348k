#!/usr/bin/env python3
"""Generate slowed/smoothed SONIC reference folders from existing references."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.spatial.transform import Rotation, Slerp

from export_sonic_references import angular_velocity_from_quat_wxyz


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
    / "retimed_nonstrict_sonic_references"
)
SONIC_FPS = 50.0


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


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


def resample_linear(values: np.ndarray, factor: float) -> np.ndarray:
    t_old = np.arange(len(values), dtype=np.float64)
    t_new = np.linspace(0.0, len(values) - 1, max(2, int(round(len(values) * factor))))
    out = np.empty((len(t_new), values.shape[1]), dtype=np.float64)
    for j in range(values.shape[1]):
        out[:, j] = np.interp(t_new, t_old, values[:, j])
    return out


def resample_quat_wxyz(quat: np.ndarray, factor: float) -> np.ndarray:
    t_old = np.arange(len(quat), dtype=np.float64)
    t_new = np.linspace(0.0, len(quat) - 1, max(2, int(round(len(quat) * factor))))
    q = quat / np.linalg.norm(quat, axis=1, keepdims=True).clip(1e-8)
    slerp = Slerp(t_old, Rotation.from_quat(q[:, [1, 2, 3, 0]]))
    out_xyzw = slerp(t_new).as_quat()
    return out_xyzw[:, [3, 0, 1, 2]]


def smooth(values: np.ndarray, sigma: float) -> np.ndarray:
    if sigma <= 0:
        return values
    return gaussian_filter1d(values, sigma=sigma, axis=0, mode="nearest")


def retime_reference(src: Path, dst: Path, factor: float, sigma: float) -> dict[str, object]:
    joint_header, joint_pos = read_csv_array(src / "joint_pos.csv")
    body_pos_header, body_pos = read_csv_array(src / "body_pos.csv")
    body_quat_header, body_quat = read_csv_array(src / "body_quat.csv")

    joint_out = smooth(resample_linear(joint_pos, factor), sigma)
    body_pos_out = smooth(resample_linear(body_pos, factor), sigma)
    body_quat_out = resample_quat_wxyz(body_quat, factor)
    body_quat_out /= np.linalg.norm(body_quat_out, axis=1, keepdims=True).clip(1e-8)
    joint_vel = np.gradient(joint_out, 1.0 / SONIC_FPS, axis=0)
    body_lin_vel = np.gradient(body_pos_out, 1.0 / SONIC_FPS, axis=0)
    body_ang_vel = angular_velocity_from_quat_wxyz(body_quat_out, SONIC_FPS)

    write_csv(dst / "joint_pos.csv", joint_header, joint_out)
    write_csv(dst / "joint_vel.csv", [f"joint_vel_{i}" for i in range(joint_out.shape[1])], joint_vel)
    write_csv(dst / "body_pos.csv", body_pos_header, body_pos_out)
    write_csv(dst / "body_quat.csv", body_quat_header, body_quat_out)
    write_csv(dst / "body_lin_vel.csv", ["body_0_vel_x", "body_0_vel_y", "body_0_vel_z"], body_lin_vel)
    write_csv(dst / "body_ang_vel.csv", ["body_0_angvel_x", "body_0_angvel_y", "body_0_angvel_z"], body_ang_vel)
    (dst / "metadata.txt").write_text(
        f"Metadata for: {dst.name}\n==============================\n\nBody part indexes:\n[0]\n\nTotal timesteps: {len(joint_out)}\n"
    )
    (dst / "info.txt").write_text(
        f"Retimed SONIC reference\nsource: {src}\nfactor: {factor}\ngaussian_sigma: {sigma}\n"
    )
    return {
        "motion": dst.name,
        "source_reference": str(src),
        "out_dir": str(dst),
        "source_frames": len(joint_pos),
        "export_frames": len(joint_out),
        "duration_s": (len(joint_out) - 1) / SONIC_FPS,
        "retime_factor": factor,
        "gaussian_sigma": sigma,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection_csv", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factors", type=float, nargs="+", default=[1.25, 1.5, 2.0])
    parser.add_argument("--sigmas", type=float, nargs="+", default=[0.0, 1.0])
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    rows = read_rows(args.selection_csv)
    targets = [row for row in rows if str(row.get("strict_tracking_pass", "")).lower() != "true"][: args.limit]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    for row in targets:
        src = Path(row["reference_root"]) / row["selected_reference"]
        for factor in args.factors:
            for sigma in args.sigmas:
                factor_tag = str(factor).replace(".", "p")
                sigma_tag = str(sigma).replace(".", "p")
                name = f"{row['selected_reference']}_slow{factor_tag}_sig{sigma_tag}"
                dst = args.out_dir / name
                meta = retime_reference(src, dst, factor, sigma)
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
                print(f"wrote {name}")
    write_rows(args.out_dir / "manifest.csv", manifest)
    print(f"Wrote {args.out_dir / 'manifest.csv'} ({len(manifest)} references)")


if __name__ == "__main__":
    main()
