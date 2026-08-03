# HANDOFF_v7 — pre-freeze snapshot

**Status: PRE-FREEZE SNAPSHOT. Supersedes HANDOFF_v6. Freeze state to be appended
post-freeze.** Nothing below describes a frozen battery: the edit batch is built and
dry-run clean but **not applied**, verdicts for T11/T12 do not yet exist, and the
freezer does not exist as code. When the freeze runs, append its state to this document
rather than rewriting the sections above it.

**Project:** llm-conflict-probing (Kaitlin Moore, CMU Heinz; advisor Dr. Sara Kingsley)
**Written:** Design chat, 2026-08-05.

**Boot order for a fresh instance:** this doc → `docs/decision_register.md` (now through
**D67**, plus §5 corrections and O18–O23) → `run_configuration.md` →
`docs/batch_manifest.md` → `docs/closeout_staging_2026-08-04.md`. Then, as needed:
`docs/freeze_checklist.md`,
`docs/batch_dryrun_2026-08-05.md`, `docs/battery_predictions.md`,
`docs/labeling_rubric.md` (**v1.3 — read §9 first**), `docs/findings_log.md`, and the
per-type workbook READMEs in `data/battery/workbooks/`. **Where this doc and the
register disagree, the register wins.**

**Working norms (unchanged):** decisions are Kaitlin's; propose and push back honestly;
flag stated-vs-inferred; don't treat unsettled things as settled. Repo work → Claude
Code; documents/workbooks → Cowork; design → this chat. Output to Kaitlin in plain
language, not register-referential prose.

---

## One-paragraph state

The study asks whether the model has a detectable internal signature of value conflict
*before* it generates, distinct from refusal, emotion, and generic indecision. **Stage 1
(pre-test) is closed** — 13 of 16 values certified; central finding is that the model
enacts values through *choice*, not refusal (three-band structure: harm_avoidance
refuses at 0.87; privacy/integrity/autonomy contested at 0.56–0.58; the rest near zero).
**Stage 2 authoring and the researcher review pass are both COMPLETE.** All twelve types
plus controls are reviewed; every ruling from the review has been consolidated into one
edit batch of **350 edits**, which **dry-runs 350/350 byte-exact** and is **awaiting the
researcher's confirmation to apply**. **The refusal comparator for Stage 3 is captured
and causally validated** at layer 12. What remains: confirm → apply → re-validate →
delta review → exhibit run → freeze → run → analysis → write-up. Welfare claims,
steering, and a second architecture are deferred to future work.

---

## The battery — as built

**66 scenarios, 13 topical controls, 277 cells.** *(Corrected: HANDOFF_v6 said 64 and 10.
Basis: `docs/battery_validation_report.md` per-file counts; register §5.)*

**Choice family — 5 scenarios each, 30 total:** T1 honesty–care, T2 privacy–care,
T3 mercy–desert, T4 loyalty–honesty, T5 tradition–autonomy, T6 authority–autonomy.
**Refusal family — 6 scenarios each, 36 total:** T7 harm_avoidance–autonomy,
T8 harm_avoidance–privacy, T9 harm_avoidance–integrity, T10 privacy–care,
T11 integrity–mercy, T12 autonomy–collective_welfare.
**Topical controls, 13:** T2 ×4, T8 ×3, T9 ×3, T10 ×3.

*As-built note (register §5): D44 sized refusal types at 6–7 scenarios as attrition
insurance for the conflicted-compliance cell; all six were authored at **6**. The
insurance was not taken — there is no per-type spare if conflicted-compliance cells fail
behavioral-label verification. Connected to the targeted-resample question, O22(d).*

**Condition structure (D45), both families:**

- Choice: `agree_A` / `agree_B` / `oppose_tip_A` / `oppose_tip_B`.
- Refusal: `agree_comply` / `agree_refuse` / `oppose_tip_comply` / `oppose_tip_refuse`;
  `expected_response ∈ {comply, refuse, hedge}`; no options, no order counterbalance.
