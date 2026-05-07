# SIGGRAPH Technical Papers — Reviewer Assessment
## "Physics-Critic-Guided Inference-Time Scaling for Humanoid Motion Generation"

> Superseded status note, 2026-05-04: this was the earlier review pass. The
> updated reviewer/author loop after the 105-identity extension is in
> `docs/reviewer_v2.md` and `docs/author_response_v2.md`. Keep this file as a
> record of earlier objections, not as the current verdict.

**Reviewer Decision: WEAK REJECT → BORDERLINE ACCEPT (after revision)**
**Confidence: High**
**Last updated: Iteration 2 — post-revision**

---

## Revision Summary (Iteration 2)

**Addressed:**
- ✅ R3: Added Wilcoxon signed-rank tests (p<10⁻⁶), bootstrap 95% CIs, Cohen's d for all major comparisons
- ✅ R4: Ran diversity source ablation (seed-only vs Gumbel-only vs combined K=4); Gumbel is primary driver, synergy for expressive motions
- ✅ R5: Ran neural-guided WC-K8; reported honest negative result (31% agreement, 2× worse mean risk); identified root cause (max-window aggregation)
- ✅ R6: Fixed references: [8] MuJoCo → correct BoN citation (Cobbe 2021); removed unused LaValle [5]; added DeepMimic [5]; renumbered
- ✅ R7b: Static regression now discussed seriously with correct interpretation (don't apply stochastic BoN to near-zero-risk motions)
- ✅ R7a: Added baseline design note explaining K=1 deterministic vs stochastic confound
- ✅ R5c: Fixed neural critic timing arithmetic (38× for K=8 pipeline, not 460×)
- ✅ R5 (circularity): Added explicit caveat that ρ=0.919 is heuristic mimicry, not physical validation

**New findings from Iteration 2 experiments:**
- Diversity ablation: Gumbel sampling (21.15) > Seed diversity (23.75); combined (20.98) only marginally better. Expressive motions show clear synergy: combined 3.65 vs gumbel-only 7.87 vs seed-only 12.21.
- Neural critic as WC-K8 selector: 31% agreement, mean risk 31.04 vs heuristic 15.50. Neural segment critic cannot replace full-clip heuristic critic for WC selection. Validated use case: PS-K (segment-level).

---

---

## Summary of Contributions (as Claimed)

1. Best-of-K inference scaling for physics-constrained humanoid motion generation
2. Compute-matched comparison: WC-K4 vs PS-K4 per-segment steering
3. Neural surrogate critic (1D CNN, ρ=0.919, 0.174ms)
4. MotionBricks GPU non-determinism characterization
5. K=1 vs K=8 video comparisons

---

## Detailed Critique

---

### R1 — FATAL: Physics Critic is Not Validated Against Actual Physics

**Severity: Reject-level**

This is the paper's single biggest problem. The entire narrative rests on the claim that the risk score predicts physical feasibility. The authors themselves report:

> *Spearman ρ = −0.09, p = 0.59 (risk score vs. PD time-to-fall)*

This is not statistically significant. Individual-level correlation between the paper's core metric and a physical controller is essentially **zero**. The authors dismiss this as "the PD controller is too weak," but this is circular — if we cannot validate the metric, we cannot trust the results.

**Specific problems:**

a) The risk weights (35, 20, 15, 10, 10, 10) and thresholds (10kN, 2kNm, etc.) are entirely ad hoc. No ablation on weight sensitivity. A 2× weight change could flip every result.

b) "Accept" threshold < 10 is arbitrary. The paper never justifies why 10 is the right boundary vs 5 or 20.

c) The "group-level ordering" validation (Table 4.5) shows static > locomotion > expressive > whole-body. This is trivially expected from domain knowledge — crawling is hard, idle is easy. It does not validate that *within* a category, the critic discriminates quality.

