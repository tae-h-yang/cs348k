# Critic Response

> Superseded status note, 2026-05-04: this response predates the 105-identity
> extension, semantic audit, computed-torque negative control, and LaTeX draft.
> Use `docs/author_response_v2.md` as the current response.

This note captures the professor/audience objections that should shape the
final talk. The project is credible if it is presented as a feasibility critic
and reranking prototype. It becomes weak if presented as real-robot safety or a
general motion repair method.

## Claim Narrowing

Original risky wording:

- "hardware/control risk"
- "repairs failures"
- "safest feasible plan"
- "safety critic"

Final wording:

- "heuristic simulation-side feasibility risk"
- "selects among retiming/smoothing variants"
- "lowest-risk candidate under this critic"
- "test-time feasibility critic"

Reason: the results come from MuJoCo inverse dynamics and derivative checks, not
hardware experiments, learned-policy rollouts, or a certified safety model.

## Evidence Upgrades

The main repair/selection result now uses all 39 local MotionBricks clips, not
only the 10 rendered demo examples.

| Question | Response |
| --- | --- |
| Did the method improve the full workload? | Yes. Mean risk 35.43 -> 23.74 across 39 clips. |
| Is 48.0% the same as aggregate reduction? | No. 48.0% is mean per-clip reduction; aggregate reduction is 33.0%. |
| How many clips improved? | 32/39. |
| Did the rejected set disappear? | No. Rejected clips remain 5/39, which is intentional. |
| Is smoothing the win? | No. Smoothing alone is slightly worse than original. Retiming is the main simple intervention. |
| Is seed reranking overclaimed? | It is labeled as best-of-seeds. Aggregate reduction vs random seed is 35.1%; mean per-style reduction is 53.2%. |

## Remaining Weak Spots

- No validation against a learned tracking policy.
- No real Unitree G1 validation.
- No self-collision or detailed contact-quality term.
- Risk weights and thresholds are hand-selected.
- Root wrench is contact/model sensitive; use it as a relative diagnostic only.
- Retiming changes duration and may alter task semantics.

## Prepared Answers

**Is this just slowing everything down?**  
Mostly, yes for the current candidate-selection experiment. That is why the
talk calls it retiming/smoothing selection rather than physical repair. The
interesting result is that the critic tells which clips benefit and which clips
remain too extreme.

**Why is the risk score meaningful?**  
It is transparent and physically motivated: torque-limit ratio, root wrench,
velocity, acceleration, and jerk. It is not calibrated. The next step is to
validate it against tracking-policy outcomes.

**Why include root wrench if idle is already high?**  
Root wrench exposes hidden support needed for exact kinematic replay, but its
absolute magnitude is sensitive to contact modeling. The robust use is relative:
whole-body/crawling is a much larger outlier than upright motion.

**What is the real contribution?**  
A systems prototype that turns MotionBricks' physical-awareness limitation into
an executable evaluation and selection layer: score, retime, rerank, reject.

**What would make it publication-level?**  
Learned tracker validation, self-collision/contact terms, risk-weight ablations,
and integration into MotionBricks sampling or planner-policy co-training.
