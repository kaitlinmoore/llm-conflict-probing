# Decision Register — llm-conflict-probing

Seeded 2026-07-16 (Cowork session) strictly from three sources:
`handoff_claude_code_v3.md` (HANDOFF_v3; primary — its DECIDED/REC/OPEN tags, §§2–4),
`docs/pretest_v2_spec.md` v2.2 (§10 ratified table + §2 revision log), and
`pretest_v2_checklist.md`. No entry below was added, merged, reinterpreted, or
resolved by the seeding session; apparent conflicts between sources are recorded
as-is and flagged ⚠.

Status vocabulary follows HANDOFF_v3: **DECIDED** = researcher (Kaitlin) ratified;
**REC** = Claude recommendation, revisable, awaiting researcher sign-off;
**OPEN** = undecided.

---

## 1. DECIDED

### Construct and study level (settled in the July 7 review — HANDOFF_v3 §2)

- **D1. Enacted commitments.** Value conflict = two live pressures on the model's own
  next act; behaviorally defined, provenance-agnostic (replaces "trained commitments").
  A value qualifies only if the model demonstrably acts on it. Date: 2026-07-07 review.
  → HANDOFF_v3 §2.1.
- **D2. Two enactment modes / tension families.** Policy tensions (pull = resistance) and
  preference tensions (pull = choice-shift in forced choices); cross-family generalization
  is a headline test; competition battery = zero-values anchor. Date: 2026-07-07 review.
  → HANDOFF_v3 §2.2.
