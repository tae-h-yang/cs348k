# State Checkpoint

Last updated: 2026-05-30.

## Current Project Spine

Controller-in-the-loop curation of humanoid robot motion data:

1. define distinct robotics motion intents,
2. generate candidate kinematic references,
3. evaluate prompt/task predicates with MotionSpec,
4. evaluate physics/contact/dynamics,
5. evaluate controller tracking where possible,
6. select candidates and render visible evidence.

## Current Truthful Headline

The best current result is a MotionBricks best-of-K verifier/selector, not a
fine-tuned generator: targeted K1024 native SONIC selection reaches 100/100
reference-aware no-fall and projected 84/100 strict tracking on the 100-prompt
Humanoid100 suite. The repeat-conservative native table is 100/100
reference-aware no-fall and 74/100 strict tracking. Do not claim 100/100 strict
or 100/100 semantic success.

The remaining 16 failures are concentrated in floor/low-posture and acrobatic
stress prompts. Retiming/smoothing, root angular-velocity correction, and a
partial upright-safe projection probe added 0 strict rescues. The next
scientifically credible direction is contact/state-conditioned retargeting or
training a tracker/generator for non-foot support contacts.

New experimental execution-refinement result: controller-manifold projection
exports the native SONIC executed qpos as a new reference and reruns the native
tracker. Iterations 1-4 rescue 10/16 remaining hard prompts and yield 100/100
reference-aware no-fall plus 94/100 strict tracking. This is not
prompt-preserving by itself; it is evidence for a refinement/projection method
that must be paired with semantic/style audit.

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
- `scripts/select_hybrid_acceptance_candidates.py`: builds a hard-gated
  learned-score queue, with optional SONIC reference export.
- `scripts/plot_combined_selector.py`: plots combined selector tradeoffs.
- `scripts/select_visual_audit_clips.py`: selects inspectable best, worst, and
  disagreement clips.
- `scripts/render_visual_audit_contact_sheet.py`: renders start/middle/end frame
  contact sheets for visual sanity checks.
- `scripts/evaluate_sonic_policy_mujoco.py`: approximate SONIC policy bridge.
  It now supports `--init_reference_pose` and records initial qpos/qvel audit
  arrays in saved rollout NPZs.
- `scripts/render_selected_overlay_videos.py`: renders saved approximate SONIC
  rollouts as solid MuJoCo robot plus red translucent reference ghost.
- `scripts/stitch_humanoid100_before_after_videos.py`: creates all-100
  side-by-side K=1 baseline versus selected-result videos.
- `scripts/make_humanoid100_video_contact_sheet.py`: creates visual contact
  sheets from rendered MP4 indexes.
- `scripts/analyze_dual_track_motion_generation.py`: harvests completed
  MotionBricks RalphLoop sweeps and writes the active MotionBricks/Kimodo
  dual-track report.
- `scripts/dual_track_kimodo_motionbricks_loop.sh`: long-running monitor that
  refreshes MotionBricks evidence and, when Hugging Face access is available,
  runs Kimodo-G1 Humanoid100 generation, physical evaluation, SONIC reference
  export, and approximate SONIC rollouts/videos.
- `scripts/run_kimodo_humanoid100_experiment.py`: resumable Kimodo-G1 runner
  for the 100-prompt suite with `(T, 36)` qpos validation and blocked/failed
  manifest reporting.
- `scripts/evaluate_kimodo_humanoid100.py`: applies the same inverse-dynamics
  and contact verifier to Kimodo qpos exports, with optional SONIC reference
  export.
- `scripts/convert_kimodo_g1_examples.py`: converts bundled official
  Kimodo-G1 demo NPZ files to `(T, 36)` MuJoCo qpos for local verifier and
  SONIC sanity checks.
- `scripts/analyze_targeted_native_rescue.py`: scores targeted native SONIC
  retry batches against the current all-100 selection table.
- `scripts/generate_retimed_sonic_references.py`: creates retimed/smoothed
  diagnostic references for hard native failures.
- `scripts/generate_angvel_corrected_sonic_references.py`: copies selected
  SONIC references and recomputes body angular velocity from body quaternions.
- `scripts/generate_upright_safe_sonic_references.py`: creates diagnostic
  upright-projected references for probing root/contact failure modes.
- `scripts/generate_sonic_projected_references.py`: extracts actual native
  SONIC MuJoCo rollout qpos and exports it as a controller-projected reference.

## Current Generated Outputs

Generated outputs live under ignored `results/`:

- `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/final_100_native_selection_ref_aware_k1024_targeted.csv`:
  best current all-100 native selection table. Headline with caveat: 100/100
  reference-aware no-fall and projected 84/100 strict tracking.
- `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/nonstrict_k1024_native_sonic/`:
  K1024 targeted retry videos/metrics for the 26 previously non-strict prompts.
