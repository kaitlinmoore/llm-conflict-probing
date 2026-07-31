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

## Done

1. **Cross-type character-name uniqueness** — IMPLEMENTED 2026-07-31
   (non-blocking, in `validate_battery.py`). Reports exact reuse across
   type files plus near-collisions (shared 4-letter prefix). Findings in
   `docs/battery_validation_report.md`.

## Open

_(none)_
