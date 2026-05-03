"""
Visualization utilities for kinematic-to-dynamic gap analysis results.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import List, Dict
from physics_eval.metrics import ClipMetrics

RESULTS_DIR = Path(__file__).parents[2] / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def _color_by_type(motion_type: str) -> str:
    palette = {
        "static":      "#4CAF50",
        "locomotion":  "#2196F3",
        "whole_body":  "#FF9800",
        "adversarial": "#F44336",
        "unknown":     "#9E9E9E",
    }
    return palette.get(motion_type, "#9E9E9E")


def plot_tracking_error_by_type(results: List[ClipMetrics], save: bool = True):
    """Bar chart: mean joint tracking RMSE grouped by motion type."""
    by_type: Dict[str, List[float]] = {}
    for r in results:
        by_type.setdefault(r.motion_type, []).append(r.mean_tracking_rmse)

    types = sorted(by_type.keys())
    means = [np.mean(by_type[t]) for t in types]
    stds  = [np.std(by_type[t]) for t in types]
    colors = [_color_by_type(t) for t in types]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(types, means, yerr=stds, color=colors, capsize=5, edgecolor="black", linewidth=0.8)
    ax.set_ylabel("Mean Joint Tracking RMSE (rad)")
    ax.set_title("Kinematic-to-Dynamic Gap: Tracking Error by Motion Type")
    ax.set_xlabel("Motion Type")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    if save:
        path = RESULTS_DIR / "tracking_error_by_type.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved: {path}")
    return fig


def plot_fall_rate_by_type(results: List[ClipMetrics], save: bool = True):
    """Bar chart: fraction of clips that resulted in a fall, by motion type."""
    by_type: Dict[str, List[bool]] = {}
    for r in results:
        by_type.setdefault(r.motion_type, []).append(r.fell)

    types = sorted(by_type.keys())
    rates = [np.mean(by_type[t]) for t in types]
    colors = [_color_by_type(t) for t in types]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(types, rates, color=colors, edgecolor="black", linewidth=0.8)
    ax.set_ylabel("Fall Rate")
    ax.set_title("Physical Execution Fall Rate by Motion Type")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Motion Type")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    if save:
        path = RESULTS_DIR / "fall_rate_by_type.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved: {path}")
    return fig


def plot_root_error_over_time(results: List[ClipMetrics], max_clips: int = 8, save: bool = True):
    """Line plot: root position error over time for each clip."""
    fig, ax = plt.subplots(figsize=(10, 5))

    for r in results[:max_clips]:
        errors = [fm.root_pos_error for fm in r.frame_metrics]
        color = _color_by_type(r.motion_type)
        ax.plot(errors, label=f"{r.clip_name} ({r.motion_type})", color=color, alpha=0.8)

    ax.set_xlabel("Frame")
    ax.set_ylabel("Root Position Error (m)")
    ax.set_title("Root Position Drift: Kinematic Target vs Physics Execution")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(linestyle="--", alpha=0.4)

    if save:
        path = RESULTS_DIR / "root_error_over_time.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved: {path}")
    return fig


def plot_summary_table(results: List[ClipMetrics], save: bool = True):
    """Print and optionally save a summary metrics table."""
    rows = [r.summary() for r in results]
    if not rows:
        return

    keys = list(rows[0].keys())
    header = " | ".join(f"{k:>20}" for k in keys)
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = " | ".join(f"{str(row[k]):>20}" for k in keys)
        print(line)
    print(sep)

    if save:
        import csv
        path = RESULTS_DIR / "summary.csv"
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved: {path}")


def plot_all(results: List[ClipMetrics]):
    plot_tracking_error_by_type(results)
    plot_fall_rate_by_type(results)
    plot_root_error_over_time(results)
    plot_summary_table(results)
    plt.show()
