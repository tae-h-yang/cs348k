# Author Response V2

## Claim Tightening

We revised the work from "physical feasibility" to "inverse-dynamics heuristic
screening." This addresses the central concern that a risk score is not the same
thing as controller execution.

## New Evidence Added

- **105-identity extension:** all 15 exposed G1 demo modes x 7 seeds. K=8 lowers
  mean risk from 35.32 to 13.58 and improves 81/105 paired identities.
- **Per-type analysis:** locomotion and expressive motions improve strongly;
  crawling remains high demand; static idle regresses and should be gated.
- **Semantic audit:** reports root displacement/path/speed change rather than
  relying on video impressions.
- **Computed-torque negative control:** stronger classical tracking does not
  validate the critic, so the report states that learned tracking is required.
- **Candidate audit:** saves every candidate for 10 representative K=8 batches;
  segment and full critic winners agree in this subset.
- **LaTeX draft:** `paper/main.tex` reframes the result as a screening/ranking
  study with explicit limitations.
- **Extended clip-level neural critic:** retraining on 210 full clips improves
  rho to 0.747, but remains below the 0.85 target, so the heuristic critic stays
  the final selector.
- **Larger clip-level neural critic:** a 3.38M-parameter residual temporal CNN
  trained for 800 epochs on 497 unique labeled clips improves rho to 0.800, but
  still remains below target.

## Unresolved Concerns

- No PHC/CLAW-style learned G1 tracking policy has been trained or imported.
- No hardware validation.
- No full sensitivity analysis over critic weights.
- No full-clip neural selector accurate enough for deployment.
- No self-collision/contact-quality critic terms.

## Final Presentation Position

The class presentation should be framed as:

> A test-time inference-scaling study for kinematic humanoid references. The
> result is strong under inverse-dynamics demand and useful as a pre-tracking
> screen, but final physical feasibility requires learned controller validation.

That position is honest and defensible.
