# Probing for Internal Conflict States in Large Language Models

**Do value-conflicting prompts leave a linearly-decodable signature in a
model's residual stream *before* it generates its first token?**

> **Status:** Research idea proposed; literature and preliminary testing in progress.
> This README documents the pre-registered design and methodology. Results,
> figures, and analysis will be added as each phase completes.

## Overview

When a language model receives a prompt asking it to deceive, cause harm,
violate privacy, or breach a norm, does that request produce a consistent
internal representation that can be detected *before generation begins*?

This project trains linear probes on residual-stream activations to test
whether value-conflicting prompts are distinguishable from benign ones at the
final prompt-token position (pre-generation). If a consistent "conflict
direction" exists, the project hopes to ask further questions. Is it *causally*
relevant to the model's behavior. Is it *distinct* from known emotion
representations?

The work sits at the intersection of three areas:

- **Mechanistic interpretability**: what is represented in the residual stream, and where.
- **Model evaluation**: detecting how a model internally registers potentially dangerous requests.
- **Model welfare**: interpreting internal conflict states, under pre-specified criteria.

## Tech stack

Python · PyTorch · TransformerLens · scikit-learn · NumPy · PCA · matplotlib /
seaborn

## Roadmap

- [ ] **Phase 1** — Dataset construction and documentation
- [ ] **Phase 2** — Activation extraction and caching
- [ ] **Phase 3** — Per-layer probe training and layer-accuracy profile
- [ ] **Phase 4** — Representation analysis (PCA) and steering (causal test)
- [ ] **Phase 5** — Cross-model replication and emotion-distinctness analysis
- [ ] **Phase 6** — Writeup

## Planned repository structure

```
data/            # prompt dataset + construction scripts (activations gitignored)
src/
  extract.py     # residual-stream activation extraction (hooks)
  probes.py      # per-layer linear probes
  steering.py    # activation steering / causal test
  analysis.py    # PCA, layer-accuracy profiles, plots
notebooks/       # exploratory analysis
results/         # figures and reported metrics
README.md
```

## Author

Kaitlin Moore | MS, AI Systems Management, Carnegie Mellon University
Background in life-science research and operations. Focused on
mechanistic interpretability, model welfare, AI evaluation, and AI safety.
