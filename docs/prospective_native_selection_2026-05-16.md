# Prospective Native SONIC Selection, 2026-05-16

## Question

Can a fixed MotionBricks generator be made more useful for humanoid robot motion
data by sampling multiple candidates, ranking them with cheap contact/dynamics
checks, and then using native SONIC as the acceptance gate?

This run is a prospective selector test: all candidate scoring happened before
native SONIC rollout.

## Protocol

Generated candidate pool:

- run directory:
  `results/prospective_native_selection/20260516_170132/`
- qpos directory:
  `data/prospective_native_selection/20260516_170132/`
- 10 exposed upright MotionBricks modes:
  `injured_walk`, `slow_walk`, `stealth_walk`, `walk`, `walk_boxing`,
  `walk_gun`, `walk_happy_dance`, `walk_scared`, `walk_stealth`,
  `walk_zombie`
- 8 held-out seeds per mode: seeds 7-14
- 8 candidates per identity, for 640 generated candidates over 80 identities
- 4 exported selector references per identity, for 320 native SONIC rollouts

Selectors:

- `baseline_k0`: deterministic candidate 0.
- `lowest_id_risk`: lowest MuJoCo inverse-dynamics risk.
- `best_precontroller`: weighted pre-controller score using contact artifact,
  inverse-dynamics risk, torque-limit ratio, and root force.
- `gated_precontroller`: same selected candidates as `best_precontroller` in
  this run because 622/640 candidates passed the loose gate; treat it as a
  duplicate repeat trial, not an independent method.

Native gate:

- native SONIC release protocol in MuJoCo.
- survival is root-height fall detection from the native rollout logs.
- strict pass is survival plus `mean_joint_rmse <= 0.20` and
  `mean_root_xy_error <= 1.5 m`.

## Commands

```bash
python scripts/run_prospective_native_selection.py \
  --out_dir results/prospective_native_selection/20260516_170132 \
  --data_dir data/prospective_native_selection/20260516_170132 \
  --seed_start 7 --n_seeds 8 --K 8

python scripts/run_sonic_native_release_batch.py \
  --reference_root results/prospective_native_selection/20260516_170132/sonic_references \
  --strategy all --limit 320 \
  --out_dir results/prospective_native_selection/20260516_170132/native_release \
  --max_hours 12 --width 640 --height 360 \
  --release_settle 1.0 --startup_timeout 90 --resume

python scripts/analyze_sonic_native_batch.py \
  --batch_dir results/prospective_native_selection/20260516_170132/native_release

python scripts/analyze_prospective_native_selection.py \
  --prospective_dir results/prospective_native_selection/20260516_170132 \
  --batch_dir results/prospective_native_selection/20260516_170132/native_release

python scripts/render_prospective_comparison_sheets.py \
  --prospective_dir results/prospective_native_selection/20260516_170132
```

For future partial/long runs, use `--order interleaved` in
`run_sonic_native_release_batch.py`; this run used sorted order and therefore
partial results were baseline-heavy until the full 320 rollouts completed.

## Results

Overall native batch:

- completed: 320/320
- survival: 300/320
- strict pass: 264/320
- mean joint RMSE: 0.143 rad
- no idle or crawling motions were included in this prospective upright run

Selector summary:

| selector | strict pass | survival | mean RMSE | mean risk |
|---|---:|---:|---:|---:|
| baseline_k0 | 64/80 (80.0%) | 73/80 (91.2%) | 0.146 | 18.86 |
| best_precontroller | 67/80 (83.8%) | 75/80 (93.8%) | 0.142 | 2.18 |
| gated_precontroller | 67/80 (83.8%) | 75/80 (93.8%) | 0.143 | 2.18 |
| lowest_id_risk | 66/80 (82.5%) | 77/80 (96.2%) | 0.140 | 2.10 |
| native oracle over tested selectors | 78/80 (97.5%) | 80/80 (100.0%) | oracle | oracle |

Paired comparison against baseline:

| selector | changed candidates | strict delta | rescues | regressions | mean RMSE delta | mean risk delta |
|---|---:|---:|---:|---:|---:|---:|
| best_precontroller | 72/80 | +3 | 13 | 10 | -0.003 | -16.68 |
| gated_precontroller | 72/80 | +3 | 12 | 9 | -0.003 | -16.68 |
| lowest_id_risk | 64/80 | +2 | 12 | 10 | -0.005 | -16.76 |

Feature calibration over the 320 selected-rollout rows is weak:

- `contact_artifact_score` is the best scalar feature, but only AUC 0.561 for
  native strict pass.
- `precontroller_score` AUC is 0.527.
- `full_risk` AUC is 0.523.

Interpretation: cheap contact/dynamics scoring is useful for reducing obvious
risk and slightly improving strict pass rate, but it is not reliable enough to
certify execution. Native SONIC must remain the acceptance gate.

## Visual Artifacts

Key generated artifacts:

- `prospective_native_analysis.md`: final selector tables.
- `native_release/analysis_summary.md`: native batch summary and failure list.
- `comparison_sheets/rescued_paired_sheet.jpg`: paired baseline-vs-selected
  rescues.
- `comparison_sheets/regressed_paired_sheet.jpg`: paired regressions.
- `comparison_sheets/both_failed_paired_sheet.jpg`: cases neither baseline nor
  selected candidate fixed.
- `native_release/strict_presentation_pass_contact_sheet.jpg`: diverse strict
  pass sample.
- `native_release/fail_contact_sheet.jpg`: native failures.
- `native_release/pass_rate_by_mode.png`: mode-level pass rates.

Visual audit notes:

- Strong fall-to-pass rescues include `walk_boxing_seed10`,
  `walk_happy_dance_seed11`, `walk_scared_seed14`, and `walk_zombie_seed13`.
- Some rescues are strict-threshold rescues rather than dramatic visual
  corrections; keep them separate from fall-to-pass examples in slides.
- Regressions are real and visible, especially `walk_stealth` and selected
  expressive clips with poor initial posture or high RMSE.

## Limitations

- This is not MotionBricks fine-tuning. The generator is fixed.
- This is not arbitrary text-to-motion. The local MotionBricks interface exposes
  discrete G1 modes, and this run used 10 upright/walking-style modes.
- This run excludes crawling and manipulation. Prior native runs showed crawling
  is a negative control for the current SONIC release setup.
- The native release protocol has repeat-run variability: `best_precontroller`
  and `gated_precontroller` selected identical candidates, but 16/80 duplicate
  pairs disagreed on strict pass and 8/80 disagreed on fall status.
- Cheap physics/contact metrics are not a substitute for controller rollout.

## Defensible Claim

The strongest claim is:

> For upright MotionBricks G1 references, inference-time candidate curation with
> contact/dynamics features gives a modest strict-pass improvement over the
> deterministic baseline, but the large improvement comes from keeping native
> SONIC as an acceptance gate: at least one tested candidate passes strictly for
> 78/80 identities.

Do not claim guaranteed physical generation, arbitrary prompt coverage, or
hardware safety.
