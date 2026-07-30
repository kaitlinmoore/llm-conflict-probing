#!/usr/bin/env python3
"""
fingerprint_screen.py — value-fingerprint screen on cached pre-test anchor
activations (Task 2, session 2026-07-30; WEEK_PLAN_stage2.md Track B).

Per value: fingerprint = mean(anchor activation, value-variant prompts)
− mean(anchor activation, neutral-twin prompts), per layer, unit-normalized.
Cells: choice channel, main block, base cells (role_included_base), complete
neutral+value readings, non-C3, mass-eligible (min variant mass ≥ MASS_FLOOR
= 0.20, the locked §5 floor — constants mirrored from
notebooks/pretest_analysis.ipynb).

Order of computation (each written before the next is computed):
  1. Split-half reliability per value per layer — split by scenario pair
     (probe_id_base), NEVER by role: role cells within a pair share content.
     All balanced pair-partitions are enumerated; reliability(layer) = mean
     cosine between the two half-fingerprints. -> reliability.csv
  2. Pairwise cosine similarity among fingerprints, per layer
     (-> similarity_layers.csv); reported at each value-pair's best
     shared-reliability layer, i.e. argmax_L min(rel_i(L), rel_j(L))
     (-> similarity_summary.csv).
  3. One-page summary -> docs/fingerprint_screen_2026-07.md: reliability
     table, similarity matrix, flag list. Flags only, no verdicts.

This is a SCREEN, not a finding: the pre-test confounds value with topic by
design, so similarity here is suggestive, not diagnostic.

Provisional analysis defaults (not researcher-ratified; stated in the
summary doc so they can be overridden):
  RELIABILITY_THRESHOLD = 0.5   value counts as reliable at a layer if mean
                                split-half cosine ≥ 0.5; UNRELIABLE overall
                                if no layer reaches it. Values with < 2
                                eligible pairs are NOT-ESTIMABLE.
  SIM_CEILING_RATIO     = 0.8   flag a value pair when cosine at the best
                                shared-reliability layer ≥ 0.8 × ceiling,
                                ceiling = sqrt(rel_i × rel_j) (attenuation
                                analogue). Applied to signed cosine: the
                                merge-risk direction is positive similarity.

CPU only. Inputs verified against the run manifest (probe file sha256 and
activations_llama8b.pt sha256) before any computation. Atomic writes
(tmp -> fsync -> os.replace) + DIGEST lines on every artifact; outputs land
in a fresh timestamped results/fingerprint_screen/<stamp>_<tag>/ dir (never
overwritten) with their own manifest.

Usage:
  python src/analysis/fingerprint_screen.py \
      [--run-dir results/pretest/20260717_204822_llama8b_instrument_validation_merged] \
      [--probes data/pretest/pretest_probes_v2.jsonl] \
      [--summary docs/fingerprint_screen_2026-07.md] \
      [--plan-only]     # eligibility counts + input checks, no activations needed
"""

import argparse
import datetime
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:  # running as a plain script
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    from runner_lib import atomic_write, file_digest

PRODUCED_BY = "Claude Fable 5 (model id claude-fable-5)"

# ---- constants mirrored from notebooks/pretest_analysis.ipynb (locked D35) --
MASS_FLOOR = 0.20

# ---- provisional screen defaults (see module docstring) --------------------
RELIABILITY_THRESHOLD = 0.5
SIM_CEILING_RATIO = 0.8

# Twelve-type battery slate, docs/WEEK_PLAN_stage2.md (type 2 and type 10
# share the privacy-care pairing). Used only for flag condition (iii).
BATTERY_TYPES = {
    1: ("honesty", "care"), 2: ("privacy", "care"), 3: ("mercy", "desert"),
    4: ("loyalty", "honesty"), 5: ("tradition", "autonomy"),
    6: ("authority", "autonomy"), 7: ("harm_avoidance", "autonomy"),
    8: ("harm_avoidance", "privacy"), 9: ("harm_avoidance", "integrity"),
    10: ("privacy", "care"), 11: ("integrity", "mercy"),
    12: ("autonomy", "collective_welfare"),
}


