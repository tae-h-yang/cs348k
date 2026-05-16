# Blockers

## True 100-Prompt Generation

The current local MotionBricks preview exposes discrete G1 modes. A 100-prompt
benchmark can be specified now, but executing all 100 as distinct natural
language tasks requires either:

- a full MotionBricks text/control interface,
- a richer control-primitive layer,
- a different generator,
- or a learned planner/policy stack trained for those task classes.

## Reliable Controller Evidence

The Python SONIC bridge is approximate. It can guide experiments, but a final
paper-level claim needs native SONIC reference tracking, an official policy
rollout path, or another trusted learned G1 controller.

## Semantic Evaluation

Current prompt alignment is hand-engineered. A stronger evaluation needs either:

- MotionSpec predicates with human-readable failure reports,
- human pairwise review,
- VLM video/frame audit,
- or a learned text-motion evaluator compatible with G1 motion.

## Artifact Sprawl

The repo has many prior result folders. Future work should update
`docs/artifact_inventory.md` and keep current-final videos in clearly named
folders rather than mixing them with failed debug artifacts.