d) The neural surrogate critic trained on heuristic labels (Section 4.6) and evaluated on heuristic labels is **completely circular**. ρ=0.919 tells us the CNN learned to mimic the heuristic, not that the heuristic is correct.

**What would fix this:** Run a learned tracking policy (PHC [2]) on K=1 vs K=8 outputs and show that K=8 clips achieve lower tracking RMSE / longer time-to-fall. This is stated as "future work" but without it, the claim "K=8 is better" means "K=8 is lower according to an unvalidated metric."

---

### R2 — MAJOR: Novelty is Questionable

**Severity: Major revision**

Best-of-N sampling is a 30-year-old idea in search and planning, and has been applied to generative models extensively. The "novelty" claimed here is applying it to motion generation with inverse dynamics as verifier. This is reasonable but incremental. Key issues:

a) **MotionBricks already uses random seeds for diversity** (cited in this paper). The contribution is "use more seeds + score them," which is incremental to the system's existing design.

b) **The verifier (mj_inverse) is not novel**. Inverse dynamics for feasibility checking is standard in biomechanics and robotics simulation. The paper cites Winter (2009) correctly, but does not differentiate from prior art in a way that clearly establishes a gap.

c) **No comparison to any prior physics-aware motion generation method.** How does WC-K8 compare to: (i) AMP [3] with physics-based discriminator, (ii) CALM or similar learned-residual-correction approaches, (iii) even a simple velocity/acceleration post-processing filter? The *only* baselines are post-hoc retiming variants (within the same system) and two K values of the same method.

d) **The CUDA nondeterminism finding is the most original contribution** but gets buried in Section 3.6 and is not presented in a way that is actionable or broadly useful. It is a footnote to a methodological design choice, not a contribution.

**What would fix this:** (i) Add one external baseline (e.g., velocity smoothing with optimal-control style refinement). (ii) Position the nondeterminism finding more prominently — this has implications for anyone reproducing MotionBricks results.

---

### R3 — MAJOR: Insufficient Statistical Power

**Severity: Major revision**

All claims rest on **39 clips** (13 styles × 3 seeds). This is far too small for the confidence level of the claimed results.

a) "K=8 reduces mean risk by 59%" — what is the confidence interval? There are no error bars, no bootstrap CIs, no Wilcoxon tests anywhere in the paper.

b) "WC-K4 wins on 25/39 clips" — this is 64%. A binomial test gives p ≈ 0.065 at 25/39 (one-sided), which is not even significant at α=0.05. The authors cannot claim statistical significance.

c) "PS-K4 wins locomotion accepts (14/18 vs 12/18)" — this is 2 clips difference in 18 samples. No test, no significance.

d) The ablation design confounds seed and K: each seed appears in K=1, K=4, K=8, K=16. If a particular seed happens to generate easy clips, that inflates all K values for that seed. A proper ablation would use held-out seeds.

e) 3 seeds per style is not enough to characterize style-level behavior. The walk/slow_walk/stealth_walk styles are highly correlated. Independence assumption is violated.

**What would fix this:** (i) Add 95% bootstrap CIs to all mean risk comparisons. (ii) Run Wilcoxon signed-rank test for paired comparisons (K=1 vs K=8 per clip). (iii) Increase to at least 10 seeds per style for key claims.

---

### R4 — MAJOR: Missing Ablation on Diversity Sources

**Severity: Major revision**

The paper claims two diversity sources: (1) seed-indexed VQ-VAE references, (2) Gumbel stochastic sampling. These are never ablated against each other. We do not know:

- Does seed diversity alone (argmax, different seeds) achieve most of the gain?
- Does Gumbel sampling add anything beyond seed diversity?
- What is the contribution of each source to the 59% reduction?

Without this ablation, the key algorithmic claim ("two sources of diversity are needed") is unsupported. If seed diversity alone achieves 55% reduction, the entire Gumbel monkey-patch mechanism is premature engineering.

