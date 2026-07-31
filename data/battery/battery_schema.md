# Battery draft schema — `battery_draft_v1`

Produced by: Claude Fable 5 (model id `claude-fable-5`), 2026-07-30 session 1.
Status: infrastructure definition for Stage 2 ingest/validation. Content
decisions remain the researcher's; open questions are listed at the bottom
for researcher decision, per standing rules.

## Scope

Defines the JSONL record format emitted by `src/battery/ingest_workbook.py`
into `data/battery/drafts/<type_id>.jsonl`, and consumed by
`src/battery/validate_battery.py`. One record = one **cell** (one condition of
one scenario). The freezer (later task) consumes these drafts; only rows whose
`metadata.reviewer_verdict == "approve"` are freeze-eligible.

This schema does NOT fix prompt rendering (how stem / inserts / options
compose into the administered prompt). Rendering is the freezer/runner's
contract and is deliberately out of scope here.

## Families

`type_num` decides the family (slate in `docs/WEEK_PLAN_stage2.md`, structure
per D45), and the sheet must agree with it — ingest raises otherwise.

| | choice family (types 1–6) | refusal family (types 7–12) |
|---|---|---|
| conditions | `agree_A`, `agree_B`, `oppose_tip_A`, `oppose_tip_B` | `agree_comply`, `agree_refuse`, `oppose_tip_comply`, `oppose_tip_refuse` |
| resolution field | `expected_pick` ∈ {A, B} | `expected_response` ∈ {comply, refuse, hedge} |
| options | `option_A_<x>` / `option_B_<x>` columns required | none (no options, no order counterbalance) |
| person variable | `relationship` | `subject` (self, confidant, friend, sibling, colleague, cousin, neighbor, teammate, …) |
| controls sheet | T2 | T8, T9, T10 |

Per-type declared design variables (`duty_source`, `domain`,
`activity_domain`, `standing_type`, `continuity_depth`, `stakes`, `ask`,
`structure`, `subject`, `relationship`, …) are **not** normalized: every
non-core column is carried through verbatim in `extra_fields` under its
original header.

**Blocklist scoping uses `type_values`, parsed from the workbook filename**
(`CB_type7_harm_vs_autonomy` → `["harm", "autonomy"]`), not the option-column
suffixes. Types 5 and 6 name their options by stance (`option_A_hold`,
`option_A_directive`), so the suffixes cannot identify the poles; the
suffixes are still recorded as `value_A` / `value_B` where present.

## Record types

Two record types, discriminated by `record_type`:
`"battery_cell"` (one condition of one scenario — the main format below) and
`"topical_control"` (topic-matched value-free control items from a
workbook's `Topical_controls` sheet; ingested by researcher direction
2026-07-30, distinct item class; more control sheets arrive with types
9–10). Control records go to `<type_id>.controls.jsonl` beside the cell
file.

