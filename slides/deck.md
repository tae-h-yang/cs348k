---
marp: true
theme: cs348k
paginate: true
size: 16:9
style: |
  section { font-size: 23px; }
---

<!-- _class: title -->

# Physical Awareness for Generated Humanoid Motion

A test-time physical audit and prompt-refinement loop for humanoid reference motions

CS348K Final Project  
Tae Hoon Yang

---

## Major Advances in Humanoid Motion Tracking

<div class="cols">

<div>

Modern humanoid trackers can follow high-quality motion clips in physics.

SONIC trains on over 100M frames / 700 hours of high-quality human motion.

The paper describes these motions as retargeted to the humanoid before tracking.

<div class="metric">

Tracking is getting strong. Where do these reference motions come from?

</div>

</div>

<div>

<img class="paper-figure" src="assets/figures/sonic_motion_dataset_samples.jpg" alt="SONIC motion dataset samples" />

<div class="hero-video small-video">

<video src="https://nvlabs.github.io/GEAR-SONIC/static/videos/teaser_title.mp4" poster="assets/video_posters/sonic_official.jpg" autoplay muted loop playsinline preload="metadata"></video>

</div>

</div>

</div>

<div class="refs"><p>Luo et al., "SONIC: Supersizing Motion Tracking for Natural Humanoid Whole-Body Control"</p></div>

---

## KIMODO Makes References Easy To Generate

<div class="cols">

<div class="tight">

KIMODO generates G1 reference motions from text and kinematic constraints.

It is trained on 700 hours of production-quality optical mocap.

This gives us a broad 100-prompt humanoid reference-motion suite.

But kinematic generation does not by itself guarantee:

- feasible torques,
- valid support contacts,
- prompt correctness,
- trackability by a learned controller.

<div class="metric">

We insert a physical-awareness prompt-refinement loop after KIMODO and before tracking.

</div>

</div>

<div class="hero-video">

<video src="assets/videos/kimodo_official/kimodo_g1_text_loco.mp4" poster="assets/video_posters/kimodo_official/kimodo_g1_text_loco.jpg" autoplay muted loop playsinline preload="metadata"></video>

</div>

</div>

<div class="refs"><p>Rempe et al., "Kimodo: Scaling Controllable Human Motion Generation"</p></div>

---

## What Exactly Are We Refining?

<div class="cols">

<div>

We refine the prompt with an LLM guided by failures observed in the generated G1 trajectory.

Each clip contains root pose and joint angles over time.

From each generated clip, we derive:

- velocity and acceleration,
- contact diagnostics,
- SONIC tracking diagnostics.

A prompt can produce a plausible replay and still need a safer rewrite.

</div>

<div class="visual-card">

<video src="assets/videos/kimodo_failures_selected/trackability__hrb_001_forward_walk__sonic_fell3p46s_torque4p29x_rootforce6593N.mp4" poster="assets/video_posters/kimodo_failures_selected/trackability__hrb_001_forward_walk__sonic_fell3p46s_torque4p29x_rootforce6593N.jpg" autoplay muted loop playsinline preload="metadata" style="width:100%; max-height:330px; background:#101820; border:1px solid #cfd8df;"></video>

<div class="caption">Local G1 example: the reference replay looks plausible, but the physics rollout becomes unstable. This failure tag becomes structured context for the next prompt rewrite.</div>

</div>

</div>

<!-- <div class="metric">

Project question: can metric failures guide useful LLM prompt rewrites before rollout?

</div> -->

<!-- <div class="refs"><p>KIMODO reference replayed through SONIC in MuJoCo; public G1 failure videos motivate the same physical-awareness question.</p></div> -->

---
<!-- 
## Evaluation Questions

Success has to be measured twice: first on the reference, then in the controller.

We ask four questions:

- How many first-pass KIMODO references pass physical rules?
- Which failure tags should drive LLM prompt rewrites?
- Do refined or lower-risk references survive longer under SONIC?
- Which clips pass both physical rules and controller rollout?

Metric definitions:

- **physical pass:** torque/root-wrench, contact, and support thresholds,
- **SONIC no-fall:** full-horizon controller rollout,
- **RMSE:** joint tracking error,
- **failure tag:** structured context for the LLM prompt rewriter.

<div class="refs"><p>Araujo et al., "Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking," arXiv:2510.02252.</p></div>

--- -->

## What We Built

<div class="cols tight">

<div>

### Baseline

- one generated clip per prompt,
- KIMODO G1 reference trajectory,
- no test-time refinement loop.

</div>

<div>

### Our Layer: Prompt Refinement

- generate a KIMODO reference,
- check dynamics/contact/support rules,
- run SONIC for rollout evidence,
- send failure tags to GPT-5.5,
- regenerate from the rewritten prompt.

</div>

</div>

---

## Method: Prompt Refinement Loop

<div class="pipeline">
  <div class="step"><strong>1. Generate</strong><span>KIMODO reference from the current text prompt</span></div>
  <div class="step"><strong>2. Evaluate</strong><span>rules on the reference plus SONIC rollout checks</span></div>
  <div class="step"><strong>3. LLM Rewrite</strong><span>GPT-5.5 adds a tag-specific safety constraint</span></div>
  <div class="step"><strong>4. Repeat / Gate</strong><span>regenerate until no flag or the sample budget ends</span></div>
</div>

<!-- <div class="metric">

The evaluator is not just a score: it tells the LLM what constraint to add.

</div> -->

<small>GPT-5.5 edits the prompt; physics rules and SONIC decide whether the new reference passes.</small>

---

<!-- _class: compact -->

## Refinement: LLM Prompt Repair

When a candidate fails, the failed metric becomes structured context for GPT-5.5.

Then we regenerate candidates and score again.

