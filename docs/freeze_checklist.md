# Freeze checklist — conflict battery

Produced by: Claude Fable 5 (model id `claude-fable-5`), 2026-08-05, seeded
from `batch_manifest.md` §C plus the ruled verdict-integrity step (§B4).
Order is the gate sequence; no step runs before the one above it is green.

1. **Close all workbooks** — `apply_pending_edits.py` refuses while Excel
   `~$` lock files exist; unsaved review edits would be lost.
2. **Apply the batch** — `apply_pending_edits.py --edits
   data/battery/pending_edit_batch.json --apply`, only after the researcher
   confirms the dry-run report (`docs/batch_dryrun_2026-08-05.md`).
3. **Re-ingest** — `ingest_workbook.py`; drafts and `ingest_manifest.json`
   regenerate.
4. **Re-validate** — `validate_battery.py`; expect PASS: the 6 lexeme hits
   and 10 overlap hits clear, zero new blocking, check f green under the
   ratified word-type operationalization.
5. **Changed-cell delta review** (researcher) — worklist grouped by check
   class in the dry-run report: privacy-still-pulls (A7), ask-coincidence
   (A5/A6), option-generalization (A9), control-repair (A10), rename-only,
   dash-only. Flip verdicts to approve; T11/T12 verdicts are entered here
   (46 cells; re-confirm the two stray approves).
6. **Pre-freeze verdict-integrity report** — list every `reviewer_verdict`
   token that is not exactly `approve` (case- and whitespace-sensitive),
   with cell IDs and counts, before the freezer runs. The freeze filter
   silently drops non-`approve` rows; this report is the loud check that
   nothing is dropped unintentionally (observed variance on record:
   `'edit '` with trailing space, T1 CB-hc-S2 agree_A). Freezer hardening
   recommendation (strip + validate + report) stands for when the freezer
   is built — `docs/battery_validator_backlog.md`.
7. **Exhibit embedding run** on freeze-candidate text
   (`stimulus_similarity.py`, no `--provisional`).
8. **Freeze** — approve-only rows, sha over the frozen set, both option
   orders generated for choice items.
