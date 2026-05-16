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
- `scripts/evaluate_sonic_policy_mujoco.py`: approximate SONIC policy bridge.

## Current Generated Outputs

Generated outputs live under ignored `results/`:

- `results/motionspec_predicates.csv`
- `results/motionspec_summary.csv`
- `results/motionspec_selector_comparison.csv`
- `results/motionspec_selector_dashboard.png`
- `results/motionspec_failure_counts.csv`
- `results/motionspec_failure_counts.png`
- `results/prompt_alignment.csv`
- `results/contact_quality.csv`
- `results/sonic_policy_mujoco_tracking_210_fixed.csv`

## Latest Numeric Snapshot

Existing 105 paired K=1/K=8 identities:

| Selector | Mean MotionSpec | Mean Prompt Proxy | Mean Contact Artifact | Mean Approx. SONIC Survival |
|---|---:|---:|---:|---:|
| K=1 baseline | 0.686 | 0.583 | 0.274 | 2.005 s |
| Existing K=8 ID selector | 0.736 | 0.568 | 0.248 | 2.054 s |
| MotionSpec over K=1/K=8 | 0.757 | 0.620 | 0.250 | 2.117 s |
| SONIC oracle over K=1/K=8 | 0.721 | 0.576 | 0.263 | 2.299 s |

Interpretation: MotionSpec curation is promising for selecting between already
generated candidates. Approximate SONIC survival is still short, so this is not
yet a physically executable motion-generation result.

## Next Actions

1. Make a single joined candidate table with one row per clip and all metrics.
2. Add a selector that combines MotionSpec + contact gates + inverse dynamics.
3. Render a small risk-audit set with readable overlays.
4. Investigate whether arbitrary-prompt generation can be accessed or whether
   the 100-prompt suite must be evaluated through another generator/control
   source.