**What would fix this:** Run K=8 with seed-only diversity (argmax, 8 seeds) vs Gumbel-only diversity (stochastic, 1 seed × 8 draws) vs combined. This can be computed from existing data if the saved .npy files include seed-only runs.

---

### R5 — MODERATE: Neural Critic Analysis is Incomplete

**Severity: Moderate revision**

Section 4.6 reports ρ=0.919 between neural and heuristic critic. This does not establish:

a) That the neural critic can generalize to out-of-distribution motions (only tested on the same clip distribution).

b) That using the neural critic in the WC-K loop produces the *same* best-of-K selection as the heuristic critic (are they selecting the same clips as winners?).

c) The speed comparison arithmetic is inconsistent: "13ms per segment" for heuristic (80ms / 6 segments) but the online segment critic as used in PS-K uses 32-frame windows, not full-clip scoring. The actual comparison should be neural segment scoring (0.174ms) vs heuristic segment scoring (not 13ms but much shorter for a 32-frame window).

**What would fix this:** (i) Report agreement rate between neural and heuristic on best-clip selection (e.g., "neural and heuristic agree on winner for X/39 clips"). (ii) Run neural-guided WC-K and compare risk distribution to heuristic-guided WC-K.

---

### R6 — MINOR: Reference and Citation Issues

a) **Reference [8]** is the MuJoCo paper (Todorov 2012), cited as an example of "test-time compute optimization." This is WRONG. The MuJoCo paper has nothing to do with inference-time scaling. The correct citation for test-time scaling is Snell et al. 2024 (which appears as [7]).

b) References [5] (LaValle, Planning Algorithms) is cited in the Related Work but does not appear in the text body. Remove unused references.

c) The statement "best-of-N for language models was first proposed by Lightman et al. [6]" — [6] is "Let's Verify Step by Step" which is about process reward models, not best-of-N. Best-of-N sampling predates this by decades; Cobbe et al. 2021 ("Training Verifiers to Solve Math Word Problems") is the more appropriate citation for BoN with LLMs.

---

### R7 — MINOR: Experimental Design Issues

a) The K=1 "deterministic baseline" uses argmax + fixed seed. If Gumbel stochasticity is enabled for K>1, comparing K=1 (argmax) to K=8 (Gumbel) confounds two variables: sample count and sampling temperature. The K=1 stochastic baseline is never reported.

b) The static category result: "K=8 mean risk = 8.6 vs K=1 mean risk = 6.1 (−41% regression)" is presented with a dismissive "noise" comment, but this is a real finding — stochastic sampling can make stable motions worse. It is not addressed or discussed seriously.

c) The claim "motion style and character are preserved" in video comparisons (Section 4.2) is asserted without user study or quantitative measure. This is subjective and unverifiable in the paper.

---

## What Would Change My Vote

**For accept (at a workshop level):**
- Statistical tests (Wilcoxon) on all paired comparisons
- Fix the reference errors
- Reframe neural critic as heuristic-surrogate (not physics validation)
- Clarify K=1 stochastic vs deterministic baseline

**For a full SIGGRAPH paper:**
- Real tracking policy (PHC or similar) validation showing K=8 → lower tracking RMSE
- Diversity source ablation (seed-only vs Gumbel-only vs combined)
- At least 10 seeds per style (not 3)
- One external baseline (not just retiming)
- Neural critic selection agreement with heuristic critic

---

## Summary Score

| Criterion | Score (1–5) | Notes |
|---|---|---|
| Novelty | 2 | Incremental application of BoN to motion generation |
| Technical rigor | 2 | Unvalidated metric, no stats, small N |
| Experimental completeness | 2 | Missing ablations, no external baselines |
| Writing clarity | 4 | Well-written, clear framing |
| Contribution potential | 3 | Nondeterminism finding is genuinely useful |
| **Overall** | **2.5** | **Reject — major revision** |

---

## Remaining Concerns (Post-Iteration 2)

### R1 — STILL CRITICAL: Critic not validated against actual physics

**Status: Partially addressed, still a real concern.**