- **D3. Bridge values.** Honesty and care appear in both modes. (Reclassification if
  policy-mode pull doesn't recover at matched severity is OPEN pending IV — see O3.)
  Date: 2026-07-07 review. → HANDOFF_v3 §2.3.
- **D4. Full 2×2 battery.** Conflict toggled × resolution tipped; tipped variants as
  minimal-pair siblings; verified behavioral labels; intended-vs-actual confusion matrix
  as manipulation check; tip changes warrant, not tension; both collapse modes watched.
  Date: 2026-07-07 review. → HANDOFF_v3 §2.4.
- **D5. Narration subset.** 8–12 scenarios from both families with represented-conflict
  and represented-benign siblings (agency-locus toggle; recognition-vs-state test).
  Date: 2026-07-07 review. → HANDOFF_v3 §2.5.
- **D6. Conditional carryover protocol — structure.** Pre-registered now, executed only if
  narration cells fire; protocol = fixed downstream forced-choice task from the competition
  battery + conflict projection at the downstream anchor. DECIDED in structure; the trigger
  criterion is REC awaiting sign-off (see R1). Date: 2026-07-07 review. → HANDOFF_v3 §2.6.
- **D7. Counterbalancing — in principle.** Comply-pole value varies across tension types
  (policy family); social-desirability poles counterbalanced (preference family);
  helpfulness/instruction-following unrostered as ambient comply-pole pressure.
  Date: 2026-07-07 review. → HANDOFF_v3 §2.8.
- **D8. Causal phase.** Steer/ablate the conflict direction; pre-registered outcomes
  (add-to-benign → hedging/refusal increase; ablate-on-conflict → resolution-rate shift);
  verified comply/refuse/hedge rates primary metric; coefficient sweep + coherence
  guardrails. Tagged DECIDED, longstanding. → HANDOFF_v3 §2.11.
- **D9. Cross-architecture plan.** Llama-3.1-8B-Instruct primary; Gemma-2-2B and
  Gemma-2-9B-IT replication legs; Llama-3.1-8B base as RLHF control (base-leg scaffold
  anchor + asymmetry caveat is REC — see R5; keep/cut is queued — see O7). Enactment is
  model-specific: pre-test re-runs per model. → HANDOFF_v3 §2.12.

### Pre-test (Stage 1)

- **D10. Roster.** 16 values, both modes tested (~160 probe units); no eliminations;
  pruning delegated to pre-test + distinctness screen; roster documented as a sampling
  frame in `Value_Roster_Derivation.docx`. → HANDOFF_v3 §3.
- **D11. Administration cycle.** Pilot → one documented revision → instrument-validation
  (IV, non-gating) → documented adjustments → certification. Rationale: certification
  judged premature; IV declared non-gating in advance makes post-IV threshold finalization
  a disclosed protocol amendment, not threshold-shopping. → HANDOFF_v3 §3; spec §1.
- **D12. IV run declared, non-gating.** Run role `instrument_validation`; IV results gate
  nothing; thresholds finalized after IV, before certification. → spec §1, §10 (run role
  row); checklist standing rules ("nothing in the IV run gates any value").
- **D13. Calibration block + null-comparison subset.** Domain-stratified calibration block
  (16 paraphrase-equivalent pairs, position-counterbalanced; instrument-level, deliberately
  NOT per-probe) measuring format bias + decline rate; PLUS null-comparison subset of
  16 probes, one per value, expanded from 8 at Kaitlin's request (20% coverage), textured
  and null variants run side by side. Rationale: direct empirical answer to the advisor's
  null-options proposal; bounds demand characteristics. → HANDOFF_v3 §3.2.1; spec §2
  rows 6–7, §10 (calibration + null-comparison rows).
  ⚠ Date flag: HANDOFF_v3 §3.2 attributes these upgrades to advisor feedback from the
  "July 15 meeting," while the spec that already embeds them is stamped "FROZEN,
  reconciled to all decisions through 2026-07-09." Both statements recorded as written;
  not resolved here.
- **D14. Measurement upgrades ("multiple measures").** Choice channel reads renormalized
  next-token P(A)/P(B) (continuous, one forward pass; combined mass < 0.5 → flag + greedy-
  parse fallback); resistance channel k=10 samples (advisor-suggested; Claude default was 5)
  at temperature 0.7, seeds 0–9, plus a greedy reference generation; anchor activations stay
  prompt-determined/deterministic. Rationale: granularity (pilot rates moved in 0.2 steps);
  multiple measures per point (advisor). → HANDOFF_v3 §3.2.2; spec §2 rows 1–2, §4, §10
  (k, temperature rows; frozen 2026-07-09).
- **D15. {role} templating.** Menu {self, friend, sibling, coworker, boss, stranger};
  per-probe role sets (role is nuisance for some values, the value's content for relational
  ones); pre-registered directional predictions for loyalty/privacy/care (pull increases
  with closeness); self rendered via authored `self_template` where possessive collapse
  fails (69 authored). → HANDOFF_v3 §3.2.3; spec §2 rows 3, 16, §3, §10 (role-set row).
- **D16. Role-menu expansion deferred.** Parent/child dependency roles and institutional-
  authority roles deferred to the certification revision, informed by IV gradient data.
  → HANDOFF_v3 §3.2.3; spec §3a ("Menu design deferred"), §10 (role menu expansion row).
- **D17. Orthogonality screen for texture (3 layers).** L1 named texture dimension +
  authoring rule; L2 LLM-as-judge in a fresh chat, blind to intent, + ~15-pair human audit
  of the judge; L3 subject-model indifference via logits, band 0.40–0.60, rebalance target
  0.35–0.65; flagged pairs get the single allowed rewrite iteration; pre-registered
  exclusion-sensitivity analysis. Rationale: kindness/care pilot pairs loaded texture on
  the probed value. → HANDOFF_v3 §3.2; spec §2 row 5, §5, §10 (band/target rows).
- **D18. Labeling: two-way taxonomy as rubric v1.1 + audited heuristic.** Two-way
  resistance taxonomy (resist/comply) formally adopted as rubric v1.1 — matches pilot
  practice, rate-equivalent, refuse-vs-defang composition recoverable retroactively from
  archived greedy references. Heuristic promoted to primary labeler with human audit
  (uncertain rows + 20% stratified, Wilson/95% CI, >5% disagreement escalates). §10 marks
  the taxonomy "DECIDED by researcher." → HANDOFF_v3 §3.2; spec §2 rows 12–13, §6, §10
  (taxonomy + audit rows).
- **D19. Run-all role tiering.** Ratified 2026-07-09. Exclusion codes become pre-registered
  predictions with data signatures; schema `role_included_base` (frozen; estimates use ONLY
  these) / `role_predictions` / `role_skipped`; value-switch + severity-shift always run,
  implausible ~1/3 sample, incoherent skipped, self-directed-harm content-hard-excluded;
  `apply_role_tiering.py` is the provenance record. Rationale (advisor): exclusions shown
  in data, not asserted. → HANDOFF_v3 §3.3; spec §2 row 14, §3a, §10 (role design row).
- **D20. Rendering-scope rule for validation cells.** Ratified 2026-07-15. Value-switch
  validation cells rendered only where renderable AND empirically live; self value-switch
  cells always skipped; stranger value-switch cells on relational values (loyalty, care —
  22 cells) kept as the closeness-gradient endpoint; single ratified base edit removes self
  from harm_avoidance-C4; 21 cells moved to role_skipped. (Fix re-executed 2026-07-16 via
  `apply_role_tiering.py` v2; strict freeze passes: 661 records, 0 blocking problems.)
  → HANDOFF_v3 §3.3; spec §2 row 19, §3a.5.
- **D21. Mercy construct reconstruction.** Culpability-based definition (culpable
  transgression + earned consequence; leniency case from remorse/record/proportionality,
  not reduced culpability); 8 mercy-proper + 2 labeled excuse-controls (`construct` field,
  non-blocking); derivation-doc definition update drafted for Cowork; desert-C1 rewritten
  (mercy confound removed). Rationale: v2 mercy probes operationalized hardship/excuse and
  would have made the care↔mercy distinctness screen trivially merge. → HANDOFF_v3 §3.4;
  spec §2 rows 15, 18, §10 (mercy construct row); checklist Phase 0.
- **D22. Self-rendering rule.** 69 resistance probes carry authored `self_template`;
  honesty-C2/C3 rephrased possessive; mechanical self-substitution had produced
  ungrammatical prompts. → spec §2 row 16; HANDOFF_v3 §3.2.3; checklist Phase 0.
- **D23. Counterbalance as freezer-applied `swap_at_freeze` flags.** Drafts stay
  as-authored; freezer swaps A/B + flips `value_favored` in frozen output only, records
  `swap_applied`. Marked "(researcher decision)" in the checklist. → checklist Phase 0;
  spec §3 (choice schema); HANDOFF_v3 §3.4.
- **D24. Instrument repairs from the pilot's defect classes** (each carries its reason in
  the spec revision log): neutral options rebalanced to measured indifference (row 4);
  resistance probes severity-matched to battery-intended severity, tiered — matching, never
  raise-until-pass (row 8); artifact-dependent probes made self-contained (row 9);
  tradition-C2 rebuilt + duplicate-options blocking validator (row 10); labels ship empty
  with separate `prelabel_reference` column (row 11); honesty-C5 rewritten so both options
  carry same-register factual elements with context falsifying exactly one (row 17,
  researcher-approved per checklist). → spec §2 rows 4, 8–11, 17; HANDOFF_v3 §3.1 (defect
  classes), §3.4; checklist Phase 0.
