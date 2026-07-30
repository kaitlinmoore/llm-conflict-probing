#!/usr/bin/env python3
"""
curate_refusal_prompts.py — build data/comparators/refusal_prompts.jsonl from
standard public sets. CURATION ONLY: every item is copied verbatim from a
public dataset with per-item provenance (source, source sha256, row index).
No harmful content is authored, paraphrased, or extended here.

Sources (downloaded by the researcher, paths passed in; not vendored):
  harmful  — AdvBench harmful_behaviors.csv (Zou et al. 2023, llm-attacks),
             the `goal` column. The `target` column (attack completions) is
             deliberately NOT read.
  harmless — Alpaca (Taori et al. 2023, stanford_alpaca), instructions with
             an empty `input` field, so both sides are self-contained
             single-turn instructions in the same imperative register.

Selection is deterministic (seed 23, repo convention): both sides are sorted
by a stable key, filtered for format-match, then sampled without replacement.
Rerunning with the same inputs reproduces the same file byte-for-byte.

Splits: `train` (n per side = --n-train, the direction-estimation set) and
`holdout` (--n-holdout per side, reserved for the ablation functional check;
never used to estimate the direction).

Format-match filters (both sides): single-line, no trailing colon, length in
[--min-chars, --max-chars], ASCII-only, no placeholder braces, and for the
harmless side an imperative-verb opener so the two sides read alike.

Usage:
  python src/comparators/curate_refusal_prompts.py \
      --advbench <path>/harmful_behaviors.csv --alpaca <path>/alpaca_data.json
"""

import argparse
import csv
import datetime
import hashlib
import json
import random
import re
import sys
from pathlib import Path

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:  # plain-script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    from runner_lib import atomic_write, file_digest

SEED = 23  # repo-wide fixed seed
SCHEMA_VERSION = "refusal_prompts_v1"

# Imperative openers for the harmless side: keeps register matched to
# AdvBench's "Write a…/Develop a…/Explain how to…" phrasing.
IMPERATIVE_RE = re.compile(
    r"^(write|develop|create|explain|describe|design|give|list|generate|"
    r"outline|provide|suggest|compose|draft|summarize|name|identify|"
    r"construct|build|make|compare|analyze|calculate|convert|edit|"
    r"rewrite|translate|classify|categorize|find|determine|propose|"
    r"recommend|demonstrate|illustrate|formulate|devise)\b",
    re.IGNORECASE)


def format_ok(text, min_chars, max_chars):
    if not text or "\n" in text or "\r" in text:
        return False
    if not (min_chars <= len(text) <= max_chars):
        return False
    if text.rstrip().endswith(":"):
        return False
    if "{" in text or "}" in text or "[" in text:
        return False
    try:
        text.encode("ascii")
    except UnicodeEncodeError:
        return False
    return True


def load_harmful(path, min_chars, max_chars):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for i, row in enumerate(rows):
        goal = (row.get("goal") or "").strip()
        if format_ok(goal, min_chars, max_chars):
            out.append({"text": goal, "row": i})
    return out, len(rows)


def load_harmless(path, min_chars, max_chars):
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for i, rec in enumerate(records):
        if (rec.get("input") or "").strip():
            continue  # needs an attached input block; not self-contained
        instr = (rec.get("instruction") or "").strip()
        if format_ok(instr, min_chars, max_chars) and IMPERATIVE_RE.match(instr):
            out.append({"text": instr, "row": i})
    return out, len(records)


def pick(pool, n, rng):
    """Deterministic sample: stable sort by text, then rng.sample."""
    pool = sorted(pool, key=lambda r: (r["text"], r["row"]))
    if len(pool) < n:
        raise ValueError(f"pool has {len(pool)} usable items, need {n}")
    return sorted(rng.sample(pool, n), key=lambda r: r["text"])


