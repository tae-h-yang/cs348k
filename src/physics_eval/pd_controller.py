"""
PD tracking controller for the Unitree G1 humanoid.

Takes a kinematic target qpos at each timestep and computes joint torques
to track it under MuJoCo physics. The free-floating root is unactuated.

qpos layout (36-dim):
  [0:3]  root position (x, y, z)
  [3:7]  root quaternion (w, x, y, z)
  [7:36] 29 hinge joint angles (same order as MuJoCo actuator list)
"""

import numpy as np

# Joint order matches the actuator list in g1_29dof.xml:
#  0  left_hip_pitch
#  1  left_hip_roll
#  2  left_hip_yaw
#  3  left_knee
#  4  left_ankle_pitch
#  5  left_ankle_roll
#  6  right_hip_pitch
#  7  right_hip_roll
#  8  right_hip_yaw
#  9  right_knee
# 10  right_ankle_pitch
# 11  right_ankle_roll
# 12  waist_yaw
# 13  waist_roll
# 14  waist_pitch
# 15  left_shoulder_pitch
# 16  left_shoulder_roll
# 17  left_shoulder_yaw
# 18  left_elbow
# 19  left_wrist_roll
# 20  left_wrist_pitch
# 21  left_wrist_yaw
# 22  right_shoulder_pitch
# 23  right_shoulder_roll
# 24  right_shoulder_yaw
# 25  right_elbow
# 26  right_wrist_roll
# 27  right_wrist_pitch
# 28  right_wrist_yaw

# Actuator force limits from the XML (symmetric)
ACTUATOR_FORCE_LIMITS = np.array([
    88, 88, 88, 139, 50, 50,   # left leg
    88, 88, 88, 139, 50, 50,   # right leg
    88, 88, 88,                 # waist
    88, 88, 88, 88, 50, 50, 50,  # left arm
    88, 88, 88, 88, 50, 50, 50,  # right arm
], dtype=np.float64)

# PD gains — tuned for G1 morphology.
# Kp chosen so the bandwidth is ~5-10 Hz per joint group.
# Kd = 2*sqrt(Kp * inertia) approximation; set conservatively.
_KP_LEG_HIP    = 100.0
_KP_LEG_KNEE   = 150.0
_KP_ANKLE      = 20.0
_KP_WAIST      = 80.0
_KP_SHOULDER   = 40.0
_KP_ELBOW      = 40.0
_KP_WRIST      = 20.0

_KD_LEG_HIP    = 2.0
_KD_LEG_KNEE   = 3.0
_KD_ANKLE      = 0.5
_KD_WAIST      = 2.0
_KD_SHOULDER   = 1.0
_KD_ELBOW      = 1.0
_KD_WRIST      = 0.5

KP = np.array([
    _KP_LEG_HIP, _KP_LEG_HIP, _KP_LEG_HIP, _KP_LEG_KNEE, _KP_ANKLE, _KP_ANKLE,
    _KP_LEG_HIP, _KP_LEG_HIP, _KP_LEG_HIP, _KP_LEG_KNEE, _KP_ANKLE, _KP_ANKLE,
    _KP_WAIST, _KP_WAIST, _KP_WAIST,
    _KP_SHOULDER, _KP_SHOULDER, _KP_SHOULDER, _KP_ELBOW, _KP_WRIST, _KP_WRIST, _KP_WRIST,
    _KP_SHOULDER, _KP_SHOULDER, _KP_SHOULDER, _KP_ELBOW, _KP_WRIST, _KP_WRIST, _KP_WRIST,
], dtype=np.float64)

KD = np.array([
    _KD_LEG_HIP, _KD_LEG_HIP, _KD_LEG_HIP, _KD_LEG_KNEE, _KD_ANKLE, _KD_ANKLE,
    _KD_LEG_HIP, _KD_LEG_HIP, _KD_LEG_HIP, _KD_LEG_KNEE, _KD_ANKLE, _KD_ANKLE,
    _KD_WAIST, _KD_WAIST, _KD_WAIST,
    _KD_SHOULDER, _KD_SHOULDER, _KD_SHOULDER, _KD_ELBOW, _KD_WRIST, _KD_WRIST, _KD_WRIST,
    _KD_SHOULDER, _KD_SHOULDER, _KD_SHOULDER, _KD_ELBOW, _KD_WRIST, _KD_WRIST, _KD_WRIST,
], dtype=np.float64)

assert len(KP) == 29 and len(KD) == 29 and len(ACTUATOR_FORCE_LIMITS) == 29


class PDController:
    """Joint-space PD controller that tracks kinematic qpos targets."""

    def __init__(self, kp: np.ndarray = KP, kd: np.ndarray = KD,
                 force_limits: np.ndarray = ACTUATOR_FORCE_LIMITS):
        self.kp = kp
        self.kd = kd
        self.force_limits = force_limits

    def compute_torques(self, q_target: np.ndarray, q: np.ndarray,
                        dq_target: np.ndarray, dq: np.ndarray) -> np.ndarray:
        """
        Args:
            q_target:  (29,) target joint angles
            q:         (29,) current joint angles (data.qpos[7:])
            dq_target: (29,) target joint velocities (finite diff of q_target)
            dq:        (29,) current joint velocities (data.qvel[6:])
        Returns:
            torques:   (29,) clamped to force limits
        """
        tau = self.kp * (q_target - q) + self.kd * (dq_target - dq)
        return np.clip(tau, -self.force_limits, self.force_limits)
