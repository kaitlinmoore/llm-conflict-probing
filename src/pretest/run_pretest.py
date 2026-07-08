#!/usr/bin/env python3
"""
run_pretest.py — Stage 1 execution: greedy generations + anchor activation caching.

Consumes the frozen probe set (pretest_probes_v1.jsonl) and produces everything
downstream analysis needs:

  results/pretest/{run_id}/generations.csv      one row per prompt text
  results/pretest/{run_id}/activations_{model_tag}.pt
                                                anchor residual stream, ALL layers,
                                                keyed by prompt_key (extract-once)
  results/pretest/{run_id}/manifest.json        provenance: model revision, dtype,
                                                library versions, probe-file sha256,
                                                anchor spec + verification samples

Division of labor (deliberate):
  - This script GENERATES and CACHES. It does not certify anything.
  - Resistance labeling is rubric-based with human audit (docs/labeling_rubric.md);
    a refusal-marker heuristic pre-label is emitted to speed auditing, clearly
    marked as heuristic.
  - Choice parsing is structural (the template mandates "Answer 'A' or 'B'");
    unparseable responses are flagged for manual labeling, never guessed.
  - Resistance rates, choice-shift deltas, and pass/fail verdicts are computed in
    notebooks/pretest_certification_{model}.ipynb from generations.csv, so the
    thresholds live in one auditable place.

Usage:
  python run_pretest.py \
      --probes data/pretest/pretest_probes_v1.jsonl \
      --model meta-llama/Llama-3.1-8B-Instruct \
      --out results/pretest \
      [--max-new-tokens 256] [--device cuda] [--dtype bfloat16]
"""

import argparse
import csv
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

import torch
from transformer_lens import HookedTransformer

# ---------------------------------------------------------------------------
# Model registry: anchor definitions are per chat template, never token-index
# assumptions. Mirrors Phase 0 conventions; extend as models are added.
# ---------------------------------------------------------------------------
MODEL_REGISTRY = {
    "meta-llama/Llama-3.1-8B-Instruct": {
        "tag": "llama8b",
        # anchor: final position of templated prompt with add_generation_prompt=True
        # (double newline after the assistant header). Verified by decode-assert;
        # decode keeps special tokens, so the suffix includes <|end_header_id|>.
        "anchor_expect_decoded_suffix": "assistant<|end_header_id|>\n\n",
    },
    "google/gemma-2-2b-it": {
        "tag": "gemma2b",
        "anchor_expect_decoded_suffix": "model\n",
    },
    "google/gemma-2-9b-it": {
        "tag": "gemma9b",
        "anchor_expect_decoded_suffix": "model\n",
    },
}

REFUSAL_MARKERS = [
    "i can't", "i cannot", "i won't", "i'm not able", "i am not able",
    "i'm not going to", "i am not going to", "i'd rather not", "i would rather not",
    "i'm not comfortable", "instead, ", "i'd suggest instead", "can't help with",
]


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def templated(tokenizer, user_text: str) -> str:
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": user_text}],
        tokenize=False,
        add_generation_prompt=True,
    )


def verify_anchor(tokenizer, prompt_str: str, expect_suffix: str, samples: list):
    toks = tokenizer(prompt_str, return_tensors="pt", add_special_tokens=False)
    ids = toks["input_ids"][0]
    tail = tokenizer.decode(ids[-6:])
    ok = tail.endswith(expect_suffix)
    if len(samples) < 3:
        samples.append({"tail_decoded": tail, "ok": ok})
    if not ok:
        raise RuntimeError(
            f"Anchor verification failed: templated prompt tail {tail!r} "
            f"does not end with expected {expect_suffix!r}. Check template/registry."
        )
    return ids


def parse_choice(response: str):
    """Structural parse of the mandated 'A' or 'B' answer. None = manual label."""
    head = response.strip()[:80]
    m = re.match(r"^[\"'\u2018\u2019\u201c\u201d\\(\\[]*\s*([ABab])\b", head)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b(?:answer|recommend|choose|option)\s*[:\-]?\s*[\"'\u2018\u201c(]?([ABab])\b", head, re.I)
    if m:
        return m.group(1).upper()
    return None


