# Benchmark Spec

## Two Benchmark Layers

### Layer A: Executable Local Suite

`configs/prompt_suite_105.csv`

- 15 exposed MotionBricks G1 modes.
- 7 seeds per mode.
- 105 rows but only 15 unique behavior prompts.
- Use for immediate experiments because clips and metrics already exist.

### Layer B: Target Robotics Suite

`configs/humanoid_robotics_100_prompts.csv`

- 100 distinct humanoid robotics motion intents.
- Covers locomotion, terrain proxies, loco-manipulation, manipulation stance,
  balance recovery, communication/safety, low posture, and workspace tasks.
- Includes success criteria, expected contacts, root motion, arm role, hardness,
  and current MotionBricks support labels.
- Use for problem definition, future generator testing, and reviewer-facing
  benchmark scope.

## Prompt Schema

- `prompt_id`: stable benchmark ID.
- `category`, `subcategory`: grouping for aggregate analysis.
- `prompt_text`: natural-language task.
- `success_criteria`: human-readable event and pose constraints.
- `expected_primary_contacts`: allowed contact types.
- `expected_root_motion`: coarse root trajectory intent.
- `expected_arm_role`: whether arms are natural, expressive, or task constrained.
- `hardness`: rough difficulty estimate.
- `current_motionbricks_support`: current support label.
- `motionbricks_mode_hint`: closest available mode where one exists.
- `evaluation_notes`: intended evaluator stack.

## Required Splits

When the full 100-prompt suite becomes executable:

- report all 100 prompts,
- report by category,
- keep a held-out reviewer set of at least 20 prompts for qualitative videos and
  manual/VLM audit,
- do not count seed duplicates as new task prompts.

## Selector Comparison

For every executable prompt identity, compare:

- first candidate / K=1 baseline,
- inverse-dynamics best-of-K,
- contact-gated selector,
- MotionSpec selector,
- controller-in-the-loop selector,
- combined selector.

Each selected clip must retain the prompt text, candidate ID, metrics, and
failed predicates.

