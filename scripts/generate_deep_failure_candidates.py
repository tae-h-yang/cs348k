#!/usr/bin/env python3
"""Generate deeper MotionBricks candidate pools for native-SONIC failures."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_sonic_references import SONIC_FPS, SOURCE_FPS, export_clip  # noqa: E402
from run_humanoid100_motionbricks_experiment import (  # noqa: E402
    MODE_CONFIGS,
    PROMPTS_CSV,
    OnlineSegmentCritic,
    generate_clip,
    load_motionbricks_agent,
    prompt_proxy,
    read_rows,
    write_rows,
)


DEFAULT_BASE = ROOT / "results" / "ralphloop" / "20260529_191342" / "humanoid100_final_eval_k256"
DEFAULT_FAILURE_CSV = DEFAULT_BASE / "failed_prompt_native_variant_sweep" / "native_variant_rescue.csv"
DEFAULT_OUT_DIR = DEFAULT_BASE / "deep_failure_candidates"
DEFAULT_DATA_DIR = ROOT / "data" / "deep_failure_candidates"


def still_failing_prompt_ids(path: Path) -> list[str]:
    rows = read_rows(path)
    return [row["prompt_id"] for row in rows if row["best_no_fall"] not in ("True", "1", "__YES__")]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--failure_csv", type=Path, default=DEFAULT_FAILURE_CSV)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--data_dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--K", type=int, default=128)
    parser.add_argument("--top_n", type=int, default=4)
    parser.add_argument("--seed_offset", type=int, default=770000)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.data_dir.mkdir(parents=True, exist_ok=True)
    sonic_dir = args.out_dir / "sonic_references"
    sonic_dir.mkdir(parents=True, exist_ok=True)

    target_ids = set(still_failing_prompt_ids(args.failure_csv))
    prompts = [row for row in read_rows(PROMPTS_CSV) if row["prompt_id"] in target_ids]
    if not prompts:
        raise SystemExit(f"No still-failing prompts found in {args.failure_csv}")

    original_cwd = Path.cwd()
    demo_agent = load_motionbricks_agent()
    os.chdir(original_cwd)
    critic = OnlineSegmentCritic()

    manifest: list[dict[str, object]] = []
    for prompt_idx, prompt in enumerate(prompts, start=1):
        mode, status, semantic_validity, explanation = prompt_proxy(prompt)
        cfg = MODE_CONFIGS[mode]
        stem = args.data_dir / f"{prompt['prompt_id']}_{prompt['subcategory']}"
        print(
            f"\n[{prompt_idx:02d}/{len(prompts):02d}] {prompt['prompt_id']} "
            f"{prompt['subcategory']} -> {mode}; K={args.K}"
        )
        scored: list[tuple[float, int, int, np.ndarray]] = []
        meta_rows: list[dict[str, object]] = []
        for k in range(args.K):
            seed = args.seed_offset + int(prompt["prompt_id"].split("_")[1]) * 10000 + k * 137
            qpos = generate_clip(demo_agent, mode, cfg["frames"], seed=seed, stochastic=True)
            risk = float(critic.score_segment(qpos))
            scored.append((risk, k, seed, qpos))
            meta_rows.append({"candidate_k": k, "seed": seed, "segment_risk": risk})
            if k % max(1, args.K // 8) == 0:
                print(f"  k={k:04d} seed={seed} seg_risk={risk:.2f}")

        scored.sort(key=lambda item: item[0])
        write_rows(stem.with_name(f"{stem.name}_deepK{args.K}_candidates.csv"), meta_rows)
        for rank, (risk, k, seed, qpos) in enumerate(scored[: args.top_n], start=1):
            name = f"{prompt['prompt_id']}_{prompt['subcategory']}_deep{rank:02d}_k{k:04d}"
            qpos_path = args.data_dir / f"{name}.npy"
            if args.overwrite or not qpos_path.exists():
                np.save(qpos_path, qpos.astype(np.float32))
            exported = export_clip(qpos_path, sonic_dir / name, SOURCE_FPS, SONIC_FPS)
            manifest.append(
                {
                    "prompt_id": prompt["prompt_id"],
                    "category": prompt["category"],
                    "subcategory": prompt["subcategory"],
                    "prompt_text": prompt["prompt_text"],
                    "proxy_mode": mode,
                    "executable_status": status,
                    "semantic_validity": semantic_validity,
                    "audit_interpretation": explanation,
                    "candidate_name": name,
                    "rank": rank,
                    "candidate_k": k,
                    "seed": seed,
                    "segment_risk": risk,
                    "qpos_path": str(qpos_path),
                    "sonic_reference": str(sonic_dir / name),
                    **exported,
                }
            )
            print(f"  saved rank={rank} k={k} risk={risk:.2f} -> {name}")
        write_rows(args.out_dir / "manifest.csv", manifest)

    write_rows(args.out_dir / "manifest.csv", manifest)
    (args.out_dir / "README.md").write_text(
        "\n".join(
            [
                "# Deep Failure Candidates",
                "",
                f"- Source failure CSV: `{args.failure_csv}`",
                f"- Prompts: `{len(prompts)}`",
                f"- K per prompt: `{args.K}`",
                f"- Top candidates exported per prompt: `{args.top_n}`",
                f"- SONIC references: `{sonic_dir}`",
                f"- Manifest: `{args.out_dir / 'manifest.csv'}`",
                "",
                "These candidates target the remaining native-SONIC failures after the K1/K8/K9 rescue sweep.",
                "",
            ]
        )
    )
    print(f"\nWrote {args.out_dir / 'manifest.csv'}")
    print(f"SONIC refs: {sonic_dir}")


if __name__ == "__main__":
    main()
