# CLAUDE.md

Instructions for Claude Code sessions in this repository. Read README.md for
the science. This file is about how to work here without breaking things.

## What this project is

Interpretability study testing whether **value conflict** has a
linearly-decodable representation in a model's residual stream at the
**pre-generation anchor token**, dissociable from (a) the Arditi-style refusal
direction and (b) the nearest emotion vectors from Anthropic's
"Emotion Concepts" paper (Transformer Circuits, Apr 2026).
Dev model: `gemma-2-2b-it`. Scale-up target: `Llama-3.1-8B-Instruct`.

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

- Hardware: single RTX 5080 laptop GPU (**16 GB VRAM**, Blackwell), 64 GB RAM.
  Blackwell needs torch built for cu128+; "no kernel image" errors mean a
  stale torch build, not a code bug.
- Gemma is **gated** on Hugging Face: requires `HF_TOKEN` with license
  accepted at huggingface.co/google/gemma-2-2b-it.
- Anthropic API key (`ANTHROPIC_API_KEY`) is used only by
  `data/generate_stories.py` (stronger-model story generation). Never commit
  keys; never echo them in output.

## Memory rules (16 GB)

- bf16 everywhere; `torch.set_grad_enabled(False)` globally. Nothing here
  needs gradients except probe training, which runs on CPU/sklearn over
  cached activations.
- Always cache selectively: `names_filter=lambda n: n.endswith("hook_resid_post")`
  (or a single layer). Never bare `run_with_cache` on the 8B model.
- 8B workflow: Generate with HF `transformers` (or quantized); save
  transcripts; then a single TransformerLens/nnsight forward pass per
  transcript for activations. Batch size 1. Layer subset (every other layer).
- `del cache; torch.cuda.empty_cache()` after each transcript. Move cached
  activations to CPU immediately (64 GB RAM is the working store).

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
