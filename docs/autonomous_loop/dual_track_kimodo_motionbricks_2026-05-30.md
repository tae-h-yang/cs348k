# Dual-Track MotionBricks/Kimodo Status

Date: 2026-05-30.

## Decision

The project should now be run as two complementary tracks:

1. MotionBricks as the low-latency candidate generator: useful for real-time
   sampling, verifier/reranker studies, and exposing physical failure modes.
2. Kimodo-G1 as the motion-quality track: likely better aligned with humanoid
   robot motion quality because it has a G1-native model and documented MuJoCo
   qpos export.

This is a correction from the too-strong earlier claim that MotionBricks
best-of-K plus repair can make all 100 prompts physically executable.

## Current Evidence

Best completed MotionBricks 100-prompt K sweep under the approximate Python
bridge:

- Run: `results/ralphloop/20260529_191342`
- K: `256`
- Selector: `sonic_verified_best`
- Physical metric pass: `76/100`
- Approximate SONIC no-fall: `17/100`
- Mean approximate SONIC survival: `2.786s`
- End-to-end wall time: `97.8` minutes

Scaling beyond K=256 did not materially improve controller acceptance:
K512 and K1024 remained around 16 no-fall clips. This strongly suggests
candidate ranking and simple kinematic repair are not enough to reach the
80-90% execution target on the current MotionBricks path.

The compute-efficiency plot in
`results/dual_track/latest/motionbricks_compute_efficiency.png` makes this
visible: larger K consumes much more wall-clock time, but the controller
acceptance curve is almost flat.

However, the native SONIC path is much more favorable than the approximate
bridge. I ran the `sonic_verified_best` selected reference for all 100
Humanoid100 prompts through the native SONIC release stack:

- Native no-fall: `76/100`
- Native strict pass: `66/100`
- Mean joint RMSE: `0.168`
- Semantic-supported prompts: `22/100`; the remaining prompts are still
  MotionBricks proxy behaviors rather than true language-conditioned generation.

Category pattern:

| category | no-fall | strict | interpretation |
|---|---:|---:|---|
| dynamic locomotion | 13/14 | 12/14 | strong for upright locomotion proxies |
| balance recovery | 12/12 | 11/12 | strong |
| terrain/obstacle | 8/8 | 6/8 | strong but proxy-only |
| loco-manipulation | 13/14 | 12/14 | surprisingly strong as proxy motions |
| manipulation stance | 10/12 | 9/12 | mostly stable |
| communication/safety | 8/8 | 8/8 | strong |
| dance/expressive | 8/12 | 6/12 | mixed |
| floor/low posture | 3/12 | 2/12 | mostly fails |
| athletic stress | 1/8 | 0/8 | mostly fails |

Artifacts:

- Full native batch:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/all100_native_sonic_release/`
- Joined Humanoid100 analysis:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/all100_native_sonic_release/humanoid100_native_analysis.md`
- Strict-pass sheet:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/all100_native_sonic_release/strict_presentation_pass_contact_sheet.jpg`
- Failure sheet:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/all100_native_sonic_release/fail_contact_sheet.jpg`

This changes the MotionBricks track from "mostly failed approximate bridge" to
"useful real-time proxy generator plus verifier for a large upright capability
envelope, with explicit failures on floor/acrobatic behaviors and exact prompt
coverage."

I then retested K1, K8, and repaired/K9 variants for the hard prompts. With
the corrected reference-aware fall metric, repeat-conservative native verifier
selection reaches:

- Native no-fall with native verifier selection/retry: `100/100`
- Native strict pass with native verifier selection/retry: `74/100`

The 100/100 number is a survival/screening claim, not a perfect prompt or pose
tracking claim. Strict failures are concentrated in floor/low-posture and
athletic/acrobatic motions. A targeted deep retry produced one extra strict
pass in its first rollout (`hrb_096_sprawl_recovery_deep02_k0008`), but that
clip did not repeat as strict in the diagnostic contact render, so it remains
exploratory. The still non-strict set
is almost entirely crawling/floor transitions and acrobatic stress tests.

Artifact:

- `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/failed_prompt_native_variant_sweep/native_variant_rescue_analysis.md`

Important correction: the approximate Python SONIC bridge was too pessimistic
for the semantically supported K256 subset. I ran those same 22 selected
references through the native SONIC release path:

- Native no-fall: `16/22`
- Native strict pass: `14/22`
- Mean joint RMSE: `0.165`
- Failures: `zombie_walk`, `scared_sneak`, `hand_crawl`, `elbow_crawl`,
  `bear_crawl`, and `direct_traffic`

Artifacts:

