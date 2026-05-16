# Final Video Sanity Audit - 2026-05-16

## What Was Checked

Artifacts inspected:

- `results/sonic_native_release_overnight/20260516_085134/strict_presentation_pass_contact_sheet.jpg`
- `results/sonic_native_release_overnight/20260516_085134/fail_contact_sheet.jpg`
- `results/sonic_native_release_overnight/20260516_085134/batch_summary.csv`
- `results/sonic_native_release_overnight/20260516_085134/summary_by_mode.csv`

This was a structured visual sanity check over sampled frames/contact sheets,
not a full external VLM API audit. The videos should still be spot-checked by a
human before presentation.

## Visual Rubric

Each final claim should satisfy:

1. Reference and actual robot are both visible.
2. Actual robot stays upright for the clip.
3. Motion is not only numerically surviving; it roughly follows the same style.
4. Root drift is not extreme.
5. Failure videos visibly show why the gate rejects candidates.

## Visual Findings

The strict presentation contact sheet is mostly coherent: upright locomotion and
style clips remain standing and roughly track the reference. The failure sheet
is also coherent: crawling examples become floor-bound/collapsed, and several
upright variants start in or fall into a low-root configuration.

The strict presentation gate is therefore more credible than a survival-only
gate. It keeps clips that:

- survived the native SONIC release run,
- had joint RMSE <= 0.20 rad,
- had mean root XY error <= 1.5 m.

This leaves 66/84 upright clips, from which 24 diverse presentation videos were
selected.

## Native Paired K1/K8 Evidence

Among upright identities where both K=1 and K=8 were present in the 100-run
native batch:

| Method | Pass / Total | Mean RMSE | Mean Fall Time | Strict Pass |
|---|---:|---:|---:|---:|
| K=1 baseline | 17 / 19 | 0.143 | 5.60 s | 16 / 19 |
| K=8 only | 17 / 19 | 0.140 | 5.65 s | 14 / 19 |
| Native best-of-{K1,K8} gate | 19 / 19 | 0.124 | 6.19 s | 18 / 19 |

Interpretation: K=8 alone is not a definitive improvement over K=1. The
improvement comes from controller-in-the-loop selection/gating, which can choose
the candidate that actually survives and tracks better.

## Answer to "Did Ours Definitely Improve?"

Yes for the narrowed method claim:

> Native SONIC controller-in-the-loop gating improves the selected executable
> set over blindly using one candidate.

No for a broader claim:

> We should not claim that K=8 alone, inverse dynamics alone, or all
> MotionBricks motions are definitely improved.

The final result is strongest as a filtering/curation method for upright
MotionBricks references, with crawling/low-posture motions explicitly rejected.
