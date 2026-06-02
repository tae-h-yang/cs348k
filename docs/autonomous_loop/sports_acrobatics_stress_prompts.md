# Sports and Acrobatics Stress Prompt Suite

This suite adds high-risk acrobatic and sports motions requested after the
broad13 native SONIC study. It is a target benchmark layer, not a claim
that the current local MotionBricks preview can generate every behavior.

## Domain Counts

- `acrobatics`: 10
- `baseball`: 6
- `basketball`: 4
- `martial_arts`: 2
- `racket_sports`: 3
- `soccer`: 6
- `track_field`: 1

## Current MotionBricks Support

- `__NO__`: 26
- `__PARTIAL__`: 6

## Evaluation Plan

- Use current partial mode hints only as coarse baselines.
- Mark acrobatic inversions, dives, slides, and sport-object interactions as unsupported until a task-conditioned generator or retargeter exists.
- For future executable clips, require native SONIC rollout, contact/root-height checks, sport-specific event predicates, and frame-level visual audit.

## Prompts

| ID | Domain | Subcategory | Prompt | Current support |
|---|---|---|---|---|
| `sport_001` | `acrobatics` | `cartwheel_left` | Perform a slow cartwheel to the left and recover to standing. | `__NO__` |
| `sport_002` | `acrobatics` | `cartwheel_right` | Perform a slow cartwheel to the right and recover to standing. | `__NO__` |
| `sport_003` | `acrobatics` | `roundoff` | Perform a cautious roundoff-like half cartwheel and land facing backward. | `__NO__` |
| `sport_004` | `acrobatics` | `forward_roll` | Perform a controlled forward roll and recover to kneeling. | `__NO__` |
| `sport_005` | `acrobatics` | `side_roll` | Roll sideways on the floor and recover to a crouched stance. | `__NO__` |
| `sport_006` | `acrobatics` | `handstand_kickup` | Kick up toward a brief handstand and return both feet to the floor. | `__NO__` |
| `sport_007` | `acrobatics` | `backbend_bridge` | Lower into a backbend bridge and return to standing. | `__NO__` |
| `sport_008` | `acrobatics` | `burpee` | Squat down, kick the legs back to a plank, return the feet under the body, and stand. | `__NO__` |
| `sport_009` | `acrobatics` | `split_squat_jump` | Perform a small split-squat jump switching which foot is forward. | `__NO__` |
| `sport_010` | `acrobatics` | `knee_slide_recovery` | Slide forward briefly on both knees and recover to kneeling. | `__NO__` |
| `sport_011` | `soccer` | `soccer_inside_pass_right` | Step forward and pass an imaginary soccer ball with the inside of the right foot. | `__NO__` |
| `sport_012` | `soccer` | `soccer_inside_pass_left` | Step forward and pass an imaginary soccer ball with the inside of the left foot. | `__NO__` |
| `sport_013` | `soccer` | `soccer_power_shot` | Take two approach steps and perform a powerful right-foot soccer shot. | `__NO__` |
| `sport_014` | `soccer` | `soccer_dribble` | Dribble an imaginary soccer ball forward with alternating light taps. | `__PARTIAL__` |
| `sport_015` | `soccer` | `soccer_goalkeeper_dive` | Dive sideways like a goalkeeper and recover to the ground safely. | `__NO__` |
| `sport_016` | `soccer` | `soccer_trap_ball` | Lift the right foot to trap an imaginary soccer ball and set it down softly. | `__NO__` |
| `sport_017` | `baseball` | `baseball_pitch_right` | Step forward and throw an overhand baseball pitch with the right arm. | `__NO__` |
| `sport_018` | `baseball` | `baseball_bat_swing_right` | Swing an imaginary baseball bat from the right-handed stance. | `__NO__` |
| `sport_019` | `baseball` | `baseball_bat_swing_left` | Swing an imaginary baseball bat from the left-handed stance. | `__NO__` |
| `sport_020` | `baseball` | `baseball_field_grounder` | Shuffle right and bend down to field a rolling ground ball. | `__PARTIAL__` |
| `sport_021` | `baseball` | `baseball_catch_fly_ball` | Backpedal and raise both hands to catch an imaginary fly ball. | `__PARTIAL__` |
| `sport_022` | `baseball` | `baseball_slide_base` | Perform a feet-first slide into an imaginary base and stop safely. | `__NO__` |
| `sport_023` | `basketball` | `basketball_free_throw` | Bend the knees and shoot an imaginary basketball free throw. | `__NO__` |
| `sport_024` | `basketball` | `basketball_jump_shot` | Perform a small jump shot with both arms extending overhead. | `__NO__` |
| `sport_025` | `basketball` | `basketball_defensive_slide` | Defensive-slide two steps to the left with knees bent and arms out. | `__PARTIAL__` |
| `sport_026` | `basketball` | `basketball_dribble_low` | Crouch slightly and mime a low right-hand basketball dribble while stepping forward. | `__NO__` |
| `sport_027` | `racket_sports` | `tennis_forehand` | Step and swing an imaginary tennis forehand across the body. | `__NO__` |
| `sport_028` | `racket_sports` | `tennis_backhand` | Step and swing an imaginary two-handed tennis backhand. | `__NO__` |
| `sport_029` | `racket_sports` | `tennis_serve` | Toss an imaginary ball and perform an overhead tennis serve. | `__NO__` |
| `sport_030` | `martial_arts` | `front_kick_right` | Lift the right knee and perform a controlled forward front kick. | `__PARTIAL__` |
| `sport_031` | `martial_arts` | `roundhouse_kick_left` | Pivot and perform a controlled left roundhouse kick. | `__PARTIAL__` |
| `sport_032` | `track_field` | `sprinter_start` | Start from a crouched sprint stance and take two explosive steps forward. | `__NO__` |
