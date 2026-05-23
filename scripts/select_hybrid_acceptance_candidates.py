"""Build a hybrid hard-gate + learned-score candidate queue.

This is the next-step selector after the learned rollout audit: do not force a
candidate for unsupported classes, first apply cheap root/contact sanity gates,
then use the learned native-acceptance ensemble for ranking.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

from export_sonic_references import SONIC_FPS, SOURCE_FPS, export_clip


ROOT = Path(__file__).resolve().parents[1]


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


def category(mode: str) -> str:
    if mode == "idle":
        return "idle"
    if "crawling" in mode:
        return "low_posture_crawling"
    return "upright"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate_scores",
        type=Path,
        default=Path("results/prospective_native_selection/20260522_broad13/learned_acceptance_selector/candidate_scores.csv"),
    )
    parser.add_argument("--out_dir", type=Path, required=True)
    parser.add_argument("--selector", default="hybrid_acceptance")
    parser.add_argument("--min_score", type=float, default=0.5)
    parser.add_argument("--max_low_root_pct", type=float, default=0.0)
    parser.add_argument("--allow_crawling", action="store_true")
    parser.add_argument("--export_references", action="store_true")
    args = parser.parse_args()

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = pd.read_csv(args.candidate_scores)
    rows["seed_idx"] = rows["seed_idx"].astype(int)
    rows["candidate_k"] = rows["candidate_k"].astype(int)
    rows["category"] = rows["mode"].map(category)
    rows["hard_gate_pass"] = (
        (rows["ensemble_accept_prob"] >= args.min_score)
        & (rows["upright_reference_gate_pass"] == "__YES__")
        & (rows["low_root_frames_pct"] <= args.max_low_root_pct)
    )
    if not args.allow_crawling:
        rows["hard_gate_pass"] &= rows["category"] != "low_posture_crawling"

    selected = rows[rows["hard_gate_pass"]].sort_values("ensemble_accept_prob", ascending=False).groupby("identity").head(1)
    selected = selected.sort_values(["mode", "seed_idx"]).copy()
    selected["selector"] = args.selector
    selected["selected_motion"] = [
        f"{args.selector}_{row.mode}_seed{int(row.seed_idx)}_cand{int(row.candidate_k)}"
        for row in selected.itertuples()
    ]

    selected.to_csv(out_dir / "prospective_selected.csv", index=False)

    covered = set(selected["identity"])
    rejected_rows = []
    for identity, grp in rows.groupby("identity"):
        if identity in covered:
            continue
        best = grp.sort_values("ensemble_accept_prob", ascending=False).iloc[0]
        reasons = []
        if best["category"] == "low_posture_crawling" and not args.allow_crawling:
            reasons.append("unsupported_crawling")
        if best["ensemble_accept_prob"] < args.min_score:
            reasons.append("learned_score_below_threshold")
        if best["upright_reference_gate_pass"] != "__YES__":
            reasons.append("upright_reference_gate_fail")
        if best["low_root_frames_pct"] > args.max_low_root_pct:
            reasons.append("low_root_frames")
        rejected_rows.append(
            {
                "identity": identity,
                "mode": best["mode"],
                "seed_idx": int(best["seed_idx"]),
                "category": best["category"],
                "best_candidate_k": int(best["candidate_k"]),
                "best_ensemble_accept_prob": float(best["ensemble_accept_prob"]),
                "reject_reasons": ";".join(reasons) if reasons else "no_candidate_after_group_filter",
            }
        )
    write_rows(out_dir / "rejected_identities.csv", rejected_rows)

    export_rows = []
    if args.export_references:
        reference_root = out_dir / "sonic_references"
        reference_root.mkdir(parents=True, exist_ok=True)
        for row in selected.itertuples():
            qpos_path = Path(row.path)
            if not qpos_path.is_absolute():
                qpos_path = ROOT / qpos_path
            export = export_clip(qpos_path, reference_root / row.selected_motion, SOURCE_FPS, SONIC_FPS)
            export_rows.append({**export, "selector": args.selector, "mode": row.mode, "seed_idx": row.seed_idx})
        write_rows(out_dir / "export_manifest.csv", export_rows)

    summary = [
        "# Hybrid Acceptance Selection",
        "",
        f"- candidate scores: `{args.candidate_scores}`",
        f"- min learned score: {args.min_score}",
        f"- max low-root frame percentage: {args.max_low_root_pct}",
        f"- crawling allowed: {args.allow_crawling}",
        f"- selected identities: {len(selected)}",
        f"- rejected identities: {len(rejected_rows)}",
        f"- exported references: {len(export_rows)}",
        "",
        "## Selected By Category",
        "",
        selected.groupby("category").size().to_markdown() if len(selected) else "(none)",
        "",
        "## Rejected By Reason",
        "",
    ]
    if rejected_rows:
        reject_df = pd.DataFrame(rejected_rows)
        reason_counts = reject_df["reject_reasons"].value_counts().rename_axis("reason").reset_index(name="count")
        summary.append(reason_counts.to_markdown(index=False))
    else:
        summary.append("(none)")
    (out_dir / "hybrid_acceptance_selection.md").write_text("\n".join(summary) + "\n")
    print(f"Selected {len(selected)} identities; rejected {len(rejected_rows)}. Wrote {out_dir}")


if __name__ == "__main__":
    main()
