# Task: build the Stage 3 analysis pipeline against the smoke shard (design-chat brief, 2026-08-05)

Read `run_configuration.md` (committed alongside this brief) — it is the plain-language spec; this brief adds the implementation contract. Goal: the pipeline is built, tested, and **frozen by commit before run day**, so the label-free results are computed the day the battery runs. Laptop-scale throughout (difference-in-means fits, cosines, regressions, permutation nulls over ~475×32×4096 fp16); no pod, no subject model.

## Fixtures
Develop and test against the smoke shard (10–15 items end-to-end, incl. automatic-labeler pass). All I/O contracts match the run capture schema: per-prompt all-layer anchor activations, entropy covariate, prompt sha, condition metadata, order flag, arm flag.

## Estimator and contrasts (estimator-consistency rule is binding)
- One estimator everywhere: difference of means, applied identically for the conflict direction, the natively refit refusal directions, and the emotion directions. No estimator mixing across constructs.
- Conflict contrast: direction-matched within-scenario differences (opposition minus agreement, same resolution direction), averaged; both option orders averaged before differencing for choice items.

## Layer selection (ratified criterion — implement exactly)
- Choice family only. Scenario-level K-fold CV, stratified by tension type (choose K for ≥4 held-out scenarios per fold; record K and seed).
- Per layer: fit on train folds; score standardized held-out separation of opposition vs agreement projections (report the statistic definition in the output header; same statistic every layer).
- Reliability gate per D50: split-half direction agreement must exceed the matched permutation null; the gate never selects. Numeric gate threshold is OPEN — parameterize it, default to permutation-null-based, and surface it in every report until the researcher pre-states the value.
- Selection: max held-out separation; ties by adjacent-layer stability (define and report the stability metric).
- Refusal-family data must be unreadable by the selection code path (enforce by construction, not convention — separate loader).

## The five label-free analyses (as-designed tier)
1. **Existence:** split-half direction agreement vs scenario-level permutation null (label shuffles at scenario level; report null distribution and observed).
2. **Layer:** the selection above, with the full per-layer curve reported.
3. **Distinctness from refusal:** cosine(conflict, refusal) at the selected layer (refusal refit natively there, same estimator), judged against both directions' split-half self-consistency ceilings; sensitivity repeat at layer 12.
4. **Reducibility:** regress the conflict direction (and per-item projections) on the emotion directions + a generic-difficulty direction fit from the competition battery; report residual norm/variance explained, with the same analysis on held-out items.
5. **Transfer:** the choice-fitted direction at the selected layer applied to refusal-family opposition-vs-agreement contrasts; standardized separation vs permutation null. Confirmatory/exploratory split respected: harm-anchored types reported separately from intermediate-anchored types, never pooled into confirmatory claims.

## Tiered outputs
`results/as_designed/` (label-free, same-day), `results/provisional/` (automatic-labeler manipulation table + provisional conflicted-compliance read; PROVISIONAL in every filename), `results/verified/` (empty until label lock). Every artifact: digest header, ingest sha, batch/freeze sha, pipeline commit sha. Figures per analysis (layer curve, cosine-vs-ceiling, transfer separation) using the documented-measurement style of the advisor packet.

## Blindness support
Produce the researcher's audit export: per-cell text file (generation + designed condition + automatic label + uncertainty flag), NO analysis quantities anywhere in it. Label-lock tool: digests the audited label file; verified tier refuses to run without a lock digest.

## Tests
Suite additions: selection cannot touch refusal loaders (negative test); estimator identity across constructs (shared code path test); permutation-null reproducibility under fixed seed; tier separation (verified tier fails loudly pre-lock); smoke-shard end-to-end producing all as-designed artifacts.

Flag back anything the capture schema is missing for these computations BEFORE freeze — schema gaps found after the pod session cost a recapture.
