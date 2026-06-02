#!/usr/bin/env python3
"""Convert bundled Kimodo-G1 demo examples to MuJoCo qpos for local evaluation.

The official Kimodo repo ships a small set of G1 example motions as Kimodo NPZ
files. They are not a replacement for generating the full Humanoid100 suite, but
they are useful as a sanity check that our G1 qpos verifier can ingest native
Kimodo artifacts while text-conditioned generation is blocked by gated text
encoder access.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch


ROOT = Path(__file__).resolve().parents[1]
KIMODO_REPO = ROOT.parent / "kimodo"
DEFAULT_EXAMPLES = KIMODO_REPO / "kimodo" / "assets" / "demo" / "examples" / "kimodo-g1-rp"
DEFAULT_OUT = ROOT / "results" / "kimodo_g1_examples_qpos"
DEFAULT_DATA = ROOT / "data" / "kimodo_g1_examples_qpos"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
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


def validate_qpos(qpos: np.ndarray, name: str) -> None:
    if qpos.ndim != 2 or qpos.shape[1] != 36:
        raise ValueError(f"{name}: expected qpos shape (T, 36), got {qpos.shape}")
    if qpos.shape[0] < 2:
        raise ValueError(f"{name}: expected at least 2 qpos frames, got {qpos.shape[0]}")
    if not np.isfinite(qpos).all():
        raise ValueError(f"{name}: qpos contains non-finite values")
    quat_norm = np.linalg.norm(qpos[:, 3:7], axis=1)
    if np.any(quat_norm < 1e-6):
        raise ValueError(f"{name}: root quaternion contains near-zero norm")


def read_meta(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples_dir", type=Path, default=DEFAULT_EXAMPLES)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--data_dir", type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()

    if not args.examples_dir.exists():
        raise FileNotFoundError(f"Kimodo G1 examples not found: {args.examples_dir}")

    sys.path.insert(0, str(KIMODO_REPO))
    from kimodo.exports.mujoco import MujocoQposConverter  # noqa: PLC0415
    from kimodo.skeleton import global_rots_to_local_rots  # noqa: PLC0415
    from kimodo.skeleton.registry import build_skeleton  # noqa: PLC0415

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.data_dir.mkdir(parents=True, exist_ok=True)
    skeleton = build_skeleton(34)
    converter = MujocoQposConverter(skeleton)
    rows: list[dict[str, object]] = []

    for example_dir in sorted(args.examples_dir.iterdir()):
        motion_path = example_dir / "motion.npz"
        if not motion_path.exists():
            continue
        motion = np.load(motion_path)
        if "global_rot_mats" not in motion or "posed_joints" not in motion:
            raise ValueError(f"{motion_path}: expected global_rot_mats and posed_joints")

        global_rots = torch.from_numpy(motion["global_rot_mats"]).float()
        posed_joints = torch.from_numpy(motion["posed_joints"]).float()
        local_rots = global_rots_to_local_rots(global_rots, skeleton)
        qpos = converter.dict_to_qpos(
            {"local_rot_mats": local_rots, "root_positions": posed_joints[:, 0]},
            device="cpu",
            numpy=True,
        ).astype(np.float32)
        validate_qpos(qpos, example_dir.name)

        csv_path = args.data_dir / f"{example_dir.name}.csv"
        npy_path = args.data_dir / f"{example_dir.name}.npy"
        np.savetxt(csv_path, qpos, delimiter=",")
        np.save(npy_path, qpos)

        meta = read_meta(example_dir / "meta.json")
        prompt_text = str(meta.get("text") or " ".join(meta.get("texts", [])) or example_dir.name)
        duration = meta.get("duration") or sum(float(x) for x in meta.get("durations", []))
        rows.append(
            {
                "prompt_id": f"kimodo_demo_{len(rows) + 1:02d}",
                "category": "kimodo_native_demo",
                "subcategory": example_dir.name,
                "prompt_text": prompt_text,
                "success_criteria": "native Kimodo-G1 demo motion; evaluate physical feasibility and tracking",
                "expected_primary_contacts": "feet_or_task_dependent",
                "expected_root_motion": "task_dependent",
                "expected_arm_role": "task_dependent",
                "hardness": "native_demo",
                "model": "Kimodo-G1-RP-v1",
                "duration_s": duration,
                "diffusion_steps": meta.get("diffusion_steps", ""),
                "seed": meta.get("seed", ""),
                "status": "success",
                "frames": int(qpos.shape[0]),
                "dims": int(qpos.shape[1]),
                "source_npz_path": str(motion_path),
                "csv_path": str(csv_path),
                "qpos_npy_path": str(npy_path),
            }
        )

    write_csv(args.out_dir / "manifest.csv", rows)
    (args.out_dir / "README.md").write_text(
        "\n".join(
            [
                "# Kimodo-G1 Bundled Example Conversion",
                "",
                "These are official bundled Kimodo-G1 demo motions converted to MuJoCo qpos.",
                "They are a sanity set for the verifier while full text generation waits on",
                "gated text-encoder access.",
                "",
                f"- Examples converted: {len(rows)}",
                f"- Manifest: `{args.out_dir / 'manifest.csv'}`",
                f"- Qpos data: `{args.data_dir}`",
                "",
            ]
        )
    )
    print(f"Converted {len(rows)} Kimodo-G1 examples to {args.data_dir}")


if __name__ == "__main__":
    main()
