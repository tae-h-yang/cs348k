from __future__ import annotations

import numpy as np
import torch

from scripts.train_native_sonic_acceptance import (
    NativeRecord,
    collate,
    normalize_qpos,
    split_folds,
    strict_pass,
)
from scripts.run_sonic_native_release_batch import category, interleave_by_mode_identity, parse_mode


def test_strict_pass_requires_survival_tracking_and_root_error() -> None:
    assert strict_pass({"fell": "False", "mean_joint_rmse": "0.19", "mean_root_xy_error": "1.4"})
    assert not strict_pass({"fell": "True", "mean_joint_rmse": "0.10", "mean_root_xy_error": "0.1"})
    assert not strict_pass({"fell": "False", "mean_joint_rmse": "0.21", "mean_root_xy_error": "0.1"})
    assert not strict_pass({"fell": "False", "mean_joint_rmse": "0.10", "mean_root_xy_error": "1.6"})


def test_normalize_qpos_recenters_xy_and_normalizes_quaternion() -> None:
    qpos = np.zeros((3, 36), dtype=np.float32)
    qpos[:, 0] = [10.0, 11.0, 12.0]
    qpos[:, 1] = [-4.0, -3.0, -2.0]
    qpos[:, 3:7] = np.array(
        [
            [2.0, 0.0, 0.0, 0.0],
            [0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 4.0, 0.0],
        ],
        dtype=np.float32,
    )

    out = normalize_qpos(qpos)

    assert np.allclose(out[:, :2], [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
    assert np.allclose(np.linalg.norm(out[:, 3:7], axis=1), 1.0)
    assert np.allclose(qpos[:, 0], [10.0, 11.0, 12.0])


def test_collate_pads_variable_length_sequences() -> None:
    x1 = torch.ones(36, 2)
    x2 = torch.full((36, 4), 2.0)

    padded, mask, labels, keys = collate(
        [
            (x1, torch.tensor(1.0), "short"),
            (x2, torch.tensor(0.0), "long"),
        ]
    )

    assert padded.shape == (2, 36, 4)
    assert mask.tolist() == [[True, True, False, False], [True, True, True, True]]
    assert labels.tolist() == [1.0, 0.0]
    assert keys == ["short", "long"]
    assert torch.all(padded[0, :, 2:] == 0.0)


def test_split_folds_keeps_identities_disjoint() -> None:
    records = [
        NativeRecord(
            key=f"motion_{identity}_{rep}",
            identity=f"id_{identity}",
            selector="baseline",
            path=None,  # type: ignore[arg-type]
            label=rep % 2,
            candidate_k=rep,
            mode="walk",
            seed_idx=identity,
            scalars={},
        )
        for identity in range(6)
        for rep in range(2)
    ]

    for train, val in split_folds(records, n_folds=3, seed=7):
        train_ids = {record.identity for record in train}
        val_ids = {record.identity for record in val}
        assert train_ids.isdisjoint(val_ids)
        assert len(val_ids) == 2


def test_native_batch_mode_parsing_strips_selector_prefixes() -> None:
    assert parse_mode("baseline_k0_idle_seed7_cand0") == "idle"
    assert parse_mode("best_precontroller_injured_walk_seed10_cand0") == "injured_walk"
    assert parse_mode("lowest_id_risk_hand_crawling_seed9_cand1") == "hand_crawling"
    assert parse_mode("learned_acceptance_walk_stealth_seed9_cand7") == "walk_stealth"
    assert parse_mode("hybrid_acceptance_walk_scared_seed8_cand2") == "walk_scared"
    assert category("baseline_k0_idle_seed7_cand0") == "idle"
    assert category("best_precontroller_hand_crawling_seed9_cand1") == "low_posture_crawling"
    assert category("gated_precontroller_walk_stealth_seed9_cand1") == "upright"
    assert category("learned_acceptance_idle_seed9_cand0") == "idle"
    assert category("hybrid_acceptance_idle_seed8_cand1") == "idle"


def test_mode_interleaved_order_balances_identity_modes() -> None:
    names = [
        "baseline_k0_elbow_crawling_seed7_cand0",
        "best_precontroller_elbow_crawling_seed7_cand1",
        "baseline_k0_idle_seed7_cand0",
        "best_precontroller_idle_seed7_cand1",
        "baseline_k0_walk_seed7_cand0",
        "best_precontroller_walk_seed7_cand1",
        "baseline_k0_elbow_crawling_seed8_cand0",
        "baseline_k0_idle_seed8_cand0",
    ]

    ordered = interleave_by_mode_identity(names)

    first_identities = [name.rsplit("_cand", 1)[0] for name in ordered[:6]]
    assert first_identities == [
        "baseline_k0_elbow_crawling_seed7",
        "best_precontroller_elbow_crawling_seed7",
        "baseline_k0_idle_seed7",
        "best_precontroller_idle_seed7",
        "baseline_k0_walk_seed7",
        "best_precontroller_walk_seed7",
    ]
