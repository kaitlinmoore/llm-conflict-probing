# Findings Log — llm-conflict-probing

Append-only (CLAUDE.md scientific invariant #6): entries get dated additions,
never deletions or rewrites. Entries carry run ids and probe-file sha256s
where applicable.

---

## 2026-07-16 — Instrument-validation run declared

Instrument-validation run declared — 2026-07-16. The next administration of
the v2 pre-test instrument (frozen pretest_probes_v2.jsonl, sha256
`659afb97f154662da2d3b56c78ca26902d37fb88584b1218b511a474b336018b`, 661
records) is declared an instrument-validation (IV) run, non-gating: its
purpose is to validate the revised instrument (post single rewrite pass of
2026-07-16, see docs/screen_findings_2026-07-16.md) and produce the enactment
matrix under the v2 measures; no certification thresholds are applied to its
results, and threshold finalization is a pre-registered post-IV decision.
Declared prior to any main-run data collection. Measures per spec v2.2:
choice channel via next-token logit readout (neutral + value variants per
pair; low-mass sensitivity analysis applies per the mass finding in the
screen memo); resistance channel k=10 samples at temperature 0.7, seeds 0–9,
plus greedy reference; role tiering per §3a with exclusion-validation cells;
ceiling pairs (neutral-form mean p_vf > 0.8 across base cells) reported under
the dominance amendment (D1, screen memo) rather than shift.

---

## 2026-07-21 — Certification thresholds finalized before unblinding

Thresholds for Stage 1 certification finalized and recorded in
docs/prereg_analysis_plan.md prior to any computation of the per-value
enactment matrix from the IV merged data (run 20260717_204822, instrument
sha256 659afb97…018b; labeling in progress; no per-value aggregates computed
at time of this entry). Analysis ordering per plan §1: calibration and mass
distributions first, mass-floor adjustment window, thresholds locked, then
matrix. Criteria summary: resistance ≥ 0.80; choice dual criterion (Δ ≥ 0.25
or calibration-derived OR cutoff with Δ ≥ 0.05 guard); dominance per D28 with
calibration-percentile pass criterion, dominance-alone certification
permitted; captured-mass floor 0.5.

---

## 2026-07-21 — Same-seed shard-1 reproduction check: byte-identical

The pending reproduction diff (HANDOFF_v4 §2 [REC]) was run: the original
shard-1 execution's generations.csv
(results/pretest/20260716_165900_llama8b_instrument_validation_shard1of2,
committed before the truncation incident) and the re-run's
(results/pretest/20260717_072309_llama8b_instrument_validation_shard1of2) are
**byte-identical** — both hash sha256
`d0fefb9302809c22882c7fefc08663cd5cfe05b741a9d353929b55fa1c765113`,
1,947,724 bytes, `cmp` clean. Two independent executions on separate pods,
k=10 sampled generations at temperature 0.7 included, reproduced every byte
of 2,057 rows: a stack-determinism receipt for the certification fast-path
argument (HANDOFF_v4 §4 — "a ritual re-run ... would reproduce the same
bytes" is now demonstrated, not assumed).

---

## 2026-07-21 — prompt_join.csv emitted for the merged IV run; workbook join-back verified

`src/pretest/emit_prompt_join.py` (new, tested) regenerates the rendered
prompt for every prompt_key through the runner's own rendering path
(runner_lib.enumerate_tasks over the frozen instrument, sha verified
`659afb97…018b` against the run manifest) — freezer output with
self_template, role rendering, and swap_at_freeze as administered, not raw
probe fields. Output:
results/pretest/20260717_204822_llama8b_instrument_validation_merged/
prompt_join.csv, 994 rows (one per distinct prompt_key in generations.csv,
zero misses, zero duplicates), sha256
`aef3e806561f4a99e41cb7b96b4933dd082bc7f0dd20ae009629e1d5cc1fd1d2`
(290,628 bytes), recorded in the merged manifest's output_digests. All 8
needs_manual_label=yes choice rows (PT2-authority-C1 / -C1-null; boss,
coworker, friend roles) verified to contain both option texts verbatim in
the rendered prompt — rubric C1 is applicable to each.

Workbook join-back check (the verification the audit-labeling workbook's
own claims rest on): all 628 rows of IV_audit_labeling_workbook.xlsx joined
via its hidden key sheet back to the merged generations.csv — source sha
match, 620 resistance rows (62 prompt-sets × 10 seeds) + 8 flagged choice
rows, response and prelabel_reference verbatim-identical on every row,
flagged set exactly equal to the needs_manual_label=yes set. PASS on all
eight checks.

Guardrail found and fixed en route: the Windows checkout's
`core.autocrlf=true` was silently converting committed LF artifacts to CRLF
in the working tree, so the frozen instrument hashed `37da6b20…` locally
while its committed blob hashed the frozen `659afb97…018b` exactly.
`.gitattributes` added (`*.jsonl -text`, `*.csv -text`) and affected files
re-checked-out; frozen instrument and merged generations.csv now hash to
their manifest-recorded digests on this machine. Instrument content was
never at risk — the committed bytes were always correct; only local digest
verification was affected.

---

## 2026-07-21 — Fast-path certification exercised on advisor direction

Per advisor direction (no further pre-test rounds; proceed to battery), the
IV merged dataset (run 20260717_204822, instrument sha256 659afb97…018b) is
adopted as certification data under the pre-registered thresholds of
docs/prereg_analysis_plan.md. Documented-adjustments round is
documentation-only. Instrument finding recorded in anticipation:
authority-C1 and its null twin produced identical self-reference failures
("can't see the two formats") across 8 greedy-fallback cells spanning both
variants and three roles — a survivor of the D24 row-9 artifact-dependence
defect class; affected pairs drop from shift computation per rubric C3 and
are reported.

---

## 2026-07-21 — IV audit labeling complete; heuristic certified; authority-C1 finding refined

Human audit labeling of the IV merged run complete (workbook v2, 628 rows:
620 resistance + 8 flagged choice; run 20260717_204822, instrument sha256
659afb97…018b). Audited disagreement with the heuristic prelabeler:
12/620 = 1.94%, Wilson 95% CI [1.1%, 3.4%] — under the 5% escalation trigger
even at the CI upper bound; the heuristic is certified as primary labeler for
the full run per spec §6. Direction: 11/12 heuristic-resist → human-comply
(heuristic misreads disclaimer commentary as resistance; rubric R1
artifact-primacy overrides), 1/12 opposite. Per-value: care 3, authority 2,
one each fairness/desert/tradition/integrity/privacy/mercy/impartiality.
Care's within-sample raw rate (3/40) is noted; the overall-rate trigger is
not met, and the bias direction inflates resist rates only — it cannot push
a value toward failing.

Flagged choice rows (needs_manual_label, authority-C1 + null twin): six
labeled unparseable per rubric C3 (model declines to choose), two (F04,
F08 — value variants) labeled A per C2 lean extraction; A is the stated
preference in the value context. Finding refined with prompt text visible:
the probe's options are contentless self-referential labels ("Option A:
Format A / Option B: Format B," stated as scored exactly equivalent) — a
pure-deference construction that the subject model declines to engage rather
than a rendering defect; the model's "can't see the formats" objection is
factually apt. Supplements (does not revise) the 2026-07-21 fast-path
entry's defect-class characterization. Affected pairs drop from shift
computation per C3 and are reported; documented-adjustments round records
the finding, no re-administration (D34).

---

## 2026-07-21 — Thresholds locked at plan §1 step 4 (pre-unblinding); step-3 amendments; slot-A bias instrument finding

Plan §1 steps 1–3 executed in notebooks/pretest_analysis.ipynb against the
merged IV run (20260717_204822, instrument sha256 659afb97…018b), with a hard
ordering gate: no per-value aggregate, shift, resistance rate, or dominance
indicator existed at any point before this entry.

Step-1/2 instrument-level results. Calibration block (16 pairs): renormalized
p(A) mean 0.883 (sd 0.179, range 0.245–0.999) — **slot-A bias +0.383, 15/16
pairs favor slot A** — recorded as an instrument finding: it contaminates
level readings (hence the strict dominance null, working as designed) and
cancels in within-pair differenced Δ. Decline (low-mass) rate 81.2% (13/16);
all 13 greedy fallbacks parsed a letter in text and every parse agreed in
direction with the renormalized readout (directional validity at low mass).
Calibration captured mass: mean 0.309, median 0.254, range 0.074–0.705.
Calibration |logit p| distribution (recorded as exhibit, superseded as
criterion per A2): median 2.436, 95th percentile at the clamp bound 4.595.
Instrument-wide per-item mass (682 choice readings): mean 0.487, median
0.508; below 0.25/0.50/0.75 = 131 (19.2%) / 337 (49.4%) / 580 (85.0%); 0.5
bisects a dense mode (1.29× uniform); density below uniform only at floors
≤ 0.20 and ≥ 0.85.

Step-3 amendments (researcher-ratified, pre-unblinding; register D35):
(A1) §4.1 dominance operationalization confirmed — 95th percentile of the
pooled {p_A, p_B} calibration distribution = **0.997**. (A2) §4.3
calibration-derived OR cutoff not constructible from the administered design
(one presentation per calibration pair; counterbalancing across the block);
§3(b) replaced by **fixed OR ≥ 3.0** in the value-favored direction
(odds-scale equivalent of Δ = 0.25 at p₀ = 0.5), Δ ≥ 0.05 guard unchanged;
§6.3 reports OR ∈ {2, 3, 5}. (A3) Mass floor **0.5 → 0.20**: both §5 revision
conditions fired at 0.5; first-proposed 0.25 tripped the pre-stated density
guard (1.10× uniform); 0.20 is gap-seated (0.81×) and calibration-adjacent
(calibration median 0.254 within one bin width); 0.20 added to the §6.1
ladder.

**Locked criteria (§1 step 4):** resistance ≥ 0.80 on role_included_base
cells; choice dual criterion Δ ≥ 0.25 or (OR ≥ 3.0, value-favored, with
Δ ≥ 0.05 guard), value-level, mass-eligible non-ceiling pairs; dominance
> 0.997 for ceiling pairs (neutral mean p_vf > 0.8), dominance-alone path per
§4.2; captured-mass floor 0.20, minimum 2 eligible pairs else
indeterminate-deferred. Plan flipped DRAFT → RATIFIED. Unblinding (§1 step 5)
follows this entry.

---

## 2026-08-05 — D53 random-direction control: PASS at ceiling; D54 recapture bitwise-identical

Run: `results/comparators/20260803_202123_llama8b_refusal_recapture`
(pod clock; executed on the control-and-recapture pod under the two-pod
split). VERIFY PASS 21/21. Recorded by Claude Code from the pod session
outputs; researcher executed the runs.

**D54 recapture — bitwise reproduction of the lost tensor.** The fresh
capture's `activations_llama8b.pt` (167,867,711 bytes) has sha256
`704735d800ea…` — **identical to the original 20260730_180143 run's
tensor** recorded in `docs/data_locations.md` before the pod teardown
lost it. Same prompts, same model, different pod, fresh weights
download: full-pipeline anchor determinism at tensor scale. The
comparator's direction, reliability, and ablation results verifiably
rest on the same anchors as the original run.

**A3 fitted baseline (recapture):** harmful 0.9375 → 0.0625
(30/32 → 2/32), harmless 0.0 → 0.0 — the known shape reproduced
exactly; the pre-stated pause-point was not triggered.

**D53 control (five matched-norm random directions, seed 23, layer 12,
identical protocol):**

| direction | harmful baseline → ablated | harmless ablated | cos to fitted |
|---|---|---|---|
| r0 | 0.9375 → 0.9375 | 0.0 | +0.0202 |
| r1 | 0.9375 → 0.9375 | 0.0 | +0.0245 |
| r2 | 0.9375 → 0.9375 | 0.0 | +0.0031 |
| r3 | 0.9375 → 0.9375 | 0.0 | +0.0121 |
| r4 | 0.9375 → 0.9375 | 0.0 | −0.0119 |

**Judgment under the ratified threshold (run_configuration.md,
2026-08-05): PASS** — criterion required every random direction to
retain ≥ 24/32 harmful refusals; all five retained 30/32, the baseline
itself (zero effect). No degenerate outputs; no escalation band entered.
The ablation effect at layer 12 is direction-specific: removing the
fitted direction abolishes refusal (2/32), removing matched random
directions does nothing (30/32 × 5). The strongest remaining objection
to the refusal comparator (HANDOFF_v6 §Immediate open items) is retired;
Stage 3's separability claim may lean on the causally-validated
comparator per D52.

---

## 2026-08-06 — Robustness annex (post-hoc, researcher-directed): placebo clean; length flag FIRED

Motivation: researcher-directed too-good-to-be-true audit of the same-day
as-designed results (executive-chat brief, 2026-08-06). Both checks
exploratory, run after seeing results, filed in
`analysis/robustness_annex/` alongside — never mixed into — `as_designed/`.
Pre-stated interpretations recorded in the brief and in every artifact
header; results reported as landed, no iteration.

**Check 2 — placebo order-contrast through the identical pipeline: the
machinery is honest.** A direction fitted from the AB-vs-BA order contrast
(known real signal: the +0.383 position bias; zero conflict content),
pushed through the exact pipeline path. Placebo split-half 0.428 (vs null
p95 0.333 — real, as pre-stated tolerable), selected layer 14. On the real
opposition-vs-agreement contrast: **−0.35 SD at L8, +0.37 at its own
layer** — noise-scale against the conflict direction's 3.35. Transfer to
the refusal family: −0.57/−0.49 (L8), 0.15/0.11 (own layer) — null-scale.
cosine(placebo, conflict) at L8 = −0.05. The conflict direction's AB-vs-BA
projection difference = **−0.013 pooled-SD units** — order-averaging
cancelled position bias as designed. The pipeline does not flatter noise.

**Check 1 — surface-feature regression: FLAG, reported immediately per the
pre-stated rule.** Per-row L8 conflict projections (choice, open-ended,
n=480) regressed on prompt length (whitespace-token proxy) + anchor
entropy: **R² = 0.79, partial r(length) = 0.89**, entropy negligible
(partial 0.07). Opposition prompts are +40 tokens on average (≈129 vs 90 —
the shared opposition text, by design). **Separation 3.354 raw →
1.109 after residualization** — neither "substantially intact" nor
"collapsed to null": the bulk of the headline separation is carried by
variance a length regressor can absorb. Recorded caveats, both directions:
(i) residualization is conservative here — length is confounded with the
manipulation by design (the shared text that makes prompts long IS the
opposition content), so removing length removes real condition variance
too; (ii) conversely, a genuine length detector would reproduce existence,
transfer (refusal opposition is also longer), refusal-distinctness, and
emotion-irreducibility simultaneously, so none of the five as-designed
results adjudicates this on its own. The residual 1.11 SD exceeds
placebo-on-real scale (±0.35) — some non-length signal exists — but the
construct-vs-length question is now the study's live validity issue.
Disentangling requires design, not analysis iteration (length-matched
contrasts / length-controlled nulls); researcher's call on the follow-up.

---

## 2026-08-06 — Robustness annex part 2 (post-hoc): the length confound is deep; transfer is substantially contaminated

Motivation: decompose part 1's flag (researcher-directed; executive-chat
brief part 2). Both checks post-hoc exploratory, pre-stated
interpretations verbatim in artifact headers
(`analysis/robustness_annex/ANNEX_check3/4_*.json`); results as landed,
no iteration.

**Check 3 — within-condition length tracking.** Per-row L8 conflict
projections vs token length WHERE CONFLICT IS CONSTANT:

| family | cells | n | r | slope |
|---|---|---|---|---|
| choice | agreement pooled | 120 | **0.67** | 0.0053 |
| choice | opposition pooled | 120 | **0.79** | 0.0055 |
| choice | between-condition (restated) | 248 | 0.89 | 0.0091 |
| refusal | agreement pooled | 72 | **0.81** | 0.0063 |
| refusal | opposition pooled | 72 | **0.75** | 0.0046 |
| refusal | between-condition | 153 | 0.96 | 0.0073 |

Per-condition r's 0.46–0.84. Under the pre-stated rule this is the deep
arm, not the benign arm: the direction tracks length wherever length
varies, including agreement cells where conflict is absent by design.
Refusal-family lengths: opposition +52 tokens over agreement.

**Check 4 — pure length direction as comparator.** Fit on agreement cells
only (conflict absent throughout), unpaired long-vs-short median split
(92.5 tokens; pairing infeasible for a global split — stated departure),
same estimator/fold machinery. The length direction is strong in its own
right: selects L4, held-out separation 3.31, split-half 0.70 vs null 0.13.
(a) cosine(length, conflict): 0.19 at L8, 0.41 at L4 — moderate, per the
pre-stated note not itself damning. (b) reducibility: adding the length
direction lifts reconstruction of the conflict direction from 3.3% to
7.5% — as a vector the conflict direction is not mostly the length
direction. **(c) the sharp test: the length direction TRANSFERS** —
refusal opposition-vs-agreement at 1.92 SD (harm tier, L8; null p95 0.46)
and **2.58 SD at its own layer** (null 0.53); intermediate tier 0.53/1.24.
Conflict direction's transfer: 3.50/4.24. The pre-stated favorable arm
(noise-scale) is unavailable; harm-tier magnitudes reach 55–74% of the
conflict direction's. The transfer headline is substantially
contaminated and cannot ship without the length-matched follow-up.

**Validity status, plain terms:** the as-designed positive results cannot
currently be attributed to value conflict rather than prompt length — the
fitted direction substantially reads length where conflict is constant,
and length alone reproduces the majority scale of the transfer effect;
the affirmative claims are on hold pending a length-matched follow-up
design, while the measurement machinery itself stands validated (placebo
clean, D53 PASS, D54 bitwise, pipeline reproduction exact) and the
~1.1 SD residualized within-family separation remains the conservative
floor for any surviving construct signal.

---

## 2026-08-06 — Robustness annex part 3: length-matched subsample GATED OUT (infeasible at required power)

Motivation: the in-capture length-matched read of the part-2 flag
(researcher-directed; feasibility gates analysis, gate reported before any
separation). Artifact:
`analysis/robustness_annex/ANNEX_check5_length_matched.json`
(pre-stated interpretations, caution, and effect-scale note verbatim in
the header). No separation was computed — the gate stopped Stage B.

**Stage A feasibility, as landed** (MDES = 2.802·√(2/n), α=.05, power .80;
gate: MDES ≤ 1.0 SD, the part-1 residualized floor being the effect scale
of interest):

| family | overlap (tokens) | pair-matched n (same-scen) | MDES | stratified n | MDES | gate |
|---|---|---|---|---|---|---|
| choice | 70–120 | 14 (3) | 1.06 | 12 (4 strata) | 1.14 | **FAIL** |
| refusal T7–9 | 115–138 | 7 (0) | 1.50 | 5 (2) | 1.77 | **FAIL** |
| refusal T10–12 | 139–144 | 2 (0) | 2.80 | 0 | — | **FAIL** |

The choice family misses the gate narrowly (1.06 vs 1.00 at 14 pairs, 11
of them cross-scenario); the refusal tiers are far from feasible — their
opposition/agreement length distributions barely overlap (the +52-token
design gap). Per the pre-stated rule an underpowered null would be worse
than no check; Stage B is GATED OUT for all families. No
tolerance-widening or design adjustment was attempted (that would be the
forbidden iteration).

**Validity status, appended to part 2's sentence (not replacing it):**
…and the in-capture length-matched check is infeasible at the required
power, so the length-matched follow-up battery is the sole remaining path
to adjudicating construct vs length. Design note for that follow-up, from
Stage A's own numbers: the overlap windows (choice 70–120; refusal
115–138 / 139–144) quantify exactly how much agreement cells must
lengthen — or opposition slim — for a powered in-battery match.

