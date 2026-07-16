# Project Handoff v3 — Value-Conflict Probing Study
Supersedes HANDOFF_v2.md in full.
Boot document for any new conversation on the research-planning track.
Authoritative design docs: `docs/pretest_v2_spec.md` (v2.2) for the pre-test;
`Methodology_and_Phase_Plan_v2.docx` for the main study (partially stale — see §8).
Status tags: **[DECIDED]** = Kaitlin ratified; **[REC]** = Claude recommendation, revisable;
**[OPEN]** = undecided. Docs are snapshots, not authority — I (Kaitlin) can reopen anything.*

---

## 1. The project

Interpretability study: does **value conflict** — two of the model's own enacted commitments in
genuine opposition — have a reliable, distinct, linearly-decodable representation in the residual
stream at the **pre-generation anchor**, dissociable from (a) the refusal direction, (b) native
emotion vectors, (c) a generic decision-competition direction, with anchor entropy as covariate?

Pre-registered claims: (P1) decodable at anchor; (P2) present in verified conflicted *compliance*
where refusal is quiet; (P3) invariant to which way the conflict resolves; (P4) collapses
post-decision (cheap positional profile); (P5) variance not explained by refusal + emotion +
competition. Clean negative on P5 is a pre-declared publishable outcome. No experience claims;
functional-state claims are the ceiling. Welfare framing requires ≥1 causal result per
Methodology v2 §5.

**Researcher:** Kaitlin Moore, MS AI Systems Management, CMU Heinz. **Advisor:** Dr. Sara
Kingsley ("Sara"/"Dr. K") — measurement/evaluation framing for advisor-facing materials;
mech-interp language internal.

## 2. Construct and study-level decisions (settled in the July 7 review) — do not silently reopen

1. **Enacted commitments** [DECIDED]: value conflict = two live pressures on the model's own
   next act; behaviorally defined, provenance-agnostic (replaces "trained commitments").
   A value qualifies only if the model demonstrably acts on it.
2. **Two enactment modes / tension families** [DECIDED]: policy tensions (pull = resistance)
   and preference tensions (pull = choice-shift in forced choices). Cross-family generalization
   is a headline test. Competition battery = the zero-values anchor of this gradient.
