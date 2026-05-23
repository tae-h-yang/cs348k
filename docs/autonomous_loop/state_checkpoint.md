# State Checkpoint

Last updated: 2026-05-23.

## Current Project Spine

Controller-in-the-loop curation of humanoid robot motion data:

1. define distinct robotics motion intents,
2. generate candidate kinematic references,
3. evaluate prompt/task predicates with MotionSpec,
4. evaluate physics/contact/dynamics,
5. evaluate controller tracking where possible,
6. select candidates and render visible evidence.

## Current Tracked Inputs

- `configs/prompt_suite_105.csv`: executable local suite, 15 MotionBricks modes
  x 7 seeds.
- `configs/humanoid_robotics_100_prompts.csv`: target benchmark, 100 distinct
  humanoid robotics prompts across dynamic locomotion, dance/expressive,
  floor/low-posture, manipulation, loco-manipulation, balance, safety,
  terrain, and athletic stress-test categories. This is no longer a walking
  style suite.

## Current Tracked Scripts

- `scripts/build_prompt_suite.py`: rebuilds the old 105 mode-seed suite.
- `scripts/build_humanoid_robotics_prompt_suite.py`: rebuilds the new 100
  distinct-prompt benchmark.
- `scripts/evaluate_prompt_alignment.py`: proxy task-alignment evaluator.
- `scripts/evaluate_contact_quality.py`: contact artifact evaluator.
- `scripts/evaluate_motionspec.py`: current MotionSpec predicate evaluator and
  selector comparison.
- `scripts/plot_motionspec_dashboard.py`: plots selector and failure-count
  summaries from MotionSpec outputs.
- `scripts/build_candidate_evidence_table.py`: joins MotionSpec, contact,
  inverse-dynamics, and approximate SONIC metrics into one candidate table.
- `scripts/analyze_native_sonic_selector.py`: joins native SONIC release
  outcomes with candidate evidence, compares selectors, and writes predictive
  calibration tables.
- `scripts/build_native_visual_audit_manifest.py`: selects native SONIC videos
  for human/VLM review and writes rubric columns for stability/reference/style
  judgments.
- `scripts/run_prospective_native_selection.py`: generates held-out
  MotionBricks candidate pools, scores candidates before controller rollout, and
  exports selector-specific SONIC references.
- `scripts/analyze_prospective_native_selection.py`: joins prospective selector
  choices with native SONIC outcomes and reports paired rescue/regression
  counts plus feature calibration.
- `scripts/render_prospective_comparison_sheets.py`: renders paired baseline vs
  selector contact sheets for rescues, regressions, and both-failed cases.
- `scripts/render_existing_sonic_diagnostics.py`: rerenders saved native SONIC
  logs with camera tracking and contact markers; does not rerun the controller.
- `scripts/visual_audit_sonic_videos.py`: reads diagnostic MP4 pixels frame by
  frame, segments red actual robot plus white reference robot, and flags visual
  failures/warnings for human review.
- `scripts/audit_sonic_reference_export.py`: verifies MotionBricks qpos to
  SONIC CSV export round-trip and reports root-height sanity metrics.
- `scripts/analyze_sonic_reference_sanity.py`: joins export/root-height sanity
  metrics with native SONIC rollout outcomes.
- `scripts/train_native_sonic_acceptance.py`: trains a temporal qpos model to
  predict native SONIC strict acceptance from controller-labeled rollouts.
- `scripts/export_learned_acceptance_selection.py`: exports learned-selector
  all-candidate choices to SONIC reference CSVs for prospective native rollout.
- `scripts/analyze_learned_acceptance_rollout.py`: audits learned rollout
  prior-evaluated versus newly evaluated splits, score-threshold abstention,
  and same-pool hybrid diagnostics.
- `scripts/plot_combined_selector.py`: plots combined selector tradeoffs.
- `scripts/select_visual_audit_clips.py`: selects inspectable best, worst, and
  disagreement clips.
- `scripts/render_visual_audit_contact_sheet.py`: renders start/middle/end frame
  contact sheets for visual sanity checks.
