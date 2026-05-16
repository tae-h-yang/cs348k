"""Plot combined selector comparison from candidate evidence table."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "results" / "combined_selector_comparison.csv"
DEFAULT_OUT = ROOT / "results" / "combined_selector_dashboard.png"


def read_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def f(row: dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, ValueError):
        return float("nan")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_IN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = read_rows(args.input)
    order = [
        "K1_baseline",
        "K8_existing",
        "MotionSpec_selector",
        "No_controller_combined",
        "Controller_combined",
        "SONIC_oracle",
    ]
    rows = sorted(rows, key=lambda r: order.index(r["selector"]) if r["selector"] in order else 999)
    labels = [r["selector"].replace("_", "\n") for r in rows]
    x = np.arange(len(rows))

    fig, axes = plt.subplots(2, 2, figsize=(13, 7.5), constrained_layout=True)
    plots = [
        ("mean_combined_score", "Combined score", (0.0, 1.0)),
        ("mean_semantic_score", "Semantic score", (0.0, 1.0)),
        ("mean_full_risk", "Inverse-dynamics risk", None),
        ("mean_sonic_track_seconds", "Approx. SONIC survival (s)", None),
    ]
    colors = ["#4C78A8", "#F58518", "#54A24B", "#72B7B2", "#B279A2", "#E45756"]
    for ax, (key, title, ylim) in zip(axes.flat, plots):
        vals = [f(r, key) for r in rows]
        ax.bar(x, vals, color=colors)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.grid(axis="y", alpha=0.25)
        if ylim:
            ax.set_ylim(*ylim)
        for i, val in enumerate(vals):
            ax.text(i, val, f"{val:.2f}", ha="center", va="bottom", fontsize=8)

    fig.suptitle("Combined selector comparison on current K=1/K=8 candidates", fontsize=13)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=180)
    plt.close(fig)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
