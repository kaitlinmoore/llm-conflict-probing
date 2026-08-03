# Three read-only diagnostics — provisional stimulus-similarity run

> **PROVISIONAL — NOT EXHIBIT OUTPUT.** Every number here derives from the
> provisional plumbing run (`20260731_174816_ingnoingest_PROVISIONAL`,
> pre-freeze text: pending-edits batch not applied, validation red on the 6
> known hits). All numbers are superseded at freeze. Diagnostics only — no
> edit recommendations, no actions taken.

Produced by: Claude Fable 5 (model id `claude-fable-5`), 2026-08-03.
Requested: design chat, 2026-08-01 (three diagnostics against the provisional
embedding outputs).

## Provenance

- Provisional run dir: `C:/Users/redsk/AppData/Local/Temp/ss_dry/20260731_174816_ingnoingest_PROVISIONAL`
  (OS temp — fragile; the numbers used here are snapshotted in this report).
- **Input verification:** all 17 input digests in the provisional run's
  manifest match the current committed drafts byte-for-byte (16 battery/control
  JSONL + competition draft). Current `data/battery/drafts/ingest_manifest.json`
  sha256 `367c5fecdc4e…`.
- Cell-level geometry (Diagnostics 1 and 3) is not stored in the provisional
  CSVs; it was recomputed by re-embedding the digest-identical drafts through
  `src/analysis/stimulus_similarity.py`'s own text-assembly and embedding code
  path (`--cell-text full`, same text ordering). **Reproduction check:**
  recomputed T2↔T10 type mean 0.346095 and TC-pc-2 margin −0.031571 match the
  provisional CSVs exactly. Diagnostic 2 is read directly from the provisional
  `*_cell_by_value.csv` artifacts.
- Encoders (same revisions as the provisional run):
  primary `sentence-transformers/all-mpnet-base-v2` @ `e8c3b32edf54…`;
  robustness `sentence-transformers/all-MiniLM-L6-v2` @ `c9745ed1d9f2…`.
  Diagnostic 1 and 3 use the primary encoder (per request); Diagnostic 2 uses
  both.

---

## Diagnostic 1 — what drives T2↔T10 (type-level cosine 0.346, rank 2/66)

Per-scenario-pair mean cosine, T2 scenarios (rows) × T10 scenarios (columns),
primary encoder, **all cells**:

| | pvc-S1 | pvc-S2 | pvc-S3 | pvc-S4 | pvc-S5 | pvc-S6 | row mean |
|---|---|---|---|---|---|---|---|
| **pc-S1** | 0.346 | 0.388 | **0.532** | 0.359 | 0.340 | 0.454 | **0.403** |
| **pc-S2** | 0.396 | 0.408 | 0.301 | 0.318 | 0.323 | 0.259 | 0.334 |
| **pc-S3** | 0.333 | 0.381 | 0.388 | 0.380 | 0.314 | 0.265 | 0.344 |
| **pc-S4** | 0.410 | 0.391 | 0.372 | 0.379 | 0.360 | 0.403 | 0.386 |
| **pc-S5** | 0.326 | 0.306 | 0.251 | 0.216 | 0.262 | 0.219 | 0.263 |

Opposition-cells-only (secondary view) shows the same structure; the top pair
sharpens slightly (pc-S1 × pvc-S3 = 0.549, pc-S1 × pvc-S6 = 0.494; matrix in
the session's diagnostic output, structure otherwise unchanged).

**Top 5 scenario pairs (all cells):**

| rank | T2 | T10 | cosine |
|---|---|---|---|
| 1 | CB-pc-S1 | CB-pvc-S3 | 0.532 |
| 2 | CB-pc-S1 | CB-pvc-S6 | 0.454 |
| 3 | CB-pc-S4 | CB-pvc-S1 | 0.410 |
| 4 | CB-pc-S2 | CB-pvc-S2 | 0.408 |
| 5 | CB-pc-S4 | CB-pvc-S6 | 0.403 |

**Concentrated or uniform: mostly uniform, with one clear near-clone pair on
top.** All 30 scenario pairs sit in 0.216–0.532 (mean 0.346, sd 0.069) — even
the *minimum* pair exceeds the battery's median type-level cosine (~0.19,
rank 33/66). One pair (pc-S1 × pvc-S3, 0.532) is a distinct outlier, 1.1 sd
above the next pair; no other pair stands apart from the pack.

