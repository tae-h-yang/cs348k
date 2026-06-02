# Run Journal

## 2026-05-30

- Reframed the active project as a dual-track study: MotionBricks for
  low-latency candidate generation and physics-aware screening, Kimodo-G1 for
  higher-quality humanoid robot motion generation.
- Harvested the completed MotionBricks RalphLoop sweeps. The best completed
  100-prompt MotionBricks result is K=256 with selector
  `sonic_verified_best`: 76/100 physical metric pass, 17/100 approximate SONIC
  no-fall, and 2.786 s mean approximate SONIC survival. K512 and K1024 did not
  materially improve controller acceptance.
- Set up the official Kimodo repo at `/home/rewardai/repos/kimodo` with an
  isolated venv at `.venv/kimodo`. The Kimodo-G1-RP-v1 checkpoint is cached
  locally, but text-conditioned generation remains blocked by missing gated
  Hugging Face access for the Llama/LLM2Vec text encoder.
- Added `scripts/run_kimodo_humanoid100_experiment.py` for resumable
  Kimodo-G1 generation over `configs/humanoid_robotics_100_prompts.csv`, with
  `(T, 36)` qpos validation and blocked/failed manifest reporting.
- Added `scripts/evaluate_kimodo_humanoid100.py` to evaluate generated Kimodo
  qpos clips with the same inverse-dynamics/contact verifier and optional
  SONIC reference export.
- Added `scripts/analyze_dual_track_motion_generation.py` and
  `scripts/dual_track_kimodo_motionbricks_loop.sh`. The loop refreshes the
  MotionBricks/Kimodo status and, once the token blocker is removed, will
  generate 100 Kimodo clips, evaluate them, export SONIC references, and run
  approximate SONIC rollouts/videos.
- Ran a zero-text Kimodo negative-control smoke test. It proved the G1
  checkpoint/export path can produce qpos locally, but failed physical
  evaluation at 0/1 pass with mean risk 280.782, so it is explicitly not a
  method.
- Added `docs/autonomous_loop/dual_track_kimodo_motionbricks_2026-05-30.md`
  to preserve the current decision, evidence, blocker, and next actions.
- Added `scripts/convert_kimodo_g1_examples.py` and evaluated the bundled
  official Kimodo-G1 demo motions as a native sanity set while full text
  generation remains gated. The eight demo clips converted cleanly to `(T, 36)`
  MuJoCo qpos. Physical verifier result: 2/8 pass, 5/8 repair/rerank, 1/8
  reject/regenerate. Approximate SONIC result with CUDA library path fixed:
  3/8 no-fall and 3.41 s mean survival. Videos are under
  `results/kimodo_g1_examples_eval/sonic_videos_cuda/` and the contact sheet is
  `results/kimodo_g1_examples_eval/sonic_videos_cuda_contact_sheet.jpg`.
- Patched `scripts/evaluate_kimodo_humanoid100.py` so `--sonic_ref_dir`
  defaults to `<out_dir>/sonic_references`, not the global Kimodo eval folder.
- Patched the dual-track loop to prepend Python-installed CUDA 12 NVIDIA
  library paths before ONNX Runtime CUDA runs.
- Swept approximate SONIC bridge gains on the eight bundled Kimodo-G1 examples:
  12 settings over `kp_scale in {0.6,0.8,1.0,1.2}` and
  `kd_scale in {0.8,1.0,1.2}`. Best result remained 3/8 no-fall, with mean
  survival 3.555 s at `kp0.8_kd1.2`. This reduces the chance that the Kimodo
  demo failures are merely one bad bridge-gain choice.
- Swept approximate SONIC bridge gains on the semantically supported K256
  MotionBricks selections. Across 12 settings, the best setting
  `kp0.7_kd1.0` reached 7/22 no-fall with 3.509 s mean survival, and all tested
  settings stayed at 7/22 no-fall. This argues against the MotionBricks
  execution failures being just a bad PD/SONIC bridge gain choice.
