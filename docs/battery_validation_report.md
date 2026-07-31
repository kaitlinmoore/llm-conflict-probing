# Battery validation report

Produced by: Claude Fable 5 (model id claude-fable-5)
Generated: 2026-07-31T14:58:43+00:00 — `src/battery/validate_battery.py`
Blocklists: `data/battery/lexeme_blocklists.json` sha256 `e37400e9cc45…`

Inputs:
- `data\battery\drafts\type10_privacy_vs_care.controls.jsonl` — sha256 `0e987d10bcad…`, 2557 bytes
- `data\battery\drafts\type10_privacy_vs_care.jsonl` — sha256 `8d7107536803…`, 43777 bytes
- `data\battery\drafts\type11_integrity_vs_mercy.jsonl` — sha256 `68bd22978c1b…`, 44020 bytes
- `data\battery\drafts\type12_autonomy_vs_collective.jsonl` — sha256 `7b65cf5f2c15…`, 45834 bytes
- `data\battery\drafts\type1_honesty_vs_care.jsonl` — sha256 `9c5f92448b35…`, 29532 bytes
- `data\battery\drafts\type2_privacy_vs_care.controls.jsonl` — sha256 `bd77948ab6db…`, 3418 bytes
- `data\battery\drafts\type2_privacy_vs_care.jsonl` — sha256 `715895c15ed5…`, 33269 bytes
- `data\battery\drafts\type3_mercy_vs_desert.jsonl` — sha256 `164445bceb2b…`, 34423 bytes
- `data\battery\drafts\type4_loyalty_vs_honesty.jsonl` — sha256 `9ea93a61cbbe…`, 33686 bytes
- `data\battery\drafts\type5_tradition_vs_autonomy.jsonl` — sha256 `53e785705fee…`, 36030 bytes
- `data\battery\drafts\type6_authority_vs_autonomy.jsonl` — sha256 `3018c2a4fe59…`, 34984 bytes
- `data\battery\drafts\type7_harm_vs_autonomy.jsonl` — sha256 `67195ff12052…`, 39069 bytes
- `data\battery\drafts\type8_harm_vs_privacy.controls.jsonl` — sha256 `efc8af4ee3f1…`, 2410 bytes
- `data\battery\drafts\type8_harm_vs_privacy.jsonl` — sha256 `bd1599fc0579…`, 43340 bytes
- `data\battery\drafts\type9_harm_vs_integrity.controls.jsonl` — sha256 `71013595cab6…`, 2415 bytes
- `data\battery\drafts\type9_harm_vs_integrity.jsonl` — sha256 `88c1fe1c290c…`, 45205 bytes

## Verdict: **PASS** — 277 cells checked, 0 blocking, 0 warnings, 0 researcher flags, 3 length flags, 7 name flags, 6 cross-type lexeme flags

## Cross-type character-name flags (non-blocking)

Reused names risk cross-item association at administration and muddy per-type similarity readings. The extractor over-collects proper nouns (place names, brands), so entries need a human glance.

- 'Dana' appears in 2 types: type1_honesty_vs_care(1 cells), type4_loyalty_vs_honesty(1 cells)
- 'Marcus' appears in 2 types: type1_honesty_vs_care(1 cells), type5_tradition_vs_autonomy(1 cells)
- 'Mom' appears in 3 types: type4_loyalty_vs_honesty(1 cells), type8_harm_vs_privacy(1 cells), type9_harm_vs_integrity(1 cells)
- 'Sam' appears in 3 types: type1_honesty_vs_care(1 cells), type3_mercy_vs_desert(1 cells), type4_loyalty_vs_honesty(1 cells)
- near-collision 'Devon' (type3_mercy_vs_desert) vs 'Devora' (type10_privacy_vs_care)
- near-collision 'Priya' (type4_loyalty_vs_honesty) vs 'Priyanka' (type10_privacy_vs_care)
- near-collision 'What' (type1_honesty_vs_care) vs 'Whatever' (type4_loyalty_vs_honesty)

