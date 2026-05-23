# Native SONIC Acceptance Model, 2026-05-22

This run asks a narrower question than the earlier heuristic-risk critic:
given only the candidate MotionBricks qpos reference, can a learned temporal
model predict whether native SONIC will strictly accept the clip?

## Data

- Source experiment:
  `results/prospective_native_selection/20260516_lowroot_gate/`
- Native rollout labels:
  `results/prospective_native_selection/20260516_lowroot_gate/native_release/batch_summary.csv`
- Rows: 320 selected references from 80 held-out `(mode, seed)` identities.
- Positive label: native SONIC completed the clip with `fell == False`,
  `mean_joint_rmse <= 0.20`, and `mean_root_xy_error <= 1.5`.
- Positives: 264/320.
- Cross-validation groups: `(mode, seed)` identities, so duplicate selector
  reruns of the same identity do not appear in both train and validation.

## Command

```bash
PYTHONUNBUFFERED=1 python scripts/train_native_sonic_acceptance.py \
  --epochs 3000 --folds 5 --batch 24 --width 192 --lr 2e-4 \
  --seed 522 --log_every 50 \
  --out_dir results/native_acceptance_model_20260522_long
```

The job ran on CUDA for about 34 minutes.

Current code now saves `fold_<n>_best.pt` checkpoints for future runs unless
`--no_save_checkpoints` is passed. The recorded 2026-05-22 long run was created
before that checkpoint-saving patch, so its durable evidence is the
cross-validation prediction table, scalar baselines, training log, plot, and
Markdown summary.

## Results

| Predictor | AUC | Average precision |
|---|---:|---:|
| Temporal qpos CNN | 0.769 | 0.921 |
| Scalar pre-controller score | 0.526 | 0.826 |
| Scalar full inverse-dynamics risk | 0.505 | 0.823 |
| Scalar contact artifact score | 0.554 | 0.841 |
| Scalar torque-limit ratio | 0.492 | 0.811 |
| Scalar minimum root height | 0.595 | 0.863 |
| Scalar low-root frame rate | 0.620 | 0.861 |

## Interpretation

The temporal model has real signal that the hand scalar gates miss. This is
useful evidence that native-acceptance prediction benefits from seeing the
whole motion trajectory, not only a few aggregate dynamics/contact features.

This is not yet a learned motion generator or a replacement for native SONIC
rollout. The low-root-gated experiment also showed measurable repeat-run
variability: same-candidate duplicate native rollouts disagreed on strict pass
for 20/74 identities. The learned model should therefore be described as a
noisy triage/ranking aid for selecting which candidates deserve native
controller evaluation.

## Follow-Up

1. Train on a broader native batch after the 13-mode run completes.
2. Calibrate predicted probabilities against repeat-run variability.
3. Use the model only as an auxiliary selector unless it is validated
   prospectively on unseen generated candidate pools.