- Rendered the best supported-subset gain setting as 22 MP4s plus a contact
  sheet under
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_sonic_gain_sweep/`.
  Visual inspection agrees with the numbers: the robust cases are mostly
  gentle upright gestures; dynamic locomotion, dance, and low-posture motions
  still fall.
- Ran the same 22 semantically supported K256 selections through the native
  SONIC release path. Native SONIC is much less pessimistic than the approximate
  bridge: 16/22 no-fall, 14/22 strict pass, mean joint RMSE 0.165. The
  remaining failures are zombie walk, scared sneak, hand crawl, elbow crawl,
  bear crawl, and direct traffic. Results and videos are under
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_native_sonic_release/`.
- Ran the full 100 `sonic_verified_best` selected references through the native
  SONIC release path. Result: 76/100 no-fall, 66/100 strict pass, mean joint
  RMSE 0.168. Category-level join shows strong native execution for dynamic
  locomotion (13/14), balance (12/12), terrain (8/8), loco-manipulation
  proxies (13/14), manipulation stance (10/12), and communication/safety (8/8),
  but poor execution for floor/low-posture (3/12) and athletic/acrobatic stress
  tests (1/8). Results are under
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/all100_native_sonic_release/`.
- Ran native SONIC over K1/K8/repaired variants for the 24 prompts that failed
  the first all-100 selected-reference pass. Native verifier selection/retry
  rescues 8/24 failed prompts, projecting 84/100 no-fall and 74/100 strict
  pass. Still-failing prompts are concentrated in crawling, floor transitions,
  rolls, and acrobatic stress tests. Analysis is in
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/failed_prompt_native_variant_sweep/native_variant_rescue_analysis.md`.

## 2026-05-16

- User rejected the old framing as too toy-like and asked for a broader,
  research-level autonomous loop around high-quality humanoid robot motion data.
- Subagent repo audit confirmed current MotionBricks generation is real but
  exposed as discrete G1 modes, not arbitrary language prompts.
- Subagent method audit recommended controller-in-the-loop curation as the
  strongest next claim, with a MoVer-like MotionSpec verifier and rule-based
  physics/contact gates.
- Created this autonomous-loop documentation structure so future runs have a
  durable place for decisions, blockers, evidence, and commands.
- Added a generator for a 100 distinct-prompt humanoid robotics benchmark.
- Generated `configs/humanoid_robotics_100_prompts.csv` and verified it has 100
  rows with 100 unique prompt texts. Coverage: 16 locomotion, 12 terrain, 18
  loco-manipulation, 12 manipulation stance, 12 balance, 10 communication, 10
  low posture, and 10 workspace tasks.
- Added `scripts/evaluate_motionspec.py`, a first MoVer-like predicate checker
  over the existing executable 105-row MotionBricks suite.
- Ran MotionSpec on the existing 210 K=1/K=8 rows. Selector comparison:
  K=1 baseline score 0.686, K=8 score 0.736, MotionSpec-over-K1/K8 score 0.757.
  MotionSpec selection also raises prompt proxy alignment from 0.583/0.568 to
  0.620 and approximate SONIC survival from 2.005/2.054 s to 2.117 s.
- Top failures are controller-related: 196/210 approximate SONIC rows fall and
  185/210 fail the 3 s survival predicate. This confirms that controller
  fidelity and controller-in-the-loop selection remain the main research risk.
- Added `scripts/plot_motionspec_dashboard.py` and generated
  `results/motionspec_selector_dashboard.png` plus
  `results/motionspec_failure_counts.png` for quick visual review.
- Ran `pytest -q`: 7 passed.
- User correctly objected that this was not enough work or evidence. Added
  `phd_student_role.md`, `reviewer_loop.md`, and `reviewer_reports.md` to force
  stricter continuation criteria before any future "presentable" claim.
- Added `scripts/build_candidate_evidence_table.py` and
  `scripts/plot_combined_selector.py`. The combined selector improves over K=1
  on combined score (0.577 -> 0.653), semantic score (0.650 -> 0.697), risk
  (35.32 -> 14.17), and approximate SONIC survival (2.005 s -> 2.148 s), but
  SONIC oracle still has the longest survival (2.299 s) while accepting worse
  risk. This supports controller-in-the-loop selection as the next real method.
- Added `scripts/select_visual_audit_clips.py` and
  `scripts/render_visual_audit_contact_sheet.py`. Generated a 12-clip visual
  audit sheet showing that low/crawling clips visibly collapse or lie on the
  ground, validating the need for visual review and stricter contact/controller
  gates.
- Added `docs/autonomous_loop/long_run_protocol.md` and
  `scripts/longrun_motion_curation.sh` to support 4-8 hour autonomous runs with
  resumable candidate generation, heavier critic training, regenerated visual
  audit artifacts, and a run summary.
- Added `scripts/render_visual_audit_videos.py` so selected audit cases can be
  watched as MP4s, not only inspected as still-frame contact sheets.
