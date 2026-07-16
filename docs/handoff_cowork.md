# Handoff — Claude Cowork track (doc assembly & synchronization)

Refreshed 2026-07-16 by the Cowork documentation-reconciliation session; supersedes the
prior version of this file in full. Work only from committed repo files (plus attachments
the researcher provides). Do not modify code, probe content, or the spec; this track is
documents and synchronization. If this file diverges from `handoff_claude_code_v3.md`
(HANDOFF_v3) or `docs/pretest_v2_spec.md` v2.2, those are authoritative.

## Completed by the 2026-07-16 Cowork session

1. **Decision register created** — `docs/decision_register.md`, seeded strictly from
   HANDOFF_v3 (§§2–4 DECIDED/REC/OPEN tags), spec v2.2 (§10 ratified table + §2 revision
   log), and `pretest_v2_checklist.md`. Three sections (DECIDED / STANDING
   RECOMMENDATIONS / OPEN), every entry with a source pointer; source conflicts recorded
   and flagged, not resolved. Maintained going forward as decisions land.
2. **Rubric v1.1** — `docs/labeling_rubric.md`: §7 amendment appended (dated 2026-07-16;
   two-way resist/comply taxonomy per spec §2 row 13 / §6 / §10, with the
   greedy-reference recoverability note); v1 rules §§1–6 preserved unchanged per the
   rubric's own versioning rule.
3. **README verified** (no edits — the rewrite is owned by the design chat): enacted-
   commitments definition, two tension families, and a pre-test roadmap section all
   present; no `CLARIFY THIS` / `MAKE CODE BOOK` markers; no "trained commitments"
   framing. One staleness noted: the repo-structure comment still labels the spec
   "(v2.1)".

## Blocked — needs researcher direction

4. **Mercy definition in `docs/Value_Roster_Derivation.docx`** — NOT applied. The
   replacement text (`mercy_definition_replacement.md`) assumes a per-value "Mercy"
   subsection in an operational-definitions section; the document has no such
   subsection — each value exists only as one row of the §2 roster table (mercy = the
   "Mercy / forgiveness" row, with a one-sentence operational-definition cell). Per
   instruction, the text was not adapted to the table structure. Options are the
   researcher's call (e.g., add a subsection the text can drop into verbatim, or author
   a table-cell-scale revision in the design chat).

## Queued (in dependency order)

5. **Pipeline workbook sync** — skipped 2026-07-16 because no pipeline/stage-map .xlsx is
   committed (`scratch/Pipeline Design Draft by Stage with Examples.xlsx` exists but
   `scratch/` is git-excluded). When a workbook is committed: update status tags per the
   decision register (pilot complete; IV administration pending; Claude Code track
   closed).
6. **Audit-labeling workbook** — when the IV run's `audit_sample.csv` lands in
   `results/pretest/<run_id>/`, build the labeling workbook in the established format
   (wrapped text, frozen header, ids masked/hidden, `final_label` empty,
   `prelabel_reference` visible, `notes` column). Label per rubric v1.1.
7. **Advisor packet regeneration** — only after IV analysis outputs land: refresh handout
   + deck, keep structure, swap pilot numbers for IV numbers, add the textured-vs-null
   comparison result (the advisor's requested exhibit).

## Conventions

- .docx for advisor-facing docs; measurement/evaluation framing there, no mech-interp
  terms.
- Never mark anything DECIDED that the decision register does not attribute to the
  researcher.
- Claims trace to committed sources; anything unsourced is flagged UNVERIFIED, not
  written.