`topical_control` fields: `schema_version`, `record_type`, `type_id`,
`type_num`, `family`, `type_values` (the type's two value names, parsed from
`type_id`, used for blocklist scoping — controls are value-free but must
still pass the type's leakage lists), `control_id`, `matched_domain`,
`stem`, `option_A`, `option_B`, `note` (authoring commentary, non-stimulus),
`metadata` (same shape as below). Control stimulus fields for
leakage-checking: `stem`, `option_A`, `option_B`.

Controls follow their family: **choice-family controls are two-option items**
(T2), **refusal-family controls are single assistance asks with no options**
(T8/T9/T10) — a format-matched compliance baseline, not a choice. Their sheets
also annotate the stem header with the control's design intent, e.g.
`stem (assistance ask, no condition, no concealment)`; ingest normalizes that
to `stem` and records the original header in
`metadata.source.stem_header` (normalization #3).

## Record fields (`battery_cell`)

| field | type | notes |
|---|---|---|
| `schema_version` | str | `"battery_draft_v1"` |
| `record_type` | str | `"battery_cell"` |
| `type_id` | str | from workbook filename `CB_<type_id>.xlsx`, e.g. `type1_honesty_vs_care` |
| `type_num` | int | parsed from `type_id` |
| `family` | str | `choice` (types 1–6) / `refusal` (types 7–12), per the twelve-type slate in `docs/WEEK_PLAN_stage2.md` |
| `scenario_id` | str | e.g. `CB-hc-S1`; scenario = 4 cells |
| `title` | str | workbook-facing scenario name |
| `condition` | str | exactly one of `agree_A`, `agree_B`, `oppose_tip_A`, `oppose_tip_B` |
| `condition_label` | str | workbook-facing long label |
| `stem` | str | shared scenario text; must be byte-identical across a scenario's 4 cells |
| `option_A` | str | verbatim option text (stimulus) |
| `option_B` | str | verbatim option text (stimulus) |
| `value_A` | str | value name parsed from the workbook's `option_A_<value>` header |
| `value_B` | str | value name parsed from the workbook's `option_B_<value>` header |
| `shared_opposition_text` | str | empty in `agree_*` cells; byte-identical across the two `oppose_tip_*` cells of a scenario |
| `condition_insert` | str | the cell's condition-specific text (stimulus) |
| `expected_pick` | str | `A` or `B` |
| `design_note` | str | author-facing rationale; NOT stimulus |
| `extra_fields` | dict | per-type authoring columns passed through 1:1 under their original headers (e.g. `structure`, `investment` / `stakes` / `domain`, `ask`, `relationship`) |
| `metadata` | dict | see below |

`metadata`:

| key | notes |
|---|---|
| `reviewer_verdict` | carried verbatim from the workbook (`approve` / empty / other) |
| `reviewer_comments` | carried verbatim |
| `source.workbook` | workbook filename |
| `source.workbook_sha256` | sha256 of the workbook file at ingest time |
| `source.sheet` | always `Scenarios` |
| `source.row` | 1-based row number in the sheet |
| `source.shared_text_header` | the original column header that populated `shared_opposition_text` (see normalization note) |

## Normalizations applied at ingest (all recorded in metadata)

1. **`shared_conflict_text` → `shared_opposition_text`.** The type-1 workbook
   names this column `shared_conflict_text`; types 2–3 and the task spec say
   `shared_opposition_text`. Ingest normalizes to the spec name and records
   the source header. No text is altered.
2. **`option_A_<value>` / `option_B_<value>` → `option_A` / `option_B` +
   `value_A` / `value_B`.** The value names ride in the workbook headers; they
   are split out so validation can select the right lexeme blocklists.

No cell text is trimmed, re-encoded, or otherwise modified: byte-identity
checks downstream are meaningful only if ingest is byte-faithful.

## Stimulus vs. non-stimulus fields (leakage-check scope)

Fields treated as **stimulus** (lexeme-blocklist-checked, blocking):
`stem`, `option_A`, `option_B`, `shared_opposition_text`, `condition_insert`.

Fields treated as **non-stimulus** (not checked): `title`, `condition_label`,
`design_note`, `extra_fields`, all metadata. Rationale: these are
workbook/reviewer-facing and are not part of the rendered prompt; design notes
legitimately name the values under test.

## Uniqueness and completeness invariants (enforced by the validator)

- `(scenario_id, condition)` unique within a type file.
- Each `scenario_id` has exactly the 4 conditions
  `{agree_A, agree_B, oppose_tip_A, oppose_tip_B}`.
- `stem` byte-identical across a scenario's 4 cells.
- `shared_opposition_text` byte-identical across the two `oppose_tip_*` cells.
- `option_A`, `option_B` nonempty and mutually distinct; `expected_pick` ∈ {A, B}.

## Open questions for the researcher

1. **Leakage-check scope** — RESOLVED 2026-07-30: researcher confirmed
   stimulus-fields-only is correct.
2. **Type-2 `Topical_controls` sheet** — RESOLVED 2026-07-30: researcher
   directed ingest; `topical_control` record type added (see Record types
   above).
3. **`shared_conflict_text` header** — still open: normalized at ingest; if
   instead the workbooks should converge on one header, that is an
   authoring-side edit.
4. **Blocklist scope across types** — RESOLVED 2026-07-31 (researcher):
   **global scope adopted**. Every type's stimulus text is validated against
   the `global` list and all nine ratified per-value lists, not only its own
   poles. Rationale on record: third-value lexemes are held to the same
   standard as third-value pressure (authoring rules 1 and 6); this matches
   the READMEs' existing "apply globally" language — own-pole scoping was the
   validator's interpretation, never a ratified decision. `discipline_only`
   stays unenforced everywhere; global scope extends only the nine ratified
   lists.

   **Known-pending consequence:** validation currently FAILS on exactly 6
   hits, and that is the correct state until the queued rewrites land —
   `deserves` in T12 `CB-acw-S5`'s stem (4 cells, `desert` list) and `safety`
   in T2 `CB-pc-S1`'s shared opposition text (2 cells, `harm` list). Both are
   queued as text rewrites in the pending-edits batch after the review pass
   closes, not as exemptions. Do not edit stimulus text to make the run pass.

   **Exemption mechanism** (`data/battery/blocklist_exemptions.json`): a
   documented per-instance record — cell, lexeme, rationale, date, grantor —
   downgrades one hit to informational. Exemptions are always printed in the
   validation report and never suppress silently; one that stops matching is
   reported as stale. The condition slot accepts `*` for a scenario-wide
   grant, since a stem hit appears in all four cells. None are granted; the
   mechanism exists so a future innocent hit cannot force a retreat from
   global scope.
