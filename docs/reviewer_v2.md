# Reviewer V2: Expert-Level Critique After 105-Identity Extension

## Summary

The revised project is substantially more defensible than the earlier
"evaluation-only" framing. It now has a clear systems contribution:
best-of-K inference-time sampling for MotionBricks references, ranked by a
transparent inverse-dynamics heuristic. The 105-identity extension addresses
the most obvious sample-size objection, and the negative controls prevent the
paper from overclaiming physical execution.

My recommendation for a class presentation is **presentable with caveats**. My
recommendation for a SIGGRAPH/robotics paper would still be **weak reject**
without learned-controller validation, but the failure mode is now precise and
research-interesting rather than embarrassing.

## Strengths

1. **Clear problem-motivation fit.** MotionBricks explicitly identifies physical
   awareness as a limitation. This project attacks that exact interface.
2. **Simple, reproducible intervention.** No retraining, no hidden controller,
   no ambiguous reward model. The method is understandable in one slide.
3. **Scale improved.** The 105 paired K=1/K=8 run is no longer a tiny anecdote.
   The 61.55% aggregate risk reduction and 78/105 accepted labels are strong
   within the heuristic metric.
4. **Boundary cases are credible.** Static regression and crawling failures are
   not hidden. That makes the work look like research, not a demo.
5. **Negative controls are included.** The report admits that PD and
   computed-torque tracking do not validate per-clip critic scores.

## Remaining Major Concerns

1. **Physical validity is not established.** The critic is inverse-dynamics
   demand, not successful execution. Without PHC/CLAW-style tracking or hardware
   rollouts, the paper must not claim executable motion.
2. **Semantic preservation is incomplete.** 15/39 original benchmark pairs
   change root displacement outside the 0.5x-1.5x band. The method may choose a
   lower-risk but different path/scale.
3. **No comparison to learned physical-aware generation.** RoboForge/CLAW-style
   methods are stronger baselines conceptually, though likely out of scope for
   the class project.
4. **Candidate audit is small.** Segment/full winner agreement is 10/10 in the
   audit, useful but not enough to prove agreement across all prompts.
5. **Heuristic weights are hand chosen.** The score is transparent, but
   sensitivity analysis over weights would strengthen the claim.

## Presentation Guidance

Lead with:

- "This is a screening/ranking layer, not a controller."
- 105-identity result: 35.32 -> 13.58 mean risk, 25/105 -> 78/105 accepted.
- Boundary cases: crawling remains high demand, idle should skip resampling.
- Negative controls: current controllers do not validate per-clip feasibility.

Do not say:

- "physically feasible motion,"
- "safe for the G1,"
- "the critic proves crawling is impossible,"
- "the selected clips will track better,"
- "real-time K=8 generation."

## What Would Make It Conference-Level

1. Import or train a learned G1 tracker and evaluate K=1 vs K=8 references.
2. Add self-collision and support/contact consistency to the critic.
3. Improve the full-clip neural selector: the 210-clip follow-up reaches
   rho=0.747, and the larger 3.38M-parameter/800-epoch model trained on 497
   unique clips reaches rho=0.800. This is better, but still below the 0.85
   target for replacing the heuristic selector.
4. Report semantic preservation against prompt/task metrics, not only risk.
5. Compare to physical plausibility optimization or planner-policy co-training.

## Verdict

For the Stanford class presentation: **yes, present it**, using the cautious
framing in `docs/presentation_notes.md`.

For an external paper: **not yet**, but it has a clean path. The next experiment
is learned tracking-policy validation; everything else is secondary.
