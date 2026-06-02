# Autonomous Loop Readme

Last updated: 2026-05-28.

## North Star

Build a defensible research project about curating high-quality humanoid robot
motion data from kinematic generators. The current strongest direction is:

> generate multiple candidate references, verify prompt/task predicates, reject
> obvious physics/contact failures, and select candidates using controller
> rollout evidence when available.

This replaces the weaker claim that inverse dynamics alone makes MotionBricks
motions executable.

## Current Truth

- The repo can call a real local MotionBricks G1 preview through the sibling
  `GR00T-WholeBodyControl/motionbricks` checkout.
- The exposed local interface is discrete mode/control based, not a true
  arbitrary 100-prompt text-to-motion endpoint.
- `configs/prompt_suite_105.csv` has 105 rows but only 15 unique local behavior
  prompts expanded by seed.
- `configs/sports_acrobatics_stress_prompts.csv` adds cartwheel, soccer,
  baseball, basketball, racket-sport, martial-arts, and sprint-start targets,
  but most are unsupported by the current local MotionBricks preview and should
  be treated as stress prompts until a richer generator/retargeter exists.
- `results/humanoid100_eval/` audits all 100 target prompts. It renders actual
  K=1-vs-K=8 proxy videos for prompts with a local mode mapping and explicit
  unsupported placeholder videos for prompts the local preview cannot execute.
- `results/humanoid100_full_proxy_eval/` runs the complete 100-prompt
  forced-proxy experiment: every prompt has an actual before/after video, with
  semantic validity labels distinguishing supported proxies from nearest-mode
  proxies that do not satisfy the prompt.
- `results/humanoid100_motionbricks_experiment/` is the full generated 100-row
  run: each prompt gets fresh K=1 and K=8 MotionBricks proxy qpos clips,
  physics-risk scoring, candidate logs, and before/after videos.
- `results/humanoid100_repaired_retimed/` is the latest second-stage repair
  run: selected K=8 references are retimed/smoothed, rescored, and rendered.
  This improves physical-risk metrics but does not solve unsupported prompt
  semantics.
- SONIC is useful as a direction for controller-in-the-loop selection, but the
  current Python harness is approximate and should not be presented as native
  hardware-quality validation.
- The project now needs a cleaner benchmark, a verifier, and a controller-aware
  experiment loop.

## Working Tree

- `problem_definition.md`: project claim, non-claims, and success criteria.
- `benchmark_spec.md`: target 100-prompt benchmark and schema.
- `humanoid_robotics_100_prompts.md`: generated summary of the prompt suite.
- `sports_acrobatics_stress_prompts.md`: generated sports/acrobatic stress
  layer with current local support labels.
- `candidate_methods.md`: method families to test and expected evidence.
- `evaluation_protocol.md`: metrics and pass/fail criteria.
- `research_notes.md`: related work notes with source links.
- `evidence_log.md`: what prior artifacts show and what they do not show.
- `experiment_queue.md`: next experiments and commands.
- `run_journal.md`: chronological decisions and results.
- `blockers.md`: technical blockers and how to retire them.

## Immediate Next Loop

1. Generate and validate `configs/humanoid_robotics_100_prompts.csv`.
2. Implement a MotionSpec predicate layer for the executable subset and desired
   100-prompt schema.
3. Run a small controller-in-the-loop baseline slice on existing K candidates:
   compare K=1, inverse-dynamics selection, contact-gated selection, and SONIC
   selector.
4. Render an audit panel where visible risk is obvious, not hidden in CSVs.

## Latest Loop Result

`scripts/evaluate_motionspec.py` now writes:

- `results/motionspec_predicates.csv`
- `results/motionspec_summary.csv`
- `results/motionspec_selector_comparison.csv`
- `results/motionspec_selector_dashboard.png`
- `results/motionspec_failure_counts.png`

On the existing 105 paired K=1/K=8 identities, selecting by MotionSpec over the
two candidates improves mean predicate score to 0.757 and mean prompt proxy
alignment to 0.620. The controller layer remains weak: approximate SONIC falls
are still the dominant failure mode.

