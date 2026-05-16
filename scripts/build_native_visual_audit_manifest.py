"""Build a human-review manifest for native SONIC release videos.

Numeric gates catch falls, RMSE, and root drift, but they do not certify that a
motion looks semantically right. This script selects a compact review set and
creates blank rubric columns for manual or VLM-assisted visual scoring.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


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


def f(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def strict_pass(row: dict[str, str]) -> bool:
    return (
        row.get("status") == "completed"
        and row.get("fell") == "False"
        and f(row, "mean_joint_rmse", 999.0) <= 0.20
        and f(row, "mean_root_xy_error", 999.0) <= 1.5
    )


def rubric_row(row: dict[str, str], group: str) -> dict[str, object]:
    return {
        "review_group": group,
        "motion": row.get("motion", ""),
        "mode": row.get("mode", ""),
        "category": row.get("category", ""),
        "fell": row.get("fell", ""),
        "fall_time_s": row.get("fall_time_s", ""),
        "mean_joint_rmse": row.get("mean_joint_rmse", ""),
        "mean_root_xy_error": row.get("mean_root_xy_error", ""),
        "min_root_z": row.get("min_root_z", ""),
        "video": row.get("video", ""),
        "stability_score_1_to_5": "",
        "reference_following_score_1_to_5": "",
        "style_or_prompt_match_score_1_to_5": "",
        "root_motion_plausible_score_1_to_5": "",
        "visible_artifact_score_1_to_5": "",
        "review_decision": "",
        "notes": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_dir", type=Path, required=True)
    parser.add_argument("--per_group", type=int, default=12)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    batch_dir = args.batch_dir.resolve()
    rows = [r for r in read_rows(batch_dir / "batch_summary.csv") if r.get("status") == "completed"]
    passes = [r for r in rows if strict_pass(r) and r.get("category") == "upright"]
    borderline = [
        r
        for r in rows
        if r.get("fell") == "False"
        and r.get("category") == "upright"
        and not strict_pass(r)
    ]
    failures = [r for r in rows if r.get("fell") == "True"]

    passes = sorted(passes, key=lambda r: (f(r, "mean_joint_rmse"), f(r, "mean_root_xy_error")))[: args.per_group]
    borderline = sorted(
        borderline,
        key=lambda r: (abs(f(r, "mean_joint_rmse") - 0.20), abs(f(r, "mean_root_xy_error") - 1.5)),
    )[: args.per_group]
    failures = sorted(failures, key=lambda r: -f(r, "fall_time_s"))[: args.per_group]

    out_rows = (
        [rubric_row(r, "strict_pass") for r in passes]
        + [rubric_row(r, "borderline_pass") for r in borderline]
        + [rubric_row(r, "failure") for r in failures]
    )
    out_path = args.out or (batch_dir / "native_visual_audit_manifest.csv")
    write_rows(out_path, out_rows)
    print(f"Wrote {len(out_rows)} visual-audit rows to {out_path}")


if __name__ == "__main__":
    main()
