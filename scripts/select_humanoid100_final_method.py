"""Build the final verifier/repair/SONIC-selection table for Humanoid100."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METRICS = ROOT / "results" / "humanoid100_final_eval" / "final_metrics.csv"
DEFAULT_SONIC = ROOT / "results" / "humanoid100_final_eval" / "sonic_all_tracking.csv"
DEFAULT_OUT_DIR = ROOT / "results" / "humanoid100_final_eval" / "final_selector"

REFERENCE_METHOD = {
    "K1": "K1_first",
    "K8": "K8_best_of_8",
    "K9": "repaired_retime",
}
METHOD_REFERENCE_K = {value: key for key, value in REFERENCE_METHOD.items()}
BASELINES = ("K1_first", "K8_best_of_8", "repaired_retime", "sonic_verified_best")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
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
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def as_float(row: dict[str, object], key: str, default: float = float("nan")) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def ref_to_method(reference: str) -> str:
    suffix = reference.rsplit("_", 1)[-1]
    return REFERENCE_METHOD[suffix]


def prompt_key_from_reference(reference: str) -> tuple[str, str]:
    # hrb_006_march_high_knees_K9 -> (hrb_006, march_high_knees)
    stem = reference.rsplit("_K", 1)[0]
    parts = stem.split("_", 2)
    return "_".join(parts[:2]), parts[2]


def build_joined(metrics_csv: Path, sonic_csv: Path) -> list[dict[str, object]]:
    metrics = {
        (row["prompt_id"], row["method"]): row
        for row in read_rows(metrics_csv)
    }
    joined: list[dict[str, object]] = []
    for sonic in read_rows(sonic_csv):
        prompt_id, subcategory = prompt_key_from_reference(sonic["reference"])
        method = ref_to_method(sonic["reference"])
        metric = metrics[(prompt_id, method)]
        row: dict[str, object] = {
            **metric,
            "reference": sonic["reference"],
            "sonic_K": sonic["K"],
            "sonic_fell": sonic["fell"],
            "sonic_track_seconds": sonic["track_seconds"],
            "sonic_mean_tracking_rmse": sonic["mean_tracking_rmse"],
            "sonic_mean_root_error": sonic["mean_root_error"],
            "sonic_final_root_z": sonic["final_root_z"],
        }
        joined.append(row)
    return joined


def sonic_key(row: dict[str, object]) -> tuple[float, float, float, float]:
    return (
        as_float(row, "sonic_track_seconds"),
        -as_float(row, "sonic_mean_tracking_rmse"),
        1.0 if row.get("physical_pass") == "__YES__" else 0.0,
        -as_float(row, "risk_score"),
    )


def risk_key(row: dict[str, object]) -> tuple[float, float, float]:
    return (
        1.0 if row.get("physical_pass") == "__YES__" else 0.0,
        -as_float(row, "risk_score"),
        as_float(row, "sonic_track_seconds"),
    )


def select_rows(joined: list[dict[str, object]]) -> list[dict[str, object]]:
    by_prompt: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in joined:
        by_prompt[str(row["prompt_id"])].append(row)

    selected: list[dict[str, object]] = []
    for prompt_id, rows in sorted(by_prompt.items()):
        by_method = {str(row["method"]): row for row in rows}
        k1 = by_method["K1_first"]
        k8 = by_method["K8_best_of_8"]
        repaired = by_method["repaired_retime"]
        sonic_best = max(rows, key=sonic_key)
        risk_best = max(rows, key=risk_key)
        for selector, row in [
            ("K1_first", k1),
            ("K8_best_of_8", k8),
            ("repaired_retime", repaired),
            ("risk_verifier_best", risk_best),
            ("sonic_verified_best", sonic_best),
        ]:
            selected.append({
                "selector": selector,
                "selected_method": row["method"],
                "selected_reference": row["reference"],
                "prompt_id": row["prompt_id"],
                "category": row["category"],
                "subcategory": row["subcategory"],
                "prompt_text": row["prompt_text"],
                "semantic_validity": row["semantic_validity"],
                "semantic_supported": row["semantic_supported"],
                "physical_pass": row["physical_pass"],
                "presentation_pass": row["presentation_pass"],
                "risk_score": row["risk_score"],
                "contact_artifact_score": row["contact_artifact_score"],
                "p95_torque_limit_ratio": row["p95_torque_limit_ratio"],
                "sonic_track_seconds": row["sonic_track_seconds"],
                "sonic_mean_tracking_rmse": row["sonic_mean_tracking_rmse"],
                "sonic_fell": row["sonic_fell"],
                "k1_track_seconds": k1["sonic_track_seconds"],
                "k8_track_seconds": k8["sonic_track_seconds"],
                "repaired_track_seconds": repaired["sonic_track_seconds"],
                "selected_minus_k1_track_seconds": as_float(row, "sonic_track_seconds") - as_float(k1, "sonic_track_seconds"),
                "selected_minus_k8_track_seconds": as_float(row, "sonic_track_seconds") - as_float(k8, "sonic_track_seconds"),
                "selected_minus_repaired_track_seconds": as_float(row, "sonic_track_seconds") - as_float(repaired, "sonic_track_seconds"),
            })
    return selected


def summarize(selected: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in selected:
        groups[f"selector={row['selector']}"].append(row)
        groups[f"selector={row['selector']}|semantic={row['semantic_validity']}"].append(row)
        groups[f"selector={row['selector']}|category={row['category']}"].append(row)
    out = []
    for group, rows in sorted(groups.items()):
        out.append({
            "group": group,
            "n": len(rows),
            "mean_risk": float(np.mean([as_float(r, "risk_score") for r in rows])),
            "median_risk": float(np.median([as_float(r, "risk_score") for r in rows])),
            "physical_pass_count": sum(r["physical_pass"] == "__YES__" for r in rows),
            "presentation_pass_count": sum(r["presentation_pass"] == "__YES__" for r in rows),
            "semantic_supported_count": sum(r["semantic_supported"] == "__YES__" for r in rows),
            "sonic_no_fall_count": sum(r["sonic_fell"] == "False" for r in rows),
            "mean_sonic_track_seconds": float(np.mean([as_float(r, "sonic_track_seconds") for r in rows])),
            "mean_sonic_rmse": float(np.mean([as_float(r, "sonic_mean_tracking_rmse") for r in rows])),
            "mean_selected_minus_k1_track_seconds": float(np.mean([as_float(r, "selected_minus_k1_track_seconds") for r in rows])),
            "mean_selected_minus_k8_track_seconds": float(np.mean([as_float(r, "selected_minus_k8_track_seconds") for r in rows])),
        })
    return out


def write_representatives(selected: list[dict[str, object]], out_dir: Path) -> None:
    sonic = [r for r in selected if r["selector"] == "sonic_verified_best"]
    supported = [r for r in sonic if r["semantic_supported"] == "__YES__"]
    forced = [r for r in sonic if r["semantic_supported"] != "__YES__"]
    rescues = sorted(sonic, key=lambda r: as_float(r, "selected_minus_k1_track_seconds"), reverse=True)[:10]
    failures = sorted(sonic, key=lambda r: (as_float(r, "sonic_track_seconds"), -as_float(r, "risk_score")))[:10]
    supported_wins = sorted(supported, key=lambda r: as_float(r, "selected_minus_k1_track_seconds"), reverse=True)[:8]
    forced_wins = sorted(forced, key=lambda r: as_float(r, "selected_minus_k1_track_seconds"), reverse=True)[:8]

    rows = []
    seen = set()
    for bucket, items in [
        ("largest_tracking_rescues", rescues),
        ("remaining_failures", failures),
        ("supported_prompt_wins", supported_wins),
        ("forced_proxy_wins", forced_wins),
    ]:
        for rank, row in enumerate(items, start=1):
            key = (bucket, row["selected_reference"])
            if key in seen:
                continue
            seen.add(key)
            rows.append({"bucket": bucket, "rank": rank, **row})
    write_csv(out_dir / "representative_cases.csv", rows)


def plot_summary(summary: list[dict[str, object]], out_dir: Path) -> None:
    rows = [r for r in summary if r["group"].startswith("selector=") and "|" not in r["group"]]
    order = ["K1_first", "K8_best_of_8", "repaired_retime", "risk_verifier_best", "sonic_verified_best"]
    by = {r["group"].split("=", 1)[1]: r for r in rows}
    labels = order
    colors = ["#707070", "#3267a8", "#2d8f67", "#8a62ad", "#c46b37"]
    seconds = [as_float(by[m], "mean_sonic_track_seconds") for m in labels]
    rmse = [as_float(by[m], "mean_sonic_rmse") for m in labels]
    physical = [int(by[m]["physical_pass_count"]) for m in labels]
    nofall = [int(by[m]["sonic_no_fall_count"]) for m in labels]

    fig, axes = plt.subplots(1, 4, figsize=(15.5, 4.1))
    panels = [
        (seconds, "Mean SONIC seconds", None),
        (rmse, "Mean SONIC RMSE", None),
        (physical, "Physical pass / 100", (0, 100)),
        (nofall, "No fall / 100", (0, 100)),
    ]
    for ax, (vals, ylabel, ylim) in zip(axes, panels):
        ax.bar(labels, vals, color=colors)
        ax.set_ylabel(ylabel)
        if ylim:
            ax.set_ylim(*ylim)
        ax.tick_params(axis="x", rotation=25)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Final Humanoid100 selector comparison", y=1.03)
    fig.tight_layout()
    fig.savefig(out_dir / "final_selector_summary.png", dpi=190, bbox_inches="tight")
    plt.close(fig)


def write_readme(out_dir: Path, summary: list[dict[str, object]]) -> None:
    rows = {r["group"].split("=", 1)[1]: r for r in summary if r["group"].startswith("selector=") and "|" not in r["group"]}
    lines = [
        "# Final Humanoid100 Selector",
        "",
        "This is the current end-to-end method table. It compares fixed baselines",
        "against two inference-time verifier selectors:",
        "",
        "- `risk_verifier_best`: choose among K=1, K=8, repaired by physical pass and risk.",
        "- `sonic_verified_best`: choose among K=1, K=8, repaired by approximate SONIC tracking.",
        "",
        "| Selector | Mean risk | Physical pass | No fall | Mean SONIC seconds | Mean RMSE |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for selector in ["K1_first", "K8_best_of_8", "repaired_retime", "risk_verifier_best", "sonic_verified_best"]:
        row = rows[selector]
        lines.append(
            f"| {selector} | {as_float(row, 'mean_risk'):.3f} | "
            f"{int(row['physical_pass_count'])}/100 | {int(row['sonic_no_fall_count'])}/100 | "
            f"{as_float(row, 'mean_sonic_track_seconds'):.3f} | {as_float(row, 'mean_sonic_rmse'):.3f} |"
        )
    lines.extend([
        "",
        "## Claim Boundary",
        "",
        "The SONIC-verified selector is an inference-time verification strategy,",
        "not a trained generator. It improves controller-tracking metrics on the",
        "generated reference set, but many references still fall and 78/100 rows",
        "remain forced semantic proxies.",
        "",
        "## Files",
        "",
        "- `joined_method_metrics.csv`",
        "- `selected_methods.csv`",
        "- `selector_summary.csv`",
        "- `representative_cases.csv`",
        "- `final_selector_summary.png`",
        "",
    ])
    (out_dir / "README.md").write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics_csv", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--sonic_csv", type=Path, default=DEFAULT_SONIC)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    joined = build_joined(args.metrics_csv, args.sonic_csv)
    selected = select_rows(joined)
    summary = summarize(selected)
    write_csv(args.out_dir / "joined_method_metrics.csv", joined)
    write_csv(args.out_dir / "selected_methods.csv", selected)
    write_csv(args.out_dir / "selector_summary.csv", summary)
    write_representatives(selected, args.out_dir)
    plot_summary(summary, args.out_dir)
    write_readme(args.out_dir, summary)
    print(f"Wrote {len(joined)} joined rows and {len(selected)} selected rows to {args.out_dir}")
    for row in summary:
        if row["group"].startswith("selector=") and "|" not in row["group"]:
            print(row)


if __name__ == "__main__":
    main()
