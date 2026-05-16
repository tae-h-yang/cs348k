"""Evaluate prompt-derived MotionSpec predicates on existing generated clips.

This is the first pass at a MoVer-like verifier for humanoid robot references.
It works on the currently executable 105-row MotionBricks mode suite and joins
three existing evidence streams:

- prompt/task proxy features from ``results/prompt_alignment.csv``
- contact and inverse-dynamics features from ``results/contact_quality.csv``
- optional approximate SONIC tracking outcomes

The output is a predicate table plus selector summary. It is deliberately
transparent: every failed predicate is named in ``failed_predicates``.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROMPT_ALIGNMENT = ROOT / "results" / "prompt_alignment.csv"
DEFAULT_CONTACT = ROOT / "results" / "contact_quality.csv"
DEFAULT_SONIC = ROOT / "results" / "sonic_policy_mujoco_tracking_210_fixed.csv"
DEFAULT_OUT = ROOT / "results" / "motionspec_predicates.csv"
DEFAULT_SUMMARY = ROOT / "results" / "motionspec_summary.csv"
DEFAULT_SELECTOR = ROOT / "results" / "motionspec_selector_comparison.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def f(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def b(row: dict[str, str], key: str) -> bool:
    value = str(row.get(key, "")).strip().lower()
    return value in {"true", "1", "yes", "__yes__"}


def clip_key_from_reference(reference: str) -> tuple[str, int] | None:
    # Examples: walk_seed0_K1, elbow_crawling_seed6_K8
    if "_K" not in reference:
        return None
    stem, k = reference.rsplit("_K", 1)
    try:
        return stem, int(k)
    except ValueError:
        return None


def index_contact(rows: Iterable[dict[str, str]]) -> dict[tuple[str, int], dict[str, str]]:
    out: dict[tuple[str, int], dict[str, str]] = {}
    for row in rows:
        out[(row["clip"], int(row["K"]))] = row
    return out


def index_sonic(rows: Iterable[dict[str, str]]) -> dict[tuple[str, int], dict[str, str]]:
    out: dict[tuple[str, int], dict[str, str]] = {}
    for row in rows:
        key = clip_key_from_reference(row.get("reference", ""))
        if key is not None:
            out[key] = row
    return out


def category_predicates(row: dict[str, str]) -> dict[str, bool]:
    category = row["category"]
    target_speed = f(row, "target_speed_mps")
    mean_speed = f(row, "mean_speed_mps")
    displacement = f(row, "planar_displacement_m")
    mean_height = f(row, "mean_root_height_m")
    min_height = f(row, "min_root_height_m")
    direction_score = f(row, "direction_score")
    speed_score = f(row, "speed_score")
    style_score = f(row, "style_proxy_score")
    arm_ratio = f(row, "arm_leg_motion_ratio")

    checks: dict[str, bool] = {}
    checks["prompt_direction"] = direction_score >= 0.60
    checks["prompt_speed"] = speed_score >= 0.45
    checks["root_not_collapsed"] = min_height >= 0.35

    if target_speed <= 1e-6 or category == "static":
        checks["static_low_translation"] = displacement <= 0.25
        checks["static_low_speed"] = mean_speed <= 0.08
    else:
        checks["meaningful_progress"] = displacement >= 0.35

    if category == "whole_body_low":
        checks["low_posture"] = mean_height <= 0.72
    else:
        checks["upright_or_task_height"] = mean_height >= 0.55

    if category == "expressive_locomotion":
        checks["upper_body_expressive"] = arm_ratio >= 0.65 or style_score >= 0.45
    elif category in {"locomotion", "directional_locomotion", "style_locomotion"}:
        checks["not_arm_dominated"] = arm_ratio <= 5.0

    return checks


def contact_predicates(row: dict[str, str] | None, category: str) -> dict[str, bool]:
    if row is None:
        return {"contact_metrics_present": False}

    nonfoot_allowed = category == "whole_body_low"
    return {
        "contact_metrics_present": True,
        "low_self_contact": f(row, "self_contact_frames_pct") <= 5.0,
        "low_nonfoot_floor_contact": (
            f(row, "nonfoot_floor_contact_frames_pct") <= (40.0 if nonfoot_allowed else 5.0)
        ),
        "low_foot_skate": f(row, "p95_contact_foot_speed_mps") <= 1.25,
        "low_contact_artifact_score": f(row, "contact_artifact_score") <= 0.45,
        "floor_penetration_bounded": f(row, "max_floor_penetration_m") <= 0.08,
    }


def dynamics_predicates(row: dict[str, str] | None) -> dict[str, bool]:
    if row is None:
        return {"dynamics_metrics_present": False}
    risk = f(row, "full_risk", default=float("inf"))
    return {
        "dynamics_metrics_present": True,
        "inverse_dynamics_risk_below_25": risk <= 25.0,
        "inverse_dynamics_risk_below_50": risk <= 50.0,
    }


def sonic_predicates(row: dict[str, str] | None) -> dict[str, bool]:
    if row is None:
        return {"sonic_metrics_present": False}
    return {
        "sonic_metrics_present": True,
        "sonic_no_fall": not b(row, "fell"),
        "sonic_survives_3s": f(row, "track_seconds") >= 3.0,
        "sonic_rmse_below_0p35": f(row, "mean_tracking_rmse") <= 0.35,
    }


def score_checks(checks: dict[str, bool]) -> tuple[float, list[str], int, int]:
    keys = [k for k in checks if not k.endswith("_present")]
    passed = [k for k in keys if checks[k]]
    failed = [k for k in keys if not checks[k]]
    return len(passed) / max(len(keys), 1), failed, len(passed), len(keys)


def evaluate(args: argparse.Namespace) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    prompt_rows = read_rows(args.prompt_alignment)
    contact = index_contact(read_rows(args.contact))
    sonic = index_sonic(read_rows(args.sonic))

    pred_rows: list[dict[str, object]] = []
    for row in prompt_rows:
        clip = row["clip"]
        k = int(row["K"])
        contact_row = contact.get((clip, k))
        sonic_row = sonic.get((clip, k))

        checks: dict[str, bool] = {}
        checks.update(category_predicates(row))
        checks.update(contact_predicates(contact_row, row["category"]))
        checks.update(dynamics_predicates(contact_row))
        checks.update(sonic_predicates(sonic_row))

        score, failed, passed_count, total_count = score_checks(checks)
        pred_rows.append({
            "prompt_id": row["prompt_id"],
            "clip": clip,
            "category": row["category"],
            "mode": row["mode"],
            "seed_idx": row["seed_idx"],
            "K": k,
            "prompt_text": row["prompt_text"],
            "motionspec_score": score,
            "motionspec_passed": passed_count,
            "motionspec_total": total_count,
            "failed_predicates": ";".join(failed),
            "alignment_score": f(row, "alignment_score"),
            "contact_artifact_score": f(contact_row or {}, "contact_artifact_score", float("nan")),
            "full_risk": f(contact_row or {}, "full_risk", float("nan")),
            "sonic_fell": b(sonic_row or {}, "fell") if sonic_row else "",
            "sonic_track_seconds": f(sonic_row or {}, "track_seconds", float("nan")),
            "sonic_rmse": f(sonic_row or {}, "mean_tracking_rmse", float("nan")),
            **{f"pred_{key}": value for key, value in checks.items()},
        })

    summary = summarize(pred_rows)
    selector = selector_summary(pred_rows)
    return pred_rows, summary, selector


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for group_name, group in grouped(rows, lambda r: f"K={r['K']}").items():
        out.append(summary_row(group_name, group))
    for group_name, group in grouped(rows, lambda r: f"{r['category']}_K={r['K']}").items():
        out.append(summary_row(group_name, group))
    return out


def grouped(rows: list[dict[str, object]], key_fn) -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        out[key_fn(row)].append(row)
    return dict(sorted(out.items()))


def summary_row(group_name: str, rows: list[dict[str, object]]) -> dict[str, object]:
    scores = np.array([float(r["motionspec_score"]) for r in rows], dtype=float)
    alignment = np.array([float(r["alignment_score"]) for r in rows], dtype=float)
    contact = np.array([float(r["contact_artifact_score"]) for r in rows], dtype=float)
    sonic_seconds = np.array([float(r["sonic_track_seconds"]) for r in rows], dtype=float)
    return {
        "group": group_name,
        "n": len(rows),
        "mean_motionspec_score": float(np.nanmean(scores)),
        "median_motionspec_score": float(np.nanmedian(scores)),
        "strict_pass_count": int(np.sum(scores >= 0.999)),
        "mean_alignment_score": float(np.nanmean(alignment)),
        "mean_contact_artifact_score": float(np.nanmean(contact)),
        "mean_sonic_track_seconds": float(np.nanmean(sonic_seconds)),
    }


def selector_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_clip: dict[str, dict[int, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        by_clip[str(row["clip"])][int(row["K"])] = row

    paired = {clip: ks for clip, ks in by_clip.items() if 1 in ks and 8 in ks}
    selected = []
    for clip, ks in paired.items():
        k1 = ks[1]
        k8 = ks[8]
        best_spec = max([k1, k8], key=lambda r: (float(r["motionspec_score"]), float(r["alignment_score"])))
        best_controller = max([k1, k8], key=lambda r: (float(r["sonic_track_seconds"]), -float(r["sonic_rmse"])))
        selected.extend([
            {"selector": "K1_baseline", **compact_selection(clip, k1)},
            {"selector": "K8_inverse_dynamics_existing", **compact_selection(clip, k8)},
            {"selector": "MotionSpec_over_K1_K8", **compact_selection(clip, best_spec)},
            {"selector": "SONIC_oracle_over_K1_K8", **compact_selection(clip, best_controller)},
        ])

    out: list[dict[str, object]] = []
    for selector, group in grouped(selected, lambda r: str(r["selector"])).items():
        scores = np.array([float(r["motionspec_score"]) for r in group], dtype=float)
        alignment = np.array([float(r["alignment_score"]) for r in group], dtype=float)
        contact = np.array([float(r["contact_artifact_score"]) for r in group], dtype=float)
        sonic_seconds = np.array([float(r["sonic_track_seconds"]) for r in group], dtype=float)
        out.append({
            "selector": selector,
            "n": len(group),
            "selected_K1_count": int(sum(int(r["K"]) == 1 for r in group)),
            "selected_K8_count": int(sum(int(r["K"]) == 8 for r in group)),
            "mean_motionspec_score": float(np.nanmean(scores)),
            "mean_alignment_score": float(np.nanmean(alignment)),
            "mean_contact_artifact_score": float(np.nanmean(contact)),
            "mean_sonic_track_seconds": float(np.nanmean(sonic_seconds)),
            "sonic_survives_3s_count": int(sum(float(r["sonic_track_seconds"]) >= 3.0 for r in group)),
        })
    return out


def compact_selection(clip: str, row: dict[str, object]) -> dict[str, object]:
    return {
        "clip": clip,
        "K": row["K"],
        "category": row["category"],
        "motionspec_score": row["motionspec_score"],
        "alignment_score": row["alignment_score"],
        "contact_artifact_score": row["contact_artifact_score"],
        "full_risk": row["full_risk"],
        "sonic_track_seconds": row["sonic_track_seconds"],
        "sonic_rmse": row["sonic_rmse"],
        "failed_predicates": row["failed_predicates"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt_alignment", type=Path, default=DEFAULT_PROMPT_ALIGNMENT)
    parser.add_argument("--contact", type=Path, default=DEFAULT_CONTACT)
    parser.add_argument("--sonic", type=Path, default=DEFAULT_SONIC)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--selector", type=Path, default=DEFAULT_SELECTOR)
    args = parser.parse_args()

    rows, summary, selector = evaluate(args)
    write_csv(args.out, rows)
    write_csv(args.summary, summary)
    write_csv(args.selector, selector)
    print(f"Wrote {len(rows)} predicate rows to {args.out}")
    print(f"Wrote summary to {args.summary}")
    print(f"Wrote selector comparison to {args.selector}")


if __name__ == "__main__":
    main()
