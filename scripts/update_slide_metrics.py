"""Write a small slide metrics snapshot from the latest completed results."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "slides" / "assets" / "metrics_snapshot.md"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def candidate_selector_files() -> list[Path]:
    paths = list((ROOT / "results" / "ralphloop").glob("20*/humanoid100_final_eval_k*/final_selector_initref/selector_summary.csv"))
    paths += [ROOT / "results" / "humanoid100_final_eval" / "final_selector_initref" / "selector_summary.csv"]
    return [p for p in paths if p.exists()]


def main() -> None:
    files = candidate_selector_files()
    if not files:
        OUT.write_text("No selector summary found yet.\n")
        print(OUT)
        return
    latest = max(files, key=lambda p: p.stat().st_mtime)
    rows = read_rows(latest)
    keep = [
        "selector=K1_first",
        "selector=K8_best_of_8",
        "selector=repaired_retime",
        "selector=risk_verifier_best",
        "selector=sonic_verified_best",
    ]
    by = {row["group"]: row for row in rows}
    lines = [
        "# Metrics Snapshot",
        "",
        f"Source: `{latest.relative_to(ROOT)}`",
        "",
        "| Selector | Physical Pass | No Fall | Mean SONIC Sec. | Mean RMSE |",
        "|---|---:|---:|---:|---:|",
    ]
    for key in keep:
        row = by.get(key)
        if not row:
            continue
        lines.append(
            f"| {key.split('=', 1)[1]} | {int(float(row['physical_pass_count']))}/100 | "
            f"{int(float(row['sonic_no_fall_count']))}/100 | "
            f"{float(row['mean_sonic_track_seconds']):.3f} | "
            f"{float(row['mean_sonic_rmse']):.3f} |"
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
