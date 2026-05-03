# Kinematic-to-Dynamic Gap in Generative Humanoid Motion

CS 348K (Visual Computing Systems, Stanford, Spring 2026) course project.

Quantifies how well [MotionBricks](https://github.com/NVlabs/GR00T-WholeBodyControl)-generated kinematic trajectories can be physically executed on the Unitree G1 in MuJoCo, and characterizes failure modes by motion type.

## Setup

Requires [conda](https://docs.conda.io/en/latest/miniconda.html).

```bash
bash setup.sh
conda activate cs348k
```

## Running the Evaluation

**Synthetic baseline** (no data download needed):
```bash
python run_eval.py --data_dir data/synthetic
```

**MotionBricks clips** (requires Colab generation first — see below):
```bash
python run_eval.py --data_dir data/motionbricks
```

Results (plots + CSV) are written to `results/`.

## Generating MotionBricks Data

Motion clips are generated on a Colab GPU and are not committed to this repo.

1. Open `colab/generate_motions.ipynb` in [Google Colab](https://colab.research.google.com) with a GPU runtime (Runtime → Change runtime type → T4 GPU)
2. Run all cells — clips save to Google Drive under `cs348k/motionbricks/`
3. Download the folder and place it at `data/motionbricks/`

## Project Structure

```
src/physics_eval/   — MuJoCo simulator, PD controller, metrics
src/analysis/       — plotting and summary
assets/g1/          — Unitree G1 MuJoCo model + meshes
data/synthetic/     — small synthetic motions for pipeline testing
colab/              — Colab generation notebook + script
run_eval.py         — evaluation entry point
```

## Key Metrics

- Joint tracking RMSE (PD controller vs. kinematic reference)
- Root position drift
- Time-to-fall
- Mechanical power
- Joint limit violations
