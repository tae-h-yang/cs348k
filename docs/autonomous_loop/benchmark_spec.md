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
- Covers dynamic locomotion, jumps/hops, hip-hop-style footwork and other
  expressive motions, floor/crawling motions, loco-manipulation, manipulation
  stance, balance recovery, communication/safety, terrain proxies, and
  high-risk athletic stress tests.
- Current composition: only 21 prompts contain the word `walk`; at least 8
  contain jump/hop/skip/bound motions and at least 17 contain crawl/floor/roll/
  kneel/plank/handstand/cartwheel-style floor transitions.
- Includes success criteria, expected contacts, root motion, arm role, hardness,
  and current MotionBricks support labels.
- Use for problem definition, future generator testing, and reviewer-facing
  benchmark scope.

### Layer C: Sports/Acrobatics Stress Suite

`configs/sports_acrobatics_stress_prompts.csv`

- 32 distinct high-risk or task-specific prompts spanning cartwheels and other
  acrobatic inversions, soccer, baseball/softball, basketball, racket sports,
  martial-arts-style kicks, and sprint starts.
- This is intentionally separated from the executable 105-row local suite: most
  prompts require sport/task-conditioned generation, object-conditioned
  retargeting, or a richer MotionBricks interface before they can be claimed as
  executable generated motions.
- Current composition: 26 prompts are marked `__NO__` for the local
  MotionBricks preview and 6 are marked `__PARTIAL__` with coarse proxy mode
  hints such as `walk`, `walk_left`, or `walk_happy_dance`.
- Use for stress-testing future methods and for reviewer-facing scope. Do not
  report a proxy mode as a solved soccer/baseball/cartwheel behavior unless it
  passes task-specific event predicates and visual audit.

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

Layer C uses the same schema concept but names the group column `domain`
instead of `category` because each row is a sport/acrobatic domain rather than a
general robotics behavior class.

## Required Splits

When the full 100-prompt suite becomes executable:

- report all 100 prompts,
- report by category,
- keep a held-out reviewer set of at least 20 prompts for qualitative videos and
  manual/VLM audit,
- do not count seed duplicates as new task prompts.

When the sports/acrobatic suite becomes executable, report it separately from
the 100-prompt robotics suite and include per-domain task-event checks. Examples:
cartwheel requires hand contact plus lateral inversion and recovery; baseball
pitch requires a step, overhand arm swing, and follow-through; soccer kick
requires single-support timing and a directed leg swing.

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
