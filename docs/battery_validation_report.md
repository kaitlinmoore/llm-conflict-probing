# Battery validation report

Produced by: Claude Fable 5 (model id claude-fable-5)
Generated: 2026-07-30T14:03:14+00:00 — `src/battery/validate_battery.py`
Blocklists: `data/battery/lexeme_blocklists.json` sha256 `3d45e707a171…`

Inputs:
- `data\battery\drafts\type1_honesty_vs_care.jsonl` — sha256 `bd986c4e7f97…`, 28312 bytes
- `data\battery\drafts\type2_privacy_vs_care.controls.jsonl` — sha256 `5ff0c7840624…`, 3326 bytes
- `data\battery\drafts\type2_privacy_vs_care.jsonl` — sha256 `8940aa5209ae…`, 31184 bytes
- `data\battery\drafts\type3_mercy_vs_desert.jsonl` — sha256 `56b777c4ed15…`, 33262 bytes

## Verdict: **PASS** — 64 cells checked, 0 blocking, 0 warnings, 0 researcher flags, 3 length flags

## Length flags (non-blocking, check e)
- type1_honesty_vs_care.jsonl:CB-hc-S1:agree_A insert 35 tokens > 1.5x scenario median 22.5
- type1_honesty_vs_care.jsonl:CB-hc-S3:agree_A insert 33 tokens > 1.5x scenario median 16
- type1_honesty_vs_care.jsonl:CB-hc-S4:agree_A insert 41 tokens > 1.5x scenario median 21

## Per-file detail

### `type1_honesty_vs_care.jsonl` — 20 cells

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

### `type2_privacy_vs_care.jsonl` — 20 cells

| scenario | cell | insert tokens | scenario median | flag |
|---|---|---|---|---|
| CB-pc-S1 | agree_A | 32 | 27 |  |
| CB-pc-S1 | agree_B | 27 | 27 |  |
| CB-pc-S1 | oppose_tip_A | 27 | 27 |  |
| CB-pc-S1 | oppose_tip_B | 23 | 27 |  |
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
| CB-pc-S5 | agree_A | 25 | 28.5 |  |
| CB-pc-S5 | agree_B | 32 | 28.5 |  |
| CB-pc-S5 | oppose_tip_A | 34 | 28.5 |  |
| CB-pc-S5 | oppose_tip_B | 25 | 28.5 |  |

### `type3_mercy_vs_desert.jsonl` — 20 cells

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

Notes: token counts are whitespace-split tokens (proxy — model tokenizer not loadable off-pod). Blocklist scope is the stimulus fields listed in data/battery/battery_schema.md (researcher-confirmed 2026-07-30). Bare 'care/cared/caring' is authoring discipline, not blocklisted — see docs/battery_validator_backlog.md for pending edits.
