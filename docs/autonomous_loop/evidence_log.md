# Evidence Log

## Existing Strong Evidence

- Real local MotionBricks calls exist through `navigation_demo` and
  `generate_new_frames`.
- Inverse-dynamics best-of-K reduces heuristic risk across existing K sweeps.
- Contact-quality scripts already compute self-contact, non-foot floor contact,
  foot skate, and support proxies.
- The approximate SONIC selector over stored variants suggests controller-aware
  selection can improve survival/RMSE, but this is not yet native validation.
- The first MotionSpec checker over existing 105 paired identities improves mean
  predicate score and prompt proxy alignment when selecting between K=1 and K=8,
  while also modestly improving approximate SONIC survival. This is evidence for
  structured curation, not for full task generation.
- Native SONIC release validation is now the strongest evidence source. The
  100-run batch shows an executable upright subset, but selector calibration
  also shows inverse-dynamics K=8 alone is not a reliable execution-improving
  method.
- The initial prospective native selection on held-out seeds 7-14 showed a
  modest real
  improvement from cheap screening: best pre-controller selection reaches 67/80
  strict pass versus 64/80 deterministic baseline, while the native oracle over
  tested selectors reaches 78/80. This is superseded by the later low-root-gated
  rerun below, but remains useful as the run that exposed the low-root failure
  mode.
- The SONIC reference export audit for the prospective run shows no broad
  conversion/joint-order bug: all 320 exported references round-trip back to the
  expected MuJoCo qpos with max absolute error `3.33e-16`. However, 23/320
  references have root height below 0.60m, mostly `walk_stealth`, and should be
  treated as low-posture/invalid for upright-locomotion claims.
- Joining reference sanity with native rollout outcomes shows a large split:
  low-root references pass the strict native gate in 7/23 cases, while
  non-low-root references pass in 257/297 cases. That supports adding a
  root-height sanity gate before native rollout.
- The low-root-gated prospective rerun completed 320/320 native SONIC rollouts.
  The updated `gated_precontroller` selector reaches 73/80 strict pass versus
  64/80 for deterministic baseline, with 14 rescues and 5 regressions. On the
  known brittle `walk_stealth` mode, it improves strict pass from 3/8 to 7/8.
- A temporal qpos-to-native-SONIC acceptance model trained on the
  low-root-gated rollout labels reaches cross-validated AUC 0.769 and average
  precision 0.921, exceeding the scalar gates tested on the same rows. This
  supports trajectory-level learned triage as a candidate next step.
- The broad 13-mode prospective generation run completed 832 generated
  candidates and 405 selected SONIC references across upright, idle, and
  crawling modes. Reference export round-trip error remains numerical
  precision (`3.33e-16` max absolute error), so broad-set failures should be
  interpreted as generated-reference/controller-distribution issues unless
  later audits identify a more local bug.
- The broad 13-mode native SONIC rollout completed 405/405 selected references.
  `gated_precontroller` improves strict identity pass from 70/104 baseline to
  78/104, with 16 rescues and 8 regressions over 93 paired gated identities.
  The native oracle over tested selectors is 88/104. The effect is strongest
  for upright stress/style modes such as `walk_stealth` (3/8 baseline strict to
  7/8 gated strict), while crawling remains 0 strict passes for every selector.
  Visual diagnostics with contact markers are generated under the broad13
  native release directory and linked from `results/current_validated/`.
- A broader temporal qpos acceptance model trained on the broad13 native labels
  reaches cross-validated AUC 0.864 and average precision 0.917, outperforming
  scalar baselines on the same 405 rows. The best scalar is root-z minimum at
  AUC 0.782; pre-controller score is AUC 0.752. This supports learned
  trajectory-level acceptance prediction as the next prospective selector to
  test.
- Applying the learned broad13 model retrospectively is not yet a decisive
  selector win. Among already native-evaluated choices, out-of-fold learned
  selection reaches 77/104 strict passes, close to the hand-coded gated
  selector's 78/104. The all-candidate checkpoint ensemble selects 58/104
  candidates that were not native-evaluated, so those are a prospective rollout
  queue rather than evidence of success.
- The prospective learned broad13 selector queue has now been evaluated through
  native SONIC. It reaches 76/104 identity strict passes, 68/80 upright strict,
  and 8/8 idle strict, versus 70/104 and 63/80 upright for deterministic
  baseline. This is a real prospective improvement over baseline.
- On the learned rollout, score thresholding is useful as abstention: requiring
  ensemble score >= 0.5 accepts 88/104 identities, removes all 16 crawling
  selections, and retains all 76 strict passes. Accepted-set strict rate rises
  from 73.1% to 86.4%, at the cost of leaving unsupported identities uncovered.