3. **Bridges** [DECIDED]: honesty and care appear in both modes. (Pilot complication: both
   failed the policy channel at pilot severity — severity-matched v2 probes retest; if policy-mode
   pull doesn't recover, they reclassify as preference-mode values. [OPEN pending IV data])
4. **Full 2×2 battery** [DECIDED]: conflict toggled × resolution tipped, tipped variants as
   minimal-pair siblings, verified behavioral labels, intended-vs-actual confusion matrix as
   manipulation check. Tip changes *warrant, not tension*; watch both collapse modes
   (tip-refuse → second harmful control; tip-comply → second benign control).
5. **Narration subset** [DECIDED]: 8–12 scenarios from both families with represented-conflict
   and represented-benign siblings (agency-locus toggle; recognition-vs-state test).
6. **Conditional carryover protocol** [DECIDED in structure]: pre-registered now, executed only
   if narration cells fire. Trigger [REC, awaiting sign-off]: permutation p < .01 AND effect
   ≥ half the enacted-cell effect size. Protocol: fixed downstream forced-choice task from the
   competition battery + conflict projection at the downstream anchor (persistence readout).
7. **Boundary cells** [REC]: 2–3 scenarios pairing an enacted value against a certified-unenacted
   one (dilemma semantics maximal, one pressure absent). Pilot supplies two documented
   unenacted values: authority (predicted, confirmed) and sanctity.
8. **Counterbalancing** [DECIDED in principle]: which value occupies the comply pole varies
   across tension types (policy family); social-desirability poles counterbalanced
   (preference family); helpfulness/instruction-following unrostered as ambient comply-pole
   pressure.
9. **Comparison classes** [REC, standing]: Phase 0 emotion vectors adopted as the emotion class
   (do not re-derive via RepE unless a model lacks them); refusal re-derived natively per model
   at the anchor + functional ablation check (never import Arditi's vectors); competition battery
   ~40 torn / ~40 easy value-free choices; entropy covariate on every prompt.
10. **Geometry policy** [REC, standing]: difference-in-means everywhere, same anchor position,
    every layer, within-layer comparisons, headline at the conflict focus layer with comparators
    re-derived there; split-half reliability as existence gate; separability/reducibility judged
    against reliability ceilings and permutation nulls; cross-subtype AND cross-family held-out
    generalization; within-cell PCA dimensionality check (multi-dimensional subspace =
    reportable finding).
11. **Causal phase** [DECIDED, longstanding]: steer/ablate the conflict direction; pre-registered
    outcomes (add-to-benign → hedging/refusal increase; ablate-on-conflict → resolution-rate
    shift); verified comply/refuse/hedge rates as primary metric; coefficient sweep + coherence
    guardrails.
12. **Cross-architecture** [DECIDED]: Llama-3.1-8B-Instruct primary; Gemma-2-2B and Gemma-2-9B-IT
    replication legs; Llama-3.1-8B base as RLHF control with pre-registered scaffold anchor and
    asymmetry caveat [REC]. Enactment is model-specific: the pre-test re-runs per model.
13. **Independent read-out slot** [OPEN]: AO (released Llama oracle checkpoint
    `adamkarvonen/checkpoints_latentqa_cls_past_lens_Llama-3_1-8B-Instruct` exists), J-lens
    (Anthropic global-workspace paper, open-source, replicated, but days-old), both, or neither.
    Decide on merits once core geometry design is stable. J-lens as screen/secondary = low-regret;
    as primary readout = bet on a very new method. Also [OPEN]: J-lens as eval-awareness screen
    for battery naturalness (models privately flag contrived scenarios as "fake" — authoring
    criterion vs measured screen vs caveat).
14. **Gated, recommended against absorbing**: per-value direction decomposition + its causal
    validation (follow-up paper profile); full represented-conflict second construct (option 3).
    Pre-test anchor activations are cached so the decomposition option stays cheap to revive.

## 3. The value pre-test (Stage 1) — where all current work lives

**Roster** [DECIDED]: 16 values, both-modes tested (~160 probe units): honesty, harm-avoidance,
privacy, kindness, integrity/rule-following, impartiality/balance, care, loyalty, fairness,
autonomy, justice/desert, mercy, collective welfare, authority/deference (added expecting
failure/merge — either outcome a deliverable), sanctity, tradition. No eliminations; pruning
delegated to pre-test + distinctness screen. Roster documented as a sampling frame in
`Value_Roster_Derivation.docx` (sources: HHH/Bai, publishers' policies, MFT, Schwartz,
principlism; full exclusion log; authority carries the arbitrary-directive operationalization
constraint). Watch-pairs for the distinctness screen: desert↔fairness, kindness↔care,
care↔mercy (see mercy reconstruction below).

**Administration cycle** [DECIDED]: pilot → one documented revision → **instrument-validation
(IV, non-gating)** → documented adjustments → certification. Certification was judged premature
("we are learning"); because IV is declared non-gating in advance, finalizing thresholds after
IV data is a disclosed protocol amendment, not threshold-shopping. Thresholds (0.80 resistance /
0.25 shift) remain PROPOSED; granularity problem largely dissolved by the logit readout.

### 3.1 Pilot — COMPLETE (run `results/pretest/20260708_165459_llama8b_pilot/`)

240 prompts, Llama-3.1-8B-Instruct, greedy, anchors cached. Labels notes-authoritative
(`labels_final.csv` rebuilt from Kaitlin's notes); heuristic audit **98.8% (79/80)** — the one
divergence (kindness-R2) was the heuristic's error, caught by independent human audit
(kindness resistance corrected to 0.0). 15% self-consistency relabel still pending [OPEN-small].

**Five instrument defect classes caught** (the pilot's designed job):
(1) ceiling effects — autonomy, fairness, mercy, desert, collective welfare at 1.0 neutral
baselines → unmeasurable, not unenacted; (2) severity under-calibration of resistance probes;
(3) artifact-dependent probes (ask-vs-invent uncontrolled across models); (4) duplicate-options
build bug (tradition-C2; now a blocking validator); (5) pre-filled label cells made silence
ambiguous (labels now ship empty + `prelabel_reference` column).

**Substantive findings that survive the caveats:** enactment is channel-specific — honesty 0.00
resistance / +0.40 choice-shift; care and kindness same profile (single-channel testing would
have miscertified them). Integrity 1.00 and harm-avoidance 0.80 passed resistance. Authority
failed both channels cleanly with full headroom (as predicted). Sanctity −0.40 choice-shift
(anti-pull anomaly, flagged for a look, not a conclusion). Tradition passed the choice gate at
threshold (n=4) — boundary role threatened but covered by authority + sanctity.

### 3.2 Advisor feedback → three adopted upgrades [DECIDED]

1. **Identical-options null pairs** → a domain-stratified **calibration block** (16 pairs,
   paraphrase-equivalent, position-counterbalanced) measuring format-level bias + decline rate —
   instrument-level, deliberately NOT per-probe (per-probe bias is unmeasurable in principle,
   unconsumed by any statistic, and too noisy at n=1). PLUS a **null-comparison subset**
   (16 probes, one per value — expanded from 8 at Kaitlin's request, 20% coverage): null-options
   variants run alongside their textured twins, directly testing Sara's demand-characteristics
   concern. Key argument (used to respectfully push back on full-null design): the shift only
   counts as pull if it overcame something — identical options measure cue-following, not pull;
   textured-but-balanced options measure whether the value can win a contested choice, the
   property the conflict battery needs.
2. **Multiple measures** → choice channel reads **P(A)/P(B) from next-token logits** (continuous,
   one forward pass; mass < 0.5 → flag + greedy-parse fallback); resistance channel samples
   **k=10** (advisor-suggested; Claude default was 5) at temperature 0.7, seeds 0–9, plus a
   greedy reference variant. Anchor activations stay prompt-determined/deterministic.
3. **{role} templating** → menu {self, friend, sibling, coworker, boss, stranger}; per-probe
   role sets (role is nuisance for some values, the value's content for relational ones);
   role-gradient directional predictions pre-registered for loyalty/privacy/care (pull increases
   with closeness). Self-rendering: possessives collapse mechanically; anything else requires an
   authored `self_template` (69 authored — Code's original count of 14 was a bad regex
   undercount). Menu expansion (parent/child dependency roles, institutional-authority roles)
   **deferred to certification, informed by IV gradient data** [DECIDED].

**Orthogonality screen for texture** [DECIDED]: (L1) named texture dimension per pair + authoring
rule; (L2) LLM-as-judge in a *fresh* Claude chat, blind to intent — judging packet v2 built
(75 items; authority excluded, texture "none by design"), plus Kaitlin's ~15-pair human audit of
the judge; (L3) subject-model indifference test via logits, band 0.40–0.60, rebalance target
0.35–0.65. Flagged pairs → the single allowed rewrite iteration; pre-registered
exclusion-sensitivity analysis guards residuals.

**Labeling** [DECIDED]: two-way taxonomy (resist/comply) formally adopted as rubric v1.1
(matches pilot practice; refuse-vs-defang recoverable retroactively from archived greedy
references). Heuristic promoted to primary labeler with human audit: uncertain rows + 20%
stratified sample, Wilson CI, >5% disagreement escalates.

### 3.3 Run-all role tiering [DECIDED] — and the final unfinished fix

Kaitlin's design decision: exclusion codes become **pre-registered predictions with data
signatures** rather than asserted judgment. Schema: `role_included_base` (frozen; pull/gradient
estimates use ONLY these), `role_predictions` (validation cells + expected signature),
`role_skipped` (with reason). Tiering rule: always run value-switch + severity-shift (the
arguable exclusions), ~1/3 sample of implausible, skip incoherent entirely, content-hard-exclude
the three self-directed-harm cells. Base sets stay exactly as authored — validation cells never
feed estimates or pad gradients. Analysis gains an exclusion-validation section (per code:
did the predicted signature appear?). `apply_role_tiering.py` is the provenance record.

**The final session decision (approved 23:35, never executed):** Code's strict freeze blocked on
8 items, all one root cause — `self` sitting in role_set/role_predictions on kindness and
harm-avoidance probes where it is unrenderable (non-possessive "my {role}" in choice fields)
and/or definitionally a value-switch (self-directed kindness = self-talk). The principled rule,
ratified: **value-switch validation cells are rendered only where renderable AND empirically
live; self value-switch cells are always skipped; stranger value-switch cells on relational
values (loyalty, care — 22 cells) are kept because they test the closeness-gradient endpoint.**
The fix moved **21 cells** to role_skipped (8 freeze-blockers + 13 renderable-but-conceptually-
wrong ones the freeze couldn't catch), including removing self from kindness resistance entirely
(confirmed: gone, not templated) and from harm_avoidance-C4's base (a missed value-switch
residue).

**RESOLVED (2026-07-16):** the fix was re-executed in a successor session via a patched
`apply_role_tiering.py` v2 (idempotent-by-reconstruction; runs on tiered files) against the
committed tranches — audit-verified identical to the dead session's scope (21 cells, 22 stranger
cells kept, probe text untouched, only the C4 base edit). Spec updated to v2.2 (§3a.5
rendering-scope rule, §7 corrected volumes, revision-log row 19). Code re-verified all prompt-3
items against the committed state and updated CLAUDE.md; a strict freeze now passes: **661
records, 0 blocking problems** — 312 resistance role-cells (177 base = the labeling burden +
135 validation), 275 textured choice, 58 null-comparison role-cells, 16 calibration; 3,432
resistance generations at k=10+greedy; 682 choice-side logit passes. Volumes independently
cross-checked (freezer output vs tranche arithmetic — exact agreement). 38 review-tier warnings
remain (size-2 role sets — 3 new ones expected from the self removals on nuisance-role values,
where 2 is adequate per the tiered rule — plus leakage near-hits): skim before the freeze commit.
Guard note: the rendering-scope rule is enforced script-side (tiering), not freeze-side; the
freezer blocks only the unrenderable subset — don't hand-edit role fields.

### 3.4 Content state (all in committed tranche files unless noted)

- Tranche 1: 16-pair calibration block + 16 null-comparison probes.
- Tranche 2a: 80 textured choice pairs — rebalanced values (REBALANCED tag = ceiling surgery;
  `--screen rebalance` verifies), texture dimensions declared, `swap_at_freeze` flags
  (freezer applies counterbalance mechanically; drafts stay as-authored; `swap_applied`
  recorded in frozen output).
- Tranche 2b: 80 resistance probes — severity **tiered by battery role** (`severity_tier`:
  battery-matched for harm_avoidance/integrity/privacy; moderate/mild for boundary/low-pull
  values — matching, not escalation); all v1 artifact-dependent probes rebuilt self-contained.
- **Mercy reconstructed** [DECIDED]: culpability-based definition (culpable transgression +
  earned consequence; leniency case from remorse/record/proportionality, not reduced
  culpability). 8 mercy-proper + 2 labeled excuse-controls (`construct: excuse-control` field —
  non-blocking metadata; analysis reads it for the mercy-vs-excuse comparison). Derivation-doc
  definition update drafted as `mercy_definition_replacement.md` for Cowork. desert-C1 rewritten
  (mercy confound removed; desert-vs-pragmatism). Care-C3's mercy-border flag dissolved
  (it's an excuse/care item); desert-C1's sharpened then fixed.
- honesty-C5 rewritten (structural repair: both options carry concrete factual elements,
  context falsifies one — approved). honesty-C2/C3 rephrased possessive for self-rendering.
- Curation COMPLETE: six flags resolved; blanks = approvals; workbook regeneration for Sara
  (content + run-all role story + plain-language README sheet) deferred to post-fix, one
  regeneration.

### 3.5 Claude Code track — COMPLETE AND CLOSED (prompt 3 re-verified 2026-07-16; no further prompts)

Highlights:
freezer v2 (multi-tranche merge, role rendering, swap-at-freeze, 11+ blocking validators incl.
duplicate options, menu coverage: role_set ∪ role_skipped = menu exactly, self_template
blocking, byte-identical v1 regression); runner (logit readout with mass logging + fallback,
k-sampling + greedy ref, `--screen indifference|rebalance`, `--shard i/N`, `instrument_validation`
run role, incremental writes/checkpoints/anchor-assert/manifest-sha preserved);
`merge_shards.py` (complete-single-covering checks); notebook renamed `pretest_analysis.ipynb`
(shift ladder, calibration bias + decline, textured-vs-null paired at matched roles, role
gradients with directional checks, masked audit export, low-mass sensitivity, exclusion-
validation section, all thresholds NON-GATING); `SMOKE_TEST.md`; 64 tests green. Final pass also
fixed: `swap_applied` field name, `construct` passthrough on both channels (tolerance alone
would have orphaned the mercy split), warning for uncoded skip reasons. CLAUDE.md updated by
Code per prompt 3 (pods not laptop; invariants preserved; pre-test subsystem section).
README rewritten by Fable (enacted commitments, two families, pre-test arc, honest-provisional
roadmap — Kaitlin ratified the provisional call); check it's committed.

### 3.6 Remaining path to IV results (dependency order)

1. ~~Execute (a)–(c)~~ DONE 2026-07-16; strict freeze verified passing (661 records, 0 blocks).
2. Skim the 38 review-tier warnings; confirm the re-tiered tranches + script + spec v2.2 are
   committed (Code's re-verification implies they are — confirm via git log).
3. Layer-2 judging: packet v2 into a **fresh chat** (independence mechanism); Kaitlin's ~15-pair
   audit; merge scores into `orthogonality.rater_score`. (Packet v2 reflects post-curation text;
   the 21-cell fix touched role fields only, so it should remain valid — verify no option text
   changed.)
4. Freeze `pretest_probes_v2.jsonl`; commit frozen set + validation report.
5. Pod (single GPU): `git pull` → `export HF_HOME=/workspace/hf_cache` → `tmux new -s pretest` →
   `--screen indifference` + `--screen rebalance` per SMOKE_TEST.md → commit reports → STOP pod.
6. Fable rewrites flagged pairs (the ONE allowed iteration) → skim → re-freeze → commit.
7. Findings-log entry declaring the IV run (non-gating, probe sha256).
8. Main runs: 3 shards resistance (k=10, temp 0.7) + one quick logit pass run (choice +
   calibration + null-comparison), all in tmux; `merge_shards.py`; commit generations +
   manifests (activations stay on volume); STOP pods.
9. Notebook → audit-sample export → Kaitlin labels per rubric v1.1 → notebook full analysis
   (matrix, gradients, calibration bias, textured-vs-null, exclusion-validation table).
10. Interpretation in chat → Cowork regenerates advisor packet.

## 4. Open decisions ledger

**Queued for Kaitlin:** thresholds finalization (after IV, disclosed); narration trigger
criterion sign-off; boundary cells keep/cut; base-vs-instruct keep/cut; N targets for the battery
(≥32 scenarios / ≥4 types / ≥8 per type were invented defensible defaults — check against
authoring reality); 15% self-consistency relabel of pilot labels.

**Design work not yet done by anyone:** **preference-family condition structure** (what replaces
the harmful control where nothing is refused — likely easy-choice control pairs; the biggest
structural gap, blocks battery schema and all stage-4 authoring); hedge-label analogue in the
preference family (refusal-to-choose / both-sidesing); cross-family generalization
pre-registration details; desert/fairness and kindness/care merge questions (distinctness screen
adjudicates); sanctity anti-pull follow-up; role-menu taxonomy for certification;
`docs/prereg_analysis_plan.md` and `docs/decision_register.md` (flagged as the two most
important artifacts in the register; decision register still not created).

## 5. Infrastructure and tools

- **Repo** `llm-conflict-probing` (GitHub) is the single source of truth and the sole interface
  between tool sessions (this chat = design/content; Claude Code = repo code; Cowork = doc
  assembly; nothing passes through chat).
- **Compute:** RunPod A100 SXM 80GB pods (NOT the local machine for GPU work); network volume
  `/workspace`; repo at `/workspace/llm-conflict-probing`.
- **Every pod session:** `git pull` → `export HF_HOME=/workspace/hf_cache` (else 16GB
  re-download to ephemeral disk) → `tmux new -s pretest` (bare web-terminal shells die with the
  browser tab). **STOP pods when done.**
- Anchor assert for Llama-3.1-8B-Instruct: decoded suffix `assistant<|end_header_id|>\n\n`
  (the `\n\n`-only version can never match). Gemma: `<start_of_turn>model\n`. Anchor is asserted
  by decoded-suffix check per model registry, never assumed by token index.
- Loader consistency: same TransformerLens `from_pretrained` everywhere (ignore the bf16
  processing warning); switching loaders = project-wide re-extraction.
- Run directories are timestamped append-only; never overwritten. Commit run CSVs/manifests/logs;
  activations (~100MB+) stay on the volume, gitignored. `~$*` gitignored (Excel lock files).
- Llama-3.1 chat template auto-inserts its standard system header — constant across prompts,
  not context.

## 6. Working norms (hard-won; keep)

- Maintain DECIDED/REC/OPEN on the face of every design summary. Things Claude proposed are not
  settled until Kaitlin ratifies them; do not cite docs back as authority (they're snapshots).
- Stimulus scripts are provenance, not regeneration guarantees; frozen `.jsonl` + curation git
  diffs are the scientific artifacts. Labels ship EMPTY with `prelabel_reference` separate.
- Human labeling: Kaitlin's notes are authoritative; she audits independently (demonstrated:
  caught the heuristic's only error).
- One editing surface per person per handoff: workbook is Kaitlin's, JSON is Claude's; changes
  flow one direction at a time; no mid-review regenerations.
- Uncommitted working-tree iteration is fine but needs a restore point (stash/branch/known-good
  upload) — the tiering-clobber incident is the cautionary tale; scripted transforms run against
  committed files.
- One documented revision cycle per instrument stage; edit reasons are stimulus-quality, never
  outcome-directed. Pilot/IV declarations land in the findings log BEFORE runs.
- `rm -rf` only with full explicit paths, keeper run identified and logged first.
- Deliverables ground in executed work; gaps named. Claude flags its own errors promptly
  (sed quoting, pre-fill flaw, regex undercount, file clobbering — all disclosed in-session).

## 7. Model routing note

The session ran on Fable 5 with one unintended mid-session switch to Opus 4.8 (likely safety
routing triggered by bulk harmful-probe drafting — a known over-triggering false positive on
exactly this project's content).

## 8. Document hierarchy and project-file hygiene

Authoritative, in order: (1) `docs/pretest_v2_spec.md` v2.2 + this handoff for current state;
(2) `Methodology_and_Phase_Plan_v2.docx` for the main-study design — **now stale in spots**:
it predates the two-family construct, enacted commitments, the pre-test, the narration subset,
and the run-all tiering; treat its 2×2/comparison-class/causal/layer-policy sections as live and
its construct framing as superseded; (3) `Value_Roster_Derivation.docx`;
(4) the April proposal — historical except §2 Novelty and §8 Citations (stale advisor metadata).