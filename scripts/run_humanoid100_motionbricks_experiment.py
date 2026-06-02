"""Run a full 100-row MotionBricks proxy experiment.

Each target prompt gets its own generated K=1 baseline and K=8 best-of-K clip.
The local MotionBricks preview exposes only a small G1 mode set, so prompts that
cannot be executed semantically are mapped to a nearest available proxy mode and
marked as forced proxies. This script still performs the same generation,
physics scoring, and before/after rendering workflow for all 100 prompt rows.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_humanoid_100_prompts import (  # noqa: E402
    PROMPTS_CSV,
    forced_proxy_mode_for,
    proxy_mode_for,
    render_proxy_video,
    write_rows,
)
from generate_guided import generate_clip  # noqa: E402
from physics_eval.online_critic import OnlineSegmentCritic  # noqa: E402
from physics_eval.physaware import PhysicalAwarenessCritic  # noqa: E402


MOTIONBRICKS_DIR = ROOT.parent / "GR00T-WholeBodyControl" / "motionbricks"
DATA_DIR = ROOT / "data" / "humanoid100_motionbricks"
OUT_DIR = ROOT / "results" / "humanoid100_motionbricks_experiment"

MODE_CONFIGS = {
    "idle": {"frames": 150, "type": "static"},
    "walk": {"frames": 200, "type": "locomotion"},
    "slow_walk": {"frames": 200, "type": "locomotion"},
    "stealth_walk": {"frames": 200, "type": "locomotion"},
    "injured_walk": {"frames": 200, "type": "locomotion"},
    "walk_zombie": {"frames": 200, "type": "locomotion"},
    "walk_stealth": {"frames": 180, "type": "locomotion"},
    "walk_left": {"frames": 180, "type": "locomotion"},
    "walk_right": {"frames": 180, "type": "locomotion"},
    "walk_boxing": {"frames": 180, "type": "expressive"},
    "walk_happy_dance": {"frames": 180, "type": "expressive"},
    "walk_gun": {"frames": 180, "type": "expressive"},
    "walk_scared": {"frames": 180, "type": "expressive"},
    "hand_crawling": {"frames": 150, "type": "whole_body"},
    "elbow_crawling": {"frames": 150, "type": "whole_body"},
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def load_motionbricks_agent():
    original_dir = Path.cwd()
    os.chdir(MOTIONBRICKS_DIR)
    import argparse as ap
    from motionbricks.motion_backbone.demo.utils import navigation_demo

    mb_args = ap.Namespace(
        explicit_dataset_folder=None, reprocess_clips=0, controller="random",
        lookat_movement_direction=0, has_viewer=0, pre_filter_qpos=1,
        source_root_realignment=1, target_root_realignment=1,
        force_canonicalization=1, skip_ending_target_cond=0,
        random_speed_scale=0, speed_scale=[0.8, 1.2], generate_dt=2.0,
        max_steps=10000, random_seed=42, num_runs=1, use_qpos=1,
        planner="default", allowed_mode=None, clips="G1",
        return_model_configs=True, return_dataloader=True,
        recording_dir=None, EXP="default",
    )
    print("Loading MotionBricks model...")
    demo_agent = navigation_demo(mb_args)
    os.chdir(original_dir)
    return demo_agent


def prompt_proxy(prompt: dict[str, str]) -> tuple[str, str, str, str]:
    mode, status, explanation = proxy_mode_for(prompt)
    if mode:
        return mode, status, "supported_proxy", explanation
    mode, explanation = forced_proxy_mode_for(prompt)
    return mode, "forced_proxy", "forced_proxy_not_prompt_following", explanation


def generate_best_of_k(
    demo_agent,
    mode: str,
    frames: int,
    base_seed: int,
    K: int,
    critic: OnlineSegmentCritic,
    out_stem: Path,
    overwrite: bool,
) -> tuple[np.ndarray, dict[str, object]]:
    out_path = out_stem.with_name(f"{out_stem.name}_K{K}.npy")
    meta_path = out_stem.with_name(f"{out_stem.name}_K{K}_candidates.csv")
    if out_path.exists() and not overwrite:
        qpos = np.load(out_path)
        return qpos, {"best_k": "", "best_seg_risk": "", "candidate_csv": str(meta_path), "path": str(out_path)}

    candidates: list[dict[str, object]] = []
    best_qpos: np.ndarray | None = None
    best_risk = float("inf")
    best_k = -1
    for k in range(K):
        seed = base_seed + k * 137
        stochastic = k > 0
        qpos = generate_clip(demo_agent, mode, frames, seed=seed, stochastic=stochastic)
        risk = float(critic.score_segment(qpos))
        candidates.append({"candidate_k": k, "seed": seed, "stochastic": stochastic, "segment_risk": risk})
        print(f"      k={k:02d} seed={seed:<6d} stochastic={stochastic} seg_risk={risk:.2f}")
        if risk < best_risk:
            best_risk = risk
            best_k = k
            best_qpos = qpos

    if best_qpos is None:
        raise RuntimeError(f"No valid candidate for {out_stem} K={K}")

    np.save(out_path, best_qpos.astype(np.float32))
    write_rows(meta_path, candidates)
    return best_qpos, {
        "best_k": best_k,
        "best_seg_risk": best_risk,
        "candidate_csv": str(meta_path),
        "path": str(out_path),
    }


def write_report(rows: list[dict[str, object]], out_dir: Path) -> None:
    supported = sum(row["semantic_validity"] == "supported_proxy" for row in rows)
    forced = sum(row["semantic_validity"] == "forced_proxy_not_prompt_following" for row in rows)
    improved = sum(float(row["after_risk"]) < float(row["before_risk"]) for row in rows)
    worsened = sum(float(row["after_risk"]) > float(row["before_risk"]) for row in rows)
    tied = len(rows) - improved - worsened
    mean_before = float(np.mean([float(row["before_risk"]) for row in rows]))
    mean_after = float(np.mean([float(row["after_risk"]) for row in rows]))
    reduction = 100.0 * (mean_before - mean_after) / max(mean_before, 1e-8)
    by_category: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_category[str(row["category"])].append(row)
    lines = [
        "# Humanoid 100 MotionBricks Experiment",
        "",
        "Every target prompt receives a freshly generated K=1 baseline and K=8",
        "best-of-K MotionBricks proxy clip, then the same physics-risk scoring and",
        "before/after rendering workflow used for the smaller mode suite.",
        "",
        "## Summary",
        "",
        f"- Prompts evaluated: {len(rows)}",
        f"- Supported/coarse local proxies: {supported}",
        f"- Forced nearest-mode proxies: {forced}",
        f"- Improved K=8 over K=1: {improved}/{len(rows)}",
        f"- Worsened K=8 over K=1: {worsened}/{len(rows)}",
        f"- Tied K=8 and K=1: {tied}/{len(rows)}",
        f"- Mean risk K=1: {mean_before:.3f}",
        f"- Mean risk K=8: {mean_after:.3f}",
        f"- Aggregate risk reduction: {reduction:.2f}%",
        "",
        "## Category Summary",
        "",
        "| Category | n | mean K=1 risk | mean K=8 risk | reduction |",
        "|---|---:|---:|---:|---:|",
    ]
    category_rows: list[dict[str, object]] = []
    for category, group in sorted(by_category.items()):
        before = np.array([float(row["before_risk"]) for row in group])
        after = np.array([float(row["after_risk"]) for row in group])
        category_reduction = 100.0 * (float(before.mean()) - float(after.mean())) / max(float(before.mean()), 1e-8)
        category_rows.append({
            "category": category,
            "n": len(group),
            "mean_before_risk": float(before.mean()),
            "mean_after_risk": float(after.mean()),
            "aggregate_reduction_pct": category_reduction,
            "improved": sum(a < b for a, b in zip(after, before)),
            "worsened": sum(a > b for a, b in zip(after, before)),
        })
        lines.append(
            f"| `{category}` | {len(group)} | {float(before.mean()):.2f} | "
            f"{float(after.mean()):.2f} | {category_reduction:.1f}% |"
        )
    write_rows(out_dir / "category_summary.csv", category_rows)
    lines.extend([
        "",
        "## Caveat",
        "",
        "This completes the 100-row generation/evaluation workflow, but it does not",
        "mean the local MotionBricks preview semantically solves all 100 prompts.",
        "Rows labeled `forced_proxy_not_prompt_following` use the nearest exposed",
        "G1 mode because the preview lacks arbitrary text/task-conditioned control.",
        "",
        "## Files",
        "",
        f"- CSV: `{out_dir / 'humanoid100_motionbricks_results.csv'}`",
        f"- Videos: `{out_dir / 'videos'}`",
        f"- Qpos: `{DATA_DIR}`",
        "",
    ])
    (out_dir / "README.md").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--k_after", type=int, default=8)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--out_dir", type=Path, default=OUT_DIR)
    parser.add_argument("--data_dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "videos").mkdir(parents=True, exist_ok=True)
    args.data_dir.mkdir(parents=True, exist_ok=True)

    prompts = read_rows(PROMPTS_CSV)[: args.limit]
    demo_agent = load_motionbricks_agent()
    segment_critic = OnlineSegmentCritic()
    full_critic = PhysicalAwarenessCritic()
    rows: list[dict[str, object]] = []

    for i, prompt in enumerate(prompts, start=1):
        mode, status, semantic_validity, explanation = prompt_proxy(prompt)
        cfg = MODE_CONFIGS[mode]
        stem = args.data_dir / f"{prompt['prompt_id']}_{prompt['subcategory']}"
        base_seed = i * 10000
        print(f"\n[{i:03d}/100] {prompt['prompt_id']} {prompt['subcategory']} -> {mode} ({semantic_validity})")

        q1, meta1 = generate_best_of_k(
            demo_agent, mode, cfg["frames"], base_seed, 1, segment_critic, stem, args.overwrite
        )
        q8, meta8 = generate_best_of_k(
            demo_agent, mode, cfg["frames"], base_seed, args.k_after, segment_critic, stem, args.overwrite
        )
        report1, _ = full_critic.score(q1, str(stem.name), cfg["type"], "K1")
        report8, _ = full_critic.score(q8, str(stem.name), cfg["type"], f"K{args.k_after}")
        before = float(report1.risk_score)
        after = float(report8.risk_score)
        improvement = 100.0 * (before - after) / before if before > 1e-6 else float("nan")

        row: dict[str, object] = {
            "prompt_id": prompt["prompt_id"],
            "category": prompt["category"],
            "subcategory": prompt["subcategory"],
            "prompt_text": prompt["prompt_text"],
            "success_criteria": prompt["success_criteria"],
            "current_motionbricks_support": prompt["current_motionbricks_support"],
            "motionbricks_mode_hint": prompt["motionbricks_mode_hint"],
            "proxy_mode": mode,
            "executable_status": status,
            "semantic_validity": semantic_validity,
            "audit_interpretation": explanation,
            "before_K": 1,
            "after_K": args.k_after,
            "before_risk": before,
            "after_risk": after,
            "risk_improvement_pct": improvement,
            "before_action": report1.recommended_action,
            "after_action": report8.recommended_action,
            "before_best_k": meta1["best_k"],
            "after_best_k": meta8["best_k"],
            "before_seg_risk": meta1["best_seg_risk"],
            "after_seg_risk": meta8["best_seg_risk"],
            "before_qpos_path": meta1["path"],
            "after_qpos_path": meta8["path"],
            "before_candidate_csv": meta1["candidate_csv"],
            "after_candidate_csv": meta8["candidate_csv"],
            "render_status": "proxy_before_after",
            "video_path": str(args.out_dir / "videos" / f"{prompt['prompt_id']}_{prompt['subcategory']}.mp4"),
        }
        rows.append(row)
        write_rows(args.out_dir / "humanoid100_motionbricks_results.csv", rows)
        write_report(rows, args.out_dir)
        print(f"      full_risk K1={before:.2f} K{args.k_after}={after:.2f} improvement={improvement:.1f}%")

        if args.render:
            render_proxy_video(row, Path(str(row["video_path"])))
            print(f"      rendered {row['video_path']}")

    write_rows(args.out_dir / "humanoid100_motionbricks_results.csv", rows)
    write_report(rows, args.out_dir)
    print(f"\nWrote {len(rows)} rows to {args.out_dir / 'humanoid100_motionbricks_results.csv'}")


if __name__ == "__main__":
    main()
