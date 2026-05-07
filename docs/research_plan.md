# Research Plan After Current Results

## Current Position

The project is now best framed as:

> inverse-dynamics-critic-guided inference-time scaling for kinematic humanoid
> motion references.

The current results support a screening/ranking claim. They do not support a
physical-execution claim.

## Completed Evidence

- 39-identity K sweep across K=[1,4,8,16].
- 105-identity K=1/K=8 extension across all exposed G1 demo modes.
- Diversity-source ablation.
- Compute-matched whole-clip vs per-segment steering comparison.
- Semantic preservation audit.
- Candidate-level audit.
- Neural critic training and neural-guided selection negative result.
- Extended clip-level neural critic follow-up on 210 clips: rho=0.747.
- Larger clip-level neural critic on 497 unique labeled clips: 3.38M parameters,
  800 epochs, rho=0.800. Improved but still below the 0.85 target.
- PD and computed-torque tracking negative controls.
- 105-task local prompt/control suite and proxy alignment audit.
- Contact-quality audit with self-contact, non-foot floor contact, foot-skate,
  and support-proxy metrics.
- Supplementary videos S0-S5.
- LaTeX paper draft in `paper/`.

## Next Experiment For A Real Paper

Train or import a learned Unitree G1 tracking policy and evaluate paired K=1/K=8
references under identical controller conditions.

Required metrics:

- tracking success rate,
- time to fall,
- joint and body tracking error,
- contact artifacts,
- self-collision,
- energy/torque usage,
- semantic/task preservation.

Existing proxy artifacts that should feed into the learned-tracker experiment:

- `configs/prompt_suite_105.csv`
- `results/prompt_alignment.csv`
- `results/contact_quality.csv`
- `results/guided_ablation_extended.csv`

Expected outcomes:

- If K=8 improves controller success, the critic is validated as a useful
  planner-interface signal.
- If K=8 does not improve controller success, the critic is only a diagnostic
  for inverse-dynamics replay demand.

## Next Method Step

If learned-controller validation succeeds, move from rejection sampling to
training:

1. Generate candidate batches from MotionBricks.
2. Score or roll out candidates under a learned controller.
3. Build pairwise preferences between lower- and higher-demand references.
4. Preference-tune or co-train the planner so low-demand references become more
   likely before best-of-K sampling.

This directly targets the MotionBricks physical-awareness limitation without
pretending that the current heuristic is already a controller.
