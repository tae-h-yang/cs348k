# Hybrid Acceptance Queue, 2026-05-23

## Question

Can the learned acceptance score become more defensible by abstaining on
unsupported modes before native SONIC rollout?

## Selector

`scripts/select_hybrid_acceptance_candidates.py` applies:

1. hard rejection of crawling/low-posture identities for the current SONIC
   upright/idle acceptance claim,
2. `upright_reference_gate_pass == "__YES__"`,
3. `low_root_frames_pct <= 0`,
4. `ensemble_accept_prob >= 0.5`,
5. learned-score ranking within each remaining identity.

Command:

```bash
python scripts/select_hybrid_acceptance_candidates.py \
  --out_dir results/prospective_native_selection/20260523_hybrid_acceptance_queue \
  --export_references
```

Output:

- selected identities: 88
- rejected identities: 16
- selected categories: 8 idle, 80 upright
- rejected categories: 16 crawling

## Native Label Closure

79/88 selected hybrid references had already been evaluated by the learned
prospective rollout. The remaining 9 were evaluated in:

`results/prospective_native_selection/20260523_hybrid_acceptance_queue/native_release_missing9/`

Command:

```bash
MUJOCO_GL=egl python scripts/run_sonic_native_release_batch.py \
  --reference_root results/prospective_native_selection/20260523_hybrid_acceptance_queue/sonic_references \
  --strategy all --limit 9 \
  --motions hybrid_acceptance_idle_seed7_cand5 hybrid_acceptance_idle_seed8_cand3 \
    hybrid_acceptance_idle_seed9_cand7 hybrid_acceptance_idle_seed10_cand4 \
    hybrid_acceptance_idle_seed11_cand7 hybrid_acceptance_idle_seed12_cand4 \
    hybrid_acceptance_idle_seed13_cand3 hybrid_acceptance_idle_seed14_cand3 \
    hybrid_acceptance_walk_stealth_seed7_cand5 \
  --out_dir results/prospective_native_selection/20260523_hybrid_acceptance_queue/native_release_missing9 \
  --max_hours 1 --width 640 --height 360 \
  --release_settle 1.0 --startup_timeout 90 --resume
```

All 9 missing rollouts survived without falling. 7/9 are strict passes; two
idle clips fail strict only because root XY drift exceeds 1.5m.

| split | strict |
|---|---:|
| all hybrid accepted identities | 74/88 |
| upright accepted identities | 68/80 |
| idle accepted identities | 6/8 |
| rejected crawling identities | 0/16 evaluated earlier |

## Visual Audit

The 9 newly evaluated hybrid videos were rerendered with camera tracking and
contact markers, then audited from MP4 pixels:

```bash
MUJOCO_GL=egl python scripts/render_existing_sonic_diagnostics.py \
  --batch_dir results/prospective_native_selection/20260523_hybrid_acceptance_queue/native_release_missing9 \
  --all \
  --out_dir results/prospective_native_selection/20260523_hybrid_acceptance_queue/native_release_missing9/diagnostic_contact_videos_all \
  --width 960 --height 540 --fps 30 --align_mode initial

python scripts/visual_audit_sonic_videos.py \
  --batch_dir results/prospective_native_selection/20260523_hybrid_acceptance_queue/native_release_missing9 \
  --video_dir results/prospective_native_selection/20260523_hybrid_acceptance_queue/native_release_missing9/diagnostic_contact_videos_all \
  --glob '*_diagnostic_contacts.mp4' \
  --out_dir results/prospective_native_selection/20260523_hybrid_acceptance_queue/native_release_missing9/visual_frame_audit_tracked \
  --sheet_limit 20
```

Visual audit result:

- visual pass: 9/9
- visual warn: 0/9
- visual fail: 0/9
- strict-pass videos with visual fail flag: 0/7

## Interpretation

The hybrid experiment supports abstention, but not a stronger headline win.
Rejecting crawling avoids the catastrophic 0/16 failure class, yet learned-score
ranking alone selected two idle references that survived and looked visually
acceptable but drifted too far in root XY to pass the strict metric. The current
best claim is therefore:

> Learned acceptance is useful for abstention and candidate triage; the strongest
> full-coverage selector remains the hand-coded gated pre-controller baseline,
> while hybrid learned gating is the next method to refine.

The next fix should add an explicit root-drift or idle-position sanity term to
the hybrid ranking before rerunning a full native batch.
