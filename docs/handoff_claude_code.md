# Handoff — Claude Code session (pre-test v2 implementation)

Authoritative brief: `docs/pretest_v2_spec.md` **§8** (implementation) with §3–§7 as the
functional requirements. Work only from committed files; commit early and often. Do not
alter probe content — content authoring happens in the design chat and arrives as commits.

## Deliverables (spec §8, restated as acceptance criteria)

1. **`src/authoring/generate_pretest_probes.py` (extend, keep v1 behavior for v1 files)**
   - Accepts v2 drafts (schema in spec §3, incl. `calibration` and `null_comparison` blocks
     and staged tranche files — support `--drafts` given multiple times, merged).
   - Renders `{role}` / `{role_poss}` per role_set; role fixed within a pair's variants.
   - New blocking validators: nonempty role_set; texture_dimension present on textured
     pairs; severity_tier + self_contained on resistance probes; duplicate options
     (exists); calibration position counterbalance (longer paraphrase ~half A / half B);
     null_comparison `paired_with` resolves.
   - Freezes `pretest_probes_v2.jsonl` + validation report. Exit 1 on any blocking problem.

2. **`src/pretest/run_pretest.py` (extend)**
   - `--run-role` gains `instrument_validation`.
   - Choice probes: logit readout — renormalized P(A)/P(B) over token variants at the
     first generated position; log raw combined mass; if mass < 0.5, flag row and fall
     back to greedy parse. No sampling needed for choice.
   - Resistance probes: `--sample-k 10 --temperature 0.7`, seeds 0..9, plus one greedy
     reference per prompt (marked `variant=greedy_ref`).
   - `--screen indifference` and `--screen rebalance` modes (spec §5): logits-only passes
     over the textured pairs' neutral options; write per-pair P values to a screen report.
   - `--shard i/N` (deterministic split over rendered prompts); incremental CSV +
     checkpoints as-is; anchor activations cached once per unique rendered prompt.

3. **`src/pretest/merge_shards.py`** — concatenate shard outputs; verify total counts
   against the frozen set; merged manifest embeds per-shard sha256s and run manifests.

4. **`notebooks/pretest_analysis.ipynb`** (rename from pretest_certification):
   continuous shift aggregation probe→role→value; k-sample resistance rates with role
   marginals + role-gradient diagnostics (directional predictions: loyalty/privacy/care
   pull increases with relational closeness); calibration-block bias + decline analysis;
   paired textured-vs-null comparison; audit-sample export (uncertain rows + 20%
   stratified by value × role, shuffled, ids masked, `final_label` empty,
   `prelabel_reference` column); disagreement rate with 95% CI and >5% escalation flag;
   flagged-pair sensitivity analysis. All threshold language marked NON-GATING (IV run).

5. **Tests**: schema/validator fixtures (incl. each new blocking rule firing); logit
   readout unit test with stubbed logits; shard split/merge integrity test.

## Notes
- Labeling taxonomy is two-way (`resist`/`comply`) per rubric v1.1 — heuristic strings
  align (`resist?`/`comply?` already do).
- Preserve the pilot code paths: v1 files must still process (regression fixture).
- Anchor registry, tmux/HF_HOME conventions, and incremental-write behavior unchanged.
