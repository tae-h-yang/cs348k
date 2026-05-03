"""
Physics plausibility metrics for kinematic-to-dynamic gap analysis.

Each metric is computed per-frame and aggregated over a clip.
All functions assume MuJoCo coordinate convention: Z-up, X-forward.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional


# G1-specific thresholds
FALL_HEIGHT_THRESHOLD = 0.45   # root Z below this → fall (nominal standing ~0.793m)
FOOT_PENETRATION_THRESHOLD = -0.01  # foot Z below this → ground penetration (m)
MIN_FOOT_HEIGHT_FOR_CONTACT = 0.03  # foot Z above this → expect no ground contact

@dataclass
class FrameMetrics:
    tracking_rmse: float       # RMSE of 29 joint angles vs kinematic target
    root_pos_error: float      # Euclidean distance of root pos vs kinematic target
    root_height: float         # Absolute root Z (to detect falls)
    fell: bool                 # True if root dropped below FALL_HEIGHT_THRESHOLD
    n_joint_limit_violations: int  # joints outside their MuJoCo range
    foot_penetration_left: float   # left foot Z (negative = penetrating ground)
    foot_penetration_right: float  # right foot Z
    mechanical_power: float    # sum |tau_i * dq_i| across all joints (W)
    contact_forces: np.ndarray     # (ncon,) normal contact forces


@dataclass
class ClipMetrics:
    clip_name: str
    motion_type: str
    n_frames: int
    time_to_fall: Optional[int]    # frame index of first fall, None if no fall
    fell: bool
    mean_tracking_rmse: float
    mean_root_pos_error: float
    mean_mechanical_power: float
    max_joint_limit_violations: int
    mean_foot_penetration: float   # avg of max(0, -foot_Z) per frame
    frame_metrics: List[FrameMetrics] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "clip": self.clip_name,
            "type": self.motion_type,
            "frames": self.n_frames,
            "fell": self.fell,
            "time_to_fall": self.time_to_fall,
            "tracking_rmse": self.mean_tracking_rmse,
            "root_pos_error": self.mean_root_pos_error,
            "mech_power_W": self.mean_mechanical_power,
            "max_joint_viol": self.max_joint_limit_violations,
            "foot_penetration_m": self.mean_foot_penetration,
        }


def compute_frame_metrics(
    model,
    data,
    q_target: np.ndarray,
    torques: np.ndarray,
    joint_ranges: np.ndarray,
    foot_body_ids: tuple,
) -> FrameMetrics:
    """
    Args:
        model:         mujoco.MjModel
        data:          mujoco.MjData (after mj_step)
        q_target:      (29,) kinematic target joint angles for this frame
        torques:       (29,) applied torques
        joint_ranges:  (29, 2) joint limits [[lo, hi], ...]
        foot_body_ids: (left_id, right_id) MuJoCo body IDs for ankle_roll links
    """
    q = data.qpos[7:]
    dq = data.qvel[6:]

    tracking_rmse = float(np.sqrt(np.mean((q - q_target) ** 2)))
    root_pos = data.qpos[:3].copy()
    root_height = float(root_pos[2])

    # Root position error vs kinematic target stored externally — caller provides q_target
    # We compute root error separately in the simulator since we have the full target qpos there

    fell = root_height < FALL_HEIGHT_THRESHOLD

    violations = int(np.sum((q < joint_ranges[:, 0]) | (q > joint_ranges[:, 1])))

    # Foot heights via xpos (world-frame body positions)
    foot_z_left = float(data.xpos[foot_body_ids[0], 2])
    foot_z_right = float(data.xpos[foot_body_ids[1], 2])

    foot_pen = float(max(0, -foot_z_left) + max(0, -foot_z_right)) / 2.0

    mech_power = float(np.sum(np.abs(torques * dq)))

    contact_forces = np.array([data.contact[i].dist for i in range(data.ncon)], dtype=np.float64)

    return FrameMetrics(
        tracking_rmse=tracking_rmse,
        root_pos_error=0.0,  # filled in by simulator
        root_height=root_height,
        fell=fell,
        n_joint_limit_violations=violations,
        foot_penetration_left=foot_z_left,
        foot_penetration_right=foot_z_right,
        mechanical_power=mech_power,
        contact_forces=contact_forces,
    )


def aggregate_clip_metrics(clip_name: str, motion_type: str,
                           frame_list: List[FrameMetrics]) -> ClipMetrics:
    n = len(frame_list)
    fell_frames = [i for i, f in enumerate(frame_list) if f.fell]
    fell = len(fell_frames) > 0
    time_to_fall = fell_frames[0] if fell else None

    # Truncate at fall for per-frame averages (no point averaging after collapse)
    active = frame_list[:time_to_fall] if fell and time_to_fall is not None else frame_list
    if not active:
        active = frame_list

    mean_tracking = float(np.mean([f.tracking_rmse for f in active]))
    mean_root_err = float(np.mean([f.root_pos_error for f in active]))
    mean_power = float(np.mean([f.mechanical_power for f in active]))
    max_violations = int(max(f.n_joint_limit_violations for f in active))

    foot_pen_per_frame = [
        (max(0, -f.foot_penetration_left) + max(0, -f.foot_penetration_right)) / 2.0
        for f in active
    ]
    mean_foot_pen = float(np.mean(foot_pen_per_frame))

    return ClipMetrics(
        clip_name=clip_name,
        motion_type=motion_type,
        n_frames=n,
        time_to_fall=time_to_fall,
        fell=fell,
        mean_tracking_rmse=mean_tracking,
        mean_root_pos_error=mean_root_err,
        mean_mechanical_power=mean_power,
        max_joint_limit_violations=max_violations,
        mean_foot_penetration=mean_foot_pen,
        frame_metrics=frame_list,
    )
