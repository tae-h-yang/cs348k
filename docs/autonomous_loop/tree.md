# Autonomous Loop Tree

```text
docs/
├── native_acceptance_broad13_2026-05-23.md
├── learned_acceptance_prospective_2026-05-23.md
├── hybrid_acceptance_queue_2026-05-23.md
├── research_positioning_2026-05-23.md
├── native_acceptance_model_2026-05-22.md
├── prospective_broad13_2026-05-22.md
├── prospective_lowroot_gate_2026-05-16.md
├── prospective_native_selection_2026-05-16.md
└── autonomous_loop/
    ├── README.md
    ├── benchmark_spec.md
    ├── blockers.md
    ├── candidate_methods.md
    ├── dual_track_kimodo_motionbricks_2026-05-30.md
    ├── evaluation_protocol.md
    ├── evidence_log.md
    ├── experiment_queue.md
    ├── humanoid_robotics_100_prompts.md
    ├── long_run_protocol.md
    ├── method_review_repair_2026-05-28.md
    ├── phd_student_role.md
    ├── problem_definition.md
    ├── ralphloop.md
    ├── research_notes.md
    ├── reviewer_loop.md
    ├── reviewer_reports.md
    ├── run_journal.md
    ├── sports_acrobatics_stress_prompts.md
    └── state_checkpoint.md

configs/
├── prompt_suite_105.csv
├── humanoid_robotics_100_prompts.csv
└── sports_acrobatics_stress_prompts.csv

scripts/
├── build_prompt_suite.py
├── build_humanoid_robotics_prompt_suite.py
├── build_sports_acrobatics_prompt_suite.py
├── evaluate_humanoid_100_prompts.py
├── evaluate_prompt_alignment.py
├── run_humanoid100_motionbricks_experiment.py
├── repair_humanoid100_references.py
├── evaluate_humanoid100_final.py
├── export_humanoid100_sonic_references.py
├── plot_humanoid100_sonic_supported.py
├── evaluate_contact_quality.py
├── evaluate_motionspec.py
├── plot_motionspec_dashboard.py
├── build_candidate_evidence_table.py
├── run_prospective_native_selection.py
├── analyze_prospective_native_selection.py
├── score_native_acceptance_candidates.py
├── export_learned_acceptance_selection.py
├── analyze_learned_acceptance_rollout.py
├── select_hybrid_acceptance_candidates.py
├── analyze_dual_track_motion_generation.py
├── dual_track_kimodo_motionbricks_loop.sh
├── run_kimodo_humanoid100_experiment.py
├── evaluate_kimodo_humanoid100.py
├── audit_sonic_reference_export.py
├── analyze_sonic_reference_sanity.py
├── render_prospective_comparison_sheets.py
├── render_existing_sonic_diagnostics.py
├── visual_audit_sonic_videos.py
├── train_native_sonic_acceptance.py
├── plot_combined_selector.py
├── select_visual_audit_clips.py
├── render_visual_audit_contact_sheet.py
├── render_visual_audit_videos.py
├── render_selected_overlay_videos.py
├── stitch_humanoid100_before_after_videos.py
├── make_humanoid100_video_contact_sheet.py
├── launch_ralphloop.py
├── ralphloop.sh
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
├── humanoid100_eval/
│   ├── README.md
│   ├── humanoid100_eval.csv
│   └── videos/*.mp4
├── humanoid100_full_proxy_eval/
│   ├── README.md
│   ├── humanoid100_eval.csv
│   └── videos/*.mp4
├── humanoid100_motionbricks_experiment/
│   ├── README.md
│   ├── humanoid100_motionbricks_results.csv
│   ├── category_summary.csv
│   └── videos/*.mp4
├── humanoid100_repaired_retimed/
│   ├── README.md
│   ├── repair_summary.csv
│   └── videos/*.mp4
├── humanoid100_final_eval/
│   ├── README.md
│   ├── final_metrics.csv
│   ├── summary.csv
│   ├── method_summary_bars.png
│   ├── risk_by_category.png
│   ├── paired_risk_scatter.png
│   ├── sonic_supported_tracking.csv
│   ├── sonic_supported_summary.csv
│   ├── sonic_supported_summary.png
│   ├── sonic_all_tracking.csv
│   ├── sonic_all_summary.csv
│   ├── sonic_all_summary.png
│   ├── sonic_references_supported/
│   ├── sonic_references_all/
│   ├── sonic_supported_rollouts/*.npz
│   ├── sonic_supported_videos/*.mp4
│   ├── final_selector_initref/
│   │   ├── README.md
│   │   ├── joined_method_metrics.csv
│   │   ├── selected_methods.csv
│   │   ├── selector_summary.csv
│   │   └── final_selector_summary.png
│   ├── final_100_selected_rollouts/*.npz
│   ├── final_100_selected_overlay_videos/*.mp4
│   ├── final_100_selected_overlay_videos.csv
│   ├── final_100_selected_overlay_contact_sheet.jpg
│   ├── k1_baseline_overlay_videos/*.mp4
│   ├── k1_baseline_overlay_videos.csv
│   ├── before_after_overlay_videos/*.mp4
│   ├── before_after_overlay_videos.csv
│   ├── before_after_overlay_contact_sheet.jpg
│   └── final_selector/
│       ├── README.md
│       ├── joined_method_metrics.csv
│       ├── selected_methods.csv
│       ├── selector_summary.csv
│       ├── representative_cases.csv
│       ├── final_selector_summary.png
│       ├── representative_contact_sheet.jpg
│       ├── representative_rollouts/*.npz
│       └── representative_videos/*.mp4
├── dual_track/latest/
│   ├── dual_track_status.md
│   ├── kimodo_status.json
│   ├── motionbricks_dual_track_summary.csv
│   ├── motionbricks_k_scaling.png
│   └── motionbricks_sonic_survival_scaling.png
├── kimodo_zero_text_smoke/
│   ├── zero_text_qpos.npy
│   └── zero_text_qpos.csv
├── kimodo_zero_text_smoke_eval/
│   ├── summary.csv
│   └── README.md
├── sonic_native_release_all210/20260516_123519/
├── prospective_native_selection/20260516_170132/
│   ├── prospective_native_analysis.md
│   ├── prospective_native_selector_summary.csv
│   ├── sonic_reference_export_audit.csv
│   ├── sonic_reference_sanity_summary.csv
│   ├── sonic_reference_sanity_worst.csv
│   ├── native_release/analysis_summary.md
│   ├── native_release/diagnostic_contact_videos/*.mp4
│   ├── native_release/diagnostic_contact_sheet_first40.jpg
│   └── comparison_sheets/*.jpg
├── prospective_native_selection/20260516_lowroot_gate/
│   ├── prospective_native_analysis.md
│   ├── prospective_native_selector_summary.csv
│   ├── sonic_reference_export_audit.csv
│   ├── sonic_reference_sanity_summary.csv
│   ├── sonic_reference_sanity_worst.csv
│   ├── native_release/analysis_summary.md
│   ├── native_release/diagnostic_contact_videos/*.mp4
│   ├── native_release/diagnostic_contact_sheet_first40.jpg
│   ├── native_release/strict_presentation_pass_videos/*.mp4
│   ├── native_release/fail_videos/*.mp4
│   └── comparison_sheets/*.jpg
├── prospective_native_selection/20260522_broad13/
│   ├── prospective_candidates.csv
│   ├── prospective_selected.csv
│   ├── prospective_native_analysis.md
│   ├── prospective_native_by_category.csv
│   ├── prospective_native_by_mode.csv
│   ├── sonic_reference_export_audit.csv
│   ├── sonic_references/*/*.csv
│   ├── comparison_sheets/*.jpg
│   ├── learned_acceptance_selector/
│   │   ├── candidate_scores.csv
│   │   ├── ensemble_selection_all_candidates.csv
│   │   ├── crossval_selection_evaluated_candidates.csv
│   │   └── learned_selector_audit.md
│   └── native_release/
│       ├── analysis_summary.md
│       ├── strict_presentation_pass_videos/*.mp4
│       ├── fail_videos/*.mp4
│       ├── diagnostic_contact_videos/*.mp4
│       ├── diagnostic_contact_videos_stress_modes/*.mp4
│       ├── diagnostic_contact_videos_all/*.mp4
│       ├── visual_frame_audit_tracked/
│       ├── diagnostic_contact_sheet_first40.jpg
│       └── diagnostic_contact_sheet_stress_modes_first48.jpg
├── prospective_native_selection/20260523_learned_acceptance_eval/
│   ├── prospective_selected.csv
│   ├── export_manifest.csv
│   ├── audit/
│   │   ├── learned_acceptance_rollout_audit.md
│   │   ├── learned_score_abstention.csv
│   │   └── known_label_hybrid_selection.csv
│   ├── sonic_references/*/*.csv
│   └── native_release/
│       ├── analysis_summary.md
│       ├── batch_summary.csv
│       ├── diagnostic_contact_videos_all/*.mp4
│       ├── visual_frame_audit_tracked/
│       └── visual_reviewed_presentation_videos/*.mp4
├── prospective_native_selection/20260523_hybrid_acceptance_queue/
│   ├── prospective_selected.csv
│   ├── rejected_identities.csv
│   ├── hybrid_selection_native_labels.csv
│   ├── sonic_references/*/*.csv
│   └── native_release_missing9/
│       ├── batch_summary.csv
│       ├── diagnostic_contact_videos_all/*.mp4
│       └── visual_frame_audit_tracked/
├── native_acceptance_model_20260522_long/
│   ├── native_acceptance_model.md
│   ├── scalar_baselines.csv
│   ├── crossval_predictions.csv
│   ├── train_log.csv
│   └── training_auc.png
├── native_acceptance_model_20260523_broad13_long/
│   ├── native_acceptance_model.md
│   ├── scalar_baselines.csv
│   ├── crossval_predictions.csv
│   ├── train_log.csv
│   ├── training_auc.png
│   └── fold_*_best.pt
└── current_validated/
    ├── README.md
    ├── prospective_native_analysis.md -> latest selector analysis
    ├── native_analysis_summary.md -> latest native SONIC analysis
    ├── comparison_sheets -> latest paired sheets
    ├── diagnostic_contact_videos -> latest diagnostic videos
    ├── diagnostic_contact_videos_stress_modes -> latest stress-mode diagnostics
    ├── diagnostic_contact_sheet_first40.jpg -> latest diagnostic sheet
    ├── diagnostic_contact_sheet_stress_modes_first48.jpg -> latest stress sheet
    ├── strict_presentation_pass_videos -> latest strict passes
    └── fail_videos -> latest failures
```

Update this file when adding a new durable loop artifact.
