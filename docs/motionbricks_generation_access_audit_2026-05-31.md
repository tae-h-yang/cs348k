# MotionBricks Generation Access Audit

Date: 2026-05-31

## Question

Can this project access more MotionBricks generation than the 15 local G1 modes,
or did we only check the tutorial?

## Short Answer

For the installed public MotionBricks preview in
`/home/rewardai/repos/GR00T-WholeBodyControl/motionbricks`, the executable G1
robot generation interface is the interactive demo / navigation demo path. That
path exposes 15 G1 clip/mode controls.

The broader MotionBricks paper and project page show more capabilities,
including smart locomotion, mixtures, and smart objects. Those examples are
present locally as GIF gallery assets, but the released code in this checkout
does not include a runnable object-authoring or open-vocabulary text generation
script for G1.

## Evidence Checked

### 1. Local executable scripts

Files under `motionbricks/scripts/`:

- `interactive_demo_g1.py`
- `train_vqvae.py`
- `train_pose.py`
- `train_root.py`

Only `interactive_demo_g1.py` is an inference/demo script. It calls
`navigation_demo(args)` and passes `allowed_mode` into the controller.

### 2. Local G1 clip holder

`motionbricks/motionbricks/motion_backbone/demo/clips.py` contains one concrete
clip holder class for the demo:

- `clip_holder_G1`

The `DEFAULT_KEYS` map has 15 keys:

- `idle`
- `slow_walk`
- `walk`
- `hand_crawling`
- `walk_boxing`
- `elbow_crawling`
- `stealth_walk`
- `injured_walk`
- `walk_stealth`
- `walk_happy_dance`
- `walk_zombie`
- `walk_gun`
- `walk_scared`
- `walk_left`
- `walk_right`

### 3. Checkpoint contents

The local clip checkpoint `motionbricks/out/G1-clip.ckpt` contains tensors with
first dimension 15:

- `global_root_positions`: `(15, 150, 3)`
- `global_joint_positions`: `(15, 150, 34, 3)`
- `global_joint_rotations`: `(15, 150, 34, 3, 3)`
- `global_headings`: `(15, 150)`
- `motion_feature`: `(15, 150, 414)`
- `mujoco_qpos`: `(15, 150, 36)`
- `num_frames_per_clip`: `(15,)`

So the local demo clip bank itself contains 15 target modes.

### 4. README and release status

The MotionBricks README says the initial public release includes:

- interactive demo,
- pretrained VQVAE / pose / root checkpoints,
- synthetic training code,
- motion-representation docs,
- GIF gallery.

It also says the full training pipeline inside GR00T Whole-Body Control is a
roadmap item. The README lists interactive movement controls and motion style
keys matching the 15-mode local interface.

### 5. Text conditioning

The shipped config files include fields such as `text_embeddings`, but the
current checkpoints/configs set:

- `text_embeddings: null`
- `loading_mode: motion_only`

That means this release is not exposing a text-to-motion interface comparable
to Kimodo.

### 6. Upstream check

`git fetch origin main` on `GR00T-WholeBodyControl` showed upstream commits
after the local checkout, but `git diff HEAD..origin/main -- motionbricks`
returned no MotionBricks changes. The newer upstream changes are outside the
MotionBricks subproject.

## What We Can Still Generate

Even with 15 modes, we can generate more than 15 clips by varying:

- random seed,
- allowed mode,
- movement direction,
- heading direction,
- speed scaling,
- control switching schedule,
- best-of-K sampling.

This gives many trajectory variants, mixtures, and path shapes, but not new
semantic primitives such as `cartwheel`, `sword pickup`, `jump over bench`, or
`sit` through a released G1 object interface.

## Presentation Implication

Use this wording:

> The full MotionBricks paper demonstrates broader smart primitives and object
> interactions. The public G1 preview available in this repo exposes a 15-mode
> structured control interface. We therefore separate a fair 15-mode local
> MotionBricks benchmark from a 100-prompt humanoid stress suite containing many
> unsupported tasks.

Avoid saying:

> MotionBricks can only generate 15 motions.

Also avoid saying:

> We evaluated 100 natively supported MotionBricks prompts.