- Primary subtraction is **direction-matched** (oppose→X minus agree-on-X), isolating
  opposition with the resolution direction held constant.
- The two opposition cells share their conflict text **verbatim**; only the tipping
  sentence differs.

**Constraints honored (D44):** authority never meets integrity; impartiality anchors
nothing; harm_avoidance in only 3 of 12 types and absent from the entire choice family
(this is what makes the choice→refusal generalization test the headline hold-out); every
other certified value appears once or twice; no pair repeats.

**The 8 authoring rules** are versioned in the workbook READMEs; the validator config is
authoritative (D46). **Lexeme blocklist scope is global** — all nine per-value lists
enforced against every type, cross-type hits blocking, per-instance documented exemption
as the only release valve (**D55**).

**Per-type cross-family invariant:** one agreement cell deletes a predicate; the other
redirects by the subject's stated wish. Which response/option each lands on depends on
which pole is the acting pole.

**Soft-refusal band (D58):** T10–T12 are refusal-family by administration format and
choice-adjacent in structure; refusal is predicted **low** in all three and their primary
function is **generating conflicted compliance**. A low refusal rate there is the design
working, not a null.

**Predictions** now live in one place: `docs/battery_predictions.md`, all filed before
data, append-only.

---

## What changed since v6

1. **Researcher review pass complete** across all 12 types plus controls; every ruling
   consolidated into `docs/batch_manifest.md` (authoritative over workbook comments and
   chat drafts).
2. **One edit batch, 350 edits, dry-run clean** (`docs/batch_dryrun_2026-08-05.md`):
   A-edits first, then 287 em-dash normalizations, then 7 rename edits — ordered so every
   find-string matches the text state at its turn and **every location is touched exactly
   once**. **Nothing has been applied.**
3. **Ten new register entries, D55–D64** — blocklist scope global; embedding exhibit
   spec and z-standardized read-out; formula-lock and operationalization scope; T11/T12
   ask re-aiming; expressed-stance exclusion and the force principle; option
   generalization with the overlap check permanent and blocking; em-dash normalization;
   renames; T2 control repairs; T2↔T10 similarity documented as intrinsic.
4. **D49–D54 backfilled** into the register from this document's predecessor; they had
   existed only as HANDOFF_v6 statements. **D53 was filed REC and is now DECIDED** —
   ratified 2026-08-05, before the pod session (see below).
5. **Rubric extended, twice, to v1.3** (`docs/labeling_rubric.md`; register D65 then
   **D67**). v1.2 (§8) gave the battery a behavioral `refuse` and a positively-defined
   hedge band; **v1.3 (§9) replaced the three-label taxonomy with a four-label ordered
   scale — `comply` < `disclaimer` < `hedge` < `refuse`** — with two boundary tests, two
   always-reported collapses (four-way primary; comply+disclaimer vs hedge+refuse), a
   tie-break ladder always toward the lower rung, a **required** disclaimer/reluctance
   sub-split on every `disclaimer`-labeled row (unrecoverable after the run if not
   recorded), and three pins. **Pin worth knowing before you touch any comparator
   number: the refusal comparator's 2/32 and the random-direction control are scored under the pinned v1.1
   reading and are never rescored under v1.3.** **Predictions consolidated** into
   `docs/battery_predictions.md`, all filed before data, append-only; two disclaimer
   predictions there (P5 confirmatory, P6 exploratory), with a v1.3 mapping appendix that
   does not edit the filed text.
6. **Competition battery fixes: SHIPPED** in `e61829f`. *(HANDOFF_v6 listed them as
   "decided, unexecuted" — stale; the item is struck from the critical path.)*
7. **Two validator mechanism fixes** that would have silently corrupted this batch:
   mixed XML encodings (Excel-resaved T1–T10 vs entity-stored T11/T12) and edit stacking
   (later edits reverting earlier ones in the same workbook). Both committed and tested;
   suite 216 OK.