**CB-pc-S1 as contributor (the pending-edit scenario):** it is the **single
largest contributing T2 scenario** — highest row mean (0.403 vs. 0.386, 0.344,
0.334, 0.263) and it supplies the top two pairs, including the one outlier.
However, it is **not the cause of the elevation**: removing CB-pc-S1 entirely
drops the T2↔T10 type mean only from 0.346 to 0.332, which would still rank
**3rd of 66** type pairs (behind T12↔T5 at 0.321 by a whisker). Stated plainly
for the edit decision: the pending T2 CB-pc-S1 rewrite is *also* touching the
top T2↔T10 similarity driver, but even a maximally effective rewrite of that
one scenario cannot bring the pairing down from its elevated position — the
elevation is battery-structural (same value pair by design, D44/D47), spread
across essentially all scenario combinations.

---

## Diagnostic 2 — per-cell culprits for T10 × honesty (unratified z-diagnostic, z = +2.09)

Cell-level cosine to the honesty anchor, all 24 T10 cells, both encoders.
Top 10 per encoder (full ranking in the session diagnostic output; cell IDs
only, per request):

| rank | primary (mpnet) | cos | robustness (MiniLM) | cos |
|---|---|---|---|---|
| 1 | CB-pvc-S4 oppose_tip_refuse | 0.251 | CB-pvc-S5 oppose_tip_comply | 0.161 |
| 2 | CB-pvc-S5 agree_refuse | 0.249 | CB-pvc-S5 agree_refuse | 0.155 |
| 3 | CB-pvc-S5 oppose_tip_refuse | 0.240 | CB-pvc-S4 oppose_tip_refuse | 0.151 |
| 4 | CB-pvc-S4 agree_comply | 0.224 | CB-pvc-S5 oppose_tip_refuse | 0.146 |
| 5 | CB-pvc-S4 oppose_tip_comply | 0.219 | CB-pvc-S3 oppose_tip_refuse | 0.139 |
| 6 | CB-pvc-S1 oppose_tip_refuse | 0.203 | CB-pvc-S5 agree_comply | 0.139 |
| 7 | CB-pvc-S5 oppose_tip_comply | 0.198 | CB-pvc-S2 oppose_tip_refuse | 0.128 |
| 8 | CB-pvc-S4 agree_refuse | 0.195 | CB-pvc-S1 oppose_tip_refuse | 0.126 |
| 9 | CB-pvc-S6 agree_refuse | 0.195 | CB-pvc-S1 oppose_tip_comply | 0.119 |
| 10 | CB-pvc-S5 agree_comply | 0.192 | CB-pvc-S4 agree_refuse | 0.118 |

Scenario means (primary → robustness): S4 0.222 → 0.122; S5 0.220 → 0.150;
S6 0.172 → **0.049**; S1 0.163 → 0.091; S2 0.142 → 0.087; S3 0.141 → 0.111.

Condition means (primary → robustness): oppose_tip_refuse 0.204 → 0.125;
agree_refuse 0.175 → 0.090; oppose_tip_comply 0.171 → 0.105;
agree_comply 0.157 → 0.087.

**Where it concentrates:** in **scenarios, not conditions** — CB-pvc-S4 and
CB-pvc-S5 carry the elevation on both encoders (all four cells of each rank
high; it is not an opposition-cells-only effect). There is a mild secondary
condition tilt: `oppose_tip_refuse` is the top condition on both encoders, but
the spread across conditions (~0.05) is small next to the scenario spread.

