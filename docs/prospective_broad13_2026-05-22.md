# Broad 13-Mode Prospective Native SONIC Run, 2026-05-22

## Question

Does the current inference-time selector still help after expanding beyond the
original upright walking-style set to include idle and crawling/low-posture
negative controls?

## Protocol

- Run directory:
  `results/prospective_native_selection/20260522_broad13/`.
- Candidate pool: 832 generated MotionBricks candidates over 104
  mode/seed identities, with 8 samples per identity.
- Modes: idle, elbow crawling, hand crawling, and 10 upright walking/style
  modes.
- Selectors tested through native SONIC:
  `baseline_k0`, `best_precontroller`, `lowest_id_risk`, and
  `gated_precontroller`.
- Selected references: 405 total. The gated selector exports fewer than 104
  references because it rejects some low-root/invalid candidates.
- Native validation: 405/405 selected references were evaluated through the
  native SONIC release path in MuJoCo.
- Video convention: white/left is the exported MotionBricks reference;
  red/right is the SONIC-controlled robot under MuJoCo physics. Diagnostic
  videos add contact dots and a robot-tracking camera.

## Commands

```bash
python scripts/run_prospective_native_selection.py \
  --out_dir results/prospective_native_selection/20260522_broad13 \
  --seed_start 7 --n_seeds 8 --K 8 \
  --modes idle elbow_crawling hand_crawling injured_walk slow_walk stealth_walk \
          walk walk_boxing walk_gun walk_happy_dance walk_scared \
          walk_stealth walk_zombie

python scripts/audit_sonic_reference_export.py \
  --prospective_dir results/prospective_native_selection/20260522_broad13

MUJOCO_GL=egl python scripts/run_sonic_native_release_batch.py \
  --reference_root results/prospective_native_selection/20260522_broad13/sonic_references \
  --strategy all --limit 416 --order interleaved \
  --out_dir results/prospective_native_selection/20260522_broad13/native_release \
  --max_hours 6 --width 640 --height 360 \
  --release_settle 1.0 --startup_timeout 90 --resume

python scripts/analyze_sonic_native_batch.py \
  --batch_dir results/prospective_native_selection/20260522_broad13/native_release

python scripts/analyze_prospective_native_selection.py \
  --prospective_dir results/prospective_native_selection/20260522_broad13 \
  --batch_dir results/prospective_native_selection/20260522_broad13/native_release

python scripts/analyze_sonic_reference_sanity.py \
  --prospective_dir results/prospective_native_selection/20260522_broad13

python scripts/render_prospective_comparison_sheets.py \
  --prospective_dir results/prospective_native_selection/20260522_broad13 \
  --max_cases 80 --samples 5 --thumb_width 220

MUJOCO_GL=egl python scripts/render_existing_sonic_diagnostics.py \
  --batch_dir results/prospective_native_selection/20260522_broad13/native_release \
  --groups fail strict_pass --limit 24 \
  --width 960 --height 540 --fps 30 --align_mode initial

MUJOCO_GL=egl python scripts/render_existing_sonic_diagnostics.py \
  --batch_dir results/prospective_native_selection/20260522_broad13/native_release \
  --mode_filters walk_stealth walk_scared walk_zombie walk_happy_dance walk_boxing walk_gun \
  --groups fail strict_pass --limit 32 \
  --out_dir results/prospective_native_selection/20260522_broad13/native_release/diagnostic_contact_videos_stress_modes \
  --width 960 --height 540 --fps 30 --align_mode initial
```

## Results

Reference export audit:

- 405 references exported.
- max qpos round-trip absolute error: `3.33e-16`.
- low-root references: 67/405.

Selector summary:

| selector | selected | strict/selected | strict/identity | survive/selected | mean RMSE | mean risk |
|---|---:|---:|---:|---:|---:|---:|
| baseline_k0 | 104/104 | 70/104 (67.3%) | 70/104 (67.3%) | 79/104 (76.0%) | 0.175 | 39.24 |
| best_precontroller | 104/104 | 73/104 (70.2%) | 73/104 (70.2%) | 80/104 (76.9%) | 0.177 | 16.77 |
| lowest_id_risk | 104/104 | 72/104 (69.2%) | 72/104 (69.2%) | 80/104 (76.9%) | 0.166 | 15.55 |
| gated_precontroller | 93/104 | 78/93 (83.9%) | 78/104 (75.0%) | 82/93 (88.2%) | 0.152 | 4.36 |
| native oracle over tested selectors | 104/104 | 88/104 (84.6%) | 88/104 (84.6%) | 88/104 (84.6%) | oracle | oracle |