- Ran the 2026-05-16 long-run protocol for more than 6 hours. It expanded the
  candidate audit to 728 candidates over 91 mode-seed identities, rendered 12
  visual-audit MP4s, and trained two width-512 neural critic seeds for 5000
  epochs each. Results are documented in
  `docs/autonomous_loop/long_run_results_2026-05-16.md`.
- Added native SONIC release validation. The official stack works through the
  native C++ deploy path plus MuJoCo qpos logging. With elastic-band release,
  11/12 curated upright MotionBricks candidates survived full clip, while both
  crawling negative controls failed. Results are documented in
  `docs/sonic_native_release_validation_2026-05-16.md`.
- Expanded the native-release check with four more strict-gate candidates,
  giving 14/16 upright candidates surviving full clip and a clean 14-video pass
  folder at `results/sonic_native_release_20260516_strict_pass/`.
- Ran a 100-attempt native SONIC release batch under an 8-hour cap. It completed
  100/100 attempts in 1.20 hours: 84/100 overall pass, 76/84 upright pass,
  66/84 strict upright pass after RMSE/root-drift gating, 8/8 idle pass, and
  0/8 crawling pass. Results are documented in
  `docs/sonic_native_overnight_100_2026-05-16.md`.
- Audited the new pivot with reviewer/explorer agents. Conclusion: true
  MotionBricks generator fine-tuning is not scientifically meaningful with the
  current local preview release; the defensible method is native
  SONIC-controller-in-the-loop curation for fixed MotionBricks candidates.
- Added `scripts/analyze_native_sonic_selector.py`. On the 100-run native batch,
  K=1 strict pass is 20/25 paired identities, K=8 inverse-dynamics-selected
  strict pass is 16/25, and native oracle upper bound is 22/25. This rules out
  the old "K=8 improves execution" claim and reframes the project around
  native acceptance gates plus calibrated pre-controller features.
- Launched an all-210 native SONIC release run with a 12-hour cap:
  `results/sonic_native_release_all210/20260516_123519/`.
- Added `scripts/build_native_visual_audit_manifest.py` and generated a
  34-row rubric manifest for the 100-run native batch, covering strict passes,
  borderline passes, and failures.
- Completed the all-210 native SONIC release run under
  `results/sonic_native_release_all210/20260516_123519/`. Results: 164/210
  overall survival, 152/168 upright survival, 136/168 strict upright pass, and
  0/28 crawling survival. Across 105 paired identities, K=1 strict pass is
  72/105, K=8 inverse-dynamics-selected strict pass is 74/105, and native oracle
  upper bound is 85/105. Added
  `docs/sonic_native_all210_2026-05-16.md`.
- Added and ran a prospective held-out native-selection experiment:
  `scripts/run_prospective_native_selection.py`,
  `scripts/analyze_prospective_native_selection.py`, and
  `scripts/render_prospective_comparison_sheets.py`.
- The prospective run generated 640 candidates over 80 upright mode-seed
  identities and evaluated 320 selector references through native SONIC. Final
  strict pass rates: baseline 64/80, best pre-controller 67/80, gated duplicate
  67/80, lowest inverse-dynamics-risk 66/80, and native oracle 78/80. Best
  pre-controller gives 13 rescues and 10 regressions versus baseline.
- Visual sheets were generated for paired rescues, regressions, and both-failed
  identities under
  `results/prospective_native_selection/20260516_170132/comparison_sheets/`.
  The evidence supports a scoped claim: cheap screening helps modestly, but
  native SONIC remains the acceptance gate.
- User flagged that some failure videos looked like the red ghost/reference was
  thrown away. Audited the renderer and corrected the color convention:
  white/left is the MotionBricks reference, red/right is the actual SONIC
  simulator qpos. Added diagnostic rerendering with contact dots and tracking
  camera in `scripts/render_existing_sonic_diagnostics.py`.
- Added `scripts/audit_sonic_reference_export.py` and audited all 320
  prospective references. Export round-trip max absolute error is `3.33e-16`,
  ruling out a broad conversion bug. 23/320 references dip below root height
  0.60m, mostly `walk_stealth`; these should be handled by a low-root posture
  gate.
- Added `scripts/analyze_sonic_reference_sanity.py` and joined the export audit
  with the native rollout table. Low-root references pass strictly in 7/23
  cases versus 257/297 for non-low-root references. Also patched
  `run_prospective_native_selection.py` so future prospective runs record and
  gate upright root-height sanity before exporting SONIC references.