- `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/retimed_nonstrict_native_sonic/`:
  96 retimed/smoothed variants for the 16 remaining hard prompts; 0/16 strict
  rescues.
- `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/angvel_corrected_native_sonic/`:
  16 angular-velocity-corrected native SONIC videos/metrics; 0/16 strict
  rescues.
- `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/sonic_projected_native_sonic/`:
  16 controller-projected native SONIC videos/metrics; 8/16 strict rescues.
- `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/sonic_projected_iter2_native_sonic/`,
  `sonic_projected_iter3_native_sonic/`, and
  `sonic_projected_iter4_native_sonic/`: iterative controller-projection
  batches; iterations 2-3 add two strict rescues and iteration 4 saturates.
- `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/final_100_native_selection_ref_aware_k1024_projected_iter4.csv`:
  experimental controller-projection table; 100/100 reference-aware no-fall and
  94/100 strict tracking.
- `results/humanoid100_final_eval/`: current final 100-prompt proxy evaluation
  package. Contains `final_metrics.csv`, `summary.csv`, physical-risk plots,
  approximate SONIC tracking over supported and all proxy references, and the
  final selector package.
- `results/humanoid100_final_eval/before_after_overlay_videos/`: newest all-100
  video review folder. Contains 100 side-by-side MP4s. Left panel is K=1
  MotionBricks baseline; right panel is the selected verifier/repair result.
  Red translucent robot is the reference ghost and solid robot is the
  MuJoCo/SONIC physics rollout.
- `results/humanoid100_final_eval/final_100_selected_overlay_videos/`: 100
  final selected MP4s, one per Humanoid100 prompt.
- `results/humanoid100_final_eval/k1_baseline_overlay_videos/`: 100 baseline
  K=1 MP4s, one per Humanoid100 prompt.
- `results/humanoid100_final_eval/before_after_overlay_contact_sheet.jpg` and
  `results/humanoid100_final_eval/final_100_selected_overlay_contact_sheet.jpg`:
  quick visual indexes for all 100 prompts.
- `results/humanoid100_final_eval/final_selector/`: current best inspection
  folder. Contains `selected_methods.csv`, `selector_summary.csv`,
  `final_selector_summary.png`, `representative_contact_sheet.jpg`, and
  27 representative SONIC rollout MP4s under `representative_videos/`.
- `results/dual_track/latest/`: active MotionBricks/Kimodo status report.
  Contains `dual_track_status.md`, `kimodo_status.json`,
  `motionbricks_dual_track_summary.csv`, `motionbricks_k_scaling.png`, and
  `motionbricks_sonic_survival_scaling.png`.
- `results/kimodo_zero_text_smoke/` and
  `results/kimodo_zero_text_smoke_eval/`: negative-control Kimodo export smoke.
  This proves the G1 checkpoint/export path runs locally, but it is not a valid
  prompt-following method and fails the physical verifier.
- `results/kimodo_g1_examples_qpos/` and
  `results/kimodo_g1_examples_eval/`: official bundled Kimodo-G1 examples
  converted to qpos and evaluated with the same verifier stack. Includes
  `sonic_videos_cuda/` and `sonic_videos_cuda_contact_sheet.jpg`.
- `results/humanoid100_motionbricks_experiment/`: fresh 100-row MotionBricks
  proxy generation run, with K=1 and K=8 qpos outputs and videos.
- `results/humanoid100_repaired_retimed/`: second-stage retiming/smoothing
  repair run, with repaired qpos outputs and videos.

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

Dual-track update, 2026-05-30:

| Track | Current status |
|---|---|
| MotionBricks best completed K sweep | K=256, physical pass 76/100, approximate SONIC no-fall 17/100, mean survival 2.786 s |
| MotionBricks larger K sweep | K512/K1024 did not improve controller acceptance beyond roughly 16 no-fall clips |
| Kimodo-G1 setup | Repo, venv, CLI, and G1-RP checkpoint cache are present |
| Kimodo blocker | Missing Hugging Face token/access for gated Llama/LLM2Vec text encoder |
| Kimodo zero-text negative control | 0/1 physical pass, mean risk 280.782 |
| Bundled Kimodo-G1 demo sanity set | 2/8 physical pass, 3/8 approximate SONIC no-fall, 3.41 s mean survival |
| Bundled Kimodo-G1 gain sweep | best 3/8 no-fall, best mean survival 3.555 s |
| MotionBricks supported-subset gain sweep | best 7/22 no-fall, best mean survival 3.509 s; no tested gain improved no-fall |
| MotionBricks supported-subset native SONIC | 16/22 no-fall, 14/22 strict pass, mean joint RMSE 0.165 |
| MotionBricks all-100 selected native SONIC | 76/100 no-fall, 66/100 strict pass, mean joint RMSE 0.168 |
| MotionBricks failed-prompt native variant rescue | rescues 8/24 failed prompts; projected 84/100 no-fall, 74/100 strict pass |

