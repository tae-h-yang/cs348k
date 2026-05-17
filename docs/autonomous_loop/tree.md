# Autonomous Loop Tree

```text
docs/autonomous_loop/
├── README.md
├── benchmark_spec.md
├── blockers.md
├── candidate_methods.md
├── evaluation_protocol.md
├── evidence_log.md
├── experiment_queue.md
├── humanoid_robotics_100_prompts.md
├── long_run_protocol.md
├── problem_definition.md
├── prospective_native_selection_2026-05-16.md
├── research_notes.md
├── run_journal.md
└── state_checkpoint.md

configs/
├── prompt_suite_105.csv
└── humanoid_robotics_100_prompts.csv

scripts/
├── build_prompt_suite.py
├── build_humanoid_robotics_prompt_suite.py
├── evaluate_prompt_alignment.py
├── evaluate_contact_quality.py
├── evaluate_motionspec.py
├── plot_motionspec_dashboard.py
├── build_candidate_evidence_table.py
├── run_prospective_native_selection.py
├── analyze_prospective_native_selection.py
├── render_prospective_comparison_sheets.py
├── plot_combined_selector.py
├── select_visual_audit_clips.py
├── render_visual_audit_contact_sheet.py
├── render_visual_audit_videos.py
├── longrun_motion_curation.sh
├── longrun_neural_critic_sweep.sh
└── evaluate_sonic_policy_mujoco.py

results/  (ignored, regenerated)
├── motionspec_predicates.csv
├── motionspec_summary.csv
├── motionspec_selector_comparison.csv
├── motionspec_selector_dashboard.png
├── motionspec_failure_counts.csv
├── motionspec_failure_counts.png
├── candidate_evidence_table.csv
├── combined_selector_comparison.csv
├── combined_selector_dashboard.png
├── visual_audit_manifest.csv
├── visual_audit_contact_sheet.png
├── videos/visual_audit/*.mp4
├── longrun/latest/longrun.log
├── longrun/latest/run_summary.md
├── long_jobs/neural_critic_sweep/latest/sweep_summary.md
├── prompt_alignment.csv
├── contact_quality.csv
├── sonic_policy_mujoco_tracking_210_fixed.csv
├── sonic_native_release_all210/20260516_123519/
└── prospective_native_selection/20260516_170132/
    ├── prospective_native_analysis.md
    ├── prospective_native_selector_summary.csv
    ├── native_release/analysis_summary.md
    └── comparison_sheets/*.jpg
```

Update this file when adding a new durable loop artifact.
