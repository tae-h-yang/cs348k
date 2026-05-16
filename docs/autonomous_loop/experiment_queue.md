# Experiment Queue

## Active

- [x] Create durable autonomous-loop docs.
- [x] Define 100 distinct humanoid robotics prompts.
- [x] Implement MotionSpec predicate checker.
- [x] Run MotionSpec on currently available K=1/K=8 clips.
- [ ] Combine MotionSpec, contact, inverse dynamics, and SONIC metrics into one
  candidate table.
- [ ] Compare selectors: K=1, inverse-dynamics, contact-gated, MotionSpec+ID,
  SONIC oracle/selector where available.
- [ ] Render a small visual audit set with non-overlapping labels and risk
  overlays.

## Candidate Commands

```bash
python scripts/build_humanoid_robotics_prompt_suite.py
python scripts/evaluate_motionspec.py
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
