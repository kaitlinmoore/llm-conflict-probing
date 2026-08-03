# Battery validator backlog

Produced by: Claude Fable 5 (model id `claude-fable-5`). Queue of validator
checks requested but not yet implemented in
`src/battery/validate_battery.py`. Items move out of here when implemented
(with tests) and noted in the validation report.

## Pending workbook edits (researcher-logged)

Applied by `src/battery/apply_pending_edits.py` — dry run by default,
`--apply` to write, idempotent, refuses while Excel holds the file open.
**Status 2026-07-31: queued, NOT yet applied** (workbooks are live under the
review pass; run it when they are closed).

2. **T12 `CB-acw-S5` stem — `deserves`** (desert list, 4 cells) and
   **T2 `CB-pc-S1` shared opposition text — `safety`** (harm list, 2 cells).
   Blocking under global scope (researcher, 2026-07-31). Replacement wording
   comes from the design chat; **not yet in the script's edit list**, and
   deliberately not exempted — validation failing on exactly these 6 hits is
   the correct state until the rewrites land.

1. **type-1 "The toast" stem** contains "really cared about getting it
   right" — swap to "wanted it exactly right" (researcher, 2026-07-30).
   Bare "care/cared/caring" is discipline-only, not blocklisted, so the
   validator will not catch this; it is tracked here instead. 4 occurrences
   (the stem repeats across the scenario's four cells).

## Accepted findings (no action)

- Type-1 `agree_A` insert-length flags (3 cells) accepted 2026-07-30:
  those inserts carry flaw-establishment plus alignment by design.
  Revisit only if the review pass agrees they're bloated.
- `docs/WEEK_PLAN_stage2.md` is **intentionally untracked** (researcher,
  2026-08-05; internal working doc). Do not commit it and do not flag it;
  add to `.gitignore` only on explicit researcher direction. (No standing
  backlog item existed to strike — recorded here so fresh sessions stop
  re-raising it.)

## Done

1. **Cross-type character-name uniqueness** — IMPLEMENTED 2026-07-31
   (non-blocking, in `validate_battery.py`). Reports exact reuse across
   type files plus near-collisions (shared 4-letter prefix). Findings in
   `docs/battery_validation_report.md`.
2. **Insert↔option overlap (check f)** — IMPLEMENTED 2026-08-04 (blocking,
   choice family; set-based ≥4 shared contentful words, names/stopwords
   masked, calibrated on the researcher's T1 S2/S4/S5 seeds; per-instance
   exemptions in `data/battery/overlap_exemptions.json`, none granted).
   Refusal ask-echo analogue informational (0 flags). 10 hits, all left
   failing pending B1 paraphrase drafts. Inventory + ruling tables in
   `docs/closeout_staging_2026-08-04.md`.
3. **Batch dry-run infrastructure** — 2026-08-04: `apply_pending_edits.py`
   gained `--edits` (JSON batch), mixed-XML-encoding matching (Excel re-save
   vs Cowork entity storage), and a per-edit re-read fixing an edit-stacking
   clobber. Batch in `data/battery/pending_edit_batch.json` (41 edits;
   40/41 byte-exact).

## Open

- **Delta review** (researcher): 117 content cells + 203 certified
  spot-sample cells; T11/T12 verdict entry (46 cells). Worklist in
  `docs/batch_apply_report_2026-08-05.md`. Then exhibit embedding run →
  freeze per `docs/freeze_checklist.md`.

_Resolved 2026-08-05 (follow-up cycle): two-cell repair executed as ruled
(cell surgery, verified byte-exact); options-uniformity check c2 built,
tested, permanent — battery-wide PASS; 40-sentence battery-wide semicolon
batch applied (audit: all clause-joining → period). Validation fully
GREEN: 277 cells, 0 blocking. Zero em dashes and zero semicolons in all
stimulus text. Certificate: 203/203 mechanical cells PASS._

_Resolved 2026-08-05 (apply session): batch APPLIED (352/352; 385
punctuation substitutions), re-ingested, re-validated — 6 lexeme + 10
overlap hits cleared, check f green on batch-touched cells; em dashes in
stimulus text 583 → 0; renames verified (Priyanka/Devora intact modulo
ruled A7 #21/#22); mechanical certificate 144/145 (1 FAIL = the T4 defect
above); Meera/Arun applied._
- **Freezer hardening** (B4, researcher-confirmed rec stands): exact-match
  `approve` filter vs observed whitespace variance (`'edit '` in T1
  CB-hc-S2 agree_A) — when the battery freezer is built, strip + validate
  tokens + report drops loudly. Pre-freeze verdict-integrity report is now
  step 6 of `docs/freeze_checklist.md`.

_Resolved 2026-08-05: A3 case drift (manifest corrected, batch regenerated);
B1 superseded by A9 option generalizations (word-type check RATIFIED); B2
ruled (proposals in `docs/emdash_replacements_2026-08-05.md`; actual
new-wording dash count 16, not 14); B3 five renames approved and in the
batch; T9 control-verdict discrepancy (A8 reconciled: stale upload)._

- **Provisional embedding-run location (2026-08-03).** The `--provisional`
  plumbing run of `stimulus_similarity.py` lives at
  `C:/Users/redsk/AppData/Local/Temp/ss_dry/20260731_174816_ingnoingest_PROVISIONAL`
  — OS temp, may be cleaned at any time. Deliberately uncommitted (pre-freeze
  working data, superseded at freeze). The numbers the 2026-08-03 diagnostics
  used are snapshotted in
  `results/stimulus_similarity/20260803_PROVISIONAL_diagnostics.md`; if the
  temp dir vanishes, re-running `--provisional` on the unchanged drafts
  reproduces it exactly (digest-verified 17/17, reproduction checked to 6
  decimals).
- **T2 control-set coupling (flagged to design chat 2026-08-03, researcher's
  call, no action).** From the provisional diagnostics: TC-pc-2 (margin
  −0.032) is under-coupled to its T2 targets more than captured by wrong
  types; TC-pc-3 borders the same state (+0.014, zero own-type cells in its
  nearest-10). The T2 controls as a set couple far more weakly to their type
  than the T8/T9/T10 control sets. Provisional numbers; re-read at the
  post-freeze exhibit run before any decision.