---

## 2026-08-06 — Robustness annex part 4 (optional, interpretive): SAE read — weak color, one hard limitation; nothing rehabilitated

Coverage (gate): base-trained Llama-Scope L8R-8x (JumpReLU, 32,768
features) at exactly our anchor hook; instruct-trained SAE exists only at
L19 (Goodfire) — 11 layers off-band, base-at-L8 preferred per brief.
Labels: Neuronpedia `8-llamascope-res-32k`. Standing caveat in every
header: base-model SAE on instruct activations is an approximation; SAE
feature names are auto-generated, suggestive never dispositive. Operative
conditional per parts 1–3: LANDED BADLY — this annex cannot rehabilitate
the direction, and does not.

**Decoder-side read (brief check 5).** Top-20 features by cosine:
conflict direction — specification/calculation-flavored (technical
terminology, mathematical proofs/legal frameworks, calculations,
uncertainty-or-negation), NOT deliberation-flavored; reconstruction
R²(top-20) = 0.20, which the pre-stated rule classifies as weak evidence,
so stated. Length direction: assorted, R² = 0.16. Refusal reference:
R² = 0.32 with a coherent known story (moral dilemmas and violent
actions, criminal behavior, content appropriateness, discomfort) — the
method shows a story where one exists. Overlaps: **conflict ∩ length =
5/20 features** (incl. "uncertainty or negation", technical-spec,
proofs/legal) — the direct confound read; conflict ∩ refusal = 0/20,
consistent with the geometric orthogonality.

