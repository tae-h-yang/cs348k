# Autonomous Loop Readme

Last updated: 2026-05-16.

## North Star

Build a defensible research project about curating high-quality humanoid robot
motion data from kinematic generators. The current strongest direction is:

> generate multiple candidate references, verify prompt/task predicates, reject
> obvious physics/contact failures, and select candidates using controller
> rollout evidence when available.

This replaces the weaker claim that inverse dynamics alone makes MotionBricks
motions executable.

## Current Truth

- The repo can call a real local MotionBricks G1 preview through the sibling
  `GR00T-WholeBodyControl/motionbricks` checkout.
- The exposed local interface is discrete mode/control based, not a true
  arbitrary 100-prompt text-to-motion endpoint.
- `configs/prompt_suite_105.csv` has 105 rows but only 15 unique local behavior
  prompts expanded by seed.
- SONIC is useful as a direction for controller-in-the-loop selection, but the
  current Python harness is approximate and should not be presented as native
  hardware-quality validation.
- The project now needs a cleaner benchmark, a verifier, and a controller-aware
  experiment loop.

## Working Tree

- `problem_definition.md`: project claim, non-claims, and success criteria.
- `benchmark_spec.md`: target 100-prompt benchmark and schema.
- `humanoid_robotics_100_prompts.md`: generated summary of the prompt suite.
- `candidate_methods.md`: method families to test and expected evidence.
- `evaluation_protocol.md`: metrics and pass/fail criteria.
- `research_notes.md`: related work notes with source links.
- `evidence_log.md`: what prior artifacts show and what they do not show.
- `experiment_queue.md`: next experiments and commands.
- `run_journal.md`: chronological decisions and results.
- `blockers.md`: technical blockers and how to retire them.

## Immediate Next Loop

1. Generate and validate `configs/humanoid_robotics_100_prompts.csv`.
2. Implement a MotionSpec predicate layer for the executable subset and desired
   100-prompt schema.
3. Run a small controller-in-the-loop baseline slice on existing K candidates:
   compare K=1, inverse-dynamics selection, contact-gated selection, and SONIC
   selector.
4. Render an audit panel where visible risk is obvious, not hidden in CSVs.

## Latest Loop Result

`scripts/evaluate_motionspec.py` now writes:

- `results/motionspec_predicates.csv`
- `results/motionspec_summary.csv`
- `results/motionspec_selector_comparison.csv`
- `results/motionspec_selector_dashboard.png`
- `results/motionspec_failure_counts.png`

On the existing 105 paired K=1/K=8 identities, selecting by MotionSpec over the
two candidates improves mean predicate score to 0.757 and mean prompt proxy
alignment to 0.620. The controller layer remains weak: approximate SONIC falls
are still the dominant failure mode.