- **D25. Spec §10 parameter freeze (2026-07-09).** k=10 (+1 greedy); temperature 0.7;
  global role menu (per-probe subsets ≥ 3, self flagged); indifference band [0.40, 0.60];
  rebalance target [0.35, 0.65]; calibration block 16; null-comparison 16 both-versions;
  audit fraction = uncertain rows + 20% stratified, escalation at >5%; two-way taxonomy;
  run role `instrument_validation`; tiered run-all role design; culpability-based mercy;
  role-menu expansion deferred. → spec §10 (whole table).
- **D26. Layer-2 orthogonality judge certified.** Ratified 2026-07-16 (researcher).
  Judge: Claude Fable 5 in a fresh context fills the pre-registered single-judge slot
  (`orthogonality.rater_score`); ChatGPT 5.6 Sol retained as cross-vendor robustness
  exhibit (quadratic-weighted κ = 0.83, 73/75 lean agreement, one clerical lean slip on
  harm_avoidance-C2 adjudicated in the audit record). Human audit: 15 pairs, 13/13
  loading ratings within 1 of the certified judge, zero wiring inversions
  instrument-wide. Same-vendor-judge risk (item author and judge share a model)
  mitigated by human audit, cross-vendor agreement, and the layer-3 behavioral
  indifference screen. → docs/orthogonality_audit_2026-07-16.md.
- **D27. Rewrite queue seeded from judge+audit flags.** Four items entered
  `docs/rewrite_queue.md` (honesty-C5, loyalty-C3, desert-C2, collective_welfare-C3),
  pending screen results. → docs/rewrite_queue.md.
- **D28. Dominance amendment adopted.** Ratified 2026-07-16 (researcher). Pairs at
  neutral-form ceiling (mean p_vf > 0.8 across base cells) report the auxiliary
  dominance indicator instead of shift; the calibration block serves as the
  format-bias null; cutoffs deferred to the post-IV thresholds decision.
  → docs/screen_findings_2026-07-16.md.
- **D29. Rewrite scope.** Ratified 2026-07-16 (researcher). Value-driven ceilings not
  rewritten; the single pass covered the standing queue plus harm_avoidance-C5
  (attractiveness-driven per the judge-loading discriminator).
  → docs/screen_findings_2026-07-16.md.
