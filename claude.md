# CS 348K — Visual Computing Systems (Spring 2026)

## Course Resources
- [Course site](https://gfxcourses.stanford.edu/cs348k/spring26/)
- [Course info / syllabus](https://gfxcourses.stanford.edu/cs348k/spring26/courseinfo)
- [Project guidelines](https://github.com/stanford-cs348k/project)
- [Class project proposals doc](https://docs.google.com/document/d/1K7WWXZXesL3PZApOppy6jPh8VGIKfYmv5nKkaiKKvsA/edit?tab=t.0)
- [Other students' proposals](CS%20348K%20Project%20Proposals.md) — useful for context and inspiration

## Project Timeline

| Date | Milestone | Weight |
|------|-----------|--------|
| ~Apr 25 (soft, ungraded) | Proposal submitted to class doc | — |
| **Fri May 8** | **Checkpoint 1** | 18% of project grade |
| **Fri May 22** | **Checkpoint 2** | 12% of project grade |
| **Tue Jun 2** | **Presentation Day + Final Report** | 70% of project grade |

Project is **50% of overall course grade** (the other 50% is reading responses + attendance/participation).

### Checkpoint 1 Requirements (May 8)
- Goal is well-defined in writing; target results articulated clearly ("this is the graph/picture I hope to make")
- Dataset / workload identified
- Evaluation infrastructure built and running end-to-end with a hello-world baseline
- After this checkpoint, staff will specify what's expected by Checkpoint 2

## Project

> **Status: active — evaluation harness complete, all plots paper-ready, awaiting MotionBricks data.**

- **Title:** Kinematic-to-Dynamic Gap in Generative Humanoid Motion
- **One-line goal:** Quantify how well MotionBricks-generated kinematic trajectories can be physically executed on the Unitree G1 in MuJoCo, and characterize failure modes by motion type.
- **Key metric / target result:** A chart: motion type × physics difficulty (joint tracking RMSE, root drift, time-to-fall, mechanical power), showing which generated motions are physically feasible vs. not.
- **Dataset / workload:** MotionBricks-generated qpos sequences (local GPU), categorized by motion style (idle, walk, jog, run, crouch, jump, wave, etc.). Baseline: BONES-SEED raw mocap data evaluated the same way.
- **Baseline:** Kinematic replay (mj_forward, zero physics) vs. physics execution (mj_step + PD controller).
- **Stack:** MotionBricks (NVlabs/GR00T-WholeBodyControl) · MuJoCo 3.2.7 · PyTorch · Python · NVIDIA GPU (local).

### Repo structure
```
src/physics_eval/   — simulator, PD controller, metrics
src/analysis/       — plotting and summary
assets/g1/          — Unitree G1 MuJoCo model + meshes
data/synthetic/     — placeholder motions for pipeline testing
data/motionbricks/  — generated clips (populated by generate_motions.py)
generate_motions.py — MotionBricks clip generation (local GPU)
results/            — output plots and CSVs
run_eval.py         — main evaluation entry point
```

### Key design decisions
- **Input format:** `(T, 36)` float32 qpos arrays — decoupled from MotionBricks inference. Generation and evaluation both run locally.
- **Controller:** Joint-space PD with gravity+Coriolis feedforward (`qfrc_bias`). Gains tuned to G1: Kp=200/Kd=10 for legs, matching typical IsaacGym/IsaacLab values. The gap the controller can't close IS the research finding.
- **Metrics:** joint tracking RMSE (scalar + per-joint 29-dim), root position drift, time-to-fall, mechanical power, joint limit violations, foot penetration, normal contact forces.
- **Visualizations (6 paper-ready plots):** tracking error by type, fall rate, time-to-fall, root error over time, per-joint heatmap, kinematic-vs-dynamic gap comparison.
- **Two modes:** `evaluate_clip()` (mj_step + PD) and `evaluate_clip_kinematic()` (mj_forward baseline); `--kinematic_baseline` flag runs both.
- **Next step (Checkpoint 2 / final):** Run on real MotionBricks data → add RL-based tracking controller → compare PD vs RL gap.

## Agent Workflow

This repo is set up for an agent-driven workflow. Claude acts as a collaborator across the full project lifecycle — brainstorming, implementation, evaluation, and writeup.

**How to work with Claude here:**
- Dump raw ideas, paper links, or course material and Claude will help structure and evaluate them
- Claude should proactively flag checkpoint deadlines when they are approaching
- For any implementation task, Claude should write code, run experiments, and summarize results
- Treat Claude as a teammate: push back, redirect, and clarify rather than accepting suggestions uncritically

Another idea: Motion brick for real robots under different terrains??
Another idea: meshai + motionbrick? meshai probably just have couple motions but provide more motions using motionbrick