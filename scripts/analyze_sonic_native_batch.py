"""Analyze a native SONIC release batch and organize videos for review."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def mean(values: list[float]) -> float:
    return sum(values) / max(1, len(values))


def summarize(rows: list[dict[str, str]], key: str) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("status") == "completed":
            groups[row[key]].append(row)
    out = []
    for name, group in sorted(groups.items()):
        passes = [r for r in group if r.get("fell") == "False"]
        out.append(
            {
                key: name,
                "n": len(group),
                "pass_count": len(passes),
                "pass_rate": len(passes) / len(group),
                "mean_rmse": mean([float(r["mean_joint_rmse"]) for r in group]),
                "mean_pass_rmse": mean([float(r["mean_joint_rmse"]) for r in passes]) if passes else "",
                "mean_fall_time_s": mean([float(r["fall_time_s"]) for r in group]),
            }
        )
    return out


def link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def organize_videos(batch_dir: Path, rows: list[dict[str, str]]) -> None:
    pass_dir = batch_dir / "pass_videos"
    fail_dir = batch_dir / "fail_videos"
    presentation_dir = batch_dir / "presentation_pass_videos"
    strict_presentation_dir = batch_dir / "strict_presentation_pass_videos"
    for row in rows:
        video = Path(row.get("video", ""))
        if not video.exists():
            continue
        target_dir = pass_dir if row.get("fell") == "False" else fail_dir
        link_or_copy(video, target_dir / video.name)

    passes = [r for r in rows if r.get("fell") == "False" and r.get("category") == "upright"]
    by_mode: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sorted(passes, key=lambda r: float(r["mean_joint_rmse"])):
        by_mode[row["mode"]].append(row)

    selected: list[dict[str, str]] = []
    # Round-robin modes so the presentation set is diverse, not just low-RMSE walk variants.
    while len(selected) < 24:
        added = False
        for mode in sorted(by_mode):
            if by_mode[mode]:
                selected.append(by_mode[mode].pop(0))
                added = True
                if len(selected) >= 24:
                    break
        if not added:
            break
    for row in selected:
        video = Path(row["video"])
        if video.exists():
            link_or_copy(video, presentation_dir / video.name)
    write_rows(batch_dir / "presentation_pass_selection.csv", selected)

    strict_passes = [
        r
        for r in passes
        if float(r["mean_joint_rmse"]) <= 0.20 and float(r["mean_root_xy_error"]) <= 1.5
    ]
    strict_by_mode: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sorted(strict_passes, key=lambda r: (float(r["mean_joint_rmse"]), float(r["mean_root_xy_error"]))):
        strict_by_mode[row["mode"]].append(row)
    strict_selected: list[dict[str, str]] = []
    while len(strict_selected) < 24:
        added = False
        for mode in sorted(strict_by_mode):
            if strict_by_mode[mode]:
                strict_selected.append(strict_by_mode[mode].pop(0))
                added = True
                if len(strict_selected) >= 24:
                    break
        if not added:
            break
    for row in strict_selected:
        video = Path(row["video"])
        if video.exists():
            link_or_copy(video, strict_presentation_dir / video.name)
    write_rows(batch_dir / "strict_presentation_pass_selection.csv", strict_selected)


def contact_sheet(video_dir: Path, out: Path, limit: int = 0) -> None:
    if not video_dir.exists() or not any(video_dir.glob("*.mp4")):
        return
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "render_video_contact_sheet.py"),
        "--video_dir",
        str(video_dir),
        "--out",
        str(out),
        "--samples",
        "4",
        "--thumb_width",
        "180",
    ]
    if limit:
        cmd += ["--limit", str(limit)]
    subprocess.run(cmd, cwd=ROOT, check=True)


def write_markdown(batch_dir: Path, rows: list[dict[str, str]]) -> None:
    completed = [r for r in rows if r.get("status") == "completed"]
    passes = [r for r in completed if r.get("fell") == "False"]
    failures = [r for r in completed if r.get("fell") == "True"]
    upright = [r for r in completed if r.get("category") == "upright"]
    upright_pass = [r for r in upright if r.get("fell") == "False"]
    idle = [r for r in completed if r.get("category") == "idle"]
    crawl = [r for r in completed if r.get("category") == "low_posture_crawling"]

    lines = [
        "# Native SONIC Batch Analysis",
        "",
        f"- completed: {len(completed)}",
        f"- overall pass: {len(passes)}/{len(completed)}",
        f"- upright pass: {len(upright_pass)}/{len(upright)}",
        f"- strict upright pass (survive, RMSE <= 0.20, root XY <= 1.5m): "
        f"{sum(r.get('fell') == 'False' and r.get('category') == 'upright' and float(r['mean_joint_rmse']) <= 0.20 and float(r['mean_root_xy_error']) <= 1.5 for r in completed)}/{len(upright)}",
        f"- idle pass: {sum(r.get('fell') == 'False' for r in idle)}/{len(idle)}",
        f"- crawling pass: {sum(r.get('fell') == 'False' for r in crawl)}/{len(crawl)}",
        f"- mean joint RMSE: {mean([float(r['mean_joint_rmse']) for r in completed]):.3f}",
        "",
        "## Failure Motions",
        "",
    ]
    for row in failures:
        lines.append(
            f"- `{row['motion']}` ({row['category']}): fall={float(row['fall_time_s']):.2f}s, "
            f"rmse={float(row['mean_joint_rmse']):.3f}, min_root_z={float(row['min_root_z']):.3f}"
        )
    lines += [
        "",
        "## Review Folders",
        "",
        "- `presentation_pass_videos/`: diverse subset of passing upright clips.",
        "- `strict_presentation_pass_videos/`: diverse subset with survival, low joint RMSE, and bounded root drift.",
        "- `pass_videos/`: all clips that passed the root-height threshold.",
        "- `fail_videos/`: all clips that failed.",
        "- `*_contact_sheet.jpg`: sampled visual summaries.",
        "",
    ]
    (batch_dir / "analysis_summary.md").write_text("\n".join(lines))


def write_plots(batch_dir: Path, rows: list[dict[str, str]]) -> None:
    mode_rows = summarize(rows, "mode")
    mode_rows = sorted(mode_rows, key=lambda r: (float(r["pass_rate"]), r["mode"]))
    labels = [str(r["mode"]) for r in mode_rows]
    rates = [float(r["pass_rate"]) for r in mode_rows]
    counts = [int(r["n"]) for r in mode_rows]

    fig_h = max(5.0, 0.34 * len(labels))
    fig, ax = plt.subplots(figsize=(8.0, fig_h))
    y = list(range(len(labels)))
    colors = ["#c84a31" if rate < 0.8 else "#3f7f5f" for rate in rates]
    ax.barh(y, rates, color=colors)
    ax.set_yticks(y, labels)
    ax.set_xlim(0.0, 1.05)
    ax.set_xlabel("Native SONIC release pass rate")
    ax.set_title("Pass Rate by Motion Type")
    for yi, rate, count in zip(y, rates, counts):
        ax.text(min(1.01, rate + 0.02), yi, f"{rate:.0%}  n={count}", va="center", fontsize=8)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(batch_dir / "pass_rate_by_mode.png", dpi=180)
    plt.close(fig)

    category_rows = summarize(rows, "category")
    labels = [str(r["category"]) for r in category_rows]
    rates = [float(r["pass_rate"]) for r in category_rows]
    counts = [int(r["n"]) for r in category_rows]
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.bar(labels, rates, color=["#3f7f5f" if rate > 0 else "#c84a31" for rate in rates])
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Native SONIC release pass rate")
    ax.set_title("Pass Rate by Category")
    for i, (rate, count) in enumerate(zip(rates, counts)):
        ax.text(i, min(1.02, rate + 0.03), f"{rate:.0%}\nn={count}", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(batch_dir / "pass_rate_by_category.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_dir", type=Path, required=True)
    args = parser.parse_args()
    batch_dir = args.batch_dir.resolve()
    rows = read_rows(batch_dir / "batch_summary.csv")

    write_rows(batch_dir / "summary_by_category.csv", summarize(rows, "category"))
    write_rows(batch_dir / "summary_by_mode.csv", summarize(rows, "mode"))
    write_rows(batch_dir / "failures.csv", [r for r in rows if r.get("fell") == "True"])
    organize_videos(batch_dir, rows)
    contact_sheet(batch_dir / "presentation_pass_videos", batch_dir / "presentation_pass_contact_sheet.jpg")
    contact_sheet(batch_dir / "strict_presentation_pass_videos", batch_dir / "strict_presentation_pass_contact_sheet.jpg")
    contact_sheet(batch_dir / "fail_videos", batch_dir / "fail_contact_sheet.jpg")
    contact_sheet(batch_dir / "pass_videos", batch_dir / "pass_contact_sheet_first40.jpg", limit=40)
    write_plots(batch_dir, rows)
    write_markdown(batch_dir, rows)
    print(f"Analyzed {batch_dir}")


if __name__ == "__main__":
    main()