- A first all-candidate hybrid queue rejects crawling, exports 88 supported
  references, and closes its 9 previously missing native labels. The 9 new
  videos have 9/9 visual pass and no falls, including a `walk_stealth` stress
  case. Overall hybrid accepted-set strict pass is 74/88 because two idle clips
  drift too far in root XY.
- Frame-level tracked-camera visual audit was added because fixed-camera video
  review created false positives when the robot walked out of frame. The
  learned prospective diagnostic set has 104/104 videos audited from pixels:
  27 pass, 61 warn, 16 fail. Only 1/76 strict native passes is also a visual
  fail, which gives a much cleaner presentation subset than relying on rollout
  CSVs alone.
- The full 100-prompt MotionBricks proxy experiment generated fresh K=1 and
  K=8 qpos clips for every benchmark row, including forced nearest-mode proxies
  for unsupported prompts. Best-of-K reduces mean inverse-dynamics risk from
  36.81 to 19.06, improving 80/100 rows, worsening 5/100, and tying 15/100.
- A new second-stage retiming/smoothing repair over those K=8 selected
  references reduces mean risk further to 14.89. It improves 47/100 references
  relative to K=8, worsens 0/100, and leaves 53/100 unchanged. This is evidence
  that simple reference conditioning can reduce dynamics demand after
  generation, but only as a feasibility repair.
- The final 100-row verifier now combines dynamics and contact/support checks.
  Under the stricter pass definition, physical-pass counts are 63/100 for K=1,
  83/100 for K=8, and 84/100 for repaired references. Mean contact artifact
  score also improves from 0.252 to 0.234 to 0.227. Presentation-pass counts
  remain 15/100, 18/100, and 18/100 because only supported prompt proxies are
  allowed to count as prompt-valid.
- Approximate SONIC tracking on the 22 semantically supported prompt proxies
  gives a controller-side signal in the same direction: K=1 averages 2.676 s /
  0.312 rad RMSE, K=8 averages 2.769 s / 0.282 rad RMSE, and repaired averages
  2.996 s / 0.258 rad RMSE. This is not native SONIC certification, but it is a
  useful qualitative/quantitative tracking stress test for the supported subset.
- Approximate SONIC tracking on all 100 generated proxy references gives the
  same broad pattern: K=1 averages 2.232 s / 0.320 rad RMSE, K=8 averages
  2.271 s / 0.323 rad RMSE, and repaired averages 2.588 s / 0.288 rad RMSE.
  Falls remain high at 86/100 repaired references, so the controller evidence
  supports "improved but not solved."
- A MoVer-style verifier-at-test-time selector can choose the best of K=1,
  K=8, and repaired under the approximate SONIC metric. This reaches 3.127 s
  mean tracking on the 22 supported proxies and 2.815 s on all 100 proxy
  identities. Because it uses SONIC as the selector, report it as an
  inference-time verification strategy rather than as a learned generator.
- The final selector package makes the tradeoff explicit. `risk_verifier_best`
  reaches 86/100 physical pass and mean risk 14.49, while
  `sonic_verified_best` reaches the best mean tracking time, 2.815 s, but only
  75/100 physical pass and mean risk 20.32. This supports presenting two
  operating points: cheap feasibility screening versus expensive
  controller-verified selection.
- The approximate SONIC bridge was corrected to start the simulated robot from
  the first reference pose with zero initial velocity. With that fix, the
  all-100 corrected selector table reports K=1 at 2.266 s mean tracking,
  K=8 at 2.279 s, repaired at 2.677 s, risk-verifier at 2.684 s, and
  SONIC-verifier at 2.914 s. The selector still does not solve execution, but
  the comparison is no longer confounded by an initial-pose mismatch.
- All 100 final selected videos and all 100 K=1 baseline videos were rendered
  from saved corrected rollouts. Index validation shows `0.0` max initial qpos
  error and `0.0` max initial qvel norm for both final and baseline sets. The
  review artifacts are `results/humanoid100_final_eval/final_100_selected_overlay_videos/`,
  `results/humanoid100_final_eval/k1_baseline_overlay_videos/`, and
  `results/humanoid100_final_eval/before_after_overlay_videos/`.

## Existing Weak Evidence

- `configs/prompt_suite_105.csv` is not 100 unique prompts; it is 15 exposed
  modes x 7 seeds.
- Prompt alignment is proxy-based and does not prove semantic matching.
- Prior PD/computed-torque videos are qualitative failure baselines, not final
  execution evidence.
- Old SONIC debug videos using the native C++ visualizer are misleading for
  MotionBricks references because the debug publisher used fixed measured root
  translation.
- True MotionBricks fine-tuning is not currently supported by the local preview
  release in a physically-aware, scientifically valid way; the available scripts
  train on synthetic tensors.
