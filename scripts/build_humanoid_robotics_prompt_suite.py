"""Build a 100-prompt humanoid robotics motion benchmark.

This suite is intentionally different from ``prompt_suite_105.csv``. The older
file expands the currently exposed MotionBricks G1 modes by seed. This file
defines 100 distinct robotics-facing motion intents that a mature generator
should support, including locomotion, whole-body manipulation, safety gestures,
balance recovery, object interaction, and constrained postures.

The current public MotionBricks preview in this repo cannot execute all prompts
directly; the ``current_motionbricks_support`` column makes that explicit.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "configs" / "humanoid_robotics_100_prompts.csv"
OUT_MD = ROOT / "docs" / "autonomous_loop" / "humanoid_robotics_100_prompts.md"


PROMPTS: list[dict[str, str]] = [
    # Locomotion basics, 16
    {"category": "locomotion_basic", "subcategory": "forward", "prompt": "Walk forward at a comfortable indoor pace with symmetric arm swing.", "criteria": "forward progress; upright torso; alternating foot contacts"},
    {"category": "locomotion_basic", "subcategory": "slow", "prompt": "Walk forward slowly as if approaching a fragile object.", "criteria": "low speed; small steps; stable trunk"},
    {"category": "locomotion_basic", "subcategory": "fast", "prompt": "Power-walk forward with brisk but non-running steps.", "criteria": "faster progress; no flight phase; controlled arms"},
    {"category": "locomotion_basic", "subcategory": "backward", "prompt": "Walk backward for several steps while keeping the chest facing forward.", "criteria": "negative forward displacement; upright torso; no spin"},
    {"category": "locomotion_basic", "subcategory": "side_left", "prompt": "Sidestep to the robot's left with feet never crossing.", "criteria": "leftward displacement; side gait; feet separated"},
    {"category": "locomotion_basic", "subcategory": "side_right", "prompt": "Sidestep to the robot's right with feet never crossing.", "criteria": "rightward displacement; side gait; feet separated"},
    {"category": "locomotion_basic", "subcategory": "turn_left", "prompt": "Turn in place ninety degrees to the left without traveling forward.", "criteria": "yaw change left; low translation; stable feet"},
    {"category": "locomotion_basic", "subcategory": "turn_right", "prompt": "Turn in place ninety degrees to the right without traveling forward.", "criteria": "yaw change right; low translation; stable feet"},
    {"category": "locomotion_basic", "subcategory": "curve", "prompt": "Walk along a gentle left-curving path while looking in the travel direction.", "criteria": "curved trajectory; heading follows path; no abrupt spin"},
    {"category": "locomotion_basic", "subcategory": "stop", "prompt": "Walk forward and come to a balanced stop with both feet planted.", "criteria": "initial progress; final low velocity; double support"},
    {"category": "locomotion_basic", "subcategory": "start", "prompt": "Start from standing and smoothly accelerate into a walk.", "criteria": "standing first frames; gradual speed increase; no jump"},
    {"category": "locomotion_basic", "subcategory": "pace_change", "prompt": "Walk forward, slow down for two steps, then resume normal speed.", "criteria": "speed modulation; forward progress; stable contacts"},
    {"category": "locomotion_basic", "subcategory": "narrow", "prompt": "Walk forward on an imaginary narrow walkway with careful foot placement.", "criteria": "narrow step width; low sway; forward progress"},
    {"category": "locomotion_basic", "subcategory": "wide", "prompt": "Walk forward with a deliberately wide stable stance.", "criteria": "wide step width; forward progress; upright torso"},
    {"category": "locomotion_basic", "subcategory": "march", "prompt": "March in place with clear alternating knee lifts.", "criteria": "low translation; alternating high knees; regular rhythm"},
    {"category": "locomotion_basic", "subcategory": "shuffle", "prompt": "Shuffle forward with short low steps and minimal arm swing.", "criteria": "short steps; low foot clearance; low arm motion"},
    # Terrain and obstacle proxies, 12
    {"category": "terrain_obstacle", "subcategory": "step_over_low", "prompt": "Step over a low obstacle with the right foot first.", "criteria": "right leg leads; elevated swing foot; no foot drag"},
    {"category": "terrain_obstacle", "subcategory": "step_over_left", "prompt": "Step over a low obstacle with the left foot first.", "criteria": "left leg leads; elevated swing foot; no foot drag"},
    {"category": "terrain_obstacle", "subcategory": "high_step", "prompt": "Walk forward using high steps as if crossing scattered cables.", "criteria": "repeated foot clearance; forward progress; no stumble"},
    {"category": "terrain_obstacle", "subcategory": "duck_under", "prompt": "Crouch slightly while walking under a low bar, then return upright.", "criteria": "temporary lower root height; forward progress; recovery upright"},
    {"category": "terrain_obstacle", "subcategory": "slope_up", "prompt": "Walk forward as if climbing a shallow ramp with a slight forward lean.", "criteria": "forward progress; mild torso pitch; stable cadence"},
    {"category": "terrain_obstacle", "subcategory": "slope_down", "prompt": "Walk forward as if descending a shallow ramp with cautious short steps.", "criteria": "forward progress; lower speed; stable trunk"},
    {"category": "terrain_obstacle", "subcategory": "uneven", "prompt": "Cross uneven ground with cautious alternating steps and visible balance corrections.", "criteria": "irregular step timing; upright recovery; no collapse"},
    {"category": "terrain_obstacle", "subcategory": "threshold", "prompt": "Approach a doorway threshold, step across it, and continue walking.", "criteria": "approach; single higher step; resume gait"},
    {"category": "terrain_obstacle", "subcategory": "avoid_left", "prompt": "Walk forward and swerve gently left around an obstacle.", "criteria": "forward then lateral path change; no abrupt jump"},
    {"category": "terrain_obstacle", "subcategory": "avoid_right", "prompt": "Walk forward and swerve gently right around an obstacle.", "criteria": "forward then lateral path change; no abrupt jump"},
    {"category": "terrain_obstacle", "subcategory": "step_down", "prompt": "Step down from a shallow platform and regain a normal walking rhythm.", "criteria": "one lowering event; stable landing; continue walking"},
    {"category": "terrain_obstacle", "subcategory": "tight_turn", "prompt": "Walk forward, make a compact one-hundred-eighty-degree turn, and walk back.", "criteria": "forward progress; 180 yaw change; return path"},
    # Loco-manipulation, 18
    {"category": "loco_manipulation", "subcategory": "carry_front", "prompt": "Walk forward while carrying a small box with both hands at chest height.", "criteria": "hands held near chest; forward gait; reduced arm swing"},
    {"category": "loco_manipulation", "subcategory": "carry_low", "prompt": "Walk forward while carrying a bag low in the right hand.", "criteria": "right hand low and steady; forward gait; asymmetric arm motion"},
    {"category": "loco_manipulation", "subcategory": "tray", "prompt": "Walk carefully while keeping both hands level as if holding a tray.", "criteria": "hands level; smooth trunk; slow forward progress"},
    {"category": "loco_manipulation", "subcategory": "push_cart", "prompt": "Walk forward with both hands extended as if pushing a cart.", "criteria": "hands forward; forward gait; stable torso"},
    {"category": "loco_manipulation", "subcategory": "pull_cart", "prompt": "Walk backward with both hands forward as if pulling a cart toward the robot.", "criteria": "backward displacement; arms forward; no body spin"},
    {"category": "loco_manipulation", "subcategory": "open_door", "prompt": "Step forward, reach with the right hand as if opening a door, then pass through.", "criteria": "right arm reach; step-through; forward continuation"},
    {"category": "loco_manipulation", "subcategory": "close_door", "prompt": "Turn slightly, pull the right hand back as if closing a door, then stand balanced.", "criteria": "right arm pull; torso turn; final stable stance"},
    {"category": "loco_manipulation", "subcategory": "reach_shelf", "prompt": "Walk to a shelf and reach upward with both hands.", "criteria": "forward approach; both hands lift; no jump"},
    {"category": "loco_manipulation", "subcategory": "place_shelf", "prompt": "Raise both hands to place an object on a shoulder-height shelf.", "criteria": "hands lift then settle; upright stance; controlled elbows"},
    {"category": "loco_manipulation", "subcategory": "pick_table", "prompt": "Step to a table and reach forward with both hands to pick up an object.", "criteria": "approach; forward arm extension; slight torso lean"},
    {"category": "loco_manipulation", "subcategory": "press_button", "prompt": "Take one step forward and press a wall button with the right index-hand pose.", "criteria": "short approach; right hand forward; final pause"},
    {"category": "loco_manipulation", "subcategory": "wipe_surface", "prompt": "Stand in place and wipe a horizontal surface with the right hand.", "criteria": "stationary feet; cyclic right arm sweep; stable trunk"},
    {"category": "loco_manipulation", "subcategory": "two_hand_lift", "prompt": "Squat slightly and lift a light object with both hands using the legs.", "criteria": "knee bend; both hands low to higher; return upright"},
    {"category": "loco_manipulation", "subcategory": "drag_object", "prompt": "Lean back slightly and pull an imaginary heavy object with both hands.", "criteria": "hands pull backward; backward lean; feet remain stable"},
    {"category": "loco_manipulation", "subcategory": "scan_shelf", "prompt": "Walk slowly past a shelf while the head and torso scan left to right.", "criteria": "slow path; yaw oscillation; stable gait"},
    {"category": "loco_manipulation", "subcategory": "handoff_receive", "prompt": "Step forward and present both hands to receive an object.", "criteria": "forward step; both hands open forward; final pause"},
    {"category": "loco_manipulation", "subcategory": "handoff_give", "prompt": "Step forward and extend both hands as if handing over an object.", "criteria": "forward step; both hands extend; stable end pose"},
    {"category": "loco_manipulation", "subcategory": "operate_panel", "prompt": "Stand at a control panel and alternate pressing buttons with left and right hands.", "criteria": "feet stationary; alternating hand reaches; low torso drift"},
    # Inspection and manipulation stance, 12
    {"category": "manipulation_stance", "subcategory": "bend_pick", "prompt": "Bend at the knees to pick up a small object from the floor with the right hand.", "criteria": "root lowers; right hand reaches floor; recover upright"},
    {"category": "manipulation_stance", "subcategory": "left_pick", "prompt": "Bend at the knees to pick up a small object from the floor with the left hand.", "criteria": "root lowers; left hand reaches floor; recover upright"},
    {"category": "manipulation_stance", "subcategory": "kneel_inspect", "prompt": "Lower into a kneeling inspection pose and look toward the floor.", "criteria": "root lowers substantially; one knee near floor; controlled posture"},
    {"category": "manipulation_stance", "subcategory": "tool_use", "prompt": "Stand and make a two-handed twisting motion as if using a screwdriver.", "criteria": "feet stable; hands near midline; cyclic forearm twist"},
    {"category": "manipulation_stance", "subcategory": "hammer", "prompt": "Stand with feet planted and swing the right hand downward as if using a hammer.", "criteria": "feet stable; right arm cyclic downstroke; torso controlled"},
    {"category": "manipulation_stance", "subcategory": "inspect_under", "prompt": "Crouch and lean forward to inspect underneath a table.", "criteria": "lower posture; forward lean; no hand-floor collapse"},
    {"category": "manipulation_stance", "subcategory": "reach_low", "prompt": "Reach down and forward with both hands without moving the feet.", "criteria": "stationary root; arms forward-low; stable knees"},
    {"category": "manipulation_stance", "subcategory": "reach_high", "prompt": "Reach overhead with the right hand while the left hand balances at the side.", "criteria": "right hand high; left arm counterbalance; feet planted"},
    {"category": "manipulation_stance", "subcategory": "sort_bins", "prompt": "Shift weight left and right while moving imaginary objects between waist-high bins.", "criteria": "lateral weight shifts; alternating hand motions; stable feet"},
    {"category": "manipulation_stance", "subcategory": "scan_ground", "prompt": "Walk two small steps, crouch, and visually inspect the ground.", "criteria": "short progress; crouch; head or torso pitch"},
    {"category": "manipulation_stance", "subcategory": "lean_reach", "prompt": "Lean to the left and reach the left hand outward while keeping both feet planted.", "criteria": "left hand reach; COM remains supported; no step"},
    {"category": "manipulation_stance", "subcategory": "right_lean_reach", "prompt": "Lean to the right and reach the right hand outward while keeping both feet planted.", "criteria": "right hand reach; COM remains supported; no step"},
    # Balance and recovery, 12
    {"category": "balance_recovery", "subcategory": "single_leg_right", "prompt": "Balance briefly on the right leg while lifting the left knee.", "criteria": "right support; left knee lift; no fall"},
    {"category": "balance_recovery", "subcategory": "single_leg_left", "prompt": "Balance briefly on the left leg while lifting the right knee.", "criteria": "left support; right knee lift; no fall"},
    {"category": "balance_recovery", "subcategory": "stumble_forward", "prompt": "Recover from a small forward stumble with one quick corrective step.", "criteria": "forward pitch; recovery step; final upright"},
    {"category": "balance_recovery", "subcategory": "stumble_left", "prompt": "Recover from a small leftward stumble with a side step.", "criteria": "left lean; lateral recovery step; final upright"},
    {"category": "balance_recovery", "subcategory": "stumble_right", "prompt": "Recover from a small rightward stumble with a side step.", "criteria": "right lean; lateral recovery step; final upright"},
    {"category": "balance_recovery", "subcategory": "back_recovery", "prompt": "Recover from a slight backward lean by stepping back.", "criteria": "backward lean; backward step; final upright"},
    {"category": "balance_recovery", "subcategory": "ankle_strategy", "prompt": "Stand still and sway gently forward and backward without stepping.", "criteria": "small root sway; feet planted; no large arm flail"},
    {"category": "balance_recovery", "subcategory": "hip_strategy", "prompt": "Stand still and make a larger torso balance correction without moving the feet.", "criteria": "torso sway; feet planted; recover center"},
    {"category": "balance_recovery", "subcategory": "catch_balance", "prompt": "Lift both arms outward to regain balance after a small perturbation.", "criteria": "arms abduct; trunk returns upright; feet stable or one step"},
    {"category": "balance_recovery", "subcategory": "toe_stand", "prompt": "Rise briefly onto the toes and return to flat feet.", "criteria": "heel lift; low translation; controlled return"},
    {"category": "balance_recovery", "subcategory": "heel_rock", "prompt": "Rock back briefly onto the heels and return to normal standing.", "criteria": "toe lift; low translation; controlled return"},
    {"category": "balance_recovery", "subcategory": "loaded_balance", "prompt": "Stand while holding both hands forward as if carrying a load and resist a small sway.", "criteria": "arms forward; small COM sway; no stepping unless needed"},
    # Communication and safety gestures, 10
    {"category": "communication_safety", "subcategory": "wave", "prompt": "Stand still and wave the right hand at shoulder height.", "criteria": "feet stationary; right arm wave; upright torso"},
    {"category": "communication_safety", "subcategory": "stop_signal", "prompt": "Take one step forward and raise the right palm in a stop signal.", "criteria": "one step; right hand forward-high; final pause"},
    {"category": "communication_safety", "subcategory": "point_left", "prompt": "Point clearly to the robot's left with the left arm while standing.", "criteria": "left arm lateral extension; feet stable; low torso drift"},
    {"category": "communication_safety", "subcategory": "point_right", "prompt": "Point clearly to the robot's right with the right arm while standing.", "criteria": "right arm lateral extension; feet stable; low torso drift"},
    {"category": "communication_safety", "subcategory": "beckon", "prompt": "Stand and make a beckoning motion with the right hand.", "criteria": "right hand cyclic pull; feet stable; upright"},
    {"category": "communication_safety", "subcategory": "yield", "prompt": "Step backward and raise both hands slightly as a yielding gesture.", "criteria": "backward step; hands lift; final stable stance"},
    {"category": "communication_safety", "subcategory": "look_around", "prompt": "Stand still and look left, right, then forward.", "criteria": "yaw sequence; feet planted; no arm requirement"},
    {"category": "communication_safety", "subcategory": "caution", "prompt": "Walk slowly while holding both hands slightly outward for caution.", "criteria": "slow forward gait; arms out; stable torso"},
    {"category": "communication_safety", "subcategory": "direct_traffic", "prompt": "Stand and sweep the right arm sideways as if directing someone to pass.", "criteria": "right arm lateral sweep; feet stable; torso controlled"},
    {"category": "communication_safety", "subcategory": "emergency_stop", "prompt": "Abruptly stop from a slow walk and plant both feet in a stable stance.", "criteria": "initial walking; rapid deceleration; double support"},
    # Low posture and floor-adjacent, 10
    {"category": "low_posture", "subcategory": "crouch_walk", "prompt": "Crouch-walk forward while keeping the torso below normal walking height.", "criteria": "lower root; forward progress; no hand-floor contact"},
    {"category": "low_posture", "subcategory": "hands_crawl", "prompt": "Crawl forward using hands and feet in a controlled low posture.", "criteria": "hand-floor contact expected; low root; forward progress"},
    {"category": "low_posture", "subcategory": "elbow_crawl", "prompt": "Crawl forward on elbows with the torso close to the ground.", "criteria": "elbow/forearm contact expected; low root; forward progress"},
    {"category": "low_posture", "subcategory": "kneel_to_stand", "prompt": "Start kneeling and rise to a stable standing posture.", "criteria": "root rises; knee contact early; final upright"},
    {"category": "low_posture", "subcategory": "stand_to_kneel", "prompt": "Lower from standing into a kneeling posture without falling.", "criteria": "root lowers; controlled knee contact; final stable kneel"},
    {"category": "low_posture", "subcategory": "duck_walk", "prompt": "Move forward in a deep squat duck-walk for several steps.", "criteria": "very low root; forward progress; alternating feet"},
    {"category": "low_posture", "subcategory": "recover_floor", "prompt": "Push up from a hands-and-knees pose into standing.", "criteria": "hands/knees contact early; root rises; final upright"},
    {"category": "low_posture", "subcategory": "inspect_floor", "prompt": "Drop into a low squat, reach toward the floor, and stand again.", "criteria": "squat; hand near floor; full recovery"},
    {"category": "low_posture", "subcategory": "crawl_turn", "prompt": "Crawl forward and turn slightly left while staying low.", "criteria": "low root; forward and yaw change; hand contact acceptable"},
    {"category": "low_posture", "subcategory": "low_side_step", "prompt": "Perform two low sideways squat steps to the right.", "criteria": "low root; rightward displacement; stable knees"},
    # Human-robot workspace tasks, 10
    {"category": "workspace_task", "subcategory": "approach_human", "prompt": "Approach a person slowly and stop at a respectful distance.", "criteria": "slow forward progress; final stop; upright neutral arms"},
    {"category": "workspace_task", "subcategory": "retreat_human", "prompt": "Step backward away from a person while keeping the torso facing them.", "criteria": "backward displacement; heading maintained; stable arms"},
    {"category": "workspace_task", "subcategory": "carry_turn", "prompt": "Carry an imaginary box, turn left, and continue walking.", "criteria": "hands held; left yaw; forward continuation"},
    {"category": "workspace_task", "subcategory": "inspect_machine", "prompt": "Walk to a machine, lean in slightly, and inspect it with hands behind the back.", "criteria": "approach; forward lean; arms held back"},
    {"category": "workspace_task", "subcategory": "pick_place_bin", "prompt": "Pick an object from the left side and place it into a bin on the right.", "criteria": "left reach; right place; torso weight shift"},
    {"category": "workspace_task", "subcategory": "open_drawer", "prompt": "Step forward, reach low with both hands, and pull as if opening a drawer.", "criteria": "approach; hands low-forward; backward pull"},
    {"category": "workspace_task", "subcategory": "push_button_sequence", "prompt": "Press three imaginary buttons from left to right on a waist-high panel.", "criteria": "three distinct reaches; left-to-right order; feet stable"},
    {"category": "workspace_task", "subcategory": "scan_package", "prompt": "Stand at a table and move both hands around a package as if scanning it.", "criteria": "feet stable; two-hand motions; hands near table height"},
    {"category": "workspace_task", "subcategory": "pass_narrow_gap", "prompt": "Turn the shoulders slightly and walk through a narrow gap.", "criteria": "forward progress; torso yaw/shoulder narrowing; no collision proxy"},
    {"category": "workspace_task", "subcategory": "recover_loaded_walk", "prompt": "Walk forward carrying a load and take a corrective step after a small imbalance.", "criteria": "arms held load; perturbation recovery; final upright"},
]


SUPPORTED_MODE_HINTS = {
    "walk": {"locomotion_basic", "communication_safety", "whole_body_expressive", "workspace_task"},
    "walk_left": {"locomotion_basic"},
    "walk_right": {"locomotion_basic"},
    "walk_zombie": {"whole_body_expressive"},
    "walk_stealth": {"whole_body_expressive"},
    "walk_boxing": {"whole_body_expressive"},
    "hand_crawling": {"low_posture"},
    "elbow_crawling": {"low_posture"},
    "idle": {"communication_safety", "manipulation_stance", "balance_recovery"},
}


def support_label(row: dict[str, str]) -> tuple[str, str]:
    category = row["category"]
    prompt = row["prompt"].lower()
    if category == "low_posture" and "crawl" in prompt:
        return "__PARTIAL__", "hand_crawling_or_elbow_crawling"
    if category == "whole_body_expressive" and "zombie" in prompt:
        return "__YES_MODE_PROXY__", "walk_zombie"
    if category == "whole_body_expressive" and "boxing" in prompt:
        return "__YES_MODE_PROXY__", "walk_boxing"
    if category == "locomotion_basic" and "left" in prompt and "sidestep" in prompt:
        return "__YES_MODE_PROXY__", "walk_left"
    if category == "locomotion_basic" and "right" in prompt and "sidestep" in prompt:
        return "__YES_MODE_PROXY__", "walk_right"
    if category in SUPPORTED_MODE_HINTS["walk"]:
        return "__PARTIAL__", "walk_or_style_mode"
    return "__NO__", "requires_new_generator_control"


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for idx, row in enumerate(PROMPTS, start=1):
        prompt = row["prompt"].strip()
        key = prompt.lower()
        if key in seen:
            raise ValueError(f"Duplicate prompt text: {prompt}")
        seen.add(key)
        support, mode_hint = support_label(row)
        rows.append({
            "prompt_id": f"hrb_{idx:03d}",
            "category": row["category"],
            "subcategory": row["subcategory"],
            "prompt_text": prompt,
            "success_criteria": row["criteria"],
            "expected_primary_contacts": infer_contacts(row),
            "expected_root_motion": infer_root_motion(row),
            "expected_arm_role": infer_arm_role(row),
            "hardness": infer_hardness(row, support),
            "current_motionbricks_support": support,
            "motionbricks_mode_hint": mode_hint,
            "evaluation_notes": "Use MotionSpec predicates plus physics/contact/controller/visual audit.",
        })
    if len(rows) != 100:
        raise ValueError(f"Expected 100 prompts, got {len(rows)}")
    return rows


def infer_contacts(row: dict[str, str]) -> str:
    text = row["prompt"].lower()
    if "crawl" in text:
        return "feet;hands_or_elbows"
    if "kneel" in text or "kneeling" in text:
        return "feet;knee"
    if "single" in row["subcategory"]:
        return "one_foot"
    return "feet"


def infer_root_motion(row: dict[str, str]) -> str:
    text = row["prompt"].lower()
    if any(word in text for word in ["stand", "standing", "in place", "without moving the feet", "feet planted"]):
        return "mostly_stationary"
    if "backward" in text or "step backward" in text:
        return "backward"
    if "left" in text and ("sidestep" in text or "swerve" in text):
        return "leftward"
    if "right" in text and ("sidestep" in text or "swerve" in text):
        return "rightward"
    if "turn" in text:
        return "turning"
    return "forward_or_task_dependent"


def infer_arm_role(row: dict[str, str]) -> str:
    text = row["prompt"].lower()
    if any(word in text for word in ["carry", "hands", "reach", "press", "push", "pull", "wipe", "point", "wave", "button", "object", "box", "tray"]):
        return "task_constrained"
    if any(word in text for word in ["arm", "punch", "zombie", "dance", "celebration"]):
        return "expressive"
    return "natural_or_unspecified"


def infer_hardness(row: dict[str, str], support: str) -> str:
    if support == "__NO__":
        return "high"
    if row["category"] in {"low_posture", "terrain_obstacle", "loco_manipulation", "workspace_task"}:
        return "medium_high"
    return "medium"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    support_counts: dict[str, int] = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
        support_counts[row["current_motionbricks_support"]] = support_counts.get(row["current_motionbricks_support"], 0) + 1

    lines = [
        "# Humanoid Robotics 100-Prompt Benchmark",
        "",
        "This is the target benchmark for the pivoted project. It contains 100",
        "distinct humanoid robotics motion intents, not seed duplicates. It is a",
        "specification for generation and evaluation; the current local MotionBricks",
        "preview only supports a subset through discrete G1 modes.",
        "",
        "## Category Counts",
        "",
    ]
    for category, count in sorted(counts.items()):
        lines.append(f"- `{category}`: {count}")
    lines.extend(["", "## Current Generator Support", ""])
    for support, count in sorted(support_counts.items()):
        lines.append(f"- `{support}`: {count}")
    lines.extend([
        "",
        "## Required Evaluation Layers",
        "",
        "- MotionSpec predicates: prompt-derived checks for direction, speed, posture, arm role, contacts, and event order.",
        "- Kinematic checks: finite qpos, joint limits, root height, foot skate, self-contact, non-foot floor contact.",
        "- Dynamics checks: inverse dynamics torque demand, unactuated root wrench, velocity/acceleration/jerk.",
        "- Controller checks: SONIC or another learned G1 tracker for survival time, tracking RMSE, falls, and effort.",
        "- Visual audit: rendered clips or contact sheets reviewed for prompt match and obvious artifacts.",
        "",
        "## First 20 Prompts",
        "",
        "| ID | Category | Prompt | Support |",
        "|---|---|---|---|",
    ])
    for row in rows[:20]:
        lines.append(
            f"| `{row['prompt_id']}` | `{row['category']}` | {row['prompt_text']} | "
            f"`{row['current_motionbricks_support']}` |"
        )
    lines.append("")
    path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_csv", type=Path, default=OUT_CSV)
    parser.add_argument("--out_md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    rows = build_rows()
    write_csv(args.out_csv, rows)
    write_md(args.out_md, rows)
    print(f"Wrote {len(rows)} distinct prompts to {args.out_csv}")
    print(f"Wrote benchmark notes to {args.out_md}")


if __name__ == "__main__":
    main()
