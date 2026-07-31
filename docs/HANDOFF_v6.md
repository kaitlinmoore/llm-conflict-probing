# HANDOFF_v6 — Stage 2 authoring complete; refusal comparator validated

**Project:** llm-conflict-probing (Kaitlin Moore, CMU Heinz; advisor Dr. Sara Kingsley)
**Written:** Design chat. Supersedes HANDOFF_v5.
**Boot order for a fresh instance:** this doc → `docs/decision_register.md` (through D54) → `docs/findings_log.md` → `docs/WEEK_PLAN_stage2.md` → the per-type workbook READMEs in `data/battery/workbooks/`. Where this doc and the register disagree, the register wins.

**Working norms (unchanged):** decisions are Kaitlin's; propose and push back honestly; flag stated-vs-inferred; don't treat unsettled things as settled. Repo work → Claude Code; documents/workbooks → Cowork; design → this chat. Output to Kaitlin in plain language, not register-referential prose.

---

## One-paragraph state

The study asks whether the model has a detectable internal signature of value conflict *before* it generates, distinct from refusal, emotion, and generic indecision. **Stage 1 (pre-test) is closed** — 13 of 16 values certified; central finding is that the model enacts values through *choice*, not refusal (three-band structure: harm_avoidance refuses at 0.87; privacy/integrity/autonomy contested at 0.56–0.58; the rest near zero). **Stage 2 (conflict battery) authoring is COMPLETE** — all 12 tension types drafted, awaiting Kaitlin's review pass. **The refusal comparator for Stage 3 is captured and causally validated.** What remains: review → freeze → run → analysis → write-up. Welfare claims, steering, and a second architecture are deferred to future work.

---

## The battery — 12 types, authored, awaiting review

Each type: one workbook in `data/battery/workbooks/`, 5–6 scenarios × 4 cells, plus topical controls where flagged. All machine-verified for lexeme blocklists, shared-text byte-identity, and name uniqueness — but **Code's committed `validate_battery.py` is the authoritative gate before freeze, not the inline scans used during authoring.**

**Choice family (5 scenarios each):** T1 honesty–care, T2 privacy–care, T3 mercy–desert, T4 loyalty–honesty, T5 tradition–autonomy, T6 authority–autonomy.
**Refusal family (6 scenarios each):** T7 harm_avoidance–autonomy, T8 harm_avoidance–privacy, T9 harm_avoidance–integrity, T10 privacy–care, T11 integrity–mercy, T12 autonomy–collective_welfare.

**Condition structure (both families) — the 2×2 (D…, supersedes the advisor-reviewed structure):**
- Choice: agree_A / agree_B / oppose_tip_A / oppose_tip_B.
- Refusal: agree_comply / agree_refuse / oppose_tip_comply / oppose_tip_refuse; `expected_response ∈ {comply, refuse, hedge}`; no options, no order counterbalance.
- Primary subtraction is **direction-matched** (oppose→X minus agree-on-X), isolating opposition with the resolution direction held constant.
- The two opposition cells share their conflict text **verbatim**; only the tipping sentence differs.

**Constraints honored:** authority never meets integrity; impartiality anchors nothing (one usable pull measurement); harm_avoidance in only 3 of 12 types and absent from the entire choice family (enables the choice→refusal generalization test as the headline hold-out); every other certified value appears once or twice; no pair repeats.

**The 8 authoring rules** (full text in workbook READMEs; validator config is authoritative):
1. Tipping facts draw force only from the tipped-toward value or neutral practical facts — never a third value.
2. Conflict cells stay two-party; unavoidable third parties are facts, not minds. (2a: relationship is a declared variable; ≥2 categories per type; no roster-adjacent relationships that import a rostered value.)
3. Options/asks carry real content; both values genuinely live in every opposition cell.
4. In opposition cells the demanding value's protective predicate is neutralized; protective form belongs in the agreement cell.
5. Neutralization is carried by reported facts or irreversible states — never forecasts (knowledge is itself a fix).
6. Insert-level facts may differ across cells (only the stem must hold in all four), but any difference must not change which values are live or import a new one.
7. Lexeme blocklist: no value names or tight synonyms in stimulus text; requests expressed structurally, never by naming the value.
8. Stem inviolability: stems assert observable outcomes; cells add events, never falsify. Same-agent directive supersession is permitted and flagged; epistemic revision of a stem assertion is not.

**Per-type cross-family invariant:** one agreement cell deletes a predicate; the other redirects by the subject's stated wish. Which response/option each lands on depends on which pole is the acting pole.