- `scripts/evaluate_sonic_policy_mujoco.py`: approximate SONIC policy bridge.

## Current Generated Outputs

Generated outputs live under ignored `results/`:

- `results/motionspec_predicates.csv`
- `results/motionspec_summary.csv`
- `results/motionspec_selector_comparison.csv`
- `results/motionspec_selector_dashboard.png`
- `results/motionspec_failure_counts.csv`
- `results/motionspec_failure_counts.png`
- `results/candidate_evidence_table.csv`
- `results/combined_selector_comparison.csv`
- `results/combined_selector_dashboard.png`
- `results/visual_audit_manifest.csv`
- `results/visual_audit_contact_sheet.png`
- `results/prompt_alignment.csv`
- `results/contact_quality.csv`
- `results/sonic_policy_mujoco_tracking_210_fixed.csv`
- `results/sonic_native_release_overnight/20260516_085134/native_selector_analysis.md`
- `results/sonic_native_release_overnight/20260516_085134/native_visual_audit_manifest.csv`
- `results/sonic_native_release_all210/20260516_123519/analysis_summary.md`
- `results/sonic_native_release_all210/20260516_123519/native_selector_analysis.md`
- `results/sonic_native_release_all210/20260516_123519/native_visual_audit_manifest.csv`
- `results/prospective_native_selection/20260516_170132/prospective_native_analysis.md`
- `results/prospective_native_selection/20260516_170132/comparison_sheets/`
- `results/prospective_native_selection/20260516_170132/native_release/diagnostic_contact_videos/`
- `results/prospective_native_selection/20260516_170132/sonic_reference_sanity_summary.csv`
- `results/prospective_native_selection/20260516_170132/sonic_reference_sanity_worst.csv`
- `results/prospective_native_selection/20260516_lowroot_gate/prospective_native_analysis.md`
- `results/prospective_native_selection/20260516_lowroot_gate/native_release/analysis_summary.md`
- `results/prospective_native_selection/20260516_lowroot_gate/comparison_sheets/`
- `results/prospective_native_selection/20260516_lowroot_gate/native_release/diagnostic_contact_videos/`
- `results/current_validated/` local pointer hub for the latest usable results

## Latest Numeric Snapshot

Existing 105 paired K=1/K=8 identities:

| Selector | Mean MotionSpec | Mean Prompt Proxy | Mean Contact Artifact | Mean Approx. SONIC Survival |
|---|---:|---:|---:|---:|
| K=1 baseline | 0.686 | 0.583 | 0.274 | 2.005 s |
| Existing K=8 ID selector | 0.736 | 0.568 | 0.248 | 2.054 s |
| MotionSpec over K=1/K=8 | 0.757 | 0.620 | 0.250 | 2.117 s |
| SONIC oracle over K=1/K=8 | 0.721 | 0.576 | 0.263 | 2.299 s |

Combined selector snapshot:

| Selector | Combined | Semantic | ID Risk | Approx. SONIC Survival |
|---|---:|---:|---:|---:|
| K=1 baseline | 0.577 | 0.650 | 35.32 | 2.005 s |
| K=8 existing | 0.640 | 0.677 | 13.58 | 2.054 s |
| MotionSpec selector | 0.643 | 0.706 | 17.74 | 2.114 s |
| No-controller combined | 0.649 | 0.694 | 13.74 | 2.098 s |
| Controller combined | 0.653 | 0.697 | 14.17 | 2.148 s |
| SONIC oracle | 0.624 | 0.670 | 24.03 | 2.299 s |

Interpretation: MotionSpec curation is promising for selecting between already
generated candidates. Approximate SONIC survival is still short, so this is not
yet a physically executable motion-generation result.

Visual audit snapshot: `results/visual_audit_contact_sheet.png` makes the worst
whole-body/crawling failures obvious. Several high-risk crawling clips collapse
or lie on the ground despite numeric selector improvements elsewhere.

Long-run snapshot:

