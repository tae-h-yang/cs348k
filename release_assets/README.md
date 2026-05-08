# Release Assets

Large generated artifacts are stored here via Git LFS.

Current bundle:

```text
release_assets/cs348k_artifacts_2026-05-08.tar.zst
release_assets/cs348k_artifacts_2026-05-08.tar.zst.sha256
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
