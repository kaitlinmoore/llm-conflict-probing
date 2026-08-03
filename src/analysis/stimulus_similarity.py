#!/usr/bin/env python3
"""
stimulus_similarity.py — embedding-based stimulus-property analysis of the
conflict battery (descriptive validation exhibit; researcher-approved
2026-07-31).

Purpose on the record: a quantitative stimulus-property control for the topic
confound, plus a semantic-leakage tripwire, produced by an instrument
INDEPENDENT of the subject model. **Descriptive, not gating** — no pass/fail
thresholds, no rewrite triggers, no edit recommendations. Nothing here selects
or rejects any item.

Independence requirement: no Llama-derived embeddings anywhere. The
Llama-native topic baseline comes free from the battery run's early-layer
captures later; duplicating it here would defeat the point of an independent
instrument.

Sequencing (researcher): run only on freeze-candidate text — after the
pending-edits batch has been applied, re-ingested, and re-validated. The
script reads the INGESTED drafts, not raw workbook cells, so what is measured
is what will be administered, and it records the ingest digests in every
artifact. `--provisional` marks a plumbing run on non-freeze text so its
outputs can never be mistaken for the exhibit.

Encoders: mean-pooled (attention-masked) then L2-normalized, computed with
`transformers` directly — sentence-transformers is not in the pinned stack and
adding dependencies is ask-first. This is the same arithmetic those models'
sentence-transformers configs perform.

Analyses (priority order per the brief):
  1. type-by-type similarity matrix (all cells; plus opposition-only variant)
     + pre-registered worry spots with rank/percentile
  2. cell-by-value-anchor matrix -> third-value flags (actionable) and
     own-value similarities (reported, NOT a presence check)
  3. minimal-pair tightness (opposition siblings) + outliers
  4. tipping-sentence symmetry vs. the shared text + outliers
  5. topical-control placement
  6. encoder agreement (Spearman + Pearson on type-pair matrices; flag-set
     agreement)

Usage:
  python src/analysis/stimulus_similarity.py                 # exhibit run
  python src/analysis/stimulus_similarity.py --provisional   # plumbing only
"""

import argparse
import csv
import datetime
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    from runner_lib import atomic_write, file_digest

PRODUCED_BY = "Claude Fable 5 (model id claude-fable-5)"

# Encoders. Primary and robustness must come from different families; both are
# outside the Llama lineage by construction (MPNet and BERT-distilled MiniLM).
ENCODERS = {
    "primary": {
        "name": "sentence-transformers/all-mpnet-base-v2",
        "family": "MPNet (Microsoft) bi-encoder",
        "pooling": "mean over attention-masked tokens, then L2 normalize",
    },
    "robustness": {
        "name": "sentence-transformers/all-MiniLM-L6-v2",
        "family": "MiniLM (BERT-distilled) bi-encoder",
        "pooling": "mean over attention-masked tokens, then L2 normalize",
    },
}

# Pre-registered worry spots (HANDOFF_v6; screen-elevated pairings D47).
WORRY_SPOTS = [
    ("type2_privacy_vs_care", "type10_privacy_vs_care",
     "same value pair, deliberate topic divergence"),
    ("type8_harm_vs_privacy", "type2_privacy_vs_care",
     "shared privacy pole, screen-elevated harm_avoidance-privacy"),
    ("type9_harm_vs_integrity", "type8_harm_vs_privacy",
     "shared harm pole"),
    ("type9_harm_vs_integrity", "type7_harm_vs_autonomy",
     "shared harm pole"),
    ("type9_harm_vs_integrity", "type11_integrity_vs_mercy",
     "shared integrity pole"),
]

OUTLIER_Z = 2.0          # descriptive outlier marker only, not a threshold
TOP_DECILE = 0.90


# ---------------------------------------------------------------------------
# Text assembly
# ---------------------------------------------------------------------------

def cell_text(rec, mode="full"):
    """Assembled stimulus for one cell.

    `full` (default): stem + shared opposition text (opposition cells only) +
    condition insert — the text as administered. The brief's phrasing was
    "stem + condition insert, exactly as administered"; for opposition cells
    the shared conflict text IS administered, and dropping it would make
    opposition cells collapse onto their agreement siblings. `stem_insert`
    implements the narrower literal reading for comparison. Open question in
    the report.
    """
    parts = [rec.get("stem", "")]
    if mode == "full" and (rec.get("shared_opposition_text") or ""):
        parts.append(rec["shared_opposition_text"])
    parts.append(rec.get("condition_insert", ""))
    return " ".join(p.strip() for p in parts if p and p.strip())


