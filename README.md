# Kinematic-to-Dynamic Gap in Generative Humanoid Motion

CS 348K (Visual Computing Systems, Stanford, Spring 2026) course project.

This repo studies a physical-awareness layer for MotionBricks-style kinematic
humanoid plans. The current defensible project is **controller-in-the-loop
curation and abstention**:

1. generate a fixed MotionBricks candidate pool,
2. score candidates with transparent pre-controller diagnostics,
3. evaluate selected references through native SONIC G1 tracking,
4. train a trajectory-level qpos acceptance model from native labels,
5. audit rendered videos frame-by-frame so the result is not just a CSV story.

The final-talk claim is intentionally scoped:

> Native SONIC exposes a real kinematic-to-dynamic gap. Hand-coded root/contact
> gates currently give the strongest full-coverage selector. A learned qpos
> acceptance model predicts native controller success better than scalar
> diagnostics and is useful for abstention/triage, but it does not fine-tune
> MotionBricks, solve crawling, or beat the hand-coded gate.

Latest headline numbers:

| Result | Strict native SONIC pass |
|---|---:|
| Deterministic MotionBricks baseline | 70/104 |
| Hand-coded gated pre-controller selector | 78/104 |
| Learned acceptance selector | 76/104 |
| Learned abstention, score >= 0.5 | 76/88 accepted |
| Hybrid hard-gate + learned ranking | 74/88 accepted |

The 16 crawling/low-posture identities are an explicit negative control:
current SONIC release validation gets 0/16 strict for them. Do not claim broad
whole-body generation is solved.

Current result docs:

- `docs/prospective_broad13_2026-05-22.md`
- `docs/native_acceptance_broad13_2026-05-23.md`
- `docs/learned_acceptance_prospective_2026-05-23.md`
- `docs/hybrid_acceptance_queue_2026-05-23.md`

## Setup