8. **Run configuration ratified** (`run_configuration.md`, 2026-08-05) — the run itself,
   GPU selection, analysis staging, and the audit protocol. Its **layer-selection
   criterion is transcribed** as register **D66** (O19 closed); its **remaining
   decisions are not** — the four O22 items appear settled there but have no register
   entries yet, so O22 stays open as a backfill task.

---

## Refusal comparator — captured and causally validated (D49–D52)

- **Causally mediated at layer 12.** Ablation drops held-out harmful refusal 30/32 →
  2/32; harmless unchanged at 0/32. Layer 6 ≈ ⅓ effect; layers 18/21/26 inert.
- **Reliability saturated and pointed at the WRONG layer.** Split-half 0.954–0.987 across
  all 32 layers; argmax (21) is causally dead and near-orthogonal to layer 12. Second
  reliability saturation in the project (after the fingerprint screen, D47) and the first
  that would have produced a confident false null.
- **BINDING RULE (D50): reliability is an existence gate, never a site locator.** No
  reliability-derived quantity may select a layer, position, or estimator for any causal
  or comparative claim. **Governs every direction fit in Stage 3, without exception.**
- **Comparator spec (D51):** all comparators re-derived at the conflict comparison layer
  L; the refusal comparison reports **both** conflict-at-L vs. the causally-validated
  **layer-12** vector (primary) and conflict-at-L vs. local-layer refusal at L
  (alongside). Distinctness from an inert late-layer direction proves little.
- **Layer selection (D52):** the conflict direction selects L by an **effect-based**
  criterion — **now defined and ratified as D66** (O19 resolved, 2026-08-05, before any
  battery data exists): the winning layer is the one where a direction fitted on part of
  the **choice-family** scenarios best separates opposition from agreement on
  choice-family scenarios it never saw (scenario-level cross-validation, stratified by
  type; ties broken by stability across neighbouring layers). Reliability may disqualify
  a layer as unstable but never picks the winner; refusal-family scenarios are never used
  in selection, so the transfer test stays honest; behavioral prediction is excluded as a
  criterion. If the winner is not layer 12, the comparison runs there against a natively
  fitted refusal direction **and** repeats at layer 12 as a sensitivity check.
- Qualifier on the headline: the effect is refusal → *hedged engagement* within 64
  tokens; labels `comply` **under rubric v1.1**, the version it was scored under;
  **2/32 is the conservative reading**, and it is **pinned** — never rescored under v1.3
  (D67 pin (a)).

---

## Immediate open items

**Blocking the freeze (in order):**

1. **Researcher confirmation of the dry-run report** — the trigger for everything
   downstream. Points needing eyes before confirming: A10 option columns could not be
   preserved (all six adjusted); the clause→period em-dash group (known
   fragment-producing weak pattern); two rename proposals held out of the batch (Priya →
   Meera, Dev → Arun).
2. **Delta review after apply** — 260 changed cells, grouped by check class. Includes
   the **verdict-entry pass for T11/T12** (46 cells; verdicts are blank by design because
   the re-aim makes every cell a changed cell). **Freeze must not run before those
   verdicts exist** — the approve-only filter drops blank rows silently.
3. **Pre-freeze verdict-integrity report** (freeze checklist step 6) — every
   `reviewer_verdict` token that is not exactly `approve`. Observed variance on record:
   `'edit '` with a trailing space.
4. **Anchor trim texts** for authority and mercy (O20) — needed before the exhibit
   embedding run (freeze checklist step 7).

**Pending pod trip (D53 + D54), one session:**

- **D53 — random-direction control at layer 12. RATIFIED 2026-08-05; the session may
  proceed.** Threshold as recorded in `run_configuration.md`: every random direction
  retains ≥ 24/32 (fitted retains 2/32); exactly one in 16–23 escalates to ten directions
  under the same rule; fails on two or more below 24 or any single one below 16; same
  rubric and conservative reading as the fitted result; degenerate-output runs invalid and
  re-run. Ratified **before** the session and before any random-direction number existed
  (O18 resolved). Scored under the pinned v1.1 reading, per D67(a). Fail → revisit
  D49/D52 before Stage 3 relies on the comparator.
