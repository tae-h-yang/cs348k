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
- [ ] Render full videos for the visual audit manifest.
- [ ] Improve native SONIC/reference conversion or replace with another trusted
  G1 tracker.
- [ ] Run 4-8 hour long-run protocol and review the resulting videos/tables.

## Candidate Commands

```bash
python scripts/build_humanoid_robotics_prompt_suite.py
python scripts/evaluate_motionspec.py
python scripts/build_candidate_evidence_table.py
python scripts/plot_combined_selector.py
python scripts/select_visual_audit_clips.py
python scripts/render_visual_audit_contact_sheet.py
bash scripts/longrun_motion_curation.sh
python scripts/evaluate_prompt_alignment.py
python scripts/evaluate_contact_quality.py
python scripts/analyze_sonic_policy_results.py
pytest -q
```

## Acceptance Bar For Next Report

- No claims of arbitrary text generation unless the generator actually supports
  it.
- No claims of physical execution unless controller evidence supports it.
- Every improvement claim must have a paired baseline and a video or frame audit
  path.
