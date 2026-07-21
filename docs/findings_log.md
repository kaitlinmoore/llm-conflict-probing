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
