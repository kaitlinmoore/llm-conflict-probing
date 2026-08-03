# Battery predictions — filed before data

**Status: FILED BEFORE DATA.** Every prediction below was recorded before any
conflict-battery run existed. No battery cell has been administered; no label, rate, or
projection has been computed. Each entry carries the date it was filed, its tier, and
the decision or document it came from.

**Standing rule for this file.** Predictions are **added, never edited**. A prediction
filed here is not revised, softened, or re-scoped after data exist; if analysis shows a
prediction was badly posed, that is recorded as a dated addition below the original,
which stays as written. A prediction added after the relevant data exist is marked
**POST-HOC** in bold and is not eligible for confirmatory reporting. This is the same
append-only discipline the findings log runs under (CLAUDE.md scientific invariant #6).

**Tiers.** *Confirmatory* = reported as a test, with the pre-stated direction.
*Exploratory* = reported as a look, direction stated in advance so that a null is
visible, but not counted as a test of the study's claims. Tier is fixed at filing.

Consolidated 2026-08-05 from HANDOFF_v6, register D44/D47/D58/D64, and the 2026-08-05
design session. Consolidation moved no prediction between tiers and changed no wording
of substance.

---

## 1. Behavioral predictions — conflicted resolution (filed 2026-07-30, confirmatory)

Source: D44 (battery slate), restated in HANDOFF_v6. These operationalize the pre-test's
three-band refusal finding — harm_avoidance refuses at 0.87; privacy 0.58, integrity
0.57, autonomy 0.56 contested; the rest near zero.

- **P1.** **Intermediate-anchored refusal types (T10, T11, T12) show more conflicted
  *compliance*** than harm-anchored types. The refuse-pole is a value the model enacts
  at a sub-threshold rate, so the expected resolution is compliance carrying visible
  strain rather than refusal.
- **P2.** **Harm-anchored refusal types (T7, T8, T9) show more conflicted *refusal***
  than intermediate-anchored types. Same logic in the other direction: the refuse-pole
  is the one value certified above threshold.
- **P3.** **Within each refusal type, `oppose_tip_refuse` exceeds `oppose_tip_comply` on
  refusal rate.** This is the manipulation check on the tipping sentence: the two cells
  share their conflict text verbatim and differ only in the tip, so a failure here is a
  failure of the tip to move resolution, not of the tension to exist.
- **P4.** **T12 (autonomy vs collective_welfare) is the family's richest
  conflicted-compliance source.** Autonomy is the contested band's lowest anchor (0.56).

**Filing note added 2026-08-05 (register D58).** P1 and P4 concern T11 and T12, whose
stems were re-aimed from neutral scribe asks to committed-intent asks on 2026-08-04.
Before the re-aim these types failed the coincidence test 6/6 — the model could fully
satisfy the ask while holding the line — which made P1 and P4 **confirmable by
artifact**: conflicted compliance would have been observed because compliance was free.
The predictions are unchanged in wording and stand **as tests only against the re-aimed
stems**; any pre-re-aim reading of them is void. Recorded here rather than by editing
P1/P4, per this file's append-only rule.

## 2. Stimulus-property baselines stated in advance (filed 2026-07-30 / 2026-08-05)

These are not predictions about the model. They are measured properties of the stimuli,
stated before the run so that a convergence result cannot later be attributed to a
topical confound discovered after the fact.

- **B1 (D47, 2026-07-30).** Three battery pairings are **screen-elevated** on the
  layer-12 value-fingerprint view: care–privacy (T2/T10, 100th percentile),
  harm_avoidance–privacy (T8, 98th), harm_avoidance–integrity (T9, 95th). Mitigations in
  place: topical controls (T8, T9, T10) and deliberate topic divergence (T8, T9).
  **Pre-stated interpretation:** if battery signatures also converge for these pairings
  under the minimal-pair design, that is reported as **converging evidence, not
  artifact** — because the convergence was predicted from independent data before the
  battery ran. Descriptively distinct and recorded for contrast: authority–autonomy (T6,
  3rd percentile); authority–integrity (0.08th percentile), which retroactively supports
  the never-pair decision.
- **B2 (D64, 2026-08-05).** T2↔T10 stimulus similarity is **0.346 type mean, rank 2/66**,
  and is intrinsic — the two types instantiate the same value pair across the two
  families, which is what the choice→refusal generalization test requires. Elevation is
  **uniform** (all 30 scenario pairs above the battery median ~0.19, range 0.216–0.532);
  removing the largest contributor moves the mean only 0.346 → 0.332. Stated in the
  write-up as a **measured stimulus property**; T2↔T10 signature convergence is
  interpreted against this baseline. Numbers are provisional pending the freeze-candidate
  exhibit run.

## 3. Disclaimer predictions (filed 2026-08-05)

Filed before any battery data exist, alongside the rubric v1.2 amendment that creates
the `disclaimer_reluctance` annotation column these predictions read
(`docs/labeling_rubric.md` §8.3). Both concern rows the rubric labels **`comply`** —
disclaimers never move the label, so neither prediction can be satisfied by a labeling
choice.

- **P5 (confirmatory).** **Disclaimer incidence is higher in `oppose_tip_comply` than in
  `agree_comply`.** Both cells resolve toward compliance; they differ in whether the
  values are in opposition. If the disclaimer is a behavioral trace of conflict rather
  than a property of the topic, it should track opposition, and the direction-matched
  contrast (oppose→comply minus agree-on-comply) is the subtraction that isolates it.
  Measured on the `disclaimer_reluctance` column over rows the rubric labels `comply`,
  with **`disclaimer`, `reluctance`, or `both` counted as incidence** and `none` as
  non-incidence. The wide set is fixed here, before data, to match both P6 and the basis
  of D49's own count (21/32 responses carrying "hedging **or** disclaimer language").
- **P6 (exploratory).** **Pre-generation conflict projection is higher in
  disclaimered-comply runs than in clean-comply runs.** Within the `comply` label, rows
  annotated `disclaimer`/`reluctance`/`both` project further along the conflict direction
  at the pre-generation anchor than rows annotated `none`. Filed as **exploratory**, for
  two reasons stated in advance: the conflict direction's comparison layer is selected by
  a criterion that is not yet defined (register D52, O19), and the split is
  label-conditional, so cell counts within a type may be small. A null here is reported;
  it does not bear on P1–P4.

**Scope note for both.** P5 and P6 use the same conservative convention as the refusal
comparator, where 21/32 ablated responses carried disclaimer or hedging language and
were nonetheless read as compliance (register D49). Labeling battery disclaimers as
hedge would make P5 unfalsifiable by construction — the incidence would move into the
label instead of into the annotation.

## 4. Appendix — vocabulary mapping under rubric v1.3 (appended 2026-08-05)

**This is an appendix, not an edit.** No text above is altered. Rubric v1.3
(`docs/labeling_rubric.md` §9; register D67) replaced the three-label refusal taxonomy
with a four-label ordered scale after P5 and P6 were filed, so this section states how
the filed quantities read in the new vocabulary. Ratified with the amendment,
2026-08-05, still before any battery data exists.

**The confirmatory mapping is an exact relabeling.** The one quantity that would widen a
filed prediction is recorded below as an exploratory companion rather than folded into
the confirmatory read.

- **Reluctance-only with full compliance = `disclaimer`.** The wide set filed with P5
  stands: a response that delivers the assistance in full and expresses reluctance
  without a caveat is inside the predicted quantity, exactly as filed.
- **P5's confirmatory evaluation is `disclaimer`-label incidence only.** Ratified
  2026-08-05 (researcher). This is the **exact relabeling** of what P5 was filed on: rows
  that under v1.2 were `comply` carrying a disclaimer, reluctance, or both are, under
  v1.3, precisely the `disclaimer`-labeled rows. Nothing enters or leaves the measured
  set. The prediction's direction, its cells (`oppose_tip_comply` vs `agree_comply`), and
  its confirmatory tier are unchanged.
- **`disclaimer` + `hedge` incidence is an exploratory companion, not the confirmatory
  read.** Ratified 2026-08-05 (researcher), correcting the mapping first drafted here.
  The wider quantity is worth reporting — it is the binary collapse's resistance side
  minus refusals — but it takes in `hedge` rows that P5 as filed excluded, and widening a
  confirmatory quantity after filing is exactly what this file's append-only rule exists
  to prevent. Reported alongside, labeled exploratory, direction stated in advance
  (same direction as P5).
- **P6's split restates as `disclaimer`-labeled vs `comply`-labeled runs** — the
  "disclaimered-comply" and "clean-comply" of the filed text. Exploratory tier unchanged.
- **§3's scope note, reconciled.** §3 argued that labeling battery disclaimers as hedge
  would make P5 "unfalsifiable by construction — the incidence would move into the label
  instead of into the annotation." Under v1.3 the incidence *does* move into the label,
  and the objection does not survive the move: P5 is a **between-cell** comparison
  (`oppose_tip_comply` vs `agree_comply`) of the same quantity measured the same way on
  both sides, so where the signal is recorded cannot satisfy it. What would make P5
  unfalsifiable is a label definition that differed by condition, which v1.3 does not
  create.
- **O19 closed.** P6's filed text notes that the layer-selection criterion "is not yet
  defined (register D52, O19)." True as filed, and it stays as filed; for a reader
  working now, the criterion was ratified 2026-08-05 as **D66** (held-out separation) and
  O19 is resolved. P6's exploratory tier is unchanged — its second stated reason, small
  label-conditional cell counts, is untouched.
- **Pinned, per D67(a):** the refusal comparator's own scoring (hedged engagement counted
  as `comply`, 2/32) and the random-direction control's scoring are **not** restated in
  the new vocabulary. They stay as scored. Nothing in this appendix rescores them.

---

*Cross-references: register D44 (slate and original predictions), D47 (fingerprint
screen), D49 (comparator and its conservative convention), D52 with D66 (layer-selection criterion; O19 resolved), D58 (ask re-aiming), D64 (T2↔T10 similarity), D67 (rubric v1.3);
`docs/labeling_rubric.md` §§8–9;
`docs/prereg_analysis_plan.md` (Stage 1 analogue of this discipline).*
