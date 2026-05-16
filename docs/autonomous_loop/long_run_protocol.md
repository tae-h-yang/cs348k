# Long-Run Protocol

This protocol is for 4-8 hour autonomous runs. It exists because quick numeric
summaries are not enough for this project.

## Goal

Produce video-grounded evidence for whether candidate curation genuinely
improves humanoid robot motion references.

## Runtime Budget

- Minimum target: 4 hours of work.
- Maximum target: 8 hours before pausing for human inspection.
- Save intermediate artifacts frequently.
- Every long run must be resumable.

## Priority Order

1. **Generate more candidates.** Expand from paired K=1/K=8 selected clips to
   saved K candidates per mode/seed, so we can compare selectors honestly.
2. **Score with multiple evaluators.** MotionSpec, contact, inverse dynamics,
   and approximate controller metrics should be joined per candidate.
3. **Render evidence.** Produce videos/contact sheets for best, worst, and
   disagreement cases. Do not trust aggregate numbers without looking.
4. **Train only if labels are meaningful.** A neural critic is useful only if it
   predicts better selection under held-out clips or controller labels, not just
   heuristic risk.
5. **Review like a hostile committee.** Update reviewer reports after every
   major output.

## Default Long Run

The current best 4-8 hour job is:

1. Run candidate audit across all exposed MotionBricks modes, 7 seeds, K=8.
2. Train a larger clip critic on the expanded candidate table.
3. Rebuild candidate evidence tables and selector plots.
4. Regenerate the visual-audit manifest and contact sheet.
5. Render audit videos for the visual-audit manifest.
6. Write a run summary with exact failures.

## Commands

```bash
bash scripts/longrun_motion_curation.sh
```

Monitor:

```bash
tail -f results/longrun/latest/longrun.log
```

## VLM Policy

Use a real VLM only if a local model or API key is available. If not available,
do not fake VLM review. Use rendered contact sheets and human-review manifests
until a VLM can be added.

## Stop Conditions

Stop before 8 hours only if:

- the long run fails with a reproducible error and the error is documented,
- GPU/system resources are unavailable,
- all planned jobs complete and artifacts are generated,
- or the user interrupts.

## Required Outputs

- `results/longrun/latest/longrun.log`
- `results/longrun/latest/run_summary.md`
- updated candidate/evaluator CSVs or a documented failure
- visual artifacts: dashboard, contact sheet, and selected audit videos
- updated `docs/autonomous_loop/run_journal.md`
