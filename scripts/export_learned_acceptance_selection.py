"""Export learned-acceptance selected candidates as SONIC references."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from export_sonic_references import SONIC_FPS, SOURCE_FPS, export_clip


ROOT = Path(__file__).resolve().parents[1]


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


def as_int(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection_csv", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, required=True)
    parser.add_argument("--selector", default="learned_acceptance")
    args = parser.parse_args()

    out_dir = args.out_dir.resolve()
    reference_root = out_dir / "sonic_references"
    reference_root.mkdir(parents=True, exist_ok=True)

    selected_rows: list[dict[str, object]] = []
    export_rows: list[dict[str, object]] = []
    for row in read_rows(args.selection_csv):
        mode = row["mode"]
        seed_idx = as_int(row, "seed_idx")
        candidate_k = as_int(row, "candidate_k")
        selected_motion = f"{args.selector}_{mode}_seed{seed_idx}_cand{candidate_k}"
        qpos_path = Path(row["path"])
        if not qpos_path.is_absolute():
            qpos_path = ROOT / qpos_path
        selected = {
            **row,
            "selector": args.selector,
            "selected_motion": selected_motion,
        }
        selected_rows.append(selected)
        export = export_clip(qpos_path, reference_root / selected_motion, SOURCE_FPS, SONIC_FPS)
        export_rows.append(
            {
                **export,
                "selector": args.selector,
                "mode": mode,
                "seed_idx": seed_idx,
                "candidate_k": candidate_k,
                "ensemble_accept_prob": row.get("ensemble_accept_prob", ""),
                "full_risk": row.get("full_risk", ""),
                "precontroller_score": row.get("precontroller_score", ""),
                "root_z_min": row.get("root_z_min", ""),
                "low_root_frames_pct": row.get("low_root_frames_pct", ""),
                "upright_reference_gate_pass": row.get("upright_reference_gate_pass", ""),
            }
        )
        print(f"[export] {selected_motion}")

    write_rows(out_dir / "prospective_selected.csv", selected_rows)
    write_rows(out_dir / "export_manifest.csv", export_rows)
    print(f"Exported {len(export_rows)} learned SONIC references to {reference_root}")


if __name__ == "__main__":
    main()
