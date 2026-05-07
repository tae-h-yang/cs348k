# SONIC Policy Tracking Experiment

## Overview

The SONIC G1 tracking policy (`gear_sonic_deploy` ONNX encoder + decoder) is
run in closed-loop MuJoCo to validate whether the inverse-dynamics critic
scores correlate with a learned controller's ability to track the same clips.

The MuJoCo harness (`scripts/evaluate_sonic_policy_mujoco.py`) reconstructs
the full SONIC observation pipeline from simulated G1 state and feeds it to
the public ONNX encoder/decoder weights.

---

## Three Bugs Fixed in the Harness (2026-05-05)

All three bugs combined to produce an "all clips immediately fall" symptom that
previously showed up as track times of 0.3–0.7 s with 30–40% torque
saturation.

### Bug 1 — Wrong PD update rate (critical)

**What was wrong:** The PD torque was computed once per 50 Hz policy step and
held constant for all physics substeps:

```python
tau = KP * (q_target - data.qpos[7:]) - KD * data.qvel[6:]  # compute once
data.ctrl[:] = tau
for _ in range(substeps):
    mujoco.mj_step(model, data)
```

**Why it matters:** In IsaacLab training and on the real G1 hardware, the motor
PD controllers re-evaluate at every physics timestep (≈200 Hz), not once per
50 Hz policy step. Applying a fixed torque for 10 physics steps means the
robot can overshoot wildly before the next correction, leading to exponentially
growing action norms (2 → 6 → 14 → 28) and immediate torque saturation.

**Fix:**

```python
for _ in range(substeps):
    tau = KP * kp_scale * (q_target - data.qpos[7:]) - KD * kd_scale * data.qvel[6:]
    data.ctrl[:] = np.clip(tau, ctrl_lo, ctrl_hi)
    mujoco.mj_step(model, data)
```

**Effect:** Torque saturation dropped from ~35% to 0%; action norms stay
bounded; mean track time increased ≈5×.

---

### Bug 2 — Wrong robot initialization pose

**What was wrong:** The simulator was initialized to reference frame 0 of the
MotionBricks clip (knees nearly fully extended, body_q ≈ −0.67 from default).
History was pre-warmed with that same unusual pose.

**Why it matters:** In real SONIC deployment, the robot is already standing at
the DEFAULT pose (body_q ≈ 0) when tracking begins. The reference motion
starts playing from frame 0 regardless. The policy was trained expecting to
see near-zero history when tracking starts, not a non-default starting pose.
MotionBricks frame 0 is a mid-stride configuration (knees extended) which the
policy has never seen as a starting state.

**Fix:** Initialize the robot at DEFAULT_ANGLES with the reference root
position, pre-warm history with the DEFAULT standing state:

```python
data.qpos[:3] = ref.body_pos[0]    # root at reference start (x,y,z)
data.qpos[3:7] = ref.body_quat[0]  # root orientation from reference
data.qpos[7:] = DEFAULT_ANGLES     # joints at default standing pose
history = [default_state for _ in range(10)]  # pre-warm with default
```

---

### Bug 3 — Wrong export permutation in `export_sonic_references.py`

**What was wrong:** The MotionBricks qpos (MuJoCo order) was being converted to
"IsaacLab order" using `ISAACLAB_TO_MUJOCO` instead of `MUJOCO_TO_ISAACLAB`:

```python
joints_isaac = joints_mujoco[:, ISAACLAB_TO_MUJOCO]  # WRONG
```

This scrambled columns — MuJoCo joint 1 (l_hip_roll) received the value
from IsaacLab index 3 (r_knee), etc.

**Fix:**

```python
joints_isaac = joints_mujoco[:, MUJOCO_TO_ISAACLAB]  # CORRECT
```

All 20 SONIC references were re-exported.

---

## Current Results (post-fix, 2026-05-05)

20 clips: walk, slow_walk, walk_gun, walk_happy_dance, hand_crawling ×
2 seeds × K=1/K=8. Maximum 5 seconds per clip.

| Group | n | Falls | Mean track time (s) | Mean joint RMSE (rad) | Torque sat. |
|---|---:|---:|---:|---:|---:|
| K=1 | 10 | 10 | **2.07** | 0.317 | 0% |
| K=8 | 10 | 10 | 1.81  | 0.401 | 0% |
| K=8 − K=1 (paired) | 10 | — | −0.26 | +0.084 | — |

Best individual clip: `walk_happy_dance_seed0_K1` tracked for **4.78 s** before
falling (out of 5.0 s max).

---

## Interpretation

All clips still fall within the 5-second window. This remains a **negative
result** for inverse-dynamics-only selection: K=8 clips have slightly shorter
tracking time and higher RMSE than K=1.

The negative direction (K=8 harder to track) is interpretable: K=8 selects
more dynamic/expressive motions with larger joint excursions, which are
inherently harder for the SONIC policy to follow from a default-standing
initial condition. This does not mean K=8 clips are physically worse — it
means they require a different controller initialization strategy.

Importantly, the negative result is now a *genuine* negative result from a
correctly functioning harness (0% torque saturation, bounded action norms,
robot actually moves and walks for 1–5 seconds), not an artifact of
implementation bugs.

---

## Full Corrected Audits (post-fix, 2026-05-05)

After the smoke test above, the full 15-mode x 7-seed x K=1/K=8 set was
re-exported with the fixed joint permutation and rerun for 5 seconds per clip.