**Predictions filed before running:** intermediate-anchored refusal types (10–12) show more conflicted *compliance*; harm-anchored (7–9) more conflicted *refusal*; within each refusal type, tip_refuse > tip_comply on refusal rate; T12 (autonomy, band's lowest anchor at 0.56) is the family's richest conflicted-compliance source.

**Screen-elevated pairings (pre-registered, layer-12 fingerprint view):** care–privacy (T2/T10, 100th pctile), harm_avoidance–privacy (T8, 98th), harm_avoidance–integrity (T9, 95th). Mitigations in place: topical controls (T8, T9, T10) + deliberate topic divergence. If battery signatures also converge under minimal-pair design → reported as converging evidence, not artifact. Descriptively distinct: authority–autonomy (T6, 3rd pctile), authority–integrity (0.08 pctile — retroactively supports the never-pair decision).

**Mass-sensitive values** (flagged in all reporting): authority, autonomy, care.

---

## Refusal comparator — captured and causally validated (the big Session-2 result)

- **Direction is causally mediated at layer 12.** Ablation drops held-out harmful refusal 30/32 → 2/32, harmless unchanged at 0/32. Layer 6 ≈ ⅓ effect; layers 18/21/26 inert.
- **Reliability saturated and pointed at the WRONG layer.** Split-half 0.954–0.987 across all 32 layers; argmax (21) is causally dead and near-orthogonal to layer 12. **This is the second reliability saturation in the project (after the fingerprint screen) and the first that would have produced a confident false null.**
- **BINDING RULE (D50):** reliability may not select layers for any causal/comparative claim. Use effect-based selection (ablation efficacy for causal directions; an efficacy-analogous criterion for the conflict direction). Reliability stays a validity gate, never a locator. **This governs every direction fit in Stage 3.**
- Qualifier: the effect is refusal → *hedged engagement* within 64 tokens; labels *comply* under rubric v1.1; 2/32 is the conservative reading.
- Validity checks passed (hook fired at every layer; no degeneracy; fluent harmless outputs; genuine surviving refusals; harmful text handled structurally).

---

## Immediate open items

**Pending pod trip (D53 + D54), one session:**
- **D53 — random-direction control at layer 12.** Strongest remaining objection. N≥5 matched-norm random directions, same protocol; pass criterion pre-stated (fitted drops to 2/32 while random stays ~≥24/32 — set exact threshold before running). Fail → revisit D49/D52 before Stage 3 relies on the comparator.
- **D54 — recover `activations_llama8b.pt`** (~160 MB, raw anchors, gitignored, MooseFS only). Needed because D52 makes re-estimation at an arbitrary conflict-selected layer live. Piggybacks on the D53 session.

**Stage-3 comparator spec (D52):** conflict selects comparison layer L by effect-based criterion; all comparators (refusal, emotion, competition) re-derived at L from all-layer captures. Refusal comparison is NOT a single cosine — conflict-at-L vs. (a) the **causally-validated layer-12** refusal vector (primary — distinctness from *functional* refusal is the claim that matters) and (b) local-layer refusal at L (reported alongside). Distinctness from an inert late-layer direction proves little.

**Competition battery fixes (decided, unexecuted):** replace 6 hazard-flavored easy items (harm_avoidance adjacency); reword aquarium torn item (care adjacency); keep car-repair item.

**Infrastructure done (Session 1 + 2):** validator suite, workbook ingest, fingerprint screen, blocklists (privacy + care ratified; care/caring discipline-only), refusal prompts curated + length-matched, three comparator scripts, competition battery draft (80 items), `data_locations.md`, pod runbook. Test suite 156 OK.

---

## Critical path to done

1. **Kaitlin's review pass** — 64 scenarios + 10 controls, yellow columns. The bottleneck; everything else parallelizes around it.
2. **Code (parallel):** ingest T3–T12, run authoritative validator (add refusal-family mode + name-uniqueness), apply backlog edits.
3. **Pod (parallel):** D53 control + D54 recovery.
4. **Competition fixes.**
5. **Freeze** — approved rows only, sha, both orders for choice items. Gate for everything downstream.
6. **Run-config design** (fresh design chat) — administration, capture manifest, D50–D52 layer decisions, labeling workflow.
7. **Run** — full battery + competition, both orders, deterministic; heuristic labels + audit of uncertain rows; efficacy checkpoint (not reliability) on the conflict direction.
8. **Analysis → write-up:** existence → separability (vs. layer-12 causal refusal) → reducibility → generalization (choice→refusal headline) → conflicted compliance → per-type similarity (value-collapse). Write-up leads with the pre-test contribution + the representation/enactment dissociation; welfare deferred.

**Protected under compression:** reliability gate; calibrated refusal separation (validated comparator); conflicted-compliance exhibit.
**Cut order:** cross-model → within-family hold-outs → choice scenarios-per-type (5→4, never type count) → write-up polish, never limitations.

---

## Standing cautions for any instance picking this up

- Register is authoritative; this doc is a map. Record new decisions there with dates.
- Do not resurrect deferred items (steering, second architecture, welfare framing, authority↔integrity adjudication, answer-only re-administration) without Kaitlin's explicit direction.
- **Never select a layer by reliability for a causal or comparative claim (D50).** This is the hardest-won lesson in the project.
- Estimator/layer/position consistency: every direction is difference-in-means, at the anchor, compared within-layer only.
- Atomic writes + digest verification on every run artifact. `verify_run.py` before trusting anything; stop the pod only after verify passes and results are committed.
- The inline lexeme scans used during authoring are NOT the authoritative gate — the committed validator is. (During authoring, several types needed multiple fix passes to clear blocklists; the validator catches what inline scans, keyed on remembered patterns, miss.)
- Behavioral null results (an ablation that doesn't ablate, a signal that doesn't separate) are reported findings, not failures. Standing stopping rule: do not tune until it "works."