- Prospective feature calibration is weak on the final low-root-gated
  320 selected-rollout table: contact artifact score is the best scalar at
  about AUC 0.554 for native
  strict pass. This is not enough for heuristic-only selection claims.
- `best_precontroller` and `gated_precontroller` selected the same candidate for
  74/80 identities in the current low-root-gated run. Duplicate native rollouts
  disagreed on strict pass for 20/74 same-candidate identities, so the release
  protocol has measurable repeat-run variability. Claim the observed paired
  improvement, not that the gate alone causally explains every rescue.
- Older visual descriptions may have inverted the color convention. In
  `render_sonic_actual_sim_examples.py`, white/left is the MotionBricks/SONIC
  reference and red/right is the actual SONIC simulator qpos.
- The learned native-acceptance model is trained on selected references from
  one prospective run. It is not a generator, not MotionBricks fine-tuning, and
  not yet validated as a prospective selector on a new native batch.
- The broad13 learned acceptance model improves cross-validated prediction but
  still has fold variability and is trained on noisy native rollout outcomes.
  It should not be described as physical feasibility certification until a new
  prospective select-and-rollout batch validates it.
- The prospective learned selector does not beat the hand-coded gated selector
  on the current broad13 run: 76/104 strict versus 78/104. Its upright split is
  also lower, 68/80 versus 71/80. The learned model is useful, but not a
  replacement for hard root/contact/category gates.
- The first hybrid queue also does not create a new headline win: 74/88 strict
  among accepted identities after native label closure. It confirms that the
  next selector needs an explicit root-drift/idle-position sanity term in
  addition to learned score.
- The prospective learned selector is not a fully clean deployment validation:
  it selects from the same broad13 candidate pool used for training labels.
  46/104 selected candidates were already native-evaluated, while 58/104 were
  newly evaluated in this run. The newly evaluated subset is 37/58 strict,
  dragged down by 0/15 newly evaluated crawling references.
- Crawling and low-posture modes remain outside the current strong-success
  claim. The broad13 completed run has 0/53 crawling native survivals and
  0 strict crawling passes in the prospective category table; current evidence
  supports rejection/exposure of this class, not successful generation.
- In the learned prospective rollout, both crawling modes still fail completely:
  0/16 survivals and 0/16 strict passes. This is now a repeated negative result,
  not a one-off artifact.
- The 100-prompt proxy experiment is not a 100-prompt semantic success result:
  78/100 prompts are forced nearest-mode proxies because the local MotionBricks
  preview does not expose arbitrary text-conditioned generation for those
  behaviors. The repair stage can lower dynamics risk for the proxy motion, but
  it cannot make a proxy walk/low crawl satisfy a cartwheel, baseball, soccer,
  or object-manipulation prompt.
- Retiming changes duration and tempo. It should be reported as a
  controller-friendly reference-conditioning baseline, not as preserving the
  original generated motion exactly.
- The 100 all-prompt overlay videos are still approximate SONIC/MuJoCo bridge
  videos, not official native SONIC certification. They are useful for
  visually auditing the red reference ghost versus the solid physics robot and
  for comparing K=1 against the selected verifier result, but final claims
  should keep the "improved but not solved" boundary.
- Latest native K1024-targeted evidence improves the strict native SONIC number
  to a projected 84/100, with 100/100 reference-aware no-fall. This is the best
  result, but not a 100/100 strict result and not a prompt-semantic success
  guarantee.
- Retiming/smoothing, root angular-velocity correction, and a partial
  upright-safe projection probe all failed to rescue the remaining 16
  floor/low-posture and acrobatic prompts. Current evidence says the hard
  frontier is contact-mode support, not just insufficient sampling.
- A controller-manifold projection baseline is the first method to move the
  hard cluster substantially. Exporting the actual native SONIC rollout qpos as
  a new reference rescues 8/16 remaining hard prompts. Iterating the projection
  rescues two more prompts and then saturates: projection iterations 1-4 give an
  experimental 94/100 strict native table with 100/100 reference-aware no-fall.
  This should be presented as execution distillation/projection, not as pure
  MotionBricks prompt-faithful generation.

## Evidence Needed Next

- Broader prompt/source coverage beyond the 10 exposed upright MotionBricks
  modes used in the prospective native-selection run.
- Rendered videos where metric risk corresponds to visible artifacts.
- A clean artifact index so the user can review only current final evidence.
- Human review of the new `results/current_validated/diagnostic_contact_videos/`
  and paired comparison sheets before making presentation clips.
- A hybrid learned-plus-hard-gate prospective rollout. The current learned model
  should not be allowed to select unsupported crawling/low-posture references
  for the upright native-SONIC acceptance claim.
