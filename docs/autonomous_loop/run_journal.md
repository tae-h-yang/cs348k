# Run Journal

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
