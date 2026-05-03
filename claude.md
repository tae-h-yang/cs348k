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

> **Status: active — evaluation harness built and running end-to-end.**

- **Title:** Kinematic-to-Dynamic Gap in Generative Humanoid Motion
- **One-line goal:** Quantify how well MotionBricks-generated kinematic trajectories can be physically executed on the Unitree G1 in MuJoCo, and characterize failure modes by motion type.
- **Key metric / target result:** A chart: motion type × physics difficulty (joint tracking RMSE, root drift, time-to-fall, mechanical power), showing which generated motions are physically feasible vs. not.
- **Dataset / workload:** MotionBricks-generated qpos sequences (via Colab GPU), categorized by motion style (idle, walk, jog, run, crouch, jump, wave, etc.). Baseline: BONES-SEED raw mocap data evaluated the same way.
- **Baseline:** Kinematic replay (mj_forward, zero physics) vs. physics execution (mj_step + PD controller).
- **Stack:** MotionBricks (NVlabs/GR00T-WholeBodyControl) · MuJoCo 3.2.7 · Python · Colab for generation · MacBook for evaluation.

### Repo structure
```
src/physics_eval/   — simulator, PD controller, metrics
src/analysis/       — plotting and summary
assets/g1/          — Unitree G1 MuJoCo model + meshes
data/synthetic/     — placeholder motions for pipeline testing
data/motionbricks/  — (to be populated via Colab)
colab/              — generation scripts to run on Colab GPU
results/            — output plots and CSVs
run_eval.py         — main evaluation entry point
```

### Key design decisions
- **Input format:** `(T, 36)` float32 qpos arrays — completely decoupled from MotionBricks inference. Colab generates, MacBook evaluates.
- **Controller:** Joint-space PD tracking (29 torque actuators). Simple baseline — the gap it can't close IS the research finding.
- **Metrics:** joint tracking RMSE, root position drift, time-to-fall, mechanical power, joint limit violations, foot penetration.
- **Next step (Checkpoint 2 / final):** Add RL-based tracking controller and compare against PD baseline.

## Agent Workflow

This repo is set up for an agent-driven workflow. Claude acts as a collaborator across the full project lifecycle — brainstorming, implementation, evaluation, and writeup.

**How to work with Claude here:**
- Dump raw ideas, paper links, or course material and Claude will help structure and evaluate them
- Claude should proactively flag checkpoint deadlines when they are approaching
- For any implementation task, Claude should write code, run experiments, and summarize results
- Treat Claude as a teammate: push back, redirect, and clarify rather than accepting suggestions uncritically

Another idea: Motion brick for real robots under different terrains??
Another idea: meshai + motionbrick? meshai probably just have couple motions but provide more motions using motionbrick