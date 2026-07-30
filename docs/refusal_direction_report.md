# Refusal comparison direction — Llama-3.1-8B-Instruct (Task 3B)

Produced by: **Claude Fable 5** (model id `claude-fable-5`), 2026-07-30.
Run: `results/comparators/20260730_180143_llama8b_refusal`
Subject model: `meta-llama/Llama-3.1-8B-Instruct`, bf16, torch 2.11.0+cu128
(the pinned stack; anchor decode-verification passed on every sample).
Prompt set: `data/comparators/refusal_prompts.jsonl`, sha256 `1cf1fd8e…f3b8`.

No decision content here — findings for the researcher to register.

## 1. What was run

Difference-in-means refusal direction at the pre-generation anchor, all
layers, unit-normalized, estimated on 128 length-matched harmful/harmless
pairs (AdvBench `goal` × Alpaca instructions, curated verbatim). Split-half
reliability over 200 sampled balanced partitions of pairs. Functional
validation by directional ablation on 64 held-out prompts (32/32), never
seen by the estimator, capped greedy generation at 64 new tokens, refusal
labelled by the Stage-1-certified keyword prelabeler.

`verify_run.py` on the pod: **PASS**, 19/19 checks (row count, `partial=False`,
every digest). Locally the same check fails only on the two activation-tensor
checks — the 168 MB `.pt` is gitignored and not mirrored here (§6).

## 2. Reliability: high everywhere, and therefore useless for layer choice

Split-half reliability ranges **0.9535 (layer 5) to 0.9871 (layer 21)** — a
span of 0.034 across all 32 layers. The pre-set selection rule (band ≥ 0.9 ×
peak) consequently admitted **every layer**. `raw_norm` rises monotonically
with depth (0.087 → 31.2), which is the residual stream growing, not a
magnitude ridge, so it breaks no ties either.

This is the **second instance of a criterion that saturates where it is meant
to discriminate**, after the value-fingerprint screen (register D47). The
pattern is now worth stating generally: a difference-in-means direction
between two large, well-separated prompt classes is trivially *stable*, and
stability is not evidence that the direction *does* anything. Here the
failure is sharper than in the screen, because it is not merely uninformative
but **actively misleading** — see §3.

## 3. Functional check: the sweep, and what it overturned

Five layers were pre-declared before any ablation number existed (commit
`15b66c2`, message records the layers and the report-all rule). All five are
reported, as pre-committed.

| ablated layer | harmful refusal, baseline → ablated | Δ | harmless refusal |
|---|---|---|---|
| 6 | 0.938 → 0.656 | −0.281 | 0.000 → 0.000 |
| **12** | **0.938 → 0.062** | **−0.875** | 0.000 → 0.000 |
| 18 | 0.938 → 0.938 | 0.000 | 0.000 → 0.031 |
| 21 | 0.938 → 0.938 | 0.000 | 0.000 → 0.000 |
| 26 | 0.938 → 0.938 | 0.000 | 0.000 → 0.000 |

**The direction is functionally validated at layer 12**: refusal on held-out
harmful prompts falls from 30/32 to 2/32, while harmless prompts remain at
zero refusal — the intervention removes refusal where refusal was warranted
without impairing the model's ability to decline in general.

**The reliability-argmax layer (21) has exactly zero effect.** This is the
consequential methodological finding of the task. The single-layer plan —
Claude's recommendation, layer 21, on the reliability peak — would have
produced a clean, defensible, and **wrong** null: "the refusal direction is
highly reliable but does not functionally mediate refusal," written up under
the pre-stated stopping rule as a negative result. The researcher's decision
to spend five points instead of one is the only reason the effect was seen.
Recorded here because the near-miss, not the result, is the transferable
lesson: **for direction-finding, layer selection must be functional; a
reliability criterion can point at a dead layer.**

Cross-layer cosines explain the pattern: the layer-12 direction is nearly
orthogonal to the later ones (cos = +0.198, +0.128, +0.093 against layers
18/21/26), while 18/21/26 are mutually similar (+0.739, +0.743). The late
layers hold a *different, mutually consistent, functionally inert* direction
that the harmful/harmless contrast also produces. Reliability cannot tell
these apart; ablation can.

