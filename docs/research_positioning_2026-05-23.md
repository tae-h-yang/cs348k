# Research Positioning, 2026-05-23

## Bottom Line

The result is submittable as a course final project if framed as
**controller-in-the-loop curation and abstention for kinematic humanoid
references**. It is not submittable as a claim that we fine-tuned MotionBricks,
solved physical motion generation, or beat the best hand-coded gate.

## Why This Framing Matches Current Research

Recent humanoid motion work is converging on the same lesson: kinematic motion
generation and physical execution must be coupled through tracking policies,
physical feedback, or adaptation.

- MotionBricks gives scalable real-time kinematic motion generation, but its
  limitation section explicitly leaves physical awareness as an open issue.
  Our work studies that limitation directly for Unitree G1 references.
- SONIC scales humanoid motion tracking with large policy/data/compute. This
  makes native tracker outcome a much better acceptance label than a weak PD
  baseline or inverse dynamics alone.
- GMT and SMAP emphasize broad motion tracking/adaptation rather than treating
  raw kinematic clips as final executable robot motion.
- RLPF is the closest conceptual next step: use physical feedback to align a
  motion generator. Our current project is the smaller pre-training-data step:
  collect acceptance labels and learn a triage model, but do not yet update the
  generator.
- MoVer motivates structured motion verification: our MotionSpec/contact/root
  gates are a robotics-flavored verification layer, but native SONIC remains
  the stronger execution oracle.

Primary sources checked:

- MotionBricks, arXiv:2604.24833,
  <https://arxiv.org/abs/2604.24833>
- SONIC, arXiv:2511.07820,
  <https://arxiv.org/abs/2511.07820>
- GMT, arXiv:2506.14770,
  <https://arxiv.org/abs/2506.14770>
- SMAP, arXiv:2505.19463,
  <https://arxiv.org/abs/2505.19463>
- RL from Physical Feedback, arXiv:2506.12769,
  <https://arxiv.org/abs/2506.12769>
- MoVer project page,
  <https://mover-dsl.github.io/>

## Current Evidence

Native SONIC broad13:

| Method | Strict native pass |
|---|---:|
| Deterministic MotionBricks baseline | 70/104 |
| Hand-coded gated pre-controller selector | 78/104 |
| Learned acceptance selector | 76/104 |
| Learned abstention, score >= 0.5 | 76/88 accepted |
| Hybrid hard-gate + learned ranking | 74/88 accepted |

Learned acceptance prediction:

| Predictor | AUC | AP |
|---|---:|---:|
| Temporal qpos CNN | 0.864 | 0.917 |
| Best scalar, root-z min | 0.782 | 0.865 |
| Pre-controller score | 0.752 | 0.845 |

Visual audit:

- Learned prospective rollout: 104 videos, 27 pass, 61 warn, 16 fail.
- Strict native passes with visual-fail flags: 1/76.
- Hybrid newly evaluated clips: 9/9 visual pass, 0 visual fails.

## Submittable Claim

> We train and evaluate a trajectory-level native-acceptance model for fixed
> MotionBricks G1 references. It predicts SONIC strict acceptance better than
> scalar diagnostics and helps identify when the system should abstain. The best
> current full-coverage selector remains hand-coded gating, so the scientific
> contribution is a measured controller-in-the-loop curation pipeline, not a
> solved generator.

## Claims To Avoid

- MotionBricks has been fine-tuned.
- Generated motions are guaranteed physically feasible.
- Crawling or low-posture motion is solved.
- The learned selector beats the hand-coded gated selector.
- Pixel visual audit is equivalent to full human validation.
- The learned rollout is a fully clean deployment split; it samples from the
  same broad13 pool used for training labels.

## Best Next Pivot

Do not spend another cycle on inverse-dynamics-only scoring. The strongest next
research direction is **physical-feedback learning**:

1. Generate a fresh broad candidate pool.
2. Run native SONIC for a diverse subset, including repeated rollouts for label
   noise.
3. Train an acceptance/abstention model with explicit root-drift and idle
   sanity terms.
4. Use the model as a reward or preference signal to steer generation, following
   the RLPF/physical-feedback direction rather than merely filtering after the
   fact.

For the current course deadline, the honest final is the controller-in-the-loop
curation study.