Requires [conda](https://docs.conda.io/en/latest/miniconda.html) and an NVIDIA GPU.

```bash
bash setup.sh
conda activate cs348k
```

## Generating MotionBricks Data

Clone and install MotionBricks (one-time):

```bash
git clone https://github.com/NVlabs/GR00T-WholeBodyControl.git
cd GR00T-WholeBodyControl/motionbricks
git lfs pull
pip install -e .
cd -
```

Then generate clips (writes to `data/motionbricks/`):

```bash
python generate_motions.py
```

## Running the Evaluation

**Synthetic baseline** (no data generation needed):
```bash
python run_eval.py --data_dir data/synthetic --kinematic_baseline --inverse_dynamics --no_plot
```

**MotionBricks clips** (after running `generate_motions.py`):
```bash
python run_eval.py --data_dir data/motionbricks --kinematic_baseline --inverse_dynamics --full_report
```

Results (plots, CSVs, optional videos) are written to ignored `results/`.

Render presentation-safe kinematic reference clips:
```bash
python run_eval.py --data_dir data/motionbricks --full_report --render --no_plot
```

Render explicitly labeled PD comparison clips only for debugging/controller discussion:
```bash
python run_eval.py --data_dir data/motionbricks --full_report --render --render_mode side_by_side --no_plot
```

Render every clip only when needed:
```bash
python run_eval.py --data_dir data/motionbricks --full_report --render --render_all --no_plot
```

Run the main MotionBricks best-of-K ablation:
```bash
python scripts/run_ablation.py
python scripts/plot_guided_ablation.py
```

Run the 105-identity K=1/K=8 extension:
```bash
python scripts/run_extended_ablation.py --seeds 7 --k_values 1 8
python scripts/summarize_extended_ablation.py
python scripts/plot_extended_ablation.py
```

Run follow-up audits:
```bash
python scripts/build_prompt_suite.py
python scripts/evaluate_prompt_alignment.py
python scripts/evaluate_contact_quality.py
python scripts/semantic_preservation.py
python scripts/evaluate_computed_torque.py
python scripts/full_candidate_audit.py --seeds 2 --K 8
```

Render supplementary videos:
```bash
python scripts/render_supplementary.py --section all
```

Render videos that make the risk score visible over time:
```bash
python scripts/render_risk_explainer.py --default_set
python scripts/render_risk_explainer.py --clip walk_seed0 --K 1 8
```

Older physical-awareness repair experiment on the full local workload:
```bash
python run_physaware.py --all
```

Render paired original/repaired reference videos for the 10 demo examples:
```bash
python run_physaware.py --render
```

Run physical-aware seed reranking across all multi-seed styles:
```bash
python scripts/physaware_seed_rerank.py
```

Controller stress-test knobs:
```bash
python run_eval.py --data_dir data/motionbricks --full_report --pd_kp_scale 0.75 --pd_kd_scale 1.0
```

Reproduce the 100-run representative PD gain sweep:
```bash
python scripts/sweep_pd_gains.py
```

## Project Structure

```
src/physics_eval/   — MuJoCo simulator, PD controller, metrics
src/analysis/       — plotting and summary
assets/g1/          — Unitree G1 MuJoCo model + meshes
data/synthetic/     — small synthetic motions for pipeline testing
data/motionbricks/  — generated clips (populated by generate_motions.py)
generate_motions.py — MotionBricks clip generation (local GPU)
run_eval.py         — evaluation entry point
docs/               — presentation notes and project narrative
scripts/            — PD sweep and PhysAware seed-reranking utilities
```

## Key Metrics

- Physical-awareness risk score: weighted combination of torque, root-wrench,
  velocity, acceleration, and jerk risks
- Inverse-dynamics torque demand: `|required torque| / actuator limit`
- Inverse-dynamics root wrench: unactuated root force/torque needed for exact replay
- Prompt/task proxy alignment: speed, direction/progress, posture, and upper-body
  style proxies for the 105 local mode-control prompts
- Contact artifact score: self-contact, non-foot floor contact, foot contact
  skate, and a simple support proxy
- Kinematic baseline checks: joint-limit violations, foot penetration, low-root clips
- Forward PD baseline: tracking RMSE, root drift, time-to-fall, mechanical power

## Current MotionBricks Result Snapshot

The original K sweep contains 39 MotionBricks motion identities:

- 18 locomotion
- 12 expressive
- 6 whole-body/crawling
- 3 static/idle

Current inverse-dynamics group means from `results/inverse_dynamics_summary.csv`:

| Type | Clips | Mean p95 torque/limit | Mean exceeded joints | Mean p95 root force |
| --- | ---: | ---: | ---: | ---: |
| static | 3 | 1.23x | 6.5% | 6.8 kN |
| locomotion | 18 | 1.70x | 7.1% | 6.8 kN |
| expressive | 12 | 1.86x | 7.6% | 6.8 kN |
| whole_body | 6 | 9.85x | 16.2% | 46.8 kN |

Interpretation: most upright motions look kinematically plausible but still ask
for actuator-limit or root-wrench help; crawling/whole-body clips are a much
larger dynamic outlier. Absolute root-wrench magnitudes are contact/model
sensitive, so use them primarily for category comparisons. See
`docs/presentation_notes.md` for the talk storyline.

The default forward PD baseline is still a weak controller baseline, not a
presentation-quality tracker. Use reference videos for visual motion examples,
and use inverse-dynamics plots for the quantitative claim. The PD sweep artifact
is written to `results/pd_gain_sweep.csv` and `results/pd_gain_sweep_heatmap.png`.

## Current Best-of-K Result Snapshot

Main 39-identity K sweep (`results/guided_ablation_full.csv`):

| K | Mean risk | Heuristic-accepted clips |
| --- | ---: | ---: |
| 1 | 38.90 | 5/39 |
| 4 | 23.24 | 20/39 |
| 8 | 15.93 | 26/39 |
| 16 | 13.61 | 31/39 |

Extended 105-identity K=1/K=8 run
(`results/guided_ablation_extended.csv`):

| Setting | Mean risk | Median risk | Critic-accept | Critic-review | Critic-reject |
| --- | ---: | ---: | ---: | ---: | ---: |
| K=1 | 35.32 | 21.28 | 25/105 | 67/105 | 13/105 |
| K=8 | 13.58 | 0.00 | 78/105 | 18/105 | 9/105 |

Paired aggregate reduction is 61.55%; 81/105 paired identities improve.
Locomotion and expressive modes improve strongly, whole-body crawling remains
mostly critic-rejected, and static idle clips regress slightly because resampling an
already-stable motion injects unnecessary variation.

Prompt/task preservation on the same 105 rows is deliberately reported as a
proxy, because the current local MotionBricks preview is mode/control based
rather than arbitrary text-to-motion. The generated suite is in
`configs/prompt_suite_105.csv`; it contains 15 unique local mode prompts x 7
seeds, not 100 different behaviors. K=8 has mean proxy alignment 0.568 vs 0.583 for
K=1; 56/105 pairs stay within -0.05 alignment and 72/105 keep displacement
ratio in [0.5, 1.5]. This supports "risk screening mostly preserves the local
task," not "risk screening improves language alignment."

Contact-quality metrics add visible physics diagnostics. Mean contact artifact
score improves from 0.274 at K=1 to 0.248 at K=8; whole-body crawling improves
from 0.654 to 0.489 but still shows high non-foot floor contact. Use these plots
when explaining what "risk" means in the videos.

Use these as the main presentation artifacts:

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
- `results/videos/comparison/*.mp4`
- `results/videos/supplementary/*.mp4`
- `results/videos/risk_explainer/*.mp4`

Important caveats:

- The critic is a heuristic pre-screen, not a safety certificate.
- Weak PD and computed-torque tracking do not validate per-clip risk scores.
- Semantic preservation is not guaranteed for every K=8 selected clip.
- Prompt following is evaluated with local task proxies, not HumanML3D-style
  R-Precision or a learned text-motion retrieval model.
- The released SONIC G1 policy was also audited in an approximate MuJoCo
  harness. After fixing the harness, the corrected 105-pair audit has 0%
  torque saturation: K=1 averages 2.005 s / 0.339 rad RMSE and K=8 averages
  2.054 s / 0.334 rad RMSE, with 98/105 falls in both groups. The K=8 deltas
  are small and non-significant despite lower inverse-dynamics risk. On the
  39-identity K=1/4/8/16 sweep, a controller-aware selector over stored
  variants improves mean survival from 2.134 s to 2.833 s and RMSE from 0.328
  to 0.286 rad, but fall count remains 36/39. The next required method is
  controller-in-the-loop screening or planner-policy co-training, not more
  heuristic-only scoring.

Neural-critic status: the segment-level critic reaches rho=0.919 against
heuristic window labels, but clip-level selection remains unresolved. A larger
3.38M-parameter clip critic trained for 800 epochs on 497 unique labeled clips
reaches rho=0.800, still below the rho=0.85 replacement target.

## Older PhysAware Retiming Snapshot

On all 39 local MotionBricks clips, deterministic test-time candidates
(`slow_1p5x`, `slow_2x`, smoothing, and smoothing+slowing) reduce the mean
heuristic feasibility risk from 35.43 to 23.74. That is a **33.0% aggregate
risk reduction**, or **48.0% mean per-clip reduction**; 32 of 39 clips improve.
The selected set increases critic-accepted clips from 8 to 17 while leaving the 5
high-risk crawling clips marked `critic_reject`/`reject_or_regenerate` in the
historical CSVs.

Important honesty point: the strongest repair is mostly retiming. Always using
`slow_2x` gives almost the same aggregate mean risk as the selected candidate
pool, while smoothing alone is slightly worse than the original. Present this
as evidence that a feasibility critic can identify when simple retiming helps
and when regeneration is still required, not as a claim that the system has
solved physical motion generation.

Across 13 styles with multiple generated seeds, critic-based seed reranking
reduces expected risk from 35.43 for a random seed to 23.00 for the selected
seed. That is a **35.1% aggregate reduction** and **53.2% mean per-style
reduction**. This is the cleanest planner-facing intervention: generate
multiple candidates, score them with the physical-awareness critic, and choose
the lower-risk plan before tracking.

Key artifacts:

- `results/physaware_before_after_risk.png`
- `results/physaware_risk_reduction_hist.png`
- `results/physaware_seed_rerank.png`
- `results/physaware_summary.csv`
- `results/physaware_best.csv`
- `results/physaware_variant_baselines.csv`
- `results/physaware_seed_rerank.csv`
- `results/physaware_seed_rerank_summary.csv`

Presentation-facing docs:

- `docs/final_report.md`
- `docs/evaluation_protocol.md`
- `docs/presentation_notes.md`
- `docs/slide_outline.md`
- `docs/critic_response.md`

## Tests

```bash
pytest -q
```

The tests cover loader validation, model layout, torque clamping, invalid clip
handling, quaternion normalization, inverse-dynamics finiteness, and fall-at-zero
aggregation.
