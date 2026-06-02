#!/usr/bin/env python3
"""Plot the final reference-aware native SONIC selection summary."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "results" / "ralphloop" / "20260529_191342" / "humanoid100_final_eval_k256"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection_csv", type=Path, default=DEFAULT_BASE / "final_100_native_selection_ref_aware.csv")
    parser.add_argument("--out_png", type=Path, default=DEFAULT_BASE / "final_100_native_selection_ref_aware.png")
    args = parser.parse_args()

    df = pd.read_csv(args.selection_csv)
    df["ref_aware_no_fall"] = df["ref_aware_no_fall"].astype(str).str.lower().eq("true")
    df["strict_tracking_pass"] = df["strict_tracking_pass"].astype(str).str.lower().eq("true")
    by_cat = (
        df.groupby("category", sort=True)
        .agg(
            prompts=("prompt_id", "count"),
            no_fall=("ref_aware_no_fall", "sum"),
            strict=("strict_tracking_pass", "sum"),
            mean_rmse=("mean_joint_rmse", "mean"),
            mean_root_xy=("mean_root_xy_error", "mean"),
        )
        .reset_index()
    )

    plt.rcParams.update({"font.size": 10})
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.2), gridspec_kw={"width_ratios": [1.15, 1.0]})

    y = range(len(by_cat))
    axes[0].barh(y, by_cat["prompts"], color="#d8dee9", label="prompts")
    axes[0].barh(y, by_cat["no_fall"], color="#55a868", label="ref-aware no-fall")
    axes[0].barh(y, by_cat["strict"], color="#4c72b0", label="strict tracking")
    axes[0].set_yticks(list(y), by_cat["category"])
    axes[0].invert_yaxis()
    axes[0].set_xlabel("count")
    axes[0].set_title("Native SONIC verifier selection by category")
    axes[0].legend(loc="lower right", frameon=False)
    for i, row in by_cat.iterrows():
        axes[0].text(row["prompts"] + 0.15, i, f"{int(row['strict'])}/{int(row['prompts'])}", va="center")

    colors = df["strict_tracking_pass"].map({True: "#4c72b0", False: "#c44e52"})
    axes[1].scatter(df["mean_joint_rmse"], df["mean_root_xy_error"], c=colors, s=38, alpha=0.86, edgecolor="white", linewidth=0.5)
    axes[1].axvline(0.20, color="#333333", linestyle="--", linewidth=1.0)
    axes[1].axhline(1.50, color="#333333", linestyle="--", linewidth=1.0)
    axes[1].set_xlabel("mean joint RMSE")
    axes[1].set_ylabel("mean root XY error (m)")
    axes[1].set_title("Strict gate: RMSE <= 0.20 and root XY <= 1.5 m")
    axes[1].grid(True, alpha=0.25)
    axes[1].text(0.02, 0.98, "blue: strict pass\nred: survives but not strict", transform=axes[1].transAxes, va="top")

    no_fall = int(df["ref_aware_no_fall"].sum())
    strict = int(df["strict_tracking_pass"].sum())
    fig.suptitle(f"Final 100-prompt selection: {no_fall}/100 no-fall, {strict}/100 strict tracking", y=1.02)
    fig.tight_layout()
    args.out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out_png, dpi=220, bbox_inches="tight")
    print(f"Wrote {args.out_png}")


if __name__ == "__main__":
    main()