- 728 candidate clips over 91 identities were generated/scored.
- 12 visual-audit MP4s were rendered under `results/videos/visual_audit/`.
- Neural critic sweep completed two width-512 seeds: best rho 0.797 and 0.759.
- Result: learned heuristic-risk imitation remains a negative/secondary path.

Native SONIC release-validation snapshot:

- Official/native deployment and MuJoCo logging work through
  `scripts/render_sonic_actual_sim_examples.py`.
- The old no-release native videos only validate deployment/visualization; they
  do not validate free-standing physical tracking.
- With `--release_before_play`, upright MotionBricks references can track:
  11/12 curated upright candidates survived full clip in
  `results/sonic_native_release_20260516_curated_batch/`.
- The expanded strict-gate set reached 14/16 upright candidates surviving full
  clip, mean joint RMSE 0.139 rad. The clean pass folder is
  `results/sonic_native_release_20260516_strict_pass/`.
- The broad 100-attempt native-release run completed in
  `results/sonic_native_release_overnight/20260516_085134/`: 84/100 overall
  pass, 76/84 upright pass, 66/84 strict upright pass, 8/8 idle pass, and 0/8
  crawling pass.
- Native selector calibration on the same 100-run batch shows that K=8
  inverse-dynamics screening is not the final method: across 25 paired K=1/K=8
  identities, K=1 strict pass is 20/25, K=8 strict pass is 16/25, and the
  native oracle upper bound is 22/25. Pre-controller metrics are moderately
  predictive of native survival, but not enough to replace native SONIC rollout.
- Crawling remains a negative control: 0/2 crawling candidates survived in the
  curated release batch.
- Clean presentable pass videos are copied to
  `results/sonic_native_release_20260516_curated_pass/`.
- All 210 exposed K=1/K=8 references have now been evaluated through native
  SONIC under `results/sonic_native_release_all210/20260516_123519/`: 164/210
  overall pass, 152/168 upright pass, 136/168 strict upright pass, and 0/28
  crawling pass. Across all 105 paired identities, K=1 strict pass is 72/105,
  K=8 inverse-dynamics-screened strict pass is 74/105, and the native oracle
  upper bound is 85/105. Contact score is the strongest scalar predictor of
  native survival in this batch (AUC 0.812).
- Initial prospective held-out native-selection run completed under
  `results/prospective_native_selection/20260516_170132/`: 640 generated
  candidates, 80 upright identities, and 320 native SONIC rollouts. Baseline
  strict pass is 64/80, best pre-controller strict pass is 67/80, lowest
  inverse-dynamics-risk strict pass is 66/80, and the native oracle over tested
  selectors is 78/80. This supports cheap screening plus native acceptance
  gating, not heuristic-only certification. Feature calibration on selected
  rows is weak: best scalar AUC is contact artifact score at 0.561. This run is
  superseded for final claims by the low-root-gated rerun below.
- Follow-up audit: white/left in current SONIC actual-qpos videos is the
  exported MotionBricks reference and red/right is the actual SONIC-controlled
  robot. Export round-trip is exact to numerical precision across all 320
  references (`3.33e-16` max absolute error), so suspicious red failures are
  actual robot/physics failures in those videos, not reference CSV corruption.
  23/320 references, mostly `walk_stealth`, have root height below 0.60m and
  need a separate low-root gate. Joining the reference audit to native outcomes
  shows 7/23 low-root references pass strictly versus 257/297 non-low-root
  references, confirming that low-root posture is a measurable execution
  quality issue.
- Low-root-gated prospective rerun:
  `results/prospective_native_selection/20260516_lowroot_gate/` completed
  320/320 native SONIC rollouts. Baseline strict pass is 64/80,
  `best_precontroller` is 62/80, `lowest_id_risk` is 65/80, and updated
  `gated_precontroller` is 73/80. Against baseline, gated gives +9 strict
  passes, 14 rescues, and 5 regressions. The stress-test `walk_stealth` mode
  improves from 3/8 strict for baseline to 7/8 for gated. There is still
  measurable native repeat-run variability: best/gated selected the same
  candidate for 74/80 identities, and duplicate rollouts disagreed on strict
  pass for 20/74 of those same-candidate identities.
