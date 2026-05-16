# Controller-Loop Pivot, 2026-05-16

## Decision

The honest project claim is now:

> Fixed MotionBricks generation plus structured verification and native SONIC
> controller-in-the-loop curation can identify an executable subset of upright
> G1 references, while rejecting visibly/controller-invalid cases.

This is not a claim that we fine-tuned MotionBricks, solved arbitrary text to
robot motion, or made crawling/manipulation broadly executable.

## Why Not MotionBricks Fine-Tuning Today

Local inspection found MotionBricks pretrained checkpoints and synthetic
training scripts, but not a complete physical-awareness fine-tuning pipeline.
The public MotionBricks page says the preview release includes an interactive G1
demo plus a self-contained synthetic training pipeline, while the full robotics
formulation and complete training pipeline is targeted for a later full release.
See:

- https://nvlabs.github.io/motionbricks/
- `/home/rewardai/repos/GR00T-WholeBodyControl/motionbricks/scripts/train_pose.py`
- `/home/rewardai/repos/GR00T-WholeBodyControl/motionbricks/scripts/train_root.py`
- `/home/rewardai/repos/GR00T-WholeBodyControl/motionbricks/scripts/train_vqvae.py`

The local scripts train on randomly generated tensors. Running them longer would
only prove that the code executes; it would not produce a scientifically valid
physically aware MotionBricks generator.

## Why Native SONIC Is The Right Acceptance Gate

The SONIC paper frames motion tracking as the scalable humanoid-control task and
reports success/failure using controller tracking in simulation and hardware.
It evaluates success with fall/root-deviation criteria and pose/velocity
tracking metrics, and its reward includes joint-limit and undesired-contact
penalties.

Useful sources:

- https://arxiv.org/abs/2511.07820
- https://nvlabs.github.io/GEAR-SONIC/
- https://github.com/NVlabs/GR00T-WholeBodyControl

Therefore, native SONIC rollout is stronger evidence than inverse dynamics
alone. Inverse dynamics/contact/MotionSpec should be treated as pre-controller
features for ranking and rejection, then calibrated against native SONIC labels.

## Current Native Evidence

Existing 100-run native release batch:

- run folder:
  `results/sonic_native_release_overnight/20260516_085134/`
- 100/100 attempts completed.
- 84/100 survived the root-height threshold.
- 76/84 upright references survived.
- 66/84 upright references passed the stricter gate:
  survived, joint RMSE <= 0.20 rad, root XY error <= 1.5 m.
- 8/8 idle survived.
- 0/8 crawling survived.

New selector/calibration outputs from the same 100-run batch:

- `native_candidate_evidence.csv`
- `native_selector_comparison.csv`
- `native_selector_pair_details.csv`
- `native_predictive_calibration.csv`
- `native_selector_comparison.png`
- `native_selector_analysis.md`

Key result on the 25 paired K=1/K=8 identities inside that 100-run batch:

| selector | strict pass | survive | interpretation |
|---|---:|---:|---|
| K1 baseline | 20/25 | 21/25 | strong baseline |
| K8 ID-screened | 16/25 | 21/25 | lower risk, worse strict pass |
| best pre-controller score | 17/25 | 21/25 | not enough alone |
| learned native-strict LOMO | 19/25 | 22/25 | promising but too small |
| native oracle upper bound | 22/25 | 23/25 | headroom if native rollouts are used as gate |

This rules out the simple claim that K=8/inverse-dynamics selection improves
native execution. It supports a stricter claim: native controller-in-the-loop
curation has usable headroom, and pre-controller metrics need calibration.

## All-210 Native SONIC Result

The all-210 native SONIC batch completed:

- run folder: `results/sonic_native_release_all210/20260516_123519/`
- completed: 210/210
- overall survival: 164/210
- upright survival: 152/168
- strict upright pass: 136/168
- crawling survival: 0/28
- paired K=1/K=8 strict pass:
  - K1 baseline: 72/105
  - K8 inverse-dynamics selected: 74/105
  - native oracle upper bound: 85/105

See `docs/sonic_native_all210_2026-05-16.md`.

## Next Scientific Move

1. Separate upright-only claims from low-posture/crawling failures.
2. Build a prospective experiment:
   generate a fixed candidate pool, select before native rollout, then evaluate
   selected winners under native SONIC.
3. Only after enough native labels exist, train a lightweight selector model.
   Do not call it MotionBricks fine-tuning.
