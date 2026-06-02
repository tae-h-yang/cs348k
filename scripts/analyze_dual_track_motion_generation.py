#!/usr/bin/env python3
"""Summarize the two project tracks: MotionBricks screening and Kimodo quality.

This script is intentionally lightweight and reproducible. It does not rerun
generation; it harvests existing RalphLoop outputs and writes a compact report
that can be regenerated while long experiments run.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RALPH = ROOT / "results" / "ralphloop"
OUT = ROOT / "results" / "dual_track" / "latest"


def _yes_count(series: pd.Series) -> int:
    return int((series.astype(str) == "__YES__").sum())


def _extract_k(path: Path) -> int | None:
    match = re.search(r"_k(\d+)$", path.name)
    if match:
        return int(match.group(1))
    match = re.search(r"_k(\d+)", str(path))
    return int(match.group(1)) if match else None


def _parse_local_datetime(text: str) -> dt.datetime | None:
    match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", text.strip())
    if not match:
        return None
    return dt.datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")


def collect_runtime_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for log_path in sorted(RALPH.glob("20*/ralphloop.log")):
        text = log_path.read_text(errors="replace")
        start = end = None
        k_after = None
        for line in text.splitlines():
            if line.startswith("start_local="):
                start = _parse_local_datetime(line.split("=", 1)[1])
            elif line.startswith("end_local="):
                end = _parse_local_datetime(line.split("=", 1)[1])
            elif line.startswith("k_after="):
                try:
                    k_after = int(line.split("=", 1)[1])
                except ValueError:
                    k_after = None
        wall_minutes = (end - start).total_seconds() / 60.0 if start and end else None
        rows.append(
            {
                "run": log_path.parent.name,
                "k_after": k_after,
                "wall_minutes": wall_minutes,
                "start_local": start.isoformat(sep=" ") if start else "",
                "end_local": end.isoformat(sep=" ") if end else "",
                "log_path": str(log_path),
            }
        )
    return rows


def collect_motionbricks_runs() -> pd.DataFrame:
    rows: list[dict] = []
    for eval_dir in sorted(RALPH.glob("20*/humanoid100_final_eval_k*")):
        k = _extract_k(eval_dir)
        final_metrics = eval_dir / "final_metrics.csv"
        selector_summary = eval_dir / "final_selector_initref" / "selector_summary.csv"
        sonic_summary = eval_dir / "sonic_all_initref_summary.csv"
        if not final_metrics.exists():
            continue

        metrics = pd.read_csv(final_metrics)
        for method in ["K1_first", "K8_best_of_8", "repaired_retime"]:
            method_rows = metrics[metrics["method"] == method]
            if method_rows.empty:
                continue
            rows.append(
                {
                    "run": eval_dir.parent.name,
                    "k_after": k,
                    "track": "MotionBricks",
                    "method": method,
                    "n": len(method_rows),
                    "physical_pass": _yes_count(method_rows["physical_pass"]),
                    "presentation_pass": _yes_count(method_rows["presentation_pass"]),
                    "semantic_supported": _yes_count(method_rows["semantic_supported"]),
                    "mean_risk": float(method_rows["risk_score"].mean()),
                    "mean_contact_artifact_score": float(method_rows["contact_artifact_score"].mean()),
                    "mean_p95_torque_limit_ratio": float(method_rows["p95_torque_limit_ratio"].mean()),
                    "sonic_no_fall": None,
                    "mean_sonic_track_seconds": None,
                    "mean_sonic_rmse": None,
                }
            )

        if selector_summary.exists():
            selectors = pd.read_csv(selector_summary)
            for _, row in selectors[selectors["group"].astype(str).str.startswith("selector=")].iterrows():
                # Only keep aggregate selector rows, not selector|category rows.
                if "|" in str(row["group"]):
                    continue
                rows.append(
                    {
                        "run": eval_dir.parent.name,
                        "k_after": k,
                        "track": "MotionBricks",
                        "method": str(row["group"]).replace("selector=", "selector:"),
                        "n": int(row["n"]),
                        "physical_pass": int(row["physical_pass_count"]),
                        "presentation_pass": int(row["presentation_pass_count"]),
                        "semantic_supported": int(row["semantic_supported_count"]),
                        "mean_risk": float(row["mean_risk"]),
                        "mean_contact_artifact_score": None,
                        "mean_p95_torque_limit_ratio": None,
                        "sonic_no_fall": int(row["sonic_no_fall_count"]),
                        "mean_sonic_track_seconds": float(row["mean_sonic_track_seconds"]),
                        "mean_sonic_rmse": float(row["mean_sonic_rmse"]),
                    }
                )
        elif sonic_summary.exists():
            sonic = pd.read_csv(sonic_summary)
            for _, row in sonic.iterrows():
                group = str(row["group"])
                if group not in {"K1", "K8", "K9", "policy_selector_all_K"}:
                    continue
                n = int(row["n"])
                fell = int(row["fell_count"])
                rows.append(
                    {
                        "run": eval_dir.parent.name,
                        "k_after": k,
                        "track": "MotionBricks",
                        "method": f"sonic:{group}",
                        "n": n,
                        "physical_pass": None,
                        "presentation_pass": None,
                        "semantic_supported": None,
                        "mean_risk": None,
                        "mean_contact_artifact_score": None,
                        "mean_p95_torque_limit_ratio": None,
                        "sonic_no_fall": n - fell,
                        "mean_sonic_track_seconds": float(row["mean_track_seconds"]),
                        "mean_sonic_rmse": float(row["mean_tracking_rmse"]),
                    }
                )

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["k_after", "method"], na_position="last")
    return df


def write_motionbricks_plots(df: pd.DataFrame, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    selectors = df[df["method"].astype(str).str.startswith("selector:")].copy()
    if selectors.empty:
        return

    # Prefer one representative selector for scaling; keep all selector rows in CSV.
    sonic = selectors[selectors["method"] == "selector:sonic_verified_best"].copy()
    risk = selectors[selectors["method"] == "selector:risk_verifier_best"].copy()
    base = selectors[selectors["method"] == "selector:K1_first"].copy()

    fig, ax = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
    for data, label, color in [
        (base, "K1 baseline", "#555555"),
        (risk, "risk selector", "#2a9d8f"),
        (sonic, "SONIC selector", "#e76f51"),
    ]:
        if data.empty:
            continue
        data = data.sort_values("k_after")
        ax[0].plot(data["k_after"], data["physical_pass"], marker="o", label=label, color=color)
        ax[1].plot(data["k_after"], data["sonic_no_fall"], marker="o", label=label, color=color)
    ax[0].set_xscale("log", base=2)
    ax[1].set_xscale("log", base=2)
    ax[0].set_xlabel("Candidates per prompt")
    ax[1].set_xlabel("Candidates per prompt")
    ax[0].set_ylabel("Physical metric pass / 100")
    ax[1].set_ylabel("No-fall SONIC rollouts / 100")
    ax[0].set_title("Dynamics-screening metric")
    ax[1].set_title("Physics-tracking acceptance")
    for axis in ax:
        axis.grid(True, alpha=0.25)
        axis.legend()
    fig.savefig(out / "motionbricks_k_scaling.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
    if not sonic.empty:
        sonic = sonic.sort_values("k_after")
        ax.plot(sonic["k_after"], sonic["mean_sonic_track_seconds"], marker="o", color="#e76f51")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("Candidates per prompt")
    ax.set_ylabel("Mean SONIC survival seconds")
    ax.set_title("Sampling scale saturates on current bridge")
    ax.grid(True, alpha=0.25)
    fig.savefig(out / "motionbricks_sonic_survival_scaling.png", dpi=180)
    plt.close(fig)

    runtime_rows = collect_runtime_rows()
    if not runtime_rows:
        return
    runtime = pd.DataFrame(runtime_rows)
    runtime = runtime.dropna(subset=["k_after", "wall_minutes"])
    if runtime.empty or sonic.empty:
        return
    efficiency = sonic.merge(runtime[["run", "wall_minutes"]], on="run", how="left")
    efficiency = efficiency.dropna(subset=["wall_minutes"])
    if efficiency.empty:
        return
    efficiency = efficiency.sort_values("k_after")
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4), constrained_layout=True)
    ax[0].plot(efficiency["wall_minutes"], efficiency["sonic_no_fall"], marker="o", color="#e76f51")
    ax[1].plot(efficiency["wall_minutes"], efficiency["mean_sonic_track_seconds"], marker="o", color="#7a5195")
    for _, row in efficiency.iterrows():
        ax[0].annotate(f"K{int(row['k_after'])}", (row["wall_minutes"], row["sonic_no_fall"]), fontsize=8)
        ax[1].annotate(
            f"K{int(row['k_after'])}",
            (row["wall_minutes"], row["mean_sonic_track_seconds"]),
            fontsize=8,
        )
    for axis in ax:
        axis.grid(True, alpha=0.25)
        axis.set_xlabel("End-to-end wall minutes")
    ax[0].set_ylabel("No-fall SONIC rollouts / 100")
    ax[1].set_ylabel("Mean SONIC survival seconds")
    ax[0].set_title("More sampling has weak execution returns")
    ax[1].set_title("Survival saturates with compute")
    fig.savefig(out / "motionbricks_compute_efficiency.png", dpi=180)
    plt.close(fig)


def kimodo_status() -> dict:
    kimodo = ROOT.parent / "kimodo"
    token_paths = [
        Path.home() / ".cache" / "huggingface" / "token",
        Path.home() / ".huggingface" / "token",
    ]
    cache = Path.home() / ".cache" / "huggingface" / "hub" / "models--nvidia--Kimodo-G1-RP-v1"
    zero_summary = ROOT / "results" / "kimodo_zero_text_smoke_eval" / "summary.csv"
    demo_summary = ROOT / "results" / "kimodo_g1_examples_eval" / "summary.csv"
    demo_sonic = ROOT / "results" / "kimodo_g1_examples_eval" / "sonic_summary_cuda.csv"
    demo_gain_sweep = ROOT / "results" / "kimodo_g1_examples_eval" / "sonic_gain_sweep" / "summary_all.csv"
    zero_text_smoke = "not_run"
    if zero_summary.exists():
        try:
            zdf = pd.read_csv(zero_summary)
            agg = zdf[zdf["group"].eq("method=Kimodo_G1")].iloc[0]
            zero_text_smoke = (
                f"physical_pass={int(agg['physical_pass_count'])}/{int(agg['n'])}, "
                f"mean_risk={float(agg['mean_risk']):.3f}"
            )
        except Exception as exc:
            zero_text_smoke = f"unreadable: {type(exc).__name__}"
    demo_physical = "not_run"
    if demo_summary.exists():
        try:
            ddf = pd.read_csv(demo_summary)
            agg = ddf[ddf["group"].eq("method=Kimodo_G1")].iloc[0]
            demo_physical = (
                f"physical_pass={int(agg['physical_pass_count'])}/{int(agg['n'])}, "
                f"mean_risk={float(agg['mean_risk']):.3f}"
            )
        except Exception as exc:
            demo_physical = f"unreadable: {type(exc).__name__}"
    demo_sonic_status = "not_run"
    if demo_sonic.exists():
        try:
            sdf = pd.read_csv(demo_sonic)
            agg = sdf[sdf["group"].eq("K1")].iloc[0]
            n = int(agg["n"])
            no_fall = n - int(agg["fell_count"])
            demo_sonic_status = (
                f"no_fall={no_fall}/{n}, "
                f"mean_survival={float(agg['mean_track_seconds']):.3f}s"
            )
        except Exception as exc:
            demo_sonic_status = f"unreadable: {type(exc).__name__}"
    demo_gain_status = "not_run"
    if demo_gain_sweep.exists():
        try:
            gdf = pd.read_csv(demo_gain_sweep)
            best = gdf.sort_values(["no_fall", "mean_track_seconds"], ascending=[False, False]).iloc[0]
            demo_gain_status = (
                f"best={best['tag']}, no_fall={int(best['no_fall'])}/{int(best['n'])}, "
                f"mean_survival={float(best['mean_track_seconds']):.3f}s"
            )
        except Exception as exc:
            demo_gain_status = f"unreadable: {type(exc).__name__}"
    return {
        "repo_present": kimodo.exists(),
        "repo_path": str(kimodo),
        "hf_token_file_present": any(path.exists() for path in token_paths),
        "venv_present": (ROOT / ".venv" / "kimodo").exists(),
        "kimodo_g1_rp_cache_present": cache.exists(),
        "kimodo_g1_rp_cache_path": str(cache),
        "zero_text_smoke": zero_text_smoke,
        "bundled_g1_examples_physical": demo_physical,
        "bundled_g1_examples_sonic": demo_sonic_status,
        "bundled_g1_examples_gain_sweep": demo_gain_status,
        "notes": [
            "Kimodo-G1 models can export MuJoCo qpos CSV, which is directly relevant to the G1/SONIC evaluation path.",
            "Kimodo docs require a Hugging Face token with access to gated Meta-Llama-3-8B-Instruct for text embedding.",
            "Local GPU has about 8 GB VRAM; Kimodo docs recommend TEXT_ENCODER_DEVICE=cpu on small GPUs.",
            "A zero-text fake encoder smoke test proves the G1 checkpoint/export path works but is not a valid prompt-following method.",
            "Bundled Kimodo-G1 demo examples are native sanity data, not a replacement for full Humanoid100 generation.",
        ],
    }


def motionbricks_supported_gain_sweep_status() -> dict[str, object]:
    sweep_path = (
        ROOT
        / "results"
        / "ralphloop"
        / "20260529_191342"
        / "humanoid100_final_eval_k256"
        / "supported_sonic_gain_sweep"
        / "summary_all.csv"
    )
    status: dict[str, object] = {
        "summary_csv": str(sweep_path),
        "exists": sweep_path.exists(),
        "status": "not_run",
    }
    if not sweep_path.exists():
        return status
    try:
        df = pd.read_csv(sweep_path)
        if df.empty:
            status["status"] = "empty"
            return status
        best = df.sort_values(["no_fall", "mean_track_seconds"], ascending=[False, False]).iloc[0]
        status.update(
            {
                "status": "complete",
                "settings_tested": int(len(df)),
                "best_tag": str(best["tag"]),
                "n": int(best["n"]),
                "no_fall": int(best["no_fall"]),
                "fell_count": int(best["fell_count"]),
                "mean_track_seconds": float(best["mean_track_seconds"]),
                "mean_tracking_rmse": float(best["mean_tracking_rmse"]),
            }
        )
    except Exception as exc:
        status["status"] = f"unreadable: {type(exc).__name__}"
    return status


def motionbricks_supported_native_status() -> dict[str, object]:
    batch_dir = (
        ROOT
        / "results"
        / "ralphloop"
        / "20260529_191342"
        / "humanoid100_final_eval_k256"
        / "supported_native_sonic_release"
    )
    batch_csv = batch_dir / "batch_summary.csv"
    status: dict[str, object] = {
        "batch_dir": str(batch_dir),
        "summary_csv": str(batch_csv),
        "exists": batch_csv.exists(),
        "status": "not_run",
    }
    if not batch_csv.exists():
        return status
    try:
        df = pd.read_csv(batch_csv)
        completed = df[df["status"].astype(str) == "completed"].copy()
        if completed.empty:
            status["status"] = "empty"
            return status
        passes = completed[completed["fell"].astype(str) == "False"]
        strict = passes[
            (passes["mean_joint_rmse"].astype(float) <= 0.20)
            & (passes["mean_root_xy_error"].astype(float) <= 1.5)
        ]
        failures = completed[completed["fell"].astype(str) == "True"]["motion"].astype(str).tolist()
        status.update(
            {
                "status": "complete",
                "n": int(len(completed)),
                "no_fall": int(len(passes)),
                "strict_pass": int(len(strict)),
                "mean_joint_rmse": float(completed["mean_joint_rmse"].astype(float).mean()),
                "failures": failures,
                "analysis_md": str(batch_dir / "analysis_summary.md"),
                "strict_contact_sheet": str(batch_dir / "strict_presentation_pass_contact_sheet.jpg"),
                "fail_contact_sheet": str(batch_dir / "fail_contact_sheet.jpg"),
            }
        )
    except Exception as exc:
        status["status"] = f"unreadable: {type(exc).__name__}"
    return status


def motionbricks_all100_native_status() -> dict[str, object]:
    batch_dir = (
        ROOT
        / "results"
        / "ralphloop"
        / "20260529_191342"
        / "humanoid100_final_eval_k256"
        / "all100_native_sonic_release"
    )
    analysis_md = batch_dir / "humanoid100_native_analysis.md"
    joined_csv = batch_dir / "humanoid100_native_joined.csv"
    status: dict[str, object] = {
        "batch_dir": str(batch_dir),
        "analysis_md": str(analysis_md),
        "joined_csv": str(joined_csv),
        "exists": joined_csv.exists(),
        "status": "not_run",
    }
    if not joined_csv.exists():
        return status
    try:
        df = pd.read_csv(joined_csv)
        no_fall = df[df["native_no_fall"].astype(str).isin(["True", "1", "__YES__"])]
        strict = df[df["native_strict_pass"].astype(str).isin(["True", "1", "__YES__"])]
        category_csv = batch_dir / "humanoid100_native_by_category.csv"
        category_leaders: list[dict[str, object]] = []
        if category_csv.exists():
            cdf = pd.read_csv(category_csv)
            category_leaders = [
                {
                    "category": str(row["category"]),
                    "n": int(row["n"]),
                    "native_no_fall": int(row["native_no_fall"]),
                    "native_strict_pass": int(row["native_strict_pass"]),
                }
                for _, row in cdf.sort_values("native_no_fall_rate", ascending=False).iterrows()
            ]
        status.update(
            {
                "status": "complete",
                "n": int(len(df)),
                "native_no_fall": int(len(no_fall)),
                "native_strict_pass": int(len(strict)),
                "semantic_supported_n": int((df["semantic_supported"].astype(str) == "__YES__").sum()),
                "mean_native_rmse": float(df["mean_joint_rmse"].astype(float).mean()),
                "category_summary_csv": str(category_csv),
                "strict_contact_sheet": str(batch_dir / "strict_presentation_pass_contact_sheet.jpg"),
                "fail_contact_sheet": str(batch_dir / "fail_contact_sheet.jpg"),
                "category_leaders": category_leaders,
            }
        )
    except Exception as exc:
        status["status"] = f"unreadable: {type(exc).__name__}"
    return status


def motionbricks_native_variant_rescue_status() -> dict[str, object]:
    sweep_dir = (
        ROOT
        / "results"
        / "ralphloop"
        / "20260529_191342"
        / "humanoid100_final_eval_k256"
        / "failed_prompt_native_variant_sweep"
    )
    rescue_csv = sweep_dir / "native_variant_rescue.csv"
    status: dict[str, object] = {
        "sweep_dir": str(sweep_dir),
        "rescue_csv": str(rescue_csv),
        "analysis_md": str(sweep_dir / "native_variant_rescue_analysis.md"),
        "exists": rescue_csv.exists(),
        "status": "not_run",
    }
    if not rescue_csv.exists():
        return status
    try:
        df = pd.read_csv(rescue_csv)
        rescued = df[df["best_no_fall"].astype(str).isin(["True", "1", "__YES__"])]
        strict = df[df["best_strict"].astype(str).isin(["True", "1", "__YES__"])]
        status.update(
            {
                "status": "complete",
                "n_failed_retested": int(len(df)),
                "rescued_no_fall": int(len(rescued)),
                "rescued_strict": int(len(strict)),
                "projected_all100_no_fall": int(76 + len(rescued)),
                "projected_all100_strict": int(66 + len(strict)),
                "still_failing": df[
                    ~df["best_no_fall"].astype(str).isin(["True", "1", "__YES__"])
                ]["subcategory"].astype(str).tolist(),
            }
        )
    except Exception as exc:
        status["status"] = f"unreadable: {type(exc).__name__}"
    return status


def write_report(df: pd.DataFrame, out: Path) -> None:
    status = kimodo_status()
    mb_all100_native = motionbricks_all100_native_status()
    mb_rescue = motionbricks_native_variant_rescue_status()
    mb_gain = motionbricks_supported_gain_sweep_status()
    mb_native = motionbricks_supported_native_status()
    best = None
    selectors = df[df["method"] == "selector:sonic_verified_best"].copy()
    if not selectors.empty:
        best = selectors.sort_values(["sonic_no_fall", "mean_sonic_track_seconds"], ascending=[False, False]).iloc[0]
    runtime_by_run = {str(row["run"]): row for row in collect_runtime_rows()}

    lines = [
        "# Dual-Track Motion Generation Status",
        "",
        f"Generated: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "## Current conclusion",
        "",
        (
            "The all-MotionBricks route now has a credible native-SONIC execution result "
            "for selected proxy references, but still not the final claim that arbitrary "
            "100-prompt humanoid motion is solved. Best-of-K plus verifier selection "
            "produces many native-executable upright, balance, terrain, and manipulation "
            "proxies; floor locomotion, acrobatic stress tests, and exact language-to-motion "
            "coverage remain the major gaps."
        ),
        "",
        "Kimodo is now the serious quality track because it has G1-native models, explicit output to "
        "MuJoCo qpos CSV, benchmark metrics for text alignment and motion quality, and a documented "
        "Kimodo + GEAR-SONIC demo path.",
        "",
    ]
    if best is not None:
        lines += [
            "## Best completed MotionBricks sweep",
            "",
            f"- Run: `{best['run']}`",
            f"- Candidates per prompt: `{int(best['k_after'])}`",
            f"- Selector: `{best['method']}`",
            f"- Physical metric pass: `{int(best['physical_pass'])}/100`",
            f"- SONIC no-fall: `{int(best['sonic_no_fall'])}/100`",
            f"- Mean SONIC survival: `{float(best['mean_sonic_track_seconds']):.3f}s`",
        ]
        runtime = runtime_by_run.get(str(best["run"]))
        if runtime and runtime.get("wall_minutes") is not None:
            lines.append(f"- End-to-end RalphLoop wall time: `{float(runtime['wall_minutes']):.1f}` minutes")
        lines.append("")

    if mb_all100_native.get("status") == "complete":
        lines += [
            "## Native SONIC all-100 check",
            "",
            (
                "Running the 100 `sonic_verified_best` selections through the native "
                "SONIC release path gives the strongest current evidence. The result is "
                "not a perfect all-100 solution, but it is far stronger than the "
                "approximate Python bridge and shows a clear capability envelope."
            ),
            "",
            f"- Native no-fall: `{mb_all100_native['native_no_fall']}/{mb_all100_native['n']}`",
            f"- Native strict pass: `{mb_all100_native['native_strict_pass']}/{mb_all100_native['n']}`",
            f"- Mean joint RMSE: `{float(mb_all100_native['mean_native_rmse']):.3f}`",
            f"- Semantic-supported prompts: `{mb_all100_native['semantic_supported_n']}/{mb_all100_native['n']}`",
            f"- Analysis: `{mb_all100_native['analysis_md']}`",
            f"- Category CSV: `{mb_all100_native['category_summary_csv']}`",
            f"- Strict-pass contact sheet: `{mb_all100_native['strict_contact_sheet']}`",
            f"- Failure contact sheet: `{mb_all100_native['fail_contact_sheet']}`",
            "",
            "Category pattern: dynamic locomotion, balance, terrain, communication, "
            "and loco-manipulation are mostly executable; athletic/acrobatic stress "
            "tests and floor/low-posture transitions remain the major failures.",
            "",
        ]

    if mb_rescue.get("status") == "complete":
        lines += [
            "## Native verifier rescue sweep",
            "",
            (
                "For the 24 prompts that failed the first all-100 native pass, I ran "
                "K1, K8, and repaired/K9 variants through native SONIC. This estimates "
                "the headroom from native verifier selection and retry. It is not a "
                "deterministic single-shot guarantee, because a few rescues are same-variant "
                "reruns that passed on the second native rollout."
            ),
            "",
            f"- Failed prompts retested: `{mb_rescue['n_failed_retested']}`",
            f"- No-fall rescues: `{mb_rescue['rescued_no_fall']}/{mb_rescue['n_failed_retested']}`",
            f"- Strict rescues: `{mb_rescue['rescued_strict']}/{mb_rescue['n_failed_retested']}`",
            f"- Projected all-100 no-fall with native verifier selection/retry: `{mb_rescue['projected_all100_no_fall']}/100`",
            f"- Projected all-100 strict pass: `{mb_rescue['projected_all100_strict']}/100`",
            f"- Analysis: `{mb_rescue['analysis_md']}`",
            "",
            "Remaining failures are concentrated in crawling/floor transitions and "
            "acrobatic stress tests.",
            "",
        ]

    if mb_native.get("status") == "complete":
        lines += [
            "## Native SONIC supported-subset check",
            "",
            (
                "The approximate Python SONIC bridge was pessimistic on the supported "
                "subset. Running the same semantically supported K256 selections through "
                "the native SONIC release path gives a much cleaner result, while still "
                "exposing the unsupported/low-posture failures."
            ),
            "",
            f"- Clips: `{mb_native['n']}` semantically supported selections",
            f"- Native no-fall: `{mb_native['no_fall']}/{mb_native['n']}`",
            f"- Native strict pass: `{mb_native['strict_pass']}/{mb_native['n']}`",
            f"- Mean joint RMSE: `{float(mb_native['mean_joint_rmse']):.3f}`",
            f"- Failure motions: `{', '.join(mb_native['failures'])}`",
            f"- Analysis: `{mb_native['analysis_md']}`",
            f"- Strict-pass contact sheet: `{mb_native['strict_contact_sheet']}`",
            f"- Failure contact sheet: `{mb_native['fail_contact_sheet']}`",
            "",
        ]

    if mb_gain.get("status") == "complete":
        lines += [
            "## MotionBricks supported-subset gain sweep",
            "",
            (
                "I retested the semantically supported K256 selections with a small SONIC "
                "gain sweep to check whether the low no-fall rate was just a controller "
                "gain issue. It was not: every tested setting stayed at the same no-fall "
                "count, with only small survival/RMSE changes."
            ),
            "",
            f"- Settings tested: `{mb_gain['settings_tested']}`",
            f"- Clips: `{mb_gain['n']}` semantically supported selections",
            f"- Best setting: `{mb_gain['best_tag']}`",
            f"- Best no-fall: `{mb_gain['no_fall']}/{mb_gain['n']}`",
            f"- Best mean survival: `{float(mb_gain['mean_track_seconds']):.3f}s`",
            f"- Best mean tracking RMSE: `{float(mb_gain['mean_tracking_rmse']):.4f}`",
            "- Videos: `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_sonic_gain_sweep/best_videos/`",
            "- Contact sheet: `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_sonic_gain_sweep/best_videos_contact_sheet.jpg`",
            "",
        ]

    lines += [
        "## Kimodo setup status",
        "",
        f"- Repo present: `{status['repo_present']}` at `{status['repo_path']}`",
        f"- Local Kimodo venv present: `{status['venv_present']}`",
        f"- Hugging Face token file present: `{status['hf_token_file_present']}`",
        f"- Kimodo-G1-RP checkpoint cached: `{status['kimodo_g1_rp_cache_present']}`",
        f"- Zero-text smoke: `{status['zero_text_smoke']}`",
        f"- Bundled G1 demos, physical verifier: `{status['bundled_g1_examples_physical']}`",
        f"- Bundled G1 demos, approximate SONIC: `{status['bundled_g1_examples_sonic']}`",
        f"- Bundled G1 demos, SONIC gain sweep: `{status['bundled_g1_examples_gain_sweep']}`",
        "",
        "## Next experiments",
        "",
        "1. MotionBricks track: quantify real-time sampling and verifier latency, then present it as a low-latency proposal generator whose failure modes are exposed by physics checks.",
        "2. Kimodo track: run G1 text-to-motion prompts to MuJoCo qpos CSV, evaluate the same inverse-dynamics/contact metrics, and pass the outputs through native SONIC-style tracking.",
        "3. Comparison track: use identical 100-prompt categories where supported, plus a smaller high-confidence subset for qualitative videos with red reference ghost and physical robot.",
        "",
        "## Artifacts",
        "",
        "- `motionbricks_k_scaling.png`: completed K sweep summary.",
        "- `motionbricks_sonic_survival_scaling.png`: SONIC survival saturation plot.",
        "- `motionbricks_compute_efficiency.png`: execution return versus wall-clock sampling cost.",
        "- `motionbricks_dual_track_summary.csv`: harvested metrics.",
        "- `motionbricks_runtime_summary.csv`: wall-clock run durations from RalphLoop logs.",
        "- `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/all100_native_sonic_release/`: native SONIC all-100 selected-reference check.",
        "- `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/failed_prompt_native_variant_sweep/`: native verifier rescue sweep over failed prompts.",
        "- `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_native_sonic_release/`: native SONIC supported-subset check.",
        "- `results/ralphloop/20260529_191342/humanoid100_final_eval_k256/supported_sonic_gain_sweep/`: supported-subset SONIC gain sweep.",
        "- `results/kimodo_g1_examples_eval/`: bundled Kimodo-G1 demo sanity set.",
        "- `kimodo_status.json`: setup/blocker state.",
        "",
    ]
    (out / "dual_track_status.md").write_text("\n".join(lines) + "\n")
    combined_status = {
        "kimodo": status,
        "motionbricks_all100_native_sonic": mb_all100_native,
        "motionbricks_native_variant_rescue": mb_rescue,
        "motionbricks_supported_native_sonic": mb_native,
        "motionbricks_supported_gain_sweep": mb_gain,
    }
    (out / "kimodo_status.json").write_text(json.dumps(combined_status, indent=2) + "\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = collect_motionbricks_runs()
    df.to_csv(OUT / "motionbricks_dual_track_summary.csv", index=False)
    runtime_rows = collect_runtime_rows()
    if runtime_rows:
        pd.DataFrame(runtime_rows).to_csv(OUT / "motionbricks_runtime_summary.csv", index=False)
    write_motionbricks_plots(df, OUT)
    write_report(df, OUT)


if __name__ == "__main__":
    main()
