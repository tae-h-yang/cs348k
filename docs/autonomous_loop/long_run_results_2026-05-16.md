# Long-Run Results - 2026-05-16

## Runtime

The autonomous run executed from 2026-05-16 01:40 PDT to 2026-05-16 08:11 PDT
with two stages:

- `scripts/longrun_motion_curation.sh`
- `scripts/longrun_neural_critic_sweep.sh`

The neural sweep was stopped after two completed seeds to stay inside the
8-hour cap. Seed 303 began and reached epoch 50, but is not counted.

## Candidate Expansion

The expanded candidate audit produced:

- 728 candidate clips,
- 91 mode-seed identities,
- 13 exposed MotionBricks modes x 7 seeds x K=8,
- risk range: 0.0 to 328.34.

Important qualitative/quantitative finding:

- normal locomotion/style categories often have low-risk alternatives within
  K=8,
- hand/elbow crawling remains extremely high-risk across most candidates,
  matching the visual audit contact sheet and videos.

## Visual Evidence

Generated artifacts:

- `results/visual_audit_contact_sheet.png`
- `results/videos/visual_audit/audit_01_walk_left_seed2_K8.mp4`
- `results/videos/visual_audit/audit_02_walk_happy_dance_seed0_K1.mp4`
- `results/videos/visual_audit/audit_03_walk_left_seed0_K1.mp4`
- `results/videos/visual_audit/audit_04_elbow_crawling_seed5_K1.mp4`
- `results/videos/visual_audit/audit_05_hand_crawling_seed3_K8.mp4`
- `results/videos/visual_audit/audit_06_hand_crawling_seed2_K1.mp4`
- `results/videos/visual_audit/audit_07_elbow_crawling_seed3_K1.mp4`
- `results/videos/visual_audit/audit_08_elbow_crawling_seed1_K1.mp4`
- `results/videos/visual_audit/audit_09_stealth_walk_seed1_K8.mp4`
- `results/videos/visual_audit/audit_10_walk_right_seed6_K1.mp4`
- `results/videos/visual_audit/audit_11_hand_crawling_seed5_K1.mp4`
- `results/videos/visual_audit/audit_12_hand_crawling_seed0_K1.mp4`

Interpretation:

- The videos make obvious that some high-risk low-posture clips visibly collapse
  or become floor-bound.
- This supports the need for visual review and controller validation, not only
  scalar risk tables.

## Combined Selector Snapshot

From `results/longrun/latest/run_summary.md`:

| Selector | Combined | Semantic | ID Risk | Approx. SONIC Survival |
|---|---:|---:|---:|---:|
| K=1 baseline | 0.577 | 0.650 | 35.32 | 2.005 s |
| K=8 existing | 0.640 | 0.677 | 13.58 | 2.054 s |
| MotionSpec selector | 0.643 | 0.706 | 17.74 | 2.114 s |
| No-controller combined | 0.649 | 0.694 | 13.74 | 2.098 s |
| Controller combined | 0.653 | 0.697 | 14.17 | 2.148 s |
| SONIC oracle | 0.624 | 0.670 | 24.03 | 2.299 s |

Interpretation:

- Combined selection improves over K=1 on aggregate scores.
- The SONIC oracle still gets the longest approximate survival while accepting
  weaker semantic and risk scores.
- Therefore the next serious method should use controller-in-the-loop selection,
  not inverse-dynamics-only ranking.

## Neural Critic Sweep

`scripts/longrun_neural_critic_sweep.sh` trained width-512, 13.4M-parameter
clip critics on 1089 unique labeled clips.

| Seed | Epochs | Best Spearman rho | Best val loss | Train seconds |
|---:|---:|---:|---:|---:|
| 101 | 5000 | 0.797 | 0.366 | 10699 |
| 202 | 5000 | 0.759 | 0.355 | 10782 |

Interpretation:

- The larger neural critic did not reach the rho >= 0.85 credibility threshold.
- Seed 101 only slightly improves over the previous 0.789 result.
- Seed 202 is substantially weaker, showing seed/split instability.
- This is a negative result for learned imitation of the heuristic risk score as
  the main project contribution.

## Reviewer Conclusion

The long run improves the evidence base, but it does not make the project
submission-ready. It strengthens a more honest direction:

> MotionBricks candidate curation can find lower-risk alternatives for some
> locomotion/style motions, but low-posture whole-body motions remain visibly
> and dynamically problematic. Learned imitation of the heuristic critic is not
> enough; the next credible method needs controller-in-the-loop labels and
> video-grounded review.

