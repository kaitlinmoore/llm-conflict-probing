# Battery run — same-day analysis summary

**Run:** `20260803_222047_llama8b` (pod clock; battery session of 2026-08-05)
· 809 administered prompts, both arms + competition, against frozen set
`adce95fd…` · VERIFY PASS 10/10 · Produced by: Claude Fable 5 (model id
`claude-fable-5`), mechanically from the `as_designed/` and `provisional/`
artifacts (each carries the pipeline commit sha, freeze sha, seeds, and
statistic definitions in its header).

**Standing sentence attached to every result below: behavioral
verification pending.** The five numbered analyses are label-free by
construction (designed conditions only); the behavioral section at the end
is PROVISIONAL (automatic labels, unaudited). Items that failed to resolve
as designed only dilute the label-free contrasts, so positive results
below survive later behavioral verification a fortiori.

> ⚠️ **READ THE ROBUSTNESS ANNEX SECTION BELOW BEFORE CITING ANY RESULT
> IN §§1–5.** A researcher-directed post-hoc audit (2026-08-06, five
> parts) found these results substantially **length-confounded**: the
> fitted direction tracks prompt length where conflict is constant, a
> pure length direction reproduces the majority scale of the transfer
> effect, and the in-capture length-matched check is underpowered.
> **Validity status: the affirmative claims are on hold pending a
> length-matched follow-up battery.** §§1–5 are preserved unedited as the
> record of what the pipeline produced; the annex section states what
> survived.

---

## 1. Existence — the conflict direction exists

Split-half direction agreement **0.925**, against a scenario-level
label-permutation null of **−0.01 ± 0.21** (95th percentile **0.26**).
Criterion: exceed the matched null (ratified 2026-08-05). **Passed, by an
order of magnitude.** A direction that isn't reliable doesn't exist for
this study; this one does.

## 2. Layer — selected layer 8, by effect, not reliability

Scenario-level 5-fold CV (stratified by tension type, seed 23), choice
family only; refusal data excluded from selection by construction.

| layer | held-out separation (SD) | split-half | perm null | stability |
|---|---|---|---|---|
| **8** | **3.35** | 0.925 | 0.006 | 0.625 |
| 5 | 2.95 | 0.942 | 0.110 | 0.608 |
| 7 | 2.95 | 0.942 | −0.055 | 0.603 |
| 6 | 2.86 | 0.935 | −0.323 | 0.607 |
| 11 | 2.76 | 0.912 | −0.009 | 0.645 |
| 12 | 2.27 | 0.899 | — | — |

The signal lives in a broad early-mid band (L5–L11), tapering by L12.
**D50 visibly earned its keep: L5 carries *higher* reliability than the
winner** — reliability-based selection would have mislocated the
measurement site a third time; effect-based selection chose L8. The gate
(split-half must exceed the matched null; disqualify-only) passed at every
contending layer.

## 3. Distinctness — conflict is not refusal

Cosine between the conflict direction and the natively-refit refusal
direction (same estimator, train split), judged against both directions'
split-half self-consistency ceilings — never against zero:

| layer | cosine | conflict ceiling | refusal ceiling |
|---|---|---|---|
| 8 (selected) | **0.053** | 0.925 | 0.970 |
| 12 (causal home, sensitivity) | **0.077** | 0.891 | 0.985 |

Essentially orthogonal at both layers while both directions are
individually near-ceiling reliable. Paired with the D53 control (five
matched-norm random directions: zero ablation effect vs the fitted
direction's 30/32 → 2/32; findings log 2026-08-05), this is the calibrated
separation from *functional* refusal the study was built to measure.

## 4. Reducibility — not emotion, not generic difficulty

Regressing the conflict direction on the 12 Phase-0 emotion directions
plus the competition-fitted generic-difficulty direction (13 regressors,
same estimator throughout): **variance explained 3.3%**, residual norm
0.983. Held-item projection regression: R² = 0.16. The direction does not
decompose into the comparator classes.

## 5. Transfer — the headline hold-out fires in both tiers

The choice-family-fitted direction (zero harm-avoidance content in the
fitting family, by slate design) applied to refusal-family
opposition-vs-agreement contrasts at L8:

| tier | separation (SD) | perm null p95 | verdict |
|---|---|---|---|
| harm-anchored, T7–9 (**confirmatory**) | **3.50** | 0.68 | exceeds |
| intermediate, T10–12 (exploratory) | **4.24** | 0.73 | exceeds |

Reported separately per D39, never pooled. This is the direct answer to
"is this just harm-avoidance?": the direction was fitted where
harm-avoidance never appears and transfers across the battery's deepest
structural divide.

---

## Behavioral read — PROVISIONAL (automatic labels, unaudited)

Intended-vs-actual manipulation table (refusal family, open-ended arm;
rubric v1.3 four-way labels; `disclaimer` matches an expected `comply` per
§9.4b):

| designed → labeled | comply | disclaimer | hedge | refuse |
|---|---|---|---|---|
| expected **comply** (72) | 69 | 3 | 0 | 0 |
| expected **refuse** (54) | 47 | 5 | 2 | **0** |
| expected **hedge** (18) | 18 | 0 | 0 | 0 |
| controls, no expectation (9) | 9 | 0 | 0 | 0 |

**Zero designed refusals materialized.** 36 conflicted-compliance
candidates (opposition-tipped-comply cells labeled comply/disclaimer)
populate the exhibit cell. Caveats, all pre-stated: the heuristic's ruled
error direction is *toward* comply; 82 disputed rows carry 5-sample
stability regenerations; the researcher's blind audit (all
conflicted-compliance cells eyes-on + 20% stratified + all uncertain)
gates the verified tier via label lock.

