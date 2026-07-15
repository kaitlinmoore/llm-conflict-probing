#!/usr/bin/env python3
"""
merge_shards.py — recombine sharded run_pretest.py outputs into one run dir.

Shards are produced with `run_pretest.py --shard i/N` (deterministic
round-robin over rendered prompts; a prompt's k samples and its activation
cache never split across shards). This script:

  1. Verifies the shard set is coherent: same probe file (sha256, re-verified
     against --probes on disk), same model/params, shard specs covering
     exactly 1..N, activations complete (partial flag False).
  2. Verifies counts against the frozen probe set: each shard's CSV row count
     must equal its manifest's expected_rows, per-shard task slices must match,
     and the merged totals must equal the full enumeration.
  3. Concatenates generations.csv rows re-sorted into canonical enumeration
     order (frozen-file order; seeds in order within a prompt, greedy_ref last).
  4. Merges activation dicts into one activations_{tag}.pt (partial: False).
  5. Writes a merged manifest.json embedding, per shard: run_id, shard spec,
     sha256 of the shard's generations.csv / activations .pt / manifest.json,
     and the shard's full run manifest.

Any mismatch is a hard failure (exit 1) — a merged run must be provably the
frozen set, whole, exactly once.

Usage:
  python src/pretest/merge_shards.py \
      --shards results/pretest/<run_shard1of3> results/pretest/<run_shard2of3> results/pretest/<run_shard3of3> \
      --probes data/pretest/pretest_probes_v2.jsonl \
      --out results/pretest/<merged_run_id>

Count verification and manifest assembly are torch-free (testable off-pod);
torch is imported only to load/merge/save activation files.
"""

import argparse
import csv
import datetime
import hashlib
import json
import sys
from pathlib import Path

try:
    from src.pretest import runner_lib as rl
except ImportError:  # running as a plain script
    import runner_lib as rl


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_shard(run_dir: Path):
    manifest = json.loads((run_dir / "manifest.json").read_text())
    csv_path = run_dir / "generations.csv"
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    return {"dir": run_dir, "manifest": manifest, "rows": rows, "csv_path": csv_path}


def verify_shards(shards, probes_path: Path, probes_sha: str, tasks):
    """Coherence + count checks. Returns (sample_k, problems). Pure logic —
    unit-testable without torch or real activations."""
    problems = []

    consistent_keys = ["probe_file_sha256", "model", "model_tag", "dtype",
                       "schema_version", "sample_k", "temperature", "max_new_tokens"]
    reference = shards[0]["manifest"]
    for s in shards[1:]:
        for k in consistent_keys:
            if s["manifest"].get(k) != reference.get(k):
                problems.append(f"{s['dir'].name}: manifest {k!r} = {s['manifest'].get(k)!r} "
                                f"differs from {shards[0]['dir'].name}'s {reference.get(k)!r}")

    if reference.get("probe_file_sha256") != probes_sha:
        problems.append(f"probe file on disk ({probes_path}) does not match the shards' "
                        f"probe_file_sha256 — wrong frozen set")
    for s in shards:
        if s["manifest"].get("screen_mode"):
            problems.append(f"{s['dir'].name}: is a screen run — screens are not sharded/merged")

    # shard specs must cover exactly 1..N
    specs = []
    for s in shards:
        spec = s["manifest"].get("shard")
        if not spec:
            problems.append(f"{s['dir'].name}: manifest has no shard spec — not a shard run")
            continue
        specs.append(rl.parse_shard(spec))
    totals = {n for _, n in specs}
    if len(totals) > 1:
        problems.append(f"shards disagree on N: {sorted(totals)}")
    elif specs:
        n = totals.pop()
        indices = sorted(i for i, _ in specs)
        if indices != list(range(1, n + 1)):
            problems.append(f"shard indices {indices} do not cover exactly 1..{n}")
        if len(shards) != n:
            problems.append(f"{len(shards)} shard dirs given but N = {n}")

    sample_k = reference.get("sample_k") or 0

    # per-shard and total counts against the frozen set
    seen_row_keys = set()
    seen_prompt_keys = set()
    for s in shards:
        spec = s["manifest"].get("shard")
        if not spec:
            continue
        i, n = rl.parse_shard(spec)
        expected_tasks = rl.shard_slice(tasks, i, n)
        expected_rows = rl.expected_total_rows(expected_tasks, sample_k)
        if len(s["rows"]) != expected_rows:
            problems.append(f"{s['dir'].name}: {len(s['rows'])} rows, expected {expected_rows} "
                            f"from the frozen set (shard {spec}, sample_k={sample_k})")
        expected_keys = {t["prompt_key"] for t in expected_tasks}
        got_keys = {r["prompt_key"] for r in s["rows"]}
        if got_keys != expected_keys:
            missing, extra = expected_keys - got_keys, got_keys - expected_keys
            if missing:
                problems.append(f"{s['dir'].name}: missing prompt_keys (first 5): {sorted(missing)[:5]}")
            if extra:
                problems.append(f"{s['dir'].name}: unexpected prompt_keys (first 5): {sorted(extra)[:5]}")
        overlap = seen_prompt_keys & got_keys
        if overlap:
            problems.append(f"{s['dir'].name}: prompt_keys already seen in another shard (first 5): "
                            f"{sorted(overlap)[:5]}")
        seen_prompt_keys |= got_keys
        for r in s["rows"]:
            row_key = (r["prompt_key"], r.get("variant", ""), r.get("seed", ""))
            if row_key in seen_row_keys:
                problems.append(f"duplicate row across shards: {row_key}")
            seen_row_keys.add(row_key)

    total_expected = rl.expected_total_rows(tasks, sample_k)
    total_rows = sum(len(s["rows"]) for s in shards)
    if total_rows != total_expected:
        problems.append(f"merged total {total_rows} rows != {total_expected} expected from the frozen set")

    return sample_k, problems