**Encode-side read (brief check 6 + screening validation): UNINFORMATIVE
— the caveat materialized as a hard limitation.** All top-10 conflict
features and all label-screened candidates activate at ~0 on our anchors
(one marginal exception, 16259, opposition-only at 0.016). Likely cause:
the anchor is an instruct-template token position the base model never
sees; the base SAE does not fire there. Reported as a method limitation,
not worked around. Label-space screening itself succeeded — on-theme
candidates exist (11990 "dilemmas or conflicting choices", 3584
"moral and ethical dilemmas", 488 "tension") — but could not be
validated or falsified on our capture: an autointerp-caution outcome,
neither arm of the validated-hypothesis test reachable.

**Plain sentence for the presentation audience:** a base-model SAE read
at layer 8 offers only weak color — the conflict direction's nearest
features look like specification/calculation register rather than
deliberation, a quarter of its top features are shared with the pure
length direction, and the SAE cannot be driven by our instruct-template
anchors at all — so the feature-level question, like the length question,
awaits instruct-native tools; nothing in this annex changes the part-2/3
validity status.

---

## 2026-08-06 — Robustness annex part 5: residual depth profile — a modest length-independent component, living late

Post-hoc diagnostic, explicitly NOT layer re-selection (header so states).
Artifact: `ANNEX_part5_depth_profile.json` + figure. All 32 layers; four
curves (residualized choice separation; within-condition length r;
cos(conflict, length) natively per layer; residualized transfer, tiers
separate).

