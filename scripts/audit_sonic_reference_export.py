"""Audit MotionBricks qpos to SONIC reference export integrity.

This catches implementation-level reference-prep bugs separately from physical
tracking failures. It verifies that exported SONIC CSVs round-trip back to the
same MuJoCo qpos trajectory produced by `export_sonic_references.export_clip`.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from export_sonic_references import SONIC_FPS, SOURCE_FPS, normalize_quat, resample_linear
from render_sonic_actual_sim_examples import load_reference_qpos


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def expected_export_qpos(source_qpos: np.ndarray) -> np.ndarray:
    root_pos = resample_linear(source_qpos[:, :3], SOURCE_FPS, SONIC_FPS)
    root_quat = normalize_quat(resample_linear(source_qpos[:, 3:7], SOURCE_FPS, SONIC_FPS))
    joints = resample_linear(source_qpos[:, 7:], SOURCE_FPS, SONIC_FPS)
    expected = np.zeros((len(root_pos), 36), dtype=np.float64)
    expected[:, :3] = root_pos
    expected[:, 3:7] = root_quat
    expected[:, 7:] = joints
    return expected


def audit_row(row: dict[str, str], reference_root: Path) -> dict[str, object]:
    motion = row["motion"]
    source = Path(row["source_path"])
    source_qpos = np.load(source).astype(np.float64)
    expected = expected_export_qpos(source_qpos)
    exported = load_reference_qpos(reference_root / motion)
    n = min(len(expected), len(exported))
    diff = expected[:n] - exported[:n]
    root_step = np.linalg.norm(np.diff(exported[:, :2], axis=0), axis=1)
    joint_step = np.max(np.abs(np.diff(exported[:, 7:], axis=0)), axis=1)
    return {
        "motion": motion,
        "source_path": str(source),
        "source_frames": len(source_qpos),
        "export_frames": len(exported),
        "roundtrip_max_abs": float(np.max(np.abs(diff))),
        "roundtrip_mean_abs": float(np.mean(np.abs(diff))),
        "root_z_min": float(np.min(exported[:, 2])),
        "root_z_start": float(exported[0, 2]),
        "root_z_end": float(exported[-1, 2]),
        "root_xy_displacement": float(np.linalg.norm(exported[-1, :2] - exported[0, :2])),
        "p95_root_xy_step_per_frame": float(np.percentile(root_step, 95)) if len(root_step) else 0.0,
        "p95_joint_step_rad_per_frame": float(np.percentile(joint_step, 95)) if len(joint_step) else 0.0,
        "low_root_frames_pct": float(np.mean(exported[:, 2] < 0.60) * 100.0),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prospective_dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    prospective_dir = args.prospective_dir.resolve()
    reference_root = prospective_dir / "sonic_references"
    rows = read_rows(prospective_dir / "export_manifest.csv")
    audited = [audit_row(row, reference_root) for row in rows]
    out = args.out or (prospective_dir / "sonic_reference_export_audit.csv")
    write_rows(out, audited)

    max_roundtrip = max(float(row["roundtrip_max_abs"]) for row in audited)
    low_root = sum(float(row["low_root_frames_pct"]) > 0.0 for row in audited)
    print(f"audited={len(audited)} max_roundtrip_abs={max_roundtrip:.3e} low_root_refs={low_root}")
    print(out)


if __name__ == "__main__":
    main()
