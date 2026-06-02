# RalphLoop

RalphLoop is the current autonomous long-run workflow for the Humanoid100
MotionBricks physical-curation project.

## Purpose

The goal is not to make the existing result sound stronger. The goal is to
produce harder evidence for or against this claim:

> Sampling, repair, and controller-aware verification can turn MotionBricks
> kinematic references into a higher-quality physically executable motion set.

## Current Command

```bash
python scripts/launch_ralphloop.py --hours 12 --k-after 32 --provider cuda
```

If CUDA ONNXRuntime is not available, rerun with:

```bash
python scripts/launch_ralphloop.py --hours 12 --k-after 32 --provider cpu
```

The launcher prints the detached supervisor PID and writes launcher output to
`results/ralphloop_launch.log`.

## Monitor

```bash
tail -f results/ralphloop/latest/ralphloop.log
cat results/ralphloop/latest/status.md
cat results/ralphloop/latest/ralphloop_summary.md
cat results/ralphloop_agent/status_latest.md
```

## Phases

1. Environment and tests.
2. Generate all 100 Humanoid100 proxy motions with larger best-of-K sampling.
3. Apply retiming/smoothing repair.
4. Recompute physical/contact/inverse-dynamics metrics.
5. Export all references to the approximate SONIC bridge.
6. Run approximate SONIC with corrected reference-pose initialization.
7. Select the controller-verified best candidate per prompt.
8. Save selected and K=1 rollout traces.
9. Render final, baseline, and before/after videos.
10. Create contact sheets and reviewer summary.

## Outputs

Latest symlink:

```text
results/ralphloop/latest/
```

Important files inside a completed run:

```text
status.md
ralphloop.log
commands.sh
ralphloop_summary.md
humanoid100_final_eval_k32/final_selector_initref/selector_summary.csv
humanoid100_final_eval_k32/before_after_overlay_videos/*.mp4
humanoid100_final_eval_k32/before_after_overlay_contact_sheet.jpg
```

## Claim Boundary

RalphLoop can create stronger evidence, but it cannot honestly claim solved
arbitrary text-to-physical motion unless the controller metrics and videos
actually pass. Unsupported prompt proxies remain unsupported, even if their
nearest generated motions become physically cleaner.

## CUDA ONNXRuntime Note

PyTorch CUDA availability is not sufficient for SONIC. The approximate SONIC
bridge uses ONNXRuntime, so `CUDAExecutionProvider` must actually load the
encoder and decoder sessions. The runner exports Python-installed NVIDIA CUDA
12 library paths via `scripts/python_nvidia_lib_paths.py`.

Verified smoke test on 2026-05-29:

```text
model_encoder.onnx ['CUDAExecutionProvider', 'CPUExecutionProvider']
model_decoder.onnx ['CUDAExecutionProvider', 'CPUExecutionProvider']
```

## Meta-Agent

`scripts/ralphloop_agent.py` is the scripted self-correction layer. It monitors
the active RalphLoop run, writes reviewer verdicts, and if the strict acceptance
bar is not met before the time budget expires, launches a stronger corrective
run such as K=64. It is not an LLM process; it is a reproducible experiment
supervisor.