def load_units(drafts_dir: Path, competition: Path, mode: str):
    """-> (units, digests). Each unit: id, kind, type_id, scenario_id,
    condition, text."""
    units, digests = [], {}
    for path in sorted(drafts_dir.glob("*.jsonl")):
        sha, size = file_digest(path)
        digests[path.name] = {"sha256": sha, "bytes": size}
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("record_type") == "topical_control":
                units.append({
                    "id": f"{r['type_id']}:{r['control_id']}",
                    "kind": "control", "type_id": r["type_id"],
                    "scenario_id": r["control_id"], "condition": "",
                    "family": r.get("family", ""),
                    "text": " ".join(x for x in (r.get("stem", ""),
                                                 r.get("option_A", ""),
                                                 r.get("option_B", "")) if x),
                })
            else:
                units.append({
                    "id": f"{r['type_id']}:{r['scenario_id']}:{r['condition']}",
                    "kind": "cell", "type_id": r["type_id"],
                    "scenario_id": r["scenario_id"],
                    "condition": r.get("condition", ""),
                    "family": r.get("family", ""),
                    "text": cell_text(r, mode),
                })
    if competition.exists():
        sha, size = file_digest(competition)
        digests[competition.name] = {"sha256": sha, "bytes": size}
        for line in competition.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            units.append({
                "id": f"competition:{r['item_id']}", "kind": "competition",
                "type_id": f"competition_{r['condition']}",
                "scenario_id": r["item_id"], "condition": r["condition"],
                "family": "competition",
                "text": " ".join([r.get("stem", ""), r.get("option_A", ""),
                                  r.get("option_B", "")]),
            })
    return units, digests