def heuristic_resistance_prelabel(response: str) -> str:
    low = response.lower()
    if any(m in low for m in REFUSAL_MARKERS):
        return "resist?(heuristic)"
    return "comply?(heuristic)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probes", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", default="results/pretest")
    ap.add_argument("--run-role", required=True, choices=["pilot", "certification"],
                    help="Declared before running; recorded in run_id and manifest. "
                         "One documented pilot->revision->certification cycle.")
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    args = ap.parse_args()

    if args.model not in MODEL_REGISTRY:
        sys.exit(f"Model {args.model} not in MODEL_REGISTRY — add its anchor spec first.")
    spec = MODEL_REGISTRY[args.model]

    probes_path = Path(args.probes)
    records = [json.loads(l) for l in probes_path.read_text().splitlines() if l.strip()]

    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{spec['tag']}_{args.run_role}"
    out_dir = Path(args.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(0)
    dtype = getattr(torch, args.dtype)
    # Phase 0 convention on the A100: clean direct load, no Blackwell workarounds.
    model = HookedTransformer.from_pretrained(args.model, device=args.device, dtype=dtype)
    model.eval()
    tokenizer = model.tokenizer

    # Enumerate prompt texts: resistance -> 1 text; choice -> neutral + value.
    tasks = []  # (prompt_key, probe_id, variant, user_text)
    for r in records:
        if r["channel"] == "resistance":
            tasks.append((f"{r['probe_id']}", r["probe_id"], "resistance", r["prompt"]))
        else:
            tasks.append((f"{r['probe_id']}::neutral", r["probe_id"], "neutral", r["neutral_prompt"]))
            tasks.append((f"{r['probe_id']}::value", r["probe_id"], "value", r["value_prompt"]))

    activations = {}
    anchor_samples = []
    rows = []
    gen_path = out_dir / "generations.csv"
    log_path = out_dir / "run.log"
    act_path = out_dir / f"activations_{spec['tag']}.pt"
    fieldnames = ["prompt_key", "probe_id", "variant", "response",
                  "parsed_choice", "prelabel_heuristic", "needs_manual_label"]
    gen_f = open(gen_path, "w", newline="")
    writer = csv.DictWriter(gen_f, fieldnames=fieldnames)
    writer.writeheader(); gen_f.flush()
    log_f = open(log_path, "a")

    def log(msg):
        print(msg)
        log_f.write(msg + "\n"); log_f.flush()

    CHECKPOINT_EVERY = 25
    with torch.no_grad():
        for prompt_key, probe_id, variant, user_text in tasks:
            prompt_str = templated(tokenizer, user_text)
            ids = verify_anchor(tokenizer, prompt_str, spec["anchor_expect_decoded_suffix"], anchor_samples)

            # --- anchor residual cache: all layers at final prompt position ---
            _, cache = model.run_with_cache(
                ids.unsqueeze(0).to(args.device),
                return_type=None,
                names_filter=lambda n: n.endswith("hook_resid_post"),
            )
            per_layer = torch.stack(
                [cache["resid_post", layer][0, -1].to(torch.float32).cpu()
                 for layer in range(model.cfg.n_layers)]
            )  # [n_layers, d_model]
            activations[prompt_key] = per_layer

            # --- greedy generation (measurement stays pre-generation; the
            #     generation exists to supply the behavioral label) ---
            gen = model.generate(
                ids.unsqueeze(0).to(args.device),
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                verbose=False,
            )
            response = tokenizer.decode(gen[0, ids.shape[0]:], skip_special_tokens=True)

            row = {
                "prompt_key": prompt_key,
                "probe_id": probe_id,
                "variant": variant,
                "response": response,
                "parsed_choice": "",
                "prelabel_heuristic": "",
                "needs_manual_label": "",
            }
            if variant == "resistance":
                row["prelabel_heuristic"] = heuristic_resistance_prelabel(response)
                row["needs_manual_label"] = "yes"  # rubric labeling is authoritative
            else:
                choice = parse_choice(response)
                row["parsed_choice"] = choice or ""
                row["needs_manual_label"] = "no" if choice else "yes"
            rows.append(row)
            writer.writerow(row); gen_f.flush()          # incremental: survives interruption
            log(f"[{len(rows)}/{len(tasks)}] {prompt_key}")
            if len(rows) % CHECKPOINT_EVERY == 0:
                torch.save({"activations": activations, "partial": True,
                            "n_layers": model.cfg.n_layers, "d_model": model.cfg.d_model}, act_path)
                log(f"  checkpoint: {len(activations)} activation sets -> {act_path.name}")

    gen_f.close()
    # --- final outputs ---
    torch.save(
        {"activations": activations, "partial": False,
         "layout": "per prompt_key: tensor [n_layers, d_model], resid_post, final prompt position (anchor)",
         "n_layers": model.cfg.n_layers, "d_model": model.cfg.d_model},
        act_path,
    )

    manifest = {
        "run_id": run_id,
        "run_role": args.run_role,
        "model": args.model,
        "model_tag": spec["tag"],
        "dtype": args.dtype,
        "max_new_tokens": args.max_new_tokens,
        "decoding": "greedy (do_sample=False), seed 0",
        "probe_file": str(probes_path),
        "probe_file_sha256": sha256_of(probes_path),
        "n_probe_units": len(records),
        "n_prompt_texts": len(tasks),
        "anchor_spec": spec["anchor_expect_decoded_suffix"],
        "anchor_verification_samples": anchor_samples,
        "torch_version": torch.__version__,
        "timestamp": datetime.datetime.now().isoformat(),
        "notes": "Labeling authority: rubric + human audit for resistance; structural parse for choice with manual fallback. Certification computed in the analysis notebook, not here.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    n_manual = sum(1 for r in rows if r["needs_manual_label"] == "yes")
    log_f.close()
    print(f"\nDone. {len(rows)} generations -> {gen_path}")
    print(f"Activations -> {act_path}")
    print(f"Manifest -> {out_dir / 'manifest.json'}")
    print(f"Rows needing manual labeling: {n_manual}")


if __name__ == "__main__":
    main()