- Learned native-acceptance model:
  `results/native_acceptance_model_20260522_long/` trained a 5-fold temporal
  qpos CNN on the low-root-gated native rollout labels. Cross-validated AUC is
  0.769 and average precision is 0.921, versus scalar gates between 0.492 and
  0.620 AUC. This is promising triage evidence, not a replacement for native
  SONIC rollout or a learned motion generator.
- Broad 13-mode prospective run:
  `results/prospective_native_selection/20260522_broad13/` generated 832
  candidates over 104 identities and exported 405 SONIC references. Export
  audit reports 405 references with max round-trip qpos error `3.33e-16` and
  67 low-root references. Native SONIC evaluation completed 405/405 selected
  references. `gated_precontroller` reaches 78/104 identity strict passes
  versus 70/104 for deterministic baseline, with 16 rescues and 8 regressions
  over 93 paired gated identities. The native oracle over tested selectors is
  88/104. Category split for gated: idle 7/8 strict, upright 71/80 strict, and
  crawling 0/5 strict. The complete report is
  `docs/prospective_broad13_2026-05-22.md`.
- Broad13 learned native-acceptance model:
  `results/native_acceptance_model_20260523_broad13_long/` trained for 6000
  epochs per fold over 405 native rollout labels and 104 grouped identities.
  Cross-validated AUC is 0.864 and average precision is 0.917, beating the best
  scalar baseline (`root_z_min`, AUC 0.782). The report is
  `docs/native_acceptance_broad13_2026-05-23.md`. This is a prospective selector
  candidate, not a generator or certification method. Retrospective
  evaluated-only learned selection reaches 77/104 strict passes, close to the
  hand-coded gated selector's 78/104, while the all-candidate learned selection
  chooses 58/104 not-yet-native-evaluated candidates. The next hard test is a
  new native rollout of learned-selected candidates.
- Prospective learned-selector native rollout:
  `results/prospective_native_selection/20260523_learned_acceptance_eval/`
  exported and evaluated the learned ensemble's 104 all-candidate choices.
  Native SONIC completed 104/104 references. Learned selection reaches 76/104
  identity strict passes, 68/80 upright strict, 8/8 idle strict, and 0/16
  crawling survival. This beats deterministic baseline (70/104, 63/80 upright)
  but does not beat the hand-coded gated selector (78/104, 71/80 upright).
  The split is partly same-pool: 46 learned selections had already been
  native-evaluated and 58 were newly evaluated; the newly evaluated subset is
  37/58 strict, mostly because newly evaluated crawling is 0/15. Learned-score
  abstention at 0.5 accepts 88/104 identities, removes crawling, and keeps all
  76 strict passes.
  Tracked-camera frame audit over all 104 diagnostic MP4s reports 27 visual
  passes, 61 warnings, 16 visual failures, and 1 strict native pass with a
  visual-fail flag. Reviewed videos are under
  `results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/visual_reviewed_presentation_videos/`.

## Next Actions

1. Recalibrate thresholds for frame-0/root-height failures separately from
   mid-trajectory falls.
2. Build a human/VLM visual-review rubric over the native release videos.
3. Keep low-posture/crawling as rejected or separate-controller categories.
4. Investigate whether arbitrary-prompt generation can be accessed or whether
   the 100-prompt suite must be evaluated through another generator/control
   source.
5. If rerunning prospective native selection, use `--order mode_interleaved` so
   partial results are not selector-block or mode-block biased.
6. Human-review the broad13 diagnostic videos and choose final presentation
   clips from `results/current_validated/`.
7. Treat crawling/low-posture as a separate unsolved controller/generator
   problem, not as part of the current upright acceptance claim.
8. Build and test a hybrid learned selector: hard-reject unsupported
   low-posture/crawling for the current claim, apply root/contact sanity gates,
   then rank remaining candidates by the learned native-acceptance ensemble.
