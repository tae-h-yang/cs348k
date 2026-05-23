# Broad13 Native SONIC Acceptance Model, 2026-05-23

## Question

Can a trajectory-level learned scorer predict native SONIC strict acceptance on
the completed broad 13-mode rollout set better than the scalar
root/contact/dynamics gates?

## Protocol

- Data:
  `results/prospective_native_selection/20260522_broad13/`.
- Native labels:
  `results/prospective_native_selection/20260522_broad13/native_release/batch_summary.csv`.
- Records: 405 selected references.
- Identities: 104 `(mode, seed)` groups.
- Positive label: native rollout survived, mean joint RMSE `<= 0.20`, and mean
  root XY error `<= 1.5m`.
- Model: temporal qpos CNN over normalized `(T, 36)` qpos.
- Validation: 5-fold group cross-validation by identity, so selector duplicates
  from the same `(mode, seed)` do not leak between train and validation.
- Training: 6000 epochs per fold, width 512, batch 64, CUDA. The run took
  about 4.5 hours and saved one best checkpoint per fold.

## Command

```bash
CUDA_VISIBLE_DEVICES=0 python scripts/train_native_sonic_acceptance.py \
  --prospective_dir results/prospective_native_selection/20260522_broad13 \
  --batch_dir results/prospective_native_selection/20260522_broad13/native_release \
  --out_dir results/native_acceptance_model_20260523_broad13_long \
  --epochs 6000 --folds 5 --batch 64 --width 512 \
  --lr 0.0005 --seed 23 --log_every 100
```

## Results

| model | AUC | average precision |
|---|---:|---:|
| temporal qpos CNN | 0.864 | 0.917 |
| scalar root-z minimum | 0.782 | 0.865 |
| scalar low-root frames | 0.768 | 0.849 |
| scalar precontroller score | 0.752 | 0.845 |
| scalar contact artifact score | 0.741 | 0.839 |
| scalar full risk | 0.737 | 0.845 |
| scalar p95 torque-limit ratio | 0.719 | 0.832 |

Artifacts:

- Report: `results/native_acceptance_model_20260523_broad13_long/native_acceptance_model.md`
- Predictions: `results/native_acceptance_model_20260523_broad13_long/crossval_predictions.csv`
- Training log: `results/native_acceptance_model_20260523_broad13_long/train_log.csv`
- Plot: `results/native_acceptance_model_20260523_broad13_long/training_auc.png`
- Checkpoints:
  `results/native_acceptance_model_20260523_broad13_long/fold_1_best.pt` through
  `fold_5_best.pt`.

## Learned Selector Audit

After training, the saved fold checkpoints were used to score all 832 broad13
candidates with `scripts/score_native_acceptance_candidates.py`. The script
also builds a fair retrospective selector over native-evaluated candidates only,
using out-of-fold predictions from `crossval_predictions.csv`.

```bash
python scripts/score_native_acceptance_candidates.py \
  --prospective_dir results/prospective_native_selection/20260522_broad13 \
  --model_dir results/native_acceptance_model_20260523_broad13_long \
  --out_dir results/prospective_native_selection/20260522_broad13/learned_acceptance_selector \
  --batch 64
```

Audit outputs:

- `candidate_scores.csv`: ensemble model scores for all 832 candidates.
- `ensemble_selection_all_candidates.csv`: best learned-score candidate per
  identity, for future prospective rollout.
- `crossval_selection_evaluated_candidates.csv`: fair retrospective best
  out-of-fold learned-score candidate among the already native-evaluated
  selector choices.
- `learned_selector_audit.md`: compact summary.

Retrospective results:

| selector view | evaluated selections | strict among evaluated |
|---|---:|---:|
| ensemble over all candidates | 46/104 | 45/46 (97.8%) |
| out-of-fold over evaluated candidates | 104/104 | 77/104 (74.0%) |

The ensemble-over-all-candidates result is not a success rate, because 58/104
selected candidates were never run through native SONIC. It is a queue for the
next native rollout. The fair evaluated-only result is conservative: 77/104 is
close to the hand-coded gated selector's 78/104 identity strict pass, so the
learned model has not yet proven prospective selection superiority.

## Interpretation

This is the strongest evidence so far that native SONIC acceptability is not
fully captured by one scalar root/contact/dynamics heuristic. A learned
trajectory-level scorer improves cross-validated AUC from the best scalar
baseline, root-z minimum at 0.782, to 0.864.

This is still not a learned MotionBricks generator or a fine-tuning result. It
is an acceptance/triage model trained on noisy native controller labels. The
model is useful as a next prospective selector candidate, but it must be tested
in a new generation-and-native-rollout batch before claiming that it improves
selected motion quality in deployment.

Important caveat: per-fold behavior was uneven. Some folds reached high AUC/AP,
while other folds showed noisier validation loss and lower average precision.
The correct claim is therefore "learned broad13 acceptance prediction is
promising and stronger than current scalar gates," not "the model certifies
physical feasibility."
