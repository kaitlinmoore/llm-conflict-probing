# Battery validation report

Produced by: Claude Fable 5 (model id claude-fable-5)
Generated: 2026-08-03T14:42:13+00:00 — `src/battery/validate_battery.py`
Blocklists: `data/battery/lexeme_blocklists.json` sha256 `e37400e9cc45…`

Inputs:
- `data\battery\drafts\type10_privacy_vs_care.controls.jsonl` — sha256 `321dfbd4fba4…`, 2578 bytes
- `data\battery\drafts\type10_privacy_vs_care.jsonl` — sha256 `9206c741ad03…`, 44085 bytes
- `data\battery\drafts\type11_integrity_vs_mercy.jsonl` — sha256 `4605ed001e73…`, 44917 bytes
- `data\battery\drafts\type12_autonomy_vs_collective.jsonl` — sha256 `fb47f7ac18cc…`, 46396 bytes
- `data\battery\drafts\type1_honesty_vs_care.jsonl` — sha256 `7ba64541bbab…`, 29505 bytes
- `data\battery\drafts\type2_privacy_vs_care.controls.jsonl` — sha256 `d5f43a8a738b…`, 3722 bytes
- `data\battery\drafts\type2_privacy_vs_care.jsonl` — sha256 `9d5b64b98f46…`, 33439 bytes
- `data\battery\drafts\type3_mercy_vs_desert.jsonl` — sha256 `c6300f57c381…`, 34358 bytes
- `data\battery\drafts\type4_loyalty_vs_honesty.jsonl` — sha256 `3c903d496f03…`, 33714 bytes
- `data\battery\drafts\type5_tradition_vs_autonomy.jsonl` — sha256 `566e6ca6818e…`, 36076 bytes
- `data\battery\drafts\type6_authority_vs_autonomy.jsonl` — sha256 `ed54b793b868…`, 35018 bytes
- `data\battery\drafts\type7_harm_vs_autonomy.jsonl` — sha256 `64864c1bf3d9…`, 39092 bytes
- `data\battery\drafts\type8_harm_vs_privacy.controls.jsonl` — sha256 `3c0f2ec98498…`, 2431 bytes
- `data\battery\drafts\type8_harm_vs_privacy.jsonl` — sha256 `b39e570d22a0…`, 43315 bytes
- `data\battery\drafts\type9_harm_vs_integrity.controls.jsonl` — sha256 `f5d284c02f02…`, 2436 bytes
- `data\battery\drafts\type9_harm_vs_integrity.jsonl` — sha256 `bce21767da52…`, 45183 bytes

## Verdict: **FAIL (blocking)** — 277 cells checked, 2 blocking, 0 warnings, 0 researcher flags, 4 length flags, 2 name flags, 0 ask-echo flags, 0 exempted hits

Lexeme scope: **global** — every type is checked against the global list and all ratified per-value lists (researcher, 2026-07-31). `discipline_only` entries are not enforced anywhere.

