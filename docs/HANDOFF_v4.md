# HANDOFF v4 — boot document (supersedes HANDOFF_v3)

Written 2026-07-17, during the shard-1 re-run of the IV administration. Purpose: everything a
fresh session needs that is not already obvious from the repo. The repo is the interface;
this document is the map. Tags: [DECIDED] researcher-ratified; [REC] standing recommendation;
[OPEN] undecided.

## 0. Project identity (unchanged from v3, compressed)

Value-conflict probing study, Llama-3.1-8B-Instruct primary. Research question: does value
conflict (a request setting two trained commitments in opposition) have a distinct internal
representation at the pre-generation anchor, or does it decompose into refusal /
emotion-concepts / generic decision competition? Pre-registered claims P1–P5; the
decomposition (null) result is publishable by design. Stage 1 = value pre-test (enacted
commitments → certified value set); Stage 2 = 2×2 tension battery (policy + preference
families); Stage 3 = probe geometry + distinctness controls (native re-derivation,
estimator consistency: difference-in-means everywhere); Stage 4 = causal; replication on
Gemma-2 (+9B leg planned) and base-model control throughout. Functional claims only.
Advisor (Dr. Sara Kingsley): measurement/evaluation framing, no mech-interp vocabulary in
her materials. Repo: github.com/kaitlinmoore/llm-conflict-probing.

## 1. Where things stand at time of writing

**IV administration in flight.** Declared 2026-07-16 in docs/findings_log.md, non-gating,
frozen instrument sha256 659afb97f154662da2d3b56c78ca26902d37fb88584b1218b511a474b336018b
(661 records; regeneration verified byte-identical from committed tranches). Shard 2/2
complete and fully intact (run 20260716_165958_...): 2,057 rows, manifest, 252MB
activations, all committed/volume-resident. Shard 1/2 first execution completed generation
(2,057 rows, committed) but its activations + manifest were truncated to zero-byte ~1h
post-completion — see docs/incident_2026-07-17_shard1_truncation.md; verdict: unattributed
MooseFS durable-write failure, human commands and merge exonerated, contributing factor:
in-place whole-file checkpoint rewrites. **Re-run of shard 1/2 launched 2026-07-17 on the
hardened runner** (fresh timestamped dir). Expected ~9–12h wall clock (the original took
~12h, NOT the ~5h estimated in-session — timestamps: 16:58 → 04:49).

**Hardening landed** (same-day commit): atomic tmp→fsync→rename on all manifest/activation
writes (runner + merge, checkpoint + final); completion DIGEST lines (sha256+bytes,
computed by re-reading persisted files) printed and recorded in manifest `output_digests`;
scripts/verify_run.py (per-check PASS/FAIL, exit 0 iff all pass; screen-aware; noted-skip
on pre-hardening manifests); runpy() function in scripts/env.sh; 73 unit tests (was 64).
Deferred to pre-certification round: part-file (append-style) activation checkpoints.
[DECIDED] Process rule: a run's outputs are committed (text) and sha-recorded (binary)
immediately upon completion, before anything else touches the run directory.

**Ops facts:** pods bill; the two IV-run pods were terminated at zero balance (no data
loss — volume + git held everything, including shard logs). Volume llm_conflict_study_volume,
EUR-IS-1, 50GB, ~21GB used. HF cache (20GB) is an asset, keep. Four stopped zombie pods
remain to terminate (Terminate ≠ volume deletion — read the dialog). Env ritual per fresh
terminal: `cd /workspace/llm-conflict-probing && source scripts/env.sh` BEFORE any uv
command (else duplicate venv builds onto the volume — quota incident class). `runpy` works
interactively; **nohup cannot see shell functions — use /root/venv/bin/python under nohup.**
uv sync ~5–10 min per fresh pod (venv on container disk by design).

## 2. Closeout checklist for the re-run (execute on pod, in order)

1. `tail -5 shard1_rerun.log` → completion lines + **three DIGEST lines** (their absence
   means pre-hardening code ran — stop and investigate).
2. `ls -1t results/pretest/ | head -3` → newest shard1of2 dir = <RERUN>.
3. `runpy scripts/verify_run.py results/pretest/<RERUN>` → all PASS (else stop, touch nothing).
4. `git add results/pretest/<RERUN>` → `git status` (NO .pt staged — gitignored) → commit
   ("...verified; activations sha per manifest output_digests") → push.
5. Merge: `runpy src/pretest/merge_shards.py --shards results/pretest/<RERUN>
   results/pretest/20260716_165958_llama8b_instrument_validation_shard2of2
   --probes data/pretest/pretest_probes_v2.jsonl` → "Merged 2 shards", 4,114 rows, exit 0.