def canonical_row_order(tasks, sample_k):
    """(prompt_key, variant, seed) -> sort index, in frozen-file order."""
    order = {}
    idx = 0
    for t in tasks:
        if t["kind"] == "resistance":
            for seed in range(sample_k):
                order[(t["prompt_key"], "sample", str(seed))] = idx; idx += 1
            order[(t["prompt_key"], "greedy_ref", "")] = idx; idx += 1
        elif t["kind"] == "v1_generate":
            order[(t["prompt_key"], t["variant"], "")] = idx; idx += 1
        else:
            order[(t["prompt_key"], t["variant"], "")] = idx; idx += 1
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", required=True, nargs="+",
                    help="Shard run directories (results/pretest/<run_id>), all N of them.")
    ap.add_argument("--probes", required=True,
                    help="The frozen probe set the shards ran against (count verification).")
    ap.add_argument("--out", default=None,
                    help="Merged output dir (default: results/pretest/<ts>_<tag>_<role>_merged).")
    args = ap.parse_args()

    probes_path = Path(args.probes)
    records = [json.loads(l) for l in probes_path.read_text().splitlines() if l.strip()]
    tasks = rl.enumerate_tasks(records)
    probes_sha = sha256_of(probes_path)

    shards = [load_shard(Path(d)) for d in args.shards]
    sample_k, problems = verify_shards(shards, probes_path, probes_sha, tasks)

    # activations must be complete (partial flag False) in every shard
    import torch  # deferred: everything above is torch-free
    merged_activations = {}
    act_meta = {}
    for s in shards:
        tag = s["manifest"]["model_tag"]
        act_path = s["dir"] / f"activations_{tag}.pt"
        if not act_path.exists():
            problems.append(f"{s['dir'].name}: missing {act_path.name}")
            continue
        blob = torch.load(act_path, map_location="cpu", weights_only=False)
        if blob.get("partial", True):
            problems.append(f"{s['dir'].name}: activations checkpoint is partial — shard run did not finish")
            continue
        overlap = set(blob["activations"]) & set(merged_activations)
        if overlap:
            problems.append(f"{s['dir'].name}: activation prompt_keys already merged (first 5): "
                            f"{sorted(overlap)[:5]}")
        merged_activations.update(blob["activations"])
        act_meta = {k: blob[k] for k in ("layout", "n_layers", "d_model") if k in blob}
        s["act_path"] = act_path

    expected_act_keys = {t["prompt_key"] for t in tasks}
    if set(merged_activations) != expected_act_keys and not problems:
        missing = expected_act_keys - set(merged_activations)
        extra = set(merged_activations) - expected_act_keys
        if missing:
            problems.append(f"merged activations missing prompt_keys (first 5): {sorted(missing)[:5]}")
        if extra:
            problems.append(f"merged activations have unexpected prompt_keys (first 5): {sorted(extra)[:5]}")

    if problems:
        print("MERGE REFUSED — the shard set is not a complete, single covering of the frozen set:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    reference = shards[0]["manifest"]
    tag = reference["model_tag"]
    run_id = (Path(args.out).name if args.out
              else datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
              + f"_{tag}_{reference['run_role']}_merged")
    out_dir = Path(args.out) if args.out else Path("results/pretest") / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- merged generations.csv in canonical (frozen-file) order ----
    order = canonical_row_order(tasks, sample_k)
    all_rows = [r for s in shards for r in s["rows"]]
    all_rows.sort(key=lambda r: order[(r["prompt_key"], r.get("variant", ""), r.get("seed", ""))])
    fieldnames = list(all_rows[0].keys())
    gen_path = out_dir / "generations.csv"
    with open(gen_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)

    act_path = out_dir / f"activations_{tag}.pt"
    torch.save({"activations": merged_activations, "partial": False, **act_meta}, act_path)

    manifest = dict(reference)  # merged run inherits the shard params...
    manifest.update({           # ...and is extended with merge provenance
        "run_id": run_id,
        "shard": None,
        "shard_index": None,
        "shard_total": None,
        "merged": True,
        "merged_timestamp": datetime.datetime.now().isoformat(),
        "n_prompt_texts": len(tasks),
        "n_tasks_shard": len(tasks),
        "expected_rows": rl.expected_total_rows(tasks, sample_k),
        "n_rows_merged": len(all_rows),
        "probe_file": str(probes_path),
        "probe_file_sha256": probes_sha,
        "anchor_verification_samples": [x for s in shards
                                        for x in s["manifest"]["anchor_verification_samples"]],
        "shards": [{
            "run_id": s["manifest"]["run_id"],
            "shard": s["manifest"]["shard"],
            "n_rows": len(s["rows"]),
            "generations_csv_sha256": sha256_of(s["csv_path"]),
            "activations_pt_sha256": sha256_of(s["act_path"]),
            "manifest_sha256": sha256_of(s["dir"] / "manifest.json"),
            "manifest": s["manifest"],
        } for s in shards],
    })
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"Merged {len(shards)} shards -> {out_dir}")
    print(f"  rows: {len(all_rows)} (verified against {probes_path.name})")
    print(f"  activation sets: {len(merged_activations)}")
    print(f"  manifest: {out_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