- Reran the prospective selection study with the low-root/upright gate under
  `results/prospective_native_selection/20260516_lowroot_gate/`. Native SONIC
  completed 320/320 rollouts. The gated selector reached 73/80 strict pass
  versus 64/80 baseline, with 14 rescues and 5 regressions. The key
  `walk_stealth` stress mode improved from 3/8 strict pass for baseline to 7/8
  for the gated selector. Added
  `docs/prospective_lowroot_gate_2026-05-16.md`.
- Refactored the 100-prompt target benchmark so it is no longer dominated by
  walking styles. The regenerated `configs/humanoid_robotics_100_prompts.csv`
  has 9 categories, only 21 prompts containing `walk`, 8 jump/hop/skip/bound
  prompts, and 17 crawl/floor/roll/kneel/plank/handstand/cartwheel-style
  prompts. Added regression tests for uniqueness, category coverage, diversity,
  and label sanity.

## 2026-05-22

- Added `scripts/train_native_sonic_acceptance.py`, a temporal qpos model that
  learns native SONIC strict-acceptance labels from actual native rollouts. It
  uses group cross-validation by `(mode, seed)` identity to avoid leakage
  through duplicate selector reruns.
- Smoke-tested the trainer for two epochs on CUDA.
- Ran a longer 5-fold, 3000-epoch CUDA training job on the low-root-gated
  prospective batch. The temporal model reached cross-validated AUC 0.769 and
  average precision 0.921, outperforming scalar gates whose AUCs ranged from
  0.492 to 0.620 on the same rows. Added
  `docs/native_acceptance_model_2026-05-22.md`.
- Generated a broader 13-mode prospective candidate pool under
  `results/prospective_native_selection/20260522_broad13/`: 832 generated
  candidates, 405 selected SONIC references, including idle, upright gaits, and
  hand/elbow crawling. Export audit reports max qpos round-trip error
  `3.33e-16` and 67 low-root references.
- Started native SONIC evaluation for the broad 13-mode set with interleaved
  selector order and a 6-hour cap. Early elbow-crawling rollouts fail around
  2 seconds, consistent with crawling remaining a negative-control category for
  the current SONIC acceptance gate.
- Completed the broad 13-mode native SONIC evaluation under
  `results/prospective_native_selection/20260522_broad13/native_release/`:
  405/405 selected references evaluated. Prospective analysis shows
  deterministic baseline at 70/104 strict identity passes, best pre-controller
  at 73/104, lowest inverse-dynamics risk at 72/104, and gated pre-controller
  at 78/104. The native oracle over tested selectors is 88/104.
- Added category-aware broad13 interpretation in
  `docs/prospective_broad13_2026-05-22.md`. The useful claim is upright
  controller-in-the-loop curation: gated reaches 71/80 strict on upright
  identities versus 63/80 baseline. Crawling is an explicit negative control:
  0 strict passes and 0 survivals for the tested crawling rows.
- Generated paired comparison sheets for broad13 rescues, regressions, and
  both-failed cases under `comparison_sheets/`.
- Generated diagnostic SONIC videos with contact markers and tracking camera,
  including a stress-mode set for `walk_stealth`, `walk_scared`,
  `walk_zombie`, `walk_happy_dance`, `walk_boxing`, and `walk_gun`. Updated
  `results/current_validated/` to point to the broad13 run without deleting old
  result directories.
- Patched native batch tooling so resumed batches refresh parsed `mode` and
  `category` fields, and added semantic `--mode_filters` to
  `render_existing_sonic_diagnostics.py` for review-oriented video selection.
- Ran a 4.5-hour CUDA training job for a broad13 temporal qpos native-acceptance
  model: 405 records, 104 grouped identities, 5 folds, 6000 epochs per fold,
  width 512. The final cross-validated AUC is 0.864 and average precision is
  0.917, versus scalar baselines between 0.719 and 0.782 AUC. Added
  `docs/native_acceptance_broad13_2026-05-23.md`.
- Added `scripts/score_native_acceptance_candidates.py` and scored all 832
  broad13 candidates with the saved fold checkpoints. Fair retrospective
  out-of-fold selection over already native-evaluated choices reaches 77/104
  strict passes, close to the hand-coded gated selector's 78/104. The learned
  ensemble's all-candidate choices are mostly not yet native-evaluated, so they
  form the next prospective native rollout queue.

