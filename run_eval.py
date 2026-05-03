"""
Main evaluation script: runs kinematic qpos sequences through physics simulation
and reports the kinematic-to-dynamic gap metrics.

Usage:
    conda activate cs348k
    python run_eval.py --data_dir data/synthetic
    python run_eval.py --data_dir data/motionbricks
    python run_eval.py --data_dir data/motionbricks --kinematic_baseline
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
    labels = np.load(labels_path, allow_pickle=True).item() if labels_path.exists() else {}

    motions = []
    for p in sorted(data_dir.glob("*.npy")):
        if p.stem == "motion_labels":
            continue
        seq = np.load(p)
        if seq.ndim != 2 or seq.shape[1] != 36:
            print(f"Skipping {p.name}: unexpected shape {seq.shape}")
            continue
        motions.append((p.stem, labels.get(p.stem, "unknown"), seq))

    return motions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/synthetic",
                        help="Directory of .npy qpos files to evaluate")
    parser.add_argument("--kinematic_baseline", action="store_true",
                        help="Also run kinematic replay (mj_forward) baseline for gap comparison")
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
    physics_results = []
    kinematic_results = []

    for clip_name, motion_type, qpos_seq in motions:
        print(f"  [{clip_name}] {motion_type} — {len(qpos_seq)} frames")

        phys = sim.evaluate_clip(
            qpos_seq, clip_name=clip_name, motion_type=motion_type,
            early_stop_on_fall=not args.no_early_stop
        )
        physics_results.append(phys)
        s = phys.summary()
        fell_str = f"FELL at frame {s['time_to_fall']}" if s['fell'] else "survived"
        print(f"    physics  → {fell_str} | tracking={s['tracking_rmse']:.4f} rad | "
              f"root_err={s['root_pos_error']:.3f} m | power={s['mech_power_W']:.1f} W")

        if args.kinematic_baseline:
            kin = sim.evaluate_clip_kinematic(qpos_seq, clip_name=clip_name, motion_type=motion_type)
            kinematic_results.append(kin)
            sk = kin.summary()
            fell_str_k = f"height<0.45m at {sk['time_to_fall']}" if sk['fell'] else "ok"
            print(f"    kinematic→ {fell_str_k} | joint_viol={sk['max_joint_viol']} | "
                  f"foot_pen={sk['foot_penetration_m']:.4f} m")

    print()
    if not args.no_plot:
        all_results = physics_results + kinematic_results
        plot_all(all_results)


if __name__ == "__main__":
    main()
