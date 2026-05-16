"""Build a joined candidate evidence table and combined selector comparison.

This script takes the MotionSpec predicate output and turns it into a
research-facing candidate table with normalized semantic, contact, dynamics, and
controller scores. It also compares simple selectors over the current paired
K=1/K=8 candidate set.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "results" / "motionspec_predicates.csv"
DEFAULT_OUT = ROOT / "results" / "candidate_evidence_table.csv"
DEFAULT_SELECTOR = ROOT / "results" / "combined_selector_comparison.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
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


def f(row: dict[str, str], key: str, default: float = float("nan")) -> float:
    try:
        value = float(row.get(key, default))
    except (TypeError, ValueError):
        return default
    return value


def normalize_clip(row: dict[str, str]) -> dict[str, object]:
    motionspec = f(row, "motionspec_score", 0.0)
    alignment = f(row, "alignment_score", 0.0)
    contact_artifact = f(row, "contact_artifact_score", 1.0)
    full_risk = f(row, "full_risk", 100.0)
    sonic_seconds = f(row, "sonic_track_seconds", 0.0)
    sonic_rmse = f(row, "sonic_rmse", 1.0)

    semantic_score = float(np.clip(0.65 * motionspec + 0.35 * alignment, 0.0, 1.0))
    contact_score = float(np.clip(1.0 - contact_artifact, 0.0, 1.0))
    dynamics_score = float(math.exp(-max(full_risk, 0.0) / 35.0))
    controller_survival_score = float(np.clip(sonic_seconds / 5.0, 0.0, 1.0))
    controller_rmse_score = float(math.exp(-max(sonic_rmse, 0.0) / 0.35))
    controller_score = float(np.clip(0.70 * controller_survival_score + 0.30 * controller_rmse_score, 0.0, 1.0))

    hard_gate_pass = (
        motionspec >= 0.60
        and contact_artifact <= 0.50
        and full_risk <= 50.0
        and sonic_seconds >= 1.5
    )
    controller_gate_pass = sonic_seconds >= 3.0 and sonic_rmse <= 0.35

    combined_score = (
        0.32 * semantic_score
        + 0.22 * contact_score
        + 0.16 * dynamics_score
        + 0.30 * controller_score
    )
    no_controller_score = (
        0.42 * semantic_score
        + 0.30 * contact_score
        + 0.28 * dynamics_score
    )

    return {
        **row,
        "semantic_score": semantic_score,
        "contact_score": contact_score,
        "dynamics_score": dynamics_score,
        "controller_score": controller_score,
        "combined_score": combined_score,
        "no_controller_score": no_controller_score,
        "hard_gate_pass": "__YES__" if hard_gate_pass else "__NO__",
        "controller_gate_pass": "__YES__" if controller_gate_pass else "__NO__",
    }


def group_pairs(rows: list[dict[str, object]]) -> dict[str, dict[int, dict[str, object]]]:
    out: dict[str, dict[int, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        out[str(row["clip"])][int(row["K"])] = row
    return {clip: ks for clip, ks in out.items() if 1 in ks and 8 in ks}


def selector_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    paired = group_pairs(rows)
    chosen: list[dict[str, object]] = []
    for clip, ks in paired.items():
        k1 = ks[1]
        k8 = ks[8]
        candidates = [k1, k8]
        chosen.extend([
            selection("K1_baseline", clip, k1),
            selection("K8_existing", clip, k8),
            selection("MotionSpec_selector", clip, max(candidates, key=lambda r: float(r["motionspec_score"]))),
            selection("No_controller_combined", clip, max(candidates, key=lambda r: float(r["no_controller_score"]))),
            selection("Controller_combined", clip, max(candidates, key=lambda r: float(r["combined_score"]))),
            selection("SONIC_oracle", clip, max(candidates, key=lambda r: (float(r["sonic_track_seconds"]), -float(r["sonic_rmse"])))),
        ])

    summaries: list[dict[str, object]] = []
    by_selector: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in chosen:
        by_selector[str(row["selector"])].append(row)

    for selector, group in sorted(by_selector.items()):
        summaries.append({
            "selector": selector,
            "n": len(group),
            "selected_K1_count": sum(int(r["K"]) == 1 for r in group),
            "selected_K8_count": sum(int(r["K"]) == 8 for r in group),
            "mean_combined_score": mean(group, "combined_score"),
            "mean_no_controller_score": mean(group, "no_controller_score"),
            "mean_semantic_score": mean(group, "semantic_score"),
            "mean_contact_score": mean(group, "contact_score"),
            "mean_dynamics_score": mean(group, "dynamics_score"),
            "mean_controller_score": mean(group, "controller_score"),
            "mean_motionspec_score": mean(group, "motionspec_score"),
            "mean_alignment_score": mean(group, "alignment_score"),
            "mean_contact_artifact_score": mean(group, "contact_artifact_score"),
            "mean_full_risk": mean(group, "full_risk"),
            "mean_sonic_track_seconds": mean(group, "sonic_track_seconds"),
            "sonic_survives_3s_count": sum(float(r["sonic_track_seconds"]) >= 3.0 for r in group),
            "hard_gate_pass_count": sum(r["hard_gate_pass"] == "__YES__" for r in group),
            "controller_gate_pass_count": sum(r["controller_gate_pass"] == "__YES__" for r in group),
        })
    return summaries


def selection(selector: str, clip: str, row: dict[str, object]) -> dict[str, object]:
    return {
        "selector": selector,
        "clip": clip,
        "K": row["K"],
        "category": row["category"],
        "combined_score": row["combined_score"],
        "no_controller_score": row["no_controller_score"],
        "semantic_score": row["semantic_score"],
        "contact_score": row["contact_score"],
        "dynamics_score": row["dynamics_score"],
        "controller_score": row["controller_score"],
        "motionspec_score": row["motionspec_score"],
        "alignment_score": row["alignment_score"],
        "contact_artifact_score": row["contact_artifact_score"],
        "full_risk": row["full_risk"],
        "sonic_track_seconds": row["sonic_track_seconds"],
        "sonic_rmse": row["sonic_rmse"],
        "hard_gate_pass": row["hard_gate_pass"],
        "controller_gate_pass": row["controller_gate_pass"],
    }


def mean(rows: list[dict[str, object]], key: str) -> float:
    values = np.array([float(r[key]) for r in rows], dtype=float)
    return float(np.nanmean(values))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predicates", type=Path, default=DEFAULT_IN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--selector", type=Path, default=DEFAULT_SELECTOR)
    args = parser.parse_args()

    rows = [normalize_clip(row) for row in read_rows(args.predicates)]
    selectors = selector_rows(rows)
    write_csv(args.out, rows)
    write_csv(args.selector, selectors)
    print(f"Wrote {len(rows)} candidate evidence rows to {args.out}")
    print(f"Wrote selector comparison to {args.selector}")


if __name__ == "__main__":
    main()