def battery_pairs():
    out = defaultdict(list)
    for t, (a, b) in BATTERY_TYPES.items():
        out[frozenset((a, b))].append(t)
    return out


# ---------------------------------------------------------------------------
# Eligibility (CSV-side; no activations needed)
# ---------------------------------------------------------------------------

def load_probe_values(probes_path: Path):
    """probe_id -> value, from the frozen instrument."""
    out = {}
    for line in probes_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if "probe_id" in rec and "value" in rec:
            out[rec["probe_id"]] = rec["value"]
    return out


def eligible_cells(gen_rows, probe_values, c3_pairs, mass_floor=MASS_FLOOR):
    """-> {value: {(probe_id, role): {"neutral": prompt_key, "value": prompt_key}}}
    over choice cells that are: main block, base cell, complete (both
    variants), non-C3, and mass-eligible (min variant mass ≥ floor).
    Also returns per-cell audit rows for the output manifest."""
    cells = defaultdict(dict)  # (probe_id, role) -> {variant: (key, mass)}
    for row in gen_rows:
        if row.get("variant") not in ("neutral", "value"):
            continue
        if row.get("block") != "main":
            continue
        if str(row.get("is_base_cell", "")) not in ("1", "1.0", "True"):
            continue
        cell = (row["probe_id"], row.get("role") or "")
        cells[cell][row["variant"]] = (row["prompt_key"],
                                       float(row["mass_combined"]))
    out, audit = defaultdict(dict), []
    for (probe_id, role), variants in sorted(cells.items()):
        complete = set(variants) == {"neutral", "value"}
        mass_min = (min(variants["neutral"][1], variants["value"][1])
                    if complete else float("nan"))
        c3 = (probe_id, role) in c3_pairs
        eligible = complete and not c3 and mass_min >= mass_floor
        value = probe_values.get(probe_id)
        audit.append({"value": value, "probe_id": probe_id, "role": role,
                      "complete": complete, "c3_dropped": c3,
                      "mass_min": None if math.isnan(mass_min) else round(mass_min, 4),
                      "eligible": eligible})
        if eligible and value is not None:
            out[value][(probe_id, role)] = {
                "neutral": variants["neutral"][0],
                "value": variants["value"][0]}
    return out, audit


# ---------------------------------------------------------------------------
# Fingerprint math (numpy only — torch is confined to the loader)
# ---------------------------------------------------------------------------

def fingerprint(acts, cells, pair_subset=None):
    """mean(value-variant) − mean(neutral-twin) per layer -> [L, d] float64.
    acts: prompt_key -> [L, d] ndarray. cells: {(probe_id, role): {variant: key}}.
    pair_subset: restrict to these probe_ids (split-half); None = all."""
    v_stack, n_stack = [], []
    for (probe_id, _role), keys in sorted(cells.items()):
        if pair_subset is not None and probe_id not in pair_subset:
            continue
        v_stack.append(acts[keys["value"]])
        n_stack.append(acts[keys["neutral"]])
    if not v_stack:
        raise ValueError("no cells in subset")
    return (np.mean(np.stack(v_stack), axis=0, dtype=np.float64)
            - np.mean(np.stack(n_stack), axis=0, dtype=np.float64))


def unit_normalize(fp):
    """Row-normalize [L, d] to unit vectors (zero rows left zero)."""
    norms = np.linalg.norm(fp, axis=1, keepdims=True)
    return np.divide(fp, norms, out=np.zeros_like(fp), where=norms > 0)


def cosine_per_layer(a, b):
    num = (a * b).sum(axis=1)
    den = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    return np.divide(num, den, out=np.zeros_like(num), where=den > 0)


