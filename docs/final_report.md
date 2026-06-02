# Test-Time Physical Awareness for Generated Humanoid Reference Motions

Tae Hoon Yang  
CS 348K: Visual Computing Systems, Stanford University, Spring 2026

## Abstract

Modern humanoid motion trackers such as SONIC can follow rich whole-body
reference trajectories in physics, but those trackers still need high-quality
reference motions. KIMODO makes reference authoring much easier by generating
Unitree G1 kinematic motions from text prompts and constraints. This project
studies the interface between those systems: given a generated G1 reference,
can we detect physical risks, use those risks to rewrite the prompt, regenerate
better candidates, and then gate the result with a controller rollout?

I built a test-time physical-awareness loop. It evaluates each generated
reference with MuJoCo inverse-dynamics/contact diagnostics and a pretrained
SONIC controller audit. The evaluator emits interpretable failure tags such as
high torque/root wrench, self-contact, non-foot floor contact, weak support,
contact artifact, and controller trackability failure. Those tags are passed as
structured context to GPT-5.5, which rewrites the prompt with a metric-specific
safety constraint. The system then regenerates and re-scores the candidate.

On the 100-prompt KIMODO benchmark, first-pass references pass the physical
screen in 48/100 cases, complete the 4-second SONIC rollout in 53/100 cases,
and pass both gates in 29/100 cases. The final deck reports a prompt-repair
snapshot where metric-guided rewriting reduces several failure tags, including
SONIC fall cases from 47 to 20. The contribution is not a solved text-to-robot
motion generator; it is a concrete evaluation, prompt-repair, and acceptance
gate that exposes where generated references are physically brittle.

## Project Goal

The project asks:

> Can a physical-awareness layer identify risky KIMODO-generated humanoid
> reference motions, and can its failure tags guide useful test-time prompt
> repair before controller execution?

Success is measured at two levels:

- reference-level physical checks: torque/root wrench, contact, support, and
  contact-artifact diagnostics,
- controller-level checks: SONIC no-fall, survival time, and tracking RMSE.

The claim boundary is important. This project does not fine-tune KIMODO, does
not train a new controller, and does not certify hardware safety. It tests
whether metric-derived failure tags can make generated references easier to
screen, repair, and explain.

## System

The final system is a prompt-refinement loop:

| Stage | Input | Contribution | Output |
|---|---|---|---|
| Generate | text prompt | KIMODO G1 reference generation | root + joint trajectory |
| Evaluate | generated reference | MuJoCo dynamics/contact checks + SONIC rollout | risk flags and rollout metrics |
| Rewrite | failed metric tag | GPT-5.5 adds a tag-specific prompt constraint | revised prompt |
| Repeat / gate | new candidate | rescore until no flag or budget ends | accepted, flagged, or rejected clip |

Failure tags are intentionally interpretable. For example, a high torque/root
wrench tag asks the LLM for slower, smoother limb motion; a self-contact tag
asks for limbs away from the torso; a weak support tag asks for wider stance
and smaller center-of-mass shifts; a trackability tag asks for lower speed and
amplitude.

SONIC is used as a foundation-style tracking evaluator and acceptance gate. It
is not the optimizer that edits KIMODO. The prompt is edited by the LLM, guided
by deterministic failure tags.

## Benchmark

The benchmark contains 100 humanoid robotics prompts. They are deliberately
broader than walking-only examples:

| Family | Count | Example prompt |
|---|---:|---|
| locomotion + recovery | 26 | "Walk forward at a comfortable indoor pace." |
| manipulation + loco-manipulation | 26 | "Step forward, reach with the right hand as if opening a door." |
| floor / low posture | 12 | "Crawl forward using hands and feet." |
| dance / expressive | 12 | "Do an energetic happy dance with bouncing knees." |
| athletic + terrain stress | 16 | "Perform a small split-squat jump." |
| communication / safety | 8 | "Stand still and wave the right hand at shoulder height." |

The suite includes walking, shuffling, crawling, carrying, panel pressing,
gestures, obstacle-style steps, forward rolls, cartwheel attempts, jumping, and
low-posture motions. Some prompts are beyond the current generator/controller
coverage; those failures are useful stress tests rather than merely bad demos.

## Evaluation

For each generated G1 trajectory, the evaluator computes:

- torque demand relative to actuator limits,
- unactuated root force and root torque,
- velocity, acceleration, and jerk,
- self-contact,
- non-foot floor contact,
- foot-contact quality and contact artifacts,
- support-region proxy violations,
- SONIC no-fall, survival time, and joint RMSE.

The screen is not a single magic score. It is a collection of failure signals
that can disagree. A physical-pass reference can still fail SONIC; a physically
flagged reference can sometimes still be tracked. That disagreement is one of
the useful results.

## Results

### First-Pass KIMODO Audit

| Set | Physical pass | SONIC no-fall | Both gates | Mean SONIC sec. | Mean RMSE |
|---|---:|---:|---:|---:|---:|
| all KIMODO references | 48/100 | 53/100 | 29/100 | 2.855 | 0.156 |
| physical-pass subset | 48/48 | 29/48 | 29/48 | 3.293 | 0.170 |
| flagged subset | 0/52 | 24/52 | 0/52 | 2.450 | 0.143 |