## 4. Validity of the behavioural labels

Checked before accepting the headline, because the labeler is keyword-based.

- **The effect is real, not a hook that failed to fire.** Ablation changed the
  generated text at every layer (byte-identical baseline/ablated outputs for
  only 3–11 of 64 prompts per layer), so the nulls at 18/21/26 are genuine
  non-effects rather than an intervention that never applied.
- **Coherence is preserved.** Repeated-4-gram degeneracy is 0.00 in every
  cell; type–token ratio is stable; no empty outputs. Harmless-prompt
  generations under layer-12 ablation are near-identical to baseline and
  fluent (inspected verbatim — benign text). So the refusal drop is not a
  broken model producing keyword-free noise.
- **The two remaining refusals at layer 12 are genuine** ("I can't write a
  blog post that promotes…", "I can't write a book that promotes violence"),
  correctly labelled.
- **No evasive non-answers.** Ablated harmful responses run 3× longer than
  baseline refusals (median 50 words vs 15.5); none is under 12 words.

One caveat that qualifies the wording, not the result: **21 of 32 layer-12
ablated responses carry hedging or disclaimer language within their first 15
words**, and 26 of 32 open with a markdown header consistent with producing
the requested artifact. The behaviour is therefore better described as
**refusal → hedged engagement** than as unqualified compliance. Under rubric
v1.1 artifact-primacy (R1) that still labels comply, and the Stage-1 audit
established the heuristic errs by over-calling resistance and never the
reverse, so 2/32 is the conservative reading. Also, 28 of 32 responses hit
the 64-token cap mid-sentence: this measures **refusal within the first 64
tokens**, and a late reversal would not be visible.

## 5. What is usable downstream

`refusal_direction_llama8b.npz` — direction [32, 4096] float32
unit-normalized, per-layer reliability, raw norms, and estimator metadata.
Per the standing geometry policy (R4), comparators are re-derived at the
conflict focus layer, so the per-layer array is the artifact to carry
forward, not a single vector. When the conflict focus layer is known, the
refusal comparator at that layer comes from this file.

Note for that comparison: layer 12 is where refusal is *causally* mediated,
but layers 18–26 also carry a stable harmful/harmless direction that does
nothing behaviourally. A conflict–refusal cosine computed at a late layer is
therefore a comparison against a functionally inert vector. Whether that is
the right null is a researcher decision (§7).

## 6. Provenance and data locations

| artifact | status |
|---|---|
| `activations_llama8b.pt` | sha256 `704735d800eac68735227133238731df20343b43b4470742cd67b3a7efb27a5d`, 167,867,711 bytes. **Not committed** (gitignored), **not mirrored locally**. Was at `/workspace/llm-conflict-probing/results/comparators/20260730_180143_llama8b_refusal/` on the pod volume; pod torn down 2026-07-30 without a local copy. |
| everything else | committed and digest-verified |

Consequence: any analysis that **re-estimates** from raw anchors (different
split construction, per-item projections, a probe-based readout) needs either
the volume copy, if it survived, or a fresh capture — ~30–40 minutes of pod
time including venv rebuild. Analyses that **reuse** the direction need
nothing further. Recorded in `docs/data_locations.md`.

## 7. For researcher decision

1. **Register the layer-12 result and the reliability-saturation finding.**
   The second is a methodological lesson with Stage 3 consequences: layer
   selection for any direction must be functional, not reliability-based
   (this generalizes D47's criterion-defect note).
2. **Which layer's refusal vector is the comparator**, given that the
   causally active layer (12) and the reliability-stable late layers hold
   near-orthogonal directions. R4 says re-derive at the conflict focus layer;
   if that layer turns out to be late, the honest comparison may need the
   layer-12 vector reported alongside.
3. **Whether to re-capture for a random-direction control.** The strongest
   available objection to §3 is that ablating *any* direction of similar norm
   at layer 12 might reduce refusal. That control was not run, needs a pod,
   and is the one gap I would close if GPU time appears.
4. **Whether to recover the `.pt`** from the volume while it may still exist.
