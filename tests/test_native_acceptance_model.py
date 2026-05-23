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
