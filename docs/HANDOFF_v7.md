# HANDOFF_v7 — pre-freeze snapshot

**Status: PRE-FREEZE SNAPSHOT, refreshed 2026-08-05. Supersedes HANDOFF_v6. Freeze state
to be appended post-freeze.** Nothing below describes a frozen battery — but everything
upstream of the freeze is now done: the batch is **applied**, the delta review is
**complete**, verdict integrity is **clean**, and the exhibit run is **finished on
freeze-candidate text**. What remains before freeze is the freeze itself; the freezer
still does not exist as code. When the freeze runs, append its state to this document
rather than rewriting the sections above it.

**Project:** llm-conflict-probing (Kaitlin Moore, CMU Heinz; advisor Dr. Sara Kingsley)
**Written:** Design chat, 2026-08-05.

**Boot order for a fresh instance:** this doc → `docs/decision_register.md` (now through
**D73**, plus §5 corrections and O18–O23) → `run_configuration.md` →
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
**Stage 2 is complete through the last pre-freeze gate.** All twelve types plus controls
were authored, reviewed, and edited: **394 edit operations** applied across the main
batch, the battery-wide semicolon batch, and two cell-targeted repairs; **425 unique
punctuation substitutions**, leaving **zero em dashes and zero semicolons in stimulus
text**; validator **PASS** (0 blocking, 0 warnings); **delta review complete** — 117
content cells read and all approved, 203 certified-mechanical cells spot-sampled, T11/T12
verdicts entered; **verdict integrity zero non-approve** across all 277 records; and the
**exhibit embedding run complete** on freeze-candidate text with trimmed anchors — all 13
topical controls positive, zero relative-diagnostic flags. **The refusal comparator for
Stage 3 is captured and causally validated** at layer 12, with its random-direction
control and the conflict layer-selection criterion both ratified. What remains: **freeze**
→ pod session → run → analysis → write-up. Welfare claims, steering, and a second
architecture are deferred to future work.

---

## The battery — as built

**66 scenarios, 13 topical controls — 264 battery cells + 13 controls = 277 records.**
*(Corrected: HANDOFF_v6 said 64 scenarios and 10 controls. The validator's "277 cells
checked" line mislabels records as cells; the cell count is 264. Basis:
`docs/battery_validation_report.md` per-file counts; register §5.)*

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

**Punctuation conventions, battery-wide:** **zero em dashes, zero semicolons** in
stimulus text (D61, D68). Scope is stimulus text only — anchor texts are analysis-side
reference and keep their definitional `Pull toward X; against Y` semicolons.

**Options invariant:** `option_A`/`option_B` exist and are byte-identical across a
scenario's four cells, enforced by blocking validator check c2 (D70).

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
   once**. **Confirmed and applied 2026-08-05** — as-built totals in item 9.
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
9. **Batch applied** (`docs/batch_apply_report_2026-08-05.md`). Cumulative: **394 edit
   operations** = 352 main batch (350 + the Meera and Arun renames) + 40 semicolon batch
   + 2 cell-targeted repairs; **425 unique-location punctuation substitutions** = 358 em
   dashes + 27 authorial semicolons in dash-touched sentences + 40 battery-wide
   semicolons. Per-cell: 583 em dashes and 113 semicolons removed. **Stimulus text now
   carries zero of either** (**D68**). Mechanical certificates: dash-only 134/134,
   dash+rename 10/10, semicolon-only 59/59.
10. **Two pre-existing defects found and repaired** (**D69**) — T4 CB-lh-S2 `agree_A`
   with a missing `option_A` cell and T1 CB-hc-S2 `agree_A` whose option aliased the
   insert's shared string. Both are **review-pass Excel damage, proven pre-batch** from
   the backups by replay-bisection; both repaired by **cell surgery**, both read and
   approved in delta review under a named `post-review-repair` class. The class is closed
   going forward by the new **options-uniformity check (c2, permanent, blocking)** —
   `option_A`/`option_B` must exist and be byte-identical across a scenario's four cells
   (**D70**); suite **219 OK**.
11. **Delta review complete** — **117 content cells** (A7 39, A5/A6 48, A9 24, A10 3,
   A2-wording 1, post-review repair 2), **all approve**; 203 certified-mechanical cells
   on the spot-sample tier; **T11/T12's 46 verdicts entered** in this pass.
   **Verdict integrity: zero non-approve tokens battery-wide** — 264 cells + 13 controls
   = 277 records, all exactly `approve`, so an approve-only freeze drops nothing
   (`docs/verdict_integrity_2026-08-05.md`). The pass touched verdicts only: 0 of 277
   records differ in any stimulus field from the applied-batch state.
12. **Anchors trimmed and the exhibit run completed** — authority and mercy trimmed by
   **pure deletion** of flagged non-semantic spans, provenance flipped in the anchors
   file, other 14 verbatim (**D71**, closing O20). Exhibit run on freeze-candidate text:
   **all 13 controls positive, zero relative-diagnostic flags**. The **relative
   within-value z-standardized diagnostic (z ≥ 2.0) is now the operative screen**; the
   absolute tripwire is non-discriminative because authoring rule 7 floors own-pole
   similarity (**D73**, amending D56). Still descriptive, never gating.
13. **Model-judge second opinion DROPPED** (**D72**, closing O21) — explicitly, with the
   independence it would have added recorded as a write-up limitation.

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

**Blocking the freeze: nothing.** Freeze-checklist steps 1–7 are all green — batch
applied, re-ingested, re-validated PASS, delta review complete, verdict integrity clean,
exhibit run done on freeze-candidate text with trimmed anchors. **Step 8, the freeze
itself, is the next action**, and the freezer still has to be built: approve-only rows
(all 277 qualify), sha over the frozen set, both option orders generated for choice items.
The freezer-hardening recommendation stands — strip, validate tokens, report drops loudly
— even though today there is nothing to drop.

**Pending pod trip (D53 + D54), one session — both ratified, nothing left to decide
before it runs:**

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

**Other OPEN (register §3), now two:** **O22** run-configuration decisions — all four
appear settled in `run_configuration.md` but are **not yet transcribed into register
entries**, so this stays open as a backfill task; **O23** the reliability gate's numeric
threshold — open per `run_configuration.md`'s own list, to be pre-stated before
unblinding. (O18, O19, O20 and O21 all closed 2026-08-05 — see D53, D66, D71, D72.)

---

## Critical path to done

1. ~~Confirm the dry-run report~~ — **done 2026-08-05.**
2. ~~Apply batch → re-ingest → re-validate~~ — **done**; all 16 blocking hits cleared,
   two pre-existing defects found, repaired, and re-validated to **PASS**.
3. ~~Changed-cell delta review~~ — **done**; 117 content cells all approve, T11/T12
   verdicts entered.
4. ~~Verdict-integrity report → exhibit embedding run~~ — **done**; zero non-approve,
   all 13 controls positive, zero relative-diagnostic flags, trimmed anchors in use.
5. **Freeze — the next action.** — approve-only rows, sha over the frozen set, both option orders for choice
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
- **The embedding exhibit is descriptive, never gating** (D56, D73). It flags; it does
  not fail anything. Its value-anchor comparison is one-sided — a third-value tripwire,
  never a presence check on a cell's own poles — and the operative screen is the
  **relative** within-value z-standardized diagnostic (z ≥ 2.0), because rule 7 floors
  own-pole similarity and makes any absolute threshold non-discriminative.
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
