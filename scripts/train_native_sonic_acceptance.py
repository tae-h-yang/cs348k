"""Train a qpos-to-native-SONIC acceptance model.

This is deliberately different from the heuristic-risk neural critic. Labels
come from native SONIC rollouts (`batch_summary.csv`), so the model tests
whether a learned reference-only predictor can anticipate actual controller
acceptance better than hand scalar gates.

The script uses group cross-validation by `(mode, seed)` identity to avoid
training and validating on duplicate selector reruns of the same identity.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import average_precision_score, roc_auc_score
from torch.utils.data import DataLoader, Dataset


ROOT = Path(__file__).resolve().parents[1]
QPOS_DIM = 36
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def as_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def strict_pass(native_row: dict[str, str]) -> bool:
    return (
        native_row.get("fell") == "False"
        and as_float(native_row, "mean_joint_rmse", 999.0) <= 0.20
        and as_float(native_row, "mean_root_xy_error", 999.0) <= 1.5
    )


def identity_from_selected(row: dict[str, str]) -> str:
    return f"{row['mode']}::seed{row['seed_idx']}"


@dataclass(frozen=True)
class NativeRecord:
    key: str
    identity: str
    selector: str
    path: Path
    label: int
    candidate_k: int
    mode: str
    seed_idx: int
    scalars: dict[str, float]


def collect_records(prospective_dir: Path, batch_dir: Path) -> list[NativeRecord]:
    selected = {row["selected_motion"]: row for row in read_rows(prospective_dir / "prospective_selected.csv")}
    native = {row["motion"]: row for row in read_rows(batch_dir / "batch_summary.csv") if row.get("status") == "completed"}
    records: list[NativeRecord] = []
    for motion, sel in selected.items():
        nat = native.get(motion)
        if not nat:
            continue
        path = Path(sel["path"])
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            continue
        scalars = {
            "full_risk": as_float(sel, "full_risk"),
            "contact_artifact_score": as_float(sel, "contact_artifact_score"),
            "precontroller_score": as_float(sel, "precontroller_score"),
            "p95_torque_limit_ratio": as_float(sel, "p95_torque_limit_ratio"),
            "p95_root_force_N": as_float(sel, "p95_root_force_N"),
            "root_z_min": as_float(sel, "root_z_min"),
            "low_root_frames_pct": as_float(sel, "low_root_frames_pct"),
        }
        records.append(
            NativeRecord(
                key=motion,
                identity=identity_from_selected(sel),
                selector=sel["selector"],
                path=path,
                label=1 if strict_pass(nat) else 0,
                candidate_k=int(float(sel["candidate_k"])),
                mode=sel["mode"],
                seed_idx=int(float(sel["seed_idx"])),
                scalars=scalars,
            )
        )
    return records


class NativeDataset(Dataset):
    def __init__(self, records: list[NativeRecord], augment: bool):
        self.records = records
        self.augment = augment

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int):
        rec = self.records[idx]
        qpos = np.load(rec.path).astype(np.float32)
        qpos = normalize_qpos(qpos)
        if self.augment and len(qpos) > 96:
            if random.random() < 0.35:
                crop = random.randint(max(96, len(qpos) // 2), len(qpos))
                start = random.randint(0, len(qpos) - crop)
                qpos = qpos[start:start + crop]
            if random.random() < 0.50:
                qpos = qpos.copy()
                qpos[:, :3] += np.random.normal(0.0, 0.002, size=qpos[:, :3].shape).astype(np.float32)
                qpos[:, 7:] += np.random.normal(0.0, 0.001, size=qpos[:, 7:].shape).astype(np.float32)
        return torch.from_numpy(qpos).T, torch.tensor(rec.label, dtype=torch.float32), rec.key


def normalize_qpos(qpos: np.ndarray) -> np.ndarray:
    out = qpos.copy()
    out[:, :2] -= out[0:1, :2]
    quat_norm = np.linalg.norm(out[:, 3:7], axis=1, keepdims=True)
    quat_norm = np.maximum(quat_norm, 1e-8)
    out[:, 3:7] /= quat_norm
    return out


def collate(batch):
    xs, ys, keys = zip(*batch)
    max_t = max(x.shape[1] for x in xs)
    padded = torch.zeros(len(xs), QPOS_DIM, max_t)
    mask = torch.zeros(len(xs), max_t, dtype=torch.bool)
    for i, x in enumerate(xs):
        t = x.shape[1]
        padded[i, :, :t] = x
        mask[i, :t] = True
    return padded, mask, torch.stack(ys), list(keys)


class ResidualBlock(nn.Module):
    def __init__(self, channels: int, dilation: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(channels, channels, kernel_size=5, padding=2 * dilation, dilation=dilation),
            nn.GroupNorm(8, channels),
            nn.GELU(),
            nn.Conv1d(channels, channels, kernel_size=5, padding=2 * dilation, dilation=dilation),
            nn.GroupNorm(8, channels),
        )
        self.act = nn.GELU()

    def forward(self, x):
        return self.act(x + self.net(x))


class AttentionPool(nn.Module):
    def __init__(self, channels: int):
        super().__init__()
        self.score = nn.Conv1d(channels, 1, kernel_size=1)

    def forward(self, x, mask):
        logits = self.score(x).squeeze(1)
        mask = mask[:, :logits.shape[1]]
        logits = logits.masked_fill(~mask, -1e9)
        weights = torch.softmax(logits, dim=1).unsqueeze(1)
        return torch.sum(x * weights, dim=2)


class NativeAcceptanceNet(nn.Module):
    def __init__(self, width: int):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv1d(QPOS_DIM, width, kernel_size=7, padding=3),
            nn.GroupNorm(8, width),
            nn.GELU(),
        )
        self.blocks = nn.Sequential(
            ResidualBlock(width, 1),
            ResidualBlock(width, 2),
            ResidualBlock(width, 4),
            ResidualBlock(width, 8),
        )
        self.pool = AttentionPool(width)
        self.head = nn.Sequential(
            nn.Linear(width, width // 2),
            nn.GELU(),
            nn.Dropout(0.20),
            nn.Linear(width // 2, 1),
        )

    def forward(self, x, mask):
        z = self.blocks(self.stem(x))
        return self.head(self.pool(z, mask)).squeeze(-1)


def split_folds(records: list[NativeRecord], n_folds: int, seed: int) -> list[tuple[list[NativeRecord], list[NativeRecord]]]:
    identities = sorted({rec.identity for rec in records})
    rng = random.Random(seed)
    rng.shuffle(identities)
    folds = [set(identities[i::n_folds]) for i in range(n_folds)]
    out = []
    for val_ids in folds:
        train = [rec for rec in records if rec.identity not in val_ids]
        val = [rec for rec in records if rec.identity in val_ids]
        out.append((train, val))
    return out


def metric_auc(labels: list[int], scores: list[float]) -> float:
    if len(set(labels)) < 2:
        return float("nan")
    return float(roc_auc_score(labels, scores))


def train_one_fold(train_records: list[NativeRecord], val_records: list[NativeRecord], args, fold: int):
    train_loader = DataLoader(NativeDataset(train_records, augment=True), batch_size=args.batch, shuffle=True, collate_fn=collate)
    val_loader = DataLoader(NativeDataset(val_records, augment=False), batch_size=args.batch, shuffle=False, collate_fn=collate)
    model = NativeAcceptanceNet(args.width).to(DEVICE)
    pos = sum(rec.label for rec in train_records)
    neg = len(train_records) - pos
    pos_weight = torch.tensor([neg / max(pos, 1)], device=DEVICE)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    best_auc = -1.0
    best_rows: list[dict[str, object]] = []
    log_rows = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        loss_sum = 0.0
        for x, mask, y, _ in train_loader:
            x, mask, y = x.to(DEVICE), mask.to(DEVICE), y.to(DEVICE)
            opt.zero_grad()
            loss = loss_fn(model(x, mask), y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            loss_sum += float(loss.item()) * len(x)
        sched.step()
        labels, scores, rows, val_loss = evaluate_model(model, val_loader, loss_fn)
        auc = metric_auc(labels, scores)
        ap = float(average_precision_score(labels, scores)) if len(set(labels)) > 1 else float("nan")
        log_rows.append({"fold": fold, "epoch": epoch, "train_loss": loss_sum / max(len(train_records), 1), "val_loss": val_loss, "auc": auc, "average_precision": ap})
        if np.isfinite(auc) and auc > best_auc:
            best_auc = auc
            best_rows = rows
        if epoch == 1 or epoch % args.log_every == 0:
            print(f"fold {fold} epoch {epoch:4d} train={log_rows[-1]['train_loss']:.4f} val={val_loss:.4f} auc={auc:.3f} ap={ap:.3f}")
    return log_rows, best_rows


def evaluate_model(model, loader, loss_fn):
    model.eval()
    labels: list[int] = []
    scores: list[float] = []
    rows: list[dict[str, object]] = []
    loss_sum = 0.0
    with torch.no_grad():
        for x, mask, y, keys in loader:
            x, mask, y = x.to(DEVICE), mask.to(DEVICE), y.to(DEVICE)
            logits = model(x, mask)
            loss_sum += float(loss_fn(logits, y).item()) * len(x)
            probs = torch.sigmoid(logits).cpu().numpy()
            ys = y.cpu().numpy()
            for key, label, score in zip(keys, ys, probs):
                labels.append(int(label))
                scores.append(float(score))
                rows.append({"key": key, "label": int(label), "pred_accept_prob": float(score)})
    return labels, scores, rows, loss_sum / max(len(loader.dataset), 1)


def scalar_baselines(records: list[NativeRecord]) -> list[dict[str, object]]:
    labels = [rec.label for rec in records]
    features = [
        ("precontroller_score", 1.0),
        ("full_risk", -1.0),
        ("contact_artifact_score", -1.0),
        ("p95_torque_limit_ratio", -1.0),
        ("root_z_min", 1.0),
        ("low_root_frames_pct", -1.0),
    ]
    out = []
    for name, sign in features:
        scores = [sign * rec.scalars[name] for rec in records]
        out.append({
            "model": f"scalar:{name}",
            "rows": len(records),
            "positives": sum(labels),
            "auc": metric_auc(labels, scores),
            "average_precision": float(average_precision_score(labels, scores)) if len(set(labels)) > 1 else float("nan"),
        })
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
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


def write_report(out_dir: Path, summary: dict[str, object], baselines: list[dict[str, object]]) -> None:
    lines = [
        "# Native SONIC Acceptance Model",
        "",
        f"- device: {summary['device']}",
        f"- records: {summary['records']}",
        f"- identities: {summary['identities']}",
        f"- strict positives: {summary['positives']}",
        f"- folds: {summary['folds']}",
        f"- epochs per fold: {summary['epochs']}",
        f"- neural cross-val AUC: {summary['neural_auc']:.3f}",
        f"- neural average precision: {summary['neural_average_precision']:.3f}",
        "",
        "## Scalar Baselines",
        "",
        "| model | AUC | average precision |",
        "|---|---:|---:|",
    ]
    for row in baselines:
        lines.append(f"| `{row['model']}` | {float(row['auc']):.3f} | {float(row['average_precision']):.3f} |")
    lines.extend([
        "",
        "Interpretation: this is an analysis model for native-SONIC acceptance, not a",
        "new motion generator. Because same-candidate duplicate native rollouts can",
        "disagree, this model should be treated as a noisy acceptance predictor.",
        "",
    ])
    (out_dir / "native_acceptance_model.md").write_text("\n".join(lines))


def plot_training(out_dir: Path, logs: list[dict[str, object]]) -> None:
    if not logs:
        return
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for fold in sorted({int(row["fold"]) for row in logs}):
        rows = [row for row in logs if int(row["fold"]) == fold]
        ax.plot([int(r["epoch"]) for r in rows], [float(r["auc"]) for r in rows], label=f"fold {fold}")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Validation AUC")
    ax.set_title("Native SONIC Acceptance Model")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "training_auc.png", dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prospective_dir", type=Path, default=ROOT / "results" / "prospective_native_selection" / "20260516_lowroot_gate")
    parser.add_argument("--batch_dir", type=Path, default=ROOT / "results" / "prospective_native_selection" / "20260516_lowroot_gate" / "native_release")
    parser.add_argument("--out_dir", type=Path, default=ROOT / "results" / "native_acceptance_model")
    parser.add_argument("--epochs", type=int, default=600)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--batch", type=int, default=24)
    parser.add_argument("--width", type=int, default=192)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--log_every", type=int, default=50)
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    records = collect_records(args.prospective_dir, args.batch_dir)
    if len(records) < args.folds:
        raise ValueError(f"Not enough records for {args.folds} folds: {len(records)}")
    print(f"Device: {DEVICE}")
    print(f"Records: {len(records)}; identities: {len({r.identity for r in records})}; positives: {sum(r.label for r in records)}")
    start = time.time()

    all_logs: list[dict[str, object]] = []
    all_preds: list[dict[str, object]] = []
    for fold, (train_records, val_records) in enumerate(split_folds(records, args.folds, args.seed), start=1):
        print(f"=== fold {fold}/{args.folds}: train={len(train_records)} val={len(val_records)} ===")
        logs, preds = train_one_fold(train_records, val_records, args, fold)
        all_logs.extend(logs)
        for row in preds:
            row["fold"] = fold
        all_preds.extend(preds)

    labels = [int(row["label"]) for row in all_preds]
    scores = [float(row["pred_accept_prob"]) for row in all_preds]
    baselines = scalar_baselines(records)
    summary = {
        "device": DEVICE,
        "records": len(records),
        "identities": len({r.identity for r in records}),
        "positives": sum(r.label for r in records),
        "folds": args.folds,
        "epochs": args.epochs,
        "width": args.width,
        "train_seconds": time.time() - start,
        "neural_auc": metric_auc(labels, scores),
        "neural_average_precision": float(average_precision_score(labels, scores)) if len(set(labels)) > 1 else float("nan"),
    }
    write_csv(args.out_dir / "train_log.csv", all_logs)
    write_csv(args.out_dir / "crossval_predictions.csv", all_preds)
    write_csv(args.out_dir / "scalar_baselines.csv", baselines)
    (args.out_dir / "config.json").write_text(json.dumps(summary, indent=2))
    write_report(args.out_dir, summary, baselines)
    plot_training(args.out_dir, all_logs)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
