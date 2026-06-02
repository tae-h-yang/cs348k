# CS348K Final Release

Final project: **Physical Awareness for Generated Humanoid Motion**.

This release contains the final slides, report, and selected video/figure
artifacts for a test-time physical-audit and prompt-refinement loop for
KIMODO-generated Unitree G1 reference motions. The system uses MuJoCo physical
checks and SONIC rollout evidence to produce failure tags, then uses GPT-5.5 to
rewrite prompts with metric-specific constraints before regeneration.

## Start Here

- [Final slides PDF](slides/build/deck.pdf)
- [Final slides PPTX](slides/build/deck.pptx)
- [Final report](docs/final_report.md)
- [Compact report PDF](paper/main.pdf)

## One-Line Result

First-pass KIMODO references are often plausible but brittle: 48/100 pass the
physical screen, 53/100 complete SONIC, and 29/100 pass both gates. Metric-guided
prompt repair reduces several failure tags, but does not solve arbitrary
text-to-robot motion.

## Viewing

```bash
open slides/build/deck.pdf
open slides/build/deck.pptx
```

On Linux:

```bash
xdg-open slides/build/deck.html
```

To rebuild the deck:

```bash
python -m pip install -r requirements.txt
bash slides/build_slides.sh
```

Selected videos and posters used by the slides live under `slides/assets/`.