def balanced_splits(pairs):
    """All balanced partitions of pair ids into (half_a, half_b),
    |half_a| = n // 2. For even n, complementary duplicates are removed by
    anchoring the lexicographically first pair in half_a."""
    pairs = sorted(pairs)
    n = len(pairs)
    if n < 2:
        return []
    k = n // 2
    out = []
    for combo in itertools.combinations(pairs, k):
        if n % 2 == 0 and pairs[0] not in combo:
            continue  # complement already enumerated
        half_a = set(combo)
        out.append((half_a, set(pairs) - half_a))
    return out


def split_half_reliability(acts, cells):
    """-> (mean cosine per layer [L], n_pairs, n_splits). Splits by scenario
    pair (probe_id), never by role."""
    pair_ids = sorted({probe_id for probe_id, _ in cells})
    splits = balanced_splits(pair_ids)
    if not splits:
        return None, len(pair_ids), 0
    cosines = []
    for half_a, half_b in splits:
        fa = fingerprint(acts, cells, half_a)
        fb = fingerprint(acts, cells, half_b)
        cosines.append(cosine_per_layer(fa, fb))
    return np.mean(np.stack(cosines), axis=0), len(pair_ids), len(splits)


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def load_activations(act_path: Path, needed_keys):
    """torch is imported here and nowhere else. Returns
    {prompt_key: [L, d] float32 ndarray} for needed_keys plus (n_layers, d)."""
    import torch
    blob = torch.load(act_path, map_location="cpu", weights_only=True)
    if blob.get("partial", True):
        raise RuntimeError(f"{act_path.name} has partial=True — refusing "
                           f"(incomplete checkpoint)")
    acts_t = blob["activations"]
    missing = [k for k in needed_keys if k not in acts_t]
    if missing:
        raise RuntimeError(f"{len(missing)} needed prompt_keys missing from "
                           f"activations (first: {missing[:3]})")
    acts = {k: acts_t[k].numpy().astype(np.float32) for k in needed_keys}
    return acts, blob["n_layers"], blob["d_model"]


