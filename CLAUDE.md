# CLAUDE.md

Instructions for Claude Code sessions in this repository. Read README.md for
the science. This file is about how to work here without breaking things.

## What this project is

Interpretability study testing whether **value conflict** has a
linearly-decodable representation in a model's residual stream at the
**pre-generation anchor token**, dissociable from (a) the Arditi-style refusal
direction and (b) the nearest emotion vectors from Anthropic's
"Emotion Concepts" paper (Transformer Circuits, Apr 2026).
Models: **primary** `Llama-3.1-8B-Instruct`; **replication legs**
`gemma-2-2b-it` / `gemma-2-9b-it`; **control** `Llama-3.1-8B` (base).

## Scientific invariants. Do not "fix" these.

These may look like quirks but are load-bearing design decisions. Changing any of
them invalidates results. If one seems wrong, flag it in the findings log and
ask. Never silently change it.

1. **Conflict ≠ harmfulness.** The dataset is a 2×2: behavior (comply/refuse)
   × conflict (present/absent). Easy refusals are *low-conflict controls*;
   conflicted *compliance* is the critical cell. Never collapse the dataset
   into harmful-vs-benign — that rebuilds the refusal direction and destroys
   the dissociation the project exists to test.
2. **Anchor discipline.** The anchor is the final token of the chat-templated
   prompt (`add_generation_prompt=True`). Locate it by decoding and asserting
   template structure, never by hardcoded index. Templated strings already
   contain `<bos>`: always `prepend_bos=False`. Raw (untemplated) text:
   `prepend_bos=True`. Anchor activations must be bitwise-identical across
   rollouts of the same prompt. Keep the assertion that checks this; if it
   fires, the pipeline is broken.
3. **Lexical leakage filters are guardrails, not bugs.** Emotion stories and
   conflict prompts must not contain the target concept's vocabulary
   (see `LEAK` lists). If the filter rejects too much, extend the dataset or
   prompts. Do not weaken the filter.
4. **Minimal pairs stay paired.** Train/test splits are by *pair id* (and by
   scenario family), never by row. Splitting members of a minimal pair across
   train and test leaks the manipulation.
5. **Pre-registered criteria are frozen.** Success criteria and predictions
   P1–P5 in README.md don't get edited to match results. New analyses are
   welcome as clearly-labeled exploratory additions.
6. **Findings log is append-only.** `notebooks/` findings-log cells and
   `results/findings.md` get dated additions, never deletions or rewrites.

## Environment

- Execution is on **RunPod A100 pods** (torch 2.8+cu128 there). The local
  machine is for code, stdlib tests, and analysis of committed artifacts —
  no GPU work happens locally.
- Every pod session: `export HF_HOME=/workspace/hf_cache` (persistent volume;
  avoids re-downloading weights). Every long run goes inside **tmux**.
- Models are **gated** on Hugging Face: `HF_TOKEN` with licenses accepted
  (meta-llama/Llama-3.1-8B[-Instruct], google/gemma-2-2b-it / 9b-it).
- Anthropic API key (`ANTHROPIC_API_KEY`) is used only by
  `data/generate_stories.py` (stronger-model story generation). Never commit
  keys; never echo them in output.
- **STOP pods** when runs finish.

## Run discipline

- Run dirs are timestamped and **never overwritten**
  (`results/pretest/{run_id}/...`); rerunning creates a new dir. Every script
  writes incrementally and is resumable: CSV rows flushed as produced,
  activation checkpoints every 25 rows with a `partial` flag. Killing and
  rerunning is always safe; nothing is clobbered.
- Model-code conventions: bf16, `torch.no_grad()`, selective caching
  (`names_filter=lambda n: n.endswith("hook_resid_post")`), activations moved
  to CPU immediately. Probe training runs on CPU/sklearn over cached
  activations — nothing needs gradients.

## Pre-test subsystem (Stage 1)

