#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$(readlink -f "$ROOT/results/ralphloop/latest")"
K_AFTER="${1:-512}"
LOG="$RUN_DIR/resume_k${K_AFTER}.log"
STATUS="$RUN_DIR/status.md"
MB_OUT="$RUN_DIR/humanoid100_motionbricks_k${K_AFTER}"
DATA_K="$ROOT/data/ralphloop_$(basename "$RUN_DIR")_humanoid100_k${K_AFTER}"
REPAIR_OUT="$RUN_DIR/humanoid100_repaired_k${K_AFTER}"
REPAIR_DATA="$ROOT/data/ralphloop_$(basename "$RUN_DIR")_repaired_k${K_AFTER}"
FINAL_OUT="$RUN_DIR/humanoid100_final_eval_k${K_AFTER}"
export RUN_DIR FINAL_OUT

export MUJOCO_GL="${MUJOCO_GL:-egl}"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
NVIDIA_LIB_PATHS="$(python "$ROOT"/scripts/python_nvidia_lib_paths.py)"
export LD_LIBRARY_PATH="$NVIDIA_LIB_PATHS:${LD_LIBRARY_PATH:-}"

exec > >(tee -a "$LOG") 2>&1

status() {
  {
    echo "# RalphLoop Status"
    echo
    echo "- run_dir: \`$RUN_DIR\`"
    echo "- latest: \`$ROOT/results/ralphloop/latest\`"
    echo "- phase: $1"
    echo "- message: $2"
    echo "- updated_local: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "- deadline_local: manual resume"
    echo "- k_after: $K_AFTER"
    echo "- sonic_provider: cuda"
    echo
    echo "## Live Files"
    echo
    echo "- log: \`$LOG\`"
    echo "- final_eval: \`$FINAL_OUT\`"
  } > "$STATUS"
  cp "$STATUS" "$ROOT/results/ralphloop/status_latest.md"
}

run_phase() {
  local name="$1"
  shift
  status "$name" running
  echo
  echo "=== $name ==="
  echo "$*"
  bash -lc "$*"
  status "$name" complete
}

cd "$ROOT"
status resume_start "resuming K=$K_AFTER"

run_phase generate_best_of_k${K_AFTER}_resume \
  "python scripts/run_humanoid100_motionbricks_experiment.py --limit 100 --k_after '$K_AFTER' --out_dir '$MB_OUT' --data_dir '$DATA_K'"

run_phase repair_retime_smooth \
  "python scripts/repair_humanoid100_references.py --input_csv '$MB_OUT/humanoid100_motionbricks_results.csv' --out_dir '$REPAIR_OUT' --data_dir '$REPAIR_DATA'"

run_phase physical_contact_eval \
  "python scripts/evaluate_humanoid100_final.py --motionbricks_csv '$MB_OUT/humanoid100_motionbricks_results.csv' --repair_csv '$REPAIR_OUT/repair_summary.csv' --out_dir '$FINAL_OUT'"

run_phase export_sonic_references_all \
  "python scripts/export_humanoid100_sonic_references.py --final_csv '$FINAL_OUT/final_metrics.csv' --out_dir '$FINAL_OUT/sonic_references_all' --all"

run_phase approx_sonic_all_initref \
  "python scripts/evaluate_sonic_policy_mujoco.py --reference_dir '$FINAL_OUT/sonic_references_all' --out_csv '$FINAL_OUT/sonic_all_initref_tracking.csv' --summary_csv '$FINAL_OUT/sonic_all_initref_summary.csv' --provider cuda --max_seconds 5.0 --init_reference_pose"

run_phase selector \
  "python scripts/select_humanoid100_final_method.py --metrics_csv '$FINAL_OUT/final_metrics.csv' --sonic_csv '$FINAL_OUT/sonic_all_initref_tracking.csv' --out_dir '$FINAL_OUT/final_selector_initref'"

python - <<'PY'
import csv
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR"])
final_out = Path(os.environ["FINAL_OUT"])
summary_path = run_dir / "ralphloop_summary.md"
selector = final_out / "final_selector_initref" / "selector_summary.csv"
lines = ["# RalphLoop Resume Summary", "", f"- run_dir: `{run_dir}`", f"- final_out: `{final_out}`", ""]
if selector.exists():
    rows = list(csv.DictReader(selector.open()))
    by = {r["group"]: r for r in rows}
    lines += ["| Selector | Physical pass | No fall | Mean SONIC seconds | Mean RMSE |", "|---|---:|---:|---:|---:|"]
    for key in ["selector=K1_first", "selector=K8_best_of_8", "selector=repaired_retime", "selector=risk_verifier_best", "selector=sonic_verified_best"]:
        r = by.get(key)
        if r:
            lines.append(f"| {key.split('=',1)[1]} | {r['physical_pass_count']}/100 | {r['sonic_no_fall_count']}/100 | {float(r['mean_sonic_track_seconds']):.3f} | {float(r['mean_sonic_rmse']):.3f} |")
summary_path.write_text("\\n".join(lines) + "\\n")
print(summary_path)
PY

status complete "resume finished"