| Failure tag | Constraint given to GPT-5.5 before resampling |
|---|---|
| high torque / root wrench | slower, smoother limb motion; avoid abrupt arm swings or snaps |
| self-contact | keep arms away from torso; avoid crossing legs or shoulders |
| non-foot floor contact | use feet-only support unless the task explicitly says crawl or kneel |
| support proxy | wider stance; planted support foot; smaller center-of-mass shift |
| contact artifact | clean foot placement; avoid dragging or sliding contacts |
| trackability failure | reduce speed and amplitude; make transitions gradual |

<div class="metric">

The rewrite stays interpretable: every new prompt is tied to the metric that failed.

</div>

<div class="refs"><p>Araujo et al., "Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking," arXiv:2510.02252.</p></div>

---

<!-- _class: compact -->

## 100-Prompt Humanoid Suite

KIMODO can attempt the full prompt suite directly on the G1 skeleton.

We use concrete text prompts, not just motion labels.

<div class="warn"><strong>Benchmark caveat:</strong> some prompts are beyond current tracker capability, so failure is useful evidence rather than just a bad generation.</div>

| Family | Count | Example text prompts |
|---|---:|---|
| locomotion + recovery | 26 | "Walk forward at a comfortable indoor pace." |
| manipulation + loco-manipulation | 26 | "Step forward, reach with the right hand as if opening a door." |
| floor / low posture | 12 | "Crawl forward using hands and feet." |
| dance / expressive | 12 | "Do an energetic happy dance with bouncing knees." |
| athletic + terrain stress | 16 | "Perform a small split-squat jump." |
| communication / safety | 8 | "Stand still and wave the right hand at shoulder height." |

---

## Generated Reference Examples

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/kimodo_reference_family_examples/hrb_001_forward_walk_forward_walk_reference.mp4" poster="assets/video_posters/kimodo_reference_family_examples/hrb_001_forward_walk_forward_walk_reference.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>locomotion + recovery</strong><br/>forward_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_reference_family_examples/hrb_056_open_door_open_door_reference.mp4" poster="assets/video_posters/kimodo_reference_family_examples/hrb_056_open_door_open_door_reference.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>manipulation + loco-manipulation</strong><br/>open_door</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_reference_family_examples/hrb_027_hand_crawl_hand_crawl_reference.mp4" poster="assets/video_posters/kimodo_reference_family_examples/hrb_027_hand_crawl_hand_crawl_reference.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>floor / low posture</strong><br/>hand_crawl</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_reference_family_examples/hrb_018_happy_dance_happy_dance_reference.mp4" poster="assets/video_posters/kimodo_reference_family_examples/hrb_018_happy_dance_happy_dance_reference.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>dance / expressive</strong><br/>happy_dance</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_reference_family_examples/hrb_097_split_squat_jump_split_squat_jump_reference.mp4" poster="assets/video_posters/kimodo_reference_family_examples/hrb_097_split_squat_jump_split_squat_jump_reference.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>athletic + terrain stress</strong><br/>split_squat_jump</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_reference_family_examples/hrb_077_wave_wave_reference.mp4" poster="assets/video_posters/kimodo_reference_family_examples/hrb_077_wave_wave_reference.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>communication / safety</strong><br/>wave</p>
</div>

</div>

<div class="caption">Reference-only KIMODO outputs rendered on the G1 mesh. No physics rollout is shown on this slide.</div>

---

## First-Pass References Can Already Track

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_008_broad_jump__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_008_broad_jump__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>broad_jump</strong><br/>physical pass + SONIC no-fall</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_030_crab_walk__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_030_crab_walk__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>crab_walk</strong><br/>physical pass + SONIC no-fall</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_043_wipe_table__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_043_wipe_table__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>wipe_table</strong><br/>physical pass + SONIC no-fall</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_080_point_right__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_080_point_right__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>point_right</strong><br/>physical pass + SONIC no-fall</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_041_reach_overhead__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_041_reach_overhead__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>reach_overhead</strong><br/>physical pass + SONIC no-fall</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/contact_support__hrb_007_vertical_jump.mp4" poster="assets/video_posters/appendix_metric_failures/contact_support__hrb_007_vertical_jump.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>vertical_jump</strong><br/>physical pass + SONIC no-fall</p>
</div>

</div>

<div class="caption">Five generated references pass the physical rules and complete SONIC immediately; Red ghost = reference; solid G1 = controller rollout.</div>

---

<!-- _class: compact -->

## First-Pass KIMODO Audit

<div class="result-grid">

<div>

![kimodo audit summary](assets/figures/kimodo_audit_summary.png)

</div>

<div>

| Set | Physical Pass | SONIC No-Fall | Mean SONIC Sec. | Mean RMSE |
|---|---:|---:|---:|---:|
| all KIMODO refs | 48/100 | 53/100 | 2.855 | 0.156 |
| physical-pass subset | 48/48 | 29/48 | 3.293 | 0.170 |
| flagged subset | 0/52 | 24/52 | 2.450 | 0.143 |

<div class="metric">Controller check: 29/48 physical-pass references also complete SONIC; flagged references complete less often and track for less time.</div>

</div>

</div>

<div class="caption">Full 100-prompt KIMODO run. Failure tags identify references that need prompt repair before resampling.</div>

---

## Generated Failure Modes

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/torque_demand__hrb_094_forward_roll.mp4" poster="assets/video_posters/presentation_failure_modes/torque_demand__hrb_094_forward_roll__late.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>Torque/root wrench</strong><br/>forward_roll, 16.7x</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failures_selected/self_contact__hrb_005_turn_in_place__selfcontact75pct_torque18p86x.mp4" poster="assets/video_posters/presentation_failure_modes/self_contact__hrb_005_turn_in_place__selfcontact75pct_torque18p86x__late.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>Self-contact</strong><br/>turn_in_place</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/nonfoot_floor__hrb_098_knee_slide.mp4" poster="assets/video_posters/presentation_failure_modes/nonfoot_floor__hrb_098_knee_slide__late.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>Non-foot floor</strong><br/>knee_slide</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/support_proxy__hrb_085_step_over_right__support14pct.mp4" poster="assets/video_posters/presentation_failure_modes/support_proxy__hrb_085_step_over_right__support14pct__late.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>Support proxy</strong><br/>step_over_right</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/trackability__hrb_051_carry_box__fell2p78s.mp4" poster="assets/video_posters/presentation_failure_modes/trackability__hrb_051_carry_box__fell2p78s__late.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>Trackability</strong><br/>carry_box</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/contact_support__hrb_018_happy_dance.mp4" poster="assets/video_posters/presentation_failure_modes/contact_support__hrb_018_happy_dance__late.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>Contact artifact</strong><br/>happy_dance</p>
</div>

