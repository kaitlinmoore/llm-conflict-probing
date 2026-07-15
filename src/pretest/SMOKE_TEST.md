# Pre-test v2 — pod smoke test

Exact commands to verify the v2 pipeline on a GPU pod, **in order**. Run from
the repo root, inside tmux (`tmux new -s pretest`), with the usual env
(`source scripts/env.sh`; `HF_TOKEN` set; `uv sync` done). Total GPU time is a
few minutes. **STOP the pod after.**

## 1. Unit tests (includes the torch-only merge test skipped off-pod)

```bash
python -m unittest discover -s tests -v
# expect: 56 tests, OK, 0 skipped
```

## 2. Freezer — v1 regression

```bash
python src/authoring/generate_pretest_probes.py \
    --drafts data/pretest/probe_drafts_v1.json \
    --out /tmp/v1_regression.jsonl --report /tmp/v1_regression.md
# expect: "records: 160  problems: 1  warnings: 0" and exit code 1
# (the single problem is the known pilot-era tradition-C2 duplicate; the
#  committed pretest_probes_v1.jsonl predates that validator)
diff <(python -c "import json,sys;[print(json.dumps(json.loads(l))) for l in open('/tmp/v1_regression.jsonl')]") \
     <(python -c "import json,sys;[print(json.dumps(json.loads(l))) for l in open('data/pretest/pretest_probes_v1.jsonl')]") \
  && echo V1-IDENTICAL
```

## 3. Freezer — v2

Until tranche 2 is committed, freeze tranche 1 alone with `--allow-partial`.
Once tranches 2a/2b are committed, run WITHOUT the flag — a real freeze must
exit 0 strict:

```bash
python src/authoring/generate_pretest_probes.py \
    --drafts data/pretest/probe_drafts_v2_tranche1.json \
    --drafts data/pretest/probe_drafts_v2_tranche2a.json \
    --drafts data/pretest/probe_drafts_v2_tranche2b.json \
    --out data/pretest/pretest_probes_v2.jsonl \
    --report data/pretest/validation_report_v2.md
# expect: problems: 0, exit 0. Review warnings in the report before committing.
```

## 4. Screens (logits-only, minutes; spec §5 — run BEFORE the final freeze)

Screens target textured (main-battery) pairs, so they need tranche 2a in the
frozen file:

```bash
python src/pretest/run_pretest.py \
    --probes data/pretest/pretest_probes_v2.jsonl \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --run-role instrument_validation --screen indifference
python src/pretest/run_pretest.py \
    --probes data/pretest/pretest_probes_v2.jsonl \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --run-role instrument_validation --screen rebalance
# expect per run: results/pretest/<run_id>/screen_<mode>.csv +
# screen_<mode>_summary.csv (per-pair P values, in_band flags), manifest.json;
# NO activations file. Check any_low_mass rows before trusting P values.
```

## 5. Tiny sharded run + merge (the critical path)

Build a 6-prompt smoke subset (4 choice + 2 resistance records so both
measurement paths and sampling run):

```bash
python - <<'EOF'
import json
recs = [json.loads(l) for l in open("data/pretest/pretest_probes_v2.jsonl")]
choice = [r for r in recs if r["channel"] == "choice"][:4]
resist = [r for r in recs if r["channel"] == "resistance"][:2]
with open("/tmp/smoke_probes.jsonl", "w") as f:
    for r in choice + resist:
        f.write(json.dumps(r) + "\n")
print("smoke set:", len(choice), "choice +", len(resist), "resistance")
EOF

python src/pretest/run_pretest.py --probes /tmp/smoke_probes.jsonl \
    --model meta-llama/Llama-3.1-8B-Instruct --run-role instrument_validation \
    --sample-k 2 --temperature 0.7 --max-new-tokens 16 --shard 1/2 --out /tmp/smoke_out
python src/pretest/run_pretest.py --probes /tmp/smoke_probes.jsonl \
    --model meta-llama/Llama-3.1-8B-Instruct --run-role instrument_validation \
    --sample-k 2 --temperature 0.7 --max-new-tokens 16 --shard 2/2 --out /tmp/smoke_out

python src/pretest/merge_shards.py \
    --shards /tmp/smoke_out/*shard1of2 /tmp/smoke_out/*shard2of2 \
    --probes /tmp/smoke_probes.jsonl --out /tmp/smoke_out/merged
# expect: "Merged 2 shards" and exit 0. Row math: each main/null choice record
# contributes 2 logit rows (neutral+value), each calibration record 1, each
# resistance record k+1 = 3 rows. The merge recomputes this from the smoke
# probe file and EXITS 1 on any count/sha/coverage mismatch — that refusal
# logic is the actual test.
```

Sanity-check the merged outputs:

```bash
python - <<'EOF'
import json, csv, torch
rows = list(csv.DictReader(open("/tmp/smoke_out/merged/generations.csv")))
acts = torch.load("/tmp/smoke_out/merged/activations_llama8b.pt", weights_only=False)
man  = json.loads(open("/tmp/smoke_out/merged/manifest.json").read())
assert not acts["partial"]
assert len(man["shards"]) == 2 and man["merged"]
assert man["expected_rows"] == len(rows)
# choice rows carry the readout; resistance rows carry samples + greedy_ref
assert any(r["choice_source"] == "logit" and r["p_a"] for r in rows)
assert any(r["variant"] == "greedy_ref" for r in rows)
assert any(r["variant"] == "sample" and r["seed"] == "1" for r in rows)
print("MERGE SMOKE OK:", len(rows), "rows,", len(acts["activations"]), "activation sets")
EOF
```

Also eyeball one shard's `manifest.json`: `anchor_verification_samples[*].ok`
all true; `choice_token_variants` lists the single-token A/B forms actually
summed; `probe_file_sha256` matches across shards.

## 6. Full IV run (after researcher sign-off, spec §7)

```bash
# resistance + choice, 3 shards across pods/GPUs (one process per GPU):
python src/pretest/run_pretest.py --probes data/pretest/pretest_probes_v2.jsonl \
    --model meta-llama/Llama-3.1-8B-Instruct --run-role instrument_validation \
    --sample-k 10 --temperature 0.7 --shard 1/3   # ... 2/3, 3/3 on the others
python src/pretest/merge_shards.py --shards results/pretest/<all three run dirs> \
    --probes data/pretest/pretest_probes_v2.jsonl
# then notebooks/pretest_analysis.ipynb on the merged dir. STOP PODS.
```

Known version gotcha (CLAUDE.md): TransformerLens `generate()` kwargs vary by
version — if `--sample-k` runs fail on `temperature`/`verbose`, check the
installed transformer-lens version before editing call sites.
