# Batch dry-run report — complete batch, 2026-08-05

Produced by: Claude Fable 5 (model id `claude-fable-5`).
**APPLY IS GATED ON RESEARCHER CONFIRMATION OF THIS REPORT. Nothing has
been applied; workbook text is untouched.** Batch:
`data/battery/pending_edit_batch.json` (350 edits), built from
`batch_manifest.md` (957e74c) + `silence_class_edit_table.md`.

## Headline

**350 / 350 edits match the current workbooks byte-exact. 0 unmatched,
0 already applied.** A3's corrected old-string now matches. Suite 216 OK.

Composition: A-edits (A1–A7, A9, A10) run first, then 287 em-dash edits
(B2), then 7 rename edits (B3) — ordered so every find-string matches the
text state at its turn and **every location is touched exactly once**.

| segment | edits | notes |
|---|---|---|
| A1–A7 | 41 | 3 of them composed with dash normalization (see below) |
| A9 option generalizations | 6 | T3 S1 composed with approved Devon→Trent |
| A10 control repairs | 9 | 3 stems + 6 option adjustments (**flagged**) |
| B2 em-dash convention | 287 | sentence-level; full list in `emdash_replacements_2026-08-05.md` |
| B3 renames (approved five) | 7 | 3 bare-name + 4 context-bounded replacements |

## Points needing researcher eyes before confirmation

1. **A10 option columns could not be preserved** — the ruled stems change
   the choice content, so all six option cells are adjusted minimally to
   match (flagged per the manifest's own note):
   - TC-pc-2: "Lead with the decade." / "Lead with the freelance year." →
     "The card with a long note." / "The short video."
   - TC-pc-3: "The furnished month-to-month." / "The cheaper annual lease."
     → "Furniture first." / "Kitchen and basics first."
   - TC-pc-4: "The weekend brunch." / "The evening open house." →
     "Her grandmother's recipes." / "Her favorite takeout spread."
2. **New-wording dash count is 16, not the manifest's 14** (A5 ×6, A6 ×6,
   A7 ×4 — #8, #10, #14, #16, #18 is 5 but #10's old also had a dash so the
   net-new count depends on the counting rule). All 16 are normalized in
   the batch JSON; ruled → applied wordings listed at the bottom of the
   em-dash file. No wording carries an em dash post-batch.
3. **Composed edits (8 + 3):** several ratified old-strings are fragments
   of dash-bearing sentences (T10 stems #13/#15/#17/#18, T2 stem #2/#3,
   A1, A4 both). Skipping those dashes would leave the post-batch text
   convention-dirty; instead each such sentence is ONE sentence-level edit
   with the A-content applied and the dash normalized (refs marked `+B2`).
   8 further dash sentences are fully owned by A-edit old-strings and are
   correctly superseded (A2, A7 #1/#9/#10/#11/#12/#14/#16).
4. **Em-dash proposals** (`docs/emdash_replacements_2026-08-05.md`,
   grouped by class for scanning): 287 sentences covering 342 dashes —
   clause→period 99, elaboration→colon 75, clause→semicolon 55,
   paired→commas 55, conjunction→comma 3. Classification is heuristic;
   known weak pattern: a right-hand fragment with an embedded relative
   clause can classify clause→period and produce a fragment sentence
   (e.g., CB-aa-S3 stem "I'd planned the reverse — the sequence I've
   worked out…" → period; colon likely better). Scan the clause→period
   group hardest. Accounting: 342 (B2) + 8 (composed) + 8 (superseded) =
   358 = the full inventory.
5. **Rename proposals, held for confirmation (NOT in the batch):**
   - **Priya (T4 CB-lh-S1) → Meera** — female in text; Indian-texture
     preserved; no 4-prefix collision post-rename; no blocklist echo.
     Clears the Priya/Priyanka near-collision (Priyanka T10 keeps).
   - **Dev (T2 CB-pc-S5) → Arun** — male in text; same register as Dev;
     no collision; clears the Dev↔Devora adjacency (Devora keeps).
6. **Name-safety verification** (why the batch is substring-safe): bare
   replaces used only where substring count == whole-word count in the
   workbook's stimulus text (Marcus 4/4, Devon 10/10, Dana 11/11); Sam is
   replaced via context-bounded strings whose occurrences cover exactly
   the whole-word count (T1 5/5, T3 2/2), so no "same"-type corruption and
   no missed occurrence is possible.

## Planned delta-review worklist (260 changed cells, by check class)

Each cell is listed once under its highest-attention class; secondary
changes (dashes, renames) ride along in the same cells.

| class | cells | scope |
|---|---|---|
| privacy-still-pulls (A7) | 39 | all T10 scenarios (24); T2 S2/S3/S4 all cells, S1 tip_A, S5 both tips |
| ask-coincidence (A5/A6) | 48 | all T11 + T12 cells (verdict-entry pass for both types) |
| option-generalization (A9) | 24 | T1 all scenarios, T3 S1 |
| control-repair (A10) | 3 | TC-pc-2/3/4 |
| lexeme/wording (A1–A4) | 1 | T2 S1 oppose_tip_B (A2 shared text; tip_A sits in A7 class) |
| rename-only | 4 | T4 CB-lh-S5 (Dana→Rowan) |
| dash-only | 141 | T3–T9 broadly + T2 S1/S5 agree cells + TC-pc-1 — byte-scan class |

(Full cell-by-cell list reproducible from the batch; the post-apply report
will re-derive it from actual diffs.)

## On confirmation (the trigger), the sequence is

close-workbooks check → `apply_pending_edits.py --edits
data/battery/pending_edit_batch.json --apply` → re-ingest → re-validate.
Expected end state: **all 16 blocking hits clear (6 lexeme + 10 overlap),
zero new hits, check f green** under the ratified word-type
operationalization. The post-apply report will include the re-validation
verdict and the changed-cell list re-derived from actual workbook diffs.
