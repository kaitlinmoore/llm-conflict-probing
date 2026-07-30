# Refusal-comparator pipeline — local CPU dry run

Produced by: Claude Fable 5 (model id `claude-fable-5`).

Purpose: prove the **plumbing** — anchor verification, activation shapes,
checkpointing, npz round-trip, `verify_run.py` compatibility, ablation hook
wiring — on the local machine with no GPU. It validates code, **not
measurement**: the stand-in model is `google/gemma-2-2b-it` (already in
`MODEL_REGISTRY`, cached locally), the prompt count is tiny, and nothing
about the numbers it produces is a result. The real measurement runs on the
pod against `meta-llama/Llama-3.1-8B-Instruct` per `docs/POD_RUNBOOK.md`.

Run from the repo root. Each command is expected to exit 0.

```bash
# 0. offline + CPU (the local box has no pod access and needs no downloads)
export HF_HUB_OFFLINE=1

# 1. capture — 3 prompts per (class, split) = 12 total, CPU, float32 stand-in
python src/comparators/capture_refusal.py \
  --model google/gemma-2-2b-it --device cpu --dtype float32 \
  --run-tag dryrun --limit 3

# 2. direction + split-half reliability (CPU; --n-splits small for speed)
python src/comparators/refusal_direction.py \
  --run-dir results/comparators/<run_id> --n-splits 20

# 3. ablation functional check — 1 prompt/class, 8 new tokens
python src/comparators/ablation_check.py \
  --run-dir results/comparators/<run_id> \
  --model google/gemma-2-2b-it --device cpu --dtype float32 \
  --max-new-tokens 8 --limit 1

# 4. run verification (same script the pre-test runs use)
python scripts/verify_run.py results/comparators/<run_id>
```

Notes and known dry-run-only wrinkles:

- `--limit` caps per `(class, split)` group, so the harmful/harmless pairing
  stays balanced (3 → 3 train pairs + 3 holdout per class). Reliability over
  3 pairs is meaningless as measurement; it exists here to prove the split
  and cosine code runs. The pod run passes no `--limit`.
- Gemma's anchor decodes to the trailing newline after
  `<start_of_turn>model` (CLAUDE.md "known version gotchas"); the capture
  script asserts it via the registry, so a tokenizer upgrade that changes it
  fails loudly here rather than silently on the pod.
- CPU float32 for a 2B model needs ~11 GB RAM and loads in ~45 s.

Automated equivalent: `python -m unittest tests.test_refusal_pipeline -v`
covers the same plumbing with a stub model and no weights (stdlib + numpy),
and runs in under a second. The commands above additionally exercise the
real TransformerLens path.
