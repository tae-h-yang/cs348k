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

## Evidence Needed Next

- Completed all-210 native SONIC validation for the exposed K=1/K=8 candidate
  set.
- Prospective controller-aware selection comparison where winners are chosen
  before native rollout on a held-out candidate pool.
- Rendered videos where metric risk corresponds to visible artifacts.
- A clean artifact index so the user can review only current final evidence.
