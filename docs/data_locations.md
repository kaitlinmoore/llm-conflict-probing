# Data locations — large run artifacts

Produced by: Claude Fable 5 (model id `claude-fable-5`), 2026-07-30 session 1
(researcher-directed entry). Large binary artifacts (activation tensors) are
gitignored; this file records where the bytes live so digests can always be
re-verified against the committed run manifests.

## Merged IV run — `20260717_204822_llama8b_instrument_validation_merged`

Canonical run record: `results/pretest/20260717_204822_llama8b_instrument_validation_merged/`
(committed text artifacts + `manifest.json`).

`activations_llama8b.pt` — 495,223,455 bytes, sha256
`7a36ab5e217e04ca4ebcc679c07ba301102711016973da7e424031d2cb1aad02`
(recorded in the run manifest's `output_digests`):

| copy | path | notes |
|---|---|---|
| MooseFS volume (pod) | `/workspace/llm-conflict-probing/results/pretest/20260717_204822_llama8b_instrument_validation_merged/` | origin of record for the tensor |
| local mirror (this machine) | `activations/20260717_204822_llama8b_instrument_validation_merged/` (repo-root-relative; directory is gitignored) | dropped 2026-07-30 to run the value-fingerprint screen locally |

Join key for the tensor's `activations` dict: `prompt_key`, via the run's
`prompt_join.csv`. Consumers must verify the sha256 against the manifest
before use (`src/analysis/fingerprint_screen.py` does this and refuses
`partial=True` checkpoints).

## Refusal comparator run — `20260730_180143_llama8b_refusal`

Canonical run record: `results/comparators/20260730_180143_llama8b_refusal/`
(committed: `prompts.csv`, `manifest.json`, `refusal_direction_llama8b.npz`,
reliability CSV, five ablation CSV/JSON pairs). `verify_run.py` PASS 19/19
on the pod.

`activations_llama8b.pt` — 167,867,711 bytes, sha256
`704735d800eac68735227133238731df20343b43b4470742cd67b3a7efb27a5d`:

| copy | path | notes |
|---|---|---|
| MooseFS volume (pod) | `/workspace/llm-conflict-probing/results/comparators/20260730_180143_llama8b_refusal/` | **status uncertain** — pod torn down 2026-07-30; survives only if the volume was retained |
| local mirror | **none** | not downloaded before teardown |

The committed `.npz` is canonical for analysis and is sufficient for every
planned use (comparators are re-derived per layer from it). The `.pt` is only
needed to *re-estimate* from raw anchors — different split construction,
per-item projections, a probe-based readout. If it is gone, that costs a
fresh capture (~30–40 min pod time including venv rebuild), not a lost
result.

## Pre-merge intermediates (volume)

`20260717_072309_llama8b_instrument_validation_shard1of2` on the volume is a
**pre-merge intermediate** (shard re-run; byte-identity receipt in the
findings log, 2026-07-21). The **merged run is canonical** — analyses join
against the merged directory only.
