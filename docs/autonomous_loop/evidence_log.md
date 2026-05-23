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
- Crawling and low-posture modes remain outside the current strong-success
  claim. The broad13 completed run has 0/53 crawling native survivals and
  0 strict crawling passes in the prospective category table; current evidence
  supports rejection/exposure of this class, not successful generation.

## Evidence Needed Next

- Broader prompt/source coverage beyond the 10 exposed upright MotionBricks
  modes used in the prospective native-selection run.
- Rendered videos where metric risk corresponds to visible artifacts.
- A clean artifact index so the user can review only current final evidence.
- Human review of the new `results/current_validated/diagnostic_contact_videos/`
  and paired comparison sheets before making presentation clips.
