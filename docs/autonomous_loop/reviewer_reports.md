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

## Review 002 - 2026-05-16 Long Run

### Paper-Level Score

Weak reject as a final paper, but notably stronger as an honest systems project.

### Evidence Reviewed

- 728-candidate audit over all exposed MotionBricks modes.
- 12 rendered visual-audit MP4s.
- Width-512 neural critic sweep: seeds 101 and 202, 5000 epochs each.
- Combined selector tables and dashboards.

### Positive Findings

- Best-of-K candidate pools contain visibly and dynamically better options for
  several locomotion/style motions.
- The visual-audit videos make the failure modes inspectable instead of hidden
  in tables.
- Crawling/low-posture failures are now clearly documented rather than
  overclaimed.

### Negative Findings

- Learned heuristic-risk critics did not reach the rho >= 0.85 target.
- Seed variance is large: seed 101 reached 0.797, seed 202 only 0.759.
- Approximate SONIC survival remains short.
- The 100-prompt benchmark remains a target spec, not an executable generator
  result.

### Required Next Work

- Use controller labels directly for selection or training.
- Fix MotionBricks-to-SONIC reference export toward full-body official format.
- Add human/VLM visual review over the generated audit videos.
- Separate claims by category: locomotion/style candidate curation is plausible;
  crawling/low-posture is currently a failure case.

## Review 003 - 2026-05-16 Native SONIC Release Check

### Paper-Level Score

Borderline as a scoped systems/evaluation project if the claim is narrowed to
controller-in-the-loop curation for upright motions.

### Evidence Reviewed

- Native C++ SONIC deploy binary.
- Official MuJoCo simulator qpos logs, not `g1_debug` fixed-root visualization.
- Elastic-band release before reference playback.
- Official references, representative MotionBricks references, and a curated
  MotionBricks batch with crawling negative controls.

### Positive Findings

- SONIC setup is not fundamentally broken: official references execute through
  the native stack, and `walking_quip_360_R_002__A428` survives the full run
  after release.
- MotionBricks-to-SONIC export is usable for upright references: 11/12 curated
  upright candidates survived full clip with low joint RMSE.
- Crawling failures are now confirmed by native controller evidence rather than
  only heuristic inverse dynamics.

### Negative Findings

- The simple root-height fall threshold is not reliable for intentional squat
  or low-posture references; video inspection remains required.
- The result is category-limited. It does not show universal MotionBricks
  tracking, arbitrary prompt generation, or policy fine-tuning.
- One upright candidate failed quickly, so the selector still needs a native
  controller acceptance gate.

### Required Next Work

- Present only the curated pass set as positive evidence.
- Use crawling and the failed upright clip as negative controls.
- Expand native-release evaluation to a larger selected pool if time permits.
- Add visual-review labels to avoid overclaiming from scalar metrics.
