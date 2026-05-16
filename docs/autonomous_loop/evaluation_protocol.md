# Evaluation Protocol

## Units

- Prompt/task: one distinct intent from `configs/humanoid_robotics_100_prompts.csv`.
- Identity: a prompt plus seed/control condition.
- Candidate: one generated qpos clip for an identity.
- Selection method: a rule that chooses one candidate per identity.

## Prompt and Task Alignment

Minimum:

- MotionSpec predicate pass rate.
- Direction/progress, speed band, posture band, arm-role, and event-order checks.
- Pairwise preservation between baseline and selected candidate.

Desired:

- Rendered video or contact-sheet audit with human or VLM scores.
- Learned text-motion retrieval metric if a compatible evaluator is available.

## Physical Plausibility

Report per clip and aggregate:

- finite qpos/qvel/qacc validity,
- joint-limit margin,
- foot skate during foot contact,
- non-foot floor contact frames,
- self-contact frames and penetration depth,
- root height collapse,
- inverse-dynamics torque-limit exceedance,
- unactuated root wrench demand,
- support-proxy violations.

## Controller Validation

Run the same selected references through the same controller setup:

- fall rate,
- survival time,
- joint tracking RMSE,
- root tracking RMSE where reliable,
- effort/torque proxy,
- video audit of policy body versus reference.

SONIC results must be labeled according to harness fidelity:

- native SONIC example: sanity check of installed policy,
- approximate Python MuJoCo bridge: experimental selector signal,
- native reference-tracking evaluation: publishable controller evidence.

## Visual Audit

Each presentation video should show:

- prompt or task ID,
- selection method,
- risk badges for prompt, contact, dynamics, and controller,
- reference and tracked body with consistent initial alignment,
- no overlapping labels.

For automated visual review, sample start/middle/end frames plus high-risk
frames from the metric timeline.

