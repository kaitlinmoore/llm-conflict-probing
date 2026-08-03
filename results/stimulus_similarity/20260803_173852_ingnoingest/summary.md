# Stimulus-similarity exhibit — conflict battery

Produced by: Claude Fable 5 (model id claude-fable-5)
Generated: 2026-08-03T17:39:19+00:00
Run dir: `results/stimulus_similarity/20260803_173852_ingnoingest`

**Descriptive exhibit — not gating.** No thresholds, no pass/fail, no rewrite triggers. Independent of the subject model by design: no Llama-derived embeddings appear anywhere in this analysis.

## Encoders

| role | model | family | revision | pooling |
|---|---|---|---|---|
| primary | `sentence-transformers/all-mpnet-base-v2` | MPNet (Microsoft) bi-encoder | `e8c3b32edf5434bc2275fc9bab85f82640a19130` | mean over attention-masked tokens, then L2 normalize |
| robustness | `sentence-transformers/all-MiniLM-L6-v2` | MiniLM (BERT-distilled) bi-encoder | `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` | mean over attention-masked tokens, then L2 normalize |

Caveat on independence: both encoders sit outside the Llama lineage (the design requirement), but they are trained on overlapping sentence-embedding corpora, so agreement between them is weaker evidence than agreement between genuinely unrelated instruments.

## Text version

Cell assembly: `full`. Ingest digests:
- `competition_battery_draft.jsonl` — `35d95ffb4419…`
- `type10_privacy_vs_care.controls.jsonl` — `9529cb898a14…`
- `type10_privacy_vs_care.jsonl` — `f925e108d452…`
- `type11_integrity_vs_mercy.jsonl` — `575724fb542d…`
- `type12_autonomy_vs_collective.jsonl` — `4ed9317dfd6b…`
- `type1_honesty_vs_care.jsonl` — `d73988a5af5d…`
- `type2_privacy_vs_care.controls.jsonl` — `084ec91b2101…`
- `type2_privacy_vs_care.jsonl` — `73347ecc5619…`
- `type3_mercy_vs_desert.jsonl` — `ca07340178a7…`
- `type4_loyalty_vs_honesty.jsonl` — `a629e7d084f7…`
- `type5_tradition_vs_autonomy.jsonl` — `c90c9038cb14…`
- `type6_authority_vs_autonomy.jsonl` — `0611b18eace1…`
- `type7_harm_vs_autonomy.jsonl` — `0065d11c983b…`
- `type8_harm_vs_privacy.controls.jsonl` — `621d657b8881…`
- `type8_harm_vs_privacy.jsonl` — `b92b88d4f289…`
- `type9_harm_vs_integrity.controls.jsonl` — `fb155fb55ba4…`
- `type9_harm_vs_integrity.jsonl` — `094d52b52899…`

Value anchors: `data/battery/value_anchors.json` sha256 `b2656d2c552f…`, from `Value_Roster_Derivation.docx` sha256 `07e0a603cabb…` (verbatim 'Operational definition (behavioral)' column).

## 1. Worry spots (pre-registered)

| pair | cosine | rank | percentile | why watched |
|---|---|---|---|---|
| type2_privacy_vs_care ↔ type10_privacy_vs_care | 0.328 | 3/66 | 0.97 | same value pair, deliberate topic divergence |
| type8_harm_vs_privacy ↔ type2_privacy_vs_care | 0.188 | 37/66 | 0.45 | shared privacy pole, screen-elevated harm_avoidance-privacy |
| type9_harm_vs_integrity ↔ type8_harm_vs_privacy | 0.279 | 7/66 | 0.91 | shared harm pole |
| type9_harm_vs_integrity ↔ type7_harm_vs_autonomy | 0.395 | 1/66 | 1.00 | shared harm pole |
| type9_harm_vs_integrity ↔ type11_integrity_vs_mercy | 0.138 | 55/66 | 0.18 | shared integrity pole |

## 2. Third-value flags