def write_csv(path: Path, header, rows):
    import csv

    def _w(f):
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    atomic_write(path, _w, mode="w", newline="", encoding="utf-8")
    sha, size = file_digest(path)
    print(f"DIGEST {sha} {size} {path.name}")
    return {"sha256": sha, "bytes": size}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", default="results/pretest/"
                    "20260717_204822_llama8b_instrument_validation_merged")
    ap.add_argument("--probes", default="data/pretest/pretest_probes_v2.jsonl")
    ap.add_argument("--out-root", default="results/fingerprint_screen")
    ap.add_argument("--summary", default="docs/fingerprint_screen_2026-07.md")
    ap.add_argument("--mass-floor", type=float, default=MASS_FLOOR)
    ap.add_argument("--plan-only", action="store_true",
                    help="eligibility + input verification only (no activations)")
    args = ap.parse_args(argv)

    import csv
    run_dir = Path(args.run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    subject_model = manifest["model"]
    model_tag = manifest["model_tag"]

    # ---- input verification before any computation ----
    failures = []

    def check(name, ok, detail=""):
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)
        return ok

    probes_path = Path(args.probes)
    p_sha, _ = file_digest(probes_path)
    check("probe file sha256 matches manifest",
          p_sha == manifest["probe_file_sha256"],
          f"{p_sha[:12]}…")

    act_name = f"activations_{model_tag}.pt"
    act_path = run_dir / act_name
    act_expected = manifest.get("output_digests", {}).get(act_name, {})
    if not args.plan_only:
        if not act_path.exists():
            check(f"{act_name} present", False,
                  f"expected sha256 {act_expected.get('sha256', '?')[:12]}…, "
                  f"{act_expected.get('bytes', '?')} bytes — volume-resident "
                  f"artifact; place it in {run_dir} (or run --plan-only)")
        else:
            a_sha, a_size = file_digest(act_path)
            check(f"{act_name} sha256 matches manifest output_digests",
                  a_sha == act_expected.get("sha256") and
                  a_size == act_expected.get("bytes"),
                  f"{a_sha[:12]}…, {a_size} bytes")
    if failures:
        print("SCREEN FAIL — input verification failed; nothing computed")
        return 1

    with open(run_dir / "generations.csv", newline="", encoding="utf-8") as f:
        gen_rows = list(csv.DictReader(f))
    with open(run_dir / f"c3_dropped_pairs_{model_tag}.csv",
              newline="", encoding="utf-8") as f:
        c3_pairs = {(r["probe_id_base"], r.get("role") or "")
                    for r in csv.DictReader(f)}
    probe_values = load_probe_values(probes_path)

    cells_by_value, audit = eligible_cells(gen_rows, probe_values, c3_pairs,
                                           args.mass_floor)
    n_cells = sum(len(c) for c in cells_by_value.values())
    print(f"eligible cells: {n_cells} across {len(cells_by_value)} values "
          f"(mass floor {args.mass_floor}, non-C3, base, main, complete)")
    for v in sorted(cells_by_value):
        pairs = {p for p, _ in cells_by_value[v]}
        print(f"  {v:<20} {len(cells_by_value[v]):>3} cells, {len(pairs)} pairs")
    if args.plan_only:
        print("PLAN-ONLY — stopping before activation load")
        return 0

    # ---- output dir (timestamped, never overwritten) ----
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_root) / f"{stamp}_{model_tag}"
    out_dir.mkdir(parents=True, exist_ok=False)
    out_digests = {}

    needed = [k for cells in cells_by_value.values()
              for c in cells.values() for k in c.values()]
    acts, n_layers, d_model = load_activations(act_path, needed)
    print(f"loaded {len(acts)} activation sets [{n_layers} layers x {d_model}]")

    # ---- step 1: reliability (written before similarity is computed) ----
    reliability, rel_rows = {}, []
    for value in sorted(cells_by_value):
        rel, n_pairs, n_splits = split_half_reliability(acts, cells_by_value[value])
        reliability[value] = {"rel": rel, "n_pairs": n_pairs, "n_splits": n_splits}
        if rel is None:
            rel_rows.append([value, n_pairs, n_splits, "", "", "NOT-ESTIMABLE"])
            continue
        best_layer = int(np.argmax(rel))
        status = ("RELIABLE" if rel[best_layer] >= RELIABILITY_THRESHOLD
                  else "UNRELIABLE")
        rel_rows.append([value, n_pairs, n_splits, best_layer,
                         round(float(rel[best_layer]), 4), status])
    out_digests["reliability.csv"] = write_csv(
        out_dir / "reliability.csv",
        ["value", "n_pairs", "n_splits", "best_layer",
         "best_layer_reliability", "status"], rel_rows)
    rel_layer_rows = [[v, l, round(float(r["rel"][l]), 6)]
                      for v, r in sorted(reliability.items()) if r["rel"] is not None
                      for l in range(n_layers)]
    out_digests["reliability_layers.csv"] = write_csv(
        out_dir / "reliability_layers.csv",
        ["value", "layer", "split_half_cosine"], rel_layer_rows)

    status_by_value = {row[0]: row[5] for row in rel_rows}

    # ---- step 2: pairwise similarity among reliable fingerprints ----
    raw_fps = {v: fingerprint(acts, cells_by_value[v])
               for v in sorted(cells_by_value)}
    fps = {v: unit_normalize(fp) for v, fp in raw_fps.items()}
    fp_rows = [[v, l, round(float(np.linalg.norm(raw_fps[v][l])), 6)]
               for v in sorted(raw_fps) for l in range(n_layers)]
    out_digests["fingerprint_norms.csv"] = write_csv(
        out_dir / "fingerprint_norms.csv",
        ["value", "layer", "raw_norm"], fp_rows)

    values = sorted(fps)
    sim_layer_rows, sim_summary_rows = [], []
    bpairs = battery_pairs()
    flags = []
    for va, vb in itertools.combinations(values, 2):
        cos = cosine_per_layer(fps[va], fps[vb])
        for l in range(n_layers):
            sim_layer_rows.append([va, vb, l, round(float(cos[l]), 6)])
        ra, rb = reliability[va]["rel"], reliability[vb]["rel"]
        both_estimable = ra is not None and rb is not None
        if both_estimable:
            shared = np.minimum(ra, rb)
            best_l = int(np.argmax(shared))
            ceiling = math.sqrt(max(float(ra[best_l]), 0.0) *
                                max(float(rb[best_l]), 0.0))
            sim_at = float(cos[best_l])
            ratio = (sim_at / ceiling) if ceiling > 0 else float("nan")
            both_reliable = (status_by_value[va] == "RELIABLE"
                             and status_by_value[vb] == "RELIABLE"
                             and float(ra[best_l]) >= RELIABILITY_THRESHOLD
                             and float(rb[best_l]) >= RELIABILITY_THRESHOLD)
            in_battery = sorted(bpairs.get(frozenset((va, vb)), []))
            flagged = (both_reliable and not math.isnan(ratio)
                       and ratio >= SIM_CEILING_RATIO and bool(in_battery))
            sim_summary_rows.append(
                [va, vb, best_l, round(sim_at, 4),
                 round(float(ra[best_l]), 4), round(float(rb[best_l]), 4),
                 round(ceiling, 4),
                 round(ratio, 4) if not math.isnan(ratio) else "",
                 both_reliable,
                 ";".join(f"type{t}" for t in in_battery), flagged])
            if flagged:
                flags.append((va, vb, best_l, sim_at, ceiling, ratio, in_battery))
        else:
            sim_summary_rows.append([va, vb, "", "", "", "", "", "", False,
                                     ";".join(f"type{t}" for t in
                                              sorted(bpairs.get(
                                                  frozenset((va, vb)), []))),
                                     False])
    out_digests["similarity_layers.csv"] = write_csv(
        out_dir / "similarity_layers.csv",
        ["value_a", "value_b", "layer", "cosine"], sim_layer_rows)
    out_digests["similarity_summary.csv"] = write_csv(
        out_dir / "similarity_summary.csv",
        ["value_a", "value_b", "best_shared_layer", "cosine_at_best",
         "rel_a_at_best", "rel_b_at_best", "ceiling_sqrt_ra_rb",
         "cos_over_ceiling", "both_reliable", "battery_types", "flagged"],
        sim_summary_rows)
    out_digests["eligibility_audit.csv"] = write_csv(
        out_dir / "eligibility_audit.csv",
        ["value", "probe_id", "role", "complete", "c3_dropped", "mass_min",
         "eligible"],
        [[a["value"], a["probe_id"], a["role"], a["complete"],
          a["c3_dropped"], a["mass_min"], a["eligible"]] for a in audit])

    # ---- step 3: summary doc ----
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    lines = []
    lines.append("# Value-fingerprint screen — pre-test activations (2026-07)")
    lines.append("")
    lines.append(f"Produced by: {PRODUCED_BY}")
    lines.append(f"Generated: {now} — `src/analysis/fingerprint_screen.py` "
                 f"-> `{out_dir.as_posix()}`")
    lines.append(f"Subject model of the underlying data: **{subject_model}** "
                 f"(merged IV run `{manifest['run_id']}`, instrument sha256 "
                 f"`{manifest['probe_file_sha256'][:8]}…`).")
    lines.append("")
    lines.append("**This is a screen, not a finding.** The pre-test confounds "
                 "value with topic by design (each value's probes live in "
                 "their own scenarios), so similarity here is **suggestive, "
                 "not diagnostic**. Flags only — no verdicts. Its one "
                 "actionable output: a flagged pairing that co-occurs in a "
                 "planned battery tension type deserves reconsideration "
                 "before that type is authored.")
    lines.append("")
    lines.append(f"Fingerprint: mean(value-variant) − mean(neutral-twin) anchor "
                 f"activation, per layer ({n_layers} layers, d={d_model}), "
                 f"unit-normalized; {n_cells} eligible cells (choice channel, "
                 f"main block, base cells, complete, non-C3, mass floor "
                 f"{args.mass_floor}). Split-half by scenario pair, never by "
                 f"role. Provisional defaults (researcher may override): "
                 f"reliable = split-half cosine ≥ {RELIABILITY_THRESHOLD} at "
                 f"the layer in question; flag threshold = cosine ≥ "
                 f"{SIM_CEILING_RATIO} × ceiling, ceiling = √(rel_a·rel_b).")
    lines.append("")
    lines.append("## Reliability (existence gate for interpretation)")
    lines.append("")
    lines.append("| value | pairs | splits | best layer | reliability | status |")
    lines.append("|---|---|---|---|---|---|")
    for row in rel_rows:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    lines.append("")
    lines.append("## Similarity at best shared-reliability layer")
    lines.append("")
    lines.append("Full per-layer matrices: `similarity_layers.csv`. Pairs "
                 "involving a NOT-ESTIMABLE value are omitted from "
                 "interpretation; UNRELIABLE values are shown but not "
                 "flag-eligible.")
    lines.append("")
    lines.append("| pair | layer | cosine | ceiling | cos/ceiling | battery? | flagged |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in sim_summary_rows:
        if r[2] == "":
            continue
        lines.append(f"| {r[0]}–{r[1]} | {r[2]} | {r[3]} | {r[6]} | {r[7]} | "
                     f"{r[9] or ''} | {'**FLAG**' if r[10] else ''} |")
    lines.append("")
    lines.append("## Flag list")
    lines.append("")
    if flags:
        for va, vb, l, sim, ceil, ratio, types in flags:
            lines.append(f"- **{va}–{vb}** (battery "
                         f"{', '.join(f'type {t}' for t in types)}): cosine "
                         f"{sim:.3f} at layer {l} vs ceiling {ceil:.3f} "
                         f"(ratio {ratio:.2f}) — both reliable. Reconsider "
                         f"this pairing before authoring.")
    else:
        lines.append("- No value pair met all three flag conditions "
                     "(both reliable; similarity ≥ "
                     f"{SIM_CEILING_RATIO} × ceiling; co-occur in a planned "
                     "battery type).")
    lines.append("")
    lines.append("Reminder: topic confound (above) — a flag is a prompt to "
                 "reconsider, a clean screen is not evidence of distinctness.")
    lines.append("")
    text = "\n".join(lines)
    summary_path = Path(args.summary)
    atomic_write(summary_path, lambda fh: fh.write(text),
                 mode="w", encoding="utf-8", newline="\n")
    s_sha, s_size = file_digest(summary_path)
    print(f"DIGEST {s_sha} {s_size} {summary_path.name}")

    screen_manifest = {
        "run_id": out_dir.name,
        "run_role": "fingerprint_screen",
        "produced_by": PRODUCED_BY,
        "subject_model": subject_model,
        "model_tag": model_tag,
        "source_run": manifest["run_id"],
        "probe_file_sha256": p_sha,
        "activations_sha256": act_expected.get("sha256"),
        "mass_floor": args.mass_floor,
        "reliability_threshold": RELIABILITY_THRESHOLD,
        "sim_ceiling_ratio": SIM_CEILING_RATIO,
        "n_eligible_cells": n_cells,
        "n_layers": n_layers,
        "d_model": d_model,
        "timestamp_utc": now,
        "output_digests": out_digests | {
            summary_path.name: {"sha256": s_sha, "bytes": s_size}},
    }
    mpath = out_dir / "manifest.json"
    atomic_write(mpath, lambda fh: fh.write(
        json.dumps(screen_manifest, indent=2) + "\n"),
        mode="w", encoding="utf-8", newline="\n")
    m_sha, m_size = file_digest(mpath)
    print(f"DIGEST {m_sha} {m_size} {mpath.name}")
    print(f"Wrote {summary_path} and {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