## 2026-05-23

- Exported the broad13 learned-acceptance ensemble's all-candidate selections
  with `scripts/export_learned_acceptance_selection.py` and ran all
  104 selected references through native SONIC under
  `results/prospective_native_selection/20260523_learned_acceptance_eval/`.
- Patched native batch parsing so the new `learned_acceptance` selector prefix
  is stripped before mode/category assignment, then refreshed the batch summary.
- Prospective learned-selector result: 76/104 strict identity passes, 68/80
  upright strict, 8/8 idle strict, and 0/16 crawling survival. This improves
  over deterministic baseline (70/104, 63/80 upright) but does not beat the
  hand-coded gated selector (78/104, 71/80 upright).
- Added `--all` to `scripts/render_existing_sonic_diagnostics.py` and
  rerendered every learned-selector rollout with camera tracking and contact
  markers.
- Added `scripts/visual_audit_sonic_videos.py`, a frame-level MP4 pixel audit.
  It segments red actual robot and white reference robot in every frame, then
  flags missing bodies, large separation, fallen-looking aspect ratios, and
  sudden visual jumps.
- Ran the visual audit on all 104 tracked learned-selector diagnostic videos:
  27 visual pass, 61 warn, 16 fail, and 1 strict native pass with a visual-fail
  contradiction. The obvious visual failures are dominated by crawling
  collapses and a few upright fall/separation cases.
- Created a reviewed 11-video presentation subset under
  `results/prospective_native_selection/20260523_learned_acceptance_eval/native_release/visual_reviewed_presentation_videos/`,
  one strict, non-visual-fail representative per supported upright/idle mode.
- Added `docs/learned_acceptance_prospective_2026-05-23.md` with commands,
  results, visual-audit counts, interpretation, and next hybrid-gate
  experiment.
- Added `scripts/select_hybrid_acceptance_candidates.py` and exported a
  hard-gated learned-score queue under
  `results/prospective_native_selection/20260523_hybrid_acceptance_queue/`.
  The queue selects 88 supported identities and rejects all 16 crawling
  identities.
- Ran native SONIC for the 9 hybrid selections not already covered by the
  learned prospective rollout. All 9 survived and all 9 pass visual pixel audit,
  but two idle clips fail strict due to root XY drift. The closed-label hybrid
  queue is therefore 74/88 strict, not a new headline win. Added
  `docs/hybrid_acceptance_queue_2026-05-23.md`.

## 2026-05-28

- User asked for one more method review and a better attempt at fixing invalid
  physical reference motions.
- Added `scripts/repair_humanoid100_references.py`, a second-stage
  reference-conditioning baseline. For every selected K=8 qpos from the
  100-prompt MotionBricks proxy experiment, it validates qpos shape/quaternions,
  tries identity, retiming at 1.25x/1.5x/2.0x, and Gaussian/Savitzky-Golay
  joint smoothing variants, then keeps the lowest inverse-dynamics-risk
  candidate.
- Ran the repair over all 100 prompt rows with rendering. Results:
  `results/humanoid100_repaired_retimed/repair_summary.csv`,
  `results/humanoid100_repaired_retimed/videos/*.mp4`, and
  `data/humanoid100_repaired_retimed/*.npy`.
- Quantitative result: mean risk moves from K=1 36.81 to K=8 19.06 to repaired
  14.89. The repaired reference is better than K=8 in 47/100 rows, worse in
  0/100 rows, and tied in 53/100 rows.
- Interpretation: this is the best current lightweight method for physically
  invalid reference conditioning in this repo. It is still not semantic prompt
  generation; 78/100 rows remain forced nearest-mode proxies.
- Added `scripts/evaluate_humanoid100_final.py`, which evaluates K=1, K=8, and
  repaired references for all 100 prompt rows with inverse-dynamics metrics,
  contact/support metrics, and separate semantic/presentation pass labels.
  Output: `results/humanoid100_final_eval/`.
- Final verifier results: physical-pass counts improve from 63/100 for K=1 to
  83/100 for K=8 and 84/100 for repaired references. Presentation-pass counts
  are 15/100, 18/100, and 18/100 because forced nearest-mode proxies are not
  counted as semantic successes.
- Added `scripts/export_humanoid100_sonic_references.py` and exported 66 SONIC
  references for the 22 semantically supported prompt proxies across K=1, K=8,
  and repaired variants.