Interpretation: MotionBricks is now credibly useful as a real-time proposal
generator plus verifier for a broad upright/proxy capability envelope. It still
does not support arbitrary language-conditioned motion generation or solved
floor/acrobatic execution. Kimodo is prepared as the higher-quality generation
track once gated text-encoder access is available. The bundled Kimodo demo
sanity set confirms the evaluator can ingest native Kimodo qpos, but also shows
generation quality and robot execution should remain separate claims.

The supported-subset gain-sweep videos and contact sheet are in
`results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_sonic_gain_sweep/`.
Those videos should be treated as negative/diagnostic evidence, not a final
success reel.

The native supported-subset videos are in
`results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_native_sonic_release/`.
These are stronger positive evidence than the approximate bridge videos, but
they cover only 22 semantically supported selections, not the full 100-prompt
suite.

The all-100 selected-reference native run is in
`results/ralphloop/20260529_191342/humanoid100_final_eval_k256/all100_native_sonic_release/`.
Use `humanoid100_native_analysis.md` and `humanoid100_native_by_category.csv`
for the category-level story.

The failed-prompt variant rescue run is in
`results/ralphloop/20260529_191342/humanoid100_final_eval_k256/failed_prompt_native_variant_sweep/`.
Use `native_variant_rescue_analysis.md` for the headroom story.

Final 100-prompt proxy benchmark with corrected approximate SONIC
initialization (`--init_reference_pose`, zero initial qvel):

| Selector | Mean Risk | Physical Pass | No Fall in Approx. SONIC | Mean Approx. SONIC |
|---|---:|---:|---:|---:|
| K=1 first generation | 36.81 | 63/100 | 11/100 | 2.266 s |
| K=8 best-of-K | 19.06 | 83/100 | 14/100 | 2.279 s |
| repaired retiming/smoothing | 14.89 | 84/100 | 16/100 | 2.677 s |
| risk-verifier selector | 14.49 | 86/100 | 16/100 | 2.684 s |
| SONIC-verifier selector | 20.00 | 76/100 | 16/100 | 2.914 s |

Interpretation: this is the current final method package. It supports a
MoVer-style inference-time verification and repair claim. It does not support a
claim of true MotionBricks fine-tuning, arbitrary text prompt success, or solved
controller execution. 78/100 rows remain forced nearest-mode semantic proxies.

Latest all-100 video validation:

- `final_100_selected_overlay_videos/`: 100/100 MP4s readable, 640x480.
- `k1_baseline_overlay_videos/`: 100/100 MP4s readable, 640x480.
- `before_after_overlay_videos/`: 100/100 MP4s readable, 1280x480.
- Initialization audit: max initial qpos error `0.0`, max initial qvel norm
  `0.0`, and `init_reference_pose=True` for all final and baseline videos.

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
- Hybrid hard-gate learned-score queue:
  `results/prospective_native_selection/20260523_hybrid_acceptance_queue/`
  selects 88 supported identities and rejects all 16 crawling identities. The 9
  selections not already covered by learned rollout labels were run through
  native SONIC in `native_release_missing9/`: all 9 survived and all 9 pass
  frame-level visual audit, but two idle clips fail the strict root-XY drift
  threshold. Closed-label hybrid accepted-set strict pass is therefore 74/88,
  with 68/80 upright strict and 6/8 idle strict. The report is
  `docs/hybrid_acceptance_queue_2026-05-23.md`.

## Next Actions

1. Use the corrected reference-aware fall metric for all current SONIC
   survival claims. Current all-100 native selection table:
   `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/final_100_native_selection_ref_aware.csv`.
   Repeat-conservative headline is 100/100 reference-aware no-fall and 74/100
   strict tracking.
2. Do not claim 100/100 semantic or tracking accuracy. The non-strict set is
   concentrated in floor/low-posture and athletic/acrobatic prompts; these
   survive under the corrected fall metric but still have high pose or root
   error.
3. Deep native SONIC retry completed under
   `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/deep_failure_native_sonic/`.
   It adds one strict rescue (`hrb_096_sprawl_recovery_deep02_k0008`) in the
   first batch rollout, but that clip did not repeat as strict in the final
   contact/camera diagnostic render. Treat deep retry as exploratory evidence,
   not as the repeat-conservative headline.
4. Render final diagnostic videos with `--contact_markers --camera_track` for a
   small set of strict successes, survival-only low-posture cases, and remaining
   hard acrobatic cases.
5. Build a human/VLM visual-review rubric over the final native videos before
   using any “accurate” wording in slides or paper.