</div>

<div class="caption">KIMODO references replayed through SONIC. Red ghost = reference; solid G1 = rollout. Failure labels come from metrics.</div>

---

<!-- _class: compact failure-stats-slide -->

## Failure Stats Across 100 KIMODO Clips

<div class="failure-stats-layout">

<div class="failure-summary">
  <div class="failure-stat">
    <strong>52</strong>
    <span>physical-rule fail</span>
  </div>
  <div class="failure-stat">
    <strong>47</strong>
    <span>SONIC fall</span>
  </div>
  <div class="failure-stat">
    <strong>48</strong>
    <span>torque limit &gt;1x</span>
  </div>
</div>

<p>Failure flags are non-exclusive: one clip can violate actuation, contact, and controller tracking.</p>

<div class="failure-bars">
  <div class="failure-bar" style="--value:52"><span>physical-rule fail</span><b>52</b></div>
  <div class="failure-bar" style="--value:47"><span>SONIC fall</span><b>47</b></div>
  <div class="failure-bar" style="--value:48"><span>torque limit &gt;1x</span><b>48</b></div>
  <div class="failure-bar" style="--value:34"><span>self-contact &gt;8%</span><b>34</b></div>
  <div class="failure-bar" style="--value:31"><span>unstable center of mass</span><b>31</b></div>
  <div class="failure-bar" style="--value:28"><span>high root force &gt;5kN</span><b>28</b></div>
  <div class="failure-bar" style="--value:11"><span>non-foot floor contact</span><b>11</b></div>
</div>

</div>

---

<!-- _class: compact repair-improvement-slide -->

## Prompt Repair Reduces Failure Tags

<div class="repair-improvement">

<div class="repair-hero">
  <span>SONIC fall</span>
  <strong>47 &rarr; 20</strong>
  <em>27 fewer fall cases; mean repair depth 3.4 iterations</em>
</div>

<div class="repair-rows">
  <div class="repair-row" style="--before:48; --after:23">
    <span class="repair-label">torque limit &gt;1x</span>
    <span class="repair-count">48 &rarr; 23</span>
    <span class="repair-delta">-25</span>
    <span class="repair-iters">avg 3 iters</span>
  </div>
  <div class="repair-row" style="--before:34; --after:10">
    <span class="repair-label">self-contact &gt;8%</span>
    <span class="repair-count">34 &rarr; 10</span>
    <span class="repair-delta">-24</span>
    <span class="repair-iters">avg 5 iters</span>
  </div>
  <div class="repair-row" style="--before:31; --after:20">
    <span class="repair-label">unstable center of mass</span>
    <span class="repair-count">31 &rarr; 20</span>
    <span class="repair-delta">-11</span>
    <span class="repair-iters">avg 4 iters</span>
  </div>
  <div class="repair-row" style="--before:28; --after:9">
    <span class="repair-label">high root force &gt;5kN</span>
    <span class="repair-count">28 &rarr; 9</span>
    <span class="repair-delta">-19</span>
    <span class="repair-iters">avg 3 iters</span>
  </div>
  <div class="repair-row" style="--before:11; --after:4">
    <span class="repair-label">non-foot floor contact</span>
    <span class="repair-count">11 &rarr; 4</span>
    <span class="repair-delta">-7</span>
    <span class="repair-iters">avg 2 iters</span>
  </div>
</div>

</div>

<div class="caption">Counts are failure-tag counts before and after metric-guided prompt repair. Tags are non-exclusive, so reductions do not sum to the SONIC-fall reduction.</div>

---

<!-- _class: compact -->

## Real Repair Rescues

<!-- <div class="metric"><strong>Experiment-video convention:</strong> red translucent G1 is the reference target; solid G1 is the MuJoCo/SONIC physics rollout. Official background videos earlier use their original project colors.</div> -->

<div class="video-grid three">

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues_presentation/rescue_preview__dynamic_locomotion__hrb_001_forward_walk__trim_end1s.mp4" poster="assets/video_posters/kimodo_repair_rescues_presentation/rescue_preview__dynamic_locomotion__hrb_001_forward_walk__trim_end1s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>forward_walk</strong><br/>caught: trackability<br/>prompt: slower, smoother steps</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__communication_safety__hrb_077_wave__3p86s_to_4p00s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__communication_safety__hrb_077_wave__3p86s_to_4p00s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>wave</strong><br/>caught: torque / tracking<br/>prompt: planted feet, smooth arm</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues_presentation/rescue_preview__athletic_stress__hrb_097_split_squat_jump__trim_end1s.mp4" poster="assets/video_posters/kimodo_repair_rescues_presentation/rescue_preview__athletic_stress__hrb_097_split_squat_jump__trim_end1s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>split_squat_jump</strong><br/>caught: support / torque<br/>prompt: smaller jump, soft landing</p>
</div>

</div>
<!-- 
<div class="caption">Three representative repair previews; the full seven-case gallery is in the appendix. Left side is original KIMODO, right side is repaired. Within each panel: red ghost = reference; solid G1 = physics rollout.</div> -->

---

<!-- _class: compact -->

## More Repair Rescues