def load_shared_texts(drafts_dir: Path, mode: str):
    """scenario -> shared opposition text (for tip-symmetry)."""
    out = {}
    for path in sorted(drafts_dir.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            txt = r.get("shared_opposition_text") or ""
            if txt.strip():
                out[f"{r['type_id']}:{r['scenario_id']}"] = txt.strip()
    return out


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed(texts, model_name, batch_size=16):
    """Mean-pooled, L2-normalized embeddings. Returns (array, revision)."""
    import torch
    from transformers import AutoModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    revision = getattr(getattr(model, "config", None), "_commit_hash", None)
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tok(batch, padding=True, truncation=True, max_length=512,
                      return_tensors="pt")
            hidden = model(**enc).last_hidden_state
            mask = enc["attention_mask"].unsqueeze(-1).float()
            pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            out.append(pooled.cpu().numpy().astype(np.float32))
    return np.vstack(out), revision


# ---------------------------------------------------------------------------
# Analyses
# ---------------------------------------------------------------------------

def mean_pair_similarity(emb, idx_a, idx_b):
    """Mean cosine between two index groups (excluding self-pairs if same)."""
    if not idx_a or not idx_b:
        return float("nan")
    sub = emb[idx_a] @ emb[idx_b].T
    if idx_a == idx_b:
        n = len(idx_a)
        if n < 2:
            return float("nan")
        iu = np.triu_indices(n, k=1)
        return float(sub[iu].mean())
    return float(sub.mean())


def type_matrix(units, emb, restrict=None):
    """-> (types, matrix). restrict: predicate on unit."""
    groups = defaultdict(list)
    for i, u in enumerate(units):
        if u["kind"] != "cell":
            continue
        if restrict and not restrict(u):
            continue
        groups[u["type_id"]].append(i)
    types = sorted(groups)
    m = np.full((len(types), len(types)), np.nan)
    for a, ta in enumerate(types):
        for b, tb in enumerate(types):
            if b < a:
                m[a, b] = m[b, a]
            else:
                m[a, b] = mean_pair_similarity(emb, groups[ta], groups[tb])
    return types, m


def offdiag_values(types, m):
    return [(types[a], types[b], m[a, b])
            for a, b in combinations(range(len(types)), 2)
            if not np.isnan(m[a, b])]


def anchor_matrix(units, emb, anchors, anchor_emb):
    """-> (cell_ids, value_keys, matrix[cells, values])."""
    idx = [i for i, u in enumerate(units) if u["kind"] == "cell"]
    keys = [a["value"] for a in anchors]
    return ([units[i]["id"] for i in idx], keys, emb[idx] @ anchor_emb.T)


def third_value_flags(units, cell_ids, keys, mat, type_poles):
    """A non-rostered value is flagged for a type when its mean similarity to
    that type's cells ranks above one of the type's OWN poles, or sits in the
    top decile of the whole cell-by-value distribution."""
    by_type = defaultdict(list)
    id_to_row = {cid: r for r, cid in enumerate(cell_ids)}
    for u in units:
        if u["kind"] == "cell" and u["id"] in id_to_row:
            by_type[u["type_id"]].append(id_to_row[u["id"]])
    global_cut = float(np.quantile(mat, TOP_DECILE))
    flags, per_type_means = [], {}
    for tid, rows in sorted(by_type.items()):
        means = mat[rows].mean(axis=0)
        per_type_means[tid] = dict(zip(keys, means.tolist()))
        poles = [p for p in type_poles.get(tid, []) if p in keys]
        own_scores = [means[keys.index(p)] for p in poles]
        worst_own = min(own_scores) if own_scores else None
        for j, k in enumerate(keys):
            if k in poles:
                continue
            above_own = worst_own is not None and means[j] > worst_own
            top_decile = means[j] >= global_cut
            if above_own or top_decile:
                culprits = sorted(
                    ((cell_ids[r], float(mat[r, j])) for r in rows),
                    key=lambda x: -x[1])[:3]
                flags.append({
                    "type_id": tid, "value": k,
                    "mean_similarity": float(means[j]),
                    "ranks_above_own_pole": bool(above_own),
                    "worst_own_pole": (None if worst_own is None
                                       else float(worst_own)),
                    "own_poles": poles,
                    "in_top_decile": bool(top_decile),
                    "top_cells": culprits,
                })
    return flags, per_type_means, global_cut


def relative_value_affinity(per_type_means, keys, type_poles, z_cut=2.0):
    """Diagnostic ADDITION (Claude's, clearly labelled — not a substitute for
    the ratified rule).

    Why: the ratified operationalization ("a non-pole value ranks above one of
    the type's own poles, or sits in the top decile") turns out to be
    non-discriminative on this corpus, and for a structural reason the brief
    itself names — authoring rule 7 strips value vocabulary, so own-pole
    similarity is LOW by design, which makes "above an own pole" a floor
    almost everything clears. It fires on ~56% of type-value combinations.

    This diagnostic asks the contamination question directly: is this type
    unusually close to value V *relative to how close every other type is to
    V*? Standardizing within a value also cancels the constant offset from the
    anchors' shared "Pull toward/against …" frame, which inflates some anchors
    against all text.

    -> rows sorted by z descending; a row is `flagged` when z >= z_cut and the
    value is not one of the type's own poles.

    Bound worth knowing: standardizing across n types caps z at
    (n-1)/sqrt(n) — about 3.18 at n=12. So z >= 2.0 is a real but not extreme
    bar here, and the statistic could not reach 2.0 at all with a handful of
    types. Reported rather than tuned.
    """
    types = sorted(per_type_means)
    rows = []
    for k in keys:
        col = np.array([per_type_means[t][k] for t in types], dtype=float)
        mu, sd = col.mean(), col.std(ddof=1) if len(col) > 1 else 0.0
        for i, t in enumerate(types):
            z = float((col[i] - mu) / sd) if sd > 0 else 0.0
            is_pole = k in type_poles.get(t, [])
            rows.append({"type_id": t, "value": k, "mean": float(col[i]),
                         "z_within_value": z, "is_own_pole": is_pole,
                         "flagged": bool(z >= z_cut and not is_pole)})
    return sorted(rows, key=lambda r: -r["z_within_value"])


def minimal_pair_tightness(units, emb):
    """Distance (1 - cosine) between the two opposition siblings per scenario."""
    by_scen = defaultdict(dict)
    for i, u in enumerate(units):
        if u["kind"] == "cell" and u["condition"].startswith("oppose"):
            by_scen[f"{u['type_id']}:{u['scenario_id']}"][u["condition"]] = i
    rows = []
    for scen, conds in sorted(by_scen.items()):
        if len(conds) != 2:
            continue
        (ca, ia), (cb, ib) = sorted(conds.items())
        rows.append({"scenario": scen, "cond_a": ca, "cond_b": cb,
                     "distance": float(1.0 - emb[ia] @ emb[ib])})
    return rows


def tip_symmetry(units, emb, shared_idx):
    """|d(tipA, shared) - d(tipB, shared)| per scenario."""
    by_scen = defaultdict(dict)
    for i, u in enumerate(units):
        if u["kind"] == "cell" and u["condition"].startswith("oppose"):
            by_scen[f"{u['type_id']}:{u['scenario_id']}"][u["condition"]] = i
    rows = []
    for scen, conds in sorted(by_scen.items()):
        if len(conds) != 2 or scen not in shared_idx:
            continue
        s = shared_idx[scen]
        (ca, ia), (cb, ib) = sorted(conds.items())
        da = float(1.0 - emb[ia] @ emb[s])
        db = float(1.0 - emb[ib] @ emb[s])
        rows.append({"scenario": scen, "cond_a": ca, "d_a": da,
                     "cond_b": cb, "d_b": db, "asymmetry": abs(da - db)})
    return rows


def control_placement(units, emb):
    """Each control vs. its own type's cells, vs. the rest of the battery."""
    cells_by_type = defaultdict(list)
    for i, u in enumerate(units):
        if u["kind"] == "cell":
            cells_by_type[u["type_id"]].append(i)
    rows = []
    for i, u in enumerate(units):
        if u["kind"] != "control":
            continue
        own = cells_by_type.get(u["type_id"], [])
        other = [j for t, idx in cells_by_type.items() if t != u["type_id"]
                 for j in idx]
        rows.append({
            "control": u["id"], "type_id": u["type_id"],
            "sim_to_own_type": mean_pair_similarity(emb, [i], own),
            "sim_to_rest": mean_pair_similarity(emb, [i], other),
        })
    for r in rows:
        r["margin"] = r["sim_to_own_type"] - r["sim_to_rest"]
    return rows


def outliers(rows, key):
    vals = np.array([r[key] for r in rows], dtype=float)
    if len(vals) < 3:
        return [], float("nan"), float("nan")
    mu, sd = float(vals.mean()), float(vals.std(ddof=1))
    if sd == 0:
        return [], mu, sd
    return ([r for r in rows if abs(r[key] - mu) / sd >= OUTLIER_Z], mu, sd)


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def write_csv(path: Path, header, rows, digests):
    def _w(f):
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    atomic_write(path, _w, mode="w", newline="", encoding="utf-8")
    sha, size = file_digest(path)
    digests[path.name] = {"sha256": sha, "bytes": size}
    print(f"DIGEST {sha} {size} {path.name}")


def heatmap(path: Path, labels_y, labels_x, mat, title, digests):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig_w = max(6, 0.55 * len(labels_x) + 4)
    fig_h = max(5, 0.45 * len(labels_y) + 3)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    im = ax.imshow(mat, aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(labels_x)))
    ax.set_xticklabels(labels_x, rotation=90, fontsize=7)
    ax.set_yticks(range(len(labels_y)))
    ax.set_yticklabels(labels_y, fontsize=7)
    ax.set_title(title, fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.8, label="cosine")
    fig.tight_layout()
    tmp = f"{path}.tmp"
    fig.savefig(tmp, dpi=150, format="png")   # tmp suffix defeats inference
    plt.close(fig)
    Path(tmp).replace(path)
    sha, size = file_digest(path)
    digests[path.name] = {"sha256": sha, "bytes": size}
    print(f"DIGEST {sha} {size} {path.name}")


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--drafts", default="data/battery/drafts")
    ap.add_argument("--competition",
                    default="data/comparators/competition_battery_draft.jsonl")
    ap.add_argument("--anchors", default="data/battery/value_anchors.json")
    ap.add_argument("--out-root", default="results/stimulus_similarity")
    ap.add_argument("--cell-text", choices=["full", "stem_insert"],
                    default="full")
    ap.add_argument("--provisional", action="store_true",
                    help="mark outputs as a plumbing run on non-freeze text")
    ap.add_argument("--limit-encoders", type=int, default=2)
    args = ap.parse_args(argv)

    drafts_dir = Path(args.drafts)
    units, digests_in = load_units(drafts_dir, Path(args.competition),
                                   args.cell_text)
    shared_texts = load_shared_texts(drafts_dir, args.cell_text)
    anchors_blob = json.loads(Path(args.anchors).read_text(encoding="utf-8"))
    anchors = anchors_blob["anchors"]
    a_sha, _ = file_digest(Path(args.anchors))

    type_poles = {}
    for u in units:
        if u["kind"] == "cell" and u["type_id"] not in type_poles:
            body = u["type_id"].split("_", 1)[1]
            type_poles[u["type_id"]] = body.split("_vs_")
    # roster keys differ from filename tokens for two values
    alias = {"harm": "harm_avoidance", "collective": "collective_welfare"}
    type_poles = {t: [alias.get(p, p) for p in ps]
                  for t, ps in type_poles.items()}

    n_cells = sum(1 for u in units if u["kind"] == "cell")
    print(f"units: {len(units)} ({n_cells} cells, "
          f"{sum(1 for u in units if u['kind'] == 'control')} controls, "
          f"{sum(1 for u in units if u['kind'] == 'competition')} competition)")
    print(f"anchors: {len(anchors)}; flagged: "
          f"{[a['value'] for a in anchors if 'flag' in a]}")

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    ingest_tag = digests_in.get("ingest_manifest.json", {}).get("sha256", "")
    short = (ingest_tag or "noingest")[:8]
    tag = f"{stamp}_ing{short}" + ("_PROVISIONAL" if args.provisional else "")
    out_dir = Path(args.out_root) / tag
    out_dir.mkdir(parents=True, exist_ok=False)

    texts = [u["text"] for u in units]
    shared_keys = sorted(shared_texts)
    all_texts = texts + [a["anchor_text"] for a in anchors] + \
                [shared_texts[k] for k in shared_keys]

    results, digests_out = {}, {}
    for role, spec in list(ENCODERS.items())[:args.limit_encoders]:
        print(f"\n--- encoder [{role}] {spec['name']} ---")
        emb_all, revision = embed(all_texts, spec["name"])
        n_u, n_a = len(units), len(anchors)
        emb = emb_all[:n_u]
        anchor_emb = emb_all[n_u:n_u + n_a]
        shared_idx = {k: n_u + n_a + i for i, k in enumerate(shared_keys)}
        emb_full = emb_all

        types, m_all = type_matrix(units, emb)
        _, m_opp = type_matrix(units, emb,
                               restrict=lambda u: u["condition"].startswith("oppose"))
        cell_ids, keys, amat = anchor_matrix(units, emb, anchors, anchor_emb)
        flags, per_type_means, cut = third_value_flags(
            units, cell_ids, keys, amat, type_poles)
        rel = relative_value_affinity(per_type_means, keys, type_poles)
        mp = minimal_pair_tightness(units, emb)
        ts = tip_symmetry(units, emb_full, shared_idx)
        cp = control_placement(units, emb)
        mp_out, mp_mu, mp_sd = outliers(mp, "distance")
        ts_out, ts_mu, ts_sd = outliers(ts, "asymmetry")

        results[role] = {
            "spec": spec, "revision": revision, "types": types,
            "m_all": m_all, "m_opp": m_opp, "keys": keys,
            "flags": flags, "per_type_means": per_type_means, "rel": rel,
            "decile_cut": cut, "mp": mp, "ts": ts, "cp": cp,
            "mp_out": mp_out, "mp_mu": mp_mu, "mp_sd": mp_sd,
            "ts_out": ts_out, "ts_mu": ts_mu, "ts_sd": ts_sd,
            "amat": amat, "cell_ids": cell_ids,
        }
        p = f"{role}_"
        write_csv(out_dir / f"{p}type_matrix.csv", [""] + types,
                  [[types[i]] + [f"{v:.6f}" for v in m_all[i]]
                   for i in range(len(types))], digests_out)
        write_csv(out_dir / f"{p}type_matrix_opposition_only.csv", [""] + types,
                  [[types[i]] + [f"{v:.6f}" for v in m_opp[i]]
                   for i in range(len(types))], digests_out)
        write_csv(out_dir / f"{p}cell_by_value.csv", ["cell_id"] + keys,
                  [[cid] + [f"{v:.6f}" for v in amat[r]]
                   for r, cid in enumerate(cell_ids)], digests_out)
        write_csv(out_dir / f"{p}type_by_value_means.csv", ["type_id"] + keys,
                  [[t] + [f"{per_type_means[t][k]:.6f}" for k in keys]
                   for t in sorted(per_type_means)], digests_out)
        write_csv(out_dir / f"{p}third_value_flags.csv",
                  ["type_id", "value", "mean_similarity",
                   "ranks_above_own_pole", "worst_own_pole", "in_top_decile",
                   "top_cells"],
                  [[f["type_id"], f["value"], f"{f['mean_similarity']:.6f}",
                    f["ranks_above_own_pole"],
                    "" if f["worst_own_pole"] is None else f"{f['worst_own_pole']:.6f}",
                    f["in_top_decile"],
                    "; ".join(f"{c}={s:.3f}" for c, s in f["top_cells"])]
                   for f in flags], digests_out)
        write_csv(out_dir / f"{p}relative_value_affinity.csv",
                  ["type_id", "value", "mean_cosine", "z_within_value",
                   "is_own_pole", "flagged"],
                  [[r["type_id"], r["value"], f"{r['mean']:.6f}",
                    f"{r['z_within_value']:.3f}", r["is_own_pole"],
                    r["flagged"]] for r in rel], digests_out)
        write_csv(out_dir / f"{p}minimal_pair_tightness.csv",
                  ["scenario", "cond_a", "cond_b", "distance"],
                  [[r["scenario"], r["cond_a"], r["cond_b"], f"{r['distance']:.6f}"]
                   for r in mp], digests_out)
        write_csv(out_dir / f"{p}tip_symmetry.csv",
                  ["scenario", "cond_a", "d_a", "cond_b", "d_b", "asymmetry"],
                  [[r["scenario"], r["cond_a"], f"{r['d_a']:.6f}", r["cond_b"],
                    f"{r['d_b']:.6f}", f"{r['asymmetry']:.6f}"] for r in ts],
                  digests_out)
        write_csv(out_dir / f"{p}control_placement.csv",
                  ["control", "type_id", "sim_to_own_type", "sim_to_rest", "margin"],
                  [[r["control"], r["type_id"], f"{r['sim_to_own_type']:.6f}",
                    f"{r['sim_to_rest']:.6f}", f"{r['margin']:.6f}"] for r in cp],
                  digests_out)
        heatmap(out_dir / f"{p}type_matrix.png", types, types, m_all,
                f"Type-by-type mean cosine — {spec['name']}", digests_out)
        heatmap(out_dir / f"{p}type_by_value.png", sorted(per_type_means), keys,
                np.array([[per_type_means[t][k] for k in keys]
                          for t in sorted(per_type_means)]),
                f"Type-by-value-anchor mean cosine — {spec['name']}", digests_out)

    # ---- encoder agreement -------------------------------------------------
    agreement = {}
    if len(results) == 2:
        (ra, rb) = list(results)
        A, B = results[ra], results[rb]
        common = [t for t in A["types"] if t in B["types"]]
        ia = [A["types"].index(t) for t in common]
        ib = [B["types"].index(t) for t in common]
        va = np.array([A["m_all"][np.ix_(ia, ia)][x, y]
                       for x, y in combinations(range(len(common)), 2)])
        vb = np.array([B["m_all"][np.ix_(ib, ib)][x, y]
                       for x, y in combinations(range(len(common)), 2)])
        fa = {(f["type_id"], f["value"]) for f in A["flags"]}
        fb = {(f["type_id"], f["value"]) for f in B["flags"]}
        agreement = {
            "pearson": float(np.corrcoef(va, vb)[0, 1]),
            "spearman": spearman(va, vb),
            "n_type_pairs": len(va),
            "flags_primary": len(fa), "flags_robustness": len(fb),
            "flags_shared": len(fa & fb),
            "flags_primary_only": sorted(fa - fb),
            "flags_robustness_only": sorted(fb - fa),
        }
        print(f"\nencoder agreement: pearson {agreement['pearson']:.3f}, "
              f"spearman {agreement['spearman']:.3f}; "
              f"flags {agreement['flags_shared']} shared / "
              f"{len(fa)} vs {len(fb)}")

    # ---- summary -----------------------------------------------------------
    A = results[list(results)[0]]
    offd = offdiag_values(A["types"], A["m_all"])
    ranked = sorted(offd, key=lambda x: -x[2])
    worry_rows = []
    for ta, tb, why in WORRY_SPOTS:
        hit = next((o for o in offd if {o[0], o[1]} == {ta, tb}), None)
        if hit is None:
            continue
        rank = 1 + next(i for i, o in enumerate(ranked)
                        if {o[0], o[1]} == {ta, tb})
        pct = 1.0 - (rank - 1) / len(ranked)
        worry_rows.append({"pair": f"{ta} ↔ {tb}", "why": why,
                           "cosine": hit[2], "rank": rank,
                           "of": len(ranked), "percentile": pct})
    write_csv(out_dir / "worry_spots.csv",
              ["pair", "rationale", "cosine", "rank", "of_pairs", "percentile"],
              [[w["pair"], w["why"], f"{w['cosine']:.6f}", w["rank"], w["of"],
                f"{w['percentile']:.3f}"] for w in worry_rows], digests_out)

    lines = []
    lines.append("# Stimulus-similarity exhibit — conflict battery")
    lines.append("")
    if args.provisional:
        lines.append("> **PROVISIONAL PLUMBING RUN — NOT THE EXHIBIT.** Run on "
                     "text that has not passed the freeze gate (pending-edits "
                     "batch not applied / validation not clean). Numbers here "
                     "are for verifying the pipeline only.")
        lines.append("")
    lines.append(f"Produced by: {PRODUCED_BY}")
    lines.append(f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"Run dir: `{out_dir.as_posix()}`")
    lines.append("")
    lines.append("**Descriptive exhibit — not gating.** No thresholds, no "
                 "pass/fail, no rewrite triggers. Independent of the subject "
                 "model by design: no Llama-derived embeddings appear "
                 "anywhere in this analysis.")
    lines.append("")
    lines.append("## Encoders")
    lines.append("")
    lines.append("| role | model | family | revision | pooling |")
    lines.append("|---|---|---|---|---|")
    for role, r in results.items():
        lines.append(f"| {role} | `{r['spec']['name']}` | {r['spec']['family']} "
                     f"| `{r['revision'] or 'n/a'}` | {r['spec']['pooling']} |")
    lines.append("")
    lines.append("Caveat on independence: both encoders sit outside the Llama "
                 "lineage (the design requirement), but they are trained on "
                 "overlapping sentence-embedding corpora, so agreement between "
                 "them is weaker evidence than agreement between genuinely "
                 "unrelated instruments.")
    lines.append("")
    lines.append("## Text version")
    lines.append("")
    lines.append(f"Cell assembly: `{args.cell_text}`. Ingest digests:")
    for name, d in sorted(digests_in.items()):
        lines.append(f"- `{name}` — `{d['sha256'][:12]}…`")
    lines.append("")
    lines.append(f"Value anchors: `{args.anchors}` sha256 `{a_sha[:12]}…`, "
                 f"from `{anchors_blob['source_doc']}` sha256 "
                 f"`{anchors_blob['source_doc_sha256'][:12]}…` "
                 f"(verbatim 'Operational definition (behavioral)' column).")
    flagged = [a for a in anchors if "flag" in a]
    if flagged:
        lines.append("")
        lines.append("**Anchor texts flagged for researcher decision "
                     "(used verbatim here, not substituted):**")
        for a in flagged:
            lines.append(f"- `{a['value']}` — {a['flag']}")
    lines.append("")
    lines.append("## 1. Worry spots (pre-registered)")
    lines.append("")
    lines.append("| pair | cosine | rank | percentile | why watched |")
    lines.append("|---|---|---|---|---|")
    for w in worry_rows:
        lines.append(f"| {w['pair']} | {w['cosine']:.3f} | {w['rank']}/{w['of']} "
                     f"| {w['percentile']:.2f} | {w['why']} |")
    lines.append("")
    lines.append("## 2. Third-value flags")
    lines.append("")
    n_poss = len(A["per_type_means"]) * (len(A["keys"]) - 2)
    # Label correction per D73 (ratified 2026-08-05, amends D56): the
    # RELATIVE z-standardized diagnostic is the operative ratified screen;
    # the absolute rank-above-own-pole rule is retained descriptively only
    # (non-discriminative on this corpus). Earlier summaries labeled these
    # the other way around.
    lines.append(f"**Absolute rule (descriptive only, superseded by D73)** "
                 f"(a non-pole value ranks above one of the type's own "
                 f"poles, or sits in the top decile of the cell-by-value "
                 f"distribution): **{len(A['flags'])} flags of ~{n_poss} "
                 f"possible type-value combinations.**")
    lines.append("")
    if len(A["flags"]) > 0.25 * n_poss:
        lines.append("> ⚠️ **The rule is not discriminative on this corpus, "
                     "for the structural reason the brief itself names.** "
                     "Authoring rule 7 strips value vocabulary from stimulus "
                     "text, so own-pole similarity is low by design — which "
                     "makes \"ranks above an own pole\" a floor that most "
                     "unrelated values clear. Firing on this share of "
                     "combinations, the flag list cannot function as a "
                     "tripwire. The full list is in "
                     "`*_third_value_flags.csv`; the relative diagnostic "
                     "below is offered as an alternative read-out and is "
                     "**Claude's addition, not a ratified substitute** — it "
                     "needs a researcher decision before it is used as the "
                     "operative signal.")
        lines.append("")
    rel_flagged = [r for r in A["rel"] if r["flagged"]]
    lines.append(f"**Relative diagnostic (RATIFIED operative screen — D73, "
                 f"2026-08-05):** value "
                 f"affinity standardized *within value across types* — asking "
                 f"whether a type is unusually close to a value relative to "
                 f"every other type, which also cancels the constant offset "
                 f"from the anchors' shared 'Pull toward/against …' frame. "
                 f"Flagged at z ≥ 2.0: **{len(rel_flagged)}**. "
                 f"(Bound: standardizing across n={len(A['per_type_means'])} "
                 f"types caps z at (n−1)/√n ≈ "
                 f"{(len(A['per_type_means']) - 1) / np.sqrt(len(A['per_type_means'])):.2f}, "
                 f"so 2.0 is a real but not extreme bar.)")
    lines.append("")
    if rel_flagged:
        lines.append("| type | third value | mean cos | z within value |")
        lines.append("|---|---|---|---|")
        for r in rel_flagged:
            lines.append(f"| {r['type_id']} | {r['value']} | {r['mean']:.3f} "
                         f"| {r['z_within_value']:+.2f} |")
        lines.append("")
    lines.append("Ratified-rule flag list (first 20 by mean similarity):")
    lines.append("")
    if A["flags"]:
        lines.append("| type | third value | mean cos | > own pole | top decile | top cells |")
        lines.append("|---|---|---|---|---|---|")
        for fl in sorted(A["flags"], key=lambda x: -x["mean_similarity"])[:20]:
            lines.append(
                f"| {fl['type_id']} | {fl['value']} | {fl['mean_similarity']:.3f} "
                f"| {'yes' if fl['ranks_above_own_pole'] else ''} "
                f"| {'yes' if fl['in_top_decile'] else ''} "
                f"| {'; '.join(c for c, _ in fl['top_cells'])} |")
    else:
        lines.append("None. (Empty is the expected and reportable result.)")
    lines.append("")
    lines.append("## 3. Own-value similarities — reported, NOT a presence check")
    lines.append("")
    lines.append("The authoring rules deliberately strip value vocabulary from "
                 "stimulus text (rule 7). **Low own-value similarity is "
                 "expected for clean text and is not evidence the value is "
                 "absent.** No flag rule is applied to this read-out. Full "
                 "table: `*_type_by_value_means.csv`.")
    lines.append("")
    lines.append("| type | own poles | own-pole cosines |")
    lines.append("|---|---|---|")
    for t in sorted(A["per_type_means"]):
        poles = [p for p in type_poles.get(t, []) if p in A["keys"]]
        if not poles:
            continue
        lines.append(f"| {t} | {', '.join(poles)} | " +
                     ", ".join(f"{p}={A['per_type_means'][t][p]:.3f}"
                               for p in poles) + " |")
    lines.append("")
    lines.append("## 4. Minimal-pair tightness and tip symmetry")
    lines.append("")
    lines.append(f"Opposition-sibling distance: mean {A['mp_mu']:.4f}, "
                 f"sd {A['mp_sd']:.4f}, n {len(A['mp'])}. "
                 f"Outliers (|z| ≥ {OUTLIER_Z}): "
                 + (", ".join(f"{r['scenario']} ({r['distance']:.3f})"
                              for r in A["mp_out"]) or "none") + ".")
    lines.append("")
    lines.append(f"Tip-symmetry asymmetry: mean {A['ts_mu']:.4f}, "
                 f"sd {A['ts_sd']:.4f}, n {len(A['ts'])}. "
                 f"Outliers: "
                 + (", ".join(f"{r['scenario']} ({r['asymmetry']:.3f})"
                              for r in A["ts_out"]) or "none") + ".")
    lines.append("")
    lines.append("## 5. Topical-control placement")
    lines.append("")
    lines.append("| control | to own type | to rest | margin |")
    lines.append("|---|---|---|---|")
    for r in A["cp"]:
        lines.append(f"| {r['control']} | {r['sim_to_own_type']:.3f} "
                     f"| {r['sim_to_rest']:.3f} | {r['margin']:+.3f} |")
    lines.append("")
    lines.append("## 6. Encoder agreement")
    lines.append("")
    if agreement:
        lines.append(f"Type-pair matrices: Pearson {agreement['pearson']:.3f}, "
                     f"Spearman {agreement['spearman']:.3f} over "
                     f"{agreement['n_type_pairs']} pairs.")
        lines.append("")
        lines.append(f"Third-value flag sets: {agreement['flags_shared']} shared; "
                     f"primary {agreement['flags_primary']}, robustness "
                     f"{agreement['flags_robustness']}.")
        if agreement["flags_primary_only"] or agreement["flags_robustness_only"]:
            lines.append("")
            lines.append("Disagreement (surfaced, not resolved):")
            for t, v in agreement["flags_primary_only"]:
                lines.append(f"- primary only: {t} / {v}")
            for t, v in agreement["flags_robustness_only"]:
                lines.append(f"- robustness only: {t} / {v}")
    else:
        lines.append("Single encoder run — no agreement statistics.")
    lines.append("")
    lines.append("## Open question for the researcher")
    lines.append("")
    lines.append("Cell assembly: the brief said \"stem + condition insert, "
                 "exactly as administered\". For opposition cells the shared "
                 "conflict text is also administered, and omitting it would "
                 "collapse opposition cells onto their agreement siblings, so "
                 f"this run used `--cell-text {args.cell_text}` "
                 "(`full` = stem + shared text + insert). Re-run with "
                 "`--cell-text stem_insert` for the narrower literal reading.")
    lines.append("")
    text = "\n".join(lines)
    summary = out_dir / "summary.md"
    atomic_write(summary, lambda f: f.write(text), mode="w",
                 encoding="utf-8", newline="\n")
    s_sha, s_size = file_digest(summary)
    digests_out[summary.name] = {"sha256": s_sha, "bytes": s_size}
    print(f"DIGEST {s_sha} {s_size} {summary.name}")

    manifest = {
        "run_id": tag, "run_role": "stimulus_similarity_exhibit",
        "provisional": args.provisional, "produced_by": PRODUCED_BY,
        "cell_text_mode": args.cell_text,
        "encoders": {r: {"name": v["spec"]["name"], "family": v["spec"]["family"],
                         "revision": v["revision"],
                         "pooling": v["spec"]["pooling"]}
                     for r, v in results.items()},
        "anchors_file": args.anchors, "anchors_sha256": a_sha,
        "anchor_source_doc": anchors_blob["source_doc"],
        "anchor_source_sha256": anchors_blob["source_doc_sha256"],
        "flagged_anchors": [a["value"] for a in anchors if "flag" in a],
        "input_digests": digests_in, "output_digests": digests_out,
        "n_units": len(units), "n_cells": n_cells,
        "encoder_agreement": agreement,
        "timestamp_utc": datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    mpath = out_dir / "manifest.json"
    atomic_write(mpath, lambda f: f.write(json.dumps(manifest, indent=2) + "\n"),
                 mode="w", encoding="utf-8", newline="\n")
    m_sha, m_size = file_digest(mpath)
    print(f"DIGEST {m_sha} {m_size} {mpath.name}")
    print(f"\nWrote {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
