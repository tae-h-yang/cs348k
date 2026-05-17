"""Relate reference sanity checks to native SONIC rollout outcomes."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

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


def as_float(row: dict[str, object], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def strict_pass(row: dict[str, object]) -> bool:
    return (
        row.get("fell") == "False"
        and as_float(row, "mean_joint_rmse", 999.0) <= 0.20
        and as_float(row, "mean_root_xy_error", 999.0) <= 1.5
    )


def summarize_joined(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row.get("status") != "completed":
            continue
        low_root = as_float(row, "ref_low_root_frames_pct") > 0.0
        groups[(str(row["mode"]), "low_root" if low_root else "upright_root")].append(row)

    out: list[dict[str, object]] = []
    for (mode, reference_group), group in sorted(groups.items()):
        falls = [row for row in group if row.get("fell") == "True"]
        strict = [row for row in group if strict_pass(row)]
        out.append(
            {
                "mode": mode,
                "reference_group": reference_group,
                "n": len(group),
                "fall_count": len(falls),
                "fall_rate": len(falls) / max(len(group), 1),
                "strict_count": len(strict),
                "strict_rate": len(strict) / max(len(group), 1),
                "mean_joint_rmse": float(np.mean([as_float(row, "mean_joint_rmse") for row in group])),
                "mean_root_xy_error": float(np.mean([as_float(row, "mean_root_xy_error") for row in group])),
                "mean_ref_root_z_min": float(np.mean([as_float(row, "ref_root_z_min") for row in group])),
                "mean_ref_low_root_frames_pct": float(
                    np.mean([as_float(row, "ref_low_root_frames_pct") for row in group])
                ),
            }
        )
    return out


def worst_references(rows: list[dict[str, object]], limit: int) -> list[dict[str, object]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            -as_float(row, "ref_low_root_frames_pct"),
            as_float(row, "ref_root_z_min", 999.0),
            -as_float(row, "mean_joint_rmse"),
        ),
    )
    return ranked[:limit]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prospective_dir", type=Path, required=True)
    parser.add_argument("--batch_dir", type=Path, default=None)
    parser.add_argument("--out_dir", type=Path, default=None)
    parser.add_argument("--worst_limit", type=int, default=25)
    args = parser.parse_args()

    prospective_dir = args.prospective_dir.resolve()
    batch_dir = args.batch_dir.resolve() if args.batch_dir else prospective_dir / "native_release"
    out_dir = args.out_dir.resolve() if args.out_dir else prospective_dir

    native_rows = read_rows(batch_dir / "batch_summary.csv")
    audit = {row["motion"]: row for row in read_rows(prospective_dir / "sonic_reference_export_audit.csv")}

    joined: list[dict[str, object]] = []
    missing = 0
    for native in native_rows:
        ref = audit.get(native["motion"])
        if ref is None:
            missing += 1
            continue
        joined.append(
            {
                **native,
                "ref_roundtrip_max_abs": ref["roundtrip_max_abs"],
                "ref_root_z_min": ref["root_z_min"],
                "ref_root_z_start": ref["root_z_start"],
                "ref_root_z_end": ref["root_z_end"],
                "ref_root_xy_displacement": ref["root_xy_displacement"],
                "ref_p95_root_xy_step_per_frame": ref["p95_root_xy_step_per_frame"],
                "ref_p95_joint_step_rad_per_frame": ref["p95_joint_step_rad_per_frame"],
                "ref_low_root_frames_pct": ref["low_root_frames_pct"],
                "ref_is_low_root": "__YES__" if float(ref["low_root_frames_pct"]) > 0.0 else "__NO__",
            }
        )

    joined_path = out_dir / "sonic_reference_sanity_joined.csv"
    summary_path = out_dir / "sonic_reference_sanity_summary.csv"
    worst_path = out_dir / "sonic_reference_sanity_worst.csv"
    write_rows(joined_path, joined)
    summary = summarize_joined(joined)
    write_rows(summary_path, summary)
    write_rows(worst_path, worst_references(joined, args.worst_limit))

    low_root = sum(row["ref_is_low_root"] == "__YES__" for row in joined)
    strict_low = sum(row["ref_is_low_root"] == "__YES__" and strict_pass(row) for row in joined)
    strict_upright = sum(row["ref_is_low_root"] == "__NO__" and strict_pass(row) for row in joined)
    upright = len(joined) - low_root
    print(f"joined={len(joined)} missing_audit={missing}")
    print(f"low_root={low_root} strict_low={strict_low}/{max(low_root, 1)}")
    print(f"upright_root={upright} strict_upright={strict_upright}/{max(upright, 1)}")
    print(summary_path)
    print(worst_path)


if __name__ == "__main__":
    main()