`scripts/evaluate_humanoid_100_prompts.py --render` now writes:

- `results/humanoid100_eval/humanoid100_eval.csv`
- `results/humanoid100_eval/README.md`
- `results/humanoid100_eval/videos/*.mp4`

On the 100-prompt target suite, the current local MotionBricks preview yields
22 proxy before/after videos and 78 explicit unsupported placeholders. This is
the correct audit framing until a generator/retargeter can execute the full
target suite.

`scripts/evaluate_humanoid_100_prompts.py --force_proxy_all --render --out_dir results/humanoid100_full_proxy_eval`
now writes a complete 100-video before/after experiment. All 100 rows have
actual rendered K=1-vs-K=8 videos, but only 22 are supported/coarse local
proxies; 78 are forced nearest-mode proxies and are labeled
`forced_proxy_not_prompt_following`.

`scripts/run_humanoid100_motionbricks_experiment.py --render` now performs the
fresh 100-row generation experiment. It generated 200 qpos clips (K=1 and K=8
selected outputs), 100 before/after videos, and
`results/humanoid100_motionbricks_experiment/category_summary.csv`. Aggregate
physics-risk reduction is 48.22% (mean K=1 risk 36.81 to mean K=8 risk 19.06),
with 80 improved, 5 worsened, and 15 tied. This still does not solve arbitrary
prompt following because 78 prompts require forced nearest-mode proxies.

`scripts/repair_humanoid100_references.py --render` now performs a stronger
second-stage physical-feasibility repair over the generated 100-row suite. It
tries identity, time-scaling, and light joint smoothing variants for each
selected K=8 reference, then keeps the lowest inverse-dynamics-risk variant.
Results are in `results/humanoid100_repaired_retimed/`: mean risk improves from
K=1 36.81 to K=8 19.06 to repaired 14.89. The repair improves 47/100 references
relative to K=8, worsens 0/100, and leaves 53/100 unchanged. This is a useful
reference-conditioning baseline, not MotionBricks fine-tuning and not a claim
that forced-proxy cartwheels/sports motions are semantically solved.

`scripts/evaluate_humanoid100_final.py` now joins the full 100-row run into a
single final evaluation table with inverse-dynamics, contact/support metrics,
and strict semantic labels. Outputs are in `results/humanoid100_final_eval/`.
The stricter verifier reports physical-pass counts of 63/100 for K=1, 83/100
for K=8, and 84/100 for repaired references. Presentation-pass counts are
15/100, 18/100, and 18/100 because only 22 prompts are semantically supported
by the local MotionBricks preview.

The 22 semantically supported prompt proxies were also exported to the
approximate SONIC MuJoCo tracker. Repaired references improve mean tracking from
2.676 s / 0.312 rad RMSE for K=1 and 2.769 s / 0.282 rad RMSE for K=8 to
2.996 s / 0.258 rad RMSE. This is controller-stress evidence, not native SONIC
certification.

For completeness, all 100 prompt identities were also exported to the same
approximate SONIC tracker across K=1, K=8, and repaired references. Repaired
references improve mean tracking from 2.232 s / 0.320 rad RMSE for K=1 and
2.271 s / 0.323 rad RMSE for K=8 to 2.588 s / 0.288 rad RMSE. The fall count is
still high (86/100 repaired), so this is evidence of improvement, not solved
humanoid tracking.

A more direct MoVer-style inference-time verifier uses the approximate SONIC
rollout itself as the selector over K=1, K=8, and repaired. That selector reaches
3.127 s mean tracking on the 22 semantically supported proxies and 2.815 s on
all 100 proxy identities. This is the cleanest current "iterative verify and
select" result, but it is expensive and still approximate.

`scripts/select_humanoid100_final_method.py` writes the current final selector
package under `results/humanoid100_final_eval/final_selector/`. It compares
fixed baselines against a risk-verifier selector and a SONIC-verifier selector,
then exports representative cases. The contact sheet at
`representative_contact_sheet.jpg` and the 27 representative MP4s are the best
place to visually inspect the final state.