- Native batch: `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_native_sonic_release/`
- Strict-pass sheet:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_native_sonic_release/strict_presentation_pass_contact_sheet.jpg`
- Failure sheet:
  `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_native_sonic_release/fail_contact_sheet.jpg`

Interpretation: the defensible MotionBricks claim is stronger but narrower
than the all-100 goal. For semantically supported upright/dance/gesture clips,
the verifier-selected references often execute under native SONIC. Low-posture
and some stylized unstable clips still fail.

I also swept approximate SONIC bridge gains on the semantically supported K256
selections to test the most obvious implementation objection: maybe the
MotionBricks candidates were fine and only our controller gains were wrong.
That did not explain the failures. Across 12 settings, the best setting
(`kp0.7_kd1.0`) reached only `7/22` no-fall with `3.509s` mean survival; every
tested setting stayed at `7/22` no-fall. This makes it much less plausible that
the execution gap is a one-knob bridge-tuning artifact.

Watchable evidence for that sweep is now under
`results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_sonic_gain_sweep/best_videos/`,
with the quick visual index at
`results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_sonic_gain_sweep/best_videos_contact_sheet.jpg`.
The visual pattern matches the metric: stable cases are mostly gentle,
upright communication gestures, while locomotion, dance, and low-posture
motions still fail.

## Kimodo Setup

Local setup is ready except for gated text-encoder access:

- Repo: `/home/rewardai/repos/kimodo`
- Isolated venv: `/home/rewardai/repos/cs348k/.venv/kimodo`
- Kimodo CLI: available
- Kimodo-G1-RP-v1 checkpoint cache: present at
  `/home/rewardai/.cache/huggingface/hub/models--nvidia--Kimodo-G1-RP-v1`
- Local GPU: RTX 4060 Laptop GPU, about 8 GB VRAM
- Required workaround for small GPU: `TEXT_ENCODER_DEVICE=cpu`

The remaining blocker is Hugging Face access for the gated Llama/LLM2Vec text
encoder used by Kimodo. The generation runner records this as
`blocked_missing_hf_token` when no token is configured.

## Negative Control

A zero-text fake encoder smoke test successfully loaded the G1 model/export
path and wrote a `(30, 36)` qpos clip, but it failed the physical verifier:

- File: `results/kimodo_zero_text_smoke/zero_text_qpos.npy`
- Eval: `results/kimodo_zero_text_smoke_eval/summary.csv`
- Result: physical pass `0/1`, mean risk `280.782`

Interpretation: bypassing text conditioning is not a credible method. It only
validates that the local G1 checkpoint/export path can produce qpos once the
text encoder is available.

## Bundled Kimodo-G1 Demo Sanity Set

Because full text-conditioned generation is blocked by gated text-encoder
access, I also evaluated the official bundled Kimodo-G1 demo motions that ship
with the repo. These are native Kimodo outputs, not generated by our local
prompt runner.

Artifacts:

- Conversion manifest: `results/kimodo_g1_examples_qpos/manifest.csv`
- Qpos clips: `data/kimodo_g1_examples_qpos/*.npy`
- Physical metrics: `results/kimodo_g1_examples_eval/final_metrics.csv`
- Physical summary: `results/kimodo_g1_examples_eval/summary.csv`
- Approximate SONIC tracking: `results/kimodo_g1_examples_eval/sonic_tracking_cuda.csv`
- Videos: `results/kimodo_g1_examples_eval/sonic_videos_cuda/*.mp4`
- Contact sheet: `results/kimodo_g1_examples_eval/sonic_videos_cuda_contact_sheet.jpg`

Results:

- Physical verifier pass: `2/8`
- Physical verifier actions: `2 accept`, `5 repair_or_rerank`,
  `1 reject_or_regenerate`
- Approximate SONIC no-fall: `3/8`
- Mean approximate SONIC survival: `3.41s`
- Approximate SONIC gain sweep: best of 12 tested gain settings remains
  `3/8` no-fall, best mean survival `3.555s`

Interpretation: Kimodo is still the better-quality generator track, but
official demo clips are not automatically guaranteed to satisfy our robot
execution gate. This supports the final project framing: generation quality and
robot-execution validity must be evaluated separately.

## Automation

The long monitor is:

```bash
scripts/dual_track_kimodo_motionbricks_loop.sh
```

When a Hugging Face token becomes available, it will automatically:

1. generate the 100 Humanoid100 prompts with Kimodo-G1,
2. validate/export qpos clips,
3. run inverse-dynamics/contact evaluation,
4. export SONIC references,
5. run the approximate SONIC bridge with rollout and video export.

Latest live report:

```text
results/dual_track/latest/dual_track_status.md
results/dual_track/latest/kimodo_status.json
```

## Next Actions

1. Configure a Hugging Face token with access to the Kimodo text encoder
   dependency, then let the loop run to completion.
2. If Kimodo produces strong G1 qpos clips, compare MotionBricks versus Kimodo
   using the identical 100-prompt verifier table and a selected video set.
3. If Kimodo also fails controller execution, present the honest final claim:
   verifier/reranker methods can screen and improve motion datasets, but
   guaranteed physical execution needs co-training or a policy-aware generator.
