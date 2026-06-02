# Experiment Queue

## Active

- [x] Create durable autonomous-loop docs.
- [x] Define 100 distinct humanoid robotics prompts.
- [x] Implement MotionSpec predicate checker.
- [x] Run MotionSpec on currently available K=1/K=8 clips.
- [x] Combine MotionSpec, contact, inverse dynamics, and SONIC metrics into one
  candidate table.
- [x] Compare selectors: K=1, inverse-dynamics, contact-gated, MotionSpec+ID,
  SONIC oracle/selector where available.
- [x] Render a small visual audit set with non-overlapping labels and risk
  overlays.
- [x] Add full video renderer for the visual audit manifest.
- [ ] Render full videos for the current visual audit manifest.
- [x] Run prospective held-out native SONIC selector comparison where candidate
  choices are made before controller rollout.
- [ ] Improve native SONIC/reference conversion or replace with another trusted
  G1 tracker.
- [x] Add a second-stage retiming/smoothing repair baseline for invalid or
  high-risk generated references.
- [ ] Run 4-8 hour long-run protocol and review the resulting videos/tables.
- [ ] Run multi-seed neural critic sweep and decide whether learned critic is
  credible or a negative result.
- [ ] Run RalphLoop K=32 for up to 12 hours and review whether larger
  best-of-K plus repair and corrected SONIC improves beyond the current K=8
  endpoint.
- [x] Harvest completed RalphLoop K sweeps through K1024 and decide whether
  the MotionBricks-only track can plausibly reach 80-90% controller success.
- [x] Set up Kimodo repo, isolated venv, CLI, and Kimodo-G1-RP checkpoint cache.
- [ ] Configure gated Hugging Face text-encoder access for Kimodo.
- [ ] Run Kimodo-G1 over the full 100-prompt suite.
- [ ] Evaluate Kimodo-G1 qpos exports with inverse-dynamics/contact metrics and
  approximate SONIC rollouts/videos.
- [ ] Decide final framing: MotionBricks real-time verifier, Kimodo quality
  generator, or an honest negative result about unsolved controller execution.

## Candidate Commands

```bash
python scripts/build_humanoid_robotics_prompt_suite.py
python scripts/evaluate_motionspec.py
python scripts/build_candidate_evidence_table.py
python scripts/plot_combined_selector.py
python scripts/select_visual_audit_clips.py
python scripts/render_visual_audit_contact_sheet.py
MUJOCO_GL=egl python scripts/render_visual_audit_videos.py --limit 12
bash scripts/longrun_motion_curation.sh
bash scripts/longrun_neural_critic_sweep.sh
python scripts/launch_ralphloop.py --hours 12 --k-after 32 --provider cuda
scripts/dual_track_kimodo_motionbricks_loop.sh
python scripts/analyze_dual_track_motion_generation.py
python scripts/run_kimodo_humanoid100_experiment.py --limit 100 --duration 4.0 --diffusion_steps 50
python scripts/evaluate_kimodo_humanoid100.py --manifest results/kimodo_humanoid100_g1/manifest.csv --out_dir results/kimodo_humanoid100_eval --export_sonic_refs
python scripts/evaluate_sonic_policy_mujoco.py --reference_dir results/kimodo_humanoid100_eval/sonic_references --out_csv results/kimodo_humanoid100_eval/sonic_tracking.csv --summary_csv results/kimodo_humanoid100_eval/sonic_summary.csv --provider cuda --init_reference_pose --video_dir results/kimodo_humanoid100_eval/sonic_videos
python scripts/evaluate_prompt_alignment.py
python scripts/evaluate_contact_quality.py
python scripts/run_humanoid100_motionbricks_experiment.py --render
python scripts/repair_humanoid100_references.py --render
python scripts/analyze_sonic_policy_results.py
python scripts/run_prospective_native_selection.py --seed_start 7 --n_seeds 8 --K 8
python scripts/run_sonic_native_release_batch.py --strategy all --order interleaved --limit 320
python scripts/analyze_prospective_native_selection.py --prospective_dir <run> --batch_dir <run>/native_release
python scripts/render_prospective_comparison_sheets.py --prospective_dir <run>
pytest -q
```

## Acceptance Bar For Next Report

- No claims of arbitrary text generation unless the generator actually supports
  it.
- No claims of physical execution unless controller evidence supports it.
- Every improvement claim must have a paired baseline and a video or frame audit
  path.
