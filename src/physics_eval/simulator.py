"""
Physics execution simulator for kinematic-to-dynamic gap analysis.

Replaces mj_forward (kinematic replay) with mj_step + PD control to measure
how well a kinematic trajectory can be physically executed.
"""

import os
import numpy as np
import mujoco
from pathlib import Path
from typing import Optional

from .pd_controller import PDController
from .metrics import (
    FrameMetrics, ClipMetrics,
    compute_frame_metrics, aggregate_clip_metrics
)

ASSETS_DIR = Path(__file__).parents[2] / "assets" / "g1"
SCENE_XML = str(ASSETS_DIR / "scene_29dof.xml")


class PhysicsSimulator:
    """
    Runs kinematic qpos sequences under MuJoCo physics via a PD tracking controller.

    Usage:
        sim = PhysicsSimulator()
        metrics = sim.evaluate_clip(qpos_sequence, clip_name="walk_01", motion_type="locomotion")
    """

    # MuJoCo will print warnings for huge qacc; suppress via this threshold
    MAX_VEL = 50.0  # rad/s or m/s — clip qvel to prevent cascading explosion

    def __init__(self, xml_path: str = SCENE_XML):
        """
        Args:
            xml_path: Path to the MuJoCo scene XML.
        """
        self.model = mujoco.MjModel.from_xml_path(xml_path)
        self.data = mujoco.MjData(self.model)
        # Use model's native timestep (0.002s). Control at 30fps = 1/30/0.002 ≈ 17 substeps.
        self.physics_dt = self.model.opt.timestep   # 0.002s
        self.ctrl_dt = 1.0 / 30.0                  # MotionBricks frame rate
        self.substeps = max(1, round(self.ctrl_dt / self.physics_dt))  # 17

        self.controller = PDController()

        self.controller = PDController()

        # Cache joint info
        self._joint_ranges = self._get_joint_ranges()
        self._foot_body_ids = self._get_foot_body_ids()
        self._n_joints = 29  # hinge joints only

    def _get_joint_ranges(self) -> np.ndarray:
        """Returns (29, 2) array of [lo, hi] joint limits in radians."""
        ranges = []
        for i in range(self.model.njnt):
            jnt = self.model.jnt_type[i]
            if jnt == mujoco.mjtJoint.mjJNT_HINGE:
                lo = self.model.jnt_range[i, 0]
                hi = self.model.jnt_range[i, 1]
                ranges.append([lo, hi])
        return np.array(ranges, dtype=np.float64)

    def _get_foot_body_ids(self) -> tuple:
        """Returns (left_ankle_roll_body_id, right_ankle_roll_body_id)."""
        left_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "left_ankle_roll_link")
        right_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "right_ankle_roll_link")
        assert left_id >= 0 and right_id >= 0, "Foot body IDs not found in model"
        return (left_id, right_id)

    def reset(self, init_qpos: Optional[np.ndarray] = None, settle_steps: int = 100):
        """
        Reset simulation and optionally settle under gravity before tracking begins.

        settle_steps: number of physics steps with PD holding the initial pose,
                      letting contact forces stabilize. Set 0 to skip.
        """
        mujoco.mj_resetData(self.model, self.data)
        if init_qpos is not None:
            self.data.qpos[:] = init_qpos
        mujoco.mj_forward(self.model, self.data)

        if settle_steps > 0 and init_qpos is not None:
            q_target = init_qpos[7:]
            dq_target = np.zeros(29)
            for _ in range(settle_steps):
                torques = self.controller.compute_torques(
                    q_target, self.data.qpos[7:],
                    dq_target, self.data.qvel[6:]
                )
                self.data.ctrl[:] = torques
                mujoco.mj_step(self.model, self.data)
                np.clip(self.data.qvel, -self.MAX_VEL, self.MAX_VEL, out=self.data.qvel)

    MAX_TARGET_VEL = 10.0  # rad/s — clamp finite-diff velocity to prevent NaN cascade

    def _finite_diff_velocity(self, q_seq: np.ndarray, t: int) -> np.ndarray:
        """Estimate target joint velocity at frame t via central / forward differences."""
        if t == 0:
            vel = (q_seq[1, 7:] - q_seq[0, 7:]) / self.ctrl_dt
        elif t >= len(q_seq) - 1:
            vel = (q_seq[-1, 7:] - q_seq[-2, 7:]) / self.ctrl_dt
        else:
            vel = (q_seq[t + 1, 7:] - q_seq[t - 1, 7:]) / (2 * self.ctrl_dt)
        return np.clip(vel, -self.MAX_TARGET_VEL, self.MAX_TARGET_VEL)

    def evaluate_clip(self, qpos_seq: np.ndarray, clip_name: str = "unknown",
                      motion_type: str = "unknown",
                      early_stop_on_fall: bool = True) -> ClipMetrics:
        """
        Evaluate physics execution of a kinematic trajectory.

        Args:
            qpos_seq:   (T, 36) kinematic qpos from MotionBricks or mocap.
            clip_name:  Identifier for this clip.
            motion_type: Category label (e.g. "walk", "run", "crawl").
            early_stop_on_fall: Stop simulation once the robot falls.

        Returns:
            ClipMetrics with per-frame and aggregate metrics.
        """
        assert qpos_seq.ndim == 2 and qpos_seq.shape[1] == 36, \
            f"Expected (T, 36) qpos, got {qpos_seq.shape}"

        T = len(qpos_seq)
        self.reset(init_qpos=qpos_seq[0])

        frame_metrics: list[FrameMetrics] = []

        for t in range(T):
            q_target = qpos_seq[t, 7:]       # (29,)
            dq_target = self._finite_diff_velocity(qpos_seq, t)  # (29,)

            q_now = self.data.qpos[7:].copy()
            dq_now = self.data.qvel[6:].copy()

            torques = self.controller.compute_torques(q_target, q_now, dq_target, dq_now)
            self.data.ctrl[:] = torques

            for _ in range(self.substeps):
                mujoco.mj_step(self.model, self.data)

            # Clip velocities after each control step to prevent cascading explosion
            np.clip(self.data.qvel, -self.MAX_VEL, self.MAX_VEL, out=self.data.qvel)

            # Guard against NaN / Inf only — velocity clipping handles huge-but-finite cases
            if not np.isfinite(self.data.qpos).all() or not np.isfinite(self.data.qvel).all():
                fm = FrameMetrics(
                    tracking_rmse=float("nan"), root_pos_error=float("nan"),
                    root_height=0.0, fell=True,
                    n_joint_limit_violations=0,
                    foot_penetration_left=0.0, foot_penetration_right=0.0,
                    mechanical_power=float("nan"), contact_forces=np.array([]),
                )
                frame_metrics.append(fm)
                for _ in range(T - t - 1):
                    frame_metrics.append(fm)
                print(f"      [NaN detected at frame {t} — simulation unstable]")
                break

            fm = compute_frame_metrics(
                self.model, self.data, q_target, torques,
                self._joint_ranges, self._foot_body_ids
            )
            # Root position error against kinematic target
            root_err = float(np.linalg.norm(self.data.qpos[:3] - qpos_seq[t, :3]))
            fm.root_pos_error = root_err

            frame_metrics.append(fm)

            if early_stop_on_fall and fm.fell:
                # Pad remaining frames with the fall state for bookkeeping
                for _ in range(T - t - 1):
                    fall_fm = FrameMetrics(
                        tracking_rmse=fm.tracking_rmse,
                        root_pos_error=fm.root_pos_error,
                        root_height=fm.root_height,
                        fell=True,
                        n_joint_limit_violations=fm.n_joint_limit_violations,
                        foot_penetration_left=fm.foot_penetration_left,
                        foot_penetration_right=fm.foot_penetration_right,
                        mechanical_power=0.0,
                        contact_forces=fm.contact_forces,
                    )
                    frame_metrics.append(fall_fm)
                break

        return aggregate_clip_metrics(clip_name, motion_type, frame_metrics)
