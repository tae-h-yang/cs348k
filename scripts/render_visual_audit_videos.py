"""Render videos for the visual audit manifest.

Each selected qpos clip gets a compact MP4 with non-overlapping labels for
audit id, clip/K, score, risk, SONIC survival, and failed predicates.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import imageio
import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "results" / "visual_audit_manifest.csv"
DEFAULT_OUT_DIR = ROOT / "results" / "videos" / "visual_audit"
MODEL_XML = ROOT / "assets" / "g1" / "scene_29dof.xml"

WIDTH = 640
HEIGHT = 480
FPS = 30


def read_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def camera_for(qpos: np.ndarray) -> mujoco.MjvCamera:
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat = np.array([qpos[0], qpos[1], 0.76], dtype=np.float64)
    cam.azimuth = 90.0
    cam.elevation = -15.0
    cam.distance = 3.6
    return cam


def short(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 3] + "..."


def put(frame: np.ndarray, text: str, x: int, y: int, scale: float = 0.48,
        color: tuple[int, int, int] = (245, 245, 245)) -> None:
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)


def overlay(frame: np.ndarray, row: dict[str, str], t: int) -> np.ndarray:
    out = frame.copy()
    h, w = out.shape[:2]
    cv2.rectangle(out, (0, 0), (w, 88), (0, 0, 0), -1)
    cv2.rectangle(out, (0, h - 60), (w, h), (0, 0, 0), -1)

    title = f"{row['audit_id']}  {row['clip']}  K={row['K']}  {row['reason']}"
    metrics = (
        f"combo {float(row['combined_score']):.2f} | semantic {float(row['semantic_score']):.2f} | "
        f"risk {float(row['full_risk']):.1f} | sonic {float(row['sonic_track_seconds']):.2f}s"
    )
    failures = short(row["failed_predicates"] or "no failed predicates", 110)

    put(out, title, 12, 24, 0.55, (255, 255, 255))
    put(out, metrics, 12, 52, 0.48, (210, 230, 255))
    put(out, f"t={t / FPS:.2f}s", w - 94, 24, 0.48, (230, 230, 230))
    put(out, failures, 12, h - 24, 0.48, (255, 210, 180))
    return out


def render_one(model: mujoco.MjModel, row: dict[str, str], out_dir: Path) -> Path:
    qpos = np.load(row["qpos_path"])
    data = mujoco.MjData(model)
    renderer = mujoco.Renderer(model, height=HEIGHT, width=WIDTH)
    frames: list[np.ndarray] = []
    for t, q in enumerate(qpos):
        mujoco.mj_resetData(model, data)
        data.qpos[:] = q
        mujoco.mj_forward(model, data)
        renderer.update_scene(data, camera=camera_for(q))
        frame = renderer.render().copy()
        frames.append(overlay(frame, row, t))
    renderer.close()

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{row['audit_id']}_{row['clip']}_K{row['K']}.mp4"
    imageio.mimwrite(str(out), frames, fps=FPS, macro_block_size=1)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out_dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    model = mujoco.MjModel.from_xml_path(str(MODEL_XML))
    rows = read_rows(args.manifest)[: args.limit]
    for row in rows:
        out = render_one(model, row, args.out_dir)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