def length_match(targets, pool, rng):
    """One harmless item per harmful item, nearest by character length,
    sampled without replacement. Prompt length shifts the anchor
    representation, so an unmatched length gap would ride into the
    difference-in-means as a confound; AdvBench goals run ~15 chars longer
    than typical Alpaca instructions, so this is not a null adjustment.

    Deterministic: candidates are pre-sorted, ties broken by text, and the
    harmful side is consumed in a fixed order."""
    by_len = {}
    for item in sorted(pool, key=lambda r: (r["text"], r["row"])):
        by_len.setdefault(len(item["text"]), []).append(item)
    for bucket in by_len.values():
        rng.shuffle(bucket)
    picked = []
    for tgt in sorted(targets, key=lambda r: r["text"]):
        want = len(tgt["text"])
        best = None
        for dist in range(0, 200):
            for cand_len in ({want - dist, want + dist} if dist else {want}):
                bucket = by_len.get(cand_len)
                if bucket:
                    best = bucket.pop()
                    if not bucket:
                        by_len.pop(cand_len, None)
                    break
            if best is not None:
                break
        if best is None:
            raise ValueError("length-matching pool exhausted")
        picked.append(best)
    # Returned in target order (NOT re-sorted): index i of the result is the
    # length-match of index i of sorted(targets), so the caller's split
    # assignment keeps matched pairs in the same split and both splits stay
    # length-balanced.
    return picked


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--advbench", required=True,
                    help="path to AdvBench harmful_behaviors.csv")
    ap.add_argument("--alpaca", required=True,
                    help="path to alpaca_data.json")
    ap.add_argument("--out", default="data/comparators/refusal_prompts.jsonl")
    ap.add_argument("--n-train", type=int, default=128)
    ap.add_argument("--n-holdout", type=int, default=32)
    ap.add_argument("--min-chars", type=int, default=30)
    ap.add_argument("--max-chars", type=int, default=160)
    ap.add_argument("--no-length-match", action="store_true",
                    help="disable nearest-length matching of the harmless "
                         "side (default: matched, see length_match docstring)")
    args = ap.parse_args(argv)

    adv_path, alp_path = Path(args.advbench), Path(args.alpaca)
    adv_sha, _ = file_digest(adv_path)
    alp_sha, _ = file_digest(alp_path)

    harmful, n_adv = load_harmful(adv_path, args.min_chars, args.max_chars)
    harmless, n_alp = load_harmless(alp_path, args.min_chars, args.max_chars)
    print(f"AdvBench: {n_adv} rows -> {len(harmful)} format-matched")
    print(f"Alpaca:   {n_alp} rows -> {len(harmless)} format-matched "
          f"(no input, imperative opener)")

    need = args.n_train + args.n_holdout
    rng = random.Random(SEED)
    sel_harmful = pick(harmful, need, rng)   # sorted by text
    if args.no_length_match:
        sel_harmless = pick(harmless, need, rng)
    else:
        sel_harmless = length_match(sel_harmful, harmless, rng)
    for name, sel in (("harmful", sel_harmful), ("harmless", sel_harmless)):
        lengths = [len(r["text"]) for r in sel]
        print(f"{name}: mean length {sum(lengths) / len(lengths):.1f} chars "
              f"[{min(lengths)}, {max(lengths)}]")

    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    records = []
    for cls, sel, src, src_sha, src_field in (
            ("harmful", sel_harmful, "advbench/harmful_behaviors.csv",
             adv_sha, "goal"),
            ("harmless", sel_harmless, "alpaca/alpaca_data.json",
             alp_sha, "instruction")):
        for j, item in enumerate(sel):
            split = "train" if j < args.n_train else "holdout"
            k = j if j < args.n_train else j - args.n_train
            records.append({
                "schema_version": SCHEMA_VERSION,
                "prompt_key": f"{cls}-{split}-{k:03d}",
                "prompt_class": cls,
                "split": split,
                "text": item["text"],
                "provenance": {
                    "source": src,
                    "source_sha256": src_sha,
                    "source_row": item["row"],
                    "source_field": src_field,
                    "curated_utc": now,
                    "curation_note": "verbatim copy; no authored content",
                    "length_matched": not args.no_length_match,
                },
            })

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    atomic_write(out_path, lambda f: f.write(payload),
                 mode="w", encoding="utf-8", newline="\n")
    sha, size = file_digest(out_path)
    counts = {}
    for r in records:
        counts[(r["prompt_class"], r["split"])] = \
            counts.get((r["prompt_class"], r["split"]), 0) + 1
    print(f"Wrote {out_path} ({len(records)} items: "
          + ", ".join(f"{c}/{s}={n}" for (c, s), n in sorted(counts.items()))
          + ")")
    print(f"DIGEST {sha} {size} {out_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
