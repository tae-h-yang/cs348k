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
- Prospective native selection on held-out seeds 7-14 shows a modest real
  improvement from cheap screening: best pre-controller selection reaches 67/80
  strict pass versus 64/80 deterministic baseline, while the native oracle over
  tested selectors reaches 78/80. This is evidence for controller acceptance
  gating, not evidence that cheap metrics certify physical execution.

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
- Prospective feature calibration is weak on the final 320 selected-rollout
  table: contact artifact score is the best scalar at AUC 0.561 for native
  strict pass. This is not enough for heuristic-only selection claims.
- `best_precontroller` and `gated_precontroller` selected identical candidates
  in the prospective run; duplicate native rollouts disagreed on strict pass for
  16/80 identities, so the release protocol has measurable repeat-run
  variability.

## Evidence Needed Next

- Broader prompt/source coverage beyond the 10 exposed upright MotionBricks
  modes used in the prospective native-selection run.
- Rendered videos where metric risk corresponds to visible artifacts.
- A clean artifact index so the user can review only current final evidence.