Paired comparison against baseline:

| selector | paired | changed candidates | strict delta | rescues | regressions | RMSE delta | risk delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| best_precontroller | 104 | 86 | +3 | 16 | 13 | +0.002 | -22.47 |
| lowest_id_risk | 104 | 83 | +2 | 15 | 13 | -0.009 | -23.69 |
| gated_precontroller | 93 | 75 | +8 | 16 | 8 | -0.007 | -20.47 |

Category summary:

| selector | category | strict | survive | n | frame-0 fails | mean RMSE |
|---|---|---:|---:|---:|---:|---:|
| baseline_k0 | idle | 7 | 8 | 8 | 0 | 0.116 |
| baseline_k0 | low-posture/crawling | 0 | 0 | 16 | 1 | 0.358 |
| baseline_k0 | upright | 63 | 71 | 80 | 6 | 0.144 |
| gated_precontroller | idle | 7 | 7 | 8 | 0 | 0.119 |
| gated_precontroller | low-posture/crawling | 0 | 0 | 5 | 0 | 0.397 |
| gated_precontroller | upright | 71 | 75 | 80 | 3 | 0.139 |

Feature calibration on native strict pass:

| feature | AUC |
|---|---:|
| p95 root force | 0.756 |
| precontroller score | 0.752 |
| contact artifact score | 0.741 |
| non-foot floor contact percentage | 0.741 |
| full risk | 0.737 |
| p95 torque-limit ratio | 0.719 |

Mode-level highlights:

- `walk_stealth`: baseline 3/8 strict, gated 7/8 strict.
- `walk_zombie`: baseline 5/8 strict, gated 7/8 strict, lowest-risk 8/8
  strict.
- `walk_scared`: baseline 5/8 strict, best pre-controller 8/8 strict, gated
  5/8 strict. This is a real selector tradeoff, not a universal win.
- `walk_boxing`: baseline 8/8 strict, gated 7/8 strict, best pre-controller
  5/8 strict. This is a regression mode and should appear in reviewer notes.
- `elbow_crawling` and `hand_crawling`: 0 strict passes for every tested
  selector family. These are negative controls for the current SONIC gate, not
  solved behaviors.

## Review Artifacts

- Main report:
  `results/prospective_native_selection/20260522_broad13/prospective_native_analysis.md`
- Native batch report:
  `results/prospective_native_selection/20260522_broad13/native_release/analysis_summary.md`
- Category and mode CSVs:
  `results/prospective_native_selection/20260522_broad13/prospective_native_by_category.csv`
  and `results/prospective_native_selection/20260522_broad13/prospective_native_by_mode.csv`
- Paired visual sheets:
  `results/prospective_native_selection/20260522_broad13/comparison_sheets/`
- Diagnostic videos with contact dots:
  `results/prospective_native_selection/20260522_broad13/native_release/diagnostic_contact_videos/`
- Stress-mode diagnostic videos:
  `results/prospective_native_selection/20260522_broad13/native_release/diagnostic_contact_videos_stress_modes/`
- Diagnostic sheets:
  `results/prospective_native_selection/20260522_broad13/native_release/diagnostic_contact_sheet_first40.jpg`
  and
  `results/prospective_native_selection/20260522_broad13/native_release/diagnostic_contact_sheet_stress_modes_first48.jpg`
- Clean local pointer hub:
  `results/current_validated/`

## Interpretation

The broad run supports a scoped claim: for upright G1-like MotionBricks
references, inference-time candidate curation plus root/contact/dynamics checks
improves native SONIC acceptance on a broader set than the original
walk-stealth-focused experiment. The strongest headline number is
`gated_precontroller`: 78/104 identity strict passes versus 70/104 for the
deterministic baseline, with 16 rescues and 8 regressions on paired evaluated
identities.

It does not support a claim that crawling or arbitrary low-posture whole-body
motion is solved. Crawling references fail under the current native SONIC
acceptance protocol even when pre-controller scores improve. That is useful
negative evidence: the gate can reject or expose out-of-distribution references,
but a different controller, retargeting setup, or generator adaptation is
needed for floor locomotion.

Do not claim MotionBricks fine-tuning, guaranteed physical generation, or
language-prompt semantic correctness. The evidence is controller-in-the-loop
curation of a fixed local MotionBricks mode interface, validated by native
SONIC rollout and visual diagnostics.
