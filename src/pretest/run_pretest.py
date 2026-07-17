#!/usr/bin/env python3
"""
run_pretest.py — Stage 1 execution: generations / logit readouts + anchor activation caching.

Consumes a frozen probe set (pretest_probes_v1.jsonl or pretest_probes_v2.jsonl)
and produces everything downstream analysis needs:

  results/pretest/{run_id}/generations.csv      one row per measurement
  results/pretest/{run_id}/activations_{model_tag}.pt
                                                anchor residual stream, ALL layers,
                                                keyed by prompt_key (extract-once;
                                                cached once per unique rendered prompt)
  results/pretest/{run_id}/manifest.json        provenance: model revision, dtype,
                                                library versions, probe-file sha256,
                                                anchor spec + verification samples
  results/pretest/{run_id}/screen_{mode}.csv    (--screen only) per-row P values
  results/pretest/{run_id}/screen_{mode}_summary.csv  per-pair aggregate + band flags

Measurement (schema-keyed, so the v1 pilot path is preserved bit-for-bit):
  - v1 probes: greedy generation for both channels; structural choice parse
    with manual fallback (the pilot path — unchanged).
  - v2 choice (incl. calibration + null_comparison blocks): logit readout —
    renormalized P(A)/P(B) over single-token surface variants at the first
    generated position; raw combined mass logged; mass < 0.5 flags the row and
    falls back to greedy parse (spec §4). No sampling.
  - v2 resistance: --sample-k samples at --temperature with seeds 0..k-1,
    plus one greedy reference per prompt (variant=greedy_ref). Heuristic
    two-way prelabel (resist?/comply?) is the primary labeler; the audit
    sample is drawn in the analysis notebook (spec §6).
  - --screen {indifference,rebalance}: logits-only passes over the textured
    pairs' neutral options (spec §5). No activations, no generations.csv.

Division of labor (deliberate):
  - This script GENERATES and CACHES. It does not certify anything.
  - Resistance labeling is rubric-based (docs/labeling_rubric.md, v1.1 two-way);
    the runner's heuristic pre-label is clearly marked as heuristic.
  - Rates, shifts, screens interpretation, and any verdicts are computed in
    notebooks/pretest_analysis.ipynb, so thresholds live in one auditable place.

Usage (v1 pilot path, unchanged):
  python run_pretest.py --probes data/pretest/pretest_probes_v1.jsonl \
      --model meta-llama/Llama-3.1-8B-Instruct --run-role pilot

Usage (v2 instrument validation; shard across pods, then merge_shards.py):
  python run_pretest.py --probes data/pretest/pretest_probes_v2.jsonl \
      --model meta-llama/Llama-3.1-8B-Instruct --run-role instrument_validation \
      --sample-k 10 --temperature 0.7 --shard 1/3

Usage (layer-3 screens, logits-only, single pod, minutes):
  python run_pretest.py --probes data/pretest/pretest_probes_v2_prefreeze.jsonl \
      --model meta-llama/Llama-3.1-8B-Instruct --run-role instrument_validation \
      --screen indifference
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

try:
    from src.pretest import runner_lib as rl
except ImportError:  # running as a plain script: python src/pretest/run_pretest.py
    import runner_lib as rl

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
    m = re.match(r"^[\"'‘’“”\\(\\[]*\s*([ABab])\b", head)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b(?:answer|recommend|choose|option)\s*[:\-]?\s*[\"'‘“(]?([ABab])\b", head, re.I)
    if m:
        return m.group(1).upper()
    return None


def heuristic_resistance_prelabel(response: str) -> str:
    low = response.lower()
    if any(m in low for m in REFUSAL_MARKERS):
        return "resist?(heuristic)"
    return "comply?(heuristic)"


V1_FIELDNAMES = ["prompt_key", "probe_id", "variant", "response",
                 "parsed_choice", "prelabel_heuristic", "needs_manual_label"]
V2_FIELDNAMES = ["prompt_key", "probe_id", "variant", "role", "block",
                 "is_base_cell", "seed",
                 "response", "parsed_choice", "p_a", "p_b", "mass_combined",
                 "low_mass_flag", "choice_source",
                 "prelabel_heuristic", "needs_manual_label"]
SCREEN_FIELDNAMES = ["prompt_key", "probe_id", "role", "value", "mode",
                     "is_base_cell", "p_a", "p_b", "mass_combined",
                     "low_mass_flag", "p_metric", "in_band"]

CHECKPOINT_EVERY = 25


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probes", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", default="results/pretest")
    ap.add_argument("--run-role", required=True,
                    choices=["pilot", "certification", "instrument_validation"],
                    help="Declared before running; recorded in run_id and manifest. "
                         "Cycle: pilot -> revision v2 -> instrument_validation (non-gating) "
                         "-> certification (docs/pretest_v2_spec.md §1).")
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--sample-k", type=int, default=10,
                    help="v2 resistance: samples per rendered prompt, seeds 0..k-1 "
                         "(+ one greedy_ref). Pre-registered default 10 (spec §10). "
                         "Ignored for v1 probe files.")
    ap.add_argument("--temperature", type=float, default=0.7,
                    help="v2 resistance sampling temperature. Pre-registered default 0.7.")
    ap.add_argument("--screen", choices=["indifference", "rebalance"], default=None,
                    help="Layer-3 logits-only screen over textured pairs (spec §5). "
                         "Writes screen CSVs instead of generations/activations.")
    ap.add_argument("--shard", default=None,
                    help="'i/N': run shard i of N (1-indexed, deterministic round-robin "
                         "over rendered prompts). Recombine with merge_shards.py.")
    args = ap.parse_args()

    if args.model not in MODEL_REGISTRY:
        sys.exit(f"Model {args.model} not in MODEL_REGISTRY — add its anchor spec first.")
    spec = MODEL_REGISTRY[args.model]

    probes_path = Path(args.probes)
    records = [json.loads(l) for l in probes_path.read_text().splitlines() if l.strip()]
    schema_version = rl.records_schema_version(records)

    if args.screen:
        tasks = rl.enumerate_screen_tasks(records, args.screen)
    else:
        tasks = rl.enumerate_tasks(records)
    n_tasks_total = len(tasks)

    shard_index = shard_total = None
    if args.shard:
        shard_index, shard_total = rl.parse_shard(args.shard)
        tasks = rl.shard_slice(tasks, shard_index, shard_total)

    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{spec['tag']}_{args.run_role}"
    if args.screen:
        run_id += f"_screen-{args.screen}"
    if args.shard:
        run_id += f"_shard{shard_index}of{shard_total}"
    out_dir = Path(args.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(0)
    dtype = getattr(torch, args.dtype)
    # Phase 0 convention on the A100: clean direct load, no Blackwell workarounds.
    model = HookedTransformer.from_pretrained(args.model, device=args.device, dtype=dtype)
    model.eval()
    tokenizer = model.tokenizer

    # Choice-letter token variants (v2 readout + screens); recorded in manifest.
    choice_tokens = None
    if schema_version == "v2" or args.screen:
        ids_a, forms_a = rl.collect_letter_token_ids(tokenizer, "A")
        ids_b, forms_b = rl.collect_letter_token_ids(tokenizer, "B")
        if not ids_a or not ids_b:
            sys.exit("No single-token surface forms found for 'A'/'B' — check tokenizer.")
        choice_tokens = {"A": {"ids": ids_a, "forms": forms_a},
                         "B": {"ids": ids_b, "forms": forms_b}}

    anchor_samples = []
    rows = []
    log_path = out_dir / "run.log"
    log_f = open(log_path, "a")

    def log(msg):
        print(msg)
        log_f.write(msg + "\n"); log_f.flush()

    # ---- output writers ----
    if args.screen:
        gen_path = out_dir / f"screen_{args.screen}.csv"
        fieldnames = SCREEN_FIELDNAMES
    else:
        gen_path = out_dir / "generations.csv"
        fieldnames = V1_FIELDNAMES if schema_version == "v1" else V2_FIELDNAMES
    act_path = out_dir / f"activations_{spec['tag']}.pt"
    gen_f = open(gen_path, "w", newline="")
    writer = csv.DictWriter(gen_f, fieldnames=fieldnames)
    writer.writeheader(); gen_f.flush()

    activations = {}
    # dedupe: anchor pass runs once per unique rendered prompt text (spec §4);
    # duplicate texts (role-free probes rendered per role) share the tensor.
    memo = {}  # prompt_str sha256 -> {"per_layer": tensor, "logits": list|None}

    def anchor_pass(user_text, want_logits, want_cache):
        prompt_str = templated(tokenizer, user_text)
        ids = verify_anchor(tokenizer, prompt_str, spec["anchor_expect_decoded_suffix"], anchor_samples)
        key = hashlib.sha256(prompt_str.encode("utf-8")).hexdigest()
        hit = memo.get(key)
        if hit is None or (want_logits and hit["logits"] is None) or (want_cache and hit["per_layer"] is None):
            if want_cache:
                logits, cache = model.run_with_cache(
                    ids.unsqueeze(0).to(args.device),
                    return_type="logits" if want_logits else None,
                    names_filter=lambda n: n.endswith("hook_resid_post"),
                )
                per_layer = torch.stack(
                    [cache["resid_post", layer][0, -1].to(torch.float32).cpu()
                     for layer in range(model.cfg.n_layers)]
                )  # [n_layers, d_model]
            else:  # screens: logits only, no residual cache
                logits = model(ids.unsqueeze(0).to(args.device))
                per_layer = hit["per_layer"] if hit else None
            memo[key] = {
                "per_layer": per_layer,
                "logits": (logits[0, -1].to(torch.float32).cpu().tolist()
                           if want_logits else (hit["logits"] if hit else None)),
            }
        return ids, memo[key]

    def emit(row):
        rows.append(row)
        writer.writerow(row); gen_f.flush()          # incremental: survives interruption

    def checkpoint_if_due():
        if not args.screen and len(rows) % CHECKPOINT_EVERY == 0:
            # atomic: checkpoint rewrites must never truncate the previous
            # complete checkpoint (2026-07-17 incident)
            rl.atomic_write(act_path, lambda f: torch.save(
                {"activations": activations, "partial": True,
                 "n_layers": model.cfg.n_layers, "d_model": model.cfg.d_model}, f))
            log(f"  checkpoint: {len(activations)} activation sets -> {act_path.name}")

    def readout_row(entry):
        r = rl.choice_readout(entry["logits"], choice_tokens["A"]["ids"], choice_tokens["B"]["ids"])
        return r

    with torch.no_grad():
        for t_i, task in enumerate(tasks, 1):
            prompt_key, user_text = task["prompt_key"], task["user_text"]

            if task["kind"] == "v1_generate":
                # ---- v1 pilot path: unchanged behavior ----
                ids, entry = anchor_pass(user_text, want_logits=False, want_cache=True)
                activations[prompt_key] = entry["per_layer"]
                gen = model.generate(
                    ids.unsqueeze(0).to(args.device),
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    verbose=False,
                )
                response = tokenizer.decode(gen[0, ids.shape[0]:], skip_special_tokens=True)
                row = {"prompt_key": prompt_key, "probe_id": task["probe_id"],
                       "variant": task["variant"], "response": response,
                       "parsed_choice": "", "prelabel_heuristic": "", "needs_manual_label": ""}
                if task["variant"] == "resistance":
                    row["prelabel_heuristic"] = heuristic_resistance_prelabel(response)
                    row["needs_manual_label"] = "yes"  # rubric labeling is authoritative
                else:
                    choice = parse_choice(response)
                    row["parsed_choice"] = choice or ""
                    row["needs_manual_label"] = "no" if choice else "yes"
                emit(row)

            elif task["kind"] == "screen":
                # ---- layer-3 screen: logits only (spec §5) ----
                ids, entry = anchor_pass(user_text, want_logits=True, want_cache=False)
                r = readout_row(entry)
                if args.screen == "indifference":
                    p_metric, band = r["p_a"], rl.INDIFFERENCE_BAND
                else:
                    p_metric = r["p_a"] if task["value_favored"] == "A" else r["p_b"]
                    band = rl.REBALANCE_BAND
                emit({"prompt_key": prompt_key, "probe_id": task["probe_id"],
                      "role": task["role"] or "", "value": task["value"], "mode": args.screen,
                      "is_base_cell": int(task["is_base_cell"]),
                      "p_a": r["p_a"], "p_b": r["p_b"], "mass_combined": r["mass_combined"],
                      "low_mass_flag": int(r["low_mass_flag"]),
                      "p_metric": p_metric, "in_band": int(rl.in_band(p_metric, band))})

            elif task["kind"] == "choice":
                # ---- v2 choice: logit readout + greedy-parse fallback (spec §4) ----
                ids, entry = anchor_pass(user_text, want_logits=True, want_cache=True)
                activations[prompt_key] = entry["per_layer"]
                r = readout_row(entry)
                row = {"prompt_key": prompt_key, "probe_id": task["probe_id"],
                       "variant": task["variant"], "role": task["role"] or "",
                       "block": task["block"], "is_base_cell": int(task["is_base_cell"]),
                       "seed": "",
                       "response": "", "parsed_choice": "",
                       "p_a": r["p_a"], "p_b": r["p_b"], "mass_combined": r["mass_combined"],
                       "low_mass_flag": int(r["low_mass_flag"]), "choice_source": "logit",
                       "prelabel_heuristic": "", "needs_manual_label": "no"}
                if r["low_mass_flag"]:
                    gen = model.generate(
                        ids.unsqueeze(0).to(args.device),
                        max_new_tokens=args.max_new_tokens,
                        do_sample=False,
                        verbose=False,
                    )
                    response = tokenizer.decode(gen[0, ids.shape[0]:], skip_special_tokens=True)
                    choice = parse_choice(response)
                    row.update({"response": response, "parsed_choice": choice or "",
                                "choice_source": "greedy_fallback",
                                "needs_manual_label": "no" if choice else "yes"})
                emit(row)

            elif task["kind"] == "resistance":
                # ---- v2 resistance: k samples (seeds 0..k-1) + greedy_ref ----
                ids, entry = anchor_pass(user_text, want_logits=False, want_cache=True)
                activations[prompt_key] = entry["per_layer"]
                base = {"prompt_key": prompt_key, "probe_id": task["probe_id"],
                        "variant": "sample", "role": task["role"] or "",
                        "block": task["block"], "is_base_cell": int(task["is_base_cell"]),
                        "parsed_choice": "",
                        "p_a": "", "p_b": "", "mass_combined": "", "low_mass_flag": "",
                        "choice_source": "", "needs_manual_label": "no"}
                for seed in range(args.sample_k):
                    torch.manual_seed(seed)
                    gen = model.generate(
                        ids.unsqueeze(0).to(args.device),
                        max_new_tokens=args.max_new_tokens,
                        do_sample=True,
                        temperature=args.temperature,
                        verbose=False,
                    )
                    response = tokenizer.decode(gen[0, ids.shape[0]:], skip_special_tokens=True)
                    emit({**base, "seed": seed, "response": response,
                          "prelabel_heuristic": heuristic_resistance_prelabel(response)})
                gen = model.generate(
                    ids.unsqueeze(0).to(args.device),
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    verbose=False,
                )
                response = tokenizer.decode(gen[0, ids.shape[0]:], skip_special_tokens=True)
                emit({**base, "variant": "greedy_ref", "seed": "", "response": response,
                      "prelabel_heuristic": heuristic_resistance_prelabel(response)})

            log(f"[{t_i}/{len(tasks)}] {prompt_key}")
            checkpoint_if_due()

    gen_f.close()

    # ---- final outputs ----
    if not args.screen:
        rl.atomic_write(act_path, lambda f: torch.save(
            {"activations": activations, "partial": False,
             "layout": "per prompt_key: tensor [n_layers, d_model], resid_post, final prompt position (anchor)",
             "n_layers": model.cfg.n_layers, "d_model": model.cfg.d_model},
            f,
        ))

    if args.screen:
        # per-pair aggregate over roles (band checks are advisory here; the
        # rewrite-or-drop decision is the researcher's, per spec §5)
        band = rl.INDIFFERENCE_BAND if args.screen == "indifference" else rl.REBALANCE_BAND
        by_probe = {}
        for row in rows:
            by_probe.setdefault(row["probe_id"], []).append(row)

        def write_summary(f):
            w = csv.DictWriter(f, fieldnames=["probe_id", "value", "mode", "n_roles",
                                              "p_metric_mean", "p_metric_min", "p_metric_max",
                                              "in_band_mean", "any_low_mass"])
            w.writeheader()
            for probe_id, group in by_probe.items():
                ps = [r["p_metric"] for r in group if r["p_metric"] is not None]
                w.writerow({
                    "probe_id": probe_id, "value": group[0]["value"], "mode": args.screen,
                    "n_roles": len(group),
                    "p_metric_mean": sum(ps) / len(ps) if ps else "",
                    "p_metric_min": min(ps) if ps else "",
                    "p_metric_max": max(ps) if ps else "",
                    "in_band_mean": int(rl.in_band(sum(ps) / len(ps), band)) if ps else "",
                    "any_low_mass": int(any(r["low_mass_flag"] for r in group)),
                })

        rl.atomic_write(out_dir / f"screen_{args.screen}_summary.csv", write_summary,
                        mode="w", newline="")

    if schema_version == "v1":
        decoding = "greedy (do_sample=False), seed 0"
    elif args.screen:
        decoding = f"screen ({args.screen}): logits-only readout at anchor, no generation"
    else:
        decoding = (f"choice: logit readout at anchor (greedy-parse fallback below mass "
                    f"{rl.LOW_MASS_THRESHOLD}); resistance: k={args.sample_k} samples at "
                    f"temperature {args.temperature}, seeds 0..{args.sample_k - 1}, + greedy_ref")

    # ---- completion digests: computed by RE-READING the persisted files so
    # they are evidence the bytes survived on disk (2026-07-17 incident) ----
    digest_paths = [gen_path]
    if args.screen:
        digest_paths.append(out_dir / f"screen_{args.screen}_summary.csv")
    else:
        digest_paths.append(act_path)
    output_digests = {}
    for p in digest_paths:
        sha, size = rl.file_digest(p)
        output_digests[p.name] = {"sha256": sha, "bytes": size}

    manifest = {
        "run_id": run_id,
        "run_role": args.run_role,
        "model": args.model,
        "model_tag": spec["tag"],
        "dtype": args.dtype,
        "max_new_tokens": args.max_new_tokens,
        "decoding": decoding,
        "probe_file": str(probes_path),
        "probe_file_sha256": sha256_of(probes_path),
        "n_probe_units": len(records),
        "n_prompt_texts": len(tasks),
        "anchor_spec": spec["anchor_expect_decoded_suffix"],
        "anchor_verification_samples": anchor_samples,
        "torch_version": torch.__version__,
        "timestamp": datetime.datetime.now().isoformat(),
        "notes": "Labeling authority: rubric + human audit for resistance; structural parse for choice with manual fallback. Certification computed in the analysis notebook, not here.",
        # ---- v2 extensions (manifest is extended, never reshaped) ----
        "schema_version": schema_version,
        "screen_mode": args.screen,
        "shard": args.shard,
        "shard_index": shard_index,
        "shard_total": shard_total,
        "n_tasks_total": n_tasks_total,
        "n_tasks_shard": len(tasks),
        "sample_k": args.sample_k if schema_version == "v2" and not args.screen else None,
        "temperature": args.temperature if schema_version == "v2" and not args.screen else None,
        "seed_list": list(range(args.sample_k)) if schema_version == "v2" and not args.screen else None,
        "choice_token_variants": choice_tokens,
        "low_mass_threshold": rl.LOW_MASS_THRESHOLD if choice_tokens else None,
        "screen_band": (list(rl.INDIFFERENCE_BAND) if args.screen == "indifference"
                        else list(rl.REBALANCE_BAND) if args.screen == "rebalance" else None),
        "expected_rows": rl.expected_total_rows(tasks, args.sample_k if schema_version == "v2" else 0),
        "n_unique_prompt_texts": len(memo),
        # digests of the other outputs, re-read from disk after their final
        # writes; the manifest can't contain its own hash — that one exists
        # only in the printed DIGEST line
        "output_digests": output_digests,
    }
    manifest_path = out_dir / "manifest.json"
    rl.atomic_write(manifest_path, lambda f: f.write(json.dumps(manifest, indent=2)), mode="w")
    manifest_sha, manifest_bytes = rl.file_digest(manifest_path)

    n_manual = sum(1 for r in rows if r.get("needs_manual_label") == "yes")
    log_f.close()
    print(f"\nDone. {len(rows)} rows -> {gen_path}")
    if not args.screen:
        print(f"Activations -> {act_path}")
    print(f"Manifest -> {out_dir / 'manifest.json'}")
    print(f"Rows needing manual labeling: {n_manual}")
    for name, d in output_digests.items():
        print(f"DIGEST {d['sha256']} {d['bytes']} {name}")
    print(f"DIGEST {manifest_sha} {manifest_bytes} manifest.json")


if __name__ == "__main__":
    main()
