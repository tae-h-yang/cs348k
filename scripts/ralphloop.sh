#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOURS=12
K_AFTER=32
SONIC_PROVIDER="cuda"
MAX_SECONDS=5.0
RENDER_VIDEOS=1

usage() {
  cat <<'EOF'
Usage: bash scripts/ralphloop.sh [--hours 12] [--k-after 32] [--provider cuda|cpu] [--no-render]

RalphLoop is the long-run research supervisor for the Humanoid100 MotionBricks
curation project. It generates a larger best-of-K run, repairs references,
evaluates physical/contact metrics, runs the approximate SONIC bridge with
reference-pose initialization, renders review videos, and writes reviewer notes.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hours) HOURS="$2"; shift 2 ;;
    --k-after) K_AFTER="$2"; shift 2 ;;
    --provider) SONIC_PROVIDER="$2"; shift 2 ;;
    --no-render) RENDER_VIDEOS=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_ROOT="$ROOT/results/ralphloop"
RUN_DIR="$RUN_ROOT/$STAMP"
LATEST="$RUN_ROOT/latest"
LOG="$RUN_DIR/ralphloop.log"
STATUS="$RUN_DIR/status.md"
COMMANDS="$RUN_DIR/commands.sh"

MB_OUT="$RUN_DIR/humanoid100_motionbricks_k${K_AFTER}"
DATA_K="$ROOT/data/ralphloop_${STAMP}_humanoid100_k${K_AFTER}"
REPAIR_OUT="$RUN_DIR/humanoid100_repaired_k${K_AFTER}"
REPAIR_DATA="$ROOT/data/ralphloop_${STAMP}_repaired_k${K_AFTER}"
FINAL_OUT="$RUN_DIR/humanoid100_final_eval_k${K_AFTER}"

mkdir -p "$RUN_DIR"
rm -f "$LATEST"
ln -s "$RUN_DIR" "$LATEST"
touch "$COMMANDS"
chmod +x "$COMMANDS"

exec > >(tee -a "$LOG") 2>&1

export MUJOCO_GL="${MUJOCO_GL:-egl}"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
NVIDIA_LIB_PATHS="$(python "$ROOT"/scripts/python_nvidia_lib_paths.py)"
export LD_LIBRARY_PATH="$NVIDIA_LIB_PATHS:${LD_LIBRARY_PATH:-}"

deadline_epoch=$(( $(date +%s) + HOURS * 3600 ))

status() {
  local phase="$1"
  local message="$2"
  {
    echo "# RalphLoop Status"
    echo
    echo "- run_dir: \`$RUN_DIR\`"
    echo "- latest: \`$LATEST\`"
    echo "- phase: $phase"
    echo "- message: $message"
    echo "- updated_local: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "- deadline_local: $(date -d "@$deadline_epoch" '+%Y-%m-%d %H:%M:%S %Z')"
    echo "- k_after: $K_AFTER"
    echo "- sonic_provider: $SONIC_PROVIDER"
    echo
    echo "## Live Files"
    echo
    echo "- log: \`$LOG\`"
    echo "- commands: \`$COMMANDS\`"
    echo "- final_eval: \`$FINAL_OUT\`"
  } > "$STATUS"
  cp "$STATUS" "$RUN_ROOT/status_latest.md"
}

append_command() {
  printf '\n# %s\n%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$COMMANDS"
}

run_phase() {
  local name="$1"
  shift
  local cmd="$*"
  local now
  now="$(date +%s)"
  if (( now >= deadline_epoch )); then
    status "$name" "deadline reached before phase; stopping cleanly"
    echo "Deadline reached before $name"
    exit 124
  fi
  status "$name" "running"
  echo
  echo "=== $name ==="
  echo "$cmd"
  append_command "$cmd"
  local start
  start="$(date +%s)"
  local remaining=$((deadline_epoch - start))
  if (( remaining <= 0 )); then
    status "$name" "deadline reached at phase start"
    exit 124
  fi
  timeout "${remaining}s" bash -lc "$cmd"
  local end
  end="$(date +%s)"
  echo "=== $name complete in $((end - start))s ==="
  status "$name" "completed in $((end - start))s"
}

