# Reviewer Loop

## Purpose

This file keeps the work from becoming self-congratulatory. Each iteration must
produce artifacts, then pass through skeptical review.

## Loop Template

1. **Claim.** Write the smallest claim the new result might support.
2. **Evidence.** List exact files, commands, and metrics.
3. **Reviewer A: Control.** Attack controller validity and physical execution.
4. **Reviewer B: Semantics.** Attack prompt following and benchmark diversity.
5. **Reviewer C: Reproducibility.** Attack scripts, paths, missing artifacts,
   and untracked assumptions.
6. **Decision.** Accept, weaken claim, or run another experiment.
7. **Next experiment.** Add a concrete queue item.

## Current Claim Under Review

MotionSpec-style structured curation can select better candidates than blindly
using the existing K=8 inverse-dynamics choice on the current executable
MotionBricks mode-seed suite.

## Current Evidence

- `scripts/evaluate_motionspec.py`
- `scripts/plot_motionspec_dashboard.py`
- `results/motionspec_selector_comparison.csv`
- `results/motionspec_selector_dashboard.png`
- `results/motionspec_failure_counts.png`

## Reviewer A: Control

Objection: approximate SONIC still falls on most clips. The selector improves
average survival only slightly and does not solve tracking. This cannot support
physical execution.

Required response: make controller validity central. Either improve native
SONIC/reference conversion or frame current results as screening evidence only.

## Reviewer B: Semantics

Objection: current executable suite is 15 modes x 7 seeds, not 100 distinct
language tasks. MotionSpec predicates are handcrafted proxies.

Required response: keep the 100-prompt file as target benchmark, but clearly
separate it from executable results. Add human/VLM visual audit for prompt
matching if possible.

## Reviewer C: Reproducibility

Objection: many result folders exist and some prior videos were known-bad debug
artifacts.

Required response: use `docs/autonomous_loop/state_checkpoint.md` and
`docs/artifact_inventory.md` to mark current artifacts. Keep generated results
ignored but commands tracked.

## Decision

Current claim is acceptable only as an early curation result, not as final
robotics evidence. Next step: build a joined candidate-evidence table and a
combined selector that makes tradeoffs explicit.

