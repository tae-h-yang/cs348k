# MotionBricks Local G1 Mode Inventory

The local MotionBricks preview used by this repo exposes a discrete `allowed_mode` interface, not arbitrary open-vocabulary text-to-motion.

Generated a fresh one-seed sanity pass for **15/15 exposed modes** on 2026-05-31.

Artifacts:

- Qpos clips: `results/motionbricks_mode_inventory_20260531_185546/qpos/`
- Reference videos: `results/motionbricks_mode_inventory_20260531_185546/reference_videos/`
- Inventory CSV: `results/motionbricks_mode_inventory_20260531_185546/mode_inventory.csv`

## Exposed Modes

| Mode | Category | Generated | Video |
|---|---|---:|---:|
| `idle` | `static` | True | True |
| `slow_walk` | `locomotion` | True | True |
| `walk` | `locomotion` | True | True |
| `hand_crawling` | `whole_body_low` | True | True |
| `walk_boxing` | `expressive_locomotion` | True | True |
| `elbow_crawling` | `whole_body_low` | True | True |
| `stealth_walk` | `locomotion` | True | True |
| `injured_walk` | `locomotion` | True | True |
| `walk_stealth` | `style_locomotion` | True | True |
| `walk_happy_dance` | `expressive_locomotion` | True | True |
| `walk_zombie` | `style_locomotion` | True | True |
| `walk_gun` | `expressive_locomotion` | True | True |
| `walk_scared` | `expressive_locomotion` | True | True |
| `walk_left` | `directional_locomotion` | True | True |
| `walk_right` | `directional_locomotion` | True | True |

## 100-Prompt Suite Fit

The 100-prompt suite is useful as a robotics stress benchmark, but it is not a 100-supported-mode MotionBricks benchmark. It intentionally contains unsupported manipulation, recovery, terrain, floor, athletic, and acrobatic prompts.

Support labels in `configs/humanoid_robotics_100_prompts.csv`:

- `__NO__`: 78
- `__PARTIAL__`: 14
- `__YES_MODE_PROXY__`: 8

Interpretation:

- `__YES_MODE_PROXY__`: prompt has a reasonably direct local mode proxy.
- `__PARTIAL__`: prompt can be approximated by a mode but should not count as semantic success.
- `__NO__`: outside the current local preview interface; use as stress/negative-control or future-work target.

Mode hints with counts:

- `requires_new_generator_control`: 36
- `requires_task_conditioned_generator_or_retargeter`: 34
- `walk_or_idle_mode`: 11
- `negative_control_high_risk`: 8
- `hand_crawling_or_elbow_crawling`: 3
- `walk_happy_dance`: 2
- `walk_left`: 2
- `walk_boxing`: 1
- `walk_right`: 1
- `walk_scared`: 1
- `walk_zombie`: 1

## Recommendation

Use two separate benchmarks in the story:

1. **Mode-faithful benchmark:** the 15 exposed modes x multiple seeds. This is the fair MotionBricks local-preview evaluation.
2. **Humanoid100 stress benchmark:** 100 robotics prompts that test what a robot-motion generator should eventually cover, with explicit prompt-support labels.

Do not present all 100 rows as if MotionBricks natively supports all 100 natural-language tasks.