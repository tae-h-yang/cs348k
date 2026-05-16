#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ROOT="$ROOT/results/long_jobs/neural_critic_sweep"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="$RUN_ROOT/$STAMP"
LATEST="$RUN_ROOT/latest"

mkdir -p "$RUN_DIR/logs"
rm -f "$LATEST"
ln -s "$RUN_DIR" "$LATEST"

cd "$ROOT"

echo "=== Neural critic sweep ===" | tee "$RUN_DIR/sweep.log"
echo "start_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$RUN_DIR/sweep.log"
echo "run_dir=$RUN_DIR" | tee -a "$RUN_DIR/sweep.log"

for seed in 101 202 303; do
  OUT_DIR="$RUN_DIR/seed_${seed}"
  LOG="$RUN_DIR/logs/seed_${seed}.log"
  echo "=== seed $seed ===" | tee -a "$RUN_DIR/sweep.log"
  PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0 python scripts/train_neural_critic_clip_v2.py \
    --epochs 5000 \
    --width 512 \
    --batch 16 \
    --lr 1e-4 \
    --seed "$seed" \
    --out_dir "$OUT_DIR" \
    2>&1 | tee "$LOG"
done

python - <<'PY' > "$RUN_DIR/sweep_summary.md"
import json
from pathlib import Path

run_dir = Path("results/long_jobs/neural_critic_sweep/latest").resolve()
print("# Neural Critic Sweep Summary")
print()
for cfg in sorted(run_dir.glob("seed_*/config.json")):
    data = json.loads(cfg.read_text())
    print(f"## {cfg.parent.name}")
    for key in [
        "records", "train_records", "val_records", "epochs", "width",
        "n_params", "best_spearman_rho", "best_val_loss", "train_seconds",
    ]:
        print(f"- {key}: {data.get(key)}")
    print()
PY

echo "summary=$RUN_DIR/sweep_summary.md" | tee -a "$RUN_DIR/sweep.log"
echo "end_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$RUN_DIR/sweep.log"
echo "=== Sweep complete ===" | tee -a "$RUN_DIR/sweep.log"
