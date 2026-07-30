#!/usr/bin/env python3
"""
capture_refusal.py — prompt-only anchor activation capture for the refusal
comparison direction. THE ONLY GPU STEP in the refusal-direction pipeline.

Consumes data/comparators/refusal_prompts.jsonl (curated, see
curate_refusal_prompts.py) and produces, in results/comparators/{run_id}/:

  activations_{model_tag}.pt   anchor residual stream, ALL layers, keyed by
                               prompt_key; {"activations", "partial",
                               "n_layers", "d_model"} — same blob shape as
                               the pre-test runner, so verify_run.py and the
                               analysis code read it unchanged
  prompts.csv                  one row per prompt (prompt_key, class, split,
                               n_tokens) — the row-count artifact verify_run
                               checks against expected_rows
  manifest.json                provenance: model, dtype, library versions,
                               prompt-file sha256, anchor spec + decode-
                               verification samples, output digests

Measurement contract (CLAUDE.md invariant 2, unchanged from Stage 1):
  - anchor = final token of the chat-templated prompt, add_generation_prompt=True
  - located by decoding and asserting template structure, never by index
  - templated strings already contain <bos>: prepend_bos=False
  - bf16, torch.no_grad(), selective caching (hook_resid_post), activations
    moved to CPU immediately
No generation happens here — this is a forward pass per prompt. The ablation
functional check (which does generate) is a separate script.

Resumable: activation checkpoints every 25 prompts with partial=True; a
completed run rewrites with partial=False. Re-running from scratch is always
safe (new timestamped run dir; nothing is overwritten).

Usage (pod):
  python src/comparators/capture_refusal.py \
      --prompts data/comparators/refusal_prompts.jsonl \
      --model meta-llama/Llama-3.1-8B-Instruct
"""

import argparse
import csv
import datetime
import json
import sys
from pathlib import Path

import torch
from transformer_lens import HookedTransformer

try:
    from src.pretest import runner_lib as rl
    from src.pretest.run_pretest import MODEL_REGISTRY, templated, verify_anchor
except ImportError:  # plain-script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    import runner_lib as rl
    from run_pretest import MODEL_REGISTRY, templated, verify_anchor

CHECKPOINT_EVERY = 25
SCHEMA_VERSION = "refusal_capture_v1"
PROMPT_FIELDNAMES = ["prompt_key", "prompt_class", "split", "n_tokens"]


def load_prompts(path: Path):
    return [json.loads(l) for l in
            path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", default="data/comparators/refusal_prompts.jsonl")
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", default="results/comparators")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--run-tag", default="refusal")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap prompts per (class, split) group — keeps the "
                         "harmful/harmless pairing balanced. Dry-run/"
                         "plumbing checks only.")
    args = ap.parse_args(argv)

    if args.model not in MODEL_REGISTRY:
        print(f"CAPTURE FAIL — {args.model!r} not in MODEL_REGISTRY "
              f"(anchor spec unknown; add it there, never guess)")
        return 1
    spec = MODEL_REGISTRY[args.model]

    prompts_path = Path(args.prompts)
    prompt_sha, _ = rl.file_digest(prompts_path)
    records = load_prompts(prompts_path)
    if args.limit:
        # per-group cap: index i of each group is the length-matched partner
        # of index i of the other class, so equal caps keep pairs aligned
        seen = {}
        kept = []
        for rec in records:
            g = (rec["prompt_class"], rec["split"])
            seen[g] = seen.get(g, 0) + 1
            if seen[g] <= args.limit:
                kept.append(rec)
        records = kept
    print(f"prompts: {len(records)} from {prompts_path} (sha {prompt_sha[:12]}…)")

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"{stamp}_{spec['tag']}_{args.run_tag}"
    out_dir = Path(args.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=False)
    print(f"run dir: {out_dir}")

    dtype = getattr(torch, args.dtype)
    model = HookedTransformer.from_pretrained(
        args.model, device=args.device, dtype=dtype)
    tokenizer = model.tokenizer
    anchor_samples = []

    act_path = out_dir / f"activations_{spec['tag']}.pt"
    csv_path = out_dir / "prompts.csv"
    csv_f = open(csv_path, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_f, fieldnames=PROMPT_FIELDNAMES)
    writer.writeheader()
    csv_f.flush()

    activations = {}

    def checkpoint(partial):
        rl.atomic_write(act_path, lambda f: torch.save(
            {"activations": activations, "partial": partial,
             "n_layers": model.cfg.n_layers, "d_model": model.cfg.d_model}, f))

    with torch.no_grad():
        for i, rec in enumerate(records, 1):
            key = rec["prompt_key"]
            prompt_str = templated(tokenizer, rec["text"])
            ids = verify_anchor(tokenizer, prompt_str,
                                spec["anchor_expect_decoded_suffix"],
                                anchor_samples)
            _, cache = model.run_with_cache(
                ids.unsqueeze(0).to(args.device),
                return_type=None,
                names_filter=lambda n: n.endswith("hook_resid_post"),
            )
            per_layer = torch.stack(
                [cache["resid_post", layer][0, -1].to(torch.float32).cpu()
                 for layer in range(model.cfg.n_layers)]
            )  # [n_layers, d_model]
            activations[key] = per_layer
            writer.writerow({"prompt_key": key,
                             "prompt_class": rec["prompt_class"],
                             "split": rec["split"],
                             "n_tokens": int(ids.shape[0])})
            csv_f.flush()
            if i % CHECKPOINT_EVERY == 0:
                checkpoint(partial=True)
                print(f"  [{i}/{len(records)}] checkpoint: "
                      f"{len(activations)} activation sets")

    checkpoint(partial=False)
    csv_f.close()

    manifest = {
        "run_id": run_id,
        "run_role": "refusal_comparator_capture",
        "model": args.model,
        "model_tag": spec["tag"],
        "dtype": args.dtype,
        "schema_version": SCHEMA_VERSION,
        "probe_file": str(prompts_path).replace("\\", "/"),
        "probe_file_sha256": prompt_sha,
        "n_prompts": len(records),
        "expected_rows": len(records),
        "row_count_file": csv_path.name,   # verify_run.py reads this
        "anchor_spec": spec["anchor_expect_decoded_suffix"],
        "anchor_verification_samples": anchor_samples,
        "n_layers": model.cfg.n_layers,
        "d_model": model.cfg.d_model,
        "torch_version": torch.__version__,
        "timestamp": datetime.datetime.now().isoformat(),
        "notes": ("Prompt-only anchor capture; no generation. Direction "
                  "estimation and the ablation check are separate scripts."),
    }
    digests = {}
    for p in (csv_path, act_path):
        sha, size = rl.file_digest(p)
        digests[p.name] = {"sha256": sha, "bytes": size}
        print(f"DIGEST {sha} {size} {p.name}")
    manifest["output_digests"] = digests
    rl.atomic_write(out_dir / "manifest.json",
                    lambda f: f.write(json.dumps(manifest, indent=2) + "\n"),
                    mode="w", encoding="utf-8", newline="\n")
    print(f"CAPTURE OK — {len(activations)} activation sets -> {out_dir}")
    print(f"next (verify before anything else touches this dir): "
          f"python scripts/verify_run.py {out_dir.as_posix()}")
    print(f"then: python src/comparators/refusal_direction.py "
          f"--run-dir {out_dir.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