<div class="video-grid three">

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/pushup_pose_height_offset_demo.mp4" poster="assets/video_posters/kimodo_repair_rescues/pushup_pose_height_offset_demo.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>pushup_pose</strong><br/>caught: non-foot floor<br/>prompt: lift torso clearance</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dance_expressive/repair_delta__hrb_018_happy_dance__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/dance_expressive/repair_delta__hrb_018_happy_dance__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>happy_dance</strong><br/>caught: contact artifact<br/>prompt: clean foot placement</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__balance_recovery__hrb_070_backward_recovery__3p38s_to_4p00s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__balance_recovery__hrb_070_backward_recovery__3p38s_to_4p00s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>backward_recovery</strong><br/>caught: support proxy<br/>prompt: smaller lean, step back</p>
</div>

</div>
<!-- 
<div class="caption">Additional repair examples for non-foot-floor, contact-artifact, and support-proxy cases. Red ghost = reference; solid G1 = rollout/proxy.</div> -->

---
<!-- 
## Physical-Pass No-Fall Examples

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_008_broad_jump__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_008_broad_jump__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>broad_jump</strong><br/>physical pass + no fall</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_030_crab_walk__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_030_crab_walk__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>crab_walk</strong><br/>physical pass + no fall</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_043_wipe_table__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_043_wipe_table__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>wipe_table</strong><br/>physical pass + no fall</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_065_single_leg_balance_right__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_065_single_leg_balance_right__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>single_leg_balance</strong><br/>physical pass + no fall</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_080_point_right__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_080_point_right__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>point_right</strong><br/>physical pass + no fall</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_selected/success__hrb_086_step_over_left__physical_pass_sonic_no_fall.mp4" poster="assets/video_posters/kimodo_success_selected/success__hrb_086_step_over_left__physical_pass_sonic_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>step_over_left</strong><br/>physical pass + no fall</p>
</div>

</div>

<div class="caption">These pass the physical rules and complete SONIC without fall. Red ghost = reference; solid G1 = rollout.</div> -->

<!-- --- -->

<!-- _class: compact -->

## Boundary: What Still Fails

<div class="video-grid three">

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/torque_demand__hrb_094_forward_roll.mp4" poster="assets/video_posters/appendix_metric_failures/torque_demand__hrb_094_forward_roll.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>forward_roll</strong><br/>torque/root wrench</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/sonic_trackability__hrb_051_carry_box.mp4" poster="assets/video_posters/appendix_metric_failures/sonic_trackability__hrb_051_carry_box.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>carry_box</strong><br/>controller trackability</p>
</div>

<div class="video-card">
<video src="assets/videos/boundary_still_fails/cartwheel_attempt_repaired_right.mp4" poster="assets/video_posters/boundary_still_fails/cartwheel_attempt_repaired_right.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>cartwheel_attempt</strong><br/>torque/root wrench</p>
</div>

</div>

<div class="warn">Still unsolved: arbitrary text-to-robot motion; robust acrobatics and low postures; automatic repair for every invalid reference.</div>

<!-- <div class="caption">Failed runs remain useful evidence. Visual/VLM checks help catch obvious behavior mismatch, but the final labels come from physics metrics and SONIC rollout.</div> -->

---

<!-- _class: compact limitations-slide -->

## Limitations

<div class="limit-grid">

<div class="limit-card">
<strong>Prompt repair is useful, not enough</strong>
<span>Given our failure metrics, the LLM can produce reasonable prompt edits. Stronger text-to-motion stability likely needs fine-tuning the generation model itself.</span>
</div>

<div class="limit-card">
<strong>Tracker-as-foundation is an assumption</strong>
<span>We treat SONIC as a foundation motion tracker, but uncovered motions remain a weak point. Dataset coverage still matters.</span>
</div>

<div class="limit-card">
<strong>Trackability is still hard to certify</strong>
<span>If a generated reference fails, deciding whether RL could learn to track it is a harder problem than our test-time metric screen.</span>
</div>

<div class="limit-card">
<strong>Iteration has deployment cost</strong>
<span>Prompt repair takes extra test-time iterations, but catching infeasible motion before controller execution is still important for real-world deployment.</span>
</div>

</div>

<div class="metric">Main point: metric-guided prompt refinement can reject or improve generated references, but it does not replace better generators, broader tracker training, or deployment-time safety checks.</div>

<!-- APPENDIX DISABLED FOR FAST MAIN BUILD

---

<!~~ _class: compact ~~>

## Appendix: No-Fall Candidate Gallery A

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_071_ankle_sway__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_071_ankle_sway__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>balance</strong><br/>ankle_sway</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_075_catch_balance_arms__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_075_catch_balance_arms__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>balance</strong><br/>catch_balance</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_016_moonwalk__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_016_moonwalk__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>dance</strong><br/>moonwalk</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_021_celebration_pump__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_021_celebration_pump__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>dance</strong><br/>celebration</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_054_push_cart__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_054_push_cart__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>loco-manip.</strong><br/>push_cart</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_057_close_door__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_057_close_door__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>loco-manip.</strong><br/>close_door</p>
</div>

</div>

<div class="caption">Additional KIMODO clips that pass the physical rules and complete the SONIC rollout. Red ghost = reference; solid G1 = rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: No-Fall Candidate Gallery B

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_058_handoff_give__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_058_handoff_give__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>loco-manip.</strong><br/>handoff_give</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_041_reach_overhead__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_041_reach_overhead__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>manipulation</strong><br/>reach_overhead</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_045_screwdriver_twist__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_045_screwdriver_twist__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>manipulation</strong><br/>screwdriver</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_050_scan_package__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_050_scan_package__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>manipulation</strong><br/>scan_package</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_082_yield_step__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_082_yield_step__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>communication</strong><br/>yield_step</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_success_candidates_review/success__hrb_087_high_step_cables__physical_pass_no_fall.mp4" poster="assets/video_posters/kimodo_success_candidates_review/success__hrb_087_high_step_cables__physical_pass_no_fall.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>terrain</strong><br/>high_step</p>
</div>

</div>