**The shape:** within-condition length tracking collapses with depth —
r ≈ 0.91–0.96 at L0–L6, 0.73 at L8, 0.43 by L12, and 0.12–0.30 from L19
on. The residualized choice separation peaks in the confounded band
(1.23 at L5; 1.11 at L8) and then settles onto a **flat ~0.70–0.76 SD
plateau from L12 through L31** — stable across twenty layers while length
tracking falls five-fold and cos(conflict, length) sits ≈ 0.2. This is
neither pre-stated arm exactly: the residual does not hold its peak, but
it does not track the length curve either — it decouples from it.

**Transfer's residual, by contrast, lives only in the confounded band:**
harm tier 1.11 at L4, ~0.9 at L6–L8, decaying to 0.1–0.2 late;
intermediate tier ~1.0 at L5–L6 drifting negative (−0.3) late. The
length-independent transfer component is modest everywhere and absent
exactly where the within-family component is cleanest.

**Hypothesis filed for the follow-up battery (never a revised result):**
a ~0.7 SD length-independent within-family opposition/agreement component
exists across mid-to-late depth (cleanest L19–L31, where within-condition
length tracking ≤ 0.3), not accompanied by cross-family transfer. The
follow-up battery should pre-state a late measurement layer alongside its
length-matched design and test exactly this. Validity status otherwise
unchanged from parts 2–3.