**Ratified rule as specified** (a non-pole value ranks above one of the type's own poles, or sits in the top decile of the cell-by-value distribution): **89 flags of ~168 possible type-value combinations.**

> ⚠️ **The rule is not discriminative on this corpus, for the structural reason the brief itself names.** Authoring rule 7 strips value vocabulary from stimulus text, so own-pole similarity is low by design — which makes "ranks above an own pole" a floor that most unrelated values clear. Firing on this share of combinations, the flag list cannot function as a tripwire. The full list is in `*_third_value_flags.csv`; the relative diagnostic below is offered as an alternative read-out and is **Claude's addition, not a ratified substitute** — it needs a researcher decision before it is used as the operative signal.

**Relative diagnostic (addition, unratified):** value affinity standardized *within value across types* — asking whether a type is unusually close to a value relative to every other type, which also cancels the constant offset from the anchors' shared 'Pull toward/against …' frame. Flagged at z ≥ 2.0: **0**. (Bound: standardizing across n=12 types caps z at (n−1)/√n ≈ 3.18, so 2.0 is a real but not extreme bar.)

Ratified-rule flag list (first 20 by mean similarity):

| type | third value | mean cos | > own pole | top decile | top cells |
|---|---|---|---|---|---|
| type10_privacy_vs_care | kindness | 0.259 | yes | yes | type10_privacy_vs_care:CB-pvc-S4:agree_comply; type10_privacy_vs_care:CB-pvc-S4:oppose_tip_refuse; type10_privacy_vs_care:CB-pvc-S4:oppose_tip_comply |
| type1_honesty_vs_care | kindness | 0.221 | yes | yes | type1_honesty_vs_care:CB-hc-S1:oppose_tip_B; type1_honesty_vs_care:CB-hc-S2:oppose_tip_B; type1_honesty_vs_care:CB-hc-S1:agree_A |
| type10_privacy_vs_care | fairness | 0.197 |  | yes | type10_privacy_vs_care:CB-pvc-S2:agree_comply; type10_privacy_vs_care:CB-pvc-S6:oppose_tip_comply; type10_privacy_vs_care:CB-pvc-S4:agree_comply |
| type12_autonomy_vs_collective | desert | 0.196 | yes | yes | type12_autonomy_vs_collective:CB-acw-S4:oppose_tip_comply; type12_autonomy_vs_collective:CB-acw-S4:agree_refuse; type12_autonomy_vs_collective:CB-acw-S4:oppose_tip_refuse |
| type11_integrity_vs_mercy | authority | 0.194 |  | yes | type11_integrity_vs_mercy:CB-imv-S1:agree_refuse; type11_integrity_vs_mercy:CB-imv-S5:oppose_tip_comply; type11_integrity_vs_mercy:CB-imv-S6:oppose_tip_comply |
| type11_integrity_vs_mercy | kindness | 0.182 |  | yes | type11_integrity_vs_mercy:CB-imv-S6:oppose_tip_comply; type11_integrity_vs_mercy:CB-imv-S6:oppose_tip_refuse; type11_integrity_vs_mercy:CB-imv-S6:agree_refuse |
| type6_authority_vs_autonomy | desert | 0.178 | yes | yes | type6_authority_vs_autonomy:CB-aa-S2:oppose_tip_B; type6_authority_vs_autonomy:CB-aa-S2:oppose_tip_A; type6_authority_vs_autonomy:CB-aa-S4:oppose_tip_A |
| type12_autonomy_vs_collective | care | 0.173 | yes |  | type12_autonomy_vs_collective:CB-acw-S6:oppose_tip_comply; type12_autonomy_vs_collective:CB-acw-S4:oppose_tip_comply; type12_autonomy_vs_collective:CB-acw-S6:oppose_tip_refuse |
| type12_autonomy_vs_collective | impartiality | 0.170 | yes |  | type12_autonomy_vs_collective:CB-acw-S6:oppose_tip_comply; type12_autonomy_vs_collective:CB-acw-S6:oppose_tip_refuse; type12_autonomy_vs_collective:CB-acw-S2:oppose_tip_comply |
| type12_autonomy_vs_collective | loyalty | 0.166 | yes |  | type12_autonomy_vs_collective:CB-acw-S5:oppose_tip_comply; type12_autonomy_vs_collective:CB-acw-S5:oppose_tip_refuse; type12_autonomy_vs_collective:CB-acw-S4:oppose_tip_comply |
| type6_authority_vs_autonomy | kindness | 0.158 | yes |  | type6_authority_vs_autonomy:CB-aa-S5:oppose_tip_A; type6_authority_vs_autonomy:CB-aa-S4:oppose_tip_B; type6_authority_vs_autonomy:CB-aa-S5:oppose_tip_B |
| type5_tradition_vs_autonomy | impartiality | 0.150 | yes |  | type5_tradition_vs_autonomy:CB-ta-S3:oppose_tip_A; type5_tradition_vs_autonomy:CB-ta-S3:oppose_tip_B; type5_tradition_vs_autonomy:CB-ta-S3:agree_B |
| type3_mercy_vs_desert | integrity | 0.148 | yes |  | type3_mercy_vs_desert:CB-md-S4:oppose_tip_A; type3_mercy_vs_desert:CB-md-S4:oppose_tip_B; type3_mercy_vs_desert:CB-md-S4:agree_A |
| type12_autonomy_vs_collective | fairness | 0.141 | yes |  | type12_autonomy_vs_collective:CB-acw-S6:oppose_tip_comply; type12_autonomy_vs_collective:CB-acw-S4:agree_refuse; type12_autonomy_vs_collective:CB-acw-S6:oppose_tip_refuse |
| type5_tradition_vs_autonomy | desert | 0.141 | yes |  | type5_tradition_vs_autonomy:CB-ta-S4:oppose_tip_A; type5_tradition_vs_autonomy:CB-ta-S4:oppose_tip_B; type5_tradition_vs_autonomy:CB-ta-S3:oppose_tip_B |
| type12_autonomy_vs_collective | kindness | 0.140 | yes |  | type12_autonomy_vs_collective:CB-acw-S5:oppose_tip_comply; type12_autonomy_vs_collective:CB-acw-S6:agree_comply; type12_autonomy_vs_collective:CB-acw-S6:oppose_tip_comply |
| type12_autonomy_vs_collective | authority | 0.135 | yes |  | type12_autonomy_vs_collective:CB-acw-S4:oppose_tip_comply; type12_autonomy_vs_collective:CB-acw-S4:oppose_tip_refuse; type12_autonomy_vs_collective:CB-acw-S4:agree_refuse |
| type9_harm_vs_integrity | kindness | 0.135 | yes |  | type9_harm_vs_integrity:CB-hvi-S2:agree_refuse; type9_harm_vs_integrity:CB-hvi-S4:agree_refuse; type9_harm_vs_integrity:CB-hvi-S6:agree_refuse |
| type6_authority_vs_autonomy | impartiality | 0.134 | yes |  | type6_authority_vs_autonomy:CB-aa-S2:oppose_tip_B; type6_authority_vs_autonomy:CB-aa-S2:oppose_tip_A; type6_authority_vs_autonomy:CB-aa-S2:agree_B |
| type5_tradition_vs_autonomy | loyalty | 0.133 | yes |  | type5_tradition_vs_autonomy:CB-ta-S4:oppose_tip_A; type5_tradition_vs_autonomy:CB-ta-S3:oppose_tip_B; type5_tradition_vs_autonomy:CB-ta-S5:oppose_tip_B |

## 3. Own-value similarities — reported, NOT a presence check

The authoring rules deliberately strip value vocabulary from stimulus text (rule 7). **Low own-value similarity is expected for clean text and is not evidence the value is absent.** No flag rule is applied to this read-out. Full table: `*_type_by_value_means.csv`.

| type | own poles | own-pole cosines |
|---|---|---|
| type10_privacy_vs_care | privacy, care | privacy=0.208, care=0.313 |
| type11_integrity_vs_mercy | integrity, mercy | integrity=0.229, mercy=0.240 |
| type12_autonomy_vs_collective | autonomy, collective_welfare | autonomy=0.103, collective_welfare=0.161 |
| type1_honesty_vs_care | honesty, care | honesty=0.068, care=0.043 |
| type2_privacy_vs_care | privacy, care | privacy=0.050, care=0.098 |
| type3_mercy_vs_desert | mercy, desert | mercy=0.110, desert=0.080 |
| type4_loyalty_vs_honesty | loyalty, honesty | loyalty=0.021, honesty=0.074 |
| type5_tradition_vs_autonomy | tradition, autonomy | tradition=0.110, autonomy=0.069 |
| type6_authority_vs_autonomy | authority, autonomy | authority=0.078, autonomy=0.056 |
| type7_harm_vs_autonomy | harm_avoidance, autonomy | harm_avoidance=-0.053, autonomy=-0.012 |
| type8_harm_vs_privacy | harm_avoidance, privacy | harm_avoidance=0.051, privacy=0.081 |
| type9_harm_vs_integrity | harm_avoidance, integrity | harm_avoidance=-0.009, integrity=0.013 |

## 4. Minimal-pair tightness and tip symmetry

Opposition-sibling distance: mean 0.0470, sd 0.0257, n 66. Outliers (|z| ≥ 2.0): type12_autonomy_vs_collective:CB-acw-S3 (0.123), type1_honesty_vs_care:CB-hc-S1 (0.127), type4_loyalty_vs_honesty:CB-lh-S1 (0.108), type5_tradition_vs_autonomy:CB-ta-S1 (0.113).

Tip-symmetry asymmetry: mean 0.0266, sd 0.0196, n 66. Outliers: type1_honesty_vs_care:CB-hc-S2 (0.075), type8_harm_vs_privacy:CB-hvp-S5 (0.084).

## 5. Topical-control placement

| control | to own type | to rest | margin |
|---|---|---|---|
| type10_privacy_vs_care:TC-pvc-1 | 0.405 | 0.155 | +0.249 |
| type10_privacy_vs_care:TC-pvc-2 | 0.342 | 0.181 | +0.160 |
| type10_privacy_vs_care:TC-pvc-3 | 0.344 | 0.155 | +0.189 |
| type2_privacy_vs_care:TC-pc-1 | 0.228 | 0.148 | +0.080 |
| type2_privacy_vs_care:TC-pc-2 | 0.269 | 0.183 | +0.086 |
| type2_privacy_vs_care:TC-pc-3 | 0.304 | 0.185 | +0.119 |
| type2_privacy_vs_care:TC-pc-4 | 0.203 | 0.181 | +0.022 |
| type8_harm_vs_privacy:TC-hvp-1 | 0.331 | 0.152 | +0.179 |
| type8_harm_vs_privacy:TC-hvp-2 | 0.239 | 0.153 | +0.086 |
| type8_harm_vs_privacy:TC-hvp-3 | 0.328 | 0.154 | +0.174 |
| type9_harm_vs_integrity:TC-hvi-1 | 0.393 | 0.137 | +0.256 |
| type9_harm_vs_integrity:TC-hvi-2 | 0.333 | 0.120 | +0.213 |
| type9_harm_vs_integrity:TC-hvi-3 | 0.390 | 0.148 | +0.243 |

## 6. Encoder agreement

Type-pair matrices: Pearson 0.925, Spearman 0.926 over 66 pairs.

Third-value flag sets: 48 shared; primary 89, robustness 78.

Disagreement (surfaced, not resolved):
- primary only: type11_integrity_vs_mercy / authority
- primary only: type11_integrity_vs_mercy / kindness
- primary only: type12_autonomy_vs_collective / authority
- primary only: type12_autonomy_vs_collective / desert
- primary only: type12_autonomy_vs_collective / impartiality
- primary only: type12_autonomy_vs_collective / integrity
- primary only: type12_autonomy_vs_collective / kindness
- primary only: type12_autonomy_vs_collective / mercy
- primary only: type12_autonomy_vs_collective / tradition
- primary only: type4_loyalty_vs_honesty / authority
- primary only: type4_loyalty_vs_honesty / care
- primary only: type4_loyalty_vs_honesty / collective_welfare
- primary only: type4_loyalty_vs_honesty / desert
- primary only: type4_loyalty_vs_honesty / harm_avoidance
- primary only: type4_loyalty_vs_honesty / impartiality
- primary only: type5_tradition_vs_autonomy / authority
- primary only: type5_tradition_vs_autonomy / care
- primary only: type5_tradition_vs_autonomy / collective_welfare
- primary only: type5_tradition_vs_autonomy / desert
- primary only: type5_tradition_vs_autonomy / fairness
- primary only: type5_tradition_vs_autonomy / honesty
- primary only: type5_tradition_vs_autonomy / impartiality
- primary only: type5_tradition_vs_autonomy / integrity
- primary only: type5_tradition_vs_autonomy / kindness
- primary only: type5_tradition_vs_autonomy / loyalty
- primary only: type5_tradition_vs_autonomy / privacy
- primary only: type6_authority_vs_autonomy / fairness
- primary only: type6_authority_vs_autonomy / honesty
- primary only: type6_authority_vs_autonomy / impartiality
- primary only: type6_authority_vs_autonomy / integrity
- primary only: type6_authority_vs_autonomy / loyalty
- primary only: type6_authority_vs_autonomy / privacy
- primary only: type7_harm_vs_autonomy / fairness
- primary only: type7_harm_vs_autonomy / mercy
- primary only: type8_harm_vs_privacy / authority
- primary only: type8_harm_vs_privacy / autonomy
- primary only: type8_harm_vs_privacy / desert
- primary only: type8_harm_vs_privacy / fairness
- primary only: type8_harm_vs_privacy / integrity
- primary only: type8_harm_vs_privacy / kindness
- primary only: type9_harm_vs_integrity / fairness
- robustness only: type10_privacy_vs_care / authority
- robustness only: type10_privacy_vs_care / desert
- robustness only: type10_privacy_vs_care / integrity
- robustness only: type10_privacy_vs_care / loyalty
- robustness only: type10_privacy_vs_care / mercy
- robustness only: type10_privacy_vs_care / tradition
- robustness only: type1_honesty_vs_care / autonomy
- robustness only: type1_honesty_vs_care / harm_avoidance
- robustness only: type1_honesty_vs_care / loyalty
- robustness only: type1_honesty_vs_care / mercy
- robustness only: type2_privacy_vs_care / authority
- robustness only: type2_privacy_vs_care / autonomy
- robustness only: type2_privacy_vs_care / desert
- robustness only: type2_privacy_vs_care / fairness
- robustness only: type2_privacy_vs_care / harm_avoidance
- robustness only: type2_privacy_vs_care / honesty
- robustness only: type2_privacy_vs_care / loyalty
- robustness only: type2_privacy_vs_care / mercy
- robustness only: type2_privacy_vs_care / tradition
- robustness only: type3_mercy_vs_desert / collective_welfare
- robustness only: type3_mercy_vs_desert / fairness
- robustness only: type3_mercy_vs_desert / harm_avoidance
- robustness only: type3_mercy_vs_desert / impartiality
- robustness only: type3_mercy_vs_desert / kindness
- robustness only: type3_mercy_vs_desert / privacy
- robustness only: type3_mercy_vs_desert / tradition
- robustness only: type4_loyalty_vs_honesty / mercy
- robustness only: type4_loyalty_vs_honesty / tradition
- robustness only: type7_harm_vs_autonomy / sanctity
- robustness only: type9_harm_vs_integrity / sanctity

## Open question for the researcher

Cell assembly: the brief said "stem + condition insert, exactly as administered". For opposition cells the shared conflict text is also administered, and omitting it would collapse opposition cells onto their agreement siblings, so this run used `--cell-text full` (`full` = stem + shared text + insert). Re-run with `--cell-text stem_insert` for the narrower literal reading.
