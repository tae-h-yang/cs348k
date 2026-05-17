# Humanoid Robotics 100-Prompt Benchmark

This is the target benchmark for the pivoted project. It contains 100
distinct humanoid robotics motion intents, not seed duplicates. The suite
was refactored to avoid a walking-only benchmark: it now includes jumps,
one-leg hops, hip-hop-style footwork, crawling, floor transitions,
manipulation, balance recovery, obstacle proxies, and high-risk athletic
negative controls.

The current local MotionBricks preview only supports a subset through
discrete G1 modes. Unsupported rows are still useful: they define the
target behavior space for evaluating future prompt steering, retargeting,
or learned physically-aware generation.

## Category Counts

- `athletic_stress`: 8
- `balance_recovery`: 12
- `communication_safety`: 8
- `dance_expressive`: 12
- `dynamic_locomotion`: 14
- `floor_low_posture`: 12
- `loco_manipulation`: 14
- `manipulation_stance`: 12
- `terrain_obstacle`: 8

## Current Generator Support

- `__NO__`: 78
- `__PARTIAL__`: 14
- `__YES_MODE_PROXY__`: 8

## Required Evaluation Layers

- Prompt/task checks: direction, speed, posture, contacts, arm role, and event order from `success_criteria`.
- Kinematic checks: finite qpos, joint limits, root height, foot skate, self-contact, non-foot floor contact.
- Dynamics checks: inverse dynamics torque demand, unactuated root wrench, velocity, acceleration, and jerk.
- Controller checks: SONIC or another learned G1 tracker for survival time, tracking RMSE, falls, and effort.
- Visual audit: rendered clips/contact sheets for semantic match and obvious artifacts.

## Full Prompt List

