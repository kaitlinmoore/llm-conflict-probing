#!/usr/bin/env python3
"""
battery_pipeline.py — Stage 3 analysis pipeline (analysis_pipeline_brief.md,
run_configuration.md). Built and committed against the smoke shard BEFORE any
real run output exists: this code is the blind specification of the five
label-free analyses. Laptop-scale; no pod, no subject model.

CAPTURE CONTRACT (what the pod writes; smoke shard instantiates it):
  <run_dir>/capture_rows.csv — one row per administered prompt:
    prompt_key,row_id,type_id,type_num,family,scenario_id,condition,order,
    arm,expected_pick,expected_response,prompt_sha256,entropy,p_A,p_B,
    generation
    family ∈ {choice, refusal, competition}; order ∈ {AB, BA, NA};
    arm ∈ {open_ended, answer_only}; p_A/p_B populated on answer_only rows
    (ruled 2026-08-05); row_id from battery_frozen_v1.jsonl.
  <run_dir>/activations.pt — {"activations": {prompt_key: tensor
    [n_layers, d]}, "partial": False} (fp16 accepted, upcast on load).
  Refusal comparator capture (recapture pod), same shape, with rows CSV
  carrying `set ∈ {harmful, harmless}`.

ESTIMATOR-CONSISTENCY RULE (binding): every direction — conflict, refusal,
emotion (pre-fit Phase-0 artifact), generic-difficulty — is a difference of
means at the anchor, and every fit in this module routes through
`diff_of_means`. No estimator mixing.

BLINDNESS BY CONSTRUCTION: layer selection accepts a ChoiceCapture only and
raises on anything else; refusal rows load through `load_refusal_capture`
into a RefusalCapture that the selection path cannot accept. The verified
tier refuses to run without a label-lock digest (label_lock.py).

Statistic definitions (reported in every output header):
  separation(layer, direction) = (mean proj of opposition rows − mean proj
    of agreement rows) / pooled SD of the two projection sets, projections
    onto the unit direction, order-averaged rows.
  split_half_agreement(layer) = cosine of directions fitted on two seeded
    halves of the scenario set (mean over N_SPLITS re-splits).
  stability(layer) = mean cosine of the layer's direction with the
    directions at the adjacent layers (tie-break only).

Usage:
  python src/analysis/battery_pipeline.py --run-dir results/battery_run/<id>
      --comparator-dir <dir> [--tier as_designed|provisional]
      [--lock <lockfile> --tier verified]
"""

import argparse
import csv
import datetime
import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.pretest.runner_lib import atomic_write, file_digest

PRODUCED_BY = "Claude Fable 5 (model id claude-fable-5)"
SEED = 23
N_SPLITS = 20          # split-half re-splits
N_PERM = 1000          # permutation-null draws
K_MIN_HELDOUT = 4      # choose K so each fold holds out >= 4 scenarios
HARM_TYPES = {7, 8, 9}          # confirmatory refusal tier
INTERMEDIATE_TYPES = {10, 11, 12}   # exploratory refusal tier

CHOICE_OPP = ("oppose_tip_A", "oppose_tip_B")
CHOICE_AGR = ("agree_A", "agree_B")
REFUSAL_OPP = ("oppose_tip_comply", "oppose_tip_refuse")
REFUSAL_AGR = ("agree_comply", "agree_refuse")


# ---------------------------------------------------------------------------
# The one estimator
# ---------------------------------------------------------------------------

def diff_of_means(group_a: np.ndarray, group_b: np.ndarray) -> np.ndarray:
    """THE estimator. Difference of means, a-minus-b, at the anchor.
    Every direction fit in this pipeline calls this function."""
    return np.asarray(group_a).mean(axis=0) - np.asarray(group_b).mean(axis=0)


def unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


# ---------------------------------------------------------------------------
# Loaders — family separation enforced by construction
# ---------------------------------------------------------------------------

@dataclass
class ChoiceCapture:
    rows: list                      # metadata dicts, family == choice
    acts: dict                      # prompt_key -> [n_layers, d] float32
    n_layers: int
    d: int


@dataclass
class RefusalCapture:
    rows: list
    acts: dict
    n_layers: int
    d: int


