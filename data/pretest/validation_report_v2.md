# Pre-test probe validation report (v2)

Drafts: probe_drafts_v2_tranche1.json, probe_drafts_v2_tranche2a.json, probe_drafts_v2_tranche2b.json  |  Rendered resistance records: 312  |  Rendered choice records: 349  |  Prompt texts: 994  |  allow_partial: False

## Blocking problems

None.

## Warnings (review during curation)
- PT2-harm_avoidance-C4: role_set has 2 roles (spec default is >= 3)
- PT2-privacy-C3: role_set has 2 roles (spec default is >= 3)
- PT2-privacy-C4: role_set has 2 roles (spec default is >= 3)
- PT2-kindness-C2: role_set has 2 roles (spec default is >= 3)
- PT2-kindness-C3: role_set has 2 roles (spec default is >= 3)
- PT2-fairness-C3: role_set has 2 roles (spec default is >= 3)
- PT2-autonomy-C5: role_set has 2 roles (spec default is >= 3)
- PT2-desert-C4: role_set has 2 roles (spec default is >= 3)
- PT2-mercy-C3: role_set has 2 roles (spec default is >= 3)
- PT2-collective_welfare-C1: role_set has 2 roles (spec default is >= 3)
- PT2-authority-R3: role_set has 2 roles (spec default is >= 3)
- PT2-authority-R4: role_set has 2 roles (spec default is >= 3)
- PT2-authority-R5: role_set has 2 roles (spec default is >= 3)
- PT2-fairness-R1: role_set has 2 roles (spec default is >= 3)
- PT2-collective_welfare-R4: role_set has 2 roles (spec default is >= 3)
- PT2-tradition-R2: role_set has 2 roles (spec default is >= 3)
- PT2-honesty-C1-null: role_set differs from paired probe PT2-honesty-C1 (paired comparison loses roles)
- PT2-privacy-C1-null: role_set differs from paired probe PT2-privacy-C1 (paired comparison loses roles)
- PT2-integrity-C1-null: role_set differs from paired probe PT2-integrity-C1 (paired comparison loses roles)
- PT2-impartiality-C1-null: role_set differs from paired probe PT2-impartiality-C1 (paired comparison loses roles)
- PT2-care-C1-null: role_set differs from paired probe PT2-care-C1 (paired comparison loses roles)
- PT2-fairness-C1-null: role_set differs from paired probe PT2-fairness-C1 (paired comparison loses roles)
- PT2-autonomy-C1-null: role_set has 2 roles (spec default is >= 3)
- PT2-autonomy-C1-null: role_set differs from paired probe PT2-autonomy-C1 (paired comparison loses roles)
- PT2-desert-C1-null: role_set differs from paired probe PT2-desert-C1 (paired comparison loses roles)
- PT2-mercy-C1-null: role_set differs from paired probe PT2-mercy-C1 (paired comparison loses roles)
- PT2-collective_welfare-C1-null: role_set has 2 roles (spec default is >= 3)
- PT2-sanctity-C1-null: role_set differs from paired probe PT2-sanctity-C1 (paired comparison loses roles)
- PT2-tradition-C1-null: role_set differs from paired probe PT2-tradition-C1 (paired comparison loses roles)
- mercy / PT2-mercy-C4::friend: possible lexical leakage: 'lenien'
- mercy / PT2-mercy-C4::friend: possible lexical leakage: 'lenien'
- mercy / PT2-mercy-C4::sibling: possible lexical leakage: 'lenien'
- mercy / PT2-mercy-C4::sibling: possible lexical leakage: 'lenien'
- mercy / PT2-mercy-C4::stranger: possible lexical leakage: 'lenien'
- mercy / PT2-mercy-C4::stranger: possible lexical leakage: 'lenien'
- impartiality / PT2-impartiality-R5::self: possible lexical leakage: 'balanced'
- impartiality / PT2-impartiality-R5::friend: possible lexical leakage: 'balanced'
- impartiality / PT2-impartiality-R5::coworker: possible lexical leakage: 'balanced'

## Statistics

- calibration counterbalance: longer paraphrase in A 8 / B 8 (ties excluded)
- rendered records by block: calibration=16, main=587, null_comparison=58
- rendered records by role: (none)=16, boss=129, coworker=129, friend=134, self=72, sibling=105, stranger=76
- resistance prompt words: median 21.0
- choice neutral-prompt words: median 48