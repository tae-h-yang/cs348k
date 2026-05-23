# Learned Acceptance Prospective SONIC Audit, 2026-05-23

## Question

Does the broad13 temporal qpos acceptance model improve native SONIC-selected
MotionBricks references when used prospectively, and do the resulting videos
survive frame-level visual audit?

## Protocol

- Candidate source:
  `results/prospective_native_selection/20260522_broad13/`.
- Learned scorer:
  `results/native_acceptance_model_20260523_broad13_long/`.
- Selection file:
  `results/prospective_native_selection/20260522_broad13/learned_acceptance_selector/ensemble_selection_all_candidates.csv`.
- Native rollout:
  `results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/`.
- Visual audit:
  `scripts/visual_audit_sonic_videos.py` reads every rendered MP4 frame,
  segments the red actual robot and white reference robot, and flags missing
  bodies, large visual separation, fallen-looking body aspect, and sudden visual
  jumps.

## Commands

```bash
python scripts/export_learned_acceptance_selection.py \
  --selection_csv results/prospective_native_selection/20260522_broad13/learned_acceptance_selector/ensemble_selection_all_candidates.csv \
  --out_dir results/prospective_native_selection/20260523_learned_acceptance_eval \
  --selector learned_acceptance

MUJOCO_GL=egl python scripts/run_sonic_native_release_batch.py \
  --reference_root results/prospective_native_selection/20260523_learned_acceptance_eval/sonic_references \
  --strategy all --limit 104 --order mode_interleaved \
  --out_dir results/prospective_native_selection/20260523_learned_acceptance_eval/native_release \
  --max_hours 6 --width 640 --height 360 \
  --release_settle 1.0 --startup_timeout 90 --resume

MUJOCO_GL=egl python scripts/render_existing_sonic_diagnostics.py \
  --batch_dir results/prospective_native_selection/20260523_learned_acceptance_eval/native_release \
  --all \
  --out_dir results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/diagnostic_contact_videos_all \
  --width 960 --height 540 --fps 30 --align_mode initial

python scripts/visual_audit_sonic_videos.py \
  --batch_dir results/prospective_native_selection/20260523_learned_acceptance_eval/native_release \
  --video_dir results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/diagnostic_contact_videos_all \
  --glob '*_diagnostic_contacts.mp4' \
  --out_dir results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/visual_frame_audit_tracked \
  --sheet_limit 80
```

## Native SONIC Results

| split | strict/native pass |
|---|---:|
| all 104 identities | 76/104 strict |
| upright identities | 68/80 strict, 74/80 survival |
| idle identities | 8/8 strict |
| crawling identities | 0/16 survival, 0/16 strict |

Per-mode strict pass:

| mode | strict |
|---|---:|
| idle | 8/8 |
| injured_walk | 6/8 |
| slow_walk | 8/8 |
| stealth_walk | 6/8 |
| walk | 4/8 |
| walk_boxing | 7/8 |
| walk_gun | 8/8 |
| walk_happy_dance | 7/8 |
| walk_scared | 8/8 |
| walk_stealth | 7/8 |
| walk_zombie | 7/8 |
| elbow_crawling | 0/8 |
| hand_crawling | 0/8 |

Comparison against the broad13 selector baselines:

| selector | all strict | upright strict | idle strict | crawling strict |
|---|---:|---:|---:|---:|
| deterministic baseline | 70/104 | 63/80 | 7/8 | 0/16 |
| hand-coded gated selector | 78/104 | 71/80 | 7/8 | 0/5 selected |
| learned acceptance selector | 76/104 | 68/80 | 8/8 | 0/16 |

The learned selector improves over deterministic baseline, but it does not beat
the hand-coded gated selector on this run. Its largest failure is that it still
selects every crawling identity even though native SONIC cannot execute those
references with the current controller/release protocol.

The learned rollout is also not a fully clean prospective split. It selects
from the same broad13 candidate pool used to train the acceptance model. Of the
104 learned selections, 46 had already been native-evaluated by the broad13
selector study and 58 were newly evaluated by this run:

| learned selection subset | strict | falls |
|---|---:|---:|
| already native-evaluated candidates | 39/46 | 3/46 |
| newly evaluated candidates | 37/58 | 19/58 |
| newly evaluated upright candidates | 36/42 | 6/42 |
| newly evaluated crawling candidates | 0/15 | 15/15 |

This makes the result useful, but not sufficient for a strong learned-selector
deployment claim.

## Learned-Score Abstention

`scripts/analyze_learned_acceptance_rollout.py` adds an abstention audit under
`results/prospective_native_selection/20260523_learned_acceptance_eval/audit/`.

| min learned score | accepted identities | strict | falls | crawling accepted |
|---:|---:|---:|---:|---:|
| 0.00 | 104 | 76/104 | 22 | 16 |
| 0.50 | 88 | 76/88 | 6 | 0 |
| 0.80 | 88 | 76/88 | 6 | 0 |
| 0.85 | 77 | 65/77 | 6 | 0 |
| 0.90 | 72 | 62/72 | 6 | 0 |

The useful behavior is abstention, not forced selection. A threshold near 0.5
removes the unsupported crawling identities and raises strict rate from 73.1%
to 86.4%, at the cost of covering only 88/104 identities.

## Frame-Level Visual Audit

Tracked-camera diagnostic videos were required because the original fixed-camera
videos create false alarms when the robot walks out of frame. On the tracked
diagnostic set:

| audit outcome | count |
|---|---:|
| videos analyzed | 104 |
| visual pass | 27 |
| visual warn | 61 |
| visual fail | 16 |
| strict native passes with visual fail flag | 1/76 |
| native fallen videos with visual pass flag | 2/22 |

The 16 visual failures are mostly crawling collapses plus a few upright
fall/large-separation cases. The one strict-pass visual contradiction is
`learned_acceptance_walk_boxing_seed14_cand1`; it should be excluded from any
presentation claim until manually reviewed.

Review artifacts:

- Full visual audit:
  `results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/visual_frame_audit_tracked/visual_frame_audit.md`
- Visual failure sheet:
  `results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/visual_frame_audit_tracked/visual_fail_contact_sheet.jpg`
- Strict-but-visual-fail sheet:
  `results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/visual_frame_audit_tracked/strict_but_visual_fail_contact_sheet.jpg`
- Reviewed presentation subset:
  `results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/visual_reviewed_presentation_videos/`

## Interpretation

The current strongest claim is:

> A learned trajectory-level native-acceptance model can predict SONIC
> executability better than scalar pre-controller metrics and, when used as a
> prospective selector, improves over deterministic MotionBricks baseline on
> upright/idle motions. Its most defensible use is abstention plus ranking
> within supported categories. It is not yet better than the best hand-coded
> gate, and it does not solve low-posture/crawling motions.

Do not claim:

- MotionBricks has been fine-tuned.
- The method generates guaranteed physically feasible motions.
- Crawling is solved.
- The learned selector is fully validated without a hard low-posture/category
  rejection gate.

## Next Fix

The next scientifically useful experiment is a hybrid selector:

1. hard-reject unsupported low-posture/crawling references for the current
   SONIC acceptance claim,
2. apply root-height/contact sanity gates,
3. rank remaining candidates by the learned native-acceptance ensemble,
4. run native SONIC and frame-level visual audit again.

That would test whether learned ranking adds value once known unsupported
classes are removed.
