"""Score prospective candidates with trained native-acceptance checkpoints.

The script writes two complementary views:

1. ensemble scores for every generated candidate in a prospective directory;
2. a fair retrospective selector over only native-evaluated candidates using
   out-of-fold cross-validation predictions from the training run.

The second view is the one to use for claims. The first view is for choosing
new candidates in a future prospective native rollout.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

from train_native_sonic_acceptance import NativeAcceptanceNet, QPOS_DIM, normalize_qpos


ROOT = Path(__file__).resolve().parents[1]
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


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


def as_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def as_int(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def motion_key(row: dict[str, str]) -> str:
    return f"{row['mode']}_seed{as_int(row, 'seed_idx')}_cand{as_int(row, 'candidate_k')}"


def selected_identity(row: dict[str, str]) -> str:
    return f"{row['mode']}::seed{as_int(row, 'seed_idx')}"


def strict_from_native(row: dict[str, str]) -> bool:
    return (
        row.get("fell") == "False"
        and as_float(row, "mean_joint_rmse", 999.0) <= 0.20
        and as_float(row, "mean_root_xy_error", 999.0) <= 1.5
    )


@dataclass(frozen=True)
class Candidate:
    row: dict[str, str]
    key: str
    identity: str
    path: Path


class CandidateDataset(Dataset):
    def __init__(self, candidates: list[Candidate]):
        self.candidates = candidates

    def __len__(self) -> int:
        return len(self.candidates)

    def __getitem__(self, idx: int):
        candidate = self.candidates[idx]
        qpos = np.load(candidate.path).astype(np.float32)
        qpos = normalize_qpos(qpos)
        return torch.from_numpy(qpos).T, candidate.key


def collate(batch):
    xs, keys = zip(*batch)
    max_t = max(x.shape[1] for x in xs)
    padded = torch.zeros(len(xs), QPOS_DIM, max_t)
    mask = torch.zeros(len(xs), max_t, dtype=torch.bool)
    for i, x in enumerate(xs):
        t = x.shape[1]
        padded[i, :, :t] = x
        mask[i, :t] = True
    return padded, mask, list(keys)


def load_candidates(path: Path) -> list[Candidate]:
    out: list[Candidate] = []
    for row in read_rows(path):
        qpos_path = Path(row["path"])
        if not qpos_path.is_absolute():
            qpos_path = ROOT / qpos_path
        if not qpos_path.exists():
            continue
        out.append(Candidate(row=row, key=motion_key(row), identity=selected_identity(row), path=qpos_path))
    return out


def load_checkpoints(model_dir: Path) -> list[NativeAcceptanceNet]:
    checkpoints = sorted(model_dir.glob("fold_*_best.pt"))
    if not checkpoints:
        raise ValueError(f"No fold checkpoints found in {model_dir}")
    models: list[NativeAcceptanceNet] = []
    for checkpoint_path in checkpoints:
        checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
        model = NativeAcceptanceNet(int(checkpoint["width"])).to(DEVICE)
        model.load_state_dict(checkpoint["model_state"])
        model.eval()
        models.append(model)
    return models


def score_candidates(candidates: list[Candidate], models: list[NativeAcceptanceNet], batch_size: int) -> dict[str, float]:
    loader = DataLoader(CandidateDataset(candidates), batch_size=batch_size, shuffle=False, collate_fn=collate)
    scores: dict[str, list[float]] = {candidate.key: [] for candidate in candidates}
    with torch.no_grad():
        for x, mask, keys in loader:
            x = x.to(DEVICE)
            mask = mask.to(DEVICE)
            for model in models:
                probs = torch.sigmoid(model(x, mask)).detach().cpu().numpy()
                for key, prob in zip(keys, probs):
                    scores[key].append(float(prob))
    return {key: float(np.mean(values)) for key, values in scores.items()}


def choose_best(rows: list[dict[str, object]], score_key: str) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["identity"]), []).append(row)
    out = []
    for identity, group in sorted(grouped.items()):
        best = max(group, key=lambda r: (float(r[score_key]), -float(r.get("full_risk", 0.0)), -float(r["candidate_k"])))
        out.append(best)
    return out


def retrospective_summary(selected: list[dict[str, object]], title: str) -> list[str]:
    evaluated = [row for row in selected if row.get("native_evaluated") == "__YES__"]
    strict = [
        row
        for row in evaluated
        if row.get("native_strict_pass") == "__YES__" or row.get("native_strict_any") == "__YES__"
    ]
    lines = [
        f"## {title}",
        "",
        f"- selected identities: {len(selected)}",
        f"- native-evaluated selections: {len(evaluated)}/{len(selected)}",
    ]
    if evaluated:
        lines.append(f"- strict among evaluated: {len(strict)}/{len(evaluated)} ({len(strict) / len(evaluated):.1%})")
    lines.append("")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prospective_dir", type=Path, required=True)
    parser.add_argument("--model_dir", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, default=None)
    parser.add_argument("--batch", type=int, default=64)
    args = parser.parse_args()

    prospective_dir = args.prospective_dir.resolve()
    model_dir = args.model_dir.resolve()
    out_dir = args.out_dir or (prospective_dir / "learned_acceptance_selector")
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = load_candidates(prospective_dir / "prospective_candidates.csv")
    models = load_checkpoints(model_dir)
    ensemble_scores = score_candidates(candidates, models, args.batch)

    selected_rows = read_rows(prospective_dir / "prospective_selected.csv")
    selected_by_motion = {row["selected_motion"]: row for row in selected_rows}
    native_path = prospective_dir / "native_release" / "batch_summary.csv"
    native_rows = {row["motion"]: row for row in read_rows(native_path) if row.get("status") == "completed"} if native_path.exists() else {}
    cv_path = model_dir / "crossval_predictions.csv"
    cv_scores = {row["key"]: as_float(row, "pred_accept_prob") for row in read_rows(cv_path)} if cv_path.exists() else {}

    score_rows: list[dict[str, object]] = []
    selected_by_raw: dict[str, list[dict[str, str]]] = {}
    for selected in selected_rows:
        selected_by_raw.setdefault(motion_key(selected), []).append(selected)
    for candidate in candidates:
        row = candidate.row
        motion = candidate.key
        selected_matches = selected_by_raw.get(motion, [])
        native_matches = [native_rows[selected["selected_motion"]] for selected in selected_matches if selected["selected_motion"] in native_rows]
        strict_matches = [native for native in native_matches if strict_from_native(native)]
        out = {
            "motion": motion,
            "identity": candidate.identity,
            "mode": row["mode"],
            "seed_idx": as_int(row, "seed_idx"),
            "candidate_k": as_int(row, "candidate_k"),
            "path": row["path"],
            "ensemble_accept_prob": ensemble_scores[motion],
            "crossval_accept_prob": cv_scores.get(motion, ""),
            "full_risk": as_float(row, "full_risk"),
            "precontroller_score": as_float(row, "precontroller_score"),
            "root_z_min": as_float(row, "root_z_min"),
            "low_root_frames_pct": as_float(row, "low_root_frames_pct"),
            "upright_reference_gate_pass": row.get("upright_reference_gate_pass", ""),
            "native_evaluated": "__YES__" if native_matches else "__NO__",
            "native_evaluated_count": len(native_matches),
            "native_strict_any": "__YES__" if strict_matches else "__NO__" if native_matches else "",
            "native_strict_count": len(strict_matches),
            "source_selectors": ";".join(sorted({selected["selector"] for selected in selected_matches})),
        }
        score_rows.append(out)

    ensemble_selection = choose_best(score_rows, "ensemble_accept_prob")
    evaluated_rows: list[dict[str, object]] = []
    for selected in selected_rows:
        selected_motion = selected["selected_motion"]
        native = native_rows.get(selected_motion)
        if not native or selected_motion not in cv_scores:
            continue
        raw_key = motion_key(selected)
        evaluated_rows.append(
            {
                "motion": selected_motion,
                "raw_motion": raw_key,
                "identity": selected_identity(selected),
                "mode": selected["mode"],
                "seed_idx": as_int(selected, "seed_idx"),
                "candidate_k": as_int(selected, "candidate_k"),
                "selector": selected["selector"],
                "crossval_accept_prob": cv_scores[selected_motion],
                "full_risk": as_float(selected, "full_risk"),
                "precontroller_score": as_float(selected, "precontroller_score"),
                "root_z_min": as_float(selected, "root_z_min"),
                "low_root_frames_pct": as_float(selected, "low_root_frames_pct"),
                "native_evaluated": "__YES__",
                "native_strict_pass": "__YES__" if strict_from_native(native) else "__NO__",
                "native_fell": native.get("fell", ""),
                "native_mean_joint_rmse": native.get("mean_joint_rmse", ""),
            }
        )
    crossval_selection = choose_best(evaluated_rows, "crossval_accept_prob")

    write_rows(out_dir / "candidate_scores.csv", score_rows)
    write_rows(out_dir / "ensemble_selection_all_candidates.csv", ensemble_selection)
    write_rows(out_dir / "crossval_selection_evaluated_candidates.csv", crossval_selection)

    lines = [
        "# Learned Native-Acceptance Selector Audit",
        "",
        f"- device: {DEVICE}",
        f"- candidates scored: {len(score_rows)}",
        f"- checkpoints: {len(models)}",
        f"- identities: {len({row['identity'] for row in score_rows})}",
        "",
        "The all-candidate ensemble selection is for future prospective rollout.",
        "The evaluated-candidate selection is the fair retrospective estimate, because",
        "it uses out-of-fold predictions for native-evaluated rows only.",
        "",
    ]
    lines.extend(retrospective_summary(ensemble_selection, "Ensemble Selection Over All Candidates"))
    lines.extend(retrospective_summary(crossval_selection, "Out-of-Fold Selection Over Evaluated Candidates"))
    (out_dir / "learned_selector_audit.md").write_text("\n".join(lines))
    print(f"Wrote learned selector audit to {out_dir}")


if __name__ == "__main__":
    main()
