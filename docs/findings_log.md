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