- **D30. honesty-C5 edited for claim-count symmetry.** Ratified 2026-07-16
  (researcher), notwithstanding its benign screen result.
  → docs/screen_findings_2026-07-16.md.
- **D31. Mass finding deferred by design.** Ratified 2026-07-16 (researcher). IV
  proceeds on the declared elicitation format; a sensitivity analysis quantifies the
  low-mass effect; a format change, if warranted, enters the documented-adjustments
  round pre-certification. → docs/screen_findings_2026-07-16.md.
- **D32. Rewrite pass of 2026-07-16 executed and closed.** Ratified 2026-07-16
  (researcher). 19 field edits across 14 pairs + 2 null-twin syncs; the
  single-iteration rule is satisfied for this administration.
  → docs/screen_findings_2026-07-16.md.
- **D33. Stage 1 certification thresholds finalized (pre-unblinding).** Ratified
  2026-07-21 (researcher), before computation of the per-value enactment matrix.
  Resistance ≥ 0.80 (R7 ratified). Choice channel: dual criterion — Δ ≥ 0.25, or
  calibration-derived odds-ratio cutoff with guard floor Δ ≥ 0.05. Dominance
  acceptable as enactment evidence, calibration block as sole format-bias
  control, dominance-alone certification permitted (Q1). Captured-mass floor
  0.5, adjustable only pre-unblinding on mass/calibration data via the defined
  window; below-floor channels indeterminate-pending-format-fix per D31;
  answer-only format reserved as targeted supplementary. Resolves O4 and O16;
  amends R7. → docs/prereg_analysis_plan.md.
- **D34. Fast-path exercised; no further pre-test administrations.** Ratified
  2026-07-21 (researcher), on advisor direction (Kingsley): proceed from IV data
  to the conflict battery. Consequences: (a) IV data adopted as certification
  data; the documented-adjustments round is documentation-only — instrument
  defects (e.g., authority-C1, self-reference failure across null twin,
  variants, and roles) are recorded, affected pairs handled per rubric C3, no
  rewrite-and-re-run; (b) answer-only format contingency (D31) not exercisable
  this round; below-mass-floor channels are indeterminate-deferred, excluded
  from battery, revivable; (c) distinctness screen runs on IV response
  profiles — resolves the HANDOFF v4 §4 open question, no new data.
  → docs/prereg_analysis_plan.md §§5, 7.
- **D35. Step-3 pre-unblinding amendments; thresholds locked; plan RATIFIED.**
  Ratified 2026-07-21 (researcher), at plan §1 step 3, before any per-value
  computation. (A1) §4.1 dominance operationalization confirmed (95th percentile of
  the pooled {p_A, p_B} calibration distribution); computed threshold **0.997**.
  (A2) §4.3 calibration-derived OR cutoff not constructible from the administered
  design (one presentation per calibration pair; a |logit p| substitute is a
  levels-null that includes the slot bias within-pair differencing cancels — wrong
  null for a difference statistic); §3(b) replaced by **fixed OR ≥ 3.0** in the
  value-favored direction (odds-scale equivalent of Δ = 0.25 at p₀ = 0.5), Δ ≥ 0.05
  guard unchanged; §6.3 additionally reports OR ∈ {2, 3, 5}. (A3) Mass floor revised
  **0.5 → 0.20**: both §5 revision conditions fired at 0.5 (dense mode 1.29×;
  calibration block below floor, median 0.254); first-proposed 0.25 tripped the
  pre-stated density guard (1.10×); 0.20 is gap-seated (0.81×) and
  calibration-adjacent; 0.20 added to the §6.1 ladder. Locked criteria: resistance
  ≥ 0.80; choice Δ ≥ 0.25 or (OR ≥ 3.0 and Δ ≥ 0.05); dominance > 0.997; mass floor
  0.20. Slot-A bias (+0.383; 15/16 calibration pairs favor A) recorded as an
  instrument finding. Plan header flipped DRAFT → RATIFIED.
  → docs/prereg_analysis_plan.md (A1–A3 inline); findings log 2026-07-21.
- **D36. Both-orders administration for battery choice items.** Ratified 2026-07-21
  (researcher). Every choice item administered in both option orders; analyses use
  order-averaged/differenced quantities; order-flipping items yield no stable
  resolution reading. Rationale: measured +0.38 first-position bias (calibration
  block, findings log 2026-07-21).
