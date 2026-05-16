# Candidate Methods

## M0: Naive Generator Sample

Use the first generated MotionBricks candidate for each task.

Evidence role: baseline.

## M1: Inverse-Dynamics Best-of-K

Generate K candidates and select the lowest inverse-dynamics risk score.

Expected strengths: cheap, deterministic after candidates exist, catches large
torque/root-wrench demands.

Known weakness: low replay demand does not guarantee closed-loop tracking or
prompt preservation.

## M2: Rule-Based Physics and Contact Gates

Reject candidates with severe self-contact, non-foot floor contact, foot skate,
joint-limit violations, root height collapse, or torque-limit exceedance before
ranking.

Expected strengths: transparent failure reports and easier video overlays.

Known weakness: rules can reject stylized but valid motions or miss controller
instability.

## M3: MotionSpec Predicate Reranker

Convert each prompt into checkable predicates: root direction, speed band,
posture, expected arm role, expected contacts, forbidden contacts, and event
order. Select candidates that satisfy the most predicates, using physics risk as
a secondary term.

Expected strengths: directly addresses prompt alignment and provides readable
failure reports.

Known weakness: requires careful predicate design and cannot replace a true
learned language-motion metric.

## M4: Controller-in-the-Loop Selector

Run candidates through SONIC or another learned G1 tracking policy and select by
survival time, tracking RMSE, fall status, and effort.

Expected strengths: best direct evidence that a reference is useful for robot
control.

Known weakness: expensive; current Python SONIC bridge is approximate; native
policy integration remains a blocker.

## M5: Learned Critic

Train a lightweight ranker from physics, contact, MotionSpec, controller, and
visual labels.

Expected strengths: fast selection at larger K and a path toward generator
preference tuning.

Known weakness: only as good as labels; prior heuristic-only neural critic
mostly learned the heuristic rather than proving execution quality.

## Current Recommendation

Lead with M4 when reliable controller rollouts are available. Use M2 and M3 as
explainable pre-filters. Keep M1 as a diagnostic baseline, not the headline.

