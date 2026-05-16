# Problem Definition

## Problem

Kinematic humanoid motion generators can produce references that look plausible
as animation but fail as robot motion data. The failure modes are mixed:
semantic mismatch to the requested task, root/contact artifacts, joint or torque
demands beyond robot limits, self-collision, and failure under a learned tracking
controller.

The project asks whether we can improve the usefulness of generated humanoid
motion references for robotics by adding a structured inference-time curation
loop.

## Target Claim

For a fixed generator and robot embodiment, candidate curation can improve the
quality of selected motion references by combining:

- prompt-derived MotionSpec predicates,
- kinematic and contact checks,
- inverse-dynamics demand,
- learned-controller rollout metrics,
- visual audit for semantic and artifact failures.

## Non-Claims

- We do not claim the current local MotionBricks preview supports arbitrary
  natural-language generation.
- We do not claim inverse dynamics alone guarantees robot execution.
- We do not claim the current approximate SONIC Python harness is equivalent to
  native SONIC deployment or hardware rollout.
- We do not claim best-of-K is a final training method; it is a screening and
  evidence-gathering method.

## Success Criteria

A presentable result should show, on a nontrivial benchmark slice:

- better prompt/task predicate pass rate than naive selection,
- lower physics/contact artifact rate,
- better controller tracking survival or RMSE under the same policy,
- qualitative videos where improvements are visible,
- honest failure cases and a credible path to generator or policy training.