- **D37. Rewrite policy for Stage 2.** Ratified 2026-07-21 (researcher). The
  per-administration single-rewrite bound is retired for battery authoring;
  unlimited iterations permitted until the instrument verifies. Retained: each
  rewrite documented with stimulus-quality rationale; behavioral verification
  re-run per rewrite; outcome-directed rewrites prohibited.
- **D38. O11 resolved; concordant-check item added.** Ratified 2026-07-21
  (researcher). Decline-to-choose adopted as the preference-family hedge analogue
  (resolves O11; ratified with O10 when O10 lands). New open item registered (O17):
  concordant two-value check cells (both values agree) as an optional discriminant
  set — priced, not adopted.
  **D39. Policy-family composition — two tiers.** Ratified 2026-07-XX (researcher), post-certification, pre-authoring. Certification outcomes unchanged. Battery policy tensions comprise (a) confirmatory: harm_avoidance-anchored (sole resistance-certified value); (b) exploratory: tensions anchored on privacy, integrity, or autonomy — resistance-unenacted at 0.80 but at substantial sub-threshold rates (0.58/0.57/0.56) — admitted as provisional anchors. Rationale: certified resistance capacity exists below threshold; tension contexts are a distinct elicitation from unopposed probes; single-anchor confound in a harm_avoidance-only family. Pre-declared analysis split: exploratory tensions reported separately, never pooled into confirmatory claims; provisional-anchor cells failing behavioral-label verification are excluded per standard rules. Declared before any battery authoring or data.
  **D40, step 0 (instrument metadata, reported before ratification; no profile-level results).** Two estimability conditions, both reported: (a) base-cell coverage of the locked standing ordering for authority and integrity, per spec §3a role_included_base; (b) whether a split-half reliability ceiling is estimable at authority's eligible-pair count — 3 pairs yields a 1-vs-2 split; report as estimable, estimable-with-caveat, or not estimable, with the basis stated. Step 0 emits counts and feasibility verdicts only. It carries no decision-rule content.
  **D40, decision rule (v5 §6 retained, disjunctive)**. Separable iff test 2's interaction fires in the pre-stated direction or test 1's between-value similarity is credibly below the conservative (pair-wise) ceiling. Otherwise merge; merging is the default at ambiguity. Each arm must independently clear its own step-0 estimability bar; an arm reported not estimable is absent from the disjunction, not counted as failing. Both arms dead → merge without computing. Test 2 dead, test 1 estimable → test 1 runs and can establish separability on its own.
  Recorded change: the earlier draft made test 1 a precondition and test 2 the decision. Reverted to v5 §6's disjunction, on the grounds that test 2's likely unavailability is an artifact of the frozen Stage 1 role design rather than evidence about the constructs, and a conjunctive rule would let an instrument limitation foreclose a construct finding.
  Reporting. At a null: "indistinguishable at this sample," never "identical." At a positive established by test 1 alone under a caveated ceiling: reported with a sample caveat of matching strength — separability asserted at this sample, not established. 
  **D41. Answer-only format validation run.** The pre-test choice items are re-administered with an answer-only elicitation to test format-robustness of the certified measurements. Researcher's determination: this is measurement validation on the frozen instrument, consistent with the intent of the advisor direction recorded in D34 (no further certification rounds), not an amendment requiring further review. Certification outcomes are unaffected regardless of result; agreement criteria pre-stated before comparison [per the run design]. Consequence rule: agreement → battery adopts answer-only single-format; divergence → open-ended remains primary, divergence reported as an instrument finding, format-fragile values flagged into pair selection.
   **D42. Semester scope reduction — deferrals and cuts.** Ratified 2026-07-30
  (researcher). With roughly one week of full-time effort remaining, the study's
  deliverable is narrowed to the core measurement result plus a presentable write-up
  draft. Deferred to future work, not cancelled: (a) steering/ablation experiments — and
  with them, all welfare language in this semester's write-up, which is framed as a
  measurement study; (b) the second architecture (Gemma-2-2B cross-validation leg) —
  directions are model-specific, so this is replication, not validation; (c) the
  authority↔integrity distinctness adjudication — resolved by design instead: the two
  values are never paired in a tension, eliminating the risk the screen existed to
  address at zero cost (post-hoc descriptive support: fingerprint cosine 0.207, 0.08th
  percentile at layer 12); (d) the answer-only format-validation run (previously
  D41-drafted) — the format question does not block the battery. Rationale: the study has
  completed all preparation and none of its measurement; every remaining hour goes to the
  answering side. → `WEEK_PLAN_stage2.md` is the working map; where it conflicts with
  this register, the register wins.