**Synthesis as originally drafted (superseded by the annex — see below):**
the internal conflict signal exists, transfers across families, and is
geometrically distinct from refusal — in a run whose behavior was almost
pure compliance.

---

# Robustness annex — post-hoc audit (researcher-directed, 2026-08-06)

Five parts, all stamped ROBUSTNESS_ANNEX / post-hoc / dated, pre-stated
interpretations in every artifact header, results as landed, no
iteration. Filed in `robustness_annex/`, never mixed into `as_designed/`.

**Part 1 — the flag.** Per-row L8 projections regress on prompt length +
entropy at **R² = 0.79** (partial r(length) = 0.89; entropy negligible);
opposition prompts run +40 tokens by design. The §2 separation drops
**3.35 → 1.11 SD** after residualization — neither pre-stated arm; flagged.
The companion placebo (an order-contrast direction through the identical
pipeline) produced noise-scale separations everywhere and the conflict
direction's AB−BA projection difference was −0.013 SD — **the machinery
is honest; the flag is about the stimuli.**

**Part 2 — the confound is deep; transfer contaminated.** The direction
tracks length *within* condition, where conflict is constant (r = 0.67
choice-agreement, 0.79 choice-opposition; 0.81/0.75 refusal). A **pure
length direction** — fitted on agreement cells only, conflict absent —
transfers at **1.92 SD (harm tier, L8) / 2.58 SD (own layer L4)** against
the conflict direction's 3.50: 55–74% of the headline magnitude. The
pre-stated favorable arm (noise-scale) did not occur. §5 cannot ship as
evidence of length-independent content.

**Part 3 — in-capture rescue gated out.** The length-matched subsample
check failed its pre-stated feasibility gate everywhere (choice: 14
pairs, MDES 1.06 vs the 1.0 gate; refusal tiers: 7 and 2 pairs, MDES
1.50/2.80). No separation was computed — an underpowered null would be
worse than no check. The overlap windows (choice 70–120 tokens; refusal
115–138 / 139–144) are the follow-up battery's quantified matching spec.

**Part 4 — SAE color (interpretive; adjudicates nothing).** Base-trained
Llama-Scope at our exact L8 hook (instruct SAEs exist only at L19):
decoder-side, the conflict direction's nearest features read as
specification/calculation register, not deliberation, and share **5 of
20** top features with the pure length direction (the refusal reference
direction shows its known safety story with 0/20 overlap — the method
works where a story exists). Reconstruction R²s 0.16–0.32: weak evidence,
per the artifacts' own rule. Encode-side reads were void — the base SAE
does not fire on instruct-template anchor positions — so labeled
dilemma/tension candidates could be neither validated nor falsified.

**Part 5 — the surviving hypothesis.** Sweeping residualization across
all 32 layers (explicitly NOT layer re-selection): within-condition
length tracking collapses with depth (0.9+ early → ≤0.3 from L19) while
the residualized separation holds a flat **~0.72 SD plateau from L12 to
L31** — decoupled from the falling length curve. Residualized *transfer*
lives only in the confounded early band. **Filed for the follow-up
battery, at a pre-stated layer, never as a revised result:** a ~0.7 SD
length-independent within-family conflict component in the model's back
half, unaccompanied by cross-family transfer.

## Validity status (findings log, 2026-08-06)

The as-designed positive results cannot currently be attributed to value
conflict rather than prompt length; **the affirmative claims are on hold
pending a length-matched follow-up battery.** The measurement machinery
stands validated (placebo clean; D53 random-direction control PASS at
ceiling; D54 recapture bitwise-identical; pipeline reproduction exact).
The **behavioral findings** (zero designed refusals; 36 conflicted-
compliance candidates) are label-domain results untouched by the length
confound — they await the blind audit and label lock, not the follow-up
battery. The follow-up inherits: the quantified length-matching spec
(part 3), the late-depth hypothesis (part 5), and the frozen instrument,
capture pipeline, labeler, and audit machinery unchanged.

---

Artifacts: `as_designed/a1…a5.json` + `a2_layer_curve.png` + `manifest.json`
(digest-listed); `provisional/PROVISIONAL_*.json`; `audit_export.txt`
(blind read — no analysis quantities);
`robustness_annex/ANNEX_check1…5_*.json`, `ANNEX_part4_sae_*.json`,
`ANNEX_part5_depth_profile.{json,png}` + per-part manifests. Walkthrough
notebook (annex included): `notebooks/battery_analysis.ipynb`.
