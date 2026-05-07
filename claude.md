# CS 348K - MotionBricks Physical-Awareness Handoff
# Updated 2026-05-04

## Current Research Contribution

**Title:** Inverse-Dynamics-Critic-Guided Inference-Time Scaling for Humanoid Motion Generation

**Narrow claim:** MotionBricks is a strong kinematic humanoid motion generator,
but its public limitation is physical awareness. This project adds a
no-generator-retraining test-time screening layer: sample K candidate qpos clips
from MotionBricks, score them with a MuJoCo inverse-dynamics heuristic critic,
and keep the lowest-risk candidate.

This is **not** a learned tracking policy, not a real-robot safety guarantee, and
not proof that lower heuristic risk always tracks better. The strongest honest
claim is: best-of-K inference-time sampling reliably lowers a transparent
inverse-dynamics demand score for upright/expressive MotionBricks outputs.

Important update: a learned-policy audit has now been added using the released
SONIC G1 encoder/decoder weights in a MuJoCo harness. It is negative for the
inverse-dynamics-only method: all 105 K=1 and all 105 K=8 paired references
fall quickly, and K=8 does not improve survival or tracking. The strongest
future direction is controller-in-the-loop selection or planner-policy
co-training, not more heuristic-only screening.

Newer update: the SONIC harness was debugged on 2026-05-05. Three bugs were
fixed: PD torque is now recomputed every physics substep, rollout starts from
SONIC's default standing pose, and exported references now use
`MUJOCO_TO_ISAACLAB` rather than the inverse permutation. Corrected 105-pair
SONIC results: K=1 averages 2.005 s / 0.339 rad RMSE, K=8 averages 2.054 s /
0.334 rad RMSE, and both groups have 98/105 falls with 0% torque saturation.
The K=8 deltas are small and non-significant. A corrected 39-identity
K=1/4/8/16 audit shows that a policy-aware selector over stored variants
improves survival from 2.134 s to 2.833 s and RMSE from 0.328 to 0.286 rad,
while fall count remains 36/39. This is evidence for policy-in-the-loop
screening, not a finished robot-retargeting solution.

## Completed Results

- Main K sweep: 13 styles x 3 seeds x K=[1,4,8,16] = 156 selected clips.
  Results: `results/guided_ablation_full.csv`.
- Extended K=1/K=8 workload: all 15 exposed G1 demo modes x 7 seeds = 105
  paired motion identities. Results: `results/guided_ablation_extended.csv`.
- Diversity ablation: seed-only vs Gumbel-only vs combined K=4.
  Results: `results/diversity_ablation.csv`.
- Compute-matched steering attempt: WC-K4 beats PS-K4 on the current setup.
  Results: `results/steered_vs_wc_ablation.csv`.
- Semantic preservation audit: K=8 often preserves mode label, but 15/39
  benchmark pairs change root displacement outside a 0.5x-1.5x band.
  Results: `results/semantic_preservation.csv`.
- Controller negative controls: weak PD and stronger torque-limited
  computed-torque tracking do not validate per-clip critic scores.
  Results: `results/critic_vs_pd_correlation.csv`,
  `results/computed_torque_tracking.csv`.
- SONIC learned-policy audit: native SONIC deployment builds and initializes,
  but waits for live Unitree `LowState`; the Python MuJoCo harness runs the
  released SONIC ONNX encoder/decoder over all 210 exported references.
  Corrected results: K=1 survival is 2.005 s, K=8 survival is 2.054 s, and
  both fall 98/105 with 0% torque saturation.
  Results: `results/sonic_policy_mujoco_tracking_210_fixed.csv`,
  `results/sonic_policy_selector_summary_fixed.csv`,
  `results/sonic_policy_tracking_k1_k8_selector_fixed.png`,
  `docs/sonic_policy_tracking.md`.
- SONIC multi-K audit: K=1/4/8/16 screened variants over the 39-identity sweep.
  The policy-aware selector improves survival/RMSE but fall count remains 36/39.
  Results: `results/sonic_policy_mujoco_tracking_k_sweep_fixed.csv`,
  `results/sonic_policy_multik_selector_summary_fixed.csv`,
  `results/sonic_policy_multik_selector_fixed.png`,
  `results/videos/sonic_policy_multik/`.