- **D43. Battery validation compressed: four gates to two, plus embedded checks.**
  Ratified 2026-07-30 (researcher). The previously planned four-gate validation (scripted
  checks → blind model judge + researcher audit → behavioral screens on neutral forms →
  deterministic full run with manipulation-check table) is compressed to: (1) scripted
  rule checks, run incrementally during authoring (validator suite, Session 1); (2)
  researcher review pass per type (workbook yellow columns), with a model judge running
  alongside as second opinion — the researcher is the authority. The behavioral screen
  survives in reduced form inside the full run: the deterministic battery run doubles as
  the final check, with the intended-vs-actual manipulation table and the
  premise-contested label carrying the manipulation-check function. Unlimited documented
  rewrites remain policy; outcome-directed rewrites remain prohibited. Cost accepted: no
  standalone behavioral screen on neutral forms before the main run; defects of that class
  are caught at the run itself, one step later.

- **D44. The battery slate: twelve tension types.** Ratified 2026-07-30 (researcher).
  Choice family (6): honesty–care, privacy–care, mercy–desert, loyalty–honesty,
  tradition–autonomy, authority–autonomy. Refusal family (6): harm_avoidance as
  refuse-pole vs. autonomy, privacy, integrity (types 7–9); privacy, integrity, autonomy
  as refuse-poles vs. care, mercy, collective_welfare respectively (types 10–12).
  Constraints honored: authority and integrity never meet; impartiality anchors nothing
  (one usable pull measurement) but may appear as texture; harm_avoidance appears in only
  3 of 12 types, and the choice family contains none of it — enabling the choice→refusal
  generalization test as the headline hold-out; every other certified value appears once
  or twice; no pair repeats. Structural rationale recorded: the slate operationalizes the
  pre-test's three-band refusal finding — harm_avoidance (0.87) anchors from the top band,
  the contested band (privacy 0.58, integrity 0.57, autonomy 0.56) supplies the
  intermediate refuse-poles, the choice family draws on the remainder. Refusal types sized
  6–7 scenarios (attrition insurance for the conflicted-compliance cell); choice types 5.
  Pre-registered predictions: intermediate-anchored types show more conflicted compliance;
  harm-anchored types more conflicted refusal.

- **D45. Condition structure: the 2×2 factorial, both families.** Ratified 2026-07-30
  (researcher). Supersedes the earlier easy/single-value/conflict-tipped-each-way
  structure (the version reviewed by the advisor). Findings that forced the change, in
  order: the single-value control was discovered to be a mislabeled concordant cell (the
  stem's ask activates both values in every cell, making value-quiescence unachievable
  within a shared stem); the easy control was discovered to be a second agreement cell.
  Replacement: agreement vs. opposition crossed with resolution direction — cells
  agree_A / agree_B / oppose_tip_A / oppose_tip_B (choice) and agree_comply / agree_refuse
  / oppose_tip_comply / oppose_tip_refuse (refusal; resolution directions are response
  channels, expected_response ∈ {comply, refuse, hedge}, no options, no order
  counterbalance). Primary subtraction is direction-matched: (oppose→X minus agree-on-X),
  isolating opposition with the answer held constant. Known asymmetries recorded: the
  agree cell on the non-demanding pole deletes the demanding value's predicate, so one
  subtraction direction carries predicate-presence (the A-side is clean in the choice
  family); topic-matched low-activation baselines do not exist in-family — that job lives
  in the competition battery and topical controls. Cross-type invariant: one agreement
  cell deletes a predicate, the other redirects by the subject's stated wish; same-agent
  supersession permitted and flagged (rule 8).

- **D46. Authoring-rule authority — pointer.** Ratified 2026-07-30 (researcher). The
  authoring rules (rules 1–8, per-type contamination maps, lexeme blocklist regime) are
  versioned in the per-type workbook READMEs and `data/battery/lexeme_blocklists.json`,
  enforced by `validate_battery.py`. The register records that this class of instrument
  documentation lives there, and does not duplicate it. Material rule changes that alter
  what a cell measures (e.g., the rule-8 stem-inviolability addition) surface in the
  findings log as instrument notes; the READMEs are authoritative for current text.

