# Author Response V3

## Changes Made After Severe Review

- Reframed the paper as risk reranking under a transparent heuristic, not
  independent physical validation.
- Added an abstract caveat that selection and evaluation use related heuristic
  scores.
- Renamed paper action labels to `critic-accept`, `critic-review`, and
  `critic-reject` to avoid implying safety.
- Clarified that the main results measure the implemented segment-critic
  selector, not an oracle best-of-K upper bound.
- Added a boundary audit summary in `paper/main.tex` with risk, prompt proxy,
  contact artifact, and controller outcomes side by side.
- Strengthened the negative controller paragraph: under the available
  forward-simulation controllers, lower heuristic risk does not translate into
  better tracking.
- Updated `docs/final_report.md`, `README.md`, `docs/presentation_notes.md`,
  and `claude.md` to use critic-label language.

## Remaining Weakness

The core reviewer objection remains correct. The project is class-presentation
ready, but a SIGGRAPH/robotics physical-execution claim needs learned G1
tracking-policy validation or hardware rollout.

## Presentation Position

Present the method as a transparent triage layer:

1. MotionBricks produces strong kinematic candidates.
2. Best-of-K reduces inverse-dynamics heuristic demand.
3. Prompt/contact audits show what is preserved and what still fails.
4. Computed-torque tracking failure is the reason this is not yet physical
   execution.