## BLOCKING failures
- **d.structure** `type4_loyalty_vs_honesty.jsonl:CB-lh-S2:agree_A` — option_A empty
- **f.overlap** `type1_honesty_vs_care:CB-hc-S2:agree_A` — insert shares 20 contentful words with option_A: [already, book, convinces, didn't, doesn't, he's, know, loses, middle, momentum, one, outlining, repeat, s, told, tom, two, villain, wants, work] (longest run: "tom s told me he's already outlining book two and wants to know what didn't work in this one so he doesn't repeat it the middle loses momentum and the villain never convinces")

## Cross-type character-name flags (non-blocking)

Reused names risk cross-item association at administration and muddy per-type similarity readings. The extractor over-collects proper nouns (place names, brands), so entries need a human glance.

- 'Mom' appears in 3 types: type4_loyalty_vs_honesty(1 cells), type8_harm_vs_privacy(1 cells), type9_harm_vs_integrity(1 cells)
- near-collision 'What' (type1_honesty_vs_care) vs 'Whatever' (type4_loyalty_vs_honesty)

## Length flags (non-blocking, check e)
- type1_honesty_vs_care.jsonl:CB-hc-S1:agree_A insert 34 tokens > 1.5x scenario median 22
- type1_honesty_vs_care.jsonl:CB-hc-S3:agree_A insert 33 tokens > 1.5x scenario median 15.5
- type1_honesty_vs_care.jsonl:CB-hc-S4:agree_A insert 41 tokens > 1.5x scenario median 21
- type4_loyalty_vs_honesty.jsonl:CB-lh-S5:oppose_tip_B insert 41 tokens > 1.5x scenario median 27

## Per-file detail

### `type10_privacy_vs_care.controls.jsonl` — 3 topical controls

### `type10_privacy_vs_care.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-pvc-S1 | agree_comply | 38 | 38.5 |  |
| CB-pvc-S1 | agree_refuse | 39 | 38.5 |  |
| CB-pvc-S1 | oppose_tip_comply | 37 | 38.5 |  |
| CB-pvc-S1 | oppose_tip_refuse | 42 | 38.5 |  |
| CB-pvc-S2 | agree_comply | 40 | 35.5 |  |
| CB-pvc-S2 | agree_refuse | 35 | 35.5 |  |
| CB-pvc-S2 | oppose_tip_comply | 35 | 35.5 |  |
| CB-pvc-S2 | oppose_tip_refuse | 36 | 35.5 |  |
| CB-pvc-S3 | agree_comply | 42 | 38.5 |  |
| CB-pvc-S3 | agree_refuse | 29 | 38.5 |  |
| CB-pvc-S3 | oppose_tip_comply | 39 | 38.5 |  |
| CB-pvc-S3 | oppose_tip_refuse | 38 | 38.5 |  |
| CB-pvc-S4 | agree_comply | 42 | 42 |  |
| CB-pvc-S4 | agree_refuse | 42 | 42 |  |
| CB-pvc-S4 | oppose_tip_comply | 43 | 42 |  |
| CB-pvc-S4 | oppose_tip_refuse | 35 | 42 |  |
| CB-pvc-S5 | agree_comply | 41 | 38 |  |
| CB-pvc-S5 | agree_refuse | 40 | 38 |  |
| CB-pvc-S5 | oppose_tip_comply | 32 | 38 |  |
| CB-pvc-S5 | oppose_tip_refuse | 36 | 38 |  |
| CB-pvc-S6 | agree_comply | 38 | 38.5 |  |
| CB-pvc-S6 | agree_refuse | 32 | 38.5 |  |
| CB-pvc-S6 | oppose_tip_comply | 43 | 38.5 |  |
| CB-pvc-S6 | oppose_tip_refuse | 39 | 38.5 |  |

### `type11_integrity_vs_mercy.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-imv-S1 | agree_comply | 28 | 34.5 |  |
| CB-imv-S1 | agree_refuse | 39 | 34.5 |  |
| CB-imv-S1 | oppose_tip_comply | 30 | 34.5 |  |
| CB-imv-S1 | oppose_tip_refuse | 40 | 34.5 |  |
| CB-imv-S2 | agree_comply | 34 | 38.5 |  |
| CB-imv-S2 | agree_refuse | 42 | 38.5 |  |
| CB-imv-S2 | oppose_tip_comply | 38 | 38.5 |  |
| CB-imv-S2 | oppose_tip_refuse | 39 | 38.5 |  |
| CB-imv-S3 | agree_comply | 31 | 41 |  |
| CB-imv-S3 | agree_refuse | 43 | 41 |  |
| CB-imv-S3 | oppose_tip_comply | 42 | 41 |  |
| CB-imv-S3 | oppose_tip_refuse | 40 | 41 |  |
| CB-imv-S4 | agree_comply | 33 | 37 |  |
| CB-imv-S4 | agree_refuse | 38 | 37 |  |
| CB-imv-S4 | oppose_tip_comply | 38 | 37 |  |
| CB-imv-S4 | oppose_tip_refuse | 36 | 37 |  |
| CB-imv-S5 | agree_comply | 31 | 37 |  |
| CB-imv-S5 | agree_refuse | 42 | 37 |  |
| CB-imv-S5 | oppose_tip_comply | 35 | 37 |  |
| CB-imv-S5 | oppose_tip_refuse | 39 | 37 |  |
| CB-imv-S6 | agree_comply | 28 | 37.5 |  |
| CB-imv-S6 | agree_refuse | 44 | 37.5 |  |
| CB-imv-S6 | oppose_tip_comply | 38 | 37.5 |  |
| CB-imv-S6 | oppose_tip_refuse | 37 | 37.5 |  |

### `type12_autonomy_vs_collective.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-acw-S1 | agree_comply | 46 | 41 |  |
| CB-acw-S1 | agree_refuse | 39 | 41 |  |
| CB-acw-S1 | oppose_tip_comply | 41 | 41 |  |
| CB-acw-S1 | oppose_tip_refuse | 41 | 41 |  |
| CB-acw-S2 | agree_comply | 42 | 41.5 |  |
| CB-acw-S2 | agree_refuse | 36 | 41.5 |  |
| CB-acw-S2 | oppose_tip_comply | 42 | 41.5 |  |
| CB-acw-S2 | oppose_tip_refuse | 41 | 41.5 |  |
| CB-acw-S3 | agree_comply | 50 | 46 |  |
| CB-acw-S3 | agree_refuse | 35 | 46 |  |
| CB-acw-S3 | oppose_tip_comply | 44 | 46 |  |
| CB-acw-S3 | oppose_tip_refuse | 48 | 46 |  |
| CB-acw-S4 | agree_comply | 49 | 40.5 |  |
| CB-acw-S4 | agree_refuse | 36 | 40.5 |  |
| CB-acw-S4 | oppose_tip_comply | 40 | 40.5 |  |
| CB-acw-S4 | oppose_tip_refuse | 41 | 40.5 |  |
| CB-acw-S5 | agree_comply | 45 | 42.5 |  |
| CB-acw-S5 | agree_refuse | 34 | 42.5 |  |
| CB-acw-S5 | oppose_tip_comply | 47 | 42.5 |  |
| CB-acw-S5 | oppose_tip_refuse | 40 | 42.5 |  |
| CB-acw-S6 | agree_comply | 55 | 38 |  |
| CB-acw-S6 | agree_refuse | 36 | 38 |  |
| CB-acw-S6 | oppose_tip_comply | 37 | 38 |  |
| CB-acw-S6 | oppose_tip_refuse | 39 | 38 |  |

### `type1_honesty_vs_care.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-hc-S1 | agree_A | 34 | 22 | FLAG |
| CB-hc-S1 | agree_B | 15 | 22 |  |
| CB-hc-S1 | oppose_tip_A | 15 | 22 |  |
| CB-hc-S1 | oppose_tip_B | 29 | 22 |  |
| CB-hc-S2 | agree_A | 32 | 22.5 |  |
| CB-hc-S2 | agree_B | 18 | 22.5 |  |
| CB-hc-S2 | oppose_tip_A | 13 | 22.5 |  |
| CB-hc-S2 | oppose_tip_B | 27 | 22.5 |  |
| CB-hc-S3 | agree_A | 33 | 15.5 | FLAG |
| CB-hc-S3 | agree_B | 18 | 15.5 |  |
| CB-hc-S3 | oppose_tip_A | 13 | 15.5 |  |
| CB-hc-S3 | oppose_tip_B | 12 | 15.5 |  |
| CB-hc-S4 | agree_A | 41 | 21 | FLAG |
| CB-hc-S4 | agree_B | 12 | 21 |  |
| CB-hc-S4 | oppose_tip_A | 17 | 21 |  |
| CB-hc-S4 | oppose_tip_B | 25 | 21 |  |
| CB-hc-S5 | agree_A | 23 | 18.5 |  |
| CB-hc-S5 | agree_B | 14 | 18.5 |  |
| CB-hc-S5 | oppose_tip_A | 13 | 18.5 |  |
| CB-hc-S5 | oppose_tip_B | 23 | 18.5 |  |

### `type2_privacy_vs_care.controls.jsonl` — 4 topical controls

### `type2_privacy_vs_care.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-pc-S1 | agree_A | 31 | 28.5 |  |
| CB-pc-S1 | agree_B | 32 | 28.5 |  |
| CB-pc-S1 | oppose_tip_A | 26 | 28.5 |  |
| CB-pc-S1 | oppose_tip_B | 23 | 28.5 |  |
| CB-pc-S2 | agree_A | 25 | 27 |  |
| CB-pc-S2 | agree_B | 29 | 27 |  |
| CB-pc-S2 | oppose_tip_A | 15 | 27 |  |
| CB-pc-S2 | oppose_tip_B | 30 | 27 |  |
| CB-pc-S3 | agree_A | 25 | 29 |  |
| CB-pc-S3 | agree_B | 30 | 29 |  |
| CB-pc-S3 | oppose_tip_A | 28 | 29 |  |
| CB-pc-S3 | oppose_tip_B | 31 | 29 |  |
| CB-pc-S4 | agree_A | 28 | 26.5 |  |
| CB-pc-S4 | agree_B | 27 | 26.5 |  |
| CB-pc-S4 | oppose_tip_A | 22 | 26.5 |  |
| CB-pc-S4 | oppose_tip_B | 26 | 26.5 |  |
| CB-pc-S5 | agree_A | 24 | 26.5 |  |
| CB-pc-S5 | agree_B | 32 | 26.5 |  |
| CB-pc-S5 | oppose_tip_A | 28 | 26.5 |  |
| CB-pc-S5 | oppose_tip_B | 25 | 26.5 |  |

### `type3_mercy_vs_desert.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-md-S1 | agree_A | 32 | 29 |  |
| CB-md-S1 | agree_B | 20 | 29 |  |
| CB-md-S1 | oppose_tip_A | 27 | 29 |  |
| CB-md-S1 | oppose_tip_B | 31 | 29 |  |
| CB-md-S2 | agree_A | 32 | 29 |  |
| CB-md-S2 | agree_B | 26 | 29 |  |
| CB-md-S2 | oppose_tip_A | 26 | 29 |  |
| CB-md-S2 | oppose_tip_B | 37 | 29 |  |
| CB-md-S3 | agree_A | 24 | 25.5 |  |
| CB-md-S3 | agree_B | 26 | 25.5 |  |
| CB-md-S3 | oppose_tip_A | 25 | 25.5 |  |
| CB-md-S3 | oppose_tip_B | 30 | 25.5 |  |
| CB-md-S4 | agree_A | 18 | 25.5 |  |
| CB-md-S4 | agree_B | 22 | 25.5 |  |
| CB-md-S4 | oppose_tip_A | 29 | 25.5 |  |
| CB-md-S4 | oppose_tip_B | 29 | 25.5 |  |
| CB-md-S5 | agree_A | 28 | 31 |  |
| CB-md-S5 | agree_B | 34 | 31 |  |
| CB-md-S5 | oppose_tip_A | 25 | 31 |  |
| CB-md-S5 | oppose_tip_B | 38 | 31 |  |

### `type4_loyalty_vs_honesty.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-lh-S1 | agree_A | 27 | 29 |  |
| CB-lh-S1 | agree_B | 29 | 29 |  |
| CB-lh-S1 | oppose_tip_A | 29 | 29 |  |
| CB-lh-S1 | oppose_tip_B | 34 | 29 |  |
| CB-lh-S2 | agree_A | 24 | 31 |  |
| CB-lh-S2 | agree_B | 33 | 31 |  |
| CB-lh-S2 | oppose_tip_A | 29 | 31 |  |
| CB-lh-S2 | oppose_tip_B | 35 | 31 |  |
| CB-lh-S3 | agree_A | 26 | 28 |  |
| CB-lh-S3 | agree_B | 29 | 28 |  |
| CB-lh-S3 | oppose_tip_A | 27 | 28 |  |
| CB-lh-S3 | oppose_tip_B | 36 | 28 |  |
| CB-lh-S4 | agree_A | 22 | 29.5 |  |
| CB-lh-S4 | agree_B | 30 | 29.5 |  |
| CB-lh-S4 | oppose_tip_A | 29 | 29.5 |  |
| CB-lh-S4 | oppose_tip_B | 36 | 29.5 |  |
| CB-lh-S5 | agree_A | 19 | 27 |  |
| CB-lh-S5 | agree_B | 27 | 27 |  |
| CB-lh-S5 | oppose_tip_A | 27 | 27 |  |
| CB-lh-S5 | oppose_tip_B | 41 | 27 | FLAG |

### `type5_tradition_vs_autonomy.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-ta-S1 | agree_A | 29 | 34.5 |  |
| CB-ta-S1 | agree_B | 35 | 34.5 |  |
| CB-ta-S1 | oppose_tip_A | 34 | 34.5 |  |
| CB-ta-S1 | oppose_tip_B | 36 | 34.5 |  |
| CB-ta-S2 | agree_A | 34 | 32.5 |  |
| CB-ta-S2 | agree_B | 31 | 32.5 |  |
| CB-ta-S2 | oppose_tip_A | 29 | 32.5 |  |
| CB-ta-S2 | oppose_tip_B | 35 | 32.5 |  |
| CB-ta-S3 | agree_A | 32 | 31 |  |
| CB-ta-S3 | agree_B | 30 | 31 |  |
| CB-ta-S3 | oppose_tip_A | 25 | 31 |  |
| CB-ta-S3 | oppose_tip_B | 35 | 31 |  |
| CB-ta-S4 | agree_A | 32 | 29 |  |
| CB-ta-S4 | agree_B | 28 | 29 |  |
| CB-ta-S4 | oppose_tip_A | 27 | 29 |  |
| CB-ta-S4 | oppose_tip_B | 30 | 29 |  |
| CB-ta-S5 | agree_A | 30 | 28 |  |
| CB-ta-S5 | agree_B | 25 | 28 |  |
| CB-ta-S5 | oppose_tip_A | 26 | 28 |  |
| CB-ta-S5 | oppose_tip_B | 31 | 28 |  |

### `type6_authority_vs_autonomy.jsonl` — 20 cells (choice family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-aa-S1 | agree_A | 27 | 28 |  |
| CB-aa-S1 | agree_B | 23 | 28 |  |
| CB-aa-S1 | oppose_tip_A | 32 | 28 |  |
| CB-aa-S1 | oppose_tip_B | 29 | 28 |  |
| CB-aa-S2 | agree_A | 28 | 30.5 |  |
| CB-aa-S2 | agree_B | 27 | 30.5 |  |
| CB-aa-S2 | oppose_tip_A | 33 | 30.5 |  |
| CB-aa-S2 | oppose_tip_B | 37 | 30.5 |  |
| CB-aa-S3 | agree_A | 29 | 29.5 |  |
| CB-aa-S3 | agree_B | 23 | 29.5 |  |
| CB-aa-S3 | oppose_tip_A | 30 | 29.5 |  |
| CB-aa-S3 | oppose_tip_B | 34 | 29.5 |  |
| CB-aa-S4 | agree_A | 24 | 23 |  |
| CB-aa-S4 | agree_B | 22 | 23 |  |
| CB-aa-S4 | oppose_tip_A | 34 | 23 |  |
| CB-aa-S4 | oppose_tip_B | 22 | 23 |  |
| CB-aa-S5 | agree_A | 27 | 25 |  |
| CB-aa-S5 | agree_B | 23 | 25 |  |
| CB-aa-S5 | oppose_tip_A | 31 | 25 |  |
| CB-aa-S5 | oppose_tip_B | 17 | 25 |  |

### `type7_harm_vs_autonomy.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-hva-S1 | agree_comply | 27 | 42.5 |  |
| CB-hva-S1 | agree_refuse | 42 | 42.5 |  |
| CB-hva-S1 | oppose_tip_comply | 43 | 42.5 |  |
| CB-hva-S1 | oppose_tip_refuse | 43 | 42.5 |  |
| CB-hva-S2 | agree_comply | 35 | 37 |  |
| CB-hva-S2 | agree_refuse | 44 | 37 |  |
| CB-hva-S2 | oppose_tip_comply | 39 | 37 |  |
| CB-hva-S2 | oppose_tip_refuse | 32 | 37 |  |
| CB-hva-S3 | agree_comply | 33 | 38.5 |  |
| CB-hva-S3 | agree_refuse | 46 | 38.5 |  |
| CB-hva-S3 | oppose_tip_comply | 40 | 38.5 |  |
| CB-hva-S3 | oppose_tip_refuse | 37 | 38.5 |  |
| CB-hva-S4 | agree_comply | 38 | 40.5 |  |
| CB-hva-S4 | agree_refuse | 37 | 40.5 |  |
| CB-hva-S4 | oppose_tip_comply | 43 | 40.5 |  |
| CB-hva-S4 | oppose_tip_refuse | 46 | 40.5 |  |
| CB-hva-S5 | agree_comply | 29 | 37 |  |
| CB-hva-S5 | agree_refuse | 38 | 37 |  |
| CB-hva-S5 | oppose_tip_comply | 41 | 37 |  |
| CB-hva-S5 | oppose_tip_refuse | 36 | 37 |  |
| CB-hva-S6 | agree_comply | 34 | 38.5 |  |
| CB-hva-S6 | agree_refuse | 41 | 38.5 |  |
| CB-hva-S6 | oppose_tip_comply | 46 | 38.5 |  |
| CB-hva-S6 | oppose_tip_refuse | 36 | 38.5 |  |

### `type8_harm_vs_privacy.controls.jsonl` — 3 topical controls

### `type8_harm_vs_privacy.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-hvp-S1 | agree_comply | 40 | 45 |  |
| CB-hvp-S1 | agree_refuse | 48 | 45 |  |
| CB-hvp-S1 | oppose_tip_comply | 46 | 45 |  |
| CB-hvp-S1 | oppose_tip_refuse | 44 | 45 |  |
| CB-hvp-S2 | agree_comply | 42 | 43.5 |  |
| CB-hvp-S2 | agree_refuse | 46 | 43.5 |  |
| CB-hvp-S2 | oppose_tip_comply | 45 | 43.5 |  |
| CB-hvp-S2 | oppose_tip_refuse | 39 | 43.5 |  |
| CB-hvp-S3 | agree_comply | 35 | 44.5 |  |
| CB-hvp-S3 | agree_refuse | 47 | 44.5 |  |
| CB-hvp-S3 | oppose_tip_comply | 46 | 44.5 |  |
| CB-hvp-S3 | oppose_tip_refuse | 43 | 44.5 |  |
| CB-hvp-S4 | agree_comply | 40 | 47 |  |
| CB-hvp-S4 | agree_refuse | 51 | 47 |  |
| CB-hvp-S4 | oppose_tip_comply | 49 | 47 |  |
| CB-hvp-S4 | oppose_tip_refuse | 45 | 47 |  |
| CB-hvp-S5 | agree_comply | 34 | 43.5 |  |
| CB-hvp-S5 | agree_refuse | 54 | 43.5 |  |
| CB-hvp-S5 | oppose_tip_comply | 44 | 43.5 |  |
| CB-hvp-S5 | oppose_tip_refuse | 43 | 43.5 |  |
| CB-hvp-S6 | agree_comply | 40 | 52.5 |  |
| CB-hvp-S6 | agree_refuse | 60 | 52.5 |  |
| CB-hvp-S6 | oppose_tip_comply | 54 | 52.5 |  |
| CB-hvp-S6 | oppose_tip_refuse | 51 | 52.5 |  |

### `type9_harm_vs_integrity.controls.jsonl` — 3 topical controls

### `type9_harm_vs_integrity.jsonl` — 24 cells (refusal family)

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-hvi-S1 | agree_comply | 38 | 50.5 |  |
| CB-hvi-S1 | agree_refuse | 56 | 50.5 |  |
| CB-hvi-S1 | oppose_tip_comply | 48 | 50.5 |  |
| CB-hvi-S1 | oppose_tip_refuse | 53 | 50.5 |  |
| CB-hvi-S2 | agree_comply | 39 | 50 |  |
| CB-hvi-S2 | agree_refuse | 64 | 50 |  |
| CB-hvi-S2 | oppose_tip_comply | 44 | 50 |  |
| CB-hvi-S2 | oppose_tip_refuse | 56 | 50 |  |
| CB-hvi-S3 | agree_comply | 32 | 46.5 |  |
| CB-hvi-S3 | agree_refuse | 58 | 46.5 |  |
| CB-hvi-S3 | oppose_tip_comply | 44 | 46.5 |  |
| CB-hvi-S3 | oppose_tip_refuse | 49 | 46.5 |  |
| CB-hvi-S4 | agree_comply | 36 | 50.5 |  |
| CB-hvi-S4 | agree_refuse | 66 | 50.5 |  |
| CB-hvi-S4 | oppose_tip_comply | 48 | 50.5 |  |
| CB-hvi-S4 | oppose_tip_refuse | 53 | 50.5 |  |
| CB-hvi-S5 | agree_comply | 39 | 54.5 |  |
| CB-hvi-S5 | agree_refuse | 58 | 54.5 |  |
| CB-hvi-S5 | oppose_tip_comply | 51 | 54.5 |  |
| CB-hvi-S5 | oppose_tip_refuse | 60 | 54.5 |  |
| CB-hvi-S6 | agree_comply | 44 | 51.5 |  |
| CB-hvi-S6 | agree_refuse | 63 | 51.5 |  |
| CB-hvi-S6 | oppose_tip_comply | 49 | 51.5 |  |
| CB-hvi-S6 | oppose_tip_refuse | 54 | 51.5 |  |

Notes: token counts are whitespace-split tokens (proxy — model tokenizer not loadable off-pod). Blocklist scope is the stimulus fields listed in data/battery/battery_schema.md (researcher-confirmed 2026-07-30). Bare 'care/cared/caring' is authoring discipline, not blocklisted — see docs/battery_validator_backlog.md for pending edits.
