#!/usr/bin/env python3
"""
refusal_direction.py — difference-in-means refusal direction from a capture
run, per layer, unit-normalized, with split-half reliability.

  direction(L) = mean(harmful anchor, layer L) − mean(harmless anchor, layer L),
                 then unit-normalized.

Estimated on the `train` split ONLY; the `holdout` split is reserved for the
ablation functional check and is never touched here.

Split-half reliability uses the same construction as the value-fingerprint
screen (src/analysis/fingerprint_screen.py): all balanced partitions of the
estimation units, direction recomputed within each half, reliability(L) =
mean cosine between the two half-directions. The unit here is the
length-matched harmful/harmless PAIR (pair i = harmful-train-i with
harmless-train-i, the correspondence built by the curator), so a split never
puts the two members of a matched pair on opposite sides. With 128 pairs the
partition space is astronomically large, so partitions are SAMPLED
(--n-splits, default 200, seed 23) rather than enumerated — reported as such.

⚠️ DEVIATION from the pre-test's screen, deliberate and noted: the screen
enumerated all balanced partitions because n was 2–5; here n is 128 and
sampling is the only option. The estimator is otherwise identical.

Outputs, in the capture run dir:
  refusal_direction_{model_tag}.npz   direction [n_layers, d_model] (float32,
                                      unit-normalized), reliability [n_layers],
                                      raw_norm [n_layers], plus metadata
                                      arrays (layers, n_pairs, n_splits)
  refusal_reliability_{model_tag}.csv per-layer reliability + raw norm
CPU only; torch is used solely to load the capture blob.

Usage:
  python src/comparators/refusal_direction.py --run-dir results/comparators/<run_id>
"""

import argparse
import csv
import json
import random
import sys
from pathlib import Path

import numpy as np

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    from runner_lib import atomic_write, file_digest

SEED = 23
DEFAULT_N_SPLITS = 200


def load_capture(run_dir: Path, model_tag: str):
    import torch
    act_path = run_dir / f"activations_{model_tag}.pt"
    blob = torch.load(act_path, map_location="cpu", weights_only=True)
    if blob.get("partial", True):
        raise RuntimeError(f"{act_path.name} has partial=True — refusing "
                           f"(incomplete capture)")
    acts = {k: v.numpy().astype(np.float32)
            for k, v in blob["activations"].items()}
    return acts, blob["n_layers"], blob["d_model"]


def pair_keys(prompts_csv: Path, split="train"):
    """[(harmful_key, harmless_key), ...] for one split, paired by index —
    the length-match correspondence built by curate_refusal_prompts.py."""
    with open(prompts_csv, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["split"] == split]
    harmful = sorted(r["prompt_key"] for r in rows
                     if r["prompt_class"] == "harmful")
    harmless = sorted(r["prompt_key"] for r in rows
                      if r["prompt_class"] == "harmless")
    if len(harmful) != len(harmless):
        raise ValueError(f"{split}: {len(harmful)} harmful vs "
                         f"{len(harmless)} harmless — expected equal counts")
    return list(zip(harmful, harmless))


def diff_in_means(acts, pairs):
    """mean(harmful) − mean(harmless) per layer -> [L, d] float64 (raw)."""
    hf = np.mean(np.stack([acts[a] for a, _ in pairs]), axis=0, dtype=np.float64)
    hl = np.mean(np.stack([acts[b] for _, b in pairs]), axis=0, dtype=np.float64)
    return hf - hl


def unit_normalize(v):
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    return np.divide(v, norms, out=np.zeros_like(v), where=norms > 0)


def cosine_per_layer(a, b):
    num = (a * b).sum(axis=1)
    den = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    return np.divide(num, den, out=np.zeros_like(num), where=den > 0)


def split_half_reliability(acts, pairs, n_splits, rng):
    """Mean cosine between half-directions over sampled balanced partitions."""
    idx = list(range(len(pairs)))
    half = len(idx) // 2
    cosines = []
    seen = set()
    for _ in range(n_splits):
        for _attempt in range(10):
            shuffled = idx[:]
            rng.shuffle(shuffled)
            a = frozenset(shuffled[:half])
            if a not in seen:
                break
        seen.add(a)
        pa = [pairs[i] for i in sorted(a)]
        pb = [pairs[i] for i in idx if i not in a]
        cosines.append(cosine_per_layer(diff_in_means(acts, pa),
                                        diff_in_means(acts, pb)))
    return np.mean(np.stack(cosines), axis=0), len(cosines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--n-splits", type=int, default=DEFAULT_N_SPLITS)
    args = ap.parse_args(argv)

    run_dir = Path(args.run_dir)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    model_tag = manifest["model_tag"]

    acts, n_layers, d_model = load_capture(run_dir, model_tag)
    pairs = pair_keys(run_dir / "prompts.csv", "train")
    missing = [k for p in pairs for k in p if k not in acts]
    if missing:
        print(f"DIRECTION FAIL — {len(missing)} train keys missing from "
              f"activations (first: {missing[:3]})")
        return 1
    print(f"estimation set: {len(pairs)} length-matched pairs "
          f"({n_layers} layers x {d_model})")

    raw = diff_in_means(acts, pairs)
    direction = unit_normalize(raw)
    raw_norm = np.linalg.norm(raw, axis=1)

    rng = random.Random(SEED)
    reliability, n_used = split_half_reliability(acts, pairs, args.n_splits, rng)
    print(f"split-half reliability over {n_used} sampled balanced partitions")
    best = int(np.argmax(reliability))
    print(f"  peak: layer {best}, reliability {reliability[best]:.4f}")
    print(f"  band >= 0.9 * peak: layers "
          f"{[int(l) for l in np.flatnonzero(reliability >= 0.9 * reliability[best])]}")

    npz_path = run_dir / f"refusal_direction_{model_tag}.npz"
    atomic_write(npz_path, lambda f: np.savez(
        f,
        direction=direction.astype(np.float32),
        raw_norm=raw_norm.astype(np.float32),
        reliability=reliability.astype(np.float32),
        layers=np.arange(n_layers),
        n_pairs=np.array([len(pairs)]),
        n_splits=np.array([n_used]),
        estimator=np.array(["difference_in_means_unit_normalized"]),
        split_unit=np.array(["length_matched_pair"]),
    ))
    csv_path = run_dir / f"refusal_reliability_{model_tag}.csv"

    def _w(f):
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["layer", "split_half_reliability", "raw_norm"])
        for l in range(n_layers):
            w.writerow([l, round(float(reliability[l]), 6),
                        round(float(raw_norm[l]), 6)])
    atomic_write(csv_path, _w, mode="w", newline="", encoding="utf-8")

    for p in (npz_path, csv_path):
        sha, size = file_digest(p)
        manifest.setdefault("output_digests", {})[p.name] = {
            "sha256": sha, "bytes": size}
        print(f"DIGEST {sha} {size} {p.name}")
    manifest["direction_estimation"] = {
        "n_pairs": len(pairs), "n_splits": n_used, "seed": SEED,
        "split_unit": "length_matched_pair",
        "peak_layer": best,
        "peak_reliability": round(float(reliability[best]), 6),
    }
    atomic_write(manifest_path,
                 lambda f: f.write(json.dumps(manifest, indent=2) + "\n"),
                 mode="w", encoding="utf-8", newline="\n")
    print(f"DIRECTION OK -> {npz_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