![KIMODO audit summary](../slides/assets/figures/kimodo_audit_summary.png)

Only 29 of 48 physical-pass references also complete SONIC. Meanwhile, 24 of
52 flagged references still complete SONIC. This means the physical screen is a
useful risk signal, but not a complete controller-success predictor.

### Failure Tags

The final slide deck summarizes the main non-exclusive failure tags:

| Failure tag | Before prompt repair | After prompt repair |
|---|---:|---:|
| SONIC fall | 47 | 20 |
| torque limit > 1x | 48 | 23 |
| self-contact > 8% | 34 | 10 |
| unstable center of mass | 31 | 20 |
| high root force > 5 kN | 28 | 9 |
| non-foot floor contact | 11 | 4 |

The failure tags are non-exclusive, so reductions do not sum to the SONIC-fall
reduction. The key point is that the metric labels are actionable: they tell
the prompt rewriter what physical constraint to add.

The representative failure videos in the deck are:

| Failure family | Example |
|---|---|
| torque/root wrench | `hrb_094_forward_roll` |
| self-contact | `hrb_005_turn_in_place` |
| non-foot floor contact | `hrb_098_knee_slide` |
| support proxy | `hrb_085_step_over_right` |
| controller trackability | `hrb_051_carry_box` |
| contact artifact | `hrb_018_happy_dance` |

### Repair Examples

The main repair videos show failure-tag-guided prompt edits:

| Prompt | Caught issue | Prompt edit shown in deck |
|---|---|---|
| `forward_walk` | trackability | slower, smoother steps |
| `wave` | torque / tracking | planted feet, smooth arm |
| `split_squat_jump` | support / torque | smaller jump, soft landing |
| `pushup_pose` | non-foot floor | lift torso clearance |
| `happy_dance` | contact artifact | clean foot placement |
| `backward_recovery` | support proxy | smaller lean, step back |

The deck also includes a boundary slide with failed runs that remain hard:
`forward_roll` for torque/root wrench, `carry_box` for controller
trackability, and `cartwheel_attempt` for acrobatic torque/root-wrench stress.

## Qualitative Artifacts

The presentation-critical artifacts are:

- [Slide PDF](../slides/build/deck.pdf)
- [Slide PPTX](../slides/build/deck.pptx)
- `slides/assets/videos/kimodo_repair_rescues/`
- `slides/assets/videos/kimodo_repair_rescues_presentation/`
- `slides/assets/videos/appendix_metric_failures/`
- `slides/assets/videos/boundary_still_fails/`
- `slides/assets/figures/kimodo_audit_summary.png`
- `slides/assets/figures/kimodo_failure_flag_counts.png`

Experiment videos use the same convention unless noted otherwise: red
translucent G1 is the reference target, and solid G1 is the MuJoCo/SONIC
physics rollout.

## Interpretation

The results support the project hypothesis in a bounded way:

- generated references have measurable physical failure modes,
- failure tags are useful for prompt refinement and curation,
- SONIC is stricter than kinematic replay,
- visual/VLM review helps catch obvious behavior mismatch, but it is not a
  complete metric set.

The current method still fails on arbitrary text-to-robot motion, robust
acrobatic tracking, low-posture tracking, and automatic repair for every
invalid reference. Stronger results likely require fine-tuning or training a
motion-level refiner, not only prompt rewriting.

## Runtime Snapshot

The deck appendix records prototype timings:

| Stage | Measured run | Average |
|---|---:|---:|
| KIMODO generation | 100 clips in 44.4 min | 26.6 s / clip |
| physics + SONIC checks | 100 clips in 2.3 min | 1.4 s / clip |

These timings include prototype overhead and are not claims of model-optimal
latency.

## Limitations

- GPT-5.5 prompt repair is useful but cannot replace a better motion generator.
- The physical screen is heuristic and simulator-dependent.
- SONIC rollout is a simulation diagnostic, not real hardware validation.
- Some motions need semantic context: floor contact can be correct for crawling
  and wrong for walking.
- Prompt fidelity is checked qualitatively; there is no full human-study or
  VLM benchmark.

## Future Work

The next step is to train a risk-conditioned refiner that learns from the
failure tags and SONIC rollouts. A stronger version would change the motion
trajectory itself, not only the prompt. Another direction is to use short
controller rollouts or a learned surrogate during candidate selection so that
the generator is steered by trackability earlier.

## References

- Rempe et al. **Kimodo: Scaling Controllable Human Motion Generation.**
  NVIDIA Research / arXiv, 2026.
- Luo et al. **SONIC: Supersizing Motion Tracking for Natural Humanoid
  Whole-Body Control.** NVIDIA Research / arXiv, 2025.
- Todorov, Erez, and Tassa. **MuJoCo: A Physics Engine for Model-Based
  Control.** IROS, 2012.
