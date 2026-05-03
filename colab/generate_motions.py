"""
MotionBricks motion generation script for Google Colab (GPU required).

Generates diverse kinematic qpos sequences from MotionBricks, categorized
by motion type, and saves them as .npy files for physics evaluation on MacBook.

Run on Colab:
    !git clone https://github.com/NVlabs/GR00T-WholeBodyControl.git
    %cd GR00T-WholeBodyControl/motionbricks
    !git lfs pull
    !pip install -e .
    # Then run this script

Output: one .npy file per clip of shape (T, 36) — mujoco qpos format.
"""

import sys
import numpy as np
from pathlib import Path

# ── config ────────────────────────────────────────────────────────────────────
RESULT_DIR = Path("generated_motions")
RESULT_DIR.mkdir(exist_ok=True)

# Motion types — exact allowed_mode keys from clip_holder_G1 in
# motionbricks/motion_backbone/demo/clips.py
MOTION_CONFIGS = [
    {"mode": "idle",             "n_frames": 150, "type": "static"},
    {"mode": "walk",             "n_frames": 200, "type": "locomotion"},
    {"mode": "slow_walk",        "n_frames": 200, "type": "locomotion"},
    {"mode": "stealth_walk",     "n_frames": 200, "type": "locomotion"},
    {"mode": "injured_walk",     "n_frames": 200, "type": "locomotion"},
    {"mode": "walk_zombie",      "n_frames": 200, "type": "locomotion"},
    {"mode": "walk_stealth",     "n_frames": 180, "type": "locomotion"},
    {"mode": "walk_boxing",      "n_frames": 180, "type": "expressive"},
    {"mode": "walk_happy_dance", "n_frames": 180, "type": "expressive"},
    {"mode": "walk_gun",         "n_frames": 180, "type": "expressive"},
    {"mode": "walk_scared",      "n_frames": 180, "type": "expressive"},
    {"mode": "hand_crawling",    "n_frames": 150, "type": "whole_body"},
    {"mode": "elbow_crawling",   "n_frames": 150, "type": "whole_body"},
]

N_SEEDS = 3   # generate N random seeds per mode for variability


def generate_clip(demo_agent, mode: str, n_frames: int, seed: int) -> np.ndarray:
    """
    Generate a single kinematic trajectory from MotionBricks.

    Returns: (n_frames, 36) float32 qpos array in MuJoCo format.
    """
    import torch
    np.random.seed(seed)
    torch.manual_seed(seed)

    demo_agent.full_agent.reset()
    qpos_list = []

    for step in range(n_frames):
        # Generate idle control signal with fixed mode
        control_signals = {
            "force_idle": False,
            "allowed_mode": mode,
            # Minimal control signal — robot holds current direction
            "velocity": np.array([0.3, 0.0]),   # forward velocity
            "heading": 0.0,
        }

        qpos = demo_agent.full_agent.get_next_frame()
        qpos_list.append(qpos.copy())

        context = demo_agent.full_agent.get_context_mujoco_qpos()
        control_signals["context_mujoco_qpos"] = context

        with torch.no_grad():
            demo_agent.full_agent.generate_new_frames(control_signals, dt=1/30)

    return np.stack(qpos_list, axis=0).astype(np.float32)


def main():
    # ── bootstrap MotionBricks ────────────────────────────────────────────────
    sys.path.insert(0, ".")
    import argparse
    from motionbricks.motion_backbone.demo.utils import navigation_demo

    args = argparse.Namespace(
        humanoid_xml="assets/skeletons/g1/scene_29dof.xml",
        result_dir="./out",
        data_root="./datasets",
        explicit_dataset_folder=None,
        reprocess_clips=0,
        controller="random",
        lookat_movement_direction=0,
        has_viewer=0,
        pre_filter_qpos=1,
        source_root_realignment=1,
        target_root_realignment=1,
        force_canonicalization=1,
        skip_ending_target_cond=0,
        random_speed_scale=0,
        speed_scale=[0.8, 1.2],
        generate_dt=2.0,
        max_steps=10000,
        random_seed=42,
        num_runs=1,
        use_qpos=1,
        planner="default",
        allowed_mode=None,
        clips="G1",
        return_model_configs=True,
        return_dataloader=True,
        recording_dir=None,
        EXP="default",
    )

    print("Loading MotionBricks model...")
    demo_agent = navigation_demo(args)
    print("Model loaded.")

    # ── generate ──────────────────────────────────────────────────────────────
    labels = {}
    for cfg in MOTION_CONFIGS:
        mode, n_frames, mtype = cfg["mode"], cfg["n_frames"], cfg["type"]
        for seed in range(N_SEEDS):
            clip_name = f"{mode}_seed{seed}"
            print(f"  Generating: {clip_name} ({n_frames} frames)...")
            try:
                qpos = generate_clip(demo_agent, mode, n_frames, seed=seed * 1000)
                out_path = RESULT_DIR / f"{clip_name}.npy"
                np.save(out_path, qpos)
                labels[clip_name] = mtype
                print(f"    Saved: {out_path} — shape {qpos.shape}")
            except Exception as e:
                print(f"    FAILED: {e}")

    np.save(RESULT_DIR / "motion_labels.npy", labels)
    print(f"\nDone. {len(labels)} clips saved to {RESULT_DIR}/")
    print("Download the generated_motions/ folder and place it in data/ on your MacBook.")
    print("Then run: python run_eval.py --data_dir data/generated_motions")


if __name__ == "__main__":
    main()