| ID | Category | Subcategory | Prompt | Support |
|---|---|---|---|---|
| `hrb_001` | `dynamic_locomotion` | `forward_walk` | Walk forward at a comfortable indoor pace with symmetric arm swing. | `__PARTIAL__` |
| `hrb_002` | `dynamic_locomotion` | `backward_walk` | Walk backward for several steps while keeping the chest facing forward. | `__PARTIAL__` |
| `hrb_003` | `dynamic_locomotion` | `side_shuffle_left` | Shuffle two meters to the robot's left with quick lateral steps. | `__YES_MODE_PROXY__` |
| `hrb_004` | `dynamic_locomotion` | `side_shuffle_right` | Shuffle two meters to the robot's right with quick lateral steps. | `__YES_MODE_PROXY__` |
| `hrb_005` | `dynamic_locomotion` | `turn_in_place` | Turn in place one hundred eighty degrees and stop facing the opposite direction. | `__PARTIAL__` |
| `hrb_006` | `dynamic_locomotion` | `march_high_knees` | March in place with clear alternating high-knee lifts. | `__PARTIAL__` |
| `hrb_007` | `dynamic_locomotion` | `vertical_jump` | Perform a small vertical jump and land with both feet at the starting spot. | `__NO__` |
| `hrb_008` | `dynamic_locomotion` | `broad_jump` | Jump forward a short distance and land in a balanced two-foot stance. | `__NO__` |
| `hrb_009` | `dynamic_locomotion` | `one_leg_hop_right` | Hop in place three times on the right leg while the left knee stays lifted. | `__NO__` |
| `hrb_010` | `dynamic_locomotion` | `one_leg_hop_left` | Hop in place three times on the left leg while the right knee stays lifted. | `__NO__` |
| `hrb_011` | `dynamic_locomotion` | `skip_forward` | Skip forward with alternating light hops and relaxed arm swing. | `__NO__` |
| `hrb_012` | `dynamic_locomotion` | `lateral_bound` | Make two lateral bounding steps to the left and recover to a stable stance. | `__YES_MODE_PROXY__` |
| `hrb_013` | `dynamic_locomotion` | `forward_lunge` | Step into a deep forward lunge and push back to standing. | `__NO__` |
| `hrb_014` | `dynamic_locomotion` | `quick_stop` | Jog two short steps forward and stop abruptly without overbalancing. | `__NO__` |
| `hrb_015` | `dance_expressive` | `hip_hop_heel_toe` | Perform C-walk-inspired hip-hop heel-toe footwork in place without traveling far. | `__YES_MODE_PROXY__` |
| `hrb_016` | `dance_expressive` | `moonwalk` | Perform a short moonwalk illusion moving backward while facing forward. | `__NO__` |
| `hrb_017` | `dance_expressive` | `robot_dance` | Stand in place and perform stiff robot-dance arm and torso isolations. | `__NO__` |
| `hrb_018` | `dance_expressive` | `happy_dance` | Do an energetic happy dance with bouncing knees and wide arm gestures. | `__YES_MODE_PROXY__` |
| `hrb_019` | `dance_expressive` | `boxing_shadow` | Shadowbox in place with alternating jabs and guarded footwork. | `__YES_MODE_PROXY__` |
| `hrb_020` | `dance_expressive` | `tai_chi_sweep` | Perform a slow tai-chi-style weight shift with both arms sweeping outward. | `__NO__` |
| `hrb_021` | `dance_expressive` | `celebration_pump` | Pump both fists overhead twice while bouncing lightly on the feet. | `__NO__` |
| `hrb_022` | `dance_expressive` | `disco_point` | Step side to side while pointing one hand diagonally upward in a disco pose. | `__NO__` |
| `hrb_023` | `dance_expressive` | `zombie_walk` | Walk forward in a zombie-like style with extended arms and stiff knees. | `__YES_MODE_PROXY__` |
| `hrb_024` | `dance_expressive` | `scared_sneak` | Sneak forward nervously with guarded arms and short cautious steps. | `__YES_MODE_PROXY__` |
| `hrb_025` | `dance_expressive` | `air_guitar` | Stand with a wide stance and mime playing an air guitar. | `__NO__` |
| `hrb_026` | `dance_expressive` | `salute_step` | Take one step forward and perform a crisp right-hand salute. | `__NO__` |
| `hrb_027` | `floor_low_posture` | `hand_crawl` | Crawl forward using hands and feet in a controlled low posture. | `__PARTIAL__` |
| `hrb_028` | `floor_low_posture` | `elbow_crawl` | Crawl forward on elbows with the torso close to the ground. | `__PARTIAL__` |
| `hrb_029` | `floor_low_posture` | `bear_crawl` | Bear crawl forward with hips high and hands and feet on the floor. | `__PARTIAL__` |
| `hrb_030` | `floor_low_posture` | `crab_walk` | Crab-walk backward with the chest facing upward and hands behind the body. | `__NO__` |
| `hrb_031` | `floor_low_posture` | `duck_walk` | Move forward in a deep squat duck-walk for several steps. | `__NO__` |
| `hrb_032` | `floor_low_posture` | `kneel_to_stand` | Start kneeling and rise to a stable standing posture. | `__NO__` |
| `hrb_033` | `floor_low_posture` | `stand_to_kneel` | Lower from standing into a kneeling posture without falling. | `__NO__` |
| `hrb_034` | `floor_low_posture` | `pushup_pose` | Lower into a push-up plank and return to standing. | `__NO__` |
| `hrb_035` | `floor_low_posture` | `sit_to_stand` | Rise from a seated floor posture into a stable stand. | `__NO__` |
| `hrb_036` | `floor_low_posture` | `roll_to_kneel` | Perform a safe floor roll onto one side and recover to kneeling. | `__NO__` |
| `hrb_037` | `floor_low_posture` | `low_side_step` | Perform two low sideways squat steps to the right. | `__NO__` |
| `hrb_038` | `floor_low_posture` | `inspect_floor` | Drop into a low squat, reach toward the floor, and stand again. | `__NO__` |
| `hrb_039` | `manipulation_stance` | `pick_floor_right` | Bend at the knees to pick up a small object from the floor with the right hand. | `__NO__` |
| `hrb_040` | `manipulation_stance` | `pick_floor_left` | Bend at the knees to pick up a small object from the floor with the left hand. | `__NO__` |
| `hrb_041` | `manipulation_stance` | `reach_overhead` | Reach overhead with both hands as if placing an item on a high shelf. | `__NO__` |
| `hrb_042` | `manipulation_stance` | `reach_low_forward` | Reach down and forward with both hands without moving the feet. | `__NO__` |
| `hrb_043` | `manipulation_stance` | `wipe_table` | Stand in place and wipe a horizontal table surface with the right hand. | `__NO__` |
| `hrb_044` | `manipulation_stance` | `hammer_down` | Stand with feet planted and swing the right hand downward as if using a hammer. | `__NO__` |
| `hrb_045` | `manipulation_stance` | `screwdriver_twist` | Hold both hands near the chest and make a two-handed twisting screwdriver motion. | `__NO__` |
| `hrb_046` | `manipulation_stance` | `press_panel_sequence` | Press three imaginary buttons from left to right on a waist-high panel. | `__NO__` |
| `hrb_047` | `manipulation_stance` | `sort_bins` | Shift weight left and right while moving imaginary objects between waist-high bins. | `__NO__` |
| `hrb_048` | `manipulation_stance` | `lean_left_reach` | Lean left and reach the left hand outward while keeping both feet planted. | `__NO__` |
| `hrb_049` | `manipulation_stance` | `lean_right_reach` | Lean right and reach the right hand outward while keeping both feet planted. | `__NO__` |
| `hrb_050` | `manipulation_stance` | `scan_package` | Stand at a table and move both hands around a package as if scanning it. | `__NO__` |
| `hrb_051` | `loco_manipulation` | `carry_box_front` | Walk forward while carrying a small box with both hands at chest height. | `__NO__` |
| `hrb_052` | `loco_manipulation` | `carry_bag_right` | Walk forward while carrying a bag low in the right hand. | `__NO__` |
| `hrb_053` | `loco_manipulation` | `tray_walk` | Walk carefully while keeping both hands level as if holding a tray. | `__NO__` |
| `hrb_054` | `loco_manipulation` | `push_cart` | Walk forward with both hands extended as if pushing a cart. | `__NO__` |
| `hrb_055` | `loco_manipulation` | `pull_cart_backward` | Walk backward with both hands forward as if pulling a cart toward the robot. | `__NO__` |
| `hrb_056` | `loco_manipulation` | `open_door` | Step forward, reach with the right hand as if opening a door, then pass through. | `__NO__` |
| `hrb_057` | `loco_manipulation` | `close_door` | Turn slightly, pull the right hand back as if closing a door, then stand balanced. | `__NO__` |
| `hrb_058` | `loco_manipulation` | `handoff_give` | Step forward and extend both hands as if handing over an object. | `__NO__` |
| `hrb_059` | `loco_manipulation` | `handoff_receive` | Step forward and present both hands to receive an object. | `__NO__` |
| `hrb_060` | `loco_manipulation` | `drag_object` | Lean back slightly and pull an imaginary heavy object with both hands. | `__NO__` |
| `hrb_061` | `loco_manipulation` | `carry_turn` | Carry an imaginary box, turn left, and continue walking. | `__NO__` |
| `hrb_062` | `loco_manipulation` | `inspect_machine` | Walk to a machine, lean in slightly, and inspect it with hands behind the back. | `__NO__` |
| `hrb_063` | `loco_manipulation` | `open_drawer` | Step forward, reach low with both hands, and pull as if opening a drawer. | `__NO__` |
| `hrb_064` | `loco_manipulation` | `loaded_recovery_step` | Walk forward carrying a load and take a corrective step after a small imbalance. | `__NO__` |
| `hrb_065` | `balance_recovery` | `single_leg_balance_right` | Balance briefly on the right leg while lifting the left knee. | `__NO__` |
| `hrb_066` | `balance_recovery` | `single_leg_balance_left` | Balance briefly on the left leg while lifting the right knee. | `__NO__` |
| `hrb_067` | `balance_recovery` | `stumble_forward` | Recover from a small forward stumble with one quick corrective step. | `__NO__` |
| `hrb_068` | `balance_recovery` | `stumble_left` | Recover from a small leftward stumble with a side step. | `__NO__` |
| `hrb_069` | `balance_recovery` | `stumble_right` | Recover from a small rightward stumble with a side step. | `__NO__` |
| `hrb_070` | `balance_recovery` | `backward_recovery` | Recover from a slight backward lean by stepping back. | `__NO__` |
| `hrb_071` | `balance_recovery` | `ankle_sway` | Stand still and sway gently forward and backward without stepping. | `__NO__` |
| `hrb_072` | `balance_recovery` | `hip_strategy` | Stand still and make a larger torso balance correction without moving the feet. | `__NO__` |
| `hrb_073` | `balance_recovery` | `toe_stand` | Rise briefly onto the toes and return to flat feet. | `__NO__` |
| `hrb_074` | `balance_recovery` | `heel_rock` | Rock back briefly onto the heels and return to normal standing. | `__NO__` |
| `hrb_075` | `balance_recovery` | `catch_balance_arms` | Lift both arms outward to regain balance after a small perturbation. | `__NO__` |
| `hrb_076` | `balance_recovery` | `narrow_stance_hold` | Hold a narrow stance while making small balance corrections with the arms. | `__NO__` |
| `hrb_077` | `communication_safety` | `wave` | Stand still and wave the right hand at shoulder height. | `__PARTIAL__` |
| `hrb_078` | `communication_safety` | `stop_signal` | Take one step forward and raise the right palm in a stop signal. | `__NO__` |
| `hrb_079` | `communication_safety` | `point_left` | Point clearly to the robot's left with the left arm while standing. | `__PARTIAL__` |
| `hrb_080` | `communication_safety` | `point_right` | Point clearly to the robot's right with the right arm while standing. | `__PARTIAL__` |
| `hrb_081` | `communication_safety` | `beckon` | Stand and make a beckoning motion with the right hand. | `__PARTIAL__` |
| `hrb_082` | `communication_safety` | `yield_step` | Step backward and raise both hands slightly as a yielding gesture. | `__PARTIAL__` |
| `hrb_083` | `communication_safety` | `look_around` | Stand still and look left, right, then forward. | `__PARTIAL__` |
| `hrb_084` | `communication_safety` | `direct_traffic` | Stand and sweep the right arm sideways as if directing someone to pass. | `__PARTIAL__` |
| `hrb_085` | `terrain_obstacle` | `step_over_right` | Step over a low imaginary obstacle with the right foot first. | `__NO__` |
| `hrb_086` | `terrain_obstacle` | `step_over_left` | Step over a low imaginary obstacle with the left foot first. | `__NO__` |
| `hrb_087` | `terrain_obstacle` | `high_step_cables` | Walk forward using high steps as if crossing scattered cables. | `__NO__` |
| `hrb_088` | `terrain_obstacle` | `duck_under_bar` | Crouch slightly while walking under a low bar, then return upright. | `__NO__` |
| `hrb_089` | `terrain_obstacle` | `slope_up` | Walk forward as if climbing a shallow ramp with a slight forward lean. | `__NO__` |
| `hrb_090` | `terrain_obstacle` | `slope_down` | Walk forward as if descending a shallow ramp with cautious short steps. | `__NO__` |
| `hrb_091` | `terrain_obstacle` | `swerve_left` | Walk forward and swerve gently left around an obstacle. | `__NO__` |
| `hrb_092` | `terrain_obstacle` | `tight_turn_back` | Walk forward, make a compact one-hundred-eighty-degree turn, and walk back. | `__NO__` |
| `hrb_093` | `athletic_stress` | `cartwheel_attempt` | Attempt a slow cartwheel-like lateral inversion and recover to standing. | `__NO__` |
| `hrb_094` | `athletic_stress` | `forward_roll` | Perform a controlled forward roll and return to a kneeling posture. | `__NO__` |
| `hrb_095` | `athletic_stress` | `burpee` | Squat down, kick the legs back to a plank, return the feet under the body, and stand. | `__NO__` |
| `hrb_096` | `athletic_stress` | `sprawl_recovery` | Drop quickly into a sprawl and recover to an athletic stance. | `__NO__` |
| `hrb_097` | `athletic_stress` | `split_squat_jump` | Perform a small split-squat jump switching which foot is forward. | `__NO__` |
| `hrb_098` | `athletic_stress` | `knee_slide` | Slide forward briefly on both knees and recover to kneeling. | `__NO__` |
| `hrb_099` | `athletic_stress` | `side_roll_recovery` | Roll sideways on the floor and recover to a crouched stance. | `__NO__` |
| `hrb_100` | `athletic_stress` | `handstand_kickup` | Kick up toward a brief handstand and return the feet to the floor. | `__NO__` |