<div class="caption">Second no-fall candidate pool. Same red-ghost/solid-G1 convention; all clips complete the rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Failure Candidate Gallery A

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/torque_root__hrb_002_backward_walk__root7353N.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/torque_root__hrb_002_backward_walk__root7353N.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>torque/root</strong><br/>backward_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/self_contact__hrb_046_press_panel__self73pct.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/self_contact__hrb_046_press_panel__self73pct.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>self-contact</strong><br/>press_panel</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/support_artifact__hrb_018_happy_dance__artifact0p57.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/support_artifact__hrb_018_happy_dance__artifact0p57.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>contact artifact</strong><br/>happy_dance</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/torque_root__hrb_053_tray_walk__root11211N.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/torque_root__hrb_053_tray_walk__root11211N.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>torque/root</strong><br/>tray_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/self_contact__hrb_079_point_left__self100pct.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/self_contact__hrb_079_point_left__self100pct.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>self-contact</strong><br/>point_left</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/contact_artifact__hrb_088_duck_under_bar__artifact0p55.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/contact_artifact__hrb_088_duck_under_bar__artifact0p55.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>contact artifact</strong><br/>duck_under_bar</p>
</div>

</div>

<div class="caption">Review pool for choosing the final six failure examples. Same red-ghost/solid-G1 convention; none are one-frame early-termination examples.</div>

---

<!~~ _class: compact ~~>

## Appendix: Failure Candidate Gallery B

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/torque_root__hrb_048_lean_left_reach__root5616N.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/torque_root__hrb_048_lean_left_reach__root5616N.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>torque/root</strong><br/>lean_left_reach</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/self_contact__hrb_076_narrow_stance__self100pct.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/self_contact__hrb_076_narrow_stance__self100pct.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>self-contact</strong><br/>narrow_stance</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/support_proxy__hrb_085_step_over_right__support14pct.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/support_proxy__hrb_085_step_over_right__support14pct.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>support proxy</strong><br/>step_over_right</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/torque__hrb_025_air_guitar__torque2p96x.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/torque__hrb_025_air_guitar__torque2p96x.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>torque</strong><br/>air_guitar</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/self_contact__hrb_066_single_leg_balance_left__self40pct.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/self_contact__hrb_066_single_leg_balance_left__self40pct.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>self-contact</strong><br/>single_leg_balance</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_failure_candidates_review/trackability__hrb_051_carry_box__fell2p78s.mp4" poster="assets/video_posters/kimodo_failure_candidates_review/trackability__hrb_051_carry_box__fell2p78s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>trackability</strong><br/>carry_box</p>
</div>

</div>

<div class="caption">Second review pool. Same red-ghost/solid-G1 convention; avoid confusing intended low posture with failure.</div>

---

<!~~ _class: compact ~~>

## Appendix: Torque Demand Failures

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/torque_demand__hrb_062_inspect_machine.mp4" poster="assets/video_posters/appendix_metric_failures/torque_demand__hrb_062_inspect_machine.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>torque 12.8x</strong><br/>hrb_062 inspect_machine</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/torque_demand__hrb_025_air_guitar.mp4" poster="assets/video_posters/appendix_metric_failures/torque_demand__hrb_025_air_guitar.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>torque 3.0x</strong><br/>hrb_025 air_guitar</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/torque_demand__hrb_094_forward_roll.mp4" poster="assets/video_posters/appendix_metric_failures/torque_demand__hrb_094_forward_roll.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>torque 16.7x</strong><br/>hrb_094 forward_roll</p>
</div>

</div>

<div class="caption">Three real KIMODO references selected by the named metric. Red ghost = reference; solid G1 = physics rollout. Full horizon is rendered to avoid confusing low postures with early termination.</div>

---

<!~~ _class: compact ~~>

## Appendix: Root Wrench Failures

<div class="video-grid three">

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/root_wrench__hrb_002_backward_walk.mp4" poster="assets/video_posters/appendix_metric_failures/root_wrench__hrb_002_backward_walk.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>root 7353N</strong><br/>hrb_002 backward_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/root_wrench__hrb_053_tray_walk.mp4" poster="assets/video_posters/appendix_metric_failures/root_wrench__hrb_053_tray_walk.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>root 11211N</strong><br/>hrb_053 tray_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/root_wrench__hrb_089_slope_up.mp4" poster="assets/video_posters/appendix_metric_failures/root_wrench__hrb_089_slope_up.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>root 7350N</strong><br/>hrb_089 slope_up</p>
</div>

</div>

<div class="caption">Three real KIMODO references selected by the named metric. Red ghost = reference; solid G1 = physics rollout. Full horizon is rendered to avoid confusing low postures with early termination.</div>

---

<!~~ _class: compact ~~>

## Appendix: Self-Contact Failures

<div class="video-grid three">

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/self_contact__hrb_005_turn_in_place.mp4" poster="assets/video_posters/appendix_metric_failures/self_contact__hrb_005_turn_in_place.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>75% frames</strong><br/>hrb_005 turn_in_place</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/self_contact__hrb_046_press_panel.mp4" poster="assets/video_posters/appendix_metric_failures/self_contact__hrb_046_press_panel.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>73% frames</strong><br/>hrb_046 press_panel</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/self_contact__hrb_079_point_left.mp4" poster="assets/video_posters/appendix_metric_failures/self_contact__hrb_079_point_left.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>100% frames</strong><br/>hrb_079 point_left</p>
</div>

</div>

<div class="caption">Three real KIMODO references selected by the named metric. Red ghost = reference; solid G1 = physics rollout. Full horizon is rendered to avoid confusing low postures with early termination.</div>

---

<!~~ _class: compact ~~>

## Appendix: Non-Foot Floor Contact Failures