- Neural critic: segment-level CNN mimics heuristic windows well, but
  neural-guided full-clip selection is a negative result. Extended full-clip
  training on 210 clips improves rho to 0.747. A larger 3.38M-parameter
  residual temporal CNN trained for 800 epochs on 497 unique labeled clips
  improves rho to 0.800 but still misses the 0.85 target.
  Results: `results/neural_critic/`, `results/neural_guided_ablation.csv`,
  `results/neural_critic_clip_extended/`, `results/neural_critic_clip_v2/`.
- Prompt/task suite: 105 local mode-control prompts (15 exposed G1 modes x 7
  seeds) with proxy alignment metrics. K=8 preserves broad task proxies but
  does not improve them: mean alignment 0.568 vs 0.583 for K=1, with 56/105
  pairs within -0.05 and 72/105 displacement ratios in [0.5, 1.5].
  Results: `configs/prompt_suite_105.csv`,
  `results/prompt_alignment_summary.csv`.
- Contact-quality audit: self-contact, non-foot floor contact, foot skate, and
  support-proxy metrics on the same 210 K=1/K=8 clips. Contact artifact score
  improves from 0.274 to 0.248 overall and from 0.654 to 0.489 on whole-body
  crawling, but crawling still has high non-foot floor contact.
  Results: `results/contact_quality_summary.csv`.
- Candidate audit: on a 10-batch representative K=8 audit, segment-selected and
  full-clip-selected winners agree 10/10 times. Treat as a sanity check, not a
  universal proof. Results: `results/candidate_audit_summary.csv`.

## Headline Numbers

Main 39-identity K sweep:

| K | Mean risk | Critic-accept/39 | Critic-reject/39 |
|---|---:|---:|---:|
| 1 baseline | 38.90 | 5 | 6 |
| 4 | 23.24 | 20 | 5 |
| 8 | 15.93 | 26 | 3 |
| 16 | 13.61 | 31 | 3 |

Extended 105-identity K=1/K=8 run:

| Setting | Mean risk | Median risk | Critic-accept | Critic-review | Critic-reject |
|---|---:|---:|---:|---:|---:|
| K=1 | 35.32 | 21.28 | 25/105 | 67/105 | 13/105 |
| K=8 | 13.58 | 0.00 | 78/105 | 18/105 | 9/105 |

Paired aggregate reduction is 61.55%; 81/105 paired identities improve.

Per-type extended reductions:

- Locomotion: 86.88% reduction, 49/56 critic-accepted at K=8.
- Expressive: 93.26% reduction, 28/28 critic-accepted at K=8.
- Whole-body crawling: 40.52% reduction, but 9/14 still critic-rejected.
- Static idle: -14.38% aggregate regression; do not resample already-stable idle clips.

## Important Negative Results

- PD tracking correlation is weak: risk vs PD time-to-fall rho=-0.09.
- Computed-torque tracking also fails as validation: all 78 paired K=1/K=8
  rollouts fall at frame 15, and K=8 does not improve tracking RMSE.
- Neural full-clip selection is not ready: 31% selection agreement and worse
  selected risk than heuristic WC-K8.
- Semantic preservation is not guaranteed; K=8 can lower risk by changing path
  scale or root displacement.
- Prompt proxy alignment is mostly preserved, not improved. This means best-of-K
  is a risk-screening method, not a prompt-following method.
- Contact-quality metrics improve overall but expose remaining whole-body
  artifacts, especially crawling floor contact.

These are not failures to hide. They make the report defensible by preventing
the overclaim that a heuristic inverse-dynamics score equals executable robot
motion.

## Safe Presentation Claims

- "Best-of-K inference-time compute lowers an inverse-dynamics heuristic risk
  score without retraining MotionBricks."
- "The effect is robust across 105 local MotionBricks motion identities,
  especially upright locomotion and expressive walking styles."
- "Across a 105-row local mode-seed audit (15 unique mode prompts x 7 seeds),
  K=8 lowers risk while broadly preserving simple trajectory/style proxies; it
  is not a learned language-motion evaluator and not 100 different behaviors."
- "Contact-quality metrics provide visible risk diagnostics for videos:
  self-contact, non-foot floor contact, foot skate, and support proxy."
- "Crawling remains high demand under this model and critic; the method is a
  triage/screening layer, not a controller."
- "Current forward controllers in this repo are negative controls, so the next
  serious step is PHC/CLAW-style learned tracking validation."
- "The neural critic is promising for speed at the window level, but not yet a
  reliable full-clip selector."

Do not claim:

