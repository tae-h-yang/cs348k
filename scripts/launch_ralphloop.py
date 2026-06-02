"""Launch RalphLoop as a detached background process."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=12)
    parser.add_argument("--k-after", type=int, default=32)
    parser.add_argument("--provider", default="cuda", choices=["cuda", "cpu", "tensorrt"])
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()

    log = ROOT / "results" / "ralphloop_launch.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "bash",
        str(ROOT / "scripts" / "ralphloop.sh"),
        "--hours",
        str(args.hours),
        "--k-after",
        str(args.k_after),
        "--provider",
        args.provider,
    ]
    if args.no_render:
        cmd.append("--no-render")

    env = os.environ.copy()
    env.setdefault("MUJOCO_GL", "egl")
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    lib_paths = subprocess.check_output(["python", str(ROOT / "scripts" / "python_nvidia_lib_paths.py")], text=True).strip()
    env["LD_LIBRARY_PATH"] = f"{lib_paths}:{env.get('LD_LIBRARY_PATH', '')}" if lib_paths else env.get("LD_LIBRARY_PATH", "")
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
    print(proc.pid)
    print(log)


if __name__ == "__main__":
    main()
