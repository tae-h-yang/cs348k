# Humanoid Robotics 100-Prompt Benchmark

This is the target benchmark for the pivoted project. It contains 100
distinct humanoid robotics motion intents, not seed duplicates. It is a
specification for generation and evaluation; the current local MotionBricks
preview only supports a subset through discrete G1 modes.

## Category Counts

- `balance_recovery`: 12
- `communication_safety`: 10
- `loco_manipulation`: 18
- `locomotion_basic`: 16
- `low_posture`: 10
- `manipulation_stance`: 12
- `terrain_obstacle`: 12
- `workspace_task`: 10

## Current Generator Support

- `__NO__`: 61
- `__PARTIAL__`: 37
- `__YES_MODE_PROXY__`: 2

## Required Evaluation Layers

- MotionSpec predicates: prompt-derived checks for direction, speed, posture, arm role, contacts, and event order.
- Kinematic checks: finite qpos, joint limits, root height, foot skate, self-contact, non-foot floor contact.
- Dynamics checks: inverse dynamics torque demand, unactuated root wrench, velocity/acceleration/jerk.
- Controller checks: SONIC or another learned G1 tracker for survival time, tracking RMSE, falls, and effort.
- Visual audit: rendered clips or contact sheets reviewed for prompt match and obvious artifacts.

## First 20 Prompts

| ID | Category | Prompt | Support |
|---|---|---|---|
| `hrb_001` | `locomotion_basic` | Walk forward at a comfortable indoor pace with symmetric arm swing. | `__PARTIAL__` |
| `hrb_002` | `locomotion_basic` | Walk forward slowly as if approaching a fragile object. | `__PARTIAL__` |
| `hrb_003` | `locomotion_basic` | Power-walk forward with brisk but non-running steps. | `__PARTIAL__` |
| `hrb_004` | `locomotion_basic` | Walk backward for several steps while keeping the chest facing forward. | `__PARTIAL__` |
| `hrb_005` | `locomotion_basic` | Sidestep to the robot's left with feet never crossing. | `__YES_MODE_PROXY__` |
| `hrb_006` | `locomotion_basic` | Sidestep to the robot's right with feet never crossing. | `__YES_MODE_PROXY__` |
| `hrb_007` | `locomotion_basic` | Turn in place ninety degrees to the left without traveling forward. | `__PARTIAL__` |
| `hrb_008` | `locomotion_basic` | Turn in place ninety degrees to the right without traveling forward. | `__PARTIAL__` |
| `hrb_009` | `locomotion_basic` | Walk along a gentle left-curving path while looking in the travel direction. | `__PARTIAL__` |
| `hrb_010` | `locomotion_basic` | Walk forward and come to a balanced stop with both feet planted. | `__PARTIAL__` |
| `hrb_011` | `locomotion_basic` | Start from standing and smoothly accelerate into a walk. | `__PARTIAL__` |
| `hrb_012` | `locomotion_basic` | Walk forward, slow down for two steps, then resume normal speed. | `__PARTIAL__` |
| `hrb_013` | `locomotion_basic` | Walk forward on an imaginary narrow walkway with careful foot placement. | `__PARTIAL__` |
| `hrb_014` | `locomotion_basic` | Walk forward with a deliberately wide stable stance. | `__PARTIAL__` |
| `hrb_015` | `locomotion_basic` | March in place with clear alternating knee lifts. | `__PARTIAL__` |
| `hrb_016` | `locomotion_basic` | Shuffle forward with short low steps and minimal arm swing. | `__PARTIAL__` |
| `hrb_017` | `terrain_obstacle` | Step over a low obstacle with the right foot first. | `__NO__` |
| `hrb_018` | `terrain_obstacle` | Step over a low obstacle with the left foot first. | `__NO__` |
| `hrb_019` | `terrain_obstacle` | Walk forward using high steps as if crossing scattered cables. | `__NO__` |
| `hrb_020` | `terrain_obstacle` | Crouch slightly while walking under a low bar, then return upright. | `__NO__` |
