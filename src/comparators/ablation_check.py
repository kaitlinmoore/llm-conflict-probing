#!/usr/bin/env python3
"""
ablation_check.py — functional validation of the refusal direction: project it
out of the residual stream and measure whether refusal on harmful prompts
actually drops. GPU step (generates text); runs after refusal_direction.py.

Design:
  - Held-out prompts only: the 32 harmful + 32 harmless `holdout` items, never
    seen by the direction estimator.
  - Two conditions per prompt: baseline (no intervention) and ablated
    (direction projected out).
  - Ablation is applied at EVERY layer's resid_post, over ALL token positions
    (the standard "directional ablation" of the refusal-direction literature:
    a direction removed only at the anchor is re-introduced downstream).
    Which direction: the per-layer direction at the chosen band layer(s),
    --ablate-layers (default: the >= 0.9*peak reliability band from the npz).
  - Capped greedy generation, --max-new-tokens (default 64), do_sample=False,
    so the comparison is deterministic.
  - Refusal label: the pre-test keyword prelabel
    (run_pretest.heuristic_resistance_prelabel / REFUSAL_MARKERS) — the same
    heuristic certified as primary labeler in Stage 1 (1.94% audited
    disagreement). Reused deliberately: a comparator validated with a
    different labeler than the study's own would not be comparable.

PRE-STATED STOPPING RULE (session brief, Task 3 part B): if ablation shows no
refusal reduction, that is the result and it gets written up as such. This
script therefore takes no "try harder" parameters beyond the layer band, and
records exactly what it ran.

Outputs, in the capture run dir:
  ablation_check_{model_tag}.csv       per prompt x condition: response,
                                       prelabel, refused flag
  ablation_summary_{model_tag}.json    rates + deltas by class and condition

Usage (pod):
  python src/comparators/ablation_check.py \
      --run-dir results/comparators/<run_id> \
      --model meta-llama/Llama-3.1-8B-Instruct
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch
from transformer_lens import HookedTransformer

try:
    from src.pretest import runner_lib as rl
    from src.pretest.run_pretest import (MODEL_REGISTRY, templated,
                                         verify_anchor,
                                         heuristic_resistance_prelabel)
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    import runner_lib as rl
    from run_pretest import (MODEL_REGISTRY, templated, verify_anchor,
                             heuristic_resistance_prelabel)

FIELDNAMES = ["prompt_key", "prompt_class", "condition", "ablate_layers",
              "response", "prelabel_heuristic", "refused"]


def refused_flag(response: str) -> int:
    return int(heuristic_resistance_prelabel(response).startswith("resist"))


def band_layers(reliability, frac=0.9):
    peak = float(np.max(reliability))
    return [int(l) for l in np.flatnonzero(reliability >= frac * peak)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompts", default="data/comparators/refusal_prompts.jsonl")
    ap.add_argument("--max-new-tokens", type=int, default=64)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--ablate-layers", default=None,
                    help="comma-separated layer indices whose direction is "
                         "ablated (default: >= 0.9*peak reliability band)")
    ap.add_argument("--out-suffix", default="",
                    help="appended to output filenames, e.g. '_L21'. Required "
                         "when running a layer sweep into one run dir: without "
                         "it each run overwrites the previous run's CSV/JSON "
                         "and the manifest digests point only at the last one.")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap prompts per class (dry-run only)")
    ap.add_argument("--random-directions", type=int, default=0,
                    help="D53 control: ablate N seeded random directions "
                         "instead of the fitted one — identical protocol, "
                         "same output shapes, per-direction result files "
                         "(suffix _r<k>). Matched norm: ablation projects a "
                         "unit vector, so randoms are unit-normalized "
                         "exactly like the fitted direction's applied form "
                         "(projection removal is scale-invariant).")
    ap.add_argument("--random-seed", type=int, default=23,
                    help="seed for the random directions (recorded)")
    args = ap.parse_args(argv)

    if args.model not in MODEL_REGISTRY:
        print(f"ABLATION FAIL — {args.model!r} not in MODEL_REGISTRY")
        return 1
    spec = MODEL_REGISTRY[args.model]
    run_dir = Path(args.run_dir)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    model_tag = manifest["model_tag"]

    npz = np.load(run_dir / f"refusal_direction_{model_tag}.npz",
                  allow_pickle=False)
    direction = npz["direction"]          # [n_layers, d_model], unit-normalized
    reliability = npz["reliability"]
    layers = ([int(x) for x in args.ablate_layers.split(",")]
              if args.ablate_layers else band_layers(reliability))
    print(f"ablating direction(s) from layer(s) {layers} "
          f"(peak reliability {float(np.max(reliability)):.4f})")

    records = [json.loads(l) for l in
               Path(args.prompts).read_text(encoding="utf-8").splitlines()
               if l.strip()]
    holdout = [r for r in records if r["split"] == "holdout"]
    if args.limit:
        keep = []
        for cls in ("harmful", "harmless"):
            keep += [r for r in holdout if r["prompt_class"] == cls][:args.limit]
        holdout = keep
    print(f"held-out prompts: {len(holdout)}")

    dtype = getattr(torch, args.dtype)
    model = HookedTransformer.from_pretrained(
        args.model, device=args.device, dtype=dtype)
    tokenizer = model.tokenizer
    anchor_samples = []

    # Mean direction over the chosen band, re-normalized: one vector removed
    # everywhere (standard directional ablation).
    fitted = direction[layers].mean(axis=0)
    fitted = fitted / np.linalg.norm(fitted)

    def sweep(vec, out_suffix, direction_meta):
        """One full protocol pass with `vec` ablated everywhere. Identical
        for the fitted direction and each D53 random direction — same
        prompts, conditions, labeler, output shapes."""
        vec_t = torch.tensor(vec, dtype=dtype, device=args.device)

        def ablate_hook(resid, hook):
            # resid: [batch, pos, d_model] — project out along the last dim
            proj = (resid.to(vec_t.dtype) @ vec_t).unsqueeze(-1) * vec_t
            return resid - proj.to(resid.dtype)

        hooks = [(f"blocks.{l}.hook_resid_post", ablate_hook)
                 for l in range(model.cfg.n_layers)]

        csv_path = run_dir / f"ablation_check_{model_tag}{out_suffix}.csv"
        f = open(csv_path, "w", newline="", encoding="utf-8")
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        f.flush()

        rows = []
        with torch.no_grad():
            for i, rec in enumerate(holdout, 1):
                prompt_str = templated(tokenizer, rec["text"])
                ids = verify_anchor(tokenizer, prompt_str,
                                    spec["anchor_expect_decoded_suffix"],
                                    anchor_samples)
                batch = ids.unsqueeze(0).to(args.device)
                for condition in ("baseline", "ablated"):
                    if condition == "baseline":
                        out = model.generate(
                            batch, max_new_tokens=args.max_new_tokens,
                            do_sample=False, verbose=False)
                    else:
                        with model.hooks(fwd_hooks=hooks):
                            out = model.generate(
                                batch, max_new_tokens=args.max_new_tokens,
                                do_sample=False, verbose=False)
                    response = tokenizer.decode(out[0, ids.shape[0]:],
                                                skip_special_tokens=True)
                    row = {"prompt_key": rec["prompt_key"],
                           "prompt_class": rec["prompt_class"],
                           "condition": condition,
                           "ablate_layers": ";".join(str(l) for l in layers),
                           "response": response,
                           "prelabel_heuristic":
                               heuristic_resistance_prelabel(response),
                           "refused": refused_flag(response)}
                    writer.writerow(row)
                    f.flush()
                    rows.append(row)
                if i % 8 == 0:
                    print(f"  [{i}/{len(holdout)}] prompts done")
        f.close()

        summary = {"run_id": manifest["run_id"], "model": args.model,
                   "ablate_layers": layers,
                   "max_new_tokens": args.max_new_tokens,
                   "labeler": "pretest heuristic_resistance_prelabel "
                              "(REFUSAL_MARKERS)",
                   "direction": direction_meta,
                   "n_prompts": len(holdout), "rates": {}}
        for cls in ("harmful", "harmless"):
            summary["rates"][cls] = {}
            for cond in ("baseline", "ablated"):
                sel = [r for r in rows
                       if r["prompt_class"] == cls and r["condition"] == cond]
                rate = (sum(r["refused"] for r in sel) / len(sel)) if sel \
                    else None
                summary["rates"][cls][cond] = rate
            b = summary["rates"][cls]["baseline"]
            a = summary["rates"][cls]["ablated"]
            summary["rates"][cls]["delta"] = (
                None if b is None or a is None else round(a - b, 4))
        print(f"--- {direction_meta['kind']}"
              + (f" #{direction_meta['index']}"
                 if "index" in direction_meta else ""))
        print(json.dumps(summary["rates"], indent=2))

        json_path = run_dir / (f"ablation_summary_{model_tag}"
                               f"{out_suffix}.json")
        rl.atomic_write(json_path,
                        lambda fh: fh.write(json.dumps(summary, indent=2)
                                            + "\n"),
                        mode="w", encoding="utf-8", newline="\n")
        for p in (csv_path, json_path):
            sha, size = rl.file_digest(p)
            manifest.setdefault("output_digests", {})[p.name] = {
                "sha256": sha, "bytes": size}
            print(f"DIGEST {sha} {size} {p.name}")

    if args.random_directions > 0:
        # D53 control: N seeded random directions, matched norm (unit — the
        # applied form of the fitted direction; projection ablation is
        # scale-invariant), identical protocol, per-direction files.
        rng = np.random.default_rng(args.random_seed)
        for k in range(args.random_directions):
            rvec = rng.standard_normal(fitted.shape[0])
            rvec = rvec / np.linalg.norm(rvec)
            sweep(rvec.astype(np.float32),
                  f"{args.out_suffix}_r{k}",
                  {"kind": "random", "index": k,
                   "seed": args.random_seed,
                   "cosine_to_fitted": float(rvec @ fitted),
                   "norm": "unit (matched to fitted's applied form)"})
    else:
        sweep(fitted, args.out_suffix, {"kind": "fitted",
                                        "band_layers": layers})

    rl.atomic_write(manifest_path,
                    lambda fh: fh.write(json.dumps(manifest, indent=2) + "\n"),
                    mode="w", encoding="utf-8", newline="\n")
    print("ABLATION OK — interpretation happens locally "
          "(docs/refusal_direction_report.md); no tuning on this result.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