<div class="video-grid three">

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/nonfoot_floor__hrb_027_hand_crawl.mp4" poster="assets/video_posters/appendix_metric_failures/nonfoot_floor__hrb_027_hand_crawl.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>100% frames</strong><br/>hrb_027 hand_crawl</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/nonfoot_floor__hrb_028_elbow_crawl.mp4" poster="assets/video_posters/appendix_metric_failures/nonfoot_floor__hrb_028_elbow_crawl.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>100% frames</strong><br/>hrb_028 elbow_crawl</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/nonfoot_floor__hrb_098_knee_slide.mp4" poster="assets/video_posters/appendix_metric_failures/nonfoot_floor__hrb_098_knee_slide.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>78% frames</strong><br/>hrb_098 knee_slide</p>
</div>

</div>

<div class="caption">Three real KIMODO references selected by the named metric. Red ghost = reference; solid G1 = physics rollout. Full horizon is rendered to avoid confusing low postures with early termination.</div>

---

<!~~ _class: compact ~~>

## Appendix: Support / Contact Artifact Failures

<div class="video-grid three">

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/contact_support__hrb_007_vertical_jump.mp4" poster="assets/video_posters/appendix_metric_failures/contact_support__hrb_007_vertical_jump.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>support/contact</strong><br/>hrb_007 vertical_jump</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/contact_support__hrb_018_happy_dance.mp4" poster="assets/video_posters/appendix_metric_failures/contact_support__hrb_018_happy_dance.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>contact artifact</strong><br/>hrb_018 happy_dance</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/contact_support__hrb_088_duck_under_bar.mp4" poster="assets/video_posters/appendix_metric_failures/contact_support__hrb_088_duck_under_bar.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>contact artifact</strong><br/>hrb_088 duck_under_bar</p>
</div>

</div>

<div class="caption">Three real KIMODO references selected by the named metric. Red ghost = reference; solid G1 = physics rollout. Full horizon is rendered to avoid confusing low postures with early termination.</div>

---

<!~~ _class: compact ~~>

## Appendix: SONIC Trackability Failures

<div class="video-grid three">

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/sonic_trackability__hrb_001_forward_walk.mp4" poster="assets/video_posters/appendix_metric_failures/sonic_trackability__hrb_001_forward_walk.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>fall marker 3.46s</strong><br/>hrb_001 forward_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/sonic_trackability__hrb_004_side_shuffle_right.mp4" poster="assets/video_posters/appendix_metric_failures/sonic_trackability__hrb_004_side_shuffle_right.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>fall marker 1.72s</strong><br/>hrb_004 side_shuffle_right</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_metric_failures/sonic_trackability__hrb_051_carry_box.mp4" poster="assets/video_posters/appendix_metric_failures/sonic_trackability__hrb_051_carry_box.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>fall marker 2.78s</strong><br/>hrb_051 carry_box</p>
</div>

</div>

<div class="caption">Three real KIMODO references selected by the named metric. Red ghost = reference; solid G1 = physics rollout. Full horizon is rendered to avoid confusing low postures with early termination.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Rescue Candidates A

<div class="video-grid four">

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__dynamic_locomotion__hrb_001_forward_walk__3p46s_to_4p00s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__dynamic_locomotion__hrb_001_forward_walk__3p46s_to_4p00s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>forward_walk</strong><br/>caught: trackability<br/>prompt: slower, smoother steps</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__loco_manipulation__hrb_056_open_door__2p62s_to_4p00s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__loco_manipulation__hrb_056_open_door__2p62s_to_4p00s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>open_door</strong><br/>caught: reach instability<br/>prompt: small step, stable reach</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__balance_recovery__hrb_068_stumble_left__1p92s_to_4p00s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__balance_recovery__hrb_068_stumble_left__1p92s_to_4p00s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>stumble_left</strong><br/>caught: support proxy<br/>prompt: wider recovery step</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__balance_recovery__hrb_069_stumble_right__2p72s_to_4p00s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__balance_recovery__hrb_069_stumble_right__2p72s_to_4p00s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>stumble_right</strong><br/>caught: support proxy<br/>prompt: wider recovery step</p>
</div>

</div>

<div class="caption">Candidate paired videos for visual selection. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Rescue Candidates B

<div class="video-grid three">

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__balance_recovery__hrb_070_backward_recovery__3p38s_to_4p00s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__balance_recovery__hrb_070_backward_recovery__3p38s_to_4p00s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>backward_recovery</strong><br/>caught: support proxy<br/>prompt: smaller lean, step back</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__communication_safety__hrb_077_wave__3p86s_to_4p00s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__communication_safety__hrb_077_wave__3p86s_to_4p00s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>wave</strong><br/>caught: torque / tracking<br/>prompt: planted feet, smooth arm</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__athletic_stress__hrb_097_split_squat_jump__3p42s_to_4p00s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__athletic_stress__hrb_097_split_squat_jump__3p42s_to_4p00s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>split_squat_jump</strong><br/>caught: support / torque<br/>prompt: smaller jump, soft landing</p>
</div>

</div>

<div class="caption">More paired rescue candidates for choosing the clearest presentation clip. Same convention: red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Candidate Gallery A

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_original__dynamic__forward_walk.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_original__dynamic__forward_walk.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>original fail</strong><br/>forward_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_original__loco_manip__open_door.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_original__loco_manip__open_door.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>original fail</strong><br/>open_door</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_original__balance__stumble_left.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_original__balance__stumble_left.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>original fail</strong><br/>stumble_left</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_original__balance__stumble_right.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_original__balance__stumble_right.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>original fail</strong><br/>stumble_right</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_original__communication__wave.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_original__communication__wave.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>original fail</strong><br/>wave</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_original__athletic__split_squat_jump.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_original__athletic__split_squat_jump.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>original fail</strong><br/>split_squat</p>
</div>

</div>

<div class="caption">KIMODO-only original failed references used to verify the repair slide. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Candidate Gallery B

