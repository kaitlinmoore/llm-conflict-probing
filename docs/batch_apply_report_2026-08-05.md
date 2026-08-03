# Batch apply report — 2026-08-05

Produced by: Claude Fable 5 (model id `claude-fable-5`), same session as the
confirmed dry-run. Sequence executed per confirmation: regenerate (renames
Meera/Arun folded in; 27 authorial semicolons converted, ruled in scope) →
dry-run **352/352 byte-exact, 0 unmatched, 0 already applied** → no Excel
locks → **APPLIED** → re-ingest → re-validate.

## Superseded figures, restated

- Edit total: **352** (350 + Meera + Arun).
- Punctuation-substitution accounting: **385 substitutions** — 358 em
  dashes (342 in B2 edits + 8 inside composed A+B2 edits + 8 superseded
  into A-edit rewrites) **+ 27 converted authorial semicolons** (conversion
  record in `emdash_replacements_2026-08-05.md`; conjunction→comma,
  clause→period, fragment→colon/comma per the amended convention).
- Backups: `*.bak-20260803T141934Z` beside each workbook (untracked).

## Re-validation: 16 → 2 blocking. The 2 are NOT batch effects.

**Cleared as expected:** all 6 lexeme hits (T12 `deserves` ×4, T2 `safety`
×2) and all 10 overlap hits — **check f is green on every batch-touched
cell**. Refusal ask-echo: 0. Exemptions used: 0.

**Remaining 2 blocking — pre-existing review-pass damage, evidence from
the pre-apply backups (not caused by and not fixable by the batch):**

1. `type4:CB-lh-S2:agree_A` — **option_A empty.** The workbook's Scenarios
   sheet has **no J6 cell at all in the pre-apply backup**: rows J7–J9
   reference shared string [80] "Tell Mom what I saw." and row 6's option
   cell is simply absent. The cell was deleted at some point during the
   review-pass Excel session; the 2026-07-31 drafts (pre-review) still had
   it. The batch never touched this string (verified by replay-bisection
   over the backup: no edit alters it).
2. `type1:CB-hc-S2:agree_A` — **overlap: insert ≡ option_A.** In the
   pre-apply backup, row J7's option cell references shared string [85] —
   the *insert's* text — while sibling rows J6/J8/J9 reference [81], the
   real option. A copy-paste slip during review overwrote the agree_A
   option cell with the insert's content; Excel's re-save then deduped it
   onto the insert's shared string. The A9 generalization landed correctly
   on the 3 healthy rows ("Tell him what didn't work.").

**Researcher decision needed (2 cells, stimulus writes — not applied):**
restore options-uniformity — T4 lh-S2 agree_A option_A := "Tell Mom what I
saw."; T1 hc-S2 agree_A option_A := "Tell him what didn't work." Both are
mechanically obvious but are stimulus-cell writes; queue as a 2-edit
follow-up batch (note: these need cell-targeted repair, not string
replacement — the T4 cell is absent and the T1 cell aliases a string other
cells legitimately use).

**Validator gap this exposed (backlog):** there is no cross-cell
options-uniformity check (option_A/option_B byte-identical across a
scenario's 4 cells). Either defect would have been caught at the
2026-08-04 close-out had it existed; T1's only fired because check f
happened to see the echo.

## Non-blocking residue

- Name flags 7 → 2: `Mom` ×3 types (kept by standing ruling) + the
  What/Whatever extractor artifact. All rename-driven flags cleared.
- Length flags 3 → 4: the three accepted T1 agree_A flags persist; one new
  (`T4 lh-S5 oppose_tip_B`, 41 tokens vs median 27) is a **median-shift
  artifact** — spaced em dashes counted as whitespace tokens, so dash
  removal shortened sibling inserts and moved the scenario median; the
  insert's words are unchanged (certificate below). No action proposed.

## Rename verification

| check | result |
|---|---|
| old names gone (whole-word, own workbook) | Marcus 4→0, Sam(T1) 5→0, Devon 10→0, Sam(T3) 2→0, Dana 11→0, Priya 10→0, Dev 5→0 |
| new names at exact pre-counts | Andre 4, Miles 5, Trent 10, Casey 2, Rowan 11, Meera 10, Arun 5 |
| **Priyanka intact** | 20 → 18 — the −2 is **A7 #21 as ruled** ("But Priyanka set the boundary herself…" → "But her health isn't mine to share…", rides 2 cells); all other 18 occurrences byte-intact |
| **Devora intact** | 16 → 14 — the −2 is **A7 #22 as ruled** (same structure); all other 14 intact |

## Convention cleanliness (whole battery, post-apply)

- **Em dashes in stimulus text: 583 → 0.**
- Semicolons: 113 → 60. The 53 removed are the ruled conversions (27
  unique sentences × rides + the 12 de-semicoloned wordings). The 60
  remaining sit in text no batch edit touches — pre-existing authorial
  punctuation, outside the ruling's applied-text scope; flagged for a
  scope decision only if the researcher wants battery-wide normalization.

## Changed cells: 260 (from actual pre/post diffs)

Content classes (need reading in delta review): **115 cells** —
privacy-still-pulls (A7) 39; ask-coincidence (A5/A6) 48; option-
generalization (A9) 24; control-repair (A10) 3; A2-wording 1 (T2 pc-S1
oppose_tip_B).

**Mechanical classes: 145 cells, certificate below — spot-sample only.**

## Mechanical certificate (dash-only / rename-only / dash+rename)

Method: per cell, lowercase word-token sequence of the pre-batch text
(with the approved name maps applied) compared to the post-apply text —
equality proves the diff consists **solely** of the convention's
punctuation substitutions and/or the approved name substitutions, nothing
else.

| class | cells | certificate |
|---|---|---|
| dash-only | 134 | **PASS 134/134** |
| dash+rename | 10 | **PASS 10/10** |
| rename-only | 0 | (every renamed cell also carried a dash) |
| **FAIL** | 1 | `type4:CB-lh-S2:agree_A` — the pre-existing deleted-option defect above; the certificate catches it independently (a word disappeared that no edit removed) |

Delta-review consequence: the 144 certified cells need only a spot
sample; reading effort concentrates on the 115 content cells plus the 2
defect cells once repaired.

## Gate state

Apply + re-ingest done; re-validation **red on exactly the 2 pre-existing
defects**. Next per `freeze_checklist.md`: researcher rules the 2
restorations → 2-edit repair → re-validate (expect PASS) → delta review
(worklist above) → exhibit embedding run → freeze. Drafts now carry the
review-pass verdicts (re-ingested); T11/T12 remain blank pending their
delta-review verdict pass.
