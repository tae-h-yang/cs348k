#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ROOT="$ROOT/results/longrun"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="$RUN_ROOT/$STAMP"
LATEST="$RUN_ROOT/latest"
LOG="$RUN_DIR/longrun.log"
export RUN_DIR

mkdir -p "$RUN_DIR"
rm -f "$LATEST"
ln -s "$RUN_DIR" "$LATEST"

exec > >(tee -a "$LOG") 2>&1

echo "=== Motion curation long run ==="
echo "start_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "root=$ROOT"
echo "run_dir=$RUN_DIR"

cd "$ROOT"

echo
echo "=== Environment ==="
python - <<'PY'
import importlib.util
mods = ["torch", "mujoco", "cv2", "onnxruntime", "imageio", "PIL"]
for mod in mods:
    print(f"{mod}: {bool(importlib.util.find_spec(mod))}")
try:
    import torch
    print("torch_cuda:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("gpu:", torch.cuda.get_device_name(0))
except Exception as exc:
    print("torch_check_error:", exc)
PY
nvidia-smi || true

echo
echo "=== Step 1: rebuild prompt and current evidence tables ==="
python scripts/build_humanoid_robotics_prompt_suite.py
python scripts/evaluate_motionspec.py
python scripts/build_candidate_evidence_table.py
python scripts/plot_motionspec_dashboard.py
python scripts/plot_combined_selector.py
python scripts/select_visual_audit_clips.py
python scripts/render_visual_audit_contact_sheet.py

echo
echo "=== Step 2: expanded full candidate audit (all exposed MotionBricks modes) ==="
python scripts/full_candidate_audit.py \
  --modes idle walk slow_walk stealth_walk injured_walk walk_zombie walk_stealth walk_boxing walk_happy_dance walk_gun walk_scared hand_crawling elbow_crawling \
  --seeds 7 \
  --K 8

echo
echo "=== Step 3: train larger clip critic on expanded labels ==="
python scripts/train_neural_critic_clip_v2.py \
  --epochs 2000 \
  --batch 24 \
  --width 256 \
  --out_dir "$RUN_DIR/neural_critic_clip_v2_2000"

echo
echo "=== Step 4: rebuild evidence after expanded labels/training ==="
python scripts/evaluate_motionspec.py
python scripts/build_candidate_evidence_table.py
python scripts/plot_motionspec_dashboard.py
python scripts/plot_combined_selector.py
python scripts/select_visual_audit_clips.py
python scripts/render_visual_audit_contact_sheet.py

echo
echo "=== Step 5: collect summary ==="
python - <<'PY' > "$RUN_DIR/run_summary.md"
import csv, json
import os
from pathlib import Path

root = Path.cwd()
print("# Long Run Summary")
print()
print("## Key Files")
for path in [
    "results/candidate_audit.csv",
    "results/candidate_audit_summary.csv",
    "results/candidate_evidence_table.csv",
    "results/combined_selector_comparison.csv",
    "results/combined_selector_dashboard.png",
    "results/visual_audit_manifest.csv",
    "results/visual_audit_contact_sheet.png",
]:
    p = root / path
    print(f"- `{path}`: {'exists' if p.exists() else 'missing'}")

print()
print("## Combined Selector")
p = root / "results/combined_selector_comparison.csv"
if p.exists():
    rows = list(csv.DictReader(open(p)))
    for r in rows:
        print(
            f"- {r['selector']}: combined={float(r['mean_combined_score']):.3f}, "
            f"semantic={float(r['mean_semantic_score']):.3f}, "
            f"risk={float(r['mean_full_risk']):.2f}, "
            f"sonic={float(r['mean_sonic_track_seconds']):.3f}s"
        )

print()
print("## Neural Critic")
cfg = Path(os.environ["RUN_DIR"]) / "neural_critic_clip_v2_2000" / "config.json"
if cfg.exists():
    data = json.loads(cfg.read_text())
    for key in ["records", "train_records", "val_records", "epochs", "width", "n_params", "best_spearman_rho", "best_val_loss", "train_seconds"]:
        print(f"- {key}: {data.get(key)}")
else:
    print("- config missing")
PY

echo "summary=$RUN_DIR/run_summary.md"
echo "end_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== Long run complete ==="