<div class="video-grid six">

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_repaired__dynamic__forward_walk.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_repaired__dynamic__forward_walk.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>repaired</strong><br/>forward_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_repaired__loco_manip__open_door.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_repaired__loco_manip__open_door.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>repaired</strong><br/>open_door</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_repaired__balance__stumble_left.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_repaired__balance__stumble_left.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>repaired</strong><br/>stumble_left</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_repaired__balance__stumble_right.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_repaired__balance__stumble_right.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>repaired</strong><br/>stumble_right</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_repaired__communication__wave.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_repaired__communication__wave.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>repaired</strong><br/>wave</p>
</div>

<div class="video-card">
<video src="assets/videos/kimodo_repair_candidates_review/repair_audit_repaired__athletic__split_squat_jump.mp4" poster="assets/video_posters/kimodo_repair_candidates_review/repair_audit_repaired__athletic__split_squat_jump.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>repaired</strong><br/>split_squat</p>
</div>

</div>

<div class="caption">Matching KIMODO-only repaired references for the same prompts. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Deltas - Dynamic Locomotion

<div class="video-grid five">

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_002_backward_walk__no_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_002_backward_walk__no_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -21.2; NO->YES</strong><br/>hrb_002 backward_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_001_forward_walk__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_001_forward_walk__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -18.4; NO->NO</strong><br/>hrb_001 forward_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_007_vertical_jump__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_007_vertical_jump__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -8.2; NO->NO</strong><br/>hrb_007 vertical_jump</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_012_lateral_bound__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_012_lateral_bound__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -6.5; YES->YES</strong><br/>hrb_012 lateral_bound</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_004_side_shuffle_right__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/dynamic_locomotion/repair_delta__hrb_004_side_shuffle_right__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -6.0; NO->NO</strong><br/>hrb_004 side_shuffle_right</p>
</div>

</div>

<div class="caption">Top five real risk-score reductions in this prompt family. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Deltas - Dance / Expressive

<div class="video-grid five">

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dance_expressive/repair_delta__hrb_018_happy_dance__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/dance_expressive/repair_delta__hrb_018_happy_dance__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -11.7; NO->YES</strong><br/>hrb_018 happy_dance</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dance_expressive/repair_delta__hrb_026_salute_step__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/dance_expressive/repair_delta__hrb_026_salute_step__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -10.6; NO->NO</strong><br/>hrb_026 salute_step</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dance_expressive/repair_delta__hrb_024_scared_sneak__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/dance_expressive/repair_delta__hrb_024_scared_sneak__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -8.8; YES->YES</strong><br/>hrb_024 scared_sneak</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dance_expressive/repair_delta__hrb_022_disco_point__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/dance_expressive/repair_delta__hrb_022_disco_point__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -8.3; NO->NO</strong><br/>hrb_022 disco_point</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/dance_expressive/repair_delta__hrb_016_moonwalk__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/dance_expressive/repair_delta__hrb_016_moonwalk__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -2.9; YES->YES</strong><br/>hrb_016 moonwalk</p>
</div>

</div>

<div class="caption">Top five real risk-score reductions in this prompt family. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Deltas - Floor / Low Posture

<div class="video-grid five">

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_034_pushup_pose__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_034_pushup_pose__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -11.0; YES->YES</strong><br/>hrb_034 pushup_pose</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_029_bear_crawl__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_029_bear_crawl__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -10.4; NO->NO</strong><br/>hrb_029 bear_crawl</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_027_hand_crawl__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_027_hand_crawl__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -6.4; NO->NO</strong><br/>hrb_027 hand_crawl</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_035_sit_to_stand__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_035_sit_to_stand__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -3.1; NO->NO</strong><br/>hrb_035 sit_to_stand</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_036_roll_to_kneel__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/floor_low_posture/repair_delta__hrb_036_roll_to_kneel__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -0.7; NO->NO</strong><br/>hrb_036 roll_to_kneel</p>
</div>

</div>

<div class="caption">Top five real risk-score reductions in this prompt family. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Deltas - Manipulation Stance

<div class="video-grid five">

<div class="video-card">
<video src="assets/videos/kimodo_repair_rescues/rescue__nonfoot_floor__hrb_098_knee_slide__2p40s_to_4p16s.mp4" poster="assets/video_posters/kimodo_repair_rescues/rescue__nonfoot_floor__hrb_098_knee_slide__2p40s_to_4p16s.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>contact artifact; fail->repair</strong><br/>hrb_098 knee_slide</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/manipulation_stance/repair_delta__hrb_043_wipe_table__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/manipulation_stance/repair_delta__hrb_043_wipe_table__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -2.4; YES->YES</strong><br/>hrb_043 wipe_table</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/manipulation_stance/repair_delta__hrb_040_pick_floor_left__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/manipulation_stance/repair_delta__hrb_040_pick_floor_left__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -2.2; NO->NO</strong><br/>hrb_040 pick_floor_left</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/manipulation_stance/repair_delta__hrb_039_pick_floor_right__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/manipulation_stance/repair_delta__hrb_039_pick_floor_right__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -0.3; NO->NO</strong><br/>hrb_039 pick_floor_right</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/manipulation_stance/repair_delta__hrb_049_lean_right_reach__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/manipulation_stance/repair_delta__hrb_049_lean_right_reach__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -0.1; YES->YES</strong><br/>hrb_049 lean_right_reach</p>
</div>

</div>

<div class="caption">Repair-delta examples, with knee_slide included as the clearest contact-artifact / non-foot-floor repair case. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Deltas - Loco-Manipulation

<div class="video-grid five">

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_053_tray_walk__no_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_053_tray_walk__no_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -21.4; NO->YES</strong><br/>hrb_053 tray_walk</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_051_carry_box_front__no_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_051_carry_box_front__no_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -14.6; NO->YES</strong><br/>hrb_051 carry_box_front</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_061_carry_turn__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_061_carry_turn__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -10.9; YES->YES</strong><br/>hrb_061 carry_turn</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_054_push_cart__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_054_push_cart__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -7.4; YES->YES</strong><br/>hrb_054 push_cart</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_062_inspect_machine__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/loco_manipulation/repair_delta__hrb_062_inspect_machine__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -5.9; NO->NO</strong><br/>hrb_062 inspect_machine</p>
</div>

