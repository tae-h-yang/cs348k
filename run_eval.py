"""
Main evaluation script: runs kinematic qpos sequences through physics simulation
and reports the kinematic-to-dynamic gap metrics.

Usage:
    conda activate toddlerbot
    python run_eval.py --data_dir data/synthetic
    python run_eval.py --data_dir data/motionbricks  # after Colab generation
"""

import sys
import argparse
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from physics_eval.simulator import PhysicsSimulator
from analysis.visualize import plot_all


def load_motion_dir(data_dir: Path):
    """
    Load all .npy motion files from a directory.

    Expected file format: (T, 36) float32/64 array.
    Optional: motion_labels.npy — dict mapping filename stem → motion_type string.
    """
    labels_path = data_dir / "motion_labels.npy"
    if labels_path.exists():
        labels = np.load(labels_path, allow_pickle=True).item()
    else:
        labels = {}

    motions = []
    for p in sorted(data_dir.glob("*.npy")):
        if p.stem == "motion_labels":
            continue
        seq = np.load(p)
        if seq.ndim != 2 or seq.shape[1] != 36:
            print(f"Skipping {p.name}: unexpected shape {seq.shape}")
            continue
        motion_type = labels.get(p.stem, "unknown")
        motions.append((p.stem, motion_type, seq))

    return motions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/synthetic",
                        help="Directory of .npy qpos files to evaluate")
    parser.add_argument("--no_early_stop", action="store_true",
                        help="Continue simulation even after fall (slower)")
    parser.add_argument("--no_plot", action="store_true",
                        help="Skip visualization")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        sys.exit(1)

    motions = load_motion_dir(data_dir)
    if not motions:
        print(f"No valid .npy motion files found in {data_dir}")
        sys.exit(1)

    print(f"Loaded {len(motions)} motion clips from {data_dir}")
    print()

    sim = PhysicsSimulator()
    results = []

    for clip_name, motion_type, qpos_seq in motions:
        print(f"  Evaluating: {clip_name} [{motion_type}] — {len(qpos_seq)} frames")
        metrics = sim.evaluate_clip(
            qpos_seq, clip_name=clip_name, motion_type=motion_type,
            early_stop_on_fall=not args.no_early_stop
        )
        results.append(metrics)
        s = metrics.summary()
        fell_str = f"FELL at frame {s['time_to_fall']}" if s['fell'] else "survived"
        print(f"    → {fell_str} | tracking={s['tracking_rmse']:.4f} rad | "
              f"root_err={s['root_pos_error']:.3f} m | power={s['mech_power_W']:.1f} W")

    print()
    if not args.no_plot:
        plot_all(results)


if __name__ == "__main__":
    main()
