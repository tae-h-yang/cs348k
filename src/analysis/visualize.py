"""
Visualization utilities for kinematic-to-dynamic gap analysis results.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")   # headless-safe; must come before pyplot import
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict
from physics_eval.metrics import ClipMetrics

RESULTS_DIR = Path(__file__).parents[2] / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Joint names matching the actuator order in g1_29dof.xml
JOINT_NAMES = [
    "L_hip_p", "L_hip_r", "L_hip_y", "L_knee", "L_ank_p", "L_ank_r",
    "R_hip_p", "R_hip_r", "R_hip_y", "R_knee", "R_ank_p", "R_ank_r",
    "W_yaw", "W_roll", "W_pitch",
    "L_sh_p", "L_sh_r", "L_sh_y", "L_elbow", "L_wr_r", "L_wr_p", "L_wr_y",
    "R_sh_p", "R_sh_r", "R_sh_y", "R_elbow", "R_wr_r", "R_wr_p", "R_wr_y",
]


def _color_by_type(motion_type: str) -> str:
    palette = {
        "static":      "#4CAF50",
        "locomotion":  "#2196F3",
        "expressive":  "#9C27B0",
        "whole_body":  "#FF9800",
        "adversarial": "#F44336",
        "unknown":     "#9E9E9E",
    }
    return palette.get(motion_type, "#9E9E9E")


def plot_tracking_error_by_type(results: List[ClipMetrics], save: bool = True):
    """Bar chart: mean joint tracking RMSE grouped by motion type (physics mode only)."""
    phys = [r for r in results if r.mode == "physics"]
    by_type: Dict[str, List[float]] = {}
    for r in phys:
        by_type.setdefault(r.motion_type, []).append(r.mean_tracking_rmse)
    if not by_type:
        return None

    types  = sorted(by_type.keys())
    means  = [np.mean(by_type[t]) for t in types]
    stds   = [np.std(by_type[t])  for t in types]
    colors = [_color_by_type(t)   for t in types]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(types, means, yerr=stds, color=colors, capsize=5, edgecolor="black", linewidth=0.8)
    ax.set_ylabel("Mean Joint Tracking RMSE (rad)")
    ax.set_title("Kinematic-to-Dynamic Gap: Tracking Error by Motion Type")
    ax.set_xlabel("Motion Type")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    if save:
        path = RESULTS_DIR / "tracking_error_by_type.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved: {path}")
    plt.close(fig)
    return fig


def plot_fall_rate_by_type(results: List[ClipMetrics], save: bool = True):
    """Bar chart: fraction of clips that fell, by motion type (physics mode only)."""
    phys = [r for r in results if r.mode == "physics"]
    by_type: Dict[str, List[bool]] = {}
    for r in phys:
        by_type.setdefault(r.motion_type, []).append(r.fell)
    if not by_type:
        return None

    types  = sorted(by_type.keys())
    rates  = [np.mean(by_type[t]) for t in types]
    colors = [_color_by_type(t)   for t in types]

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
    plt.close(fig)
    return fig


def plot_root_error_over_time(results: List[ClipMetrics], max_clips: int = 12,
                              save: bool = True):
    """Line plot: root position error over time, physics mode clips only."""
    phys = [r for r in results if r.mode == "physics"][:max_clips]
    if not phys:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    for r in phys:
        errors = [fm.root_pos_error for fm in r.frame_metrics]
        ax.plot(errors, label=f"{r.clip_name}", color=_color_by_type(r.motion_type), alpha=0.8)

    ax.set_xlabel("Frame")
    ax.set_ylabel("Root Position Error (m)")
    ax.set_title("Root Position Drift: Kinematic Target vs Physics Execution")
    ax.legend(fontsize=7, loc="upper left", ncol=2)
    ax.grid(linestyle="--", alpha=0.4)

    if save:
        path = RESULTS_DIR / "root_error_over_time.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved: {path}")
    plt.close(fig)
    return fig


def plot_per_joint_error_heatmap(results: List[ClipMetrics], save: bool = True):
    """
    Heatmap: mean per-joint tracking error (rad) for each clip × joint.
    Reveals which joints fail most and whether failure is motion-type-specific.
    Only uses physics mode results.
    """
    phys = [r for r in results if r.mode == "physics"]
    if not phys:
        return None

    data_matrix = np.stack([r.mean_per_joint_error for r in phys], axis=0)  # (N_clips, 29)
    clip_labels  = [f"{r.clip_name}\n[{r.motion_type}]" for r in phys]

    fig, ax = plt.subplots(figsize=(max(10, len(JOINT_NAMES) * 0.45),
                                    max(4, len(phys) * 0.4 + 1.5)))
    im = ax.imshow(data_matrix, aspect="auto", cmap="YlOrRd", vmin=0)
    plt.colorbar(im, ax=ax, label="Mean |error| (rad)")

    ax.set_xticks(range(len(JOINT_NAMES)))
    ax.set_xticklabels(JOINT_NAMES, rotation=60, ha="right", fontsize=7)
    ax.set_yticks(range(len(phys)))
    ax.set_yticklabels(clip_labels, fontsize=7)
    ax.set_title("Per-Joint Tracking Error Heatmap (physics execution)")
    fig.tight_layout()

    if save:
        path = RESULTS_DIR / "per_joint_error_heatmap.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved: {path}")
    plt.close(fig)
    return fig


def plot_time_to_fall(results: List[ClipMetrics], fps: float = 30.0, save: bool = True):
    """
    Bar chart: time-to-fall (seconds) per clip, grouped by motion type.
    Clips that survive the full sequence show the clip duration as a filled bar.
    Physics mode only.
    """
    phys = [r for r in results if r.mode == "physics"]
    if not phys:
        return None

    clips   = [r.clip_name for r in phys]
    durations = [r.n_frames / fps for r in phys]
    ttf       = [(r.time_to_fall / fps) if r.fell else (r.n_frames / fps) for r in phys]
    colors    = [_color_by_type(r.motion_type) for r in phys]
    hatches   = ['' if r.fell else '///' for r in phys]

    x = np.arange(len(clips))
    fig, ax = plt.subplots(figsize=(max(8, len(clips) * 0.7), 5))

    # Full clip duration (background)
    ax.bar(x, durations, color="#ECEFF1", edgecolor="#90A4AE", linewidth=0.8, label="Clip duration")
    # Time to fall (foreground)
    bars = ax.bar(x, ttf, color=colors, edgecolor="black", linewidth=0.8,
                  label="Time to fall (physics)")
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)

    ax.set_xticks(x)
    ax.set_xticklabels(clips, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Time (s)")
    ax.set_title("Physical Feasibility: Time-to-Fall Under PD Tracking\n"
                 "(hatched = survived full clip)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    if save:
        path = RESULTS_DIR / "time_to_fall.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved: {path}")
    plt.close(fig)
    return fig


def plot_gap_comparison(physics_results: List[ClipMetrics],
                        kinematic_results: List[ClipMetrics],
                        save: bool = True):
    """
    Side-by-side: kinematic joint violations vs physics tracking RMSE per motion type.
    Kinematic mode is zero-gap by definition (qpos set directly), so we show
    joint violations as a proxy for kinematic difficulty instead.
    """
    if not kinematic_results:
        return None

    kin_viol:  Dict[str, List[int]]   = {}
    phys_rmse: Dict[str, List[float]] = {}
    for r in kinematic_results:
        kin_viol.setdefault(r.motion_type, []).append(r.max_joint_limit_violations)
    for r in physics_results:
        phys_rmse.setdefault(r.motion_type, []).append(r.mean_tracking_rmse)

    types = sorted(set(kin_viol) | set(phys_rmse))
    x = np.arange(len(types))
    w = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    colors = [_color_by_type(t) for t in types]
    ax1.bar(x, [np.mean(kin_viol.get(t, [0])) for t in types],
            color=colors, edgecolor="black", linewidth=0.8)
    ax1.set_xticks(x); ax1.set_xticklabels(types)
    ax1.set_ylabel("Max Joint Limit Violations (kinematic)")
    ax1.set_title("Kinematic Difficulty\n(joint violations in raw sequence)")
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    ax2.bar(x, [np.mean(phys_rmse.get(t, [0])) for t in types],
            color=colors, edgecolor="black", linewidth=0.8)
    ax2.set_xticks(x); ax2.set_xticklabels(types)
    ax2.set_ylabel("Mean Joint Tracking RMSE (rad)")
    ax2.set_title("Dynamic Tracking Gap\n(physics execution with PD control)")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    fig.suptitle("Kinematic-to-Dynamic Gap: Difficulty vs Tracking Error", fontweight="bold")
    fig.tight_layout()

    if save:
        path = RESULTS_DIR / "gap_comparison.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"Saved: {path}")
    plt.close(fig)
    return fig


def plot_summary_table(results: List[ClipMetrics], save: bool = True):
    """Print and save a summary metrics CSV."""
    rows = [r.summary() for r in results]
    if not rows:
        return

    keys   = list(rows[0].keys())
    header = " | ".join(f"{k:>22}" for k in keys)
    sep    = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        print(" | ".join(f"{str(row[k]):>22}" for k in keys))
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
    phys = [r for r in results if r.mode == "physics"]
    kin  = [r for r in results if r.mode == "kinematic"]

    plot_tracking_error_by_type(results)
    plot_fall_rate_by_type(results)
    plot_time_to_fall(results)
    plot_root_error_over_time(results)
    plot_per_joint_error_heatmap(results)
    plot_gap_comparison(phys, kin)
    plot_summary_table(results)