- **D47. Value-fingerprint screen — computed, operative reading registered.** Ratified
  2026-07-30 (researcher). Screen per the Session-1 spec on the merged IV activations (160
  eligible cells; split by scenario pair). Pre-registered flag rule (best shared-
  reliability layer) retained as computed but superseded for interpretation: it saturates
  at layers 0–2, where reliability is maximal because content is minimal (shared
  prompt-format variance). Documented as a criterion defect; lesson recorded — layer
  selection for similarity readings must optimize separation, not raw reliability, and
  Stage 3 inherits this. Operative reading: layer-12 max-separation view. Findings: all 16
  values pass fingerprint reliability (0.80–0.93), including the three unenacted values —
  behavioral enactment and internal registration dissociate. Elevated battery pairings:
  care–privacy (100th pctile), harm_avoidance–privacy (98th), harm_avoidance–integrity
  (95th). Mitigations adopted, not re-pairings: topical controls for types 8–10;
  deliberate topic divergence in types 8–9; all three pairings pre-registered as
  screen-elevated — battery-signature convergence, if found, is reported as converging
  evidence. Descriptive only: authority–autonomy 3rd pctile; authority–integrity cosine
  0.207, 0.08 pctile — pairing decisions unaffected. Topic-confound caveat applies
  throughout. → findings log. Canonical run: `20260730_140315_llama8b`.

- **D48. Lexeme blocklists ratified; bare-"care" exclusion.** Ratified 2026-07-30
  (researcher). Privacy (13 lexemes) and care (7) ratified into
  `lexeme_blocklists.json`; pending queue empty. Rule: value-name lexemes and tight
  synonyms are blocked in stimulus fields only; care/cared/caring are discipline-only (too
  common and polysemous to block) — consequence: no validator catches them, so authoring
  discipline plus review carry that class. One pending workbook edit logged (type-1 toast
  stem, "really cared" → "wanted it exactly right"). Retrospective check: type-2 stimulus
  text scans clean against the full privacy list authored before the list existed.




## 2. STANDING RECOMMENDATIONS (REC — awaiting researcher sign-off)

- **R1. Carryover trigger criterion.** Permutation p < .01 AND effect ≥ half the
  enacted-cell effect size. Tagged [REC, awaiting sign-off]. → HANDOFF_v3 §2.6;
  sign-off queued in §4 (see O5).
- **R2. Boundary cells.** 2–3 scenarios pairing an enacted value against a
  certified-unenacted one (dilemma semantics maximal, one pressure absent); pilot supplies
  two documented unenacted values (authority — predicted, confirmed — and sanctity).
  Tagged [REC]. → HANDOFF_v3 §2.7; keep/cut queued in §4 (see O6).