@dataclass
class CompetitionCapture:
    rows: list
    acts: dict


def _load_run(run_dir: Path):
    import torch
    rows = list(csv.DictReader(
        (run_dir / "capture_rows.csv").open(encoding="utf-8", newline="")))
    blob = torch.load(run_dir / "activations.pt", map_location="cpu",
                      weights_only=False)
    if blob.get("partial"):
        raise RuntimeError(f"{run_dir}: partial capture — refuse to analyze")
    acts = {k: np.asarray(v, dtype=np.float32)
            for k, v in blob["activations"].items()}
    some = next(iter(acts.values()))
    return rows, acts, some.shape[0], some.shape[1]


def load_choice_capture(run_dir: Path) -> ChoiceCapture:
    rows, acts, L, d = _load_run(run_dir)
    keep = [r for r in rows if r["family"] == "choice"
            and r["arm"] == "open_ended"]
    return ChoiceCapture(keep, {r["prompt_key"]: acts[r["prompt_key"]]
                                for r in keep}, L, d)


def load_refusal_capture(run_dir: Path) -> RefusalCapture:
    rows, acts, L, d = _load_run(run_dir)
    keep = [r for r in rows if r["family"] == "refusal"
            and r["arm"] == "open_ended"]
    return RefusalCapture(keep, {r["prompt_key"]: acts[r["prompt_key"]]
                                 for r in keep}, L, d)


def load_competition_capture(run_dir: Path) -> CompetitionCapture:
    rows, acts, _, _ = _load_run(run_dir)
    keep = [r for r in rows if r["family"] == "competition"]
    return CompetitionCapture(keep, {r["prompt_key"]: acts[r["prompt_key"]]
                                     for r in keep})


# ---------------------------------------------------------------------------
# Contrast construction (choice family; order-averaged first)
# ---------------------------------------------------------------------------

def order_averaged(rows, acts, layer):
    """(scenario_id, condition) -> mean anchor vector over orders at layer."""
    bucket = defaultdict(list)
    for r in rows:
        bucket[(r["scenario_id"], r["condition"])].append(
            acts[r["prompt_key"]][layer])
    return {k: np.mean(v, axis=0) for k, v in bucket.items()}


def scenario_contrasts(cap, layer, opp=CHOICE_OPP, agr=CHOICE_AGR):
    """Direction-matched within-scenario contrasts (opposition minus
    agreement, same resolution direction). -> {scenario: [contrast, ...]}"""
    av = order_averaged(cap.rows, cap.acts, layer)
    scen = defaultdict(list)
    for (sid, cond) in av:
        if cond in opp:
            partner = agr[opp.index(cond)]
            if (sid, partner) in av:
                scen[sid].append(av[(sid, cond)] - av[(sid, partner)])
    return dict(scen)


def fit_conflict_direction(cap, layer, scenarios=None):
    """Difference-of-means fit: mean of opposition anchors minus mean of
    agreement anchors, direction-matched pairs, restricted to `scenarios`."""
    av = order_averaged(cap.rows, cap.acts, layer)
    opp_vecs, agr_vecs = [], []
    for (sid, cond), v in av.items():
        if scenarios is not None and sid not in scenarios:
            continue
        if cond in CHOICE_OPP:
            partner = CHOICE_AGR[CHOICE_OPP.index(cond)]
            if (sid, partner) in av:
                opp_vecs.append(v)
                agr_vecs.append(av[(sid, partner)])
    return diff_of_means(opp_vecs, agr_vecs)


def separation(direction, cap, layer, scenarios, opp=CHOICE_OPP,
               agr=CHOICE_AGR):
    """Standardized separation of opposition vs agreement projections."""
    u = unit(direction)
    av = order_averaged(cap.rows, cap.acts, layer)
    po = [v @ u for (sid, c), v in av.items()
          if sid in scenarios and c in opp]
    pa = [v @ u for (sid, c), v in av.items()
          if sid in scenarios and c in agr]
    if len(po) < 2 or len(pa) < 2:
        return float("nan")
    pooled = np.sqrt((np.var(po, ddof=1) + np.var(pa, ddof=1)) / 2)
    return float((np.mean(po) - np.mean(pa)) / pooled) if pooled > 0 else 0.0