| Group | n | Falls | Mean track time (s) | Mean joint RMSE (rad) | Torque sat. |
|---|---:|---:|---:|---:|---:|
| K=1 | 105 | 98 | 2.005 | 0.339 | 0% |
| K=8 | 105 | 98 | 2.054 | 0.334 | 0% |
| K=8 - K=1 (paired) | 105 | - | +0.049 | -0.0056 | - |
| SONIC selector over K=1/K=8 | 105 | 98 | 2.299 | 0.310 | 0% |

The K=8 learned-policy deltas are small and non-significant despite the large
inverse-dynamics risk drop (`mean_full_risk_delta=-21.74`):

- Survival: `+0.049 s`, Wilcoxon `p=0.159` for greater survival.
- RMSE: `-0.0056 rad`, Wilcoxon `p=0.457` for lower RMSE.

The two-candidate policy-aware selector improves survival and RMSE:

- Survival: `+0.294 s`, Wilcoxon `p=1.75e-10`.
- RMSE: `-0.0295 rad`, Wilcoxon `p=0.0169`.

The corrected K=1/4/8/16 39-identity audit shows the same pattern:

| Group | n | Falls | Mean track time (s) | Mean joint RMSE (rad) | Torque sat. |
|---|---:|---:|---:|---:|---:|
| K=1 | 39 | 36 | 2.134 | 0.328 | 0% |
| K=4 | 39 | 36 | 2.132 | 0.347 | 0% |
| K=8 | 39 | 36 | 2.193 | 0.329 | 0% |
| K=16 | 39 | 36 | 2.129 | 0.315 | 0% |
| SONIC selector over K=1/4/8/16 | 39 | 36 | 2.833 | 0.286 | 0% |

Direct inverse-dynamics-selected K is not monotonic under SONIC, but the
controller-aware oracle over stored variants improves survival by `+0.699 s`
(`p=1.89e-06`) and RMSE by `-0.042 rad` (`p=0.019`). This is not a deployable
generator; it is an upper-bound audit showing that the target tracking policy
contains selection information missing from the inverse-dynamics heuristic.

---

## Videos

Side-by-side videos (left = SONIC policy simulation, right = reference replay)
are saved in `results/sonic_videos/`:

| Clip | K | Track time |
|---|---:|---:|
| walk_happy_dance_seed0_K1 | 1 | 4.78 s |
| walk_happy_dance_seed0_K8 | 8 | 2.32 s |
| slow_walk_seed0_K1 | 1 | 1.84 s |
| slow_walk_seed0_K8 | 8 | 1.62 s |
| slow_walk_seed1_K8 | 8 | 2.10 s |
| walk_seed0_K1 | 1 | 1.68 s |
| walk_seed0_K8 | 8 | 1.46 s |
| walk_gun_seed0_K1 | 1 | 1.70 s |
| walk_gun_seed0_K8 | 8 | 1.46 s |
| walk_gun_seed1_K8 | 8 | 1.76 s |

---

## Commands

Export 20 SONIC references (5 modes × 2 seeds × K=1,K=8):

```bash
python scripts/export_sonic_references.py \
  --modes walk slow_walk walk_happy_dance walk_gun hand_crawling \
  --seeds 2 \
  --k_values 1 8
```

Run the full evaluation with video output:

```bash
python scripts/evaluate_sonic_policy_mujoco.py \
  --reference_dir results/sonic_references \
  --max_seconds 5.0 \
  --provider cpu \
  --video_dir results/sonic_videos \
  --video_names walk_happy_dance_seed0_K1 walk_happy_dance_seed0_K8 \
                slow_walk_seed0_K1 slow_walk_seed0_K8
```

---

## Key Files

| File | Description |
|---|---|
| `scripts/export_sonic_references.py` | Convert MotionBricks .npy clips to SONIC CSV format |
| `scripts/evaluate_sonic_policy_mujoco.py` | SONIC encoder+decoder closed-loop in MuJoCo |
| `results/sonic_references/` | 20 exported reference clips |
| `results/sonic_policy_mujoco_tracking.csv` | Per-clip tracking metrics |
| `results/sonic_policy_mujoco_summary.csv` | K=1 vs K=8 summary |
| `results/sonic_videos/*.mp4` | Side-by-side tracking videos |
| `results/sonic_policy_mujoco_tracking_210_fixed.csv` | Corrected 105-pair full audit |
| `results/sonic_policy_selector_summary_fixed.csv` | Corrected paired stats and two-candidate selector |
| `results/sonic_policy_mujoco_tracking_k_sweep_fixed.csv` | Corrected K=1/4/8/16 audit |
| `results/sonic_policy_multik_selector_summary_fixed.csv` | Corrected four-way selector stats |
| `results/sonic_policy_multik_selector_fixed.png` | Corrected K=1/4/8/16 selector plot |

---

## Known Limitations

- Initialization mismatch: robot starts at DEFAULT standing pose; reference
  starts mid-stride. First 0.5–1 s the robot transitions rather than tracks.
- No GPU ONNX: installed wheel expects CUDA 12, machine has CUDA 13. CPU
  inference is used (policy runs fast enough for offline batch evaluation).
- The SONIC native binary (C++ DDS stack) still requires live Unitree LowState
  messages and cannot be used for batch offline evaluation.
- The corrected full 105-pair and 39-identity K-sweep audits are now available,
  but the Python harness is still an approximate offline reconstruction of
  SONIC deployment rather than the native DDS-controlled loop.
