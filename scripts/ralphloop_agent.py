"""Meta-supervisor for RalphLoop experiment cycles.

This is not an LLM process. It is a durable scripted research loop: monitor the
current RalphLoop run, review objective metrics, and launch the next run while
the wall-clock budget remains if the result is not good enough.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import signal
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_ROOT = ROOT / "results" / "ralphloop_agent"
RALPH_ROOT = ROOT / "results" / "ralphloop"


@dataclass
class Verdict:
    run_dir: Path
    selector: str
    physical_pass: int
    sonic_no_fall: int
    mean_seconds: float
    mean_rmse: float
    passed: bool
    reason: str


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def active_ralphloop_pids() -> list[int]:
    pattern = (
        r"scripts/ralphloop\.sh|scripts/resume_ralphloop_latest\.sh|"
        r"run_humanoid100_motionbricks_experiment\.py|repair_humanoid100_references\.py|"
        r"evaluate_humanoid100_final\.py|evaluate_sonic_policy_mujoco\.py|"
        r"render_selected_overlay_videos\.py"
    )
    out = subprocess.run(["pgrep", "-f", pattern], text=True, capture_output=True)
    pids = []
    for line in out.stdout.splitlines():
        try:
            pid = int(line.strip())
        except ValueError:
            continue
        if pid != os.getpid():
            pids.append(pid)
    return pids


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def latest_ralph_run() -> Path | None:
    latest = RALPH_ROOT / "latest"
    if latest.exists():
        return latest.resolve()
    runs = sorted([p for p in RALPH_ROOT.glob("20*") if p.is_dir()])
    return runs[-1] if runs else None


def read_selector_summary(run_dir: Path) -> Verdict | None:
    matches = sorted(run_dir.glob("humanoid100_final_eval_k*/final_selector_initref/selector_summary.csv"))
    if not matches:
        return None
    path = matches[-1]
    rows = list(csv.DictReader(path.open()))
    by = {row["group"]: row for row in rows}
    preferred = by.get("selector=sonic_verified_best") or by.get("selector=risk_verifier_best")
    if not preferred:
        return None
    physical = int(float(preferred["physical_pass_count"]))
    no_fall = int(float(preferred["sonic_no_fall_count"]))
    seconds = float(preferred["mean_sonic_track_seconds"])
    rmse = float(preferred["mean_sonic_rmse"])
    passed = physical >= 95 and no_fall >= 80 and seconds >= 4.5 and rmse <= 0.18
    if passed:
        reason = "passes strict all-100 acceptance bar"
    else:
        reason = (
            "does not pass strict all-100 bar "
            f"(physical={physical}/100, no_fall={no_fall}/100, seconds={seconds:.3f}, rmse={rmse:.3f})"
        )
    return Verdict(
        run_dir=run_dir,
        selector=preferred["group"].split("=", 1)[1],
        physical_pass=physical,
        sonic_no_fall=no_fall,
        mean_seconds=seconds,
        mean_rmse=rmse,
        passed=passed,
        reason=reason,
    )


def run_k(run_dir: Path | None) -> int | None:
    if not run_dir:
        return None
    status = run_dir / "status.md"
    if status.exists():
        text = status.read_text(errors="ignore")
        match = re.search(r"- k_after: (\d+)", text)
        if match:
            return int(match.group(1))
    matches = list(run_dir.glob("humanoid100_final_eval_k*"))
    if matches:
        match = re.search(r"_k(\d+)$", matches[-1].name)
        if match:
            return int(match.group(1))
    return None


def write_status(agent_dir: Path, message: str, deadline: float, active: list[int]) -> None:
    remaining = max(0, int(deadline - time.time()))
    text = "\n".join(
        [
            "# RalphLoop Agent Status",
            "",
            f"- updated: {now()}",
            f"- message: {message}",
            f"- remaining_seconds: {remaining}",
            f"- active_ralphloop_pids: {active}",
            f"- latest_ralph_run: `{latest_ralph_run()}`",
            "",
            "This meta-supervisor is scripted. It monitors runs and launches the",
            "next experiment when objective metrics fail the acceptance bar.",
            "",
        ]
    )
    (agent_dir / "status.md").write_text(text)
    AGENT_ROOT.mkdir(parents=True, exist_ok=True)
    (AGENT_ROOT / "status_latest.md").write_text(text)


def write_review(agent_dir: Path, verdict: Verdict) -> None:
    review = "\n".join(
        [
            "# RalphLoop Reviewer Verdict",
            "",
            f"- reviewed_at: {now()}",
            f"- run_dir: `{verdict.run_dir}`",
            f"- selector: `{verdict.selector}`",
            f"- physical_pass: {verdict.physical_pass}/100",
            f"- sonic_no_fall: {verdict.sonic_no_fall}/100",
            f"- mean_sonic_seconds: {verdict.mean_seconds:.3f}",
            f"- mean_rmse: {verdict.mean_rmse:.3f}",
            f"- passed: {verdict.passed}",
            f"- reason: {verdict.reason}",
            "",
            "Reviewer A/control: if no-fall is low, do not claim physically",
            "executable all-100 motion. Continue with stronger sampling/repair or",
            "narrow the claim to accepted-set curation.",
            "",
            "Reviewer B/semantics: forced proxy rows still cannot be counted as",
            "prompt-following successes.",
            "",
            "Reviewer C/reproducibility: keep this review beside the run logs and",
            "commands.",
            "",
        ]
    )
    path = agent_dir / f"review_{verdict.run_dir.name}.md"
    path.write_text(review)
    (AGENT_ROOT / "review_latest.md").write_text(review)


def launch_ralphloop(agent_dir: Path, hours: float, k_after: int, provider: str, render: bool) -> subprocess.Popen:
    cmd = [
        "bash",
        str(ROOT / "scripts" / "ralphloop.sh"),
        "--hours",
        str(max(1, int(hours))),
        "--k-after",
        str(k_after),
        "--provider",
        provider,
    ]
    if not render:
        cmd.append("--no-render")
    log = agent_dir / f"child_k{k_after}_{int(time.time())}.log"
    lib_paths = subprocess.check_output(["python", str(ROOT / "scripts" / "python_nvidia_lib_paths.py")], text=True).strip()
    env = {
        **os.environ,
        "MUJOCO_GL": os.environ.get("MUJOCO_GL", "egl"),
        "PYTHONPATH": f"{ROOT}:{os.environ.get('PYTHONPATH', '')}",
    }
    if lib_paths:
        env["LD_LIBRARY_PATH"] = f"{lib_paths}:{os.environ.get('LD_LIBRARY_PATH', '')}"
    with log.open("ab", buffering=0) as f:
        proc = subprocess.Popen(
            cmd,
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=f,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env=env,
        )
    (agent_dir / "launches.log").open("a").write(f"{now()} pid={proc.pid} k={k_after} render={render} log={log}\n")
    return proc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=float, default=12.0)
    parser.add_argument("--provider", default="cuda")
    parser.add_argument("--poll-seconds", type=int, default=120)
    parser.add_argument("--next-k", type=int, default=64)
    parser.add_argument("--max-k", type=int, default=512)
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    agent_dir = AGENT_ROOT / stamp
    agent_dir.mkdir(parents=True, exist_ok=True)
    latest = AGENT_ROOT / "latest"
    if latest.exists() or latest.is_symlink():
        latest.unlink()
    latest.symlink_to(agent_dir)

    deadline = time.time() + args.hours * 3600
    launched_ks: set[int] = set()
    write_status(agent_dir, "agent started", deadline, active_ralphloop_pids())

    while time.time() < deadline:
        active = active_ralphloop_pids()
        if active:
            write_status(agent_dir, "waiting for active RalphLoop run", deadline, active)
            time.sleep(args.poll_seconds)
            continue

        run = latest_ralph_run()
        verdict = read_selector_summary(run) if run else None
        if verdict:
            write_review(agent_dir, verdict)
            if verdict.passed:
                write_status(agent_dir, "acceptance bar passed; agent idle", deadline, [])
                time.sleep(args.poll_seconds)
                continue
            latest_k = run_k(run)
            candidate_k = args.next_k if latest_k is None else max(args.next_k, latest_k * 2)
            while candidate_k in launched_ks:
                candidate_k *= 2
            if candidate_k <= args.max_k and time.time() + 1800 < deadline:
                write_status(agent_dir, f"launching corrective K={candidate_k} run", deadline, [])
                launch_ralphloop(agent_dir, (deadline - time.time()) / 3600, candidate_k, args.provider, render=False)
                launched_ks.add(candidate_k)
                time.sleep(args.poll_seconds)
                continue
            write_status(agent_dir, "review says not solved; no more launch budget or max-k reached", deadline, [])
        else:
            write_status(agent_dir, "no completed selector summary yet", deadline, [])
        time.sleep(args.poll_seconds)

    write_status(agent_dir, "agent deadline reached", deadline, active_ralphloop_pids())


if __name__ == "__main__":
    main()
