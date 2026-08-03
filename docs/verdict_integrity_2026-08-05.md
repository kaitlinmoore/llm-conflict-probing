# Pre-freeze verdict-integrity report — 2026-08-05

Produced by: Claude Fable 5 (model id `claude-fable-5`), freeze checklist
step 6, run after the researcher's completed delta-review pass
(2026-08-05). Reads the re-ingested drafts (workbook state of the delta
pass; `ingest_manifest.json` regenerated this run).

## Result: ZERO non-approve tokens battery-wide

| population | records | exactly `approve` | anything else |
|---|---|---|---|
| battery cells | 264 | 264 | 0 |
| topical controls | 13 | 13 | 0 |
| **total** | **277** | **277** | **0** |

Checked with exact string equality (case- and whitespace-sensitive, the
freeze filter's own criterion): no blanks, no `edit`, no whitespace
variants (the previously observed `'edit '` at T1 CB-hc-S2 agree_A is
resolved), no other tokens. T11/T12's 46 delta-entered verdicts and the
re-confirmed stray approves are included.

**Freeze-filter consequence: an approve-only freeze would keep all 277
records and silently drop zero.**

Companion checks run alongside (same drafts state):

- **Stimulus text unchanged by the delta pass:** 0 of 277 records differ
  from the applied-batch state (HEAD) in any stimulus field — the pass
  touched verdicts only. (This check exists because the review pass
  previously introduced two accidental cell edits; the options-uniformity
  validator check c2 also passes.)
- **Validator: PASS** — 0 blocking, 0 warnings; residue unchanged
  (4 length flags: 3 accepted + 1 median-shift artifact; 2 name flags:
  `Mom` kept by ruling + extractor artifact).
- Count labeling note: the validator's verdict line says "277 cells
  checked" — that figure counts records (264 cells + 13 controls); the
  battery's cell count is 264 (6 choice types × 20 + 6 refusal types
  × 24). Cosmetic mislabel in the report line, tracked in the backlog.