- real robot safety,
- physical feasibility in the controller/hardware sense,
- semantic preservation for every clip,
- that crawling is fundamentally impossible,
- that K=8 generation is fully real-time end-to-end,
- that the nondeterminism is definitely caused by cuDNN.

## Commands

```bash
# Main K sweep and plots
python scripts/run_ablation.py
python scripts/plot_guided_ablation.py

# Extended 105-identity K=1/K=8 run
python scripts/run_extended_ablation.py --seeds 7 --k_values 1 8
python scripts/summarize_extended_ablation.py
python scripts/plot_extended_ablation.py

# Follow-up audits
python scripts/semantic_preservation.py
python scripts/evaluate_computed_torque.py
python scripts/full_candidate_audit.py --seeds 2 --K 8

# Videos
python scripts/render_comparison.py
python scripts/render_supplementary.py --section all
python scripts/render_risk_explainer.py --default_set

# Tests
pytest -q
```

## Key Artifacts

- Main report: `docs/final_report.md`
- Presentation notes: `docs/presentation_notes.md`
- Slide outline: `docs/slide_outline.md`
- Reviewer critique/response: `docs/reviewer.md`, `docs/critic_response.md`
- Evaluation protocol: `docs/evaluation_protocol.md`
- Prompt suite: `configs/prompt_suite_105.csv`, `docs/prompt_suite.md`
- Main figures:
  - `results/guided_risk_vs_K.png`
  - `results/guided_action_counts_vs_K.png`
  - `results/guided_k1_vs_k8_scatter.png`
  - `results/guided_extended_k1_vs_k8.png`
  - `results/guided_extended_action_counts.png`
  - `results/semantic_preservation.png`
- `results/prompt_alignment_by_category.png`
- `results/risk_vs_prompt_alignment.png`
- `results/contact_quality_by_category.png`
- `results/risk_vs_contact_artifacts.png`
- `results/computed_torque_tracking.png`
- `results/neural_critic_clip_extended/validation.png`
- `results/neural_critic_clip_v2/training.png`
- Risk-explainer videos:
  - `results/videos/risk_explainer/walk_seed0_K1_vs_K8_risk_explainer.mp4`
  - `results/videos/risk_explainer/walk_happy_dance_seed0_K1_vs_K8_risk_explainer.mp4`
  - `results/videos/risk_explainer/hand_crawling_seed0_K1_vs_K8_risk_explainer.mp4`
- Videos:
  - Original paired clips: `results/videos/comparison/*.mp4`
  - Supplementary stitched videos: `results/videos/supplementary/*.mp4`

## Next Serious Research Step

Use controller outcomes in the generation loop. The next defensible method is
to sample multiple MotionBricks candidates, run a short-horizon learned-policy
rollout, and select or fine-tune toward references that survive and track under
the target controller. The current SONIC audit shows that inverse dynamics alone
does not solve physical feasibility.

## 2026-05-05 SONIC Visualization Correction

The native SONIC deploy stack does run against the official MuJoCo simulator,
but the earlier `g1_debug` MP4s are not valid evidence for measured root
tracking. The C++ debug publisher hard-codes `base_trans_measured` in
`output_interface.hpp`, so the red/measured robot in those debug videos can
look fixed or floating even when the simulator state differs.

Use the actual-qpos renders instead:

```bash
python scripts/render_sonic_actual_sim_examples.py \
  --out_dir results/sonic_actual_sim_examples_released \
  --release_before_play \
  --release_settle 1.0

python scripts/render_sonic_actual_sim_examples.py \
  --out_dir results/sonic_actual_sim_examples_pose_aligned \
  --release_before_play \
  --release_settle 1.0 \
  --align_mode per_frame
```

Key corrected artifacts:

- `results/sonic_actual_sim_examples_released/*_actual_sim_qpos.mp4`
- `results/sonic_actual_sim_examples_released/actual_qpos_summary.csv`
- `results/sonic_actual_sim_examples_pose_aligned/*_actual_sim_qpos.mp4`
- `results/sonic_actual_sim_examples_pose_aligned/contact_sheet_pose_aligned.jpg`
- Notes: `docs/sonic_native_check.md`

Do not cite `results/sonic_native_examples/*.mp4` as physical tracking evidence.
Those are only diagnostic debug-stream videos. Also do not claim the
MotionBricks-to-SONIC exporter is fully validated yet: it currently writes root
body data, while official SONIC references include 14 tracked bodies.
