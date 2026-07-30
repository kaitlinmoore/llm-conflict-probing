# Value-fingerprint screen — pre-test activations (2026-07)

Produced by: Claude Fable 5 (model id claude-fable-5)
Generated: 2026-07-30T14:03:18+00:00 — `src/analysis/fingerprint_screen.py` -> `results/fingerprint_screen/20260730_140315_llama8b`
Subject model of the underlying data: **meta-llama/Llama-3.1-8B-Instruct** (merged IV run `20260717_204822_llama8b_instrument_validation_merged`, instrument sha256 `659afb97…`).

**This is a screen, not a finding.** The pre-test confounds value with topic by design (each value's probes live in their own scenarios), so similarity here is **suggestive, not diagnostic**. Flags only — no verdicts. Its one actionable output: a flagged pairing that co-occurs in a planned battery tension type deserves reconsideration before that type is authored.

Fingerprint: mean(value-variant) − mean(neutral-twin) anchor activation, per layer (32 layers, d=4096), unit-normalized; 160 eligible cells (choice channel, main block, base cells, complete, non-C3, mass floor 0.2). Split-half by scenario pair, never by role. Provisional defaults (researcher may override): reliable = split-half cosine ≥ 0.5 at the layer in question; flag threshold = cosine ≥ 0.8 × ceiling, ceiling = √(rel_a·rel_b).

## Reliability (existence gate for interpretation)

| value | pairs | splits | best layer | reliability | status |
|---|---|---|---|---|---|
| authority | 3 | 3 | 1 | 0.8583 | RELIABLE |
| autonomy | 5 | 10 | 0 | 0.8727 | RELIABLE |
| care | 4 | 3 | 0 | 0.9125 | RELIABLE |
| collective_welfare | 4 | 3 | 0 | 0.8984 | RELIABLE |
| desert | 5 | 10 | 0 | 0.889 | RELIABLE |
| fairness | 4 | 3 | 0 | 0.9191 | RELIABLE |
| harm_avoidance | 5 | 10 | 0 | 0.9118 | RELIABLE |
| honesty | 3 | 3 | 0 | 0.8735 | RELIABLE |
| impartiality | 2 | 1 | 0 | 0.7971 | RELIABLE |
| integrity | 5 | 10 | 0 | 0.8655 | RELIABLE |
| kindness | 5 | 10 | 0 | 0.8916 | RELIABLE |
| loyalty | 5 | 10 | 0 | 0.9055 | RELIABLE |
| mercy | 5 | 10 | 0 | 0.9259 | RELIABLE |
| privacy | 4 | 3 | 0 | 0.8482 | RELIABLE |
| sanctity | 5 | 10 | 2 | 0.8139 | RELIABLE |
| tradition | 5 | 10 | 0 | 0.9081 | RELIABLE |

## Similarity at best shared-reliability layer

Full per-layer matrices: `similarity_layers.csv`. Pairs involving a NOT-ESTIMABLE value are omitted from interpretation; UNRELIABLE values are shown but not flag-eligible.

| pair | layer | cosine | ceiling | cos/ceiling | battery? | flagged |
|---|---|---|---|---|---|---|
| authority–autonomy | 1 | 0.7447 | 0.8542 | 0.8719 | type6 | **FLAG** |
| authority–care | 1 | 0.7913 | 0.8755 | 0.9038 |  |  |
| authority–collective_welfare | 1 | 0.6658 | 0.8563 | 0.7774 |  |  |
| authority–desert | 1 | 0.7199 | 0.8558 | 0.8412 |  |  |
| authority–fairness | 1 | 0.7812 | 0.8784 | 0.8893 |  |  |
| authority–harm_avoidance | 1 | 0.767 | 0.8774 | 0.8742 |  |  |
| authority–honesty | 0 | 0.8182 | 0.8612 | 0.9501 |  |  |
| authority–impartiality | 0 | 0.74 | 0.8226 | 0.8995 |  |  |
| authority–integrity | 0 | 0.7367 | 0.8572 | 0.8594 |  |  |
| authority–kindness | 1 | 0.7463 | 0.8679 | 0.86 |  |  |
| authority–loyalty | 1 | 0.8133 | 0.8693 | 0.9355 |  |  |
| authority–mercy | 1 | 0.7844 | 0.871 | 0.9006 |  |  |
| authority–privacy | 0 | 0.8063 | 0.8486 | 0.9501 |  |  |
| authority–sanctity | 2 | 0.6657 | 0.8322 | 0.7999 |  |  |
| authority–tradition | 1 | 0.7163 | 0.8767 | 0.8171 |  |  |
| autonomy–care | 0 | 0.935 | 0.8924 | 1.0478 |  |  |
| autonomy–collective_welfare | 0 | 0.8845 | 0.8855 | 0.9989 | type12 | **FLAG** |
| autonomy–desert | 0 | 0.8971 | 0.8808 | 1.0185 |  |  |
| autonomy–fairness | 0 | 0.9017 | 0.8956 | 1.0068 |  |  |
| autonomy–harm_avoidance | 0 | 0.9102 | 0.892 | 1.0203 | type7 | **FLAG** |
| autonomy–honesty | 0 | 0.9206 | 0.8731 | 1.0543 |  |  |
| autonomy–impartiality | 0 | 0.882 | 0.834 | 1.0575 |  |  |
| autonomy–integrity | 0 | 0.835 | 0.8691 | 0.9608 |  |  |
| autonomy–kindness | 0 | 0.9145 | 0.8821 | 1.0367 |  |  |
| autonomy–loyalty | 0 | 0.9089 | 0.8889 | 1.0225 |  |  |
| autonomy–mercy | 0 | 0.9274 | 0.8989 | 1.0317 |  |  |
| autonomy–privacy | 0 | 0.901 | 0.8604 | 1.0472 |  |  |
| autonomy–sanctity | 2 | 0.8691 | 0.8263 | 1.0517 |  |  |
| autonomy–tradition | 0 | 0.8996 | 0.8902 | 1.0105 | type5 | **FLAG** |
| care–collective_welfare | 0 | 0.9219 | 0.9054 | 1.0182 |  |  |
| care–desert | 0 | 0.9251 | 0.9006 | 1.0271 |  |  |
| care–fairness | 0 | 0.9559 | 0.9158 | 1.0438 |  |  |
| care–harm_avoidance | 0 | 0.9509 | 0.9121 | 1.0425 |  |  |
| care–honesty | 0 | 0.9342 | 0.8928 | 1.0464 | type1 | **FLAG** |
| care–impartiality | 0 | 0.9023 | 0.8528 | 1.058 |  |  |
| care–integrity | 0 | 0.8897 | 0.8887 | 1.0012 |  |  |
| care–kindness | 0 | 0.9599 | 0.902 | 1.0642 |  |  |
| care–loyalty | 0 | 0.9442 | 0.909 | 1.0387 |  |  |
| care–mercy | 0 | 0.9282 | 0.9192 | 1.0098 |  |  |
| care–privacy | 0 | 0.9415 | 0.8798 | 1.0701 | type2;type10 | **FLAG** |
| care–sanctity | 2 | 0.832 | 0.8331 | 0.9987 |  |  |
| care–tradition | 0 | 0.941 | 0.9103 | 1.0337 |  |  |
| collective_welfare–desert | 0 | 0.9405 | 0.8937 | 1.0524 |  |  |
| collective_welfare–fairness | 0 | 0.9407 | 0.9087 | 1.0352 |  |  |
| collective_welfare–harm_avoidance | 0 | 0.9223 | 0.9051 | 1.019 |  |  |
| collective_welfare–honesty | 0 | 0.9296 | 0.8859 | 1.0493 |  |  |
| collective_welfare–impartiality | 0 | 0.9296 | 0.8462 | 1.0986 |  |  |
| collective_welfare–integrity | 0 | 0.8953 | 0.8818 | 1.0153 |  |  |
| collective_welfare–kindness | 0 | 0.9236 | 0.895 | 1.0319 |  |  |
| collective_welfare–loyalty | 0 | 0.9191 | 0.902 | 1.0191 |  |  |
| collective_welfare–mercy | 0 | 0.8643 | 0.9121 | 0.9476 |  |  |
| collective_welfare–privacy | 0 | 0.9347 | 0.873 | 1.0707 |  |  |
| collective_welfare–sanctity | 0 | 0.8454 | 0.851 | 0.9933 |  |  |
| collective_welfare–tradition | 0 | 0.9404 | 0.9033 | 1.0411 |  |  |
| desert–fairness | 0 | 0.9341 | 0.9039 | 1.0334 |  |  |
| desert–harm_avoidance | 0 | 0.9106 | 0.9003 | 1.0115 |  |  |
| desert–honesty | 0 | 0.9271 | 0.8812 | 1.052 |  |  |
| desert–impartiality | 0 | 0.9131 | 0.8418 | 1.0847 |  |  |
| desert–integrity | 0 | 0.9107 | 0.8771 | 1.0383 |  |  |
| desert–kindness | 0 | 0.9153 | 0.8903 | 1.0281 |  |  |
| desert–loyalty | 0 | 0.9107 | 0.8972 | 1.0151 |  |  |
| desert–mercy | 0 | 0.8907 | 0.9072 | 0.9818 | type3 | **FLAG** |
| desert–privacy | 0 | 0.9193 | 0.8684 | 1.0587 |  |  |
| desert–sanctity | 0 | 0.8559 | 0.8465 | 1.0111 |  |  |
| desert–tradition | 0 | 0.9322 | 0.8985 | 1.0375 |  |  |
| fairness–harm_avoidance | 0 | 0.9552 | 0.9154 | 1.0435 |  |  |
| fairness–honesty | 0 | 0.9345 | 0.896 | 1.0429 |  |  |
| fairness–impartiality | 0 | 0.9061 | 0.8559 | 1.0586 |  |  |
| fairness–integrity | 0 | 0.8822 | 0.8919 | 0.9891 |  |  |
| fairness–kindness | 0 | 0.9489 | 0.9052 | 1.0483 |  |  |
| fairness–loyalty | 0 | 0.9488 | 0.9122 | 1.0401 |  |  |
| fairness–mercy | 0 | 0.9057 | 0.9225 | 0.9819 |  |  |
| fairness–privacy | 0 | 0.9501 | 0.8829 | 1.0761 |  |  |
| fairness–sanctity | 2 | 0.8787 | 0.835 | 1.0524 |  |  |
| fairness–tradition | 0 | 0.9623 | 0.9136 | 1.0533 |  |  |
| harm_avoidance–honesty | 0 | 0.9379 | 0.8924 | 1.051 |  |  |
| harm_avoidance–impartiality | 0 | 0.8961 | 0.8525 | 1.0512 |  |  |
| harm_avoidance–integrity | 0 | 0.9091 | 0.8883 | 1.0234 | type9 | **FLAG** |
| harm_avoidance–kindness | 0 | 0.9412 | 0.9016 | 1.0439 |  |  |
| harm_avoidance–loyalty | 0 | 0.9461 | 0.9086 | 1.0412 |  |  |
| harm_avoidance–mercy | 0 | 0.9056 | 0.9188 | 0.9857 |  |  |
| harm_avoidance–privacy | 0 | 0.9567 | 0.8794 | 1.0879 | type8 | **FLAG** |
| harm_avoidance–sanctity | 2 | 0.8505 | 0.8422 | 1.0099 |  |  |
| harm_avoidance–tradition | 0 | 0.9615 | 0.9099 | 1.0567 |  |  |
| honesty–impartiality | 0 | 0.9128 | 0.8344 | 1.0939 |  |  |
| honesty–integrity | 0 | 0.8999 | 0.8695 | 1.035 |  |  |
| honesty–kindness | 0 | 0.9241 | 0.8825 | 1.0471 |  |  |
| honesty–loyalty | 0 | 0.9327 | 0.8894 | 1.0487 | type4 | **FLAG** |
| honesty–mercy | 0 | 0.9082 | 0.8993 | 1.0098 |  |  |
| honesty–privacy | 0 | 0.927 | 0.8608 | 1.0769 |  |  |
| honesty–sanctity | 0 | 0.8892 | 0.8391 | 1.0597 |  |  |
| honesty–tradition | 0 | 0.9322 | 0.8906 | 1.0466 |  |  |
| impartiality–integrity | 0 | 0.8736 | 0.8306 | 1.0518 |  |  |
| impartiality–kindness | 0 | 0.9083 | 0.843 | 1.0774 |  |  |
| impartiality–loyalty | 0 | 0.8866 | 0.8496 | 1.0436 |  |  |
| impartiality–mercy | 0 | 0.8445 | 0.8591 | 0.983 |  |  |
| impartiality–privacy | 0 | 0.9173 | 0.8223 | 1.1156 |  |  |
| impartiality–sanctity | 0 | 0.853 | 0.8016 | 1.0641 |  |  |
| impartiality–tradition | 0 | 0.9216 | 0.8508 | 1.0832 |  |  |
| integrity–kindness | 0 | 0.8842 | 0.8785 | 1.0065 |  |  |
| integrity–loyalty | 0 | 0.8771 | 0.8853 | 0.9907 |  |  |
| integrity–mercy | 0 | 0.8429 | 0.8952 | 0.9417 | type11 | **FLAG** |
| integrity–privacy | 0 | 0.9091 | 0.8568 | 1.061 |  |  |
| integrity–sanctity | 2 | 0.7333 | 0.8218 | 0.8923 |  |  |
| integrity–tradition | 0 | 0.9029 | 0.8865 | 1.0185 |  |  |
| kindness–loyalty | 0 | 0.9388 | 0.8985 | 1.0448 |  |  |
| kindness–mercy | 0 | 0.9187 | 0.9086 | 1.0111 |  |  |
| kindness–privacy | 0 | 0.9462 | 0.8697 | 1.088 |  |  |
| kindness–sanctity | 2 | 0.8093 | 0.8186 | 0.9886 |  |  |
| kindness–tradition | 0 | 0.9495 | 0.8998 | 1.0551 |  |  |
| loyalty–mercy | 0 | 0.932 | 0.9156 | 1.0178 |  |  |
| loyalty–privacy | 0 | 0.9398 | 0.8764 | 1.0723 |  |  |
| loyalty–sanctity | 2 | 0.8265 | 0.8204 | 1.0075 |  |  |
| loyalty–tradition | 0 | 0.942 | 0.9068 | 1.0388 |  |  |
| mercy–privacy | 0 | 0.8973 | 0.8862 | 1.0125 |  |  |
| mercy–sanctity | 2 | 0.728 | 0.8401 | 0.8666 |  |  |
| mercy–tradition | 0 | 0.8913 | 0.9169 | 0.972 |  |  |
| privacy–sanctity | 0 | 0.8926 | 0.8269 | 1.0794 |  |  |
| privacy–tradition | 0 | 0.9563 | 0.8777 | 1.0896 |  |  |
| sanctity–tradition | 2 | 0.8716 | 0.8437 | 1.033 |  |  |

## Flag list

- **authority–autonomy** (battery type 6): cosine 0.745 at layer 1 vs ceiling 0.854 (ratio 0.87) — both reliable. Reconsider this pairing before authoring.
- **autonomy–collective_welfare** (battery type 12): cosine 0.885 at layer 0 vs ceiling 0.885 (ratio 1.00) — both reliable. Reconsider this pairing before authoring.
- **autonomy–harm_avoidance** (battery type 7): cosine 0.910 at layer 0 vs ceiling 0.892 (ratio 1.02) — both reliable. Reconsider this pairing before authoring.
- **autonomy–tradition** (battery type 5): cosine 0.900 at layer 0 vs ceiling 0.890 (ratio 1.01) — both reliable. Reconsider this pairing before authoring.
- **care–honesty** (battery type 1): cosine 0.934 at layer 0 vs ceiling 0.893 (ratio 1.05) — both reliable. Reconsider this pairing before authoring.
- **care–privacy** (battery type 2, type 10): cosine 0.941 at layer 0 vs ceiling 0.880 (ratio 1.07) — both reliable. Reconsider this pairing before authoring.
- **desert–mercy** (battery type 3): cosine 0.891 at layer 0 vs ceiling 0.907 (ratio 0.98) — both reliable. Reconsider this pairing before authoring.
- **harm_avoidance–integrity** (battery type 9): cosine 0.909 at layer 0 vs ceiling 0.888 (ratio 1.02) — both reliable. Reconsider this pairing before authoring.
- **harm_avoidance–privacy** (battery type 8): cosine 0.957 at layer 0 vs ceiling 0.879 (ratio 1.09) — both reliable. Reconsider this pairing before authoring.
- **honesty–loyalty** (battery type 4): cosine 0.933 at layer 0 vs ceiling 0.889 (ratio 1.05) — both reliable. Reconsider this pairing before authoring.
- **integrity–mercy** (battery type 11): cosine 0.843 at layer 0 vs ceiling 0.895 (ratio 0.94) — both reliable. Reconsider this pairing before authoring.

Reminder: topic confound (above) — a flag is a prompt to reconsider, a clean screen is not evidence of distinctness.

## Operative reading — layer-12 view (registered by researcher direction, 2026-07-30)

This section is the **operative reading** of the screen; the specced flag list above is retained as the pre-registered computation but is superseded for interpretation. **Criterion defect, documented:** the specced rule reports similarity at the best shared-reliability layer, and every battery pairing flagged there, all at layers 0–2 — where mean cross-value similarity equals median reliability (separation ≈ 0). Early-layer fingerprints are dominated by shared prompt-format variance, which is itself highly split-half reliable: **reliability-max = content-min**, so the criterion selects exactly the layers where the screen cannot discriminate. Value-specific signal is clearest where separation peaks: **layer 12** (median reliability 0.547, mean cross-pair cosine 0.430).

| layer | mean cross-pair cosine | median reliability | separation |
|---|---|---|---|
| 0 | 0.899 | 0.890 | -0.009 |
| 2 | 0.834 | 0.828 | -0.005 |
| 4 | 0.664 | 0.717 | +0.053 |
| 6 | 0.657 | 0.684 | +0.027 |
| 8 | 0.573 | 0.619 | +0.046 |
| 10 | 0.504 | 0.590 | +0.086 |
| 11 | 0.491 | 0.599 | +0.108 |
| 12 | 0.430 | 0.547 | +0.118 |
| 13 | 0.406 | 0.518 | +0.112 |
| 14 | 0.335 | 0.397 | +0.063 |
| 16 | 0.400 | 0.506 | +0.105 |
| 20 | 0.404 | 0.433 | +0.029 |
| 24 | 0.394 | 0.370 | -0.024 |
| 28 | 0.372 | 0.338 | -0.035 |
| 31 | 0.343 | 0.343 | +0.000 |

Battery pairings ranked at layer 12, with each cosine's percentile among all 120 value pairs at that layer (the relative view the saturated flag list cannot give):

| pair | battery type | cosine @L12 | percentile | min split-half rel @L12 |
|---|---|---|---|---|
| care–privacy | type2;type10 | 0.682 | 1.00 | 0.552 |
| harm_avoidance–privacy | type8 | 0.650 | 0.98 | 0.552 |
| harm_avoidance–integrity | type9 | 0.622 | 0.95 | 0.633 |
| care–honesty | type1 | 0.438 | 0.49 | 0.401 |
| autonomy–tradition | type5 | 0.432 | 0.44 | 0.414 |
| autonomy–collective_welfare | type12 | 0.408 | 0.36 | 0.318 |
| honesty–loyalty | type4 | 0.392 | 0.32 | 0.401 |
| autonomy–harm_avoidance | type7 | 0.379 | 0.28 | 0.414 |
| desert–mercy | type3 | 0.358 | 0.23 | 0.484 |
| integrity–mercy | type11 | 0.354 | 0.22 | 0.633 |
| authority–autonomy | type6 | 0.113 | 0.03 | 0.414 |

authority–integrity: cosine 0.207 at layer 12, percentile 0.08 — descriptive only — pairing decision unaffected.

Battery pairings in the top decile of cross-value similarity at the max-separation layer: **care–privacy** (type 2, type 10, cosine 0.682, percentile 1.00); **harm_avoidance–privacy** (type 8, cosine 0.650, percentile 0.98); **harm_avoidance–integrity** (type 9, cosine 0.622, percentile 0.95). Same caveat as everywhere in this screen: the pre-test confounds value with topic, and some of these pairings share topic bridges by design.
