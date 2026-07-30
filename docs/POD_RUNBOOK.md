# Pod runbook — refusal comparison direction (Task 3, GPU step)

Produced by: Claude Fable 5 (model id `claude-fable-5`), 2026-07-30.
Audience: the researcher, pasting commands on a RunPod A100 pod they
provision. Claude Code has no pod access and does not run any of this.

**What this run does:** captures anchor activations for 320 curated
prompts (160 harmful / 160 harmless, length-matched), estimates the
difference-in-means refusal direction with split-half reliability, and runs
the ablation functional check on the 64 held-out prompts. One model:
`meta-llama/Llama-3.1-8B-Instruct`.

**Expected wall-clock:** ~10–20 min total on one A100-80GB — 320 forward
passes (no generation) plus 128 short greedy generations. This fits far
inside a single-day window; no sharding, no tmux gymnastics.

**Before you start:** `HF_TOKEN` must have the Llama-3.1 license accepted
(same gate as Stage 1). Everything below runs from the repo root.

---

## 1. Set up the shell (every fresh terminal)

```bash
cd /workspace/llm-conflict-probing
source scripts/env.sh          # HF_HOME + uv guards; defines runpy()
git pull
```

`source scripts/env.sh` **before any uv command** — otherwise uv silently
builds a duplicate venv on the network volume and hits quota (CLAUDE.md).
If the environment needs rebuilding: `uv sync`. When in doubt use `runpy`
(= `/root/venv/bin/python`), which bypasses uv entirely; the commands below
use it for exactly that reason.

Sanity check (should print the frozen prompt-set digest
`1cf1fd8ef69eac84e3392d0d5f458d4e97922e39c269cbd05bcd2fb7b571f3b8`):

```bash
sha256sum data/comparators/refusal_prompts.jsonl
```

## 2. Capture (GPU, ~5–10 min)

tmux has been unreliable on this pod image — use `nohup`:

```bash
nohup runpy src/comparators/capture_refusal.py \
  --prompts data/comparators/refusal_prompts.jsonl \
  --model meta-llama/Llama-3.1-8B-Instruct \
  > capture.log 2>&1 &

tail -f capture.log        # Ctrl-C stops watching, NOT the run
```

Watch for: `prompts: 320 …`, then a `[25/320] checkpoint:` line every 25
prompts, ending with two `DIGEST` lines and `CAPTURE OK`. The run dir it
prints (`results/comparators/<run_id>`) is `$RUN` below:

```bash
RUN=$(ls -d results/comparators/*_llama8b_refusal | tail -1); echo $RUN
```

If it dies partway: nothing is lost or corrupted — activations checkpoint
every 25 with `partial=True`, and re-running creates a **new** timestamped
dir rather than overwriting. Just run it again.

## 3. Direction + split-half reliability (CPU, seconds)

```bash
runpy src/comparators/refusal_direction.py --run-dir $RUN
```

Prints the peak reliability layer and the ≥ 0.9 × peak band, and writes
`refusal_direction_llama8b.npz` + `refusal_reliability_llama8b.csv`.

## 4. Ablation functional check (GPU, ~5 min)

```bash
nohup runpy src/comparators/ablation_check.py \
  --run-dir $RUN --model meta-llama/Llama-3.1-8B-Instruct \
  > ablation.log 2>&1 &

tail -f ablation.log
```

Uses the ≥ 0.9 × peak band automatically and prints baseline/ablated refusal
rates per class. **Do not re-run this with different layers to get a better
number** — the stopping rule is pre-stated: whatever it shows is the result
(session brief, Task 3B). If it errors out, that's different: fix and re-run.

## 5. Verify (seconds)

```bash
runpy scripts/verify_run.py $RUN
```

Must print `VERIFY PASS`. This checks manifest keys, row count vs
`expected_rows`, `partial=False`, and every recorded digest. If it FAILs,
**stop and report the output** rather than committing.

## 6. Commit the results (this is the handoff channel)

Activation tensors are gitignored by design — commit the text artifacts
only; they carry the digests that make the tensor verifiable later.

```bash
git add $RUN/prompts.csv $RUN/manifest.json \
        $RUN/refusal_direction_llama8b.npz \
        $RUN/refusal_reliability_llama8b.csv \
        $RUN/ablation_check_llama8b.csv \
        $RUN/ablation_summary_llama8b.json
git status --short          # confirm no .pt file is staged
git commit -m "Refusal comparator run: capture + direction + ablation ($RUN)"
git push
```

`.npz` is ~0.5 MB (32 layers × 4096 floats) — small enough to commit, and
it is the artifact the analysis needs. If `git status` shows
`activations_llama8b.pt` staged, unstage it (`git restore --staged`) and
tell me — the ignore rule needs fixing.

Then note the tensor's location per `docs/data_locations.md` conventions
(volume path + sha256 from the manifest) so it can be re-verified later.

## 7. Stop the pod

Stop it as soon as step 6 pushes. Nothing further needs the GPU: the report
(`docs/refusal_direction_report.md`) is written locally from the committed
text artifacts.

---

## If something goes wrong

| symptom | what it means | do |
|---|---|---|
| `not in MODEL_REGISTRY` | model name typo'd | use the exact string above |
| `Anchor verification failed` | tokenizer/template changed under us | **stop**, report the printed tail — this is a real invariant breach, not a nuisance |
| `partial=True — refusing` | capture didn't finish | re-run step 2 |
| `VERIFY FAIL` | digest/row mismatch | report the output; don't commit |
| OOM | another process holds the GPU | `nvidia-smi`, kill strays, re-run |

The pipeline was dry-run end-to-end on CPU locally (`src/comparators/DRY_RUN.md`)
with a stand-in model, so plumbing failures here are unlikely; measurement
behavior on Llama is what this run establishes.
