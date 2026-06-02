#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID="$(date +%Y%m%d_%H%M%S)"
OUT="$ROOT/results/dual_track/$RUN_ID"
LATEST="$ROOT/results/dual_track/latest"
KIMODO_REPO="$ROOT/../kimodo"
VENV="$ROOT/.venv/kimodo"
HOURS="${DUAL_TRACK_HOURS:-12}"
END_EPOCH="$(python - <<PY
import time
print(int(time.time() + float("$HOURS") * 3600))
PY
)"

mkdir -p "$OUT"
if [[ -L "$LATEST" || -f "$LATEST" ]]; then
  rm -f "$LATEST"
elif [[ -d "$LATEST" ]]; then
  mv "$LATEST" "$ROOT/results/dual_track/manual_latest_before_${RUN_ID}"
fi
ln -s "$OUT" "$LATEST"

CUDA_LIBS="$(python "$ROOT/scripts/python_nvidia_lib_paths.py" 2>/dev/null || true)"
if [[ -n "$CUDA_LIBS" ]]; then
  export LD_LIBRARY_PATH="$CUDA_LIBS:${LD_LIBRARY_PATH:-}"
fi

log() {
  local line
  line="[$(date '+%Y-%m-%d %H:%M:%S %Z')] $*"
  printf '%s\n' "$line" >> "$OUT/dual_track.log"
  printf '%s\n' "$line"
}

has_hf_token() {
  python - <<'PY'
from pathlib import Path
paths = [Path.home()/".cache/huggingface/token", Path.home()/".huggingface/token"]
print("yes" if any(p.exists() and p.read_text().strip() for p in paths) else "no")
PY
}

write_status() {
  cat > "$OUT/status.md" <<EOF
# Dual-Track Loop Status

- run_dir: \`$OUT\`
- phase: \`$1\`
- message: $2
- updated_local: $(date '+%Y-%m-%d %H:%M:%S %Z')
- planned_hours: $HOURS
- kimodo_repo: \`$KIMODO_REPO\`
- latest_report: \`$LATEST/dual_track_status.md\`
EOF
}

log "starting dual-track loop"
write_status "start" "initializing MotionBricks/Kimodo split"

if [[ ! -d "$KIMODO_REPO/.git" ]]; then
  log "cloning Kimodo"
  git clone https://github.com/nv-tlabs/kimodo "$KIMODO_REPO" 2>&1 | tee -a "$OUT/dual_track.log"
else
  log "Kimodo repo already present"
fi

log "writing current MotionBricks/Kimodo report"
python "$ROOT/scripts/analyze_dual_track_motion_generation.py" 2>&1 | tee -a "$OUT/dual_track.log"

if [[ ! -x "$VENV/bin/python" ]]; then
  log "creating isolated Kimodo venv with system packages"
  python -m venv --system-site-packages "$VENV" 2>&1 | tee -a "$OUT/dual_track.log"
fi

log "installing/updating Kimodo package in isolated venv"
"$VENV/bin/python" -m pip install --upgrade pip 2>&1 | tee -a "$OUT/dual_track.log"
"$VENV/bin/python" -m pip install -e "$KIMODO_REPO" 2>&1 | tee -a "$OUT/dual_track.log" || {
  write_status "kimodo_install_failed" "Kimodo pip install failed; inspect dual_track.log"
  exit 1
}

log "checking Kimodo CLI"
"$VENV/bin/kimodo_gen" --help > "$OUT/kimodo_gen_help.txt" 2>&1 || true

while [[ "$(date +%s)" -lt "$END_EPOCH" ]]; do
  log "refreshing status report"
  python "$ROOT/scripts/analyze_dual_track_motion_generation.py" 2>&1 | tee -a "$OUT/dual_track.log"

  if [[ "$(has_hf_token)" == "yes" ]]; then
    log "HF token found; attempting resumable Kimodo G1 Humanoid100 generation"
    export TEXT_ENCODER_DEVICE=cpu
    "$ROOT/scripts/run_kimodo_humanoid100_experiment.py" \
      --out_dir "$OUT/kimodo_humanoid100_g1" \
      --data_dir "$ROOT/data/kimodo_humanoid100_g1" \
      --kimodo_bin "$VENV/bin/kimodo_gen" \
      --limit 100 \
      --duration 4.0 \
      --diffusion_steps 50 \
      --max_runtime_s 41400 \
      > "$OUT/kimodo_humanoid100_generation.log" 2>&1
    "$ROOT/scripts/evaluate_kimodo_humanoid100.py" \
      --manifest "$OUT/kimodo_humanoid100_g1/manifest.csv" \
      --out_dir "$OUT/kimodo_humanoid100_eval" \
      --export_sonic_refs \
      > "$OUT/kimodo_humanoid100_eval.log" 2>&1 || true
    if [[ -d "$OUT/kimodo_humanoid100_eval/sonic_references" ]]; then
      log "running approximate SONIC bridge on Kimodo refs with full video/rollout export"
      "$ROOT/scripts/evaluate_sonic_policy_mujoco.py" \
        --reference_dir "$OUT/kimodo_humanoid100_eval/sonic_references" \
        --out_csv "$OUT/kimodo_humanoid100_eval/sonic_tracking.csv" \
        --summary_csv "$OUT/kimodo_humanoid100_eval/sonic_summary.csv" \
        --provider cuda \
        --max_seconds 5.0 \
        --init_reference_pose \
        --save_rollouts_dir "$OUT/kimodo_humanoid100_eval/sonic_rollouts" \
        --video_dir "$OUT/kimodo_humanoid100_eval/sonic_videos" \
        > "$OUT/kimodo_humanoid100_sonic.log" 2>&1 || true
    fi
    break
  else
    log "HF token missing; Kimodo generation blocked by gated text encoder. Waiting and continuing report refresh."
  fi

  write_status "waiting_or_retrying" "MotionBricks report refreshed; Kimodo generation waits for token or successful smoke run"
  sleep 1800
done

python "$ROOT/scripts/analyze_dual_track_motion_generation.py" 2>&1 | tee -a "$OUT/dual_track.log"
write_status "complete" "dual-track loop completed or Kimodo smoke generation reached"
log "dual-track loop finished"