- Ran the approximate MuJoCo SONIC tracker on those 66 references. Mean
  tracking improves from K=1 2.676 s / 0.312 rad RMSE to K=8 2.769 s /
  0.282 rad RMSE and repaired 2.996 s / 0.258 rad RMSE. Rendered 9 selected
  SONIC rollout videos under
  `results/humanoid100_final_eval/sonic_supported_videos/`.
- Also exported all 100 prompt identities across K=1, K=8, and repaired
  references to the approximate SONIC tracker. Repaired references improve mean
  tracking from K=1 2.232 s / 0.320 rad RMSE and K=8 2.271 s / 0.323 rad RMSE
  to 2.588 s / 0.288 rad RMSE, but still fall in 86/100 cases.
- Added `scripts/select_humanoid100_final_method.py`. It builds the final
  selector table comparing K=1, K=8, repaired, a risk-verifier selector, and a
  SONIC-verifier selector. Results:
  `results/humanoid100_final_eval/final_selector/`.
- Final selector result: `risk_verifier_best` has the best physical-pass count
  at 86/100 and mean risk 14.49. `sonic_verified_best` has the best tracking
  time at 2.815 s mean, but a higher mean risk 20.32 and only 75/100 physical
  pass. This exposes the real tradeoff between cheap physical-risk screening
  and controller-in-the-loop verification.
- Rendered 27 representative selector rollout videos and a contact sheet under
  `results/humanoid100_final_eval/final_selector/representative_videos/` and
  `representative_contact_sheet.jpg`.
- Fixed an approximate SONIC initialization credibility issue: `scripts/evaluate_sonic_policy_mujoco.py` can now start the simulated robot exactly from the first reference qpos via `--init_reference_pose`, always zeros initial qvel, and saves `initial_sim_qpos`, `initial_ref_qpos`, and `initial_sim_qvel` into rollout NPZs for audit.
- Reran corrected all-100 approximate SONIC tracking. Corrected selector means: K=1 2.266 s / 0.301 RMSE, K=8 2.279 s / 0.297 RMSE, repaired 2.677 s / 0.267 RMSE, risk-verifier 2.684 s / 0.271 RMSE, and SONIC-verifier 2.914 s / 0.262 RMSE.
- Rendered the complete all-100 video set with red translucent reference ghost and solid MuJoCo physics robot: `results/humanoid100_final_eval/final_100_selected_overlay_videos/*.mp4`.
- Rendered the complete K=1 baseline set with the same visual convention: `results/humanoid100_final_eval/k1_baseline_overlay_videos/*.mp4`.
- Stitched 100 side-by-side before/after videos, one per prompt: `results/humanoid100_final_eval/before_after_overlay_videos/*.mp4`. Left is K=1 baseline; right is the selected verifier/repair result.
- Generated all-100 visual indexes: `results/humanoid100_final_eval/before_after_overlay_contact_sheet.jpg` and `results/humanoid100_final_eval/final_100_selected_overlay_contact_sheet.jpg`.
- Validation: all three MP4 sets have 100/100 readable videos; final and baseline index CSVs report max initial qpos error `0.0`, max initial qvel norm `0.0`, and `init_reference_pose=True` for every row.
- Added RalphLoop supervisor: `scripts/ralphloop.sh` plus detached launcher `scripts/launch_ralphloop.py` and documentation `docs/autonomous_loop/ralphloop.md`.
- Started a 12-hour K=32 RalphLoop run at `results/ralphloop/20260529_170525/`. It passed environment checks, confirmed CUDA is visible, passed `pytest` (22 tests), and entered `generate_best_of_k32`.
- Monitor with `cat results/ralphloop/latest/status.md` and `tail -f results/ralphloop/latest/ralphloop.log`.
- Fixed ONNXRuntime GPU execution. `onnxruntime-gpu` exposed CUDA provider after reinstall, but session creation needed CUDA 12 runtime libraries. Installed CUDA 12 NVIDIA Python wheels and added `scripts/python_nvidia_lib_paths.py`; `ralphloop.sh`, `launch_ralphloop.py`, and `ralphloop_agent.py` now export those library paths. Verified SONIC encoder/decoder sessions load on `CUDAExecutionProvider`.
- Killed the earlier CPU-backed/partial RalphLoop and relaunched a fresh K=32 run at `results/ralphloop/20260529_172911/` with CUDA ONNXRuntime enabled.
- Added and launched `scripts/ralphloop_agent.py` as the scripted self-correction monitor. It watches the active run and will write reviewer verdicts and launch a K=64 corrective run if the K=32 result fails the strict acceptance bar within the time budget.
- User required at least 6 more hours. The prior K=32/K=64 RalphLoop completed quickly and failed strict acceptance. Patched `scripts/ralphloop_agent.py` to keep launching corrective runs by doubling K until `--max-k` instead of stopping after one relaunch.
- Started a 6-hour extended monitor with `--next-k 128 --max-k 512`. It launched `results/ralphloop/20260529_182242/`, currently running `generate_best_of_k128` with CUDA available.
- Added `scripts/ralphloop_wakeup_watch.py` and launched it. It polls active RalphLoop processes every 120s, writes `results/ralphloop_wakeup.md` when the run finishes, logs to `results/ralphloop_wakeup.log`, and attempts a desktop notification/terminal bell.
- Set up a slide-generation workflow under `slides/`: Marp source deck
  (`slides/deck.md`), custom theme (`slides/theme.css`), Python fallback HTML
  builder (`scripts/build_slides_html.py`), metrics snapshot updater
  (`scripts/update_slide_metrics.py`), and one-command build script
  (`slides/build_slides.sh`).
