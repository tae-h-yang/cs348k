# Prospective Low-Root-Gated Native SONIC Run, 2026-05-16

## Question

Does adding an explicit upright root-height sanity gate fix the suspicious
`walk_stealth` failures and improve native SONIC execution, or were the earlier
videos only a rendering/conversion artifact?

## Protocol

- Base generated candidates: reused the same 640 qpos files from
  `data/prospective_native_selection/20260516_170132/`.
- New run directory:
  `results/prospective_native_selection/20260516_lowroot_gate/`.
- Candidate selectors: `baseline_k0`, `best_precontroller`,
  `lowest_id_risk`, and the updated `gated_precontroller`.
- New gate: for upright modes, reject candidates with `root_z_min < 0.60` or
  any `low_root_frames_pct > 0`; whole-body/low-posture categories are exempt.
- Native validation: 320/320 selected references were evaluated with native
  SONIC release in MuJoCo using interleaved selector order.
- Video convention: white/left is the exported MotionBricks reference;
  red/right is the SONIC-controlled robot under MuJoCo physics.

## Commands

```bash
python scripts/run_prospective_native_selection.py \
  --out_dir results/prospective_native_selection/20260516_lowroot_gate \
  --data_dir data/prospective_native_selection/20260516_170132 \
  --seed_start 7 --n_seeds 8 --K 8 \
  --modes injured_walk slow_walk stealth_walk walk walk_boxing walk_gun \
          walk_happy_dance walk_scared walk_stealth walk_zombie

python scripts/audit_sonic_reference_export.py \
  --prospective_dir results/prospective_native_selection/20260516_lowroot_gate

MUJOCO_GL=egl python scripts/run_sonic_native_release_batch.py \
  --reference_root results/prospective_native_selection/20260516_lowroot_gate/sonic_references \
  --strategy all --limit 320 --order interleaved \
  --out_dir results/prospective_native_selection/20260516_lowroot_gate/native_release \
  --max_hours 12 --width 640 --height 360 \
  --release_settle 1.0 --startup_timeout 90 --resume

python scripts/analyze_sonic_native_batch.py \
  --batch_dir results/prospective_native_selection/20260516_lowroot_gate/native_release

python scripts/analyze_prospective_native_selection.py \
  --prospective_dir results/prospective_native_selection/20260516_lowroot_gate \
  --batch_dir results/prospective_native_selection/20260516_lowroot_gate/native_release

python scripts/analyze_sonic_reference_sanity.py \
  --prospective_dir results/prospective_native_selection/20260516_lowroot_gate

python scripts/render_prospective_comparison_sheets.py \
  --prospective_dir results/prospective_native_selection/20260516_lowroot_gate

MUJOCO_GL=egl python scripts/render_existing_sonic_diagnostics.py \
  --batch_dir results/prospective_native_selection/20260516_lowroot_gate/native_release \
  --groups fail strict_pass --limit 20 --width 960 --height 540
```

## Results

Overall native batch:

- completed: 320/320
- survival: 295/320
- strict pass: 264/320
- mean joint RMSE: 0.145 rad

Selector summary:

| selector | strict pass | survival | mean RMSE | mean risk |
|---|---:|---:|---:|---:|
| baseline_k0 | 64/80 (80.0%) | 71/80 (88.8%) | 0.150 | 18.86 |
| best_precontroller | 62/80 (77.5%) | 74/80 (92.5%) | 0.144 | 2.18 |
| lowest_id_risk | 65/80 (81.2%) | 74/80 (92.5%) | 0.144 | 2.10 |
| gated_precontroller | 73/80 (91.2%) | 76/80 (95.0%) | 0.141 | 3.25 |
| native oracle over tested selectors | 80/80 (100.0%) | 80/80 (100.0%) | oracle | oracle |

Paired comparison against baseline:

| selector | changed candidates | strict delta | rescues | regressions | RMSE delta | risk delta |
|---|---:|---:|---:|---:|---:|---:|
| best_precontroller | 72/80 | -2 | 10 | 12 | -0.006 | -16.68 |
| lowest_id_risk | 64/80 | +1 | 10 | 9 | -0.006 | -16.76 |
| gated_precontroller | 71/80 | +9 | 14 | 5 | -0.010 | -15.61 |

Key stress-test mode:

- `walk_stealth` strict pass:
  - baseline: 3/8
  - best pre-controller: 3/8
  - lowest inverse-dynamics risk: 3/8
  - low-root gated pre-controller: 7/8
- This directly addresses the earlier suspicious low-root videos: the problem
  was not broad CSV/joint-order corruption. It was a real reference-sanity
  failure mode that an explicit upright root-height gate can mostly avoid.

Reference export audit:

- 320 references audited.
- max round-trip qpos error: `3.33e-16`.
- low-root exported references: 17/320, because baseline/best/lowest still
  include low-root choices; the updated `gated_precontroller` has zero selected
  low-root `walk_stealth` references.
- Joined outcome split: low-root references strict pass 3/17; non-low-root
  references strict pass 261/303.

## Review Artifacts

- Clean pointer folder: `results/current_validated/`
- Main report: `results/current_validated/prospective_native_analysis.md`
- Native summary: `results/current_validated/native_analysis_summary.md`
- Paired visual sheets: `results/current_validated/comparison_sheets/`
- Contact/camera-tracked diagnostics:
  `results/current_validated/diagnostic_contact_videos/`
- Diagnostic sheet:
  `results/current_validated/diagnostic_contact_sheet_first40.jpg`
- Strict-pass videos:
  `results/current_validated/strict_presentation_pass_videos/`
- Failure videos:
  `results/current_validated/fail_videos/`

## Interpretation

The defensible method is now stronger and narrower: a fixed MotionBricks
generator can be made more useful for G1-style upright motion data by applying
structured reference-sanity, contact/dynamics, and native-SONIC acceptance
gates. The most important new result is not a generic heuristic score; it is a
specific failure-mode fix. Low-root `walk_stealth` references were brittle, and
an explicit upright root-height gate improved that mode from 3/8 strict pass to
7/8 strict pass while improving the full held-out selector from 64/80 to 73/80.

The native release protocol still has measurable stochastic/repeat-run
variability. In this run, `best_precontroller` and `gated_precontroller` chose
the same candidate for 74/80 identities, and duplicate native rollouts disagreed
on strict pass for 20/74 same-candidate identities. The paired result is
therefore best phrased as an observed native-validation improvement under the
current protocol, not as proof that the low-root gate causally explains every
individual rescue. A paired binary test over rescues/regressions is suggestive
rather than overwhelming: 14 rescues versus 5 regressions is about McNemar
two-sided p=0.064, one-sided p=0.032.

Do not claim learned MotionBricks fine-tuning, arbitrary language-prompt
generation, hardware safety, or guaranteed physical motion generation.
