# SONIC Native 100-Attempt Run - 2026-05-16

## Purpose

Run a broad native SONIC release validation, not a small demo set. The batch
uses the native C++ SONIC deploy binary, the official MuJoCo simulator, real
qpos logging, and `--release_before_play` so the elastic band is disabled before
reference playback.

## Command

```bash
python scripts/run_sonic_native_release_batch.py \
  --out_dir results/sonic_native_release_overnight/20260516_085134 \
  --limit 100 \
  --max_hours 8 \
  --width 640 \
  --height 360
```

Post-processing:

```bash
python scripts/analyze_sonic_native_batch.py \
  --batch_dir results/sonic_native_release_overnight/20260516_085134
```

## Outputs

- `results/sonic_native_release_overnight/20260516_085134/batch_summary.csv`
- `results/sonic_native_release_overnight/20260516_085134/analysis_summary.md`
- `results/sonic_native_release_overnight/20260516_085134/summary_by_mode.csv`
- `results/sonic_native_release_overnight/20260516_085134/summary_by_category.csv`
- `results/sonic_native_release_overnight/20260516_085134/pass_rate_by_mode.png`
- `results/sonic_native_release_overnight/20260516_085134/pass_rate_by_category.png`
- `results/sonic_native_release_overnight/20260516_085134/strict_presentation_pass_videos/`
- `results/sonic_native_release_overnight/20260516_085134/strict_presentation_pass_contact_sheet.jpg`
- `results/sonic_native_release_overnight/20260516_085134/fail_videos/`
- `results/sonic_native_release_overnight/20260516_085134/fail_contact_sheet.jpg`

## Results

| Split | Pass / Total | Notes |
|---|---:|---|
| Overall | 84 / 100 | Native release, root-height survival threshold |
| Upright MotionBricks | 76 / 84 | Locomotion/style candidates from approximate screen |
| Strict upright | 66 / 84 | Survive, joint RMSE <= 0.20, root XY error <= 1.5 m |
| Idle controls | 8 / 8 | Expected easy controls |
| Crawling controls | 0 / 8 | Expected low-posture failures |

Mean joint RMSE over all completed attempts: 0.160 rad.

## Interpretation

This is now a controller-backed filtering result rather than a toy qualitative
demo. Native SONIC can execute a large fraction of screened upright
MotionBricks references after elastic-band release. The result is not universal:
some upright variants still fail quickly, and every sampled crawling reference
fails. That makes the strongest claim:

> Native controller-in-the-loop screening can recover a large presentable set of
> executable upright MotionBricks references, while rejecting brittle variants
> and low-posture motions that the current SONIC setup cannot track.

The recommended presentation folder is:

`results/sonic_native_release_overnight/20260516_085134/strict_presentation_pass_videos/`

The recommended failure evidence is:

`results/sonic_native_release_overnight/20260516_085134/fail_videos/`

## Visual Review Notes

The strict presentation contact sheet shows mostly upright, coherent tracking
over locomotion/style motions. The failure contact sheet shows the expected
negative controls: crawling motions become floor-bound or collapse, and several
upright variants begin in or fall into a low-root configuration. This supports a
selection/gating narrative, not a claim that MotionBricks or SONIC alone solves
all humanoid motion execution.