- Installed Node.js and `@marp-team/marp-cli` in the active environment.
  `bash slides/build_slides.sh` now exports
  `slides/build/deck.html`, `slides/build/deck.marp.html`,
  `slides/build/deck.pdf`, and `slides/build/deck.pptx`.
- The Node install disturbed SciPy's compiled package state; repaired the
  environment by pinning `numpy==1.26.4` and `scipy==1.14.1`. Verified
  `pytest -q` passes 22/22 and SONIC ONNX sessions still load on
  `CUDAExecutionProvider`.
- User requested at least 8 more hours after K=512 if result is not near 80/90/100 no-fall. Patched `scripts/ralphloop_agent.py` so active-process detection includes `resume_ralphloop_latest.sh` and child eval/repair/SONIC jobs, not just `ralphloop.sh`.
- Replaced the old short monitor with an 8-hour monitor: `python scripts/ralphloop_agent.py --hours 8 --provider cuda --poll-seconds 180 --next-k 1024 --max-k 2048`. It currently sees the active K=512 resume and will wait for it before deciding whether to launch K=1024/2048.
- Added reference-aware SONIC fall metrics because a fixed root-height
  threshold incorrectly penalized intentional low-posture references. The
  recomputed all-100 native SONIC batch is
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/all100_native_sonic_release/batch_summary_ref_aware.csv`:
  91/100 reference-aware no-fall and 66/100 strict tracking.
- Recomputed the failed-prompt native variant sweep with the same metric:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/failed_prompt_native_variant_sweep/batch_summary_ref_aware.csv`.
  Verifier selection over original plus K1/K8/K9 variants reaches 100/100
  reference-aware no-fall, but only 74/100 strict tracking before deep retry.
- Built the final 100-prompt selection table and figure:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/final_100_native_selection_ref_aware.csv`,
  `.md`, and `.png`. Repeat-conservative headline: 100/100 survival under a
  reference-aware fall metric; 74/100 strict tracking; low-posture/acrobatic
  prompts remain the main non-strict region.
- Added deep retry tooling for the remaining non-strict/failure region:
  `scripts/generate_deep_failure_candidates.py`,
  `scripts/analyze_deep_failure_rescue.py`, and native SONIC rollout under
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/deep_failure_native_sonic/`.
  The completed 64-candidate deep retry adds one strict rescue in its first
  rollout, producing an exploratory 75/100 table. The same rescued clip did not
  repeat as strict in the contact/camera diagnostic render, so the headline
  table excludes deep candidates and remains 74/100 strict.

## 2026-05-30

- Completed a targeted K1024 rescue pass for the 26 prompts that remained
  non-strict after the repeat-conservative K1/K8/K9 native selector.
  Artifacts:
  `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/nonstrict_k1024_native_sonic/`.
