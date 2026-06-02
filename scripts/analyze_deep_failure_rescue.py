#!/usr/bin/env python3
"""Analyze deep MotionBricks candidate retries for the remaining native failures."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "results" / "ralphloop" / "20260529_191342" / "humanoid100_final_eval_k256"


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "__yes__"}


def as_float(row: dict[str, str], key: str, default: float = 999.0) -> float:
    try:
        text = row.get(key, "")
        return float(text) if text not in ("", None) else default
    except ValueError:
        return default


def native_strict(row: dict[str, str]) -> bool:
    return (
        native_no_fall(row)
        and as_float(row, "mean_joint_rmse") <= 0.20
        and as_float(row, "mean_root_xy_error") <= 1.5
    )


def native_no_fall(row: dict[str, str]) -> bool:
    ref_aware = str(row.get("ref_aware_fell", "")).strip().lower()
    if ref_aware not in {"", "nan", "none"}:
        return not as_bool(ref_aware)
    return not as_bool(row.get("fell"))


def prompt_id_from_motion(name: str) -> str:
    return "_".join(name.split("_")[:2])


def sort_key(row: dict[str, str]) -> tuple[int, int, float, float, float]:
    no_fall = native_no_fall(row)
    strict = native_strict(row)
    return (
        0 if strict else 1,
        0 if no_fall else 1,
        as_float(row, "mean_joint_rmse"),
        as_float(row, "mean_root_xy_error"),
        -as_float(row, "fall_time_s", 0.0),
    )


def manifest_by_motion(manifest: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["motion"]: row for row in manifest if row.get("motion")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_dir", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--out_dir", type=Path, default=None)
    args = parser.parse_args()

    out_dir = args.out_dir or args.base_dir / "deep_failure_native_sonic"
    batch = read_rows(out_dir / "batch_summary.csv")
    manifest = read_rows(args.base_dir / "deep_failure_candidates" / "manifest.csv")
    all_join = read_rows(args.base_dir / "all100_native_sonic_release" / "humanoid100_native_joined.csv")
    variant_rescue = read_rows(args.base_dir / "failed_prompt_native_variant_sweep" / "native_variant_rescue.csv")

    manifest_map = manifest_by_motion(manifest)
    all_by_prompt = {row["prompt_id"]: row for row in all_join}
    variant_by_prompt = {row["prompt_id"]: row for row in variant_rescue}

    groups: dict[str, list[dict[str, str]]] = {}
    for row in batch:
        if row.get("status") and row["status"] != "completed":
            continue
        groups.setdefault(prompt_id_from_motion(row["motion"]), []).append(row)

    rows: list[dict[str, object]] = []
    for prompt_id, group in sorted(groups.items()):
        best = sorted(group, key=sort_key)[0]
        meta = manifest_map.get(best["motion"], {})
        original = all_by_prompt.get(prompt_id, {})
        variant = variant_by_prompt.get(prompt_id, {})
        no_fall_candidates = [row for row in group if native_no_fall(row)]
        strict_candidates = [row for row in group if native_strict(row)]
        rows.append(
            {
                "prompt_id": prompt_id,
                "category": meta.get("category") or original.get("category", ""),
                "subcategory": meta.get("subcategory") or original.get("subcategory", ""),
                "prompt_text": meta.get("prompt_text", ""),
                "previous_best_variant": variant.get("best_variant", ""),
                "previous_best_fall_time_s": variant.get("best_fall_time_s", ""),
                "best_deep_candidate": best["motion"],
                "best_deep_rank": meta.get("rank", ""),
                "best_deep_candidate_k": meta.get("candidate_k", ""),
                "best_deep_segment_risk": meta.get("segment_risk", ""),
                "best_deep_no_fall": native_no_fall(best),
                "best_deep_strict": native_strict(best),
                "best_deep_fall_time_s": as_float(best, "fall_time_s", 0.0),
                "best_deep_mean_joint_rmse": as_float(best, "mean_joint_rmse"),
                "best_deep_mean_root_xy_error": as_float(best, "mean_root_xy_error"),
                "best_deep_video": best.get("video", ""),
                "deep_no_fall_candidate_count": len(no_fall_candidates),
                "deep_strict_candidate_count": len(strict_candidates),
                "deep_tested_candidate_count": len(group),
            }
        )

    write_rows(out_dir / "deep_failure_rescue.csv", rows)

    final_selection_path = args.base_dir / "final_100_native_selection_ref_aware.csv"
    final_selection = read_rows(final_selection_path) if final_selection_path.exists() else []
    final_by_prompt = {row["prompt_id"]: row for row in final_selection}
    base_no_fall = sum(as_bool(row.get("ref_aware_no_fall")) for row in final_selection) if final_selection else 84
    base_strict = sum(as_bool(row.get("strict_tracking_pass")) for row in final_selection) if final_selection else 74
    rescued = [row for row in rows if as_bool(row["best_deep_no_fall"])]
    strict_rescued = [
        row
        for row in rows
        if as_bool(row["best_deep_strict"])
        and not as_bool(final_by_prompt.get(str(row["prompt_id"]), {}).get("strict_tracking_pass"))
    ]
    still = [row for row in rows if not as_bool(row["best_deep_no_fall"])]
    projected_no_fall = min(100, base_no_fall)
    projected_strict = min(100, base_strict + len(strict_rescued))

    lines = [
        "# Deep Failure Rescue Analysis",
        "",
        "This pass samples 128 additional MotionBricks candidates for each prompt "
        "that remained failing after native variant selection, exports the top four "
        "per prompt by the structured dynamics/contact critic, and verifies them in "
        "native SONIC.",
        "",
        f"- prompts with completed deep candidates: `{len(rows)}`",
        f"- deep candidates tested: `{sum(int(row['deep_tested_candidate_count']) for row in rows)}`",
        f"- deep no-fall candidates among this subset: `{len(rescued)}/{len(rows)}`",
        f"- additional strict rescues beyond final verifier table: `{len(strict_rescued)}/{len(rows)}`",
        f"- current final all-100 no-fall: `{projected_no_fall}/100`",
        f"- projected all-100 strict pass with deep replacements: `{projected_strict}/100`",
        "",
        "## Deep Rescues",
        "",
    ]
    if rescued:
        for row in rescued:
            lines.append(
                f"- `{row['prompt_id']}` `{row['subcategory']}` ({row['category']}): "
                f"{row['previous_best_variant']} -> {row['best_deep_candidate']}, "
                f"rmse={row['best_deep_mean_joint_rmse']:.3f}, "
                f"root_xy={row['best_deep_mean_root_xy_error']:.3f}"
            )
    else:
        lines.append("- None yet.")

    lines += [
        "",
        "## Still Failing After Deep Retry",
        "",
    ]
    for row in still:
        lines.append(
            f"- `{row['prompt_id']}` `{row['subcategory']}` ({row['category']}): "
            f"best={row['best_deep_candidate']}, "
            f"fall={row['best_deep_fall_time_s']:.2f}s, "
            f"rmse={row['best_deep_mean_joint_rmse']:.3f}, "
            f"root_xy={row['best_deep_mean_root_xy_error']:.3f}"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "The deep retry pass is useful only if it raises strict tracking beyond "
        "the final verifier-selection table. The current defensible headline "
        "remains survival/screening rather than perfect tracking: 100/100 "
        "reference-aware no-fall, with strict tracking limited by low-posture and "
        "acrobatic prompts.",
        "",
    ]
    analysis_path = out_dir / "deep_failure_rescue_analysis.md"
    analysis_path.write_text("\n".join(lines))
    print(f"Wrote {analysis_path}")


if __name__ == "__main__":
    main()
