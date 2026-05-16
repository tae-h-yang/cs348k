"""Render a contact sheet for visually auditing selected qpos clips."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "results" / "visual_audit_manifest.csv"
DEFAULT_OUT = ROOT / "results" / "visual_audit_contact_sheet.png"
MODEL_XML = ROOT / "assets" / "g1" / "scene_29dof.xml"

CELL_W = 320
CELL_H = 250
FRAMES_PER_CLIP = 3
LABEL_H = 72


def read_rows(path: Path) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def camera_for(qpos: np.ndarray) -> mujoco.MjvCamera:
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat = np.array([qpos[0], qpos[1], 0.76], dtype=np.float64)
    cam.azimuth = 90.0
    cam.elevation = -15.0
    cam.distance = 3.4
    return cam


def render_frame(model: mujoco.MjModel, renderer: mujoco.Renderer, qpos: np.ndarray) -> Image.Image:
    data = mujoco.MjData(model)
    mujoco.mj_resetData(model, data)
    data.qpos[:] = qpos
    mujoco.mj_forward(model, data)
    renderer.update_scene(data, camera=camera_for(qpos))
    arr = renderer.render()
    img = Image.fromarray(arr)
    return img.resize((CELL_W, CELL_H - LABEL_H))


def short(text: str, n: int) -> str:
    return text if len(text) <= n else text[: n - 3] + "..."


def draw_label(draw: ImageDraw.ImageDraw, x: int, y: int, row: dict[str, str], font) -> None:
    lines = [
        f"{row['audit_id']} {row['clip']} K={row['K']} [{row['reason']}]",
        f"combo {float(row['combined_score']):.2f} risk {float(row['full_risk']):.1f} sonic {float(row['sonic_track_seconds']):.2f}s",
        short(row["failed_predicates"] or "no failed predicates", 70),
    ]
    for i, line in enumerate(lines):
        draw.text((x + 6, y + 4 + 20 * i), line, fill=(20, 20, 20), font=font)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = read_rows(args.manifest)
    model = mujoco.MjModel.from_xml_path(str(MODEL_XML))
    renderer = mujoco.Renderer(model, height=CELL_H - LABEL_H, width=CELL_W)

    sheet_w = CELL_W * FRAMES_PER_CLIP
    sheet_h = CELL_H * len(rows)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for r, row in enumerate(rows):
        qpos = np.load(row["qpos_path"])
        idxs = [0, len(qpos) // 2, len(qpos) - 1]
        for c, idx in enumerate(idxs):
            img = render_frame(model, renderer, qpos[idx])
            x = c * CELL_W
            y = r * CELL_H
            sheet.paste(img, (x, y + LABEL_H))
            draw.text((x + 8, y + LABEL_H + 6), f"t={idx / 30.0:.2f}s", fill=(255, 255, 255), font=font)
        draw.rectangle((0, r * CELL_H, sheet_w - 1, r * CELL_H + LABEL_H - 1), fill=(235, 235, 235))
        draw_label(draw, 0, r * CELL_H, row, font)
        draw.line((0, (r + 1) * CELL_H - 1, sheet_w, (r + 1) * CELL_H - 1), fill=(120, 120, 120), width=1)

    renderer.close()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