# ---------------------------------------------------------------------------
# Layer selection (choice family ONLY — enforced)
# ---------------------------------------------------------------------------

def _folds(scenarios_by_type, k, rng):
    scen = [s for ss in scenarios_by_type.values() for s in ss]
    folds = [[] for _ in range(k)]
    for ttype, ss in sorted(scenarios_by_type.items()):
        ss = sorted(ss)
        rng.shuffle(ss)
        for i, s in enumerate(ss):
            folds[i % k].append(s)
    return [set(f) for f in folds], scen


def split_half_agreement(cap, layer, rng, n_splits=N_SPLITS,
                         permute=False):
    """Mean cosine of directions fitted on two scenario halves. With
    permute=True, opposition/agreement labels are shuffled at SCENARIO level
    before fitting (the matched null)."""
    scen = sorted({r["scenario_id"] for r in cap.rows})
    cos = []
    for _ in range(n_splits):
        order = scen[:]
        rng.shuffle(order)
        half = len(order) // 2
        a, b = set(order[:half]), set(order[half:])
        if permute:
            flip = {s: rng.random() < 0.5 for s in scen}
            da = _fit_permuted(cap, layer, a, flip)
            db = _fit_permuted(cap, layer, b, flip2={s: rng.random() < 0.5
                                                     for s in scen})
        else:
            da = fit_conflict_direction(cap, layer, a)
            db = fit_conflict_direction(cap, layer, b)
        cos.append(float(unit(da) @ unit(db)))
    return float(np.mean(cos)), cos


def _fit_permuted(cap, layer, scenarios, flip=None, flip2=None):
    fl = flip if flip is not None else flip2
    av = order_averaged(cap.rows, cap.acts, layer)
    opp_vecs, agr_vecs = [], []
    for (sid, cond), v in av.items():
        if sid not in scenarios or cond not in CHOICE_OPP:
            continue
        partner = CHOICE_AGR[CHOICE_OPP.index(cond)]
        if (sid, partner) not in av:
            continue
        o, a = v, av[(sid, partner)]
        if fl.get(sid):
            o, a = a, o
        opp_vecs.append(o)
        agr_vecs.append(a)
    return diff_of_means(opp_vecs, agr_vecs)


