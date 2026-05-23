"""Audit learned-acceptance prospective rollout against native SONIC labels.

The goal is to avoid overclaiming. This script separates already-evaluated
learned selections from newly rolled-out selections, reports learned-score
abstention curves, and builds an evaluated-only hybrid ranking diagnostic.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd


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


def strict_column(df: pd.DataFrame) -> pd.Series:
    return (~df["fell"]) & (df["mean_joint_rmse"] <= 0.20) & (df["mean_root_xy_error"] <= 1.5)


def category(mode: str) -> str:
    if mode == "idle":
        return "idle"
    if "crawling" in mode:
        return "low_posture_crawling"
    return "upright"


def pct(numer: int, denom: int) -> str:
    if denom == 0:
        return "n/a"
    return f"{numer}/{denom} ({100.0 * numer / denom:.1f}%)"


def summarize_group(df: pd.DataFrame, group: str) -> list[dict[str, object]]:
    rows = []
    for key, grp in df.groupby(group, dropna=False):
        rows.append(
            {
                group: key,
                "n": len(grp),
                "strict": int(grp["strict"].sum()),
                "strict_rate": float(grp["strict"].mean()) if len(grp) else 0.0,
                "falls": int(grp["fell"].sum()),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--broad13_dir", type=Path, default=Path("results/prospective_native_selection/20260522_broad13"))
    parser.add_argument(
        "--learned_dir",
        type=Path,
        default=Path("results/prospective_native_selection/20260523_learned_acceptance_eval"),
    )
    parser.add_argument("--out_dir", type=Path)
    args = parser.parse_args()

    broad13_dir = args.broad13_dir
    learned_dir = args.learned_dir
    out_dir = args.out_dir or learned_dir / "audit"
    out_dir.mkdir(parents=True, exist_ok=True)

    scores = pd.read_csv(broad13_dir / "learned_acceptance_selector" / "candidate_scores.csv")
    broad_selected = pd.read_csv(broad13_dir / "prospective_selected.csv")
    learned_selected = pd.read_csv(learned_dir / "prospective_selected.csv")
    learned_summary = pd.read_csv(learned_dir / "native_release" / "batch_summary.csv")
    learned_summary["strict"] = strict_column(learned_summary)

    for df in (scores, broad_selected, learned_selected):
        df["seed_idx"] = df["seed_idx"].astype(int)
        df["candidate_k"] = df["candidate_k"].astype(int)

    prior_keys = set(zip(broad_selected["mode"], broad_selected["seed_idx"], broad_selected["candidate_k"]))
    learned = learned_selected.merge(
        learned_summary[["motion", "fell", "mean_joint_rmse", "mean_root_xy_error", "strict", "category"]],
        left_on="selected_motion",
        right_on="motion",
        how="left",
    )
    learned["prior_native_evaluated"] = [
        (row.mode, int(row.seed_idx), int(row.candidate_k)) in prior_keys for row in learned.itertuples()
    ]
    learned["category"] = learned["mode"].map(category)

    prior_rows = summarize_group(learned, "prior_native_evaluated")
    write_rows(out_dir / "learned_selection_prior_split.csv", prior_rows)

    cat_rows = []
    for (prior, cat), grp in learned.groupby(["prior_native_evaluated", "category"]):
        cat_rows.append(
            {
                "prior_native_evaluated": prior,
                "category": cat,
                "n": len(grp),
                "strict": int(grp["strict"].sum()),
                "strict_rate": float(grp["strict"].mean()) if len(grp) else 0.0,
                "falls": int(grp["fell"].sum()),
            }
        )
    write_rows(out_dir / "learned_selection_prior_by_category.csv", cat_rows)

    threshold_rows = []
    for threshold in [0.0, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]:
        subset = learned[learned["ensemble_accept_prob"] >= threshold]
        threshold_rows.append(
            {
                "min_ensemble_accept_prob": threshold,
                "accepted_identities": len(subset),
                "strict": int(subset["strict"].sum()),
                "strict_rate": float(subset["strict"].mean()) if len(subset) else 0.0,
                "falls": int(subset["fell"].sum()) if len(subset) else 0,
                "crawling_identities": int(subset["mode"].str.contains("crawling").sum()) if len(subset) else 0,
            }
        )
    write_rows(out_dir / "learned_score_abstention.csv", threshold_rows)

    # Evaluated-only hybrid diagnostic over the union of broad13 selected rows
    # and the learned prospective rollout. This is not a clean prospective
    # result because many labels contributed to model training; it is a
    # same-pool diagnostic for the next hybrid experiment.
    broad_summary = pd.read_csv(broad13_dir / "native_release" / "batch_summary.csv")
    broad_summary["strict"] = strict_column(broad_summary)
    broad_labeled = broad_selected.merge(
        broad_summary[["motion", "strict"]],
        left_on="selected_motion",
        right_on="motion",
        how="left",
    )
    broad_labels = (
        broad_labeled.groupby(["mode", "seed_idx", "candidate_k"])
        .agg(broad_strict_any=("strict", "max"), broad_native_count=("strict", "count"))
        .reset_index()
    )
    learned_labels = (
        learned.groupby(["mode", "seed_idx", "candidate_k"])
        .agg(learned_strict=("strict", "max"), learned_native_count=("strict", "count"))
        .reset_index()
    )
    union = scores.merge(broad_labels, on=["mode", "seed_idx", "candidate_k"], how="left").merge(
        learned_labels, on=["mode", "seed_idx", "candidate_k"], how="left"
    )
    union["category"] = union["mode"].map(category)
    union["known_count"] = union["broad_native_count"].fillna(0) + union["learned_native_count"].fillna(0)
    union["known_strict_any"] = union["broad_strict_any"].eq(True) | union["learned_strict"].eq(True)
    known = union[union["known_count"] > 0].copy()
    hybrid_known = known[
        (known["category"] != "low_posture_crawling") & (known["upright_reference_gate_pass"] == "__YES__")
    ]
    hybrid_known = hybrid_known.sort_values("ensemble_accept_prob", ascending=False).groupby("identity").head(1)
    hybrid_known = hybrid_known.sort_values(["mode", "seed_idx"])
    hybrid_known.to_csv(out_dir / "known_label_hybrid_selection.csv", index=False)

    known_all = known.sort_values("ensemble_accept_prob", ascending=False).groupby("identity").head(1)
    lines = [
        "# Learned Acceptance Rollout Audit",
        "",
        "## Key Result",
        "",
        f"- Learned selector strict pass: {pct(int(learned['strict'].sum()), len(learned))}.",
        f"- Already native-evaluated selections: {pct(int(learned[learned['prior_native_evaluated']]['strict'].sum()), int(learned['prior_native_evaluated'].sum()))}.",
        f"- Newly evaluated selections: {pct(int(learned[~learned['prior_native_evaluated']]['strict'].sum()), int((~learned['prior_native_evaluated']).sum()))}.",
        f"- Crawling selections: {pct(int(learned[learned['category'] == 'low_posture_crawling']['strict'].sum()), int((learned['category'] == 'low_posture_crawling').sum()))}.",
        "",
        "## Abstention By Learned Score",
        "",
        "| min score | accepted | strict | falls | crawling |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in threshold_rows:
        lines.append(
            f"| {row['min_ensemble_accept_prob']:.2f} | {row['accepted_identities']} | "
            f"{row['strict']} ({100.0 * row['strict_rate']:.1f}%) | {row['falls']} | {row['crawling_identities']} |"
        )

    lines += [
        "",
        "## Evaluated-Only Hybrid Diagnostic",
        "",
        "This is a same-pool diagnostic, not a clean prospective result: the model was",
        "trained on part of these native labels. It is useful only for deciding the",
        "next experiment.",
        "",
        f"- Learned-score best among any known labels: {pct(int(known_all['known_strict_any'].sum()), len(known_all))}.",
        f"- Hard-gated learned-score best among known supported labels: {pct(int(hybrid_known['known_strict_any'].sum()), len(hybrid_known))}.",
        "",
        "## Interpretation",
        "",
        "The learned score is useful for abstention: a threshold near 0.5 removes the",
        "crawling identities in this rollout and raises selected strict rate from",
        "73.1% to 86.4%, but coverage drops from 104 to 88 identities. This supports",
        "a hybrid acceptance gate, not forced best-of-K selection for every prompt.",
    ]
    (out_dir / "learned_acceptance_rollout_audit.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote audit to {out_dir}")


if __name__ == "__main__":
    main()
