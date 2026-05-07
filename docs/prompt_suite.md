# Prompt/Task Suite

This suite contains 105 mode-seed rows mapped onto the 15 exposed Unitree G1
MotionBricks preview modes and 7 seeds per mode. It is **not** 100 different
behaviors: there are 15 unique local behavior prompts. The current public
preview is a mode/control interface, not a fully free-form text-to-motion
generator, so prompt following is evaluated with trajectory and style proxies.

## Category Counts

- `directional_locomotion`: 14
- `expressive_locomotion`: 28
- `locomotion`: 28
- `static`: 7
- `style_locomotion`: 14
- `whole_body_low`: 14

## Evaluation Proxies

- Direction/progress: root displacement along the requested direction.
- Speed: path-length speed compared with the nominal task speed.
- Static stability: low root displacement and low joint motion.
- Low-posture tasks: low mean root height.
- Expressive tasks: upper-body motion relative to leg motion.
- Preservation: compare K=1 and K=8 on displacement, speed, and proxy score.

These proxies are weaker than HumanML3D-style R-Precision/FID with a
learned text-motion evaluator; that limitation is explicit in the report.

## First 20 Tasks

| ID | Category | Prompt |
|---|---|---|
| `idle_seed00` | `static` | Stand upright in a relaxed idle pose without traveling. |
| `idle_seed01` | `static` | Stand upright in a relaxed idle pose without traveling. |
| `idle_seed02` | `static` | Stand upright in a relaxed idle pose without traveling. |
| `idle_seed03` | `static` | Stand upright in a relaxed idle pose without traveling. |
| `idle_seed04` | `static` | Stand upright in a relaxed idle pose without traveling. |
| `idle_seed05` | `static` | Stand upright in a relaxed idle pose without traveling. |
| `idle_seed06` | `static` | Stand upright in a relaxed idle pose without traveling. |
| `walk_seed00` | `locomotion` | Walk forward at a natural pace with balanced arm swing. |
| `walk_seed01` | `locomotion` | Walk forward at a natural pace with balanced arm swing. |
| `walk_seed02` | `locomotion` | Walk forward at a natural pace with balanced arm swing. |
| `walk_seed03` | `locomotion` | Walk forward at a natural pace with balanced arm swing. |
| `walk_seed04` | `locomotion` | Walk forward at a natural pace with balanced arm swing. |
| `walk_seed05` | `locomotion` | Walk forward at a natural pace with balanced arm swing. |
| `walk_seed06` | `locomotion` | Walk forward at a natural pace with balanced arm swing. |
| `slow_walk_seed00` | `locomotion` | Walk forward slowly and carefully. |
| `slow_walk_seed01` | `locomotion` | Walk forward slowly and carefully. |
| `slow_walk_seed02` | `locomotion` | Walk forward slowly and carefully. |
| `slow_walk_seed03` | `locomotion` | Walk forward slowly and carefully. |
| `slow_walk_seed04` | `locomotion` | Walk forward slowly and carefully. |
| `slow_walk_seed05` | `locomotion` | Walk forward slowly and carefully. |
