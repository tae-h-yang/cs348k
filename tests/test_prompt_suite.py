from __future__ import annotations

from collections import Counter

from scripts.build_humanoid_robotics_prompt_suite import build_rows


def test_humanoid_robotics_suite_is_diverse() -> None:
    rows = build_rows()
    assert len(rows) == 100
    assert len({row["prompt_text"].lower() for row in rows}) == 100

    categories = Counter(row["category"] for row in rows)
    assert len(categories) >= 8
    assert categories["dynamic_locomotion"] >= 10
    assert categories["dance_expressive"] >= 10
    assert categories["floor_low_posture"] >= 10
    assert categories["athletic_stress"] >= 8

    prompts = [row["prompt_text"].lower() for row in rows]
    assert sum("walk" in prompt for prompt in prompts) <= 25
    assert sum(any(token in prompt for token in ["jump", "hop", "skip", "bound"]) for prompt in prompts) >= 8
    assert sum(any(token in prompt for token in ["crawl", "floor", "roll", "kneel", "plank", "handstand", "cartwheel"]) for prompt in prompts) >= 17


def test_prompt_suite_labeling_avoids_substring_artifacts() -> None:
    rows = {row["subcategory"]: row for row in build_rows()}

    assert rows["forward_walk"]["expected_arm_role"] == "natural_or_unspecified"
    assert rows["one_leg_hop_right"]["expected_primary_contacts"] == "one_foot"
    assert rows["one_leg_hop_right"]["expected_root_motion"] == "aerial_or_impulsive"
    assert rows["hip_hop_heel_toe"]["motionbricks_mode_hint"] == "walk_happy_dance"
    assert rows["handstand_kickup"]["hardness"] == "extreme_negative_control"
