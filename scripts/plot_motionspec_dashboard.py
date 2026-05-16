"""Plot MotionSpec selector and failure summaries."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SELECTOR = ROOT / "results" / "motionspec_selector_comparison.csv"
DEFAULT_PREDICATES = ROOT / "results" / "motionspec_predicates.csv"
DEFAULT_DASHBOARD = ROOT / "results" / "motionspec_selector_dashboard.png"
DEFAULT_FAILURES = ROOT / "results" / "motionspec_failure_counts.csv"
DEFAULT_FAILURE_PLOT = ROOT / "results" / "motionspec_failure_counts.png"


def read_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def f(row: dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, ValueError):
        return float("nan")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_selector(selector_path: Path, out_path: Path) -> None:
    rows = read_rows(selector_path)
    labels = [r["selector"].replace("_", "\n") for r in rows]
    metrics = [
        ("mean_motionspec_score", "MotionSpec"),
        ("mean_alignment_score", "Prompt proxy"),
        ("mean_contact_artifact_score", "Contact artifact"),
        ("mean_sonic_track_seconds", "SONIC survival (s)"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B279A2"]
    for ax, (key, title) in zip(axes.flat, metrics):
        values = [f(r, key) for r in rows]
        ax.bar(np.arange(len(rows)), values, color=colors)
        ax.set_title(title)
        ax.set_xticks(np.arange(len(rows)))
        ax.set_xticklabels(labels, rotation=0, fontsize=8)
        ax.grid(axis="y", alpha=0.25)
        if "score" in key:
            ax.set_ylim(0.0, 1.0)
        for i, val in enumerate(values):
            ax.text(i, val, f"{val:.2f}", ha="center", va="bottom", fontsize=8)

    fig.suptitle("MotionSpec selector comparison on existing 105 paired identities", fontsize=13)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def failure_counts(predicates_path: Path) -> list[dict[str, object]]:
    counter: Counter[str] = Counter()
    for row in read_rows(predicates_path):
        for item in row.get("failed_predicates", "").split(";"):
            if item:
                counter[item] += 1
    return [{"predicate": pred, "failed_rows": count} for pred, count in counter.most_common()]


def plot_failures(rows: list[dict[str, object]], out_path: Path, top_n: int = 15) -> None:
    rows = rows[:top_n]
    labels = [str(r["predicate"]) for r in rows]
    values = [int(r["failed_rows"]) for r in rows]

    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    y = np.arange(len(rows))
    ax.barh(y, values, color="#E45756")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Failed rows out of 210")
    ax.set_title("Most common MotionSpec predicate failures")
    ax.grid(axis="x", alpha=0.25)
    for i, val in enumerate(values):
        ax.text(val + 1, i, str(val), va="center", fontsize=8)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selector", type=Path, default=DEFAULT_SELECTOR)
    parser.add_argument("--predicates", type=Path, default=DEFAULT_PREDICATES)
    parser.add_argument("--dashboard", type=Path, default=DEFAULT_DASHBOARD)
    parser.add_argument("--failures", type=Path, default=DEFAULT_FAILURES)
    parser.add_argument("--failure_plot", type=Path, default=DEFAULT_FAILURE_PLOT)
    args = parser.parse_args()

    plot_selector(args.selector, args.dashboard)
    failures = failure_counts(args.predicates)
    write_csv(args.failures, failures)
    plot_failures(failures, args.failure_plot)
    print(f"Wrote {args.dashboard}")
    print(f"Wrote {args.failures}")
    print(f"Wrote {args.failure_plot}")


if __name__ == "__main__":
    main()