def select_layer(cap, seed=SEED, gate_threshold=None):
    """Ratified criterion (run_configuration.md): scenario-level K-fold CV
    stratified by tension type; per-layer mean held-out standardized
    separation; ties broken by adjacent-layer stability. Refusal data
    cannot enter: type-enforced.

    Reliability gate — RATIFIED as the pipeline default (researcher,
    2026-08-05): split-half agreement must EXCEED the matched
    scenario-permutation null; the gate disqualifies only, never selects
    (D50). Disclosure rule (same ruling): if a stricter numeric criterion
    is later pre-stated, pass it as gate_threshold — selection re-runs
    under it AND the ratified default, and both results are reported."""
    if not isinstance(cap, ChoiceCapture):
        raise TypeError("layer selection accepts ChoiceCapture ONLY — "
                        "refusal-family data is excluded by construction")
    if any(r["family"] != "choice" for r in cap.rows):
        raise ValueError("non-choice row reached layer selection")
    rng = np.random.default_rng(seed)
    by_type = defaultdict(set)
    for r in cap.rows:
        by_type[r["type_num"]].add(r["scenario_id"])
    n_scen = sum(len(s) for s in by_type.values())
    k = max(2, min(5, n_scen // K_MIN_HELDOUT))
    folds, scen = _folds(by_type, k, rng)

    per_layer = []
    for layer in range(cap.n_layers):
        seps = []
        for f in folds:
            train = set(scen) - f
            d = fit_conflict_direction(cap, layer, train)
            seps.append(separation(d, cap, layer, f))
        rel, _ = split_half_agreement(cap, layer,
                                      np.random.default_rng(seed + layer))
        nul, _ = split_half_agreement(cap, layer,
                                      np.random.default_rng(seed + layer),
                                      n_splits=max(4, N_SPLITS // 2),
                                      permute=True)
        per_layer.append({"layer": layer,
                          "heldout_separation": float(np.nanmean(seps)),
                          "split_half": rel, "perm_null_split_half": nul})

    dirs = [unit(fit_conflict_direction(cap, l)) for l in range(cap.n_layers)]
    for row in per_layer:
        l = row["layer"]
        adj = [float(dirs[l] @ dirs[j]) for j in (l - 1, l + 1)
               if 0 <= j < cap.n_layers]
        row["stability"] = float(np.mean(adj))
        # ratified default gate: exceed the matched permutation null
        row["gate_pass"] = bool(row["split_half"] >
                                row["perm_null_split_half"])
        if gate_threshold is not None:
            row["gate_pass_stricter"] = bool(row["split_half"] >
                                             gate_threshold)

    def pick(flag):
        eligible = [r for r in per_layer if r[flag]]
        pool = eligible if eligible else per_layer
        best = max(pool, key=lambda r: (round(r["heldout_separation"], 6),
                                        round(r["stability"], 6)))
        return best["layer"]

    selected = pick("gate_pass")
    meta = {"k": k, "seed": seed,
            "gate": "exceeds matched permutation null, disqualify-only "
                    "(ratified 2026-08-05; D50: never selects)"}
    if gate_threshold is not None:
        meta["stricter_criterion"] = {
            "threshold": gate_threshold,
            "selected_layer": pick("gate_pass_stricter"),
            "disclosure": "stricter criterion re-runs selection; both "
                          "results reported (ruling 2026-08-05)"}
    return selected, per_layer, meta


# ---------------------------------------------------------------------------
# Other directions (same estimator)
# ---------------------------------------------------------------------------

def fit_refusal_direction(comparator_dir: Path, layer):
    """Native refusal refit at `layer` from the comparator capture
    (harmful vs harmless sets). Same estimator."""
    rows, acts, _, _ = _load_run(comparator_dir)
    harm = [acts[r["prompt_key"]][layer] for r in rows
            if r.get("set") == "harmful"]
    benign = [acts[r["prompt_key"]][layer] for r in rows
              if r.get("set") == "harmless"]
    return diff_of_means(harm, benign), len(harm), len(benign)


def fit_difficulty_direction(comp: CompetitionCapture, layer):
    """Generic-difficulty direction: competition torn minus easy."""
    torn = [comp.acts[r["prompt_key"]][layer] for r in comp.rows
            if r["condition"] == "torn"]
    easy = [comp.acts[r["prompt_key"]][layer] for r in comp.rows
            if r["condition"] == "easy"]
    return diff_of_means(torn, easy)


def load_emotion_directions(path: Path, layer):
    """Phase-0 per-layer emotion directions (checked 2026-08-05: 12
    emotions, layers 2..31). Returns {} at uncovered layers — reported."""
    import torch
    blob = torch.load(path, map_location="cpu", weights_only=False)
    out = {}
    for emo, per_layer in blob["vec"].items():
        if layer in per_layer:
            out[emo] = np.asarray(per_layer[layer], dtype=np.float32)
    return out


# ---------------------------------------------------------------------------
# The five label-free analyses
# ---------------------------------------------------------------------------

def analysis_existence(cap, layer, seed=SEED):
    rng = np.random.default_rng(seed)
    obs, _ = split_half_agreement(cap, layer, rng)
    null = []
    for i in range(max(20, N_PERM // 20)):
        n, _ = split_half_agreement(cap, layer,
                                    np.random.default_rng(seed + 1000 + i),
                                    n_splits=2, permute=True)
        null.append(n)
    null = np.array(null)
    return {"observed_split_half": obs,
            "null_mean": float(null.mean()), "null_sd": float(null.std()),
            "null_p95": float(np.percentile(null, 95)),
            "exceeds_null_p95": bool(obs > np.percentile(null, 95))}


def analysis_distinctness(cap, layer, comparator_dir, seed=SEED):
    conflict = unit(fit_conflict_direction(cap, layer))
    refusal, nh, nb = fit_refusal_direction(comparator_dir, layer)
    refusal = unit(refusal)
    cosine = float(conflict @ refusal)
    ceil_c, _ = split_half_agreement(cap, layer, np.random.default_rng(seed))
    # refusal self-consistency ceiling: split-half over comparator prompts
    rows, acts, _, _ = _load_run(Path(comparator_dir))
    rng = np.random.default_rng(seed)
    cos = []
    for _ in range(N_SPLITS // 2):
        h = [r for r in rows if r.get("set") == "harmful"]
        b = [r for r in rows if r.get("set") == "harmless"]
        rng.shuffle(h)
        rng.shuffle(b)
        d1 = diff_of_means([acts[r["prompt_key"]][layer] for r in h[::2]],
                           [acts[r["prompt_key"]][layer] for r in b[::2]])
        d2 = diff_of_means([acts[r["prompt_key"]][layer] for r in h[1::2]],
                           [acts[r["prompt_key"]][layer] for r in b[1::2]])
        cos.append(float(unit(d1) @ unit(d2)))
    return {"cosine_conflict_refusal": cosine,
            "conflict_ceiling": ceil_c,
            "refusal_ceiling": float(np.mean(cos)),
            "n_harmful": nh, "n_harmless": nb}


def analysis_reducibility(cap, layer, comp, emotion_path, seed=SEED):
    conflict = unit(fit_conflict_direction(cap, layer))
    emos = load_emotion_directions(emotion_path, layer)
    regressors, names = [], []
    for emo, v in sorted(emos.items()):
        regressors.append(unit(v))
        names.append(f"emotion:{emo}")
    regressors.append(unit(fit_difficulty_direction(comp, layer)))
    names.append("difficulty:competition")
    X = np.stack(regressors, axis=1)
    coef, *_ = np.linalg.lstsq(X, conflict, rcond=None)
    resid = conflict - X @ coef
    r2 = 1.0 - float(np.sum(resid ** 2))  # conflict is unit norm
    # per-item projections on held-out half
    rng = np.random.default_rng(seed)
    scen = sorted({r["scenario_id"] for r in cap.rows})
    rng.shuffle(scen)
    held = set(scen[len(scen) // 2:])
    contrasts = [c for s, cs in scenario_contrasts(cap, layer).items()
                 if s in held for c in cs]
    if contrasts:
        C = np.stack(contrasts)
        y = C @ conflict
        Z = C @ X
        cz, *_ = np.linalg.lstsq(Z, y, rcond=None)
        pred = Z @ cz
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        item_r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    else:
        item_r2 = float("nan")
    return {"direction_variance_explained": r2,
            "direction_residual_norm": float(np.linalg.norm(resid)),
            "helditem_projection_r2": item_r2,
            "n_regressors": len(names),
            "emotion_layers_covered": bool(emos),
            "regressors": names}


def analysis_transfer(cap, refusal_cap, layer, seed=SEED):
    if not isinstance(refusal_cap, RefusalCapture):
        raise TypeError("transfer needs the RefusalCapture loader")
    u = unit(fit_conflict_direction(cap, layer))
    out = {}
    for label, types in (("harm_anchored_confirmatory", HARM_TYPES),
                         ("intermediate_exploratory", INTERMEDIATE_TYPES)):
        rows = [r for r in refusal_cap.rows if int(r["type_num"]) in types]
        sub = RefusalCapture(rows, refusal_cap.acts, refusal_cap.n_layers,
                             refusal_cap.d)
        scen = {r["scenario_id"] for r in rows}
        sep = _refusal_separation(sub, u, layer, scen)
        null = []
        rng = np.random.default_rng(seed)
        for _ in range(max(50, N_PERM // 10)):
            null.append(_refusal_separation(sub, u, layer, scen,
                                            flip={s: rng.random() < 0.5
                                                  for s in scen}))
        null = np.array(null)
        out[label] = {"separation": sep,
                      "null_p95": float(np.percentile(null, 95)),
                      "exceeds_null_p95": bool(sep > np.percentile(null, 95)),
                      "n_scenarios": len(scen)}
    return out


def _refusal_separation(cap, u, layer, scenarios, flip=None):
    av = order_averaged(cap.rows, cap.acts, layer)
    po, pa = [], []
    for (sid, cond), v in av.items():
        if sid not in scenarios:
            continue
        if cond in REFUSAL_OPP:
            partner = REFUSAL_AGR[REFUSAL_OPP.index(cond)]
            if (sid, partner) in av:
                o, a = v, av[(sid, partner)]
                if flip and flip.get(sid):
                    o, a = a, o
                po.append(o @ u)
                pa.append(a @ u)
    if len(po) < 2:
        return float("nan")
    pooled = np.sqrt((np.var(po, ddof=1) + np.var(pa, ddof=1)) / 2)
    return float((np.mean(po) - np.mean(pa)) / pooled) if pooled > 0 else 0.0


# ---------------------------------------------------------------------------
# Tiers, artifacts, provenance
# ---------------------------------------------------------------------------

def _git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"],
                              capture_output=True, text=True,
                              timeout=10).stdout.strip()
    except Exception:
        return "unavailable"


def _freeze_sha():
    p = Path("data/battery/frozen/freeze_manifest.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8")).get("frozen_sha256",
                                                             "unavailable")
    return "unavailable"


def write_artifact(path: Path, header: dict, payload: dict, digests: dict):
    doc = {"_header": header, **payload}
    atomic_write(path, lambda f: f.write(json.dumps(doc, indent=2) + "\n"),
                 mode="w", encoding="utf-8", newline="\n")
    sha, size = file_digest(path)
    digests[path.name] = {"sha256": sha, "bytes": size}
    print(f"DIGEST {sha} {size} {path.name}")


def run_as_designed(run_dir: Path, comparator_dir: Path, emotion_path: Path,
                    out_root: Path, seed=SEED, gate_threshold=None):
    cap = load_choice_capture(run_dir)
    refusal_cap = load_refusal_capture(run_dir)
    comp = load_competition_capture(run_dir)

    layer, curve, sel_meta = select_layer(cap, seed=seed,
                                          gate_threshold=gate_threshold)
    header = {
        "produced_by": PRODUCED_BY,
        "generated_utc": datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds"),
        "pipeline_commit": _git_sha(),
        "freeze_sha256": _freeze_sha(),
        "run_dir": str(run_dir),
        "statistic_definitions": {
            "separation": "(mean opp proj - mean agr proj) / pooled SD, "
                          "unit direction, order-averaged rows",
            "split_half": f"mean cosine over {N_SPLITS} scenario re-splits",
            "stability": "mean cosine with adjacent-layer directions "
                         "(tie-break only)",
        },
        "selection": sel_meta,
        "seed": seed,
    }
    out = out_root / "as_designed"
    out.mkdir(parents=True, exist_ok=True)
    digests = {}
    write_artifact(out / "a2_layer_selection.json", header,
                   {"selected_layer": layer, "per_layer": curve}, digests)
    write_artifact(out / "a1_existence.json", header,
                   analysis_existence(cap, layer, seed), digests)
    write_artifact(out / "a3_distinctness.json", header,
                   {"at_selected_layer":
                        analysis_distinctness(cap, layer, comparator_dir,
                                              seed),
                    "sensitivity_layer12":
                        (analysis_distinctness(cap, 12, comparator_dir, seed)
                         if cap.n_layers > 12 else "n/a (capture has "
                         f"{cap.n_layers} layers)")}, digests)
    write_artifact(out / "a4_reducibility.json", header,
                   analysis_reducibility(cap, layer, comp, emotion_path,
                                         seed), digests)
    write_artifact(out / "a5_transfer.json", header,
                   analysis_transfer(cap, refusal_cap, layer, seed), digests)
    _figures(out, curve, layer, digests)
    write_artifact(out / "manifest.json", header,
                   {"artifacts": digests}, {})
    return layer


def _figures(out, curve, layer, digests):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    xs = [r["layer"] for r in curve]
    ax.plot(xs, [r["heldout_separation"] for r in curve],
            marker="o", ms=3, label="held-out separation")
    ax.plot(xs, [r["split_half"] for r in curve], ls="--",
            label="split-half agreement")
    ax.plot(xs, [r["perm_null_split_half"] for r in curve], ls=":",
            label="permutation null")
    ax.axvline(layer, color="grey", lw=1)
    ax.set_xlabel("layer")
    ax.set_title("Layer selection — held-out separation (gate: reliability "
                 "vs null; never selects)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    tmp = out / "a2_layer_curve.png.tmp"
    fig.savefig(tmp, dpi=150, format="png")
    plt.close(fig)
    tmp.replace(out / "a2_layer_curve.png")
    sha, size = file_digest(out / "a2_layer_curve.png")
    digests["a2_layer_curve.png"] = {"sha256": sha, "bytes": size}
    print(f"DIGEST {sha} {size} a2_layer_curve.png")


def run_provisional(run_dir: Path, out_root: Path):
    """Automatic-labeler manipulation table + provisional conflicted-
    compliance read. PROVISIONAL in every filename."""
    from src.battery import labeler as lb
    rows = list(csv.DictReader(
        (run_dir / "capture_rows.csv").open(encoding="utf-8", newline="")))
    out = out_root / "provisional"
    out.mkdir(parents=True, exist_ok=True)
    table = defaultdict(lambda: defaultdict(int))
    cc = []
    for r in rows:
        if r["family"] != "refusal" or r["arm"] != "open_ended":
            continue
        lab = lb.prelabel_response(r.get("generation", ""))
        exp = r.get("expected_response", "")
        table[exp][lab["label"]] += 1
        if r["condition"] == "oppose_tip_comply" and \
                lab["label"] in ("comply", "disclaimer"):
            cc.append({"row_id": r["row_id"], "label": lab["label"],
                       "uncertain": lab["uncertain"]})
    digests = {}
    header = {"produced_by": PRODUCED_BY, "PROVISIONAL": True,
              "note": "automatic labels, unaudited; superseded by the "
                      "verified tier at label lock"}
    write_artifact(out / "PROVISIONAL_manipulation_table.json", header,
                   {"expected_vs_labeled": {k: dict(v)
                                            for k, v in table.items()}},
                   digests)
    write_artifact(out / "PROVISIONAL_conflicted_compliance.json", header,
                   {"n_candidates": len(cc), "rows": cc}, digests)


def run_verified(lock_path: Path, labels_path: Path, out_root: Path):
    from src.analysis.label_lock import verify_lock
    if not lock_path or not Path(lock_path).exists():
        raise SystemExit("VERIFIED TIER REFUSED: no label-lock digest. "
                         "Run label_lock.py after the audit.")
    verify_lock(Path(lock_path), Path(labels_path))
    (out_root / "verified").mkdir(parents=True, exist_ok=True)
    print("label lock verified — verified-tier analyses may proceed "
          "(implemented post-lock per the audit protocol)")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--comparator-dir")
    ap.add_argument("--emotion",
                    default="results/emotion_vectors_llama8b_inference.pt")
    ap.add_argument("--out-root", default=None,
                    help="default: <run-dir>/analysis")
    ap.add_argument("--tier", default="as_designed",
                    choices=["as_designed", "provisional", "verified"])
    ap.add_argument("--gate-threshold", type=float, default=None,
                    help="OPTIONAL stricter reliability criterion; the "
                         "ratified default (exceeds matched permutation "
                         "null, 2026-08-05) always runs — a stricter value "
                         "re-runs selection and BOTH results are reported")
    ap.add_argument("--lock", help="label-lock file (verified tier)")
    ap.add_argument("--labels", help="audited labels file (verified tier)")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    run_dir = Path(args.run_dir)
    out_root = Path(args.out_root) if args.out_root else run_dir / "analysis"
    if args.tier == "as_designed":
        if not args.comparator_dir:
            ap.error("--comparator-dir required for as_designed")
        layer = run_as_designed(run_dir, Path(args.comparator_dir),
                                Path(args.emotion), out_root,
                                seed=args.seed,
                                gate_threshold=args.gate_threshold)
        print(f"selected layer: {layer}")
    elif args.tier == "provisional":
        run_provisional(run_dir, out_root)
    else:
        run_verified(args.lock, Path(args.labels), out_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
