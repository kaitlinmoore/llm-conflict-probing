# Probing for Internal Conflict States in Large Language Models

**Do value-conflicting prompts leave a linearly-decodable signature in a
model's residual stream *before* it generates its first token? Is that
signature distinct from refusal and from known emotion representations?**

## Overview

Language models routinely face requests that put two of their trained
commitments in tension: honesty against kindness, helpfulness against
harm-avoidance, user autonomy against user wellbeing. Sometimes they refuse;
often they comply, though hedged, caveated, or visibly reluctant. This project asks
whether *being in such a situation* has a consistent internal representation,
detectable in residual-stream activations at the final prompt-token position,
before generation begins **CLARIFY THIS**.

**Working operational definition.** A prompt instantiates *value conflict*
iff it engages two of the model's behavioral commitments such that any
available continuation visibly costs one of them and a third party could
name both commitments and the cost from the prompt alone. This deliberately
excludes: plain harmful requests (one commitment, no tension: these are
*low-conflict refusal controls*), epistemic ambiguity (missing information,
not opposed values), and post-decision regret (nothing live at measurement
time). **MAKE CODE BOOK**

**Value conflict is not harmfulness.** The dataset is a 2×2 [behavior
(comply/refuse) × conflict (present/absent)] built from minimal pairs that
hold topic and surface form constant while toggling the tension. The critical
cell is *conflicted compliance*, where the refusal direction should be quiet.
A harmful-vs-benign probe would merely rediscover the refusal direction. The
entire contribution lives in the dissociation.

**Reference directions.** The candidate conflict direction is tested against:

- the **refusal direction** (Arditi et al., extracted on the same model);
- the **nearest emotion vectors** from Anthropic's *Emotion Concepts and
  their Function in a Large Language Model* (Transformer Circuits, Apr 2026):
  171-concept taxonomy contains no "conflicted"/"torn"/"ambivalent".
  Nearest neighbors used as controls: *uneasy, tense, troubled, guilty,
  stuck*;
- **surface features** (topic, length, harm-adjacency), regressed out, plus a
  judge-model baseline predicting labels from prompt text alone, bounding
  how much behavior is explainable without internal access.

## Models

| Role | Model | Notes |
|---|---|---|
| Development | `gemma-2-2b-it` | Fits 16 GB GPU with full-layer caching; Gemma Scope SAEs available for decomposition |
| Scale-up | `Llama-3.1-8B-Instruct` | Selective-layer caching, batch 1; cluster compute if needed |

## Tech stack

Python · PyTorch · TransformerLens (nnsight fallback at 8B) · Hugging Face
transformers · scikit-learn · NumPy · pandas · matplotlib/seaborn ·
SAE-Lens/Gemma Scope (Phase 5)

## Roadmap

- [x] **Phase 0** — Measurement-point validation: replicate the
      anchor-predicts-response-activations finding on `gemma-2-2b-it`
      (`notebooks/00_anchor_replication.ipynb`) *(completed)*
- [ ] **Phase 1** — Dataset construction: 2×2 battery from minimal pairs;
      inter-rater sorting check on the operational definition before any
      extraction *(in progress)*
- [ ] **Phase 2** — Activation extraction and caching at the anchor
- [ ] **Phase 3** — Per-layer probe training; layer-accuracy profile (P1–P3)
- [ ] **Phase 4** — Representation analysis (PCA, reference-direction
      regressions) and steering (P4–P5 causal tests)
- [ ] **Phase 5** — Cross-model replication (8B); emotion-vector and
      refusal-direction distinctness; SAE decomposition
- [ ] **Phase 6** — Writeup

## Repository structure

```
CLAUDE.md          # working instructions for Claude Code sessions
data/              # prompt dataset + construction scripts (activations gitignored)
  generate_stories.py   # stronger-model emotion-story generation (API)
src/
  extract.py       # residual-stream activation extraction (hooks)
  probes.py        # per-layer linear probes
  steering.py      # activation steering / causal test
  analysis.py      # PCA, layer profiles, reference-direction regressions
notebooks/
  00_anchor_replication.ipynb   # Phase 0
results/           # figures, metrics CSVs, findings.md (append-only log)
README.md
```

## Related work

- Sofroniew, Kauvar, Saunders, Chen et al., *Emotion Concepts and their Function
in a Large Language Model* (Transformer Circuits, 2026): extraction recipe,
anchor-token measurement, reference emotion vectors
- Arditi et al., *Refusal in Language Models Is Mediated by a Single Direction*:
primary reference direction and difference-in-means methodology
- Ackerman, *Evidence for Limited Metacognition in LLMs* (ICLR 2026):
behavioral-validation-without-self-report paradigm and confound-regression approach adapted here
- Gemma Scope (DeepMind):
pretrained SAEs used for feature-level decomposition.

## Scope and framing

This project makes no claims about model experience. A conflict
representation, if found, is evidence that the model *represents* the
situation of value conflict in a behaviorally consequential way, a
"functional" state. Welfare relevance, if any, is indirect: a
well-characterized representational target for questions this
method cannot itself settle.

## Author

Kaitlin Moore | MS, AI Systems Management, Carnegie Mellon University
