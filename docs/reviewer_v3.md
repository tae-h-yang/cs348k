# Reviewer V3

## Verdict

Weak reject at a SIGGRAPH/robotics-systems bar. Borderline or weak accept as a
CS 348K project/presentation if framed narrowly as **heuristic
inverse-dynamics screening of MotionBricks candidates**, not as physical
feasibility, controller success, or semantic text-to-motion improvement.

## Top Rejection Reasons

1. The main quantitative win is partly metric self-optimization: candidates are
   selected with an inverse-dynamics-style critic and evaluated with a related
   full inverse-dynamics heuristic.
2. No learned tracking policy or hardware validation exists. The
   computed-torque result is actively negative: all K=1 and K=8 rollouts fall at
   frame 15, K=8 tracking RMSE is not better, and K=8 risk-vs-tracking
   correlation is rho=-0.078, p=0.637.
3. Critic-accept labels are hand-defined critic thresholds, not validation
   labels calibrated against controller success or hardware logs.
4. K=1 is deterministic argmax while K>1 changes both sample count and sampling
   mode. Diversity ablations help but do not remove this vulnerability.
5. Prompt/task preservation is weakly supported: mean proxy alignment drops
   from 0.583 to 0.568, only 56/105 are within -0.05 of K=1, and 72/105 keep
   displacement ratio in [0.5, 1.5].

## Prompt/Contact Audits

The prompt audit improves scope control but should be described as damage
auditing, not alignment improvement.

The contact audit materially helps presentation because it adds an independent
visible diagnostic: artifact score improves from 0.274 to 0.248, while crawling
is exposed as still bad. It remains post-hoc and does not replace controller
validation.

## Required Framing

Strongest honest talk sentence:

> Best-of-K substantially reduces a transparent inverse-dynamics heuristic on
> MotionBricks G1 references; prompt/contact audits show the reduction is not
> purely nonsense; computed-torque tracking fails uniformly, so this is a
> screening layer before learned tracking, not physical execution.

## Required Next Experiment

Run paired K=1/K=8 references through a competent learned G1 tracking policy and
report success rate, time to fall, tracking error, contact artifacts, and torque
usage. Without that, a robotics physical-execution paper remains weak reject.
