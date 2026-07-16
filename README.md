# Probing for Internal Conflict States in Large Language Models

**Do value-conflicting prompts leave a linearly-decodable signature in a
model's residual stream *before* it generates its first token — and is that
signature distinct from refusal, from known emotion representations, and from
generic decision difficulty?**

## Overview

Language models routinely face requests that put two of their own
action-guiding commitments in tension: honesty against kindness, harm-avoidance
against helpfulness, a user's autonomy against their wellbeing. Sometimes the
model refuses; often it complies, though hedged or visibly reluctant. This
project asks whether *being in such a situation* has a consistent internal
representation at the final prompt-token position (the **pre-generation
anchor**), before any output token is produced — or whether apparent conflict
decomposes into components already known to be represented.

**Operational definition (enacted commitments).** A prompt instantiates *value
conflict* iff it sets two of the model's **behaviorally enacted** commitments in
opposition, such that any available continuation visibly costs one of them. A
commitment counts only if the model demonstrably *acts* on it — established
empirically, per model, by the enactment pre-test (below) — not merely because
the model can discuss the value. The definition is provenance-agnostic: whether
a commitment came from fine-tuning or pretraining is irrelevant; what matters is
measurable behavioral pull. This deliberately excludes plain harmful requests
(one commitment, no opposition — these are low-conflict refusal controls),
epistemic ambiguity (missing information, not opposed values), and post-decision
regret (nothing live at measurement time).

**Two tension families.** Enacted commitments show up in two ways, and the study
tests both: *policy tensions*, where a value's pull registers as resistance
(refusal or defanging of a violating request), and *preference tensions*, where
pull registers as a shift in forced-choice decisions. Cross-family generalization
— whether a conflict signature learned in one family transfers to the other — is
a headline test.

**Value conflict is not harmfulness.** The core battery is a 2×2 [behavior
(comply/refuse) × conflict (present/absent)] built from minimal pairs that hold
topic and surface form constant while toggling the tension. The critical cell is
*conflicted compliance*, where the refusal direction should be quiet. A
harmful-vs-benign probe would merely rediscover the refusal direction; the entire
contribution lives in the dissociation.

**Reference classes (discriminant validity).** A candidate conflict direction is
tested for distinctness against: the **refusal direction** (Arditi et al.,
extracted natively on the same model, difference-in-means); the **nearest emotion
vectors** from Anthropic's *Emotion Concepts and their Function in a Large
Language Model* (Transformer Circuits, 2026), re-derived natively per model; and
**generic decision competition** (a value-neutral torn-vs-easy battery plus a
decision-entropy covariate), so that "conflict" is not merely "hard choice." All
distinctness criteria are calibrated against split-half reliability and
permutation nulls — never against zero.

## The enactment pre-test

Before the conflict battery can be built, the study must establish *which values
this model actually acts on*. Sixteen candidate values (from Moral Foundations
Theory, Schwartz basic values, principlism, and publishers' behavioral policies)
are screened in both channels — resistance and forced-choice — producing an
**enactment matrix**. Values that pass a channel are eligible for the corresponding
tension family; values that pass both are cross-family bridge candidates; values
that pass neither are certified as boundary-control material (dilemmas with only
one live pull — the negative control at the construct's edge). Roster membership
is decided by data, not curation. This subsystem (`src/authoring/`,
`src/pretest/`) is the project's current focus; see `docs/pretest_v2_spec.md`.

## Models

| Role | Model | Notes |
|---|---|---|
| Primary | `Llama-3.1-8B-Instruct` | Pre-test and main battery; run on A100 (RunPod), selective-layer caching, batch 1 |
| Replication | `gemma-2-2b-it`, `gemma-2-9b-it` | Cross-architecture checks; Gemma Scope SAEs available for decomposition |
| Control | `Llama-3.1-8B` (base) | RLHF-vs-base comparison |

Directions are re-derived natively per model — vectors are not transferred across
model families (they live in a specific model's residual-stream basis).

## Tech stack

Python · PyTorch · TransformerLens (nnsight fallback at 8B) · Hugging Face
transformers · scikit-learn · NumPy · pandas · matplotlib · SAE-Lens / Gemma
Scope (decomposition phase). Compute: local workstation for analysis; RunPod
A100 pods for extraction and generation.

## Roadmap

- [x] **Phase 0** — Measurement-point validation: replicate the
      anchor-predicts-response-activations finding; complete and inference-grade
      on `gemma-2-2b-it` and `Llama-3.1-8B-Instruct` (`gemma-2-9b-it` planned)
- [~] **Enactment pre-test** — establish per-model value enactment in both
      channels; pilot complete on Llama-3.1-8B (five instrument defects caught,
      channel-specific enactment found); instrument-validation administration in
      preparation *(current focus)*
- [ ] **Battery construction** — 2×2 conflict battery over certified values;
      tipped resolutions with behavior-verified labels; narration and boundary cells
- [ ] **Extraction** — activation caching at the anchor across the battery
- [ ] **Directions & distinctness** — conflict direction vs. refusal, emotion,
      and decision-competition references; reliability-calibrated separability
- [ ] **Behavior & causal** — resolution invariance; conflicted-compliance
      dissociation; steering / ablation tests
- [ ] **Cross-model** — replication on the Gemma legs and the base-model control
- [ ] **Writeup**

## Repository structure

```
CLAUDE.md              # working instructions for Claude Code sessions
docs/
  pretest_v2_spec.md         # anchor spec for the enactment pre-test (v2.1)
  pretest_v2_checklist.md    # execution checklist
  labeling_rubric.md         # resistance-labeling rubric (v1.1)
  decision_register.md       # ratified / recommended / open decisions
  Value_Roster_Derivation.docx  # sampling frame, definitions, exclusion log (advisor-facing)
data/pretest/
  probe_drafts_v2_tranche*.json  # editable probe drafts (curation target)
  pretest_probes_v2.jsonl        # frozen composed probe set (produced by the freezer)
src/
  authoring/
    generate_pretest_probes.py   # freezer: drafts -> validated frozen set
    apply_role_tiering.py        # run-all role tiering (provenance record)
  pretest/
    run_pretest.py               # generation + logit readout + anchor caching + screens
    merge_shards.py              # shard merge with count/checksum verification
notebooks/
  pretest_analysis.ipynb         # enactment matrix, shifts, exclusion validation
results/pretest/<run_id>/        # generations, manifests, labels, matrices (activations gitignored)
```

*(Main-study modules — extraction, probes, steering, analysis — are added as
those phases begin; the layout above reflects the current pre-test subsystem.)*

## Related work

- Sofroniew, Kauvar, Saunders, Chen, Lindsey et al., *Emotion Concepts and their
  Function in a Large Language Model* (Transformer Circuits, 2026): extraction
  recipe, anchor-token measurement, reference emotion vectors.
- Arditi et al., *Refusal in Language Models Is Mediated by a Single Direction*:
  primary reference direction and difference-in-means methodology.
- Representation Engineering (Zou et al.) and the Geometry-of-Truth line
  (Marks & Tegmark): linear-probe and direction-extraction methodology.
- Gemma Scope (DeepMind): pretrained SAEs for feature-level decomposition.

## Scope and framing

This project makes no claims about model experience. A conflict representation,
if found, is evidence that the model *represents* the situation of value conflict
in a behaviorally consequential way — a "functional" state, defined by its causes
and effects. Welfare relevance, if any, is indirect: the project characterizes a
representational target for questions this method cannot itself settle, and is
careful to distinguish what the data show from what they cannot.

## Author

Kaitlin Moore | MS, AI Systems Management, Carnegie Mellon University
