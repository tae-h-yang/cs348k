# Speaker Notes

Target length: complete by the 8-minute timer inside a 10-minute CS348K slot.
Kayvon's latest guidance is to focus on the project goal, technical challenge,
definition of success, evaluation questions, experiments, and what the results
say about success.

## 1. Title

This project is about the object between a motion generator and a humanoid
controller: the reference trajectory. I am not claiming solved text-to-robot
motion. I am claiming a prompt-refinement loop for generated references.

## 2. Tracking Progress

Start with the optimistic side: humanoid tracking policies have become
impressive. SONIC is the SOTA-style example in this deck. Explain it at the data
level: the system tracks reference trajectories built from high-quality human
motion data, such as mocap-style full-body pose sequences. The slide's visual
shows human motion data becoming a root/joint target trajectory, then a
humanoid tracker following it in physics. The transition line is: great,
tracking works, but where do the reference motions come from?

## 3. KIMODO References

KIMODO gives broad kinematic G1 reference generation from text and constraints,
which makes a 100-prompt benchmark plausible. The caveat is the thesis of the
project: kinematic generation is not enough to ensure feasible torques, valid
contacts, prompt correctness, or controller trackability.

## 4. Reference Bottleneck

Define what is being refined: not the text alone, but the prompt in response to
failures observed in the generated root-and-joint trajectory. GPT-5.5 is the
prompt rewriter, and the deterministic failure tags tell it what physical
constraint to add. Then state the project question: can metric failures guide
useful prompt rewrites?

## 5. Success Criteria and Evaluation

State the definition of success explicitly: better physical-risk and tracking
evidence than the one-sample baseline, not guaranteed execution. Then read the
evaluation questions quickly. This slide is the bridge to the experiments.

## 6. What We Built

The baseline is one generated reference per prompt. The added system generates a
reference, checks physical rules and SONIC rollout behavior, sends the failure
tag to GPT-5.5 for prompt rewriting, then regenerates until the clip clears the
gate or the budget ends.

## 7. Method

Explain the loop simply: generate, evaluate the reference and SONIC rollout,
let GPT-5.5 rewrite the prompt from the failed metric, regenerate, and gate. The
point is test-time prompt refinement, not training a new generator.

## 8. LLM Prompt Repair

Explain that GPT-5.5 is not guessing freely. Each rewrite receives a structured
failure tag and a constraint vocabulary, such as smoother limbs for torque
spikes or wider stance for support failures. Every rewrite is traceable to the
metric that failed.

## 9. Benchmark

The benchmark has 100 humanoid robotics prompts across locomotion, manipulation,
floor, dance, athletic, and communication categories. A key caveat is that many
prompts are outside the local generator vocabulary: 8 are direct mode proxies,
14 are partial proxies, and 78 are unsupported stress/refusal tests.

## 10. Generated Reference Examples

Show what raw generated references look like before physics rollout. This slide
is reference-only, so do not describe it as SONIC or controller execution.

## 11. First-Pass Successes

Before showing failures, show that the pipeline is not only negative. Five
KIMODO references pass the physical rules and the pretrained SONIC rollout
immediately: broad jump, crab walk, wipe table, point right, and reach overhead.
Vertical jump is included as a support/contact contrast.

## 12. Main Result

The audit snapshot shows many usable references and many failures. Read this
honestly: 48 of 100 pass the physical screen, 53 of 100 do not fall in this SONIC
rollout, and only 29 pass both. The controller-check row is the key point:
offline physical pass correlates with longer SONIC tracking, but it is not the
same as controller success.

## 13. Generated Failure Modes

These are full rollout renders, not early-terminated clips. Point to the six
failure families: torque/root-wrench demand, self-contact, non-foot floor
contact, support proxy, controller trackability, and contact artifact. Verbally
explain that each video corresponds to one evaluator check, so the failure tags
are not just abstract numbers.

## 14. Failure Stats

Upright balance and communication examples are often more usable. Low-posture,
terrain, object-like, and acrobatic categories remain hard. Use this slide to
show where the risk comes from across the 100 clips.

## 15. Repair Statistics

Use this as the quantitative repair slide: retiming and smoothing improve some
cases but do not solve the problem. Keep the claim bounded.

## 16. Before/After Evidence

Do not oversell this. These are the four logged before/after pairs where K1
fell and the selected reference reached the full horizon. They show the curation
layer can produce real wins, but many hard motions still fail.

## 17. More Repair Evidence

This restores the extra qualitative examples: pushup for non-foot-floor,
happy_dance for contact artifact, and backward_recovery for support proxy. Make
clear that pushup is a visualization demo, while the main evidence comes from
the logged metric and rollout records.

## 18. No-Fall Examples

These are successful controller rollouts. They replace the all-100 status grid
as a cleaner positive qualitative slide.

## 19. What Still Fails

Show the failed-run videos directly. Say that visual/VLM inspection is helpful
for behavior sanity, but it is not the full metric set; physical rules and SONIC
rollout still define the labels.

## 20. Takeaway

Close with the useful lesson: generated humanoid motion needs a physical
awareness layer, and the next version should learn from controller-labeled SONIC
rollouts.

## 21. Backup Oracle Visualization

Only show this if someone asks what a good-looking tracker outcome would look
like. Say explicitly that this is an oracle target visualization, not SONIC
evidence and not part of the result table.

## 22. Backup Clean Oracle Videos

This is a remote-inspection convenience slide for the same oracle visual, with
no in-frame text. It is not a result slide.

## 23. Backup Failure-Case Oracle Checks

This slide is for debugging and remote review only. These ten clips were chosen
from references whose actual SONIC rollout failed. The white mesh is a delayed
and slightly offset replay of the reference, while the red mesh is the target
reference. Say clearly that this is not a SONIC success video and not evidence
for the result table.