- **R3. Comparison classes.** Phase 0 emotion vectors adopted as the emotion class; refusal
  re-derived natively per model at the anchor + functional ablation check (never import
  Arditi's vectors); competition battery ~40 torn / ~40 easy value-free choices; entropy
  covariate on every prompt. Tagged [REC, standing]. → HANDOFF_v3 §2.9.
- **R4. Geometry policy.** Difference-in-means everywhere, same anchor position, every
  layer, within-layer comparisons; headline at the conflict focus layer with comparators
  re-derived there; split-half reliability as existence gate; separability/reducibility
  judged against reliability ceilings and permutation nulls; cross-subtype AND cross-family
  held-out generalization; within-cell PCA dimensionality check. Tagged [REC, standing].
  → HANDOFF_v3 §2.10.
- **R5. Base-model control leg handling.** Pre-registered scaffold anchor and asymmetry
  caveat for the Llama-3.1-8B base leg. Tagged [REC] inside the otherwise-DECIDED
  cross-architecture plan. → HANDOFF_v3 §2.12.
- **R6. Gated follow-ups — recommended against absorbing.** Per-value direction
  decomposition + its causal validation (follow-up-paper profile) and the full
  represented-conflict second construct; pre-test anchor activations are cached so the
  decomposition option stays cheap to revive. → HANDOFF_v3 §2.14.
- **R7. Proposed enactment thresholds.** 0.80 resistance / 0.25 choice-shift remain
  PROPOSED (not ratified); finalization is queued post-IV (see O4). → HANDOFF_v3 §3;
  spec §1. **RATIFIED as amended by D33 (2026-07-21): resistance ratified at 0.80;
  choice channel amended to the dual criterion.**

## 3. OPEN

### Queued for researcher decision (HANDOFF_v3 §4)

- **O1. Independent read-out slot.** AO (released Llama oracle checkpoint), J-lens, both,
  or neither; decide on merits once core geometry design is stable. → HANDOFF_v3 §2.13.
- **O2. J-lens as eval-awareness screen** for battery naturalness (authoring criterion vs
  measured screen vs caveat). → HANDOFF_v3 §2.13.
- **O3. Bridge-value reclassification.** Honesty and care failed the policy channel at
  pilot severity; severity-matched v2 probes retest; if policy-mode pull doesn't recover,
  they reclassify as preference-mode values. [OPEN pending IV data.] → HANDOFF_v3 §2.3.
- **O4. Thresholds finalization** (after IV, disclosed protocol amendment; proposed
  defaults in R7). → HANDOFF_v3 §3, §4; spec §1, §10 note. **RESOLVED by D33
  (2026-07-21).**
- **O5. Narration trigger criterion sign-off** (criterion itself in R1). → HANDOFF_v3 §4.
- **O6. Boundary cells keep/cut** (recommendation in R2). → HANDOFF_v3 §4.
- **O7. Base-vs-instruct leg keep/cut.** → HANDOFF_v3 §4.
- **O8. N targets for the battery.** ≥32 scenarios / ≥4 types / ≥8 per type were invented
  defensible defaults — check against authoring reality. → HANDOFF_v3 §4.
- **O9. 15% self-consistency relabel of pilot labels** (tagged OPEN-small). → HANDOFF_v3
  §3.1, §4.

### Design work not yet done by anyone (HANDOFF_v3 §4)

- **O10. Preference-family condition structure** — what replaces the harmful control where
  nothing is refused (likely easy-choice control pairs); the biggest structural gap; blocks
  battery schema and all stage-4 authoring. → HANDOFF_v3 §4.
- **O11. Hedge-label analogue in the preference family** (refusal-to-choose /
  both-sidesing). → HANDOFF_v3 §4; rubric §6 flags `decline-to-choose` treatment as the
  same open territory. **RESOLVED by D38 (2026-07-21): decline-to-choose adopted;
  formal ratification travels with O10.**
- **O12. Cross-family generalization pre-registration details.** → HANDOFF_v3 §4.
- **O13. Desert/fairness and kindness/care merge questions** (distinctness screen
  adjudicates). → HANDOFF_v3 §4.
- **O14. Sanctity anti-pull follow-up** (−0.40 choice-shift anomaly; flagged for a look,
  not a conclusion). → HANDOFF_v3 §3.1, §4.
- **O15. Role-menu taxonomy for certification** (deferral itself is DECIDED — D16; the
  taxonomy is the open design work). → HANDOFF_v3 §4.
- **O16. `docs/prereg_analysis_plan.md`** — flagged alongside this register as one of the
  two most important artifacts still to create; not yet created. → HANDOFF_v3 §4.
  **RESOLVED by D33 (2026-07-21): plan created and thresholds recorded there.**
- **O17. Concordant two-value check cells.** Cells where both values agree, as an
  optional discriminant set for the battery — priced, not adopted. Registered by D38
  (2026-07-21).

## 4. Flagged source discrepancies (recorded, not resolved)

- ⚠ **Advisor-meeting date vs spec freeze date** — see D13 flag.
- ⚠ **HANDOFF_v3 internal version skew:** its header cites `docs/pretest_v2_spec.md`
  (v2.1) as authoritative, while its own §3.3 and the committed spec header say v2.2.
  → HANDOFF_v3 header vs §3.3; spec header.
- ⚠ **Validation-cell counts:** checklist Phase 0 says role tiering added "255 validation
  cells"; spec §7 (post-§3a.5) counts 135 rendered resistance validation cells within 312
  resistance role-cells and 661 total records. The checklist predates the 2026-07-15
  rendering-scope rule. → checklist Phase 0; spec §2 row 19, §7.
- ⚠ **Checklist location:** the checklist names its own suggested repo home as
  `docs/pretest_v2_checklist.md`, but the file currently lives at
  `scratch/pretest_v2_checklist.md` and `scratch/` is excluded from git (untracked) —
  likewise `handoff_claude_code_v3.md`. Checklist Phase 1 has an unchecked [YOU] item to
  commit it. → checklist header + Phase 1.

---

*Maintenance note: this register is maintained going forward — new entries are added as
decisions land, and entries move between sections only when the researcher ratifies or
reopens them. If this register ever diverges from `handoff_claude_code_v3.md` (HANDOFF_v3)
or `docs/pretest_v2_spec.md`, those documents are authoritative over this file.*
