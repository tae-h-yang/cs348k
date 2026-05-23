# Release Assets

Large generated artifacts are stored here via Git LFS.

Current bundle:

```text
release_assets/cs348k_artifacts_2026-05-08.tar.zst
release_assets/cs348k_artifacts_2026-05-08.tar.zst.sha256
```

Full local-results bundle:

```text
release_assets/cs348k_full_results_motionbricks_2026-05-08.tar.zst
release_assets/cs348k_full_results_motionbricks_2026-05-08.tar.zst.sha256
```

Latest current-validated handoff bundle:

```text
release_assets/cs348k_current_validated_results_data_2026-05-22.tar.zst.part-00
release_assets/cs348k_current_validated_results_data_2026-05-22.tar.zst.part-01
release_assets/cs348k_current_validated_results_data_2026-05-22.tar.zst.sha256
```

Contents include:

- final SONIC actual-qpos videos from `results/sonic_actual_sim_examples_pose_aligned/`
- released-root SONIC videos from `results/sonic_actual_sim_examples_released/`
- generated plots and CSV summaries from `results/`
- supplementary, comparison, risk-explainer, and SONIC policy videos from `results/videos/`
- neural critic checkpoints/logs/plots
- paper PDF and key documentation

Restore on another machine:

```bash
git lfs pull
tar --zstd -xf release_assets/cs348k_artifacts_2026-05-08.tar.zst
sha256sum -c release_assets/cs348k_artifacts_2026-05-08.tar.zst.sha256
```

The extracted top-level folder is `artifact_bundle/`.

Restore the full local results and MotionBricks data:

```bash
git lfs pull
tar --zstd -xf release_assets/cs348k_full_results_motionbricks_2026-05-08.tar.zst
sha256sum -c release_assets/cs348k_full_results_motionbricks_2026-05-08.tar.zst.sha256
```

The full bundle extracts `results/` and `data/motionbricks/`.

Restore the latest current validated run and data tree:

```bash
git lfs pull
cd release_assets
cat cs348k_current_validated_results_data_2026-05-22.tar.zst.part-* > cs348k_current_validated_results_data_2026-05-22.tar.zst
sha256sum -c cs348k_current_validated_results_data_2026-05-22.tar.zst.sha256
cd ..
tar --zstd -xf release_assets/cs348k_current_validated_results_data_2026-05-22.tar.zst
```

This bundle extracts:

- `data/`
- `results/current_validated/`
- `results/prospective_native_selection/20260516_lowroot_gate/`

It is the recommended handoff for continuing the latest SONIC validation work
on another machine. It intentionally omits older scratch/failed result trees
from `results/`, which are much larger and not needed for the current result
hub.