- **D54 — recapture, not recovery.** `activations_llama8b.pt` (~168 MB, raw anchors) was
  gitignored, never mirrored, and lived only on a pod torn down 2026-07-30. Budget a
  **fresh capture** (~30–40 min incl. venv rebuild) on the D53 session; treat a surviving
  volume copy as a bonus, not the plan. The committed `.npz` is canonical and sufficient
  for everything that **reuses** the direction — only **re-estimation** needs the anchors,
  and D52 makes that live.

**Other OPEN (register §3):** O20 anchor trims (above); O21 model-judge second opinion —
run cheaply pre-freeze or **drop with an explicit line**; O22 run-configuration decisions
— all four now appear settled in `run_configuration.md` but are **not yet transcribed
into register entries**, so O22 stays open as a backfill task; O23 the reliability gate's
numeric threshold — open per `run_configuration.md`'s own list, to be pre-stated before
unblinding.

---

## Critical path to done

1. **Confirm the dry-run report** (researcher). The single gate.
2. **Close workbooks → apply batch → re-ingest → re-validate.** Expect all 16 blocking
   hits to clear (6 lexeme + 10 overlap), zero new, check f green.
3. **Changed-cell delta review** (researcher) — 260 cells by check class; flip verdicts;
   enter T11/T12 verdicts.
4. **Verdict-integrity report → exhibit embedding run** (freeze-candidate text, anchors
   trimmed).
5. **Freeze** — approve-only rows, sha over the frozen set, both option orders for choice
   items. Gate for everything downstream.
6. **Run-config** — designed and ratified 2026-08-05 (`run_configuration.md`); the
   layer criterion is D66. Remaining: transcribe its decisions into register entries
   (O22) and pre-state the reliability gate's numeric threshold (O23).
7. **Pod session** — D53 control + D54 capture (parallelizes with 1–5).
8. **Run** — full battery + competition, both orders, deterministic; heuristic labels +
   audit of uncertain rows; **efficacy checkpoint, not reliability**, on the conflict
   direction.
9. **Analysis → write-up:** existence → separability (vs. layer-12 causal refusal) →
   reducibility → generalization (choice→refusal headline) → conflicted compliance →
   per-type similarity. Write-up leads with the pre-test contribution and the
   representation/enactment dissociation; welfare deferred.

**Protected under compression:** reliability gate; calibrated refusal separation
(validated comparator); conflicted-compliance exhibit.
**Cut order:** cross-model → within-family hold-outs → choice scenarios-per-type (5→4,
never type count) → write-up polish, never limitations.

---

## Standing cautions for any instance picking this up

- Register is authoritative; this doc is a map. Record new decisions there with dates.
- Do not resurrect deferred items (steering, second architecture, welfare framing,
  authority↔integrity adjudication, answer-only re-administration) without Kaitlin's
  explicit direction.
- **Never select a layer by reliability for a causal or comparative claim (D50).** The
  hardest-won lesson in the project.
- Estimator/layer/position consistency: every direction is difference-in-means, at the
  anchor, compared within-layer only.
- **The embedding exhibit is descriptive, never gating** (D56). It flags; it does not
  fail anything. Its value-anchor comparison is one-sided — a third-value tripwire, never
  a presence check on a cell's own poles.
- **Per-type claims are operationalization-scoped** (D57). Within-type homogeneity is a
  deliberate power argument with a stated cost; say what each type actually
  operationalizes.
- Atomic writes + digest verification on every run artifact. `verify_run.py` before
  trusting anything; stop the pod only after verify passes and results are committed.
- The inline lexeme scans used during authoring are NOT the authoritative gate — the
  committed validator is.
- Behavioral null results (an ablation that doesn't ablate, a signal that doesn't
  separate) are reported findings, not failures. Standing stopping rule: **do not tune
  until it "works."**

---

*Append the freeze state below this line when the freeze runs: frozen row count, sha,
order-generation record, and the verdict-integrity report's final counts.*