## Cross-type lexeme flags (non-blocking — scope question)

Hits against **another type's** per-value list. The per-type scoping used for blocking above checks each type against the global list plus its own two poles; the workbook READMEs additionally say prior lists 'apply globally'. If that is the intended rule, these become blocking — a researcher decision, recorded in `data/battery/battery_schema.md`.

- type12_autonomy_vs_collective:CB-acw-S5:agree_comply:stem — 'deserves' (other type's 'desert' list)
- type12_autonomy_vs_collective:CB-acw-S5:agree_refuse:stem — 'deserves' (other type's 'desert' list)
- type12_autonomy_vs_collective:CB-acw-S5:oppose_tip_comply:stem — 'deserves' (other type's 'desert' list)
- type12_autonomy_vs_collective:CB-acw-S5:oppose_tip_refuse:stem — 'deserves' (other type's 'desert' list)
- type2_privacy_vs_care:CB-pc-S1:oppose_tip_A:shared_opposition_text — 'safety' (other type's 'harm' list)
- type2_privacy_vs_care:CB-pc-S1:oppose_tip_B:shared_opposition_text — 'safety' (other type's 'harm' list)

## Length flags (non-blocking, check e)
- type1_honesty_vs_care.jsonl:CB-hc-S1:agree_A insert 35 tokens > 1.5x scenario median 22.5
- type1_honesty_vs_care.jsonl:CB-hc-S3:agree_A insert 33 tokens > 1.5x scenario median 16
- type1_honesty_vs_care.jsonl:CB-hc-S4:agree_A insert 41 tokens > 1.5x scenario median 21

## Per-file detail

### `type10_privacy_vs_care.controls.jsonl` — 3 topical controls

### `type10_privacy_vs_care.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-pvc-S1 | agree_comply | 39 | 39.5 |  |
| CB-pvc-S1 | agree_refuse | 40 | 39.5 |  |
| CB-pvc-S1 | oppose_tip_comply | 39 | 39.5 |  |
| CB-pvc-S1 | oppose_tip_refuse | 44 | 39.5 |  |
| CB-pvc-S2 | agree_comply | 41 | 37.5 |  |
| CB-pvc-S2 | agree_refuse | 36 | 37.5 |  |
| CB-pvc-S2 | oppose_tip_comply | 37 | 37.5 |  |
| CB-pvc-S2 | oppose_tip_refuse | 38 | 37.5 |  |
| CB-pvc-S3 | agree_comply | 43 | 40.5 |  |
| CB-pvc-S3 | agree_refuse | 30 | 40.5 |  |
| CB-pvc-S3 | oppose_tip_comply | 41 | 40.5 |  |
| CB-pvc-S3 | oppose_tip_refuse | 40 | 40.5 |  |
| CB-pvc-S4 | agree_comply | 44 | 43.5 |  |
| CB-pvc-S4 | agree_refuse | 43 | 43.5 |  |
| CB-pvc-S4 | oppose_tip_comply | 45 | 43.5 |  |
| CB-pvc-S4 | oppose_tip_refuse | 37 | 43.5 |  |
| CB-pvc-S5 | agree_comply | 42 | 39.5 |  |
| CB-pvc-S5 | agree_refuse | 41 | 39.5 |  |
| CB-pvc-S5 | oppose_tip_comply | 34 | 39.5 |  |
| CB-pvc-S5 | oppose_tip_refuse | 38 | 39.5 |  |
| CB-pvc-S6 | agree_comply | 39 | 40 |  |
| CB-pvc-S6 | agree_refuse | 33 | 40 |  |
| CB-pvc-S6 | oppose_tip_comply | 45 | 40 |  |
| CB-pvc-S6 | oppose_tip_refuse | 41 | 40 |  |

### `type11_integrity_vs_mercy.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-imv-S1 | agree_comply | 29 | 35 |  |
| CB-imv-S1 | agree_refuse | 40 | 35 |  |
| CB-imv-S1 | oppose_tip_comply | 30 | 35 |  |
| CB-imv-S1 | oppose_tip_refuse | 42 | 35 |  |
| CB-imv-S2 | agree_comply | 35 | 39.5 |  |
| CB-imv-S2 | agree_refuse | 43 | 39.5 |  |
| CB-imv-S2 | oppose_tip_comply | 38 | 39.5 |  |
| CB-imv-S2 | oppose_tip_refuse | 41 | 39.5 |  |
| CB-imv-S3 | agree_comply | 32 | 43 |  |
| CB-imv-S3 | agree_refuse | 44 | 43 |  |
| CB-imv-S3 | oppose_tip_comply | 44 | 43 |  |
| CB-imv-S3 | oppose_tip_refuse | 42 | 43 |  |
| CB-imv-S4 | agree_comply | 34 | 38 |  |
| CB-imv-S4 | agree_refuse | 39 | 38 |  |
| CB-imv-S4 | oppose_tip_comply | 38 | 38 |  |
| CB-imv-S4 | oppose_tip_refuse | 38 | 38 |  |
| CB-imv-S5 | agree_comply | 32 | 38 |  |
| CB-imv-S5 | agree_refuse | 43 | 38 |  |
| CB-imv-S5 | oppose_tip_comply | 35 | 38 |  |
| CB-imv-S5 | oppose_tip_refuse | 41 | 38 |  |
| CB-imv-S6 | agree_comply | 30 | 38.5 |  |
| CB-imv-S6 | agree_refuse | 45 | 38.5 |  |
| CB-imv-S6 | oppose_tip_comply | 38 | 38.5 |  |
| CB-imv-S6 | oppose_tip_refuse | 39 | 38.5 |  |

### `type12_autonomy_vs_collective.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-acw-S1 | agree_comply | 47 | 41.5 |  |
| CB-acw-S1 | agree_refuse | 40 | 41.5 |  |
| CB-acw-S1 | oppose_tip_comply | 41 | 41.5 |  |
| CB-acw-S1 | oppose_tip_refuse | 42 | 41.5 |  |
| CB-acw-S2 | agree_comply | 43 | 42.5 |  |
| CB-acw-S2 | agree_refuse | 37 | 42.5 |  |
| CB-acw-S2 | oppose_tip_comply | 42 | 42.5 |  |
| CB-acw-S2 | oppose_tip_refuse | 43 | 42.5 |  |
| CB-acw-S3 | agree_comply | 51 | 48 |  |
| CB-acw-S3 | agree_refuse | 36 | 48 |  |
| CB-acw-S3 | oppose_tip_comply | 46 | 48 |  |
| CB-acw-S3 | oppose_tip_refuse | 50 | 48 |  |
| CB-acw-S4 | agree_comply | 50 | 41 |  |
| CB-acw-S4 | agree_refuse | 37 | 41 |  |
| CB-acw-S4 | oppose_tip_comply | 40 | 41 |  |
| CB-acw-S4 | oppose_tip_refuse | 42 | 41 |  |
| CB-acw-S5 | agree_comply | 46 | 44 |  |
| CB-acw-S5 | agree_refuse | 35 | 44 |  |
| CB-acw-S5 | oppose_tip_comply | 49 | 44 |  |
| CB-acw-S5 | oppose_tip_refuse | 42 | 44 |  |
| CB-acw-S6 | agree_comply | 56 | 39 |  |
| CB-acw-S6 | agree_refuse | 37 | 39 |  |
| CB-acw-S6 | oppose_tip_comply | 37 | 39 |  |
| CB-acw-S6 | oppose_tip_refuse | 41 | 39 |  |

### `type1_honesty_vs_care.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-hc-S1 | agree_A | 35 | 22.5 | FLAG |
| CB-hc-S1 | agree_B | 16 | 22.5 |  |
| CB-hc-S1 | oppose_tip_A | 15 | 22.5 |  |
| CB-hc-S1 | oppose_tip_B | 29 | 22.5 |  |
| CB-hc-S2 | agree_A | 32 | 23 |  |
| CB-hc-S2 | agree_B | 19 | 23 |  |
| CB-hc-S2 | oppose_tip_A | 14 | 23 |  |
| CB-hc-S2 | oppose_tip_B | 27 | 23 |  |
| CB-hc-S3 | agree_A | 33 | 16 | FLAG |
| CB-hc-S3 | agree_B | 19 | 16 |  |
| CB-hc-S3 | oppose_tip_A | 13 | 16 |  |
| CB-hc-S3 | oppose_tip_B | 12 | 16 |  |
| CB-hc-S4 | agree_A | 41 | 21 | FLAG |
| CB-hc-S4 | agree_B | 13 | 21 |  |
| CB-hc-S4 | oppose_tip_A | 17 | 21 |  |
| CB-hc-S4 | oppose_tip_B | 25 | 21 |  |
| CB-hc-S5 | agree_A | 23 | 19 |  |
| CB-hc-S5 | agree_B | 15 | 19 |  |
| CB-hc-S5 | oppose_tip_A | 13 | 19 |  |
| CB-hc-S5 | oppose_tip_B | 24 | 19 |  |

### `type2_privacy_vs_care.controls.jsonl` — 4 topical controls

### `type2_privacy_vs_care.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-pc-S1 | agree_A | 32 | 29.5 |  |
| CB-pc-S1 | agree_B | 32 | 29.5 |  |
| CB-pc-S1 | oppose_tip_A | 27 | 29.5 |  |
| CB-pc-S1 | oppose_tip_B | 23 | 29.5 |  |
| CB-pc-S2 | agree_A | 26 | 30 |  |
| CB-pc-S2 | agree_B | 30 | 30 |  |
| CB-pc-S2 | oppose_tip_A | 39 | 30 |  |
| CB-pc-S2 | oppose_tip_B | 30 | 30 |  |
| CB-pc-S3 | agree_A | 26 | 31 |  |
| CB-pc-S3 | agree_B | 31 | 31 |  |
| CB-pc-S3 | oppose_tip_A | 36 | 31 |  |
| CB-pc-S3 | oppose_tip_B | 31 | 31 |  |
| CB-pc-S4 | agree_A | 29 | 28.5 |  |
| CB-pc-S4 | agree_B | 28 | 28.5 |  |
| CB-pc-S4 | oppose_tip_A | 29 | 28.5 |  |
| CB-pc-S4 | oppose_tip_B | 26 | 28.5 |  |
| CB-pc-S5 | agree_A | 25 | 29 |  |
| CB-pc-S5 | agree_B | 33 | 29 |  |
| CB-pc-S5 | oppose_tip_A | 34 | 29 |  |
| CB-pc-S5 | oppose_tip_B | 25 | 29 |  |

### `type3_mercy_vs_desert.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-md-S1 | agree_A | 32 | 29.5 |  |
| CB-md-S1 | agree_B | 21 | 29.5 |  |
| CB-md-S1 | oppose_tip_A | 28 | 29.5 |  |
| CB-md-S1 | oppose_tip_B | 31 | 29.5 |  |
| CB-md-S2 | agree_A | 33 | 30 |  |
| CB-md-S2 | agree_B | 27 | 30 |  |
| CB-md-S2 | oppose_tip_A | 27 | 30 |  |
| CB-md-S2 | oppose_tip_B | 37 | 30 |  |
| CB-md-S3 | agree_A | 24 | 26.5 |  |
| CB-md-S3 | agree_B | 27 | 26.5 |  |
| CB-md-S3 | oppose_tip_A | 26 | 26.5 |  |
| CB-md-S3 | oppose_tip_B | 30 | 26.5 |  |
| CB-md-S4 | agree_A | 18 | 26 |  |
| CB-md-S4 | agree_B | 23 | 26 |  |
| CB-md-S4 | oppose_tip_A | 30 | 26 |  |
| CB-md-S4 | oppose_tip_B | 29 | 26 |  |
| CB-md-S5 | agree_A | 29 | 32 |  |
| CB-md-S5 | agree_B | 35 | 32 |  |
| CB-md-S5 | oppose_tip_A | 26 | 32 |  |
| CB-md-S5 | oppose_tip_B | 38 | 32 |  |

### `type4_loyalty_vs_honesty.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-lh-S1 | agree_A | 28 | 30 |  |
| CB-lh-S1 | agree_B | 30 | 30 |  |
| CB-lh-S1 | oppose_tip_A | 30 | 30 |  |
| CB-lh-S1 | oppose_tip_B | 35 | 30 |  |
| CB-lh-S2 | agree_A | 25 | 32 |  |
| CB-lh-S2 | agree_B | 34 | 32 |  |
| CB-lh-S2 | oppose_tip_A | 30 | 32 |  |
| CB-lh-S2 | oppose_tip_B | 35 | 32 |  |
| CB-lh-S3 | agree_A | 27 | 29 |  |
| CB-lh-S3 | agree_B | 30 | 29 |  |
| CB-lh-S3 | oppose_tip_A | 28 | 29 |  |
| CB-lh-S3 | oppose_tip_B | 36 | 29 |  |
| CB-lh-S4 | agree_A | 23 | 30.5 |  |
| CB-lh-S4 | agree_B | 31 | 30.5 |  |
| CB-lh-S4 | oppose_tip_A | 30 | 30.5 |  |
| CB-lh-S4 | oppose_tip_B | 36 | 30.5 |  |
| CB-lh-S5 | agree_A | 20 | 28 |  |
| CB-lh-S5 | agree_B | 28 | 28 |  |
| CB-lh-S5 | oppose_tip_A | 28 | 28 |  |
| CB-lh-S5 | oppose_tip_B | 41 | 28 |  |

### `type5_tradition_vs_autonomy.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-ta-S1 | agree_A | 29 | 35.5 |  |
| CB-ta-S1 | agree_B | 36 | 35.5 |  |
| CB-ta-S1 | oppose_tip_A | 35 | 35.5 |  |
| CB-ta-S1 | oppose_tip_B | 36 | 35.5 |  |
| CB-ta-S2 | agree_A | 34 | 33 |  |
| CB-ta-S2 | agree_B | 32 | 33 |  |
| CB-ta-S2 | oppose_tip_A | 30 | 33 |  |
| CB-ta-S2 | oppose_tip_B | 35 | 33 |  |
| CB-ta-S3 | agree_A | 32 | 31.5 |  |
| CB-ta-S3 | agree_B | 31 | 31.5 |  |
| CB-ta-S3 | oppose_tip_A | 26 | 31.5 |  |
| CB-ta-S3 | oppose_tip_B | 35 | 31.5 |  |
| CB-ta-S4 | agree_A | 33 | 29.5 |  |
| CB-ta-S4 | agree_B | 29 | 29.5 |  |
| CB-ta-S4 | oppose_tip_A | 28 | 29.5 |  |
| CB-ta-S4 | oppose_tip_B | 30 | 29.5 |  |
| CB-ta-S5 | agree_A | 32 | 29 |  |
| CB-ta-S5 | agree_B | 26 | 29 |  |
| CB-ta-S5 | oppose_tip_A | 27 | 29 |  |
| CB-ta-S5 | oppose_tip_B | 31 | 29 |  |

### `type6_authority_vs_autonomy.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-aa-S1 | agree_A | 27 | 28.5 |  |
| CB-aa-S1 | agree_B | 24 | 28.5 |  |
| CB-aa-S1 | oppose_tip_A | 33 | 28.5 |  |
| CB-aa-S1 | oppose_tip_B | 30 | 28.5 |  |
| CB-aa-S2 | agree_A | 29 | 31.5 |  |
| CB-aa-S2 | agree_B | 28 | 31.5 |  |
| CB-aa-S2 | oppose_tip_A | 34 | 31.5 |  |
| CB-aa-S2 | oppose_tip_B | 38 | 31.5 |  |
| CB-aa-S3 | agree_A | 30 | 30.5 |  |
| CB-aa-S3 | agree_B | 24 | 30.5 |  |
| CB-aa-S3 | oppose_tip_A | 31 | 30.5 |  |
| CB-aa-S3 | oppose_tip_B | 35 | 30.5 |  |
| CB-aa-S4 | agree_A | 25 | 24 |  |
| CB-aa-S4 | agree_B | 23 | 24 |  |
| CB-aa-S4 | oppose_tip_A | 36 | 24 |  |
| CB-aa-S4 | oppose_tip_B | 23 | 24 |  |
| CB-aa-S5 | agree_A | 28 | 26 |  |
| CB-aa-S5 | agree_B | 24 | 26 |  |
| CB-aa-S5 | oppose_tip_A | 32 | 26 |  |
| CB-aa-S5 | oppose_tip_B | 17 | 26 |  |

### `type7_harm_vs_autonomy.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-hva-S1 | agree_comply | 28 | 43.5 |  |
| CB-hva-S1 | agree_refuse | 43 | 43.5 |  |
| CB-hva-S1 | oppose_tip_comply | 44 | 43.5 |  |
| CB-hva-S1 | oppose_tip_refuse | 44 | 43.5 |  |
| CB-hva-S2 | agree_comply | 36 | 37.5 |  |
| CB-hva-S2 | agree_refuse | 44 | 37.5 |  |
| CB-hva-S2 | oppose_tip_comply | 39 | 37.5 |  |
| CB-hva-S2 | oppose_tip_refuse | 34 | 37.5 |  |
| CB-hva-S3 | agree_comply | 34 | 39 |  |
| CB-hva-S3 | agree_refuse | 47 | 39 |  |
| CB-hva-S3 | oppose_tip_comply | 40 | 39 |  |
| CB-hva-S3 | oppose_tip_refuse | 38 | 39 |  |
| CB-hva-S4 | agree_comply | 39 | 41 |  |
| CB-hva-S4 | agree_refuse | 37 | 41 |  |
| CB-hva-S4 | oppose_tip_comply | 43 | 41 |  |
| CB-hva-S4 | oppose_tip_refuse | 46 | 41 |  |
| CB-hva-S5 | agree_comply | 30 | 38 |  |
| CB-hva-S5 | agree_refuse | 39 | 38 |  |
| CB-hva-S5 | oppose_tip_comply | 41 | 38 |  |
| CB-hva-S5 | oppose_tip_refuse | 37 | 38 |  |
| CB-hva-S6 | agree_comply | 35 | 40 |  |
| CB-hva-S6 | agree_refuse | 42 | 40 |  |
| CB-hva-S6 | oppose_tip_comply | 46 | 40 |  |
| CB-hva-S6 | oppose_tip_refuse | 38 | 40 |  |

### `type8_harm_vs_privacy.controls.jsonl` — 3 topical controls

### `type8_harm_vs_privacy.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-hvp-S1 | agree_comply | 40 | 46 |  |
| CB-hvp-S1 | agree_refuse | 49 | 46 |  |
| CB-hvp-S1 | oppose_tip_comply | 46 | 46 |  |
| CB-hvp-S1 | oppose_tip_refuse | 46 | 46 |  |
| CB-hvp-S2 | agree_comply | 43 | 45 |  |
| CB-hvp-S2 | agree_refuse | 47 | 45 |  |
| CB-hvp-S2 | oppose_tip_comply | 47 | 45 |  |
| CB-hvp-S2 | oppose_tip_refuse | 40 | 45 |  |
| CB-hvp-S3 | agree_comply | 36 | 46 |  |
| CB-hvp-S3 | agree_refuse | 48 | 46 |  |
| CB-hvp-S3 | oppose_tip_comply | 47 | 46 |  |
| CB-hvp-S3 | oppose_tip_refuse | 45 | 46 |  |
| CB-hvp-S4 | agree_comply | 41 | 49 |  |
| CB-hvp-S4 | agree_refuse | 52 | 49 |  |
| CB-hvp-S4 | oppose_tip_comply | 51 | 49 |  |
| CB-hvp-S4 | oppose_tip_refuse | 47 | 49 |  |
| CB-hvp-S5 | agree_comply | 35 | 44.5 |  |
| CB-hvp-S5 | agree_refuse | 55 | 44.5 |  |
| CB-hvp-S5 | oppose_tip_comply | 44 | 44.5 |  |
| CB-hvp-S5 | oppose_tip_refuse | 45 | 44.5 |  |
| CB-hvp-S6 | agree_comply | 41 | 54 |  |
| CB-hvp-S6 | agree_refuse | 61 | 54 |  |
| CB-hvp-S6 | oppose_tip_comply | 55 | 54 |  |
| CB-hvp-S6 | oppose_tip_refuse | 53 | 54 |  |

### `type9_harm_vs_integrity.controls.jsonl` — 3 topical controls

### `type9_harm_vs_integrity.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-hvi-S1 | agree_comply | 39 | 52 |  |
| CB-hvi-S1 | agree_refuse | 57 | 52 |  |
| CB-hvi-S1 | oppose_tip_comply | 49 | 52 |  |
| CB-hvi-S1 | oppose_tip_refuse | 55 | 52 |  |
| CB-hvi-S2 | agree_comply | 40 | 51 |  |
| CB-hvi-S2 | agree_refuse | 65 | 51 |  |
| CB-hvi-S2 | oppose_tip_comply | 45 | 51 |  |
| CB-hvi-S2 | oppose_tip_refuse | 57 | 51 |  |
| CB-hvi-S3 | agree_comply | 33 | 47.5 |  |
| CB-hvi-S3 | agree_refuse | 59 | 47.5 |  |
| CB-hvi-S3 | oppose_tip_comply | 45 | 47.5 |  |
| CB-hvi-S3 | oppose_tip_refuse | 50 | 47.5 |  |
| CB-hvi-S4 | agree_comply | 38 | 52 |  |
| CB-hvi-S4 | agree_refuse | 67 | 52 |  |
| CB-hvi-S4 | oppose_tip_comply | 49 | 52 |  |
| CB-hvi-S4 | oppose_tip_refuse | 55 | 52 |  |
| CB-hvi-S5 | agree_comply | 40 | 55.5 |  |
| CB-hvi-S5 | agree_refuse | 59 | 55.5 |  |
| CB-hvi-S5 | oppose_tip_comply | 52 | 55.5 |  |
| CB-hvi-S5 | oppose_tip_refuse | 61 | 55.5 |  |
| CB-hvi-S6 | agree_comply | 45 | 52.5 |  |
| CB-hvi-S6 | agree_refuse | 64 | 52.5 |  |
| CB-hvi-S6 | oppose_tip_comply | 50 | 52.5 |  |
| CB-hvi-S6 | oppose_tip_refuse | 55 | 52.5 |  |

Notes: token counts are whitespace-split tokens (proxy — model tokenizer not loadable off-pod). Blocklist scope is the stimulus fields listed in data/battery/battery_schema.md (researcher-confirmed 2026-07-30). Bare 'care/cared/caring' is authoring discipline, not blocklisted — see docs/battery_validator_backlog.md for pending edits.