6. `runpy scripts/verify_run.py results/pretest/<MERGED>`.
7. Add/status/commit/push <MERGED> (again: no .pt staged).
8. Console: STOP the pod; terminate the four zombies.
9. Retire the truncated first-execution shard1 dir from active use (its generations.csv
   stays committed as record + reproduction-check material).

[REC] Bonus exhibit when convenient: same-seed reproduction check — diff old vs new shard-1
generations.csv (modulo run_id fields). Match = a reproducibility receipt few studies have;
mismatch = important fact about stack determinism to know before certification claims.

## 3. Post-merge pipeline (Stage 1 completion)

1. **Audit-sample export** lands in <MERGED> (or runner equivalent) → Cowork builds the
   labeling workbook per its standing brief (docs/handoff_cowork.md): wrapped text, frozen
   header, ids masked, `final_label` empty, `prelabel_reference` visible, notes column.
2. **Kaitlin labels** under docs/labeling_rubric.md v1.1 (two-way taxonomy). 8 rows
   flagged "needing manual labeling" across the run (6 shard1-original + 2 shard2) surface
   here. Pilot lesson: notes are authoritative; her audit catches heuristic errors.
   Open item from pilot: 15% self-consistency relabel of pilot labels [OPEN, low priority].
3. **Thresholds decision — BEFORE unblinding the matrix** [DECIDED as procedure]:
   notebook computes calibration-block (16 identical-option pairs) format-bias distribution
   FIRST; criteria defined against it + pre-stated conventions; decision recorded (register
   + findings log); ONLY THEN compute the per-value matrix. Sara's three questions (status
   doc §6) feed this: (1) dominance as auxiliary enactment evidence — acceptable? what
   additional control? (2) response-format trade — sensitivity analysis vs answer-only
   instruction; captured-mass floor below which renormalized p is untrusted? (3) absolute
   change vs baseline-respecting scale (odds ratios) for choice criterion; dominance pass
   criterion relative to calibration distribution? Her answers → drafted decision here or
   in fresh session.
