"""Select clips for human visual audit from the candidate evidence table."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "results" / "candidate_evidence_table.csv"
DEFAULT_OUT = ROOT / "results" / "visual_audit_manifest.csv"
DATA_DIR = ROOT / "data" / "guided_ablation_extended"


def read_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def f(row: dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, ValueError):
        return float("nan")


def row_id(row: dict[str, str]) -> str:
    return f"{row['clip']}_K{row['K']}"


def add_case(out: list[dict[str, object]], seen: set[str], row: dict[str, str], reason: str) -> None:
    rid = row_id(row)
    if rid in seen:
        return
    seen.add(rid)
    out.append({
        "audit_id": f"audit_{len(out) + 1:02d}",
        "reason": reason,
        "clip": row["clip"],
        "K": row["K"],
        "category": row["category"],
        "prompt_text": row["prompt_text"],
        "qpos_path": str(DATA_DIR / f"{row['clip']}_K{row['K']}.npy"),
        "combined_score": row["combined_score"],
        "semantic_score": row["semantic_score"],
        "contact_score": row["contact_score"],
        "dynamics_score": row["dynamics_score"],
        "controller_score": row["controller_score"],
        "full_risk": row["full_risk"],
        "sonic_track_seconds": row["sonic_track_seconds"],
        "failed_predicates": row["failed_predicates"],
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--n", type=int, default=12)
    args = parser.parse_args()

    rows = read_rows(args.candidates)
    non_static = [r for r in rows if r["category"] != "static"]
    out: list[dict[str, object]] = []
    seen: set[str] = set()

    for row in sorted(non_static, key=lambda r: f(r, "combined_score"), reverse=True)[:3]:
        add_case(out, seen, row, "best_nonstatic_combined")
    for row in sorted(non_static, key=lambda r: f(r, "combined_score"))[:3]:
        add_case(out, seen, row, "worst_nonstatic_combined")
    for row in sorted(non_static, key=lambda r: f(r, "full_risk"), reverse=True)[:2]:
        add_case(out, seen, row, "highest_inverse_dynamics_risk")
    for row in sorted(non_static, key=lambda r: f(r, "sonic_track_seconds"), reverse=True)[:2]:
        add_case(out, seen, row, "best_controller_survival_nonstatic")
    for row in sorted(non_static, key=lambda r: f(r, "semantic_score"), reverse=True)[:2]:
        add_case(out, seen, row, "best_semantic_nonstatic")

    if len(out) < args.n:
        for row in sorted(non_static, key=lambda r: f(r, "contact_score")):
            add_case(out, seen, row, "low_contact_score_fill")
            if len(out) >= args.n:
                break

    out = out[: args.n]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as fobj:
        writer = csv.DictWriter(fobj, fieldnames=list(out[0].keys()))
        writer.writeheader()
        writer.writerows(out)
    print(f"Wrote {len(out)} audit clips to {args.out}")


if __name__ == "__main__":
    main()
