"""Analyze prospective selector winners after native SONIC rollout."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


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


def f(row: dict[str, object], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def strict_pass(row: dict[str, object]) -> bool:
    return (
        row.get("fell") == "False"
        and f(row, "mean_joint_rmse", 999.0) <= 0.20
        and f(row, "mean_root_xy_error", 999.0) <= 1.5
    )


def join_rows(prospective_dir: Path, batch_dir: Path) -> list[dict[str, object]]:
    selected = {r["selected_motion"]: r for r in read_rows(prospective_dir / "prospective_selected.csv")}
    native = {r["motion"]: r for r in read_rows(batch_dir / "batch_summary.csv") if r.get("status") == "completed"}
    rows = []
    for motion, sel in selected.items():
        nat = native.get(motion)
        if not nat:
            rows.append({**sel, "native_status": "missing"})
            continue
        rows.append(
            {
                **sel,
                **{f"native_{k}": v for k, v in nat.items()},
                "native_status": "completed",
                "native_pass": "__YES__" if nat.get("fell") == "False" else "__NO__",
                "native_strict_pass": "__YES__" if strict_pass(nat) else "__NO__",
            }
        )
    return rows


def summarize(rows: list[dict[str, object]], candidate_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    identities = {(r["clip"], r["seed_idx"]) for r in candidate_rows}
    total_identities = len(identities)
    by_selector: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row.get("native_status") == "completed":
            by_selector[str(row["selector"])].append(row)

    out = []
    for selector, group in sorted(by_selector.items()):
        n = len(group)
        survive = [r for r in group if r["native_pass"] == "__YES__"]
        strict = [r for r in group if r["native_strict_pass"] == "__YES__"]
        out.append(
            {
                "selector": selector,
                "selected_count": n,
                "total_identities": total_identities,
                "coverage_rate": n / max(total_identities, 1),
                "native_survive_count": len(survive),
                "native_survive_rate_per_selected": len(survive) / max(n, 1),
                "native_survive_rate_per_identity": len(survive) / max(total_identities, 1),
                "native_strict_count": len(strict),
                "native_strict_rate_per_selected": len(strict) / max(n, 1),
                "native_strict_rate_per_identity": len(strict) / max(total_identities, 1),
                "mean_native_joint_rmse": float(np.mean([f(r, "native_mean_joint_rmse") for r in group])),
                "mean_native_root_xy_error": float(np.mean([f(r, "native_mean_root_xy_error") for r in group])),
                "mean_full_risk": float(np.mean([f(r, "full_risk") for r in group])),
                "mean_contact_artifact_score": float(np.mean([f(r, "contact_artifact_score") for r in group])),
                "mean_precontroller_score": float(np.mean([f(r, "precontroller_score") for r in group])),
            }
        )
    return out


def per_mode_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row.get("native_status") == "completed":
            grouped[(str(row["selector"]), str(row["mode"]))].append(row)
    out = []
    for (selector, mode), group in sorted(grouped.items()):
        out.append(
            {
                "selector": selector,
                "mode": mode,
                "n": len(group),
                "survive": sum(r["native_pass"] == "__YES__" for r in group),
                "strict": sum(r["native_strict_pass"] == "__YES__" for r in group),
                "mean_rmse": float(np.mean([f(r, "native_mean_joint_rmse") for r in group])),
            }
        )
    return out


def identity_key(row: dict[str, object]) -> tuple[str, str]:
    return str(row["mode"]), str(row["seed_idx"])


def baseline_comparison(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_identity: dict[tuple[str, str], dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        if row.get("native_status") == "completed":
            by_identity[identity_key(row)][str(row["selector"])] = row

    selectors = sorted(
        {
            selector
            for grouped in by_identity.values()
            for selector in grouped
            if selector != "baseline_k0"
        }
    )
    out = []
    for selector in selectors:
        paired = [
            (grouped["baseline_k0"], grouped[selector])
            for grouped in by_identity.values()
            if "baseline_k0" in grouped and selector in grouped
        ]
        baseline_strict = [base for base, _ in paired if base["native_strict_pass"] == "__YES__"]
        selector_strict = [sel for _, sel in paired if sel["native_strict_pass"] == "__YES__"]
        rescued = [
            sel
            for base, sel in paired
            if base["native_strict_pass"] != "__YES__" and sel["native_strict_pass"] == "__YES__"
        ]
        regressed = [
            sel
            for base, sel in paired
            if base["native_strict_pass"] == "__YES__" and sel["native_strict_pass"] != "__YES__"
        ]
        changed_candidate = [
            sel
            for base, sel in paired
            if int(f(base, "candidate_k", -1)) != int(f(sel, "candidate_k", -1))
        ]
        out.append(
            {
                "selector": selector,
                "paired_identities": len(paired),
                "changed_candidate_count": len(changed_candidate),
                "baseline_strict_count": len(baseline_strict),
                "selector_strict_count": len(selector_strict),
                "strict_delta": len(selector_strict) - len(baseline_strict),
                "rescued_count": len(rescued),
                "regressed_count": len(regressed),
                "mean_rmse_delta_vs_baseline": float(
                    np.mean(
                        [
                            f(sel, "native_mean_joint_rmse") - f(base, "native_mean_joint_rmse")
                            for base, sel in paired
                        ]
                    )
                )
                if paired
                else 0.0,
                "mean_risk_delta_vs_baseline": float(
                    np.mean([f(sel, "full_risk") - f(base, "full_risk") for base, sel in paired])
                )
                if paired
                else 0.0,
            }
        )
    return out


def auc_score(values: list[float], labels: list[int]) -> float:
    positives = [v for v, y in zip(values, labels) if y == 1]
    negatives = [v for v, y in zip(values, labels) if y == 0]
    if not positives or not negatives:
        return 0.5
    wins = 0.0
    for pos in positives:
        for neg in negatives:
            if pos > neg:
                wins += 1.0
            elif pos == neg:
                wins += 0.5
    return wins / (len(positives) * len(negatives))


def feature_calibration(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    completed = [row for row in rows if row.get("native_status") == "completed"]
    labels = [1 if row["native_strict_pass"] == "__YES__" else 0 for row in completed]
    features = [
        ("precontroller_score", "higher_is_better", 1.0),
        ("full_risk", "lower_is_better", -1.0),
        ("contact_artifact_score", "lower_is_better", -1.0),
        ("p95_torque_limit_ratio", "lower_is_better", -1.0),
        ("p95_root_force_N", "lower_is_better", -1.0),
        ("nonfoot_floor_contact_frames_pct", "lower_is_better", -1.0),
    ]
    out = []
    for key, direction, sign in features:
        values = [sign * f(row, key) for row in completed]
        out.append(
            {
                "feature": key,
                "direction": direction,
                "completed_rows": len(completed),
                "strict_positive_rows": sum(labels),
                "auc_for_native_strict_pass": auc_score(values, labels),
                "mean_value_strict_pass": float(np.mean([f(row, key) for row, y in zip(completed, labels) if y == 1]))
                if any(labels)
                else "",
                "mean_value_strict_fail": float(np.mean([f(row, key) for row, y in zip(completed, labels) if y == 0]))
                if any(y == 0 for y in labels)
                else "",
            }
        )
    return out


def identity_outcomes(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_identity: dict[tuple[str, str], dict[str, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        if row.get("native_status") == "completed":
            by_identity[identity_key(row)][str(row["selector"])] = row

    out = []
    for (mode, seed_idx), grouped in sorted(by_identity.items()):
        baseline = grouped.get("baseline_k0")
        if not baseline:
            continue
        for selector, row in sorted(grouped.items()):
            if selector == "baseline_k0":
                continue
            base_strict = baseline["native_strict_pass"] == "__YES__"
            sel_strict = row["native_strict_pass"] == "__YES__"
            if sel_strict and not base_strict:
                outcome = "rescued"
            elif base_strict and not sel_strict:
                outcome = "regressed"
            elif sel_strict and base_strict:
                outcome = "both_strict"
            else:
                outcome = "both_failed"
            out.append(
                {
                    "mode": mode,
                    "seed_idx": seed_idx,
                    "selector": selector,
                    "outcome_vs_baseline": outcome,
                    "baseline_motion": baseline["selected_motion"],
                    "selector_motion": row["selected_motion"],
                    "baseline_candidate_k": baseline["candidate_k"],
                    "selector_candidate_k": row["candidate_k"],
                    "baseline_strict": baseline["native_strict_pass"],
                    "selector_strict": row["native_strict_pass"],
                    "baseline_fell": baseline["native_fell"],
                    "selector_fell": row["native_fell"],
                    "baseline_rmse": baseline["native_mean_joint_rmse"],
                    "selector_rmse": row["native_mean_joint_rmse"],
                    "baseline_video": baseline["native_video"],
                    "selector_video": row["native_video"],
                }
            )
    return out


def native_selector_oracle(rows: list[dict[str, object]], candidate_rows: list[dict[str, str]]) -> dict[str, object]:
    total_identities = len({(r["clip"], r["seed_idx"]) for r in candidate_rows})
    by_identity: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row.get("native_status") == "completed":
            by_identity[identity_key(row)].append(row)
    strict_any = [group for group in by_identity.values() if any(r["native_strict_pass"] == "__YES__" for r in group)]
    survive_any = [group for group in by_identity.values() if any(r["native_pass"] == "__YES__" for r in group)]
    return {
        "selector": "native_oracle_over_tested_selectors",
        "selected_count": len(by_identity),
        "total_identities": total_identities,
        "coverage_rate": len(by_identity) / max(total_identities, 1),
        "native_survive_count": len(survive_any),
        "native_survive_rate_per_selected": len(survive_any) / max(len(by_identity), 1),
        "native_survive_rate_per_identity": len(survive_any) / max(total_identities, 1),
        "native_strict_count": len(strict_any),
        "native_strict_rate_per_selected": len(strict_any) / max(len(by_identity), 1),
        "native_strict_rate_per_identity": len(strict_any) / max(total_identities, 1),
        "mean_native_joint_rmse": "",
        "mean_native_root_xy_error": "",
        "mean_full_risk": "",
        "mean_contact_artifact_score": "",
        "mean_precontroller_score": "",
    }


def plot_summary(path: Path, summary: list[dict[str, object]]) -> None:
    if not summary:
        return
    ordered = sorted(summary, key=lambda r: float(r["native_strict_rate_per_identity"]))
    labels = [str(r["selector"]) for r in ordered]
    selected = [float(r["native_strict_rate_per_selected"]) for r in ordered]
    identity = [float(r["native_strict_rate_per_identity"]) for r in ordered]
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.barh(y - 0.17, selected, height=0.32, label="strict / selected", color="#3f7f5f")
    ax.barh(y + 0.17, identity, height=0.32, label="strict / identity", color="#7aa6c2")
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Native SONIC strict pass rate")
    ax.set_title("Prospective Selector Native Validation")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def write_markdown(
    path: Path,
    summary: list[dict[str, object]],
    mode_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
    calibration_rows: list[dict[str, object]],
) -> None:
    lines = [
        "# Prospective Native Selection Analysis",
        "",
        "Candidates were selected before native SONIC rollout.",
        "",
        "## Selector Summary",
        "",
        "| selector | selected | strict/selected | strict/identity | survive/selected | mean RMSE | mean risk |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(summary, key=lambda r: str(r["selector"])):
        mean_rmse = row["mean_native_joint_rmse"]
        mean_risk = row["mean_full_risk"]
        prefix = (
            f"| {row['selector']} | {int(row['selected_count'])}/{int(row['total_identities'])} | "
            f"{int(row['native_strict_count'])}/{int(row['selected_count'])} "
            f"({float(row['native_strict_rate_per_selected']):.1%}) | "
            f"{int(row['native_strict_count'])}/{int(row['total_identities'])} "
            f"({float(row['native_strict_rate_per_identity']):.1%}) | "
            f"{int(row['native_survive_count'])}/{int(row['selected_count'])} "
            f"({float(row['native_survive_rate_per_selected']):.1%}) | "
        )
        if mean_rmse == "":
            lines.append(prefix + "oracle | oracle |")
        else:
            lines.append(prefix + f"{float(mean_rmse):.3f} | {float(mean_risk):.2f} |")
    lines += [
        "",
        "## Baseline Comparison",
        "",
        "| selector | paired | changed cand | baseline strict | selector strict | delta | rescued | regressed | RMSE delta | risk delta |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in comparison_rows:
        lines.append(
            f"| {row['selector']} | {int(row['paired_identities'])} | "
            f"{int(row['changed_candidate_count'])} | "
            f"{int(row['baseline_strict_count'])} | {int(row['selector_strict_count'])} | "
            f"{int(row['strict_delta']):+d} | {int(row['rescued_count'])} | "
            f"{int(row['regressed_count'])} | "
            f"{float(row['mean_rmse_delta_vs_baseline']):+.3f} | "
            f"{float(row['mean_risk_delta_vs_baseline']):+.2f} |"
        )
    lines += [
        "",
        "## Feature Calibration",
        "",
        "| feature | direction | AUC for native strict pass | strict mean | fail mean |",
        "|---|---|---:|---:|---:|",
    ]
    for row in sorted(calibration_rows, key=lambda r: -float(r["auc_for_native_strict_pass"])):
        pass_mean = row["mean_value_strict_pass"]
        fail_mean = row["mean_value_strict_fail"]
        prefix = (
            f"| {row['feature']} | {row['direction']} | "
            f"{float(row['auc_for_native_strict_pass']):.3f} | "
        )
        if pass_mean == "":
            lines.append(prefix + "n/a | n/a |")
        else:
            lines.append(prefix + f"{float(pass_mean):.3f} | {float(fail_mean):.3f} |")
    lines += [
        "",
        "## Per-Mode Strict Counts",
        "",
        "| selector | mode | strict | n | mean RMSE |",
        "|---|---|---:|---:|---:|",
    ]
    for row in mode_rows:
        lines.append(
            f"| {row['selector']} | {row['mode']} | {int(row['strict'])} | "
            f"{int(row['n'])} | {float(row['mean_rmse']):.3f} |"
        )
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prospective_dir", type=Path, required=True)
    parser.add_argument("--batch_dir", type=Path, required=True)
    args = parser.parse_args()
    prospective_dir = args.prospective_dir.resolve()
    batch_dir = args.batch_dir.resolve()

    joined = join_rows(prospective_dir, batch_dir)
    candidate_rows = read_rows(prospective_dir / "prospective_candidates.csv")
    summary = summarize(joined, candidate_rows)
    summary_with_oracle = summary + [native_selector_oracle(joined, candidate_rows)]
    mode_rows = per_mode_summary(joined)
    comparison_rows = baseline_comparison(joined)
    calibration_rows = feature_calibration(joined)
    identity_rows = identity_outcomes(joined)
    write_rows(prospective_dir / "prospective_native_joined.csv", joined)
    write_rows(prospective_dir / "prospective_native_selector_summary.csv", summary_with_oracle)
    write_rows(prospective_dir / "prospective_native_by_mode.csv", mode_rows)
    write_rows(prospective_dir / "prospective_native_baseline_comparison.csv", comparison_rows)
    write_rows(prospective_dir / "prospective_native_feature_calibration.csv", calibration_rows)
    write_rows(prospective_dir / "prospective_native_identity_outcomes.csv", identity_rows)
    plot_summary(prospective_dir / "prospective_native_selector_summary.png", summary)
    write_markdown(
        prospective_dir / "prospective_native_analysis.md",
        summary_with_oracle,
        mode_rows,
        comparison_rows,
        calibration_rows,
    )
    print(f"Wrote prospective native analysis to {prospective_dir}")


if __name__ == "__main__":
    main()