4. **Notebook** (notebooks/pretest_analysis.ipynb): enactment matrix (16×2), calibration
   bias, dominance indicators for ceiling pairs (per D1, screen memo), textured-vs-null
   exhibit (Sara's requested exhibit), role gradients + exclusion-prediction validation,
   low-mass sensitivity analysis (impartiality median mass 0.111 = worst; possible
   "indeterminate pending format fix" outcome for it).
5. **Interpretation + advisor packet regeneration** (Cowork standing brief task 2).

## 4. Fast-path certification [DECIDED as available option, researcher exercises]

"Non-gating" ≠ "cannot certify": it meant no post-hoc failure by unpre-registered
thresholds. If analysis shows no instrument defects: (a) declare the documented-adjustments
round EMPTY (one-line register entry with reasons); (b) adopt IV data as certification
data by declared decision — a ritual re-run of an unchanged deterministic-readout
instrument with fixed seeds would reproduce the same bytes; adopting is the honest version.
Conditions: thresholds set before unblinding (§3.3); "imperfect" handled granularly —
certify clean values, mark contaminated ones (likely impartiality) indeterminate-pending-
format-fix, proceed. Partial certification with named exceptions is a defensible
measurement outcome. If analysis DOES surface defects → the sanctioned adjustments round
exists precisely for that; using it is not failure. After certification: the distinctness
screen (kindness↔care, fairness↔desert merges; authority↔integrity if authority shows
life) — [OPEN] whether IV response profiles suffice or new data needed; decide on seeing
the matrix.

## 5. Pre-registered informal predictions [REC: commit before unblinding — evidential value]

Filed 2026-07-17, before any IV analysis. Non-binding handicapping; value = making
surprises register as surprises. Near-locks: honesty, harm_avoidance, privacy, integrity,
autonomy (autonomy via dominance — 3 ceiling pairs, 2 floors, zero mid-range). Likely:
fairness, loyalty, care (all-floor: if disclosed-vulnerability contexts move it, cleanest
floor-to-shift evidence), desert (enacts; jeopardy is the fairness/desert merge). Moderate:
kindness (likely merges with care), collective_welfare, tradition. Coin flips: mercy
(threshold-scale-dependent — floors handicapped on absolute shift, strong on odds ratios;
Sara Q3 made flesh), impartiality (enacted but possibly uncertifiable this round — mass).
Designed failures: sanctity (slightly more life in screens than roster expected — the
0.995 mock-funeral ceiling may be tact/harm cross-loading), authority (the question is
whether the role gradient separates deference from ambient instruction-following; roster
prediction: merge into rule-following or unenacted-after-controls). Net expectation:
~11–13 certified values after merges — ample pairable material for the battery.

## 6. Stage 2+ checklist (post-confirmed-values; produced in-session, commit-worthy)

**Pair selection & design:** channel-eligibility table (which values passed which channel;
bridge values eligible both families) → tension-pair selection AS A RECORDED DECISION
against pre-stated criteria (pairability, counterbalancing, bridge coverage, budget) BEFORE
any authoring → preference-family condition structure (the major undesigned piece) → 2×2
per tension (conflict toggled × resolution tipped via JUSTIFICATION strength, never tension
strength) → controls per tension (harmful-only twin, benign twin, generic decision-
competition) + narration subset with pre-registered carryover protocol → volume/budget math
BEFORE authoring (labeling burden first — her hours are the binding constraint, pilot lesson).
**Authoring & validation (reuse pre-test machinery):** authoring-rules doc → freezer/
validators extended to battery schema → three-layer review (rules; blind judge + human
audit; behavioral screens on neutral forms) → verified behavioral labels per cell → one
documented rewrite → freeze, sha, declaration.
**Stage 3 prerequisites (parallelizable):** comparison directions re-derived natively on
the frozen battery model — refusal (DIM), emotion vectors (Phase 0 assets; Llama focus
layer ≈44% depth, plateau 12–15; Gemma-2-2B ≈85%; Gemma-2-9B-IT leg planned, HARC anchor
L34/42) — same estimator everywhere; entropy covariate confirmed in outputs; independent
read-out slot decision [OPEN]: AO released checkpoint
(adamkarvonen/checkpoints_latentqa_cls_past_lens_Llama-3_1-8B-Instruct) vs J-lens vs NLA
(transformer-circuits.pub/2026/nla — see §7) vs none; trigger = Stage 2 design stable;
activation caching sized (volume resize stops being optional at battery scale; Gemma-9B
~18GB also pressures the 50GB).

## 7. NLA placement (new since v3)

NLA = Natural Language Autoencoders (Anthropic, Transformer Circuits 2026-05-07;
Fraser-Taliente/Kantamneni/Ong et al.): activation verbalizer + reconstructor, RL-trained
unsupervised for reconstruction; explanations read as interpretations. Slot: Stage 3
independent read-out candidate ALONGSIDE AO and J-lens — same gated status. For NLA
specifically: (+) unsupervised = no question-cue to confabulate around (paper's own
argument: unprompted outputs carry more evidential weight — directly strengthens the
dissociation test vs AO's targeted-question weakness); their unverbalized-eval-awareness
validation is structurally the template for a conflict version. (−) confabulation (trust
themes over specifics; recurring claims more reliable), grader burden (a conflict-mention
grader over noisy free text = the AO sub-project's known scope risk, enlarged), layer
sensitivity (NLAs read ONE layer; check against the ~44%-depth focus layer), availability
(released open-model NLAs + Neuronpedia frontend — VERIFY Llama-3.1-8B-Instruct coverage
when decision goes live; training one = joint RL on two full models, out of scope).
[OPEN] Literature characterization entry (stated-vs-inferred + locus pointers) not yet
written — offered, pending. Advisor framing: "a second, independent instrument that reads
internal states in natural language — convergent evidence, multitrait-multimethod."

## 8. Advisor state

Sara has: Pretest_Status_Update_2026-07-16.docx (with §6 full-form questions 1–3),
6-slide two-panel deck + speaker notes, Study_Overview_Plain_Language.docx (whole-study,
committed spine only — AO/NLA deliberately absent as gated contingencies; one-paragraph
Stage 3 addition drafted-in-principle if a read-out is ever adopted). Choice-channel
probability explanation delivered at 3 depths (core: read P(A)/P(B) from next-token
distribution at the answer point; caveat: mass renormalization + per-item logging).
"Why remove values" answer on record: enactment gate = manipulation check; three fates
(excluded→controls, merged→discovery, indeterminate→deferred); pre-registered failures
give the gate teeth. [OPEN] Her answers to Q1–Q3 → thresholds decision.

## 9. Working norms (unchanged, load-bearing)

One rewrite iteration per administration (executed for IV; next sanctioned round =
pre-certification documented adjustments). Reasons stimulus-quality only, never
outcome-directed. Append-only logs; decisions attributed to researcher in the register.
Confirmation-type context defects attenuate SHIFT and are INVISIBLE to screens (screens
measure neutral-form balance only) — decide such flags on construct grounds. Judge
loading discriminates value-driven ceilings (don't rewrite; dominance) from
attractiveness-driven (rewrite). Editing surfaces: design chat authors content; Code owns
src/tests; Cowork owns docs/bookkeeping per standing briefs; register/log write path =
Code/Cowork on instruction. Deliverables grounded in executed work; gaps named. docx for
advisor-facing; measurement framing there. Fresh-context judging for independence.
Claude's memory of this project compacts and dies — the repo and this document are what
persist; update HANDOFF at each major transition (v5 due when Stage 2 design settles).
