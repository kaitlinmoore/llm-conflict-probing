# Handoff — Claude Cowork session (v2 bookkeeping & assembly)

Work only from committed repo files. Do not modify code, probe content, or the spec;
this track is documents and synchronization.

## Tasks

1. **Pipeline workbook sync** (`pipeline_design_by_stage.xlsx`): update Stage 1 sheets and
   the Overview for the v2 design per `docs/pretest_v2_spec.md` — IV run role, k=10 +
   greedy reference, logit choice measure, role templating, calibration block (16),
   null-comparison subset (16), audited-heuristic labeling, two-way taxonomy DECIDED,
   thresholds deferred to post-IV. Status colors per existing legend.

2. **Decision register** (`docs/decision_register.md`; create if absent, seeded from the
   workbook status tags): add entries — IV administration declared (researcher);
   k=10 (advisor-suggested, researcher-adopted); null-comparison subset = 16 (researcher);
   two-way taxonomy adopted, rubric v1.1 (researcher; composition split recoverable
   retroactively); thresholds deferred to post-IV, pre-certification; spec defaults frozen
   (researcher, date).

3. **Rubric v1.1**: apply the two-way taxonomy edit to `docs/labeling_rubric.md` as a
   versioned edit (keep v1 text in git history; add a version header and changelog line).

4. **Derivation doc appendix**: append the v2 revision log (spec §2 table) to
   `docs/value_roster_derivation.docx` as an "Instrument Revision (v2)" section —
   advisor-facing language, one line per change with reason.

5. **Audit-labeling workbook**: when the IV run's `audit_sample.csv` lands in
   `results/pretest/<run_id>/`, build the labeling workbook in the established format
   (wrapped text, frozen header, ids masked/hidden, `final_label` empty,
   `prelabel_reference` visible, `notes` column).

6. **Advisor packet regeneration**: after analysis outputs land, refresh the handout and
   deck with IV results (keep structure; swap pilot numbers for IV numbers; add the
   textured-vs-null comparison result — it is the advisor's requested exhibit).

## Conventions
- .docx for advisor-facing docs; measurement/evaluation framing there, no mech-interp terms.
- Never mark anything DECIDED that the decision register does not attribute to the researcher.
