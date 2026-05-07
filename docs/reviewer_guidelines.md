# Reviewer Guidelines

Please review this project at a SIGGRAPH/robotics-systems bar. Do not be nice
for morale; be useful for acceptance.

## Current Claim

The paper claims a zero-training inference-time screening method for
MotionBricks-style kinematic Unitree G1 motions:

1. Generate K candidates per local mode-control prompt.
2. Score them with a MuJoCo inverse-dynamics heuristic critic.
3. Select the lowest-risk candidate.
4. Report risk, prompt/task proxy preservation, contact artifacts, and negative
   controller validation.

## What The Review Should Check

- Is the contribution more than "evaluate MotionBricks"?
- Is best-of-K screening positioned honestly as a test-time method rather than
  a trained model?
- Are baselines fair enough for a class/research prototype?
- Are prompt/task-following metrics credible given that the local release is
  mode/control based rather than arbitrary text?
- Are inverse-dynamics, contact, and support metrics meaningful and correctly
  limited?
- Do the negative PD/computed-torque results undermine the paper or merely set
  a clear boundary?
- Is the missing learned tracking-policy validation fatal for SIGGRAPH, and if
  so what exact experiment would repair it?
- Are figures/videos sufficient for an expert audience to inspect risk?
- Are claims phrased so they cannot be mistaken for hardware safety?

## Key Files

- `docs/final_report.md`
- `docs/evaluation_protocol.md`
- `docs/prompt_suite.md`
- `docs/presentation_notes.md`
- `paper/main.tex`
- `results/guided_ablation_extended_summary.csv`
- `results/prompt_alignment_summary.csv`
- `results/contact_quality_summary.csv`
- `results/computed_torque_tracking_summary.csv`

## Desired Output

Return:

1. Verdict: strong accept, accept, weak accept, borderline, weak reject, reject.
2. Top 5 reasons.
3. Fatal missing experiments.
4. Specific edits that would make the paper harder to reject.
5. Whether the current project is class-presentation-ready.