The individual-level correlation is still ρ=−0.09. The paper now acknowledges this clearly (Section 4.5 and Limitation). However, the paper's claims about "risk reduction" still imply that lower heuristic risk → better physical quality. Without validation via a learned tracking policy, this remains circular.

**What still needs to happen:**
- Run K=1 vs K=8 clips through PHC or a comparable learned controller
- Show that K=8 clips track longer or have lower tracking error
- This is the single biggest remaining gap

### R2 — PARTIALLY ADDRESSED: Novelty

**Status: Better framed, but limited external comparisons.**

The paper now correctly cites Cobbe et al. for BoN and distinguishes from prior work. However, there is still no comparison to any physics-aware generation method (AMP, CALM, etc.) — only retiming variants. This limits the claim of "best method" to within a narrow design space.

**What would help:** Even a simple velocity-smoothing post-process (not retiming) as an additional baseline.

### R3 — ADDRESSED: Statistics

**Status: Resolved.** Wilcoxon p<10⁻⁶, Cohen's d=1.09. Well powered for the main finding.

Note: Small n for static (3) and whole-body (6) sub-group comparisons, but these are correctly qualified.

### R4 — ADDRESSED: Diversity source ablation

**Status: Resolved.** Gumbel is primary driver; expressive motions show genuine synergy. Now in Section 4.8.

### R5 — ADDRESSED WITH HONEST NEGATIVE: Neural critic

**Status: Resolved (honest negative result is better than overselling).** 
- ρ=0.919 on window-level but only 31% clip-level selection agreement
- Max-window aggregation is the root cause
- Neural critic validated as PS-K scorer, not WC-K selector
- Identifies clear follow-up: train clip-level neural model on full-clip labels

### R6 — ADDRESSED: References

**Status: Resolved.** Correct citations, no spurious references.

### R7 — ADDRESSED: Experimental design issues

**Status: Resolved.** Static regression addressed, K=1 stochastic confound documented.

---

## Revised Score

| Criterion | Score (1–5) | Notes |
|---|---|---|
| Novelty | 3 | Better framed; diversity ablation adds value |
| Technical rigor | 3.5 | Strong stats, honest negatives, still lacks real-robot validation |
| Experimental completeness | 3.5 | Diversity ablation + neural-guided results added |
| Writing clarity | 4 | Clear, well-organized |
| Contribution potential | 3.5 | Non-determinism + diversity finding are novel and useful |
| **Overall** | **3.5** | **Borderline accept at workshop; needs R1 validation for full paper** |

**Revised decision (Iteration 3):** WEAK ACCEPT for a course project / workshop submission. Strong iteration with honest negative results and new external baseline. The one remaining critical gap is critic validation against a real physics controller — everything else has been substantively addressed.

---

## Revision Checklist

- [x] Statistical tests (Wilcoxon) on all key comparisons
- [x] Bootstrap 95% CIs on mean risk values
- [x] Fix Reference [8] (not MuJoCo → proper BoN reference)
- [x] Diversity source ablation: seed-only vs Gumbel-only vs combined
- [x] Neural critic: report selection agreement rate with heuristic
- [x] Run neural-guided WC-K8 and compare to heuristic-guided
- [x] Static regression discussed seriously, not dismissed as "noise"
- [x] Remove/fix unused reference [5] (LaValle)
- [x] Reframe neural critic results: acknowledge circularity with heuristic labels
- [x] Baseline design note (K=1 stochastic vs deterministic confound)
- [x] R2: Added smoothing baselines (Gaussian, SavGol) — smoothing hurts (41.02 vs 38.90), WC-K8 far better
- [x] R5: Attempted clip-level neural critic — fails (ρ=0.536, n=39 clips too small for clip-level training)
- [ ] R1: Validate with learned physics controller (PHC or equivalent) — major gap, requires external system

---

*Revision tracked: items will be checked off as addressed. This document is updated each iteration.*
