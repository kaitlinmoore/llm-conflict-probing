# Battery validator backlog

Produced by: Claude Fable 5 (model id `claude-fable-5`). Queue of validator
checks requested but not yet implemented in
`src/battery/validate_battery.py`. Items move out of here when implemented
(with tests) and noted in the validation report.

## Open

1. **Cross-type character-name uniqueness** (researcher-requested,
   2026-07-30; NON-BLOCKING warning). Detect the same character name used in
   scenarios of different tension types. Rationale: types 1 and 4 shipped
   with two collisions (Sam, Dana); reused names risk cross-item association
   in administration and muddy per-type similarity readings. Sketch: extract
   capitalized given names from stimulus fields (stem, options, shared text,
   inserts), compare across type files, warn on any name appearing in more
   than one type_id. Needs a small allowlist for non-name capitals
   (sentence-initial words, place names).
