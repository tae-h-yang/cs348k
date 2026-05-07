# Slide Outline — CS 348K Final Presentation
# "Inverse-Dynamics-Critic-Guided Inference-Time Scaling for Humanoid Motion Generation"

**~12 slides, ~15 minutes**
**Last updated: 2026-05-04**

## Slide 1 — Title + Motivation

**Visual:** K=1 vs K=8 side-by-side reference video.

**Key message:** MotionBricks generates impressive kinematic humanoid motion,
but physical awareness is still an open gap.

## Slide 2 — The Gap

**Visual:** MotionBricks generator -> qpos reference -> tracking policy.

**Text:**
- Kinematic generation can ignore actuator demand, balance support, and contact.
- Recent G1 systems validate references through low-level controllers.
- This project asks: can a cheap test-time critic screen bad references before
  tracking?

## Slide 3 — The Critic

**Visual:** MuJoCo `mj_inverse` pipeline and one risk-explainer video frame.

**Key message:** Exact replay inverse dynamics estimates required joint torques
and unactuated root wrench. The score is transparent but heuristic.

**Say explicitly:** accept/review/reject are critic labels, not robot safety labels.

**Show briefly:** `results/videos/risk_explainer/walk_seed0_K1_vs_K8_risk_explainer.mp4`
so the audience sees risk as timeline spikes, component bars, and top
torque-limited joints.

## Slide 4 — Best-of-K Test-Time Scaling

**Visual:** K candidates from one prompt/mode, critic selects lowest risk.

**Key message:** This is best-of-N inference scaling translated to kinematic
humanoid motion. No MotionBricks retraining.

## Slide 5 — Main K Sweep

**Visual:** `results/guided_risk_vs_K.png`.

**Numbers:**
- K=1 mean risk 38.90, 5/39 accepted.
- K=8 mean risk 15.93, 26/39 accepted.
- K=16 mean risk 13.61, 31/39 accepted.

**Interpretation:** Most gain appears by K=4-8 on this benchmark.

## Slide 6 — Larger 105-Identity Check

**Visual:** `results/guided_extended_k1_vs_k8.png`.

**Numbers:**
- 15 modes x 7 seeds = 105 paired identities.
- Mean risk 35.32 -> 13.58.
- Accepted clips 25/105 -> 78/105.
- 81/105 pairs improve.

**Boundary cases:** expressive and locomotion improve strongly; crawling remains
high demand; idle should skip resampling.

## Slide 7 — Videos

**Show:**
- `results/videos/risk_explainer/walk_happy_dance_seed0_K1_vs_K8_risk_explainer.mp4`
- `results/videos/comparison/walk_happy_dance_seed0_K1_vs_K8.mp4`
- `results/videos/comparison/walk_boxing_seed0_K1_vs_K8.mp4`
- `results/videos/comparison/hand_crawling_seed0_K1_vs_K8.mp4`

**Key message:** Videos are qualitative inspection, not proof of execution.

## Slide 8 — Semantic Preservation Audit

**Visual:** `results/semantic_preservation.png`.

**Message:** Median displacement/path/speed ratios are near 1.0, but 15/39
benchmark pairs change root displacement outside 0.5x-1.5x. The method screens
candidate references; it does not guarantee exact style/path preservation.

## Slide 9 — What Did Not Validate

**Visual:** `results/computed_torque_tracking.png`.

**Message:** Weak PD and computed-torque tracking are negative controls. Lower
critic score does not currently imply longer tracking under these controllers.
This is why the contribution is screening/ranking, not physical execution.

## Slide 10 — Ablations

**Visual:** Small table or bar chart.

Include:
- WC-K4 beats PS-K4 at equal compute on the current setup.
- Gumbel sampling is the main diversity source; seed diversity helps expressive
  motions.
- Neural segment critic reaches high window-level rho, but neural full-clip
  selection is a negative result.

## Slide 11 — Limitations

- Heuristic critic, no safety guarantee.
- No learned G1 tracking-policy validation yet.
- Semantic preservation not guaranteed.
- Self-collision/contact-quality terms are incomplete.
- K-times generation cost; neural selector needs more full-clip training data.

## Slide 12 — Conclusion

**Three takeaways:**
1. Best-of-K inference scaling lowers inverse-dynamics demand without retraining.
2. The result holds across a 105-identity local MotionBricks workload.
3. The next publishable step is planner-policy co-training or validation with a
   PHC/CLAW-style learned G1 tracking controller.

## Anticipated Q&A

**Q: Is this physically feasible motion?**  
A: It is lower-demand kinematic reference motion under a heuristic inverse-
dynamics score. Physical feasibility requires learned-controller or hardware
validation.

**Q: Why not train a tracking policy now?**  
A: That is the right next experiment, but it requires a reliable G1 controller
training setup or pretrained policy. The current work establishes the screening
signal and shows where it succeeds and fails.

**Q: Does best-of-K just choose easier or different motions?**  
A: Sometimes it changes motion scale. The semantic audit quantifies that instead
of hiding it.

**Q: Why include negative results?**  
A: Because without them the claim is circular. They define the contribution
honestly and make the next research step clear.
