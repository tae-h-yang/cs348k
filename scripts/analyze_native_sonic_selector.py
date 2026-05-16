"""Compare MotionBricks selectors against native SONIC release validation.

The earlier project used inverse dynamics and an approximate Python SONIC bridge.
This script treats the native C++ SONIC + official MuJoCo simulator results as
the execution label, then asks a narrow question:

    If we have K=1 and a physics-screened K=8 candidate for the same identity,
    which selector chooses the candidate that actually survives native SONIC?

It intentionally separates pre-controller evidence (prompt proxy, contact,
inverse-dynamics risk) from the native SONIC labels used for evaluation.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = ROOT / "results" / "candidate_evidence_table.csv"
DEFAULT_GUIDED = ROOT / "results" / "guided_ablation_extended.csv"


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


def f(row: dict[str, object], key: str, default: float = float("nan")) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def parse_motion(name: str) -> tuple[str, int]:
    match = re.match(r"(.+)_K(\d+)$", name)
    if not match:
        raise ValueError(f"Could not parse native motion name with _K suffix: {name}")
    return match.group(1), int(match.group(2))


def precontroller_score(row: dict[str, object]) -> float:
    semantic = np.clip(0.65 * f(row, "motionspec_score", 0.0) + 0.35 * f(row, "alignment_score", 0.0), 0.0, 1.0)
    contact = np.clip(1.0 - f(row, "contact_artifact_score", 1.0), 0.0, 1.0)
    dynamics = math.exp(-max(f(row, "full_risk", 100.0), 0.0) / 35.0)
    torque = math.exp(-max(f(row, "p95_torque_limit_ratio", 10.0), 0.0) / 3.0)
    return float(0.34 * semantic + 0.24 * contact + 0.26 * dynamics + 0.16 * torque)


def native_quality_tuple(row: dict[str, object]) -> tuple[float, float, float, float]:
    survived = 1.0 if str(row.get("native_fell")) == "False" else 0.0
    strict = 1.0 if str(row.get("native_strict_pass")) == "__YES__" else 0.0
    rmse = -f(row, "native_mean_joint_rmse", 999.0)
    root_xy = -f(row, "native_mean_root_xy_error", 999.0)
    return strict, survived, rmse, root_xy


def load_native(batch_csv: Path) -> list[dict[str, object]]:
    rows = []
    for row in read_rows(batch_csv):
        if row.get("status") != "completed":
            continue
        clip, k = parse_motion(row["motion"])
        fell = str(row.get("fell")) == "True"
        rmse = f(row, "mean_joint_rmse", 999.0)
        root_xy = f(row, "mean_root_xy_error", 999.0)
        strict = (not fell) and rmse <= 0.20 and root_xy <= 1.5
        rows.append(
            {
                "clip": clip,
                "K": k,
                "native_motion": row["motion"],
                "native_fell": str(fell),
                "native_pass": "__YES__" if not fell else "__NO__",
                "native_strict_pass": "__YES__" if strict else "__NO__",
                "native_fall_time_s": f(row, "fall_time_s", 0.0),
                "native_min_root_z": f(row, "min_root_z", float("nan")),
                "native_mean_joint_rmse": rmse,
                "native_mean_root_xy_error": root_xy,
                "native_video": row.get("video", ""),
                "native_category": row.get("category", ""),
                "native_mode": row.get("mode", ""),
            }
        )
    return rows


def join_evidence(native_rows: list[dict[str, object]], evidence_csv: Path, guided_csv: Path) -> list[dict[str, object]]:
    evidence = {(r["clip"], int(r["K"])): r for r in read_rows(evidence_csv)}
    guided = {(r["clip"], int(r["K"])): r for r in read_rows(guided_csv)}
    joined = []
    for native in native_rows:
        key = (str(native["clip"]), int(native["K"]))
        row = {**evidence.get(key, {}), **guided.get(key, {}), **native}
        row["precontroller_score"] = precontroller_score(row)
        joined.append(row)
    return joined


def feature_dict(row: dict[str, object]) -> dict[str, object]:
    return {
        "K": int(row["K"]),
        "mode": str(row.get("mode") or row.get("native_mode", "")),
        "category": str(row.get("category") or row.get("native_category", "")),
        "motionspec_score": f(row, "motionspec_score", 0.0),
        "alignment_score": f(row, "alignment_score", 0.0),
        "contact_artifact_score": f(row, "contact_artifact_score", 1.0),
        "full_risk": f(row, "full_risk", 100.0),
        "p95_torque_limit_ratio": f(row, "p95_torque_limit_ratio", 10.0),
        "precontroller_score": f(row, "precontroller_score", 0.0),
    }


def add_leave_mode_out_predictions(rows: list[dict[str, object]], seed: int) -> None:
    modes = sorted({str(r.get("mode") or r.get("native_mode", "")) for r in rows})
    labels = np.array([1 if r["native_strict_pass"] == "__YES__" else 0 for r in rows], dtype=int)
    global_rate = float(np.mean(labels)) if len(labels) else 0.0

    for held_mode in modes:
        train_idx = [i for i, r in enumerate(rows) if str(r.get("mode") or r.get("native_mode", "")) != held_mode]
        test_idx = [i for i, r in enumerate(rows) if str(r.get("mode") or r.get("native_mode", "")) == held_mode]
        y_train = labels[train_idx]
        if len(set(y_train.tolist())) < 2:
            probs = np.full(len(test_idx), float(np.mean(y_train)) if len(y_train) else global_rate)
        else:
            model = make_pipeline(
                DictVectorizer(sparse=False),
                RandomForestClassifier(
                    n_estimators=300,
                    min_samples_leaf=3,
                    class_weight="balanced",
                    random_state=seed,
                ),
            )
            model.fit([feature_dict(rows[i]) for i in train_idx], y_train)
            probs = model.predict_proba([feature_dict(rows[i]) for i in test_idx])[:, 1]
        for i, prob in zip(test_idx, probs):
            rows[i]["native_pred_strict_prob_lomo"] = float(prob)


def group_pairs(rows: list[dict[str, object]]) -> dict[str, dict[int, dict[str, object]]]:
    pairs: dict[str, dict[int, dict[str, object]]] = defaultdict(dict)
    for row in rows:
        pairs[str(row["clip"])][int(row["K"])] = row
    return {clip: ks for clip, ks in pairs.items() if 1 in ks and 8 in ks}


def summarize_selection(selector: str, selected: list[dict[str, object]]) -> dict[str, object]:
    n = len(selected)
    pass_count = sum(r["native_pass"] == "__YES__" for r in selected)
    strict_count = sum(r["native_strict_pass"] == "__YES__" for r in selected)
    return {
        "selector": selector,
        "n_pairs": n,
        "selected_K1_count": sum(int(r["K"]) == 1 for r in selected),
        "selected_K8_count": sum(int(r["K"]) == 8 for r in selected),
        "native_pass_count": pass_count,
        "native_pass_rate": pass_count / max(n, 1),
        "native_strict_pass_count": strict_count,
        "native_strict_pass_rate": strict_count / max(n, 1),
        "mean_native_joint_rmse": float(np.mean([f(r, "native_mean_joint_rmse") for r in selected])) if selected else "",
        "mean_native_root_xy_error": float(np.mean([f(r, "native_mean_root_xy_error") for r in selected])) if selected else "",
        "mean_full_risk": float(np.mean([f(r, "full_risk") for r in selected])) if selected else "",
        "mean_alignment_score": float(np.mean([f(r, "alignment_score") for r in selected])) if selected else "",
        "mean_contact_artifact_score": float(np.mean([f(r, "contact_artifact_score") for r in selected])) if selected else "",
        "mean_precontroller_score": float(np.mean([f(r, "precontroller_score") for r in selected])) if selected else "",
    }


def selector_comparison(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    pairs = group_pairs(rows)
    selectors: dict[str, list[dict[str, object]]] = defaultdict(list)
    details = []
    for clip, ks in sorted(pairs.items()):
        k1, k8 = ks[1], ks[8]
        candidates = [k1, k8]
        choices = {
            "K1_baseline": k1,
            "K8_ID_screened": k8,
            "lowest_inverse_dynamics_risk": min(candidates, key=lambda r: f(r, "full_risk", 999.0)),
            "best_precontroller_score": max(candidates, key=lambda r: f(r, "precontroller_score", -999.0)),
            "learned_native_strict_lomo": max(candidates, key=lambda r: f(r, "native_pred_strict_prob_lomo", -999.0)),
            "native_oracle_upper_bound": max(candidates, key=native_quality_tuple),
        }
        for selector, row in choices.items():
            selectors[selector].append(row)
            details.append(
                {
                    "clip": clip,
                    "selector": selector,
                    "selected_K": row["K"],
                    "selected_native_pass": row["native_pass"],
                    "selected_native_strict_pass": row["native_strict_pass"],
                    "selected_native_rmse": row["native_mean_joint_rmse"],
                    "selected_full_risk": row.get("full_risk", ""),
                    "selected_alignment_score": row.get("alignment_score", ""),
                    "selected_precontroller_score": row.get("precontroller_score", ""),
                    "selected_native_pred_strict_prob_lomo": row.get("native_pred_strict_prob_lomo", ""),
                    "k1_native_strict_pass": k1["native_strict_pass"],
                    "k8_native_strict_pass": k8["native_strict_pass"],
                    "k1_full_risk": k1.get("full_risk", ""),
                    "k8_full_risk": k8.get("full_risk", ""),
                }
            )
    return [summarize_selection(name, rows) for name, rows in sorted(selectors.items())], details


def safe_auc(y: np.ndarray, score: np.ndarray) -> float | str:
    if len(set(y.tolist())) < 2:
        return ""
    return float(roc_auc_score(y, score))


def safe_ap(y: np.ndarray, score: np.ndarray) -> float | str:
    if len(set(y.tolist())) < 2:
        return ""
    return float(average_precision_score(y, score))


def calibration_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    labels = {
        "native_survive": np.array([1 if r["native_pass"] == "__YES__" else 0 for r in rows], dtype=int),
        "native_strict": np.array([1 if r["native_strict_pass"] == "__YES__" else 0 for r in rows], dtype=int),
    }
    predictors = {
        "motionspec_score": np.array([f(r, "motionspec_score", 0.0) for r in rows], dtype=float),
        "alignment_score": np.array([f(r, "alignment_score", 0.0) for r in rows], dtype=float),
        "contact_score": np.array([1.0 - f(r, "contact_artifact_score", 1.0) for r in rows], dtype=float),
        "inverse_dynamics_low_risk": np.array([-f(r, "full_risk", 100.0) for r in rows], dtype=float),
        "torque_low_p95": np.array([-f(r, "p95_torque_limit_ratio", 10.0) for r in rows], dtype=float),
        "precontroller_score": np.array([f(r, "precontroller_score", 0.0) for r in rows], dtype=float),
        "learned_native_strict_lomo": np.array(
            [f(r, "native_pred_strict_prob_lomo", 0.0) for r in rows], dtype=float
        ),
    }
    out: list[dict[str, object]] = []
    for label_name, y in labels.items():
        for pred_name, score in predictors.items():
            finite = np.isfinite(score)
            yy = y[finite]
            ss = score[finite]
            out.append(
                {
                    "label": label_name,
                    "predictor": pred_name,
                    "n": int(len(yy)),
                    "positive_count": int(np.sum(yy)),
                    "roc_auc": safe_auc(yy, ss),
                    "average_precision": safe_ap(yy, ss),
                    "score_mean_positive": float(np.mean(ss[yy == 1])) if np.any(yy == 1) else "",
                    "score_mean_negative": float(np.mean(ss[yy == 0])) if np.any(yy == 0) else "",
                }
            )
    return out


def plot_summary(path: Path, summary: list[dict[str, object]]) -> None:
    if not summary:
        return
    ordered = sorted(summary, key=lambda r: float(r["native_strict_pass_rate"]))
    labels = [str(r["selector"]) for r in ordered]
    strict = [float(r["native_strict_pass_rate"]) for r in ordered]
    loose = [float(r["native_pass_rate"]) for r in ordered]
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8.5, max(4.5, 0.45 * len(labels))))
    ax.barh(y - 0.17, loose, height=0.32, label="survive", color="#7aa6c2")
    ax.barh(y + 0.17, strict, height=0.32, label="strict", color="#3f7f5f")
    ax.set_yticks(y, labels)
    ax.set_xlim(0.0, 1.05)
    ax.set_xlabel("Native SONIC release pass rate")
    ax.set_title("Selector Comparison Under Native SONIC")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def write_markdown(
    path: Path,
    summary: list[dict[str, object]],
    calibration: list[dict[str, object]],
    rows: list[dict[str, object]],
    batch_csv: Path,
) -> None:
    completed = len(rows)
    paired = len(group_pairs(rows))
    lines = [
        "# Native SONIC Selector Analysis",
        "",
        f"- native batch: `{batch_csv}`",
        f"- completed candidates joined: {completed}",
        f"- paired K=1/K=8 identities: {paired}",
        "",
        "This analysis uses native SONIC release validation as the execution label.",
        "The learned selector is leave-one-motion-mode-out; it is diagnostic, not a deployed model claim.",
        "",
        "## Selector Summary",
        "",
        "| selector | strict pass | survive | K=8 selected | mean RMSE | mean risk |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(summary, key=lambda r: str(r["selector"])):
        lines.append(
            f"| {row['selector']} | {int(row['native_strict_pass_count'])}/{int(row['n_pairs'])} "
            f"({float(row['native_strict_pass_rate']):.1%}) | "
            f"{int(row['native_pass_count'])}/{int(row['n_pairs'])} ({float(row['native_pass_rate']):.1%}) | "
            f"{int(row['selected_K8_count'])}/{int(row['n_pairs'])} | "
            f"{float(row['mean_native_joint_rmse']):.3f} | {float(row['mean_full_risk']):.2f} |"
        )
    lines += [
        "",
        "## Predictive Calibration",
        "",
        "| label | predictor | AUC | AP | positives |",
        "|---|---|---:|---:|---:|",
    ]
    for row in sorted(calibration, key=lambda r: (str(r["label"]), str(r["predictor"]))):
        auc = row["roc_auc"]
        ap = row["average_precision"]
        auc_s = f"{float(auc):.3f}" if auc != "" else ""
        ap_s = f"{float(ap):.3f}" if ap != "" else ""
        lines.append(
            f"| {row['label']} | {row['predictor']} | {auc_s} | {ap_s} | "
            f"{int(row['positive_count'])}/{int(row['n'])} |"
        )
    lines += [
        "",
        "## Interpretation Rules",
        "",
        "- If `K8_ID_screened` does not beat `K1_baseline`, inverse-dynamics best-of-K alone is not enough.",
        "- If `best_precontroller_score` improves over K1, hand-designed physics/contact/prompt gates are useful before SONIC.",
        "- `native_oracle_upper_bound` is not deployable without running SONIC; it shows how much headroom exists for controller-in-the-loop curation.",
        "- The learned selector needs more native labels before it can be claimed as a robust model.",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch_csv", type=Path, required=True)
    parser.add_argument("--evidence_csv", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--guided_csv", type=Path, default=DEFAULT_GUIDED)
    parser.add_argument("--out_dir", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()

    batch_csv = args.batch_csv.resolve()
    out_dir = args.out_dir.resolve() if args.out_dir else batch_csv.parent
    native_rows = load_native(batch_csv)
    joined = join_evidence(native_rows, args.evidence_csv, args.guided_csv)
    add_leave_mode_out_predictions(joined, args.seed)
    summary, details = selector_comparison(joined)
    calibration = calibration_rows(joined)

    write_rows(out_dir / "native_candidate_evidence.csv", joined)
    write_rows(out_dir / "native_selector_comparison.csv", summary)
    write_rows(out_dir / "native_selector_pair_details.csv", details)
    write_rows(out_dir / "native_predictive_calibration.csv", calibration)
    plot_summary(out_dir / "native_selector_comparison.png", summary)
    write_markdown(out_dir / "native_selector_analysis.md", summary, calibration, joined, batch_csv)
    print(f"Wrote native selector analysis to {out_dir}")


if __name__ == "__main__":
    main()