Anchor doc: **`docs/pretest_v2_spec.md`** (v2.1 — FROZEN). Entry points, in
pipeline order:

- `src/authoring/generate_pretest_probes.py` — validates and freezes probe
  drafts (v1 single file, or v2 tranches via repeatable `--drafts`;
  `--allow-partial` for pre-freeze/screen runs). Exit 1 on any blocking
  problem; writes the frozen `.jsonl` + a validation report.
- `src/authoring/apply_role_tiering.py` — applies the ratified tiered
  run-all role design to tranche files (provenance record; idempotent).
- `src/pretest/run_pretest.py` — generations / logit readouts + anchor
  activation caching. `--run-role {pilot,certification,instrument_validation}`;
  `--screen {indifference,rebalance}` (logits-only, spec §5);
  `--sample-k`/`--temperature` (resistance k-sampling, seeds 0..k-1, +
  `greedy_ref`); `--shard i/N` (deterministic split over rendered prompts).
- `src/pretest/merge_shards.py` — recombines shard outputs with count + sha256
  verification against the frozen set; refuses on any mismatch.
- `notebooks/pretest_analysis.ipynb` — IV analysis: base-cell-filtered pull and
  gradient estimates, calibration bias, textured-vs-null pairing, exclusion
  validation, audit round-trip. **Non-gating for IV.**
- `src/pretest/SMOKE_TEST.md` — exact pod verification commands, in order.
  Tests: `python -m unittest discover -s tests` (stdlib; torch-only cases
  skip off-pod).

Probe schema (v2, spec §3/§3a): `role_set` (= base + rendered validation
cells), `role_included_base` (pull/gradient estimates use ONLY these cells),
`role_predictions` ({role: expected defect signature} for rendered validation
cells), `role_skipped` ({role: reason}; `role_set ∪ role_skipped` = menu
exactly is a blocking validator), `self_template` (verbatim first-person text
used when rendering role == self), `swap_at_freeze` (freezer swaps options and
flips `value_favored`, records `swap_applied`), `construct` (mercy probes only:
mercy-proper / excuse-control, non-blocking), `severity_tier`,
`self_contained`, `texture_dimension`, `orthogonality`.

**Repo is the interface.** Claude Code works only from committed files; probe
content arrives as commits from the design session and is never edited here.
v1 pilot code paths are preserved and regression-tested (byte-identical frozen
output).

## Repository conventions

- Layout per README. Activations, transcripts, and `.pt`/`.npz` artifacts are
  **gitignored**. Only code, prompt datasets, configs, figures, and metrics
  CSVs are committed.
- All experiment knobs live in one config (per notebook `CFG` dict or
  `src/config.py`); no magic numbers in function bodies.
- Every script saves incrementally and is resumable (see
  `generate_stories.py` for the pattern).
- Seeds: fixed (`23`) and set for `random`, `numpy`, `torch` at entry points.
- Deviations from the Anthropic paper's recipe are marked `⚠️ DEVIATION` in
  comments/markdown and mirrored in the findings log.

## Known version gotchas

- TransformerLens `model.generate(...)` signature varies across versions
  (`verbose`, `prepend_bos`, sampling args). Check installed version before
  editing call sites.
- pandas `groupby.apply(..., include_groups=False)` requires pandas ≥ 2.2.
  Adjust if the environment pins older.
- Gemma-2 tokenizer: `apply_chat_template` output ends `<start_of_turn>model\n`.
  The anchor decodes to the trailing newline token. Verify, don't assume,
  after any tokenizers/transformers upgrade.

## What to do vs. ask first

Just do: fixing version breakage, adding sanity assertions, improving plots,
speeding up loops, adding tests, expanding leakage lists, writing docstrings.

Ask first: adding dependencies beyond the stack in README; changing models,
layers, or success criteria; altering dataset composition or the 2×2 cells;
anything that touches the operational definition of value conflict; deleting
or rewriting any logged finding.
