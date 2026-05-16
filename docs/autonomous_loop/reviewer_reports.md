# Reviewer Reports

## Review 001 - 2026-05-16

### Paper-Level Score

Weak reject as a final paper. Useful as a project direction.

### Strengths

- The problem is real: kinematic generator output is not automatically robot
  motion data.
- The repo now separates distinct target prompts from seed-expanded executable
  prompts.
- The MotionSpec checker gives named predicate failures rather than opaque
  scores.
- The current results honestly show that controller failure is the main problem.

### Major Weaknesses

- The executable benchmark is still narrow.
- Controller evidence is approximate and mostly negative.
- No new generator training or policy training has happened in this loop.
- Visual evidence is not yet sufficient for an audience to understand risk.
- The proposed method currently selects between K=1 and K=8 only, not a broad
  candidate pool for 100 behaviors.

### Required Experiments

- Join all candidate evidence into one table. Done in
  `results/candidate_evidence_table.csv`.
- Add combined selectors and ablations. Initial K=1/K=8 selector comparison
  done in `results/combined_selector_comparison.csv`.
- Render a risk-audit panel for at least 8 clips: good, bad, and disagreement
  cases. Initial 12-clip contact sheet done in
  `results/visual_audit_contact_sheet.png`.
- Investigate arbitrary-prompt generation or alternative generators for the
  100-prompt suite.
- Improve or replace approximate SONIC validation.

### Verdict

Continue. Do not write a triumphant paper yet.

### Updated Critique

The new evidence helps reproducibility and failure visibility. It does not
change the core verdict: controller evidence remains too weak, and the broad
100-prompt benchmark is not executable yet.
