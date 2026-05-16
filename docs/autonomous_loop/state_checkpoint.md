# State Checkpoint

Last updated: 2026-05-16.

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
  humanoid robotics prompts.

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

## Next Actions

1. Prepare a prospective held-out native-selection experiment where the selector
   chooses before native rollout.
2. Recalibrate thresholds for frame-0/root-height failures separately from
   mid-trajectory falls.
3. Build a human/VLM visual-review rubric over the native release videos.
4. Keep low-posture/crawling as rejected or separate-controller categories.
5. Investigate whether arbitrary-prompt generation can be accessed or whether
   the 100-prompt suite must be evaluated through another generator/control
   source.
