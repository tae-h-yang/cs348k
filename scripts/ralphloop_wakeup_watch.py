"""Wait for RalphLoop to finish and write a visible wake-up marker."""

from __future__ import annotations

import subprocess
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "ralphloop_wakeup.md"
LOG = ROOT / "results" / "ralphloop_wakeup.log"


def active_pids() -> list[str]:
    proc = subprocess.run(
        ["pgrep", "-af", r"ralphloop\.sh|run_humanoid100_motionbricks_experiment\.py|evaluate_sonic_policy_mujoco\.py|repair_humanoid100_references\.py|render_selected_overlay_videos\.py"],
        text=True,
        capture_output=True,
    )
    lines = []
    for line in proc.stdout.splitlines():
        if "ralphloop_wakeup_watch.py" not in line:
            lines.append(line)
    return lines


def latest_status() -> str:
    path = ROOT / "results" / "ralphloop" / "latest" / "status.md"
    return path.read_text(errors="ignore") if path.exists() else "(missing status)"


def notify(message: str) -> None:
    for cmd in [
        ["notify-send", "RalphLoop", message],
        ["bash", "-lc", "printf '\\a'"],
    ]:
        try:
            subprocess.run(cmd, timeout=3, check=False)
        except Exception:
            pass


def main() -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    start = datetime.now()
    with LOG.open("a") as f:
        f.write(f"{start.isoformat()} watcher started\n")
    while True:
        pids = active_pids()
        if not pids:
            done = datetime.now()
            text = "\n".join(
                [
                    "# RalphLoop Wake-Up",
                    "",
                    f"- completed_at: {done.strftime('%Y-%m-%d %H:%M:%S')}",
                    f"- watched_since: {start.strftime('%Y-%m-%d %H:%M:%S')}",
                    "",
                    "## Latest Status",
                    "",
                    latest_status(),
                    "",
                    "## Next Check",
                    "",
                    "- Inspect `results/ralphloop/latest/ralphloop_summary.md`.",
                    "- Inspect `results/ralphloop_agent/review_latest.md` if present.",
                    "- If the strict bar still fails, launch the next corrective experiment.",
                    "",
                ]
            )
            OUT.write_text(text)
            with LOG.open("a") as f:
                f.write(f"{done.isoformat()} watcher completed\n")
            notify(f"RalphLoop finished at {done.strftime('%H:%M:%S')}")
            break
        with LOG.open("a") as f:
            f.write(f"{datetime.now().isoformat()} active={len(pids)}\n")
        time.sleep(120)


if __name__ == "__main__":
    main()
