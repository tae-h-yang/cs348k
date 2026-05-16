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
├── problem_definition.md
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
├── plot_combined_selector.py
├── select_visual_audit_clips.py
├── render_visual_audit_contact_sheet.py
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
├── prompt_alignment.csv
├── contact_quality.csv
└── sonic_policy_mujoco_tracking_210_fixed.csv
```

Update this file when adding a new durable loop artifact.