</div>

<div class="caption">Top five real risk-score reductions in this prompt family. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Deltas - Balance Recovery

<div class="video-grid five">

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/balance_recovery/repair_delta__hrb_070_backward_recovery__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/balance_recovery/repair_delta__hrb_070_backward_recovery__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -9.6; YES->YES</strong><br/>hrb_070 backward_recovery</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/balance_recovery/repair_delta__hrb_066_single_leg_balance_left__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/balance_recovery/repair_delta__hrb_066_single_leg_balance_left__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -5.1; NO->NO</strong><br/>hrb_066 single_leg_balance_left</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/balance_recovery/repair_delta__hrb_069_stumble_right__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/balance_recovery/repair_delta__hrb_069_stumble_right__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -2.7; YES->YES</strong><br/>hrb_069 stumble_right</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/balance_recovery/repair_delta__hrb_071_ankle_sway__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/balance_recovery/repair_delta__hrb_071_ankle_sway__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -1.8; YES->YES</strong><br/>hrb_071 ankle_sway</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/balance_recovery/repair_delta__hrb_073_toe_stand__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/balance_recovery/repair_delta__hrb_073_toe_stand__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -1.7; YES->YES</strong><br/>hrb_073 toe_stand</p>
</div>

</div>

<div class="caption">Top five real risk-score reductions in this prompt family. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Deltas - Communication / Safety

<div class="video-grid five">

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/communication_safety/repair_delta__hrb_082_yield_step__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/communication_safety/repair_delta__hrb_082_yield_step__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -9.2; YES->YES</strong><br/>hrb_082 yield_step</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/communication_safety/repair_delta__hrb_078_stop_signal__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/communication_safety/repair_delta__hrb_078_stop_signal__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -2.8; YES->YES</strong><br/>hrb_078 stop_signal</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/communication_safety/repair_delta__hrb_084_direct_traffic__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/communication_safety/repair_delta__hrb_084_direct_traffic__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -1.9; YES->YES</strong><br/>hrb_084 direct_traffic</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/communication_safety/repair_delta__hrb_079_point_left__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/communication_safety/repair_delta__hrb_079_point_left__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -1.9; NO->NO</strong><br/>hrb_079 point_left</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/communication_safety/repair_delta__hrb_083_look_around__yes_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/communication_safety/repair_delta__hrb_083_look_around__yes_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -1.8; YES->YES</strong><br/>hrb_083 look_around</p>
</div>

</div>

<div class="caption">Top five real risk-score reductions in this prompt family. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Deltas - Terrain / Obstacle

<div class="video-grid five">

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_089_slope_up__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_089_slope_up__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -15.1; NO->NO</strong><br/>hrb_089 slope_up</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_092_tight_turn_back__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_092_tight_turn_back__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -9.9; NO->NO</strong><br/>hrb_092 tight_turn_back</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_091_swerve_left__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_091_swerve_left__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -9.2; NO->NO</strong><br/>hrb_091 swerve_left</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_088_duck_under_bar__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_088_duck_under_bar__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -6.1; NO->NO</strong><br/>hrb_088 duck_under_bar</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_085_step_over_right__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/terrain_obstacle/repair_delta__hrb_085_step_over_right__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -5.0; NO->NO</strong><br/>hrb_085 step_over_right</p>
</div>

</div>

<div class="caption">Top five real risk-score reductions in this prompt family. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Repair Deltas - Athletic Stress

<div class="video-grid five">

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/athletic_stress/repair_delta__hrb_094_forward_roll__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/athletic_stress/repair_delta__hrb_094_forward_roll__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -17.3; NO->NO</strong><br/>hrb_094 forward_roll</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/athletic_stress/repair_delta__hrb_100_handstand_kickup__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/athletic_stress/repair_delta__hrb_100_handstand_kickup__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -8.9; NO->NO</strong><br/>hrb_100 handstand_kickup</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/athletic_stress/repair_delta__hrb_093_cartwheel_attempt__no_to_yes.mp4" poster="assets/video_posters/appendix_repair_by_category/athletic_stress/repair_delta__hrb_093_cartwheel_attempt__no_to_yes.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -8.0; NO->YES</strong><br/>hrb_093 cartwheel_attempt</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/athletic_stress/repair_delta__hrb_099_side_roll_recovery__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/athletic_stress/repair_delta__hrb_099_side_roll_recovery__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -5.9; NO->NO</strong><br/>hrb_099 side_roll_recovery</p>
</div>

<div class="video-card">
<video src="assets/videos/appendix_repair_by_category/athletic_stress/repair_delta__hrb_095_burpee__no_to_no.mp4" poster="assets/video_posters/appendix_repair_by_category/athletic_stress/repair_delta__hrb_095_burpee__no_to_no.jpg" autoplay muted loop playsinline preload="metadata"></video>
<p><strong>delta risk -5.6; NO->NO</strong><br/>hrb_095 burpee</p>
</div>

</div>

<div class="caption">Top five real risk-score reductions in this prompt family. Each video: left = original KIMODO, right = repaired. Red ghost = reference; solid G1 = physics rollout.</div>

---

<!~~ _class: compact ~~>

## Appendix: Runtime Snapshot

<div class="cols">

<div>

| stage | measured run | average |
|---|---:|---:|
| KIMODO generation | 100 clips in 44.4 min | 26.6 s / clip |
| physics + SONIC checks | 100 clips in 2.3 min | 1.4 s / clip |
| repair gallery render | 45 clips in 45 s | 1.0 s / clip |

</div>

<div>

<div class="metric">Numbers are from this machine's logged runs and include practical overhead. They are timing evidence for the current prototype, not a claim of model-optimal latency.</div>

<div class="warn">Appendix videos are visual review candidates. Main-slide claims stay bounded to measured pass rates and tracked summaries.</div>

</div>

</div>

-->
