#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="cs348k"
PYTHON_VERSION="3.11"

echo "=== CS 348K — Kinematic-to-Dynamic Gap ==="

# Create conda env (skip if already exists)
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "Conda env '${ENV_NAME}' already exists, skipping creation."
else
    echo "Creating conda env '${ENV_NAME}' with Python ${PYTHON_VERSION}..."
    conda create -n "${ENV_NAME}" python="${PYTHON_VERSION}" -y
fi

# Activate and install deps
eval "$(conda shell.bash hook)"
conda activate "${ENV_NAME}"

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Setup complete ==="
echo "Activate the env with:  conda activate ${ENV_NAME}"
echo "Run evaluation:         python run_eval.py --data_dir data/synthetic"
echo ""
echo "To evaluate MotionBricks clips:"
echo "  1. Open colab/generate_motions.ipynb in Google Colab (GPU runtime)"
echo "  2. Run all cells — outputs save to Google Drive under cs348k/motionbricks/"
echo "  3. Download the folder to data/motionbricks/"
echo "  4. python run_eval.py --data_dir data/motionbricks"