write_summary() {
  status "summary" "writing final summary"
  python - <<'PY'
import csv
import os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR"])
final_out = Path(os.environ["FINAL_OUT"])
summary_path = run_dir / "ralphloop_summary.md"
selector = final_out / "final_selector_initref" / "selector_summary.csv"

lines = [
    "# RalphLoop Summary",
    "",
    f"- run_dir: `{run_dir}`",
    f"- final_out: `{final_out}`",
    "",
]

if selector.exists():
    rows = list(csv.DictReader(selector.open()))
    keep = [
        "selector=K1_first",
        "selector=K8_best_of_8",
        "selector=repaired_retime",
        "selector=risk_verifier_best",
        "selector=sonic_verified_best",
    ]
    by = {r["group"]: r for r in rows}
    lines += [
        "## Selector Snapshot",
        "",
        "| Selector | Physical pass | No fall | Mean SONIC seconds | Mean RMSE |",
        "|---|---:|---:|---:|---:|",
    ]
    for key in keep:
        row = by.get(key)
        if not row:
            continue
        label = key.split("=", 1)[1]
        lines.append(
            f"| {label} | {row['physical_pass_count']}/100 | {row['sonic_no_fall_count']}/100 | "
            f"{float(row['mean_sonic_track_seconds']):.3f} | {float(row['mean_sonic_rmse']):.3f} |"
        )
else:
    lines += ["## Selector Snapshot", "", f"- Missing selector summary: `{selector}`"]

lines += [
    "",
    "## Video Artifacts",
    "",
    f"- before/after: `{final_out / 'before_after_overlay_videos'}`",
    f"- final selected: `{final_out / 'final_100_selected_overlay_videos'}`",
    f"- contact sheet: `{final_out / 'before_after_overlay_contact_sheet.jpg'}`",
    "",
    "## Reviewer Verdict",
    "",
    "Reviewer A/control: do not claim solved physical execution unless SONIC no-fall and tracking metrics support it.",
    "Reviewer B/motion generation: forced proxy rows are not semantic prompt successes.",
    "Reviewer C/reproducibility: use `commands.sh` and this run directory to regenerate artifacts.",
]
summary_path.write_text("\n".join(lines) + "\n")
print(summary_path)
PY
  cp "$RUN_DIR/ralphloop_summary.md" "$RUN_ROOT/summary_latest.md"
}

export RUN_DIR FINAL_OUT

status "init" "starting"
echo "=== RalphLoop ==="
echo "start_local=$(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "run_dir=$RUN_DIR"
echo "hours=$HOURS"
echo "k_after=$K_AFTER"
echo "provider=$SONIC_PROVIDER"
echo "mujoco_gl=$MUJOCO_GL"

run_phase "environment" "cd '$ROOT' && python - <<'PY'
import importlib.util
mods = ['torch', 'mujoco', 'cv2', 'onnxruntime', 'numpy', 'scipy']
for mod in mods:
    print(f'{mod}:', bool(importlib.util.find_spec(mod)))
try:
    import torch
    print('torch_cuda:', torch.cuda.is_available())
    if torch.cuda.is_available():
        print('gpu:', torch.cuda.get_device_name(0))
except Exception as exc:
    print('torch_error:', exc)
PY
nvidia-smi || true"

run_phase "tests" "cd '$ROOT' && PYTHONPATH=. pytest -q"

run_phase "generate_best_of_k${K_AFTER}" \
  "cd '$ROOT' && python scripts/run_humanoid100_motionbricks_experiment.py --limit 100 --k_after '$K_AFTER' --out_dir '$MB_OUT' --data_dir '$DATA_K'"

run_phase "repair_retime_smooth" \
  "cd '$ROOT' && python scripts/repair_humanoid100_references.py --input_csv '$MB_OUT/humanoid100_motionbricks_results.csv' --out_dir '$REPAIR_OUT' --data_dir '$REPAIR_DATA'"

run_phase "physical_contact_eval" \
  "cd '$ROOT' && python scripts/evaluate_humanoid100_final.py --motionbricks_csv '$MB_OUT/humanoid100_motionbricks_results.csv' --repair_csv '$REPAIR_OUT/repair_summary.csv' --out_dir '$FINAL_OUT'"

run_phase "export_sonic_references_all" \
  "cd '$ROOT' && python scripts/export_humanoid100_sonic_references.py --final_csv '$FINAL_OUT/final_metrics.csv' --out_dir '$FINAL_OUT/sonic_references_all' --all"

run_phase "approx_sonic_all_initref" \
  "cd '$ROOT' && python scripts/evaluate_sonic_policy_mujoco.py --reference_dir '$FINAL_OUT/sonic_references_all' --out_csv '$FINAL_OUT/sonic_all_initref_tracking.csv' --summary_csv '$FINAL_OUT/sonic_all_initref_summary.csv' --provider '$SONIC_PROVIDER' --max_seconds '$MAX_SECONDS' --init_reference_pose"

