"""
Generate synthetic kinematic qpos sequences for pipeline testing.

Produces a set of simple parameterized motions for the G1 (36-dim qpos)
without requiring MotionBricks weights. Used to validate the evaluation
harness before real data arrives from Colab.
"""

import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent
# With all joints at 0, the ankle_roll links sit 0.036m above the ground.
# To put the feet on the ground, lower the pelvis by that offset.
NOMINAL_ROOT_HEIGHT = 0.793 - 0.036  # ≈ 0.757m — feet at ground contact
FPS = 30
DT = 1.0 / FPS


def _standing_qpos(root_height: float = NOMINAL_ROOT_HEIGHT) -> np.ndarray:
    """
    Zero-joint standing pose. All joints at 0, pelvis lowered so feet touch ground.
    (With all joints at 0, the G1 ankle_roll links sit 0.036m above the ground;
    subtracting that from the nominal XML pelvis height of 0.793m gives 0.757m.)
    """
    q = np.zeros(36)
    q[2] = root_height
    q[3] = 1.0  # quaternion w (identity)
    return q


def generate_static_stand(n_frames: int = 150) -> np.ndarray:
    """Robot stands still. Should execute perfectly — zero gap expected."""
    base = _standing_qpos()
    return np.tile(base, (n_frames, 1))


def generate_slow_walk(n_frames: int = 200, speed: float = 0.5) -> np.ndarray:
    """
    Simple parameterized walking gait: sinusoidal hip/knee oscillation.
    Root translates forward at `speed` m/s. Not physically derived — just
    a plausible-looking kinematic pattern to test the pipeline.
    """
    t = np.arange(n_frames) * DT
    freq = 1.0  # stride frequency Hz
    omega = 2 * np.pi * freq

    qpos = np.zeros((n_frames, 36))

    # Root trajectory
    qpos[:, 0] = speed * t                  # x: walk forward
    qpos[:, 2] = NOMINAL_ROOT_HEIGHT + 0.02 * np.sin(2 * omega * t)  # z: slight bob
    qpos[:, 3] = 1.0                         # quaternion w

    # Hip pitch (joints 0, 6): alternating swing
    qpos[:, 7 + 0] =  0.4 * np.sin(omega * t)   # left hip pitch
    qpos[:, 7 + 6] = -0.4 * np.sin(omega * t)   # right hip pitch

    # Knee (joints 3, 9): always slightly bent, more during swing
    qpos[:, 7 + 3] = 0.3 + 0.3 * np.abs(np.sin(omega * t))     # left knee
    qpos[:, 7 + 9] = 0.3 + 0.3 * np.abs(np.sin(omega * t + np.pi))  # right knee

    # Ankle pitch (joints 4, 10): slight push-off
    qpos[:, 7 + 4]  = -0.1 * np.sin(omega * t)
    qpos[:, 7 + 10] =  0.1 * np.sin(omega * t)

    return qpos


def generate_fast_run(n_frames: int = 200, speed: float = 2.5) -> np.ndarray:
    """
    Fast running: larger hip/knee amplitude, higher frequency, bigger vertical oscillation.
    Likely to stress physics more than walking.
    """
    t = np.arange(n_frames) * DT
    freq = 2.5
    omega = 2 * np.pi * freq

    qpos = np.zeros((n_frames, 36))
    qpos[:, 0] = speed * t
    qpos[:, 2] = NOMINAL_ROOT_HEIGHT + 0.06 * np.sin(2 * omega * t)
    qpos[:, 3] = 1.0

    qpos[:, 7 + 0] =  0.7 * np.sin(omega * t)
    qpos[:, 7 + 6] = -0.7 * np.sin(omega * t)
    qpos[:, 7 + 3] = 0.5 + 0.4 * np.abs(np.sin(omega * t))
    qpos[:, 7 + 9] = 0.5 + 0.4 * np.abs(np.sin(omega * t + np.pi))
    qpos[:, 7 + 4]  = -0.2 * np.sin(omega * t)
    qpos[:, 7 + 10] =  0.2 * np.sin(omega * t)

    return qpos


def generate_squat(n_frames: int = 120) -> np.ndarray:
    """
    Squat down and stand up. Tests large joint excursions and ground contact.
    """
    t = np.arange(n_frames) * DT
    squat_phase = 0.5 * (1 - np.cos(2 * np.pi * t / t[-1]))  # 0 → 1 → 0

    qpos = np.zeros((n_frames, 36))
    qpos[:, 2] = NOMINAL_ROOT_HEIGHT - 0.25 * squat_phase
    qpos[:, 3] = 1.0

    max_hip = 1.0
    max_knee = 2.0
    max_ankle = -0.5

    for side_hip, side_knee, side_ankle in [(0, 3, 4), (6, 9, 10)]:
        qpos[:, 7 + side_hip]   = max_hip * squat_phase
        qpos[:, 7 + side_knee]  = max_knee * squat_phase
        qpos[:, 7 + side_ankle] = max_ankle * squat_phase

    return qpos


def generate_sinewave_joints(n_frames: int = 150, amplitude: float = 1.5) -> np.ndarray:
    """
    All joints oscillate at maximum amplitude simultaneously.
    Designed to be physically impossible — extreme baseline for gap measurement.
    """
    t = np.arange(n_frames) * DT
    qpos = np.zeros((n_frames, 36))
    qpos[:, 2] = NOMINAL_ROOT_HEIGHT
    qpos[:, 3] = 1.0
    for j in range(29):
        freq = 1.0 + j * 0.1
        qpos[:, 7 + j] = amplitude * np.sin(2 * np.pi * freq * t + j)
    return qpos


MOTIONS = {
    "stand":       (generate_static_stand,   "static"),
    "walk_slow":   (generate_slow_walk,      "locomotion"),
    "run_fast":    (generate_fast_run,       "locomotion"),
    "squat":       (generate_squat,          "whole_body"),
    "chaos_joints": (generate_sinewave_joints, "adversarial"),
}


if __name__ == "__main__":
    for name, (fn, mtype) in MOTIONS.items():
        seq = fn()
        out_path = OUTPUT_DIR / f"{name}.npy"
        np.save(out_path, seq)
        print(f"Saved {name}: {seq.shape} → {out_path}")

    # Save motion type labels for the evaluator
    labels = {name: mtype for name, (_, mtype) in MOTIONS.items()}
    np.save(OUTPUT_DIR / "motion_labels.npy", labels)
    print("Done.")
