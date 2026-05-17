"""Generate held-out MotionBricks candidates and select before native SONIC.

This is a prospective experiment: candidate scoring happens before native
controller rollout. The output reference folders can then be passed to
`run_sonic_native_release_batch.py` and analyzed by
`analyze_prospective_native_selection.py`.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from export_sonic_references import SOURCE_FPS, SONIC_FPS, export_clip
from generate_guided import MOTIONBRICKS_DIR, MOTION_CONFIGS, generate_clip
from physics_eval.physaware import PhysicalAwarenessCritic
from evaluate_contact_quality import SCENE_XML, artifact_score, evaluate_clip as contact_evaluate_clip


DEFAULT_MODES = [
    "walk",
    "slow_walk",
    "stealth_walk",
    "injured_walk",
    "walk_zombie",
    "walk_stealth",
    "walk_boxing",
    "walk_happy_dance",
    "walk_gun",
    "walk_scared",
    "hand_crawling",
    "elbow_crawling",
]


def load_agent():
    original = Path.cwd()
    os.chdir(MOTIONBRICKS_DIR)
    import argparse as ap
    from motionbricks.motion_backbone.demo.utils import navigation_demo

    mb_args = ap.Namespace(
        explicit_dataset_folder=None,
        reprocess_clips=0,
        controller="random",
        lookat_movement_direction=0,
        has_viewer=0,
        pre_filter_qpos=1,
        source_root_realignment=1,
        target_root_realignment=1,
        force_canonicalization=1,
        skip_ending_target_cond=0,
        random_speed_scale=0,
        speed_scale=[0.8, 1.2],
        generate_dt=2.0,
        max_steps=10000,
        random_seed=42,
        num_runs=1,
        use_qpos=1,
        planner="default",
        allowed_mode=None,
        clips="G1",
        return_model_configs=True,
        return_dataloader=True,
        recording_dir=None,
        EXP="default",
    )
    agent = navigation_demo(mb_args)
    os.chdir(original)
    return agent


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
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


def precontroller_score(row: dict[str, object]) -> float:
    contact_score = max(0.0, min(1.0, 1.0 - float(row["contact_artifact_score"])))
    dynamics_score = float(np.exp(-max(float(row["full_risk"]), 0.0) / 35.0))
    torque_score = float(np.exp(-max(float(row["p95_torque_limit_ratio"]), 0.0) / 3.0))
    root_score = float(np.exp(-max(float(row["p95_root_force_N"]), 0.0) / 20000.0))
    return 0.42 * contact_score + 0.32 * dynamics_score + 0.16 * torque_score + 0.10 * root_score


def precontroller_gate(row: dict[str, object]) -> bool:
    upright_ok = (
        row["type"] == "whole_body"
        or (
            float(row["root_z_min"]) >= 0.60
            and float(row["low_root_frames_pct"]) <= 0.0
        )
    )
    return (
        upright_ok
        and float(row["contact_artifact_score"]) <= 0.45
        and float(row["full_risk"]) <= 55.0
        and float(row["p95_torque_limit_ratio"]) <= 4.0
        and float(row["nonfoot_floor_contact_frames_pct"]) <= 20.0
    )


def reference_sanity_metrics(qpos: np.ndarray, motion_type: str) -> dict[str, object]:
    root_z = qpos[:, 2]
    root_step = np.linalg.norm(np.diff(qpos[:, :2], axis=0), axis=1)
    joint_step = np.max(np.abs(np.diff(qpos[:, 7:], axis=0)), axis=1)
    low_root_frames_pct = float(np.mean(root_z < 0.60) * 100.0)
    upright_gate = motion_type == "whole_body" or (float(np.min(root_z)) >= 0.60 and low_root_frames_pct <= 0.0)
    return {
        "root_z_min": float(np.min(root_z)),
        "root_z_start": float(root_z[0]),
        "root_z_end": float(root_z[-1]),
        "root_xy_displacement": float(np.linalg.norm(qpos[-1, :2] - qpos[0, :2])),
        "p95_root_xy_step_per_frame": float(np.percentile(root_step, 95)) if len(root_step) else 0.0,
        "p95_joint_step_rad_per_frame": float(np.percentile(joint_step, 95)) if len(joint_step) else 0.0,
        "low_root_frames_pct": low_root_frames_pct,
        "upright_reference_gate_pass": "__YES__" if upright_gate else "__NO__",
    }


def score_candidate(
    qpos: np.ndarray,
    qpos_path: Path,
    clip: str,
    mode: str,
    motion_type: str,
    seed_idx: int,
    candidate_k: int,
    full_critic: PhysicalAwarenessCritic,
    contact_model: mujoco.MjModel,
) -> dict[str, object]:
    report, _ = full_critic.score(qpos, clip, motion_type, variant=f"candidate_{candidate_k}")
    contact = contact_evaluate_clip(contact_model, qpos, clip)
    contact["contact_artifact_score"] = artifact_score(contact)
    row: dict[str, object] = {
        "clip": clip,
        "mode": mode,
        "type": motion_type,
        "seed_idx": seed_idx,
        "candidate_k": candidate_k,
        "path": str(qpos_path),
        **report.summary(),
        **contact,
        **reference_sanity_metrics(qpos, motion_type),
    }
    row["full_risk"] = row["risk_score"]
    row["precontroller_score"] = precontroller_score(row)
    row["precontroller_gate_pass"] = "__YES__" if precontroller_gate(row) else "__NO__"
    return row


def select_rows(group: list[dict[str, object]]) -> list[dict[str, object]]:
    by_k = {int(row["candidate_k"]): row for row in group}
    out = []

    def add(selector: str, row: dict[str, object]) -> None:
        out.append(
            {
                **row,
                "selector": selector,
                "selected_motion": (
                    f"{selector}_{row['mode']}_seed{int(row['seed_idx'])}_cand{int(row['candidate_k'])}"
                ),
            }
        )

    add("baseline_k0", by_k.get(0, group[0]))
    add("lowest_id_risk", min(group, key=lambda r: float(r["full_risk"])))
    add("best_precontroller", max(group, key=lambda r: float(r["precontroller_score"])))
    gated = [row for row in group if row["precontroller_gate_pass"] == "__YES__"]
    if gated:
        add("gated_precontroller", max(gated, key=lambda r: float(r["precontroller_score"])))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=Path, default=ROOT / "results" / "prospective_native_selection")
    parser.add_argument("--data_dir", type=Path, default=ROOT / "data" / "prospective_native_selection")
    parser.add_argument("--modes", nargs="*", default=DEFAULT_MODES)
    parser.add_argument("--seed_start", type=int, default=7)
    parser.add_argument("--n_seeds", type=int, default=4)
    parser.add_argument("--K", type=int, default=4)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    args.out_dir = args.out_dir.resolve()
    args.data_dir = args.data_dir.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.data_dir.mkdir(parents=True, exist_ok=True)
    reference_root = args.out_dir / "sonic_references"
    reference_root.mkdir(parents=True, exist_ok=True)

    requested_modes = set(args.modes)
    available_modes = {cfg["mode"] for cfg in MOTION_CONFIGS}
    missing_modes = sorted(requested_modes - available_modes)
    if missing_modes:
        print(f"[warn] skipping unavailable MotionBricks modes: {', '.join(missing_modes)}")
    configs = [cfg for cfg in MOTION_CONFIGS if cfg["mode"] in requested_modes]
    if not configs:
        raise ValueError("No modes selected")

    agent = load_agent()
    full_critic = PhysicalAwarenessCritic()
    contact_model = mujoco.MjModel.from_xml_path(str(SCENE_XML))

    candidate_rows: list[dict[str, object]] = []
    selected_rows: list[dict[str, object]] = []
    export_rows: list[dict[str, object]] = []

    candidate_csv = args.out_dir / "prospective_candidates.csv"
    selected_csv = args.out_dir / "prospective_selected.csv"
    export_csv = args.out_dir / "export_manifest.csv"

    for cfg in configs:
        for seed_idx in range(args.seed_start, args.seed_start + args.n_seeds):
            clip = f"{cfg['mode']}_seed{seed_idx}"
            group: list[dict[str, object]] = []
            for candidate_k in range(args.K):
                qpos_path = args.data_dir / f"{clip}_cand{candidate_k}.npy"
                if qpos_path.exists() and not args.overwrite:
                    qpos = np.load(qpos_path)
                    print(f"[reuse] {qpos_path}")
                else:
                    seed = seed_idx * 1000 + candidate_k * 137
                    print(f"[generate] {clip} cand={candidate_k} seed={seed}")
                    qpos = generate_clip(
                        agent,
                        cfg["mode"],
                        cfg["n_frames"],
                        seed=seed,
                        stochastic=(candidate_k > 0),
                    )
                    np.save(qpos_path, qpos.astype(np.float32))

                row = score_candidate(
                    qpos,
                    qpos_path,
                    clip,
                    cfg["mode"],
                    cfg["type"],
                    seed_idx,
                    candidate_k,
                    full_critic,
                    contact_model,
                )
                candidate_rows.append(row)
                group.append(row)
                print(
                    f"  risk={float(row['full_risk']):.2f} "
                    f"contact={float(row['contact_artifact_score']):.3f} "
                    f"score={float(row['precontroller_score']):.3f} "
                    f"gate={row['precontroller_gate_pass']}"
                )
                write_rows(candidate_csv, candidate_rows)

            for selected in select_rows(group):
                selected_rows.append(selected)
                motion_dir = reference_root / str(selected["selected_motion"])
                qpos_path = Path(str(selected["path"]))
                export = export_clip(qpos_path, motion_dir, SOURCE_FPS, SONIC_FPS)
                export_rows.append(
                    {
                        **export,
                        "selector": selected["selector"],
                        "clip": selected["clip"],
                        "mode": selected["mode"],
                        "seed_idx": selected["seed_idx"],
                        "candidate_k": selected["candidate_k"],
                        "full_risk": selected["full_risk"],
                        "contact_artifact_score": selected["contact_artifact_score"],
                        "precontroller_score": selected["precontroller_score"],
                        "precontroller_gate_pass": selected["precontroller_gate_pass"],
                        "root_z_min": selected["root_z_min"],
                        "low_root_frames_pct": selected["low_root_frames_pct"],
                        "upright_reference_gate_pass": selected["upright_reference_gate_pass"],
                    }
                )
                print(f"[export] {selected['selected_motion']}")
                write_rows(selected_csv, selected_rows)
                write_rows(export_csv, export_rows)

    write_rows(candidate_csv, candidate_rows)
    write_rows(selected_csv, selected_rows)
    write_rows(export_csv, export_rows)
    print(f"Wrote candidates: {candidate_csv}")
    print(f"Wrote selections: {selected_csv}")
    print(f"Wrote SONIC refs: {reference_root}")


if __name__ == "__main__":
    main()