run_phase "selector" \
  "cd '$ROOT' && python scripts/select_humanoid100_final_method.py --metrics_csv '$FINAL_OUT/final_metrics.csv' --sonic_csv '$FINAL_OUT/sonic_all_initref_tracking.csv' --out_dir '$FINAL_OUT/final_selector_initref'"

if [[ "$RENDER_VIDEOS" == "1" ]]; then
  run_phase "save_selected_rollouts" \
    "cd '$ROOT' && python scripts/evaluate_sonic_policy_mujoco.py --reference_dir '$FINAL_OUT/sonic_references_all' --out_csv '$FINAL_OUT/selected_initref_tracking.csv' --summary_csv '$FINAL_OUT/selected_initref_summary.csv' --provider '$SONIC_PROVIDER' --max_seconds '$MAX_SECONDS' --init_reference_pose --save_rollouts_dir '$FINAL_OUT/final_100_selected_rollouts' --only_save_names --save_names \$(python - <<'PY'
import csv
rows=[r for r in csv.DictReader(open('$FINAL_OUT/final_selector_initref/selected_methods.csv')) if r['selector']=='sonic_verified_best']
print(' '.join(r['selected_reference'] for r in rows))
PY
)"

  run_phase "save_k1_rollouts" \
    "cd '$ROOT' && python scripts/evaluate_sonic_policy_mujoco.py --reference_dir '$FINAL_OUT/sonic_references_all' --out_csv '$FINAL_OUT/k1_initref_tracking.csv' --summary_csv '$FINAL_OUT/k1_initref_summary.csv' --provider '$SONIC_PROVIDER' --max_seconds '$MAX_SECONDS' --init_reference_pose --save_rollouts_dir '$FINAL_OUT/final_100_selected_rollouts' --only_save_names --save_names \$(python - <<'PY'
import csv
rows=[r for r in csv.DictReader(open('$FINAL_OUT/final_selector_initref/selected_methods.csv')) if r['selector']=='K1_first']
print(' '.join(r['selected_reference'] for r in rows))
PY
)"

  run_phase "render_final_selected_overlays" \
    "cd '$ROOT' && python scripts/render_selected_overlay_videos.py --selected_csv '$FINAL_OUT/final_selector_initref/selected_methods.csv' --selector sonic_verified_best --rollout_dir '$FINAL_OUT/final_100_selected_rollouts' --out_dir '$FINAL_OUT/final_100_selected_overlay_videos' --index_csv '$FINAL_OUT/final_100_selected_overlay_videos.csv' --width 640 --height 480"

  run_phase "render_k1_baseline_overlays" \
    "cd '$ROOT' && python scripts/render_selected_overlay_videos.py --selected_csv '$FINAL_OUT/final_selector_initref/selected_methods.csv' --selector K1_first --rollout_dir '$FINAL_OUT/final_100_selected_rollouts' --out_dir '$FINAL_OUT/k1_baseline_overlay_videos' --index_csv '$FINAL_OUT/k1_baseline_overlay_videos.csv' --width 640 --height 480"

  run_phase "stitch_before_after" \
    "cd '$ROOT' && python scripts/stitch_humanoid100_before_after_videos.py --baseline_index '$FINAL_OUT/k1_baseline_overlay_videos.csv' --final_index '$FINAL_OUT/final_100_selected_overlay_videos.csv' --out_dir '$FINAL_OUT/before_after_overlay_videos' --out_index '$FINAL_OUT/before_after_overlay_videos.csv'"

  run_phase "contact_sheets" \
    "cd '$ROOT' && python scripts/make_humanoid100_video_contact_sheet.py --index_csv '$FINAL_OUT/before_after_overlay_videos.csv' --out '$FINAL_OUT/before_after_overlay_contact_sheet.jpg' --cols 5 --thumb_width 320 && python scripts/make_humanoid100_video_contact_sheet.py --index_csv '$FINAL_OUT/final_100_selected_overlay_videos.csv' --video_column video_path --out '$FINAL_OUT/final_100_selected_overlay_contact_sheet.jpg' --cols 5 --thumb_width 240"
fi

write_summary
status "complete" "finished"
echo "end_local=$(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "summary=$RUN_DIR/ralphloop_summary.md"