**Encoder disagreement, surfaced not resolved:** the encoders agree on S4/S5
as culprits but **disagree sharply on CB-pvc-S6** — 3rd-highest scenario under
the primary encoder, dead last under robustness. S6 readings should be treated
as encoder-fragile.

Reminder: the z = +2.09 flag comes from the **unratified** relative-affinity
diagnostic (Claude's addition, not the ratified rule).

---

## Diagnostic 3 — why TC-pc-2 misplaces (margin −0.032, only negative control)

**Its 10 nearest battery cells (primary encoder):**

| rank | cell | type | cosine |
|---|---|---|---|
| 1 | CB-acw-S4 oppose_tip_refuse | T12 | 0.434 |
| 2 | CB-acw-S4 agree_refuse | T12 | 0.410 |
| 3 | CB-acw-S4 oppose_tip_comply | T12 | 0.403 |
| 4 | CB-acw-S4 agree_comply | T12 | 0.370 |
| 5 | CB-ta-S4 agree_B | T5 | 0.331 |
| 6 | **CB-pc-S2 oppose_tip_A** | **T2** | 0.326 |
| 7 | CB-ta-S4 oppose_tip_A | T5 | 0.322 |
| 8 | CB-ta-S5 agree_B | T5 | 0.321 |
| 9 | CB-ta-S4 oppose_tip_B | T5 | 0.315 |
| 10 | CB-ta-S4 agree_A | T5 | 0.297 |

One of ten is its own type. The wrong-type attraction is specific, not
diffuse: all four cells of T12 CB-acw-S4, and five cells of T5 CB-ta-S4/S5.

**Similarity to each intended T2 target scenario:** CB-pc-S2 **0.275**;
CB-pc-S3 0.107; CB-pc-S5 0.085; CB-pc-S4 0.043; CB-pc-S1 **0.015**.

**Contrast — the other T2 privacy–care controls (all placed positive):**

| control | margin | to own type | best target scenario | own-type cells in nearest-10 |
|---|---|---|---|---|
| TC-pc-1 | +0.073 | 0.228 | pc-S1 = 0.369 | 4 |
| **TC-pc-2** | **−0.032** | 0.105 | pc-S2 = 0.275 | 1 |
| TC-pc-3 | +0.014 | 0.096 | pc-S3 = 0.184 | **0** |
| TC-pc-4 | +0.032 | 0.165 | pc-S4 = 0.315 | 2 |

(For scale: the T8/T9/T10 refusal-family controls run margins +0.085 to
+0.258.)

**Verdict: both, but "far from its targets" is the dominant term.** TC-pc-2's
background similarity to the rest of the battery (0.137) is ordinary — in the
range every other control occupies (0.08–0.18). What is anomalous is the
target side: it couples to exactly one T2 scenario (pc-S2, 0.275) and is
near-orthogonal to the other four (0.015–0.107), giving the lowest own-type
mean of any T2 control with a normal-sized denominator. The wrong-type
attraction (T12 CB-acw-S4 at 0.37–0.43) is real and specific and pushes the
margin over the line into negative, but removing it would still leave a
weakly-coupled control, not a well-placed one. Read for the fix decision
(researcher's): the failure mode is under-coupling to T2's scenario spread,
not topical capture by another type alone.

**Adjacent observation (flagged, no action):** TC-pc-3 shows the same anatomy
one notch milder — zero own-type cells in its nearest-10, margin barely
positive (+0.014). The T2 control set as a whole couples far more weakly to
its type than the three refusal-family control sets do; TC-pc-2 is the extreme
of a T2-wide pattern, not a lone defect.

---

*Flags for the design chat: (1) D1 — CB-pc-S1 is the top T2↔T10 driver but
the elevation survives its removal at rank ~3/66; the pending rewrite decision
should not be expected to also resolve the similarity elevation. (2) D2 —
honesty affinity concentrates in CB-pvc-S4/S5 across all conditions; S6 is
encoder-fragile. (3) D3 — TC-pc-2 is under-coupled to its targets more than
captured by wrong ones; TC-pc-3 borders the same state. No actions taken on
any of these.*