- K1024 native selection rescues 10/26 non-strict prompts. Integrated table:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/final_100_native_selection_ref_aware_k1024_targeted.csv`.
  Best current headline with caveat: 100/100 reference-aware no-fall and
  projected 84/100 strict tracking. Repeat-conservative headline remains
  74/100 strict.
- Remaining non-strict prompts after K1024 are 16 floor/low-posture or
  acrobatic-stress motions: hand crawl, elbow crawl, bear crawl, crab walk,
  kneel/stand transitions, pushup/sit/roll variants, cartwheel/roll/burpee/
  sprawl/knee-slide/handstand variants.
- Ran a retiming/smoothing ablation over the 16 remaining failures:
  `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/retimed_nonstrict_native_sonic/`.
  Result: 96 variants, 0/16 new strict rescues. It improves some survival
  durations and near-miss RMSEs but does not cross the strict gate.
- Fixed a reference-export correctness issue: generated SONIC references now
  compute root/body angular velocity from body quaternions instead of writing
  zeros. Updated `scripts/export_sonic_references.py`,
  `scripts/generate_retimed_sonic_references.py`, and
  `scripts/generate_upright_safe_sonic_references.py`; added
  `scripts/generate_angvel_corrected_sonic_references.py`.
- Tested angular-velocity-corrected references for the same 16 hard prompts:
  `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/angvel_corrected_native_sonic/`.
  Result: 0/16 new strict rescues; contact/camera videos and
  `contact_sheet.jpg` were generated for review.
- Tested a partial upright-safe projection diagnostic:
  `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/upright_safe_native_sonic/`.
  It was stopped after 8 variants because it produced 0 strict rescues and
  weakens semantics for floor/acrobatic prompts.
- Current technical conclusion: blind best-of-K sampling helps within SONIC's
  upright support manifold, but the remaining floor/acrobatic cluster is a
  contact-mode mismatch. The next credible method is contact/state-conditioned
  retargeting or policy/generator training for non-foot support, not another
  scalar-risk sweep.
- Added `scripts/generate_sonic_projected_references.py`, a
  controller-manifold projection baseline. For each remaining hard prompt it
  extracts the actual native SONIC MuJoCo qpos from the first rollout,
  re-exports that trajectory as a SONIC reference, and reruns native tracking.
- Controller-projected references are in
  `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/sonic_projected_references/`;
  rerun videos/metrics are in
  `results/ralphloop/20260530_003531/humanoid100_final_eval_k1024/sonic_projected_native_sonic/`.
- Result: controller projection rescues 8/16 remaining hard prompts and creates
  an experimental 92/100 strict table:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/final_100_native_selection_ref_aware_k1024_projected.csv`.
  This is the strongest execution baseline, but it is not prompt-preserving by
  itself; it proves that native SONIC can execute a projected version of many
  hard motions, while semantic/style fidelity still needs visual or task-level
  audit.
- Ran projection iterations 2-4 over the remaining non-strict prompts.
  Iteration 2 rescues burpee, iteration 3 rescues pushup, and iteration 4 adds
  no new strict rescues. Final experimental controller-projection table:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/final_100_native_selection_ref_aware_k1024_projected_iter4.csv`.
  Current experimental execution result: 100/100 reference-aware no-fall and
  94/100 strict tracking. Remaining failures are elbow crawl, roll to kneel,
  forward roll, sprawl recovery, knee slide, and side-roll recovery.
- After Hugging Face gated Llama access was fixed with a read token, ran the
  full Kimodo-G1 Humanoid100 pipeline:
  `results/kimodo_humanoid100_full_kimodo100_full_20260530_200838/`.
  Generation succeeded for all 100 prompts at 4.0s and 50 diffusion steps.
  Physics-screen result: 48/100 `physical_pass`. Approximate SONIC tracking
  with `--init_reference_pose`: 53/100 no-fall, 47/100 fell, mean tracking
  duration 2.855s, median duration 3.98s, mean RMSE 0.156.
- Kimodo category breakdown under SONIC:
  athletic stress 0/8, floor/low-posture 1/12, dynamic locomotion 7/14,
  terrain/obstacle 7/8, balance/recovery 9/12, manipulation stance 9/12,
  loco-manipulation 7/14, communication/safety 4/8, dance/expressive 9/12.
  Interpretation: Kimodo gives strong visual-quality candidates and covers all
  requested prompt categories, but it does not solve physical executability for
  G1 under SONIC; low-posture and acrobatic contact modes remain the clearest
  failure region.
- Kimodo artifacts: `generation/manifest.csv`, `eval/final_metrics.csv`,
  `eval/sonic_tracking_cuda.csv`, 100 videos in `eval/sonic_videos_cuda/`,
  `eval/sonic_videos_cuda_contact_sheet.jpg`, and
  `eval/kimodo_physical_summary.png`.
