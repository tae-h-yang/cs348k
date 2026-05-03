# Kinematic-to-Dynamic Gap in Generative Humanoid Motion

CS 348K (Visual Computing Systems, Stanford, Spring 2026) course project.

Quantifies how well [MotionBricks](https://github.com/NVlabs/GR00T-WholeBodyControl)-generated kinematic trajectories can be physically executed on the Unitree G1 in MuJoCo, and characterizes failure modes by motion type.

## Setup

Requires [conda](https://docs.conda.io/en/latest/miniconda.html) and an NVIDIA GPU.

```bash
bash setup.sh
conda activate cs348k
```

## Generating MotionBricks Data

Clone and install MotionBricks (one-time):

```bash
git clone https://github.com/NVlabs/GR00T-WholeBodyControl.git
cd GR00T-WholeBodyControl/motionbricks
git lfs pull
pip install -e .
cd -
```

Then generate clips (writes to `data/motionbricks/`):

```bash
python generate_motions.py
```

## Running the Evaluation

**Synthetic baseline** (no data generation needed):
```bash
python run_eval.py --data_dir data/synthetic
```

**MotionBricks clips** (after running `generate_motions.py`):
```bash
python run_eval.py --data_dir data/motionbricks
```

Results (plots + CSV) are written to `results/`.

## Project Structure

```
src/physics_eval/   — MuJoCo simulator, PD controller, metrics
src/analysis/       — plotting and summary
assets/g1/          — Unitree G1 MuJoCo model + meshes
data/synthetic/     — small synthetic motions for pipeline testing
data/motionbricks/  — generated clips (populated by generate_motions.py)
generate_motions.py — MotionBricks clip generation (local GPU)
run_eval.py         — evaluation entry point
```

## Key Metrics

- Joint tracking RMSE (PD controller vs. kinematic reference)
- Root position drift
- Time-to-fall
- Mechanical power
- Joint limit violations
