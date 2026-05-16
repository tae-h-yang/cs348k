# Run Journal

## 2026-05-16

- User rejected the old framing as too toy-like and asked for a broader,
  research-level autonomous loop around high-quality humanoid robot motion data.
- Subagent repo audit confirmed current MotionBricks generation is real but
  exposed as discrete G1 modes, not arbitrary language prompts.
- Subagent method audit recommended controller-in-the-loop curation as the
  strongest next claim, with a MoVer-like MotionSpec verifier and rule-based
  physics/contact gates.
- Created this autonomous-loop documentation structure so future runs have a
  durable place for decisions, blockers, evidence, and commands.
- Added a generator for a 100 distinct-prompt humanoid robotics benchmark.
- Generated `configs/humanoid_robotics_100_prompts.csv` and verified it has 100
  rows with 100 unique prompt texts. Coverage: 16 locomotion, 12 terrain, 18
  loco-manipulation, 12 manipulation stance, 12 balance, 10 communication, 10
  low posture, and 10 workspace tasks.
- Added `scripts/evaluate_motionspec.py`, a first MoVer-like predicate checker
  over the existing executable 105-row MotionBricks suite.
- Ran MotionSpec on the existing 210 K=1/K=8 rows. Selector comparison:
  K=1 baseline score 0.686, K=8 score 0.736, MotionSpec-over-K1/K8 score 0.757.
  MotionSpec selection also raises prompt proxy alignment from 0.583/0.568 to
  0.620 and approximate SONIC survival from 2.005/2.054 s to 2.117 s.
- Top failures are controller-related: 196/210 approximate SONIC rows fall and
  185/210 fail the 3 s survival predicate. This confirms that controller
  fidelity and controller-in-the-loop selection remain the main research risk.
- Added `scripts/plot_motionspec_dashboard.py` and generated
  `results/motionspec_selector_dashboard.png` plus
  `results/motionspec_failure_counts.png` for quick visual review.
- Ran `pytest -q`: 7 passed.
- User correctly objected that this was not enough work or evidence. Added
  `phd_student_role.md`, `reviewer_loop.md`, and `reviewer_reports.md` to force
  stricter continuation criteria before any future "presentable" claim.
- Added `scripts/build_candidate_evidence_table.py` and
  `scripts/plot_combined_selector.py`. The combined selector improves over K=1
  on combined score (0.577 -> 0.653), semantic score (0.650 -> 0.697), risk
  (35.32 -> 14.17), and approximate SONIC survival (2.005 s -> 2.148 s), but
  SONIC oracle still has the longest survival (2.299 s) while accepting worse
  risk. This supports controller-in-the-loop selection as the next real method.
- Added `scripts/select_visual_audit_clips.py` and
  `scripts/render_visual_audit_contact_sheet.py`. Generated a 12-clip visual
  audit sheet showing that low/crawling clips visibly collapse or lie on the
  ground, validating the need for visual review and stricter contact/controller
  gates.
- Added `docs/autonomous_loop/long_run_protocol.md` and
  `scripts/longrun_motion_curation.sh` to support 4-8 hour autonomous runs with
  resumable candidate generation, heavier critic training, regenerated visual
  audit artifacts, and a run summary.
- Added `scripts/render_visual_audit_videos.py` so selected audit cases can be
  watched as MP4s, not only inspected as still-frame contact sheets.
- Ran the 2026-05-16 long-run protocol for more than 6 hours. It expanded the
  candidate audit to 728 candidates over 91 mode-seed identities, rendered 12
  visual-audit MP4s, and trained two width-512 neural critic seeds for 5000
  epochs each. Results are documented in
  `docs/autonomous_loop/long_run_results_2026-05-16.md`.
