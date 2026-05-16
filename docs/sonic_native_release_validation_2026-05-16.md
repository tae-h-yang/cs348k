# SONIC Native Release Validation - 2026-05-16

## Purpose

This run checks whether the SONIC stack is actually working in its native
deployment path, and whether MotionBricks-exported references can be tracked
when the MuJoCo elastic band is released.

Important correction: videos rendered with the elastic band enabled are useful
for checking deployment, logging, and visualization, but they are not physical
survival evidence. The folders below use `--release_before_play`.

## Commands

Official SONIC sanity check:

```bash
MUJOCO_GL=egl python scripts/render_sonic_actual_sim_examples.py \
  --out_dir results/sonic_native_release_20260516_official \
  --motions forward_lunge_R_001__A359_M walking_quip_360_R_002__A428 squat_001__A359 \
  --release_before_play --release_settle 1.0 \
  --align_mode initial --width 960 --height 540
```

Representative MotionBricks check:

```bash
MUJOCO_GL=egl python scripts/render_sonic_actual_sim_examples.py \
  --reference_root results/sonic_references_210_fixed \
  --out_dir results/sonic_native_release_20260516_motionbricks \
  --motions idle_seed0_K1 walk_happy_dance_seed0_K1 stealth_walk_seed1_K8 walk_left_seed2_K8 hand_crawling_seed0_K1 elbow_crawling_seed3_K8 \
  --release_before_play --release_settle 1.0 \
  --align_mode initial --width 960 --height 540
```

Curated MotionBricks batch:

```bash
MUJOCO_GL=egl python scripts/render_sonic_actual_sim_examples.py \
  --reference_root results/sonic_references_210_fixed \
  --out_dir results/sonic_native_release_20260516_curated_batch \
  --motions walk_happy_dance_seed0_K1 stealth_walk_seed1_K8 walk_left_seed2_K8 walk_left_seed0_K1 walk_seed5_K1 injured_walk_seed2_K8 walk_happy_dance_seed3_K8 walk_right_seed2_K8 slow_walk_seed4_K1 walk_seed3_K8 stealth_walk_seed6_K1 walk_boxing_seed2_K1 hand_crawling_seed0_K1 elbow_crawling_seed3_K8 \
  --release_before_play --release_settle 1.0 \
  --align_mode initial --width 960 --height 540
```

Incremental strict-gate check:

```bash
MUJOCO_GL=egl python scripts/render_sonic_actual_sim_examples.py \
  --reference_root results/sonic_references_210_fixed \
  --out_dir results/sonic_native_release_20260516_curated_incremental \
  --motions injured_walk_seed6_K8 walk_happy_dance_seed4_K1 walk_scared_seed5_K8 walk_boxing_seed6_K8 \
  --release_before_play --release_settle 1.0 \
  --align_mode initial --width 960 --height 540
```

## Outputs

- `results/sonic_native_release_20260516_official/`
- `results/sonic_native_release_20260516_motionbricks/`
- `results/sonic_native_release_20260516_curated_batch/`
- `results/sonic_native_release_20260516_curated_pass/`
- `results/sonic_native_release_20260516_curated_incremental/`
- `results/sonic_native_release_20260516_strict_pass/`

Each folder contains MP4s, `native_tracking_summary.csv`, and a
`contact_sheet.jpg`.

## Result Summary

Official release sanity check:

| Motion | Root-threshold flag | Time | Joint RMSE |
|---|---:|---:|---:|
| `forward_lunge_R_001__A359_M` | flagged | 6.33 s | 0.409 |
| `walking_quip_360_R_002__A428` | pass | 11.00 s | 0.232 |
| `squat_001__A359` | flagged at 0.00 s | 0.00 s | 0.536 |

The squat flag is a known limitation of the simple root-height threshold: the
reference intentionally lowers the body. Use the video/contact sheet for that
case.

Representative MotionBricks release check:

| Group | Result |
|---|---|
| Upright examples | 4/4 survived full clip, RMSE 0.110-0.136 |
| Crawling examples | 0/2 survived full clip |

Curated MotionBricks release batch:

| Group | Result |
|---|---|
| Upright candidates | 11/12 survived full clip |
| Crawling negative controls | 0/2 survived full clip |
| Clean pass folder | 11 selected MP4s |

Expanded strict-gate upright set:

| Group | Result |
|---|---|
| Approx-screened upright candidates | 14/16 survived full clip |
| Mean joint RMSE over 16 | 0.139 rad |
| Native-release rejected candidates | `walk_seed3_K8`, `injured_walk_seed6_K8` |
| Clean strict pass folder | 14 selected MP4s |

## Interpretation

SONIC is working well enough to use as a native controller-in-the-loop
validation tool. The earlier impression that all MotionBricks-to-SONIC results
were broken was partly caused by the approximate Python harness and misleading
debug visualizations.

The strongest defensible project claim is now narrower and better:

> For upright locomotion/style clips, MotionBricks references can be screened
> into a set that tracks under native SONIC with elastic-band release. Low
> posture crawling remains a failure category and should be rejected or handled
> by a specialized controller/training setup.

This is not yet "100% all humanoid motions." It is a credible controller-backed
filtering result for the subset that SONIC can track.

The recommended presentation folder is
`results/sonic_native_release_20260516_strict_pass/`. The recommended negative
controls are `hand_crawling_seed0_K1`, `elbow_crawling_seed3_K8`,
`walk_seed3_K8`, and `injured_walk_seed6_K8`.
