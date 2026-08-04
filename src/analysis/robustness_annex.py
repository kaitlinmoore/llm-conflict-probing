#!/usr/bin/env python3
"""
robustness_annex.py — two POST-HOC robustness checks on the as-designed
results (researcher-directed 2026-08-06, executive-chat brief). Exploratory,
run after seeing results; every output header carries ROBUSTNESS_ANNEX /
post_hoc / date. Filed in analysis/robustness_annex/, never mixed into
as_designed/. No iteration on either check — results report as they land.

Check 1 — surface-feature regression: is the conflict direction a
length/entropy detector? Per-row L8 projections (choice, open-ended arm)
regressed on prompt length (whitespace-token proxy of the administered
user message — model tokenizer not loadable off-pod; proxy documented) and
anchor entropy. Key statistic: opposition-vs-agreement separation (the
pipeline's standardized-SD statistic, order-averaged, in-sample over all
scenarios) computed raw and after residualizing projections on
length + entropy. Pre-stated: length↔condition correlation is expected
(opposition cells carry shared text by design); the question is whether
separation survives residualization.

Check 2 — placebo contrast: does the pipeline flatter noise? A direction
fitted from the AB-vs-BA order contrast within condition (choice only),
pushed through the IDENTICAL pipeline path — same estimator, same CV layer
selection, same existence gate, same distinctness/reducibility/transfer
evaluations — by relabeling rows (AB→"opposition", BA→"agreement",
order-averaging thereby a no-op). The placebo carries one known real
signal (the +0.383 position bias) and zero conflict content. Pre-stated:
non-null placebo reliability is NOT a failure; the placebo fails the study
only if it separates real opposition-vs-agreement (within-family or
transfer) at magnitudes resembling the conflict direction's.

Also emitted: cosine(placebo, conflict) at L8, and the conflict
direction's AB-vs-BA projection difference (differencing was designed to
cancel position bias; confirm ~0).
"""

import argparse
import datetime
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.analysis import battery_pipeline as bp  # noqa: E402
from src.pretest.runner_lib import atomic_write, file_digest  # noqa: E402

DATE = "2026-08-06"
SEL_LAYER = 8   # the as-designed selected layer (a2 artifact)


def header(run_dir, extra=None):
    h = {"ROBUSTNESS_ANNEX": True, "post_hoc": True, "date": DATE,
         "motivation": "researcher-directed too-good-to-be-true audit "
                       "(executive chat, 2026-08-06); exploratory, run "
                       "after seeing the as-designed results",
         "produced_by": bp.PRODUCED_BY,
         "pipeline_commit": bp._git_sha(),
         "freeze_sha256": bp._freeze_sha(),
         "run_dir": str(run_dir),
         "generated_utc": datetime.datetime.now(
             datetime.timezone.utc).isoformat(timespec="seconds"),
         "separation_definition": "(mean opp proj - mean agr proj) / pooled "
                                  "SD, order-averaged cells, in-sample over "
                                  "all choice scenarios",
         "length_proxy": "whitespace tokens of the administered user "
                         "message (rendered_prompts.txt); model tokenizer "
                         "not loadable off-pod"}
    if extra:
        h.update(extra)
    return h


def prompt_lengths(run_dir: Path):
    """prompt_key -> whitespace-token count of the administered message."""
    out, key = {}, None
    buf = []
    for line in (run_dir / "rendered_prompts.txt").read_text(
            encoding="utf-8").splitlines():
        if line.startswith("=== "):
            if key is not None:
                out[key] = len(" ".join(buf).split())
            key = line[4:].strip()
            buf = []
        else:
            buf.append(line)
    if key is not None:
        out[key] = len(" ".join(buf).split())
    return out


def scalar_separation(vals_by_cell):
    """The pipeline's separation formula on scalar projections:
    {(sid, cond): value} order-averaged upstream."""
    po = [v for (s, c), v in vals_by_cell.items() if c.startswith("oppose")]
    pa = [v for (s, c), v in vals_by_cell.items() if c.startswith("agree")]
    pooled = np.sqrt((np.var(po, ddof=1) + np.var(pa, ddof=1)) / 2)
    return float((np.mean(po) - np.mean(pa)) / pooled)


def check1(cap, run_dir):
    u = bp.unit(bp.fit_conflict_direction(cap, SEL_LAYER))
    lengths = prompt_lengths(run_dir)
    rows = []
    for r in cap.rows:
        rows.append({"sid": r["scenario_id"], "cond": r["condition"],
                     "order": r["order"],
                     "proj": float(cap.acts[r["prompt_key"]][SEL_LAYER] @ u),
                     "length": lengths[r["prompt_key"]],
                     "entropy": float(r["entropy"])})
    proj = np.array([r["proj"] for r in rows])
    L = np.array([r["length"] for r in rows], dtype=float)
    E = np.array([r["entropy"] for r in rows], dtype=float)
    z = lambda x: (x - x.mean()) / x.std(ddof=1)
    X = np.column_stack([np.ones(len(rows)), z(L), z(E)])
    coef, *_ = np.linalg.lstsq(X, proj, rcond=None)
    pred = X @ coef
    resid = proj - pred
    ss_tot = float(np.sum((proj - proj.mean()) ** 2))
    r2 = 1.0 - float(np.sum(resid ** 2)) / ss_tot
    # partial correlations: each predictor vs proj, controlling the other
    def partial(a, b, c):
        ra = a - np.polyval(np.polyfit(c, a, 1), c)
        rb = b - np.polyval(np.polyfit(c, b, 1), c)
        return float(np.corrcoef(ra, rb)[0, 1])

    def avg(vals):
        cells = defaultdict(list)
        for r, v in zip(rows, vals):
            cells[(r["sid"], r["cond"])].append(v)
        return {k: float(np.mean(v)) for k, v in cells.items()}

    lengths_by_cond = defaultdict(list)
    for r in rows:
        lengths_by_cond[r["cond"]].append(r["length"])
    return {
        "n_rows": len(rows),
        "regression": {"r2": r2,
                       "beta_length_std": float(coef[1]),
                       "beta_entropy_std": float(coef[2]),
                       "partial_r_length": partial(z(L), proj, z(E)),
                       "partial_r_entropy": partial(z(E), proj, z(L))},
        "separation_raw": scalar_separation(avg(proj)),
        "separation_residualized": scalar_separation(avg(resid)),
        "mean_length_by_condition": {c: float(np.mean(v))
                                     for c, v in sorted(
                                         lengths_by_cond.items())},
        "mean_length_opposition_minus_agreement": float(
            np.mean([r["length"] for r in rows
                     if r["cond"].startswith("oppose")]) -
            np.mean([r["length"] for r in rows
                     if r["cond"].startswith("agree")])),
        "prestated_interpretation": "length↔condition correlation expected "
            "by design; the check fails only if separation collapses toward "
            "null after residualization",
    }


def placebo_capture(cap):
    rows = []
    for r in cap.rows:
        r2 = dict(r)
        r2["condition"] = ("oppose_tip_A" if r["order"] == "AB"
                           else "agree_A")
        r2["order"] = "NA"
        rows.append(r2)
    return bp.ChoiceCapture(rows, cap.acts, cap.n_layers, cap.d)


def check2(cap, refusal_cap, comp, comparator_dir, emotion_path):
    pcap = placebo_capture(cap)
    layer_p, curve_p, meta_p = bp.select_layer(pcap)
    panel = {
        "selected_layer": layer_p,
        "selection_meta": meta_p,
        "layer_curve_top5": sorted(curve_p,
                                   key=lambda r: -r["heldout_separation"])[:5],
        "a1_existence": bp.analysis_existence(pcap, layer_p),
        "a3_distinctness_vs_refusal": bp.analysis_distinctness(
            pcap, layer_p, comparator_dir),
        "a4_reducibility": bp.analysis_reducibility(
            pcap, layer_p, comp, emotion_path),
        "a5_transfer_at_own_layer": bp.analysis_transfer(
            pcap, refusal_cap, layer_p),
        "a5_transfer_at_L8": bp.analysis_transfer(pcap, refusal_cap,
                                                  SEL_LAYER),
    }
    u_p = bp.unit(bp.fit_conflict_direction(pcap, SEL_LAYER))
    u_c = bp.unit(bp.fit_conflict_direction(cap, SEL_LAYER))
    scen = sorted({r["scenario_id"] for r in cap.rows})
    panel["placebo_on_real_opposition_agreement_L8"] = bp.separation(
        u_p, cap, SEL_LAYER, set(scen))
    u_p_own = bp.unit(bp.fit_conflict_direction(pcap, layer_p))
    panel["placebo_on_real_opposition_agreement_own_layer"] = bp.separation(
        u_p_own, cap, layer_p, set(scen))
    panel["cosine_placebo_conflict_L8"] = float(u_p @ u_c)
    # conflict direction AB-vs-BA projection difference (should be ~0)
    ab = [float(cap.acts[r["prompt_key"]][SEL_LAYER] @ u_c)
          for r in cap.rows if r["order"] == "AB"]
    ba = [float(cap.acts[r["prompt_key"]][SEL_LAYER] @ u_c)
          for r in cap.rows if r["order"] == "BA"]
    pooled = np.sqrt((np.var(ab, ddof=1) + np.var(ba, ddof=1)) / 2)
    panel["conflict_projection_AB_minus_BA"] = {
        "raw": float(np.mean(ab) - np.mean(ba)),
        "in_pooled_SD_units": float((np.mean(ab) - np.mean(ba)) / pooled),
        "prestated": "order-averaging was designed to cancel position "
                     "bias; expect ~0"}
    panel["prestated_interpretation"] = (
        "non-null placebo reliability is not a failure (position bias is "
        "real); the placebo fails the study only if it separates real "
        "opposition-vs-agreement (within-family or transfer) at magnitudes "
        "resembling the conflict direction's (3.35 held-out; 3.50/4.24 "
        "transfer)")
    return panel


# ---------------------------------------------------------------------------
# Part 2 (researcher-directed 2026-08-06): length-confound decomposition
# ---------------------------------------------------------------------------

PRESTATED_C3 = (
    "a genuine length detector tracks length wherever length varies — "
    "strong positive within-condition slopes (comparable to the "
    "between-condition association) mean the direction reads length "
    "itself, and the confound is deep. Near-zero within-condition slopes "
    "with the strong between-condition association mean the length "
    "association rides the condition contrast — consistent with a "
    "conflict direction whose training contrast happens to be "
    "length-confounded, and the construct reading strengthens materially. "
    "Intermediate is intermediate; report without adjudicating.")

PRESTATED_C4 = (
    "(c) is decisive in one direction only. Length direction transfers at "
    "magnitudes resembling the conflict direction's (order of 3–4 SD) → "
    "the transfer headline is contaminated and cannot ship without the "
    "length-matched follow-up; flag immediately. Length direction "
    "transfers at noise scale while the conflict direction's transfer "
    "stands → transfer survives as the evidence that the conflict "
    "direction carries content length doesn't; the confound is then "
    "bounded to the raw within-family separation magnitude, with transfer "
    "and the ~1.1 SD residualized floor as the conservative claims. "
    "(a) and (b) contextualize but don't adjudicate — a moderate cosine "
    "is expected given the confounded training contrast and is not itself "
    "damning.")


def _reg(pairs):
    """[(length, proj)] -> {n, r, slope}."""
    if len(pairs) < 3:
        return {"n": len(pairs), "r": None, "slope": None}
    x = np.array([p[0] for p in pairs], dtype=float)
    y = np.array([p[1] for p in pairs], dtype=float)
    if x.std() == 0:
        return {"n": len(pairs), "r": None, "slope": None}
    r = float(np.corrcoef(x, y)[0, 1])
    slope = float(np.polyfit(x, y, 1)[0])
    return {"n": len(pairs), "r": round(r, 4), "slope": round(slope, 6)}


def _rows_with_proj(cap, layer, u, lengths):
    return [{"sid": r["scenario_id"], "cond": r["condition"],
             "length": lengths[r["prompt_key"]],
             "proj": float(cap.acts[r["prompt_key"]][layer] @ u)}
            for r in cap.rows]


def check3(cap, refusal_cap, run_dir):
    lengths = prompt_lengths(run_dir)
    u = bp.unit(bp.fit_conflict_direction(cap, SEL_LAYER))
    rows = _rows_with_proj(cap, SEL_LAYER, u, lengths)

    def group(pred):
        return [(r["length"], r["proj"]) for r in rows if pred(r)]

    out = {"choice_within_condition": {
        "agreement_pooled": _reg(group(lambda r: r["cond"].startswith("agree"))),
        "agree_A": _reg(group(lambda r: r["cond"] == "agree_A")),
        "agree_B": _reg(group(lambda r: r["cond"] == "agree_B")),
        "opposition_pooled": _reg(group(lambda r: r["cond"].startswith("oppose"))),
        "oppose_tip_A": _reg(group(lambda r: r["cond"] == "oppose_tip_A")),
        "oppose_tip_B": _reg(group(lambda r: r["cond"] == "oppose_tip_B")),
        "between_condition_all_rows_restated": _reg(
            [(r["length"], r["proj"]) for r in rows]),
    }}
    # refusal family, same read (transfer interpretation leans on it)
    rrows = _rows_with_proj(refusal_cap, SEL_LAYER, u, lengths)
    out["refusal_within_condition"] = {
        "agreement_pooled": _reg([(r["length"], r["proj"]) for r in rrows
                                  if r["cond"].startswith("agree")]),
        "opposition_pooled": _reg([(r["length"], r["proj"]) for r in rrows
                                   if r["cond"].startswith("oppose")]),
        "between_condition_all_rows": _reg([(r["length"], r["proj"])
                                            for r in rrows]),
    }
    # length distributions per condition per family
    dist = defaultdict(list)
    for r in rows:
        dist[("choice", r["cond"])].append(r["length"])
    for r in rrows:
        dist[("refusal", r["cond"])].append(r["length"])
    out["length_distributions"] = {
        f"{fam}:{cond}": {"n": len(v), "mean": round(float(np.mean(v)), 1),
                          "sd": round(float(np.std(v, ddof=1)), 1)}
        for (fam, cond), v in sorted(dist.items())}
    ropp = [r["length"] for r in rrows if r["cond"].startswith("oppose")]
    ragr = [r["length"] for r in rrows if r["cond"].startswith("agree")]
    out["refusal_opposition_minus_agreement_mean_length"] = round(
        float(np.mean(ropp) - np.mean(ragr)), 1)
    return out


def _length_rows(cap, lengths):
    """Agreement cells only (conflict absent throughout); global
    median-split by token length (ties go long, >= median). Unpaired by
    necessity: within a scenario the agreement rows share nearly one
    length, so a global split leaves most scenarios one-sided and the
    pipeline's within-scenario pairing would starve. Same estimator, same
    fold machinery and statistic — pairing is the one departure, stated."""
    agree = [r for r in cap.rows if r["condition"].startswith("agree")]
    med = float(np.median([lengths[r["prompt_key"]] for r in agree]))
    rows = [dict(r, long=lengths[r["prompt_key"]] >= med) for r in agree]
    return rows, med


def _fit_length_dir(rows, acts, layer, scenarios=None):
    keep = [r for r in rows
            if scenarios is None or r["scenario_id"] in scenarios]
    long = [acts[r["prompt_key"]][layer] for r in keep if r["long"]]
    short = [acts[r["prompt_key"]][layer] for r in keep if not r["long"]]
    if not long or not short:
        return None
    return bp.diff_of_means(long, short)


def _length_sep(u, rows, acts, layer, scenarios):
    keep = [r for r in rows if r["scenario_id"] in scenarios]
    pl = [float(acts[r["prompt_key"]][layer] @ u) for r in keep if r["long"]]
    ps = [float(acts[r["prompt_key"]][layer] @ u) for r in keep
          if not r["long"]]
    if len(pl) < 2 or len(ps) < 2:
        return float("nan")
    pooled = np.sqrt((np.var(pl, ddof=1) + np.var(ps, ddof=1)) / 2)
    return float((np.mean(pl) - np.mean(ps)) / pooled) if pooled > 0 else 0.0


def select_layer_length(rows, acts, n_layers, seed=bp.SEED):
    """The pipeline's CV selection logic on the unpaired long/short
    contrast: scenario-level K-fold stratified by type; held-out
    standardized separation; split-half gate vs scenario-level label-flip
    null (disqualify-only); ties by adjacent-layer stability."""
    rng = np.random.default_rng(seed)
    by_type = defaultdict(set)
    for r in rows:
        by_type[r["type_num"]].add(r["scenario_id"])
    n_scen = sum(len(s) for s in by_type.values())
    k = max(2, min(5, n_scen // bp.K_MIN_HELDOUT))
    folds, scen = bp._folds(by_type, k, rng)

    def split_half(layer, permute=False, n_splits=bp.N_SPLITS):
        rr = np.random.default_rng(seed + layer)
        cos = []
        for _ in range(n_splits):
            order = sorted(scen)
            rr.shuffle(order)
            half = len(order) // 2
            a, b = set(order[:half]), set(order[half:])
            use = rows
            if permute:
                flip = {s: rr.random() < 0.5 for s in sorted(set(scen))}
                use = [dict(r, long=(not r["long"]) if flip[r["scenario_id"]]
                            else r["long"]) for r in rows]
            da = _fit_length_dir(use, acts, layer, a)
            db = _fit_length_dir(use, acts, layer, b)
            if da is None or db is None:
                continue
            cos.append(float(bp.unit(da) @ bp.unit(db)))
        return float(np.mean(cos)) if cos else float("nan")

    per_layer = []
    for layer in range(n_layers):
        seps = []
        for f in folds:
            train = set(scen) - f
            d = _fit_length_dir(rows, acts, layer, train)
            if d is not None:
                seps.append(_length_sep(bp.unit(d), rows, acts, layer, f))
        rel = split_half(layer)
        nul = split_half(layer, permute=True,
                         n_splits=max(4, bp.N_SPLITS // 2))
        per_layer.append({"layer": layer,
                          "heldout_separation": float(np.nanmean(seps)),
                          "split_half": rel,
                          "perm_null_split_half": nul,
                          "gate_pass": bool(rel > nul)})
    dirs = [bp.unit(_fit_length_dir(rows, acts, l))
            for l in range(n_layers)]
    for row in per_layer:
        l = row["layer"]
        adj = [float(dirs[l] @ dirs[j]) for j in (l - 1, l + 1)
               if 0 <= j < n_layers]
        row["stability"] = float(np.mean(adj))
    eligible = [r for r in per_layer if r["gate_pass"]] or per_layer
    best = max(eligible, key=lambda r: (round(r["heldout_separation"], 6),
                                        round(r["stability"], 6)))
    return best["layer"], per_layer, {"k": k, "seed": seed,
                                      "pairing": "unpaired (stated "
                                      "departure; see _length_rows)"}


def transfer_eval(u, refusal_cap, layer, seed=bp.SEED):
    """analysis_transfer's evaluation with a FIXED direction u — same
    tiers, same statistic, same seeded scenario-flip nulls."""
    out = {}
    for label, types in (("harm_anchored_confirmatory", bp.HARM_TYPES),
                         ("intermediate_exploratory",
                          bp.INTERMEDIATE_TYPES)):
        rows = [r for r in refusal_cap.rows if int(r["type_num"]) in types]
        sub = bp.RefusalCapture(rows, refusal_cap.acts,
                                refusal_cap.n_layers, refusal_cap.d)
        scen = {r["scenario_id"] for r in rows}
        sep = bp._refusal_separation(sub, u, layer, scen)
        rng = np.random.default_rng(seed)
        null = [bp._refusal_separation(sub, u, layer, scen,
                                       flip={s: rng.random() < 0.5
                                             for s in sorted(scen)})
                for _ in range(max(50, bp.N_PERM // 10))]
        out[label] = {"separation": sep,
                      "null_p95": float(np.percentile(null, 95)),
                      "exceeds_null_p95": bool(
                          sep > np.percentile(null, 95)),
                      "n_scenarios": len(scen)}
    return out


def check4(cap, refusal_cap, comp, emotion_path, run_dir):
    lengths = prompt_lengths(run_dir)
    lrows, median = _length_rows(cap, lengths)
    layer_l, curve_l, meta_l = select_layer_length(lrows, cap.acts,
                                                   cap.n_layers)
    out = {"median_split_tokens": median,
           "n_agreement_rows": len(lrows),
           "n_long": sum(1 for r in lrows if r["long"]),
           "length_direction_selected_layer": layer_l,
           "selection_meta": meta_l,
           "existence_split_half_at_selected": next(
               r for r in curve_l if r["layer"] == layer_l),
           "layer_curve_top5": sorted(
               curve_l, key=lambda r: -r["heldout_separation"])[:5]}
    u_l8 = bp.unit(_fit_length_dir(lrows, cap.acts, SEL_LAYER))
    u_lown = bp.unit(_fit_length_dir(lrows, cap.acts, layer_l))
    u_c8 = bp.unit(bp.fit_conflict_direction(cap, SEL_LAYER))
    u_cown = bp.unit(bp.fit_conflict_direction(cap, layer_l))
    out["a_cosines"] = {
        "L8": float(u_l8 @ u_c8),
        f"own_layer_L{layer_l}": float(u_lown @ u_cown)}

    # (b) reducibility with and without the length direction
    def reducibility(with_length):
        conflict = u_c8
        emos = bp.load_emotion_directions(Path(emotion_path), SEL_LAYER)
        regs = [bp.unit(v) for _, v in sorted(emos.items())]
        regs.append(bp.unit(bp.fit_difficulty_direction(comp, SEL_LAYER)))
        if with_length:
            regs.append(u_l8)
        X = np.stack(regs, axis=1)
        coef, *_ = np.linalg.lstsq(X, conflict, rcond=None)
        resid = conflict - X @ coef
        ve = 1.0 - float(np.sum(resid ** 2))
        rng = np.random.default_rng(bp.SEED)
        scen = sorted({r["scenario_id"] for r in cap.rows})
        rng.shuffle(scen)
        held = set(scen[len(scen) // 2:])
        contrasts = [c for s, cs in
                     bp.scenario_contrasts(cap, SEL_LAYER).items()
                     if s in held for c in cs]
        C = np.stack(contrasts)
        y = C @ conflict
        Z = C @ X
        cz, *_ = np.linalg.lstsq(Z, y, rcond=None)
        ss_res = float(np.sum((y - Z @ cz) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        return {"variance_explained": round(ve, 4),
                "helditem_projection_r2": round(1 - ss_res / ss_tot, 4),
                "n_regressors": X.shape[1]}
    out["b_reducibility"] = {"without_length": reducibility(False),
                             "with_length": reducibility(True)}

    # (c) the sharp test: length direction on the transfer analysis,
    # exactly as the conflict direction was evaluated
    out["c_transfer_at_L8"] = transfer_eval(u_l8, refusal_cap, SEL_LAYER)
    out["c_transfer_at_own_layer"] = transfer_eval(u_lown, refusal_cap,
                                                   layer_l)
    return out


# ---------------------------------------------------------------------------
# Part 3 (researcher-directed 2026-08-06): length-matched subsample analysis.
# Feasibility (Stage A) gates the separation (Stage B); the gate is reported
# before any separation is computed.
# ---------------------------------------------------------------------------

PRESTATED_P3 = (
    "Matched separation ≳ 1 SD against its matched null, with the length "
    "direction flat on the same set → first direct evidence of conflict "
    "content at fixed length; the follow-up battery becomes confirmation, "
    "and the study's conservative sentence upgrades from 'on hold' to "
    "'supported at reduced magnitude, pending length-matched replication.' "
    "Matched separation at null scale with adequate power → the "
    "within-family signal is not separable from length in this capture; "
    "the follow-up battery is the whole game, and the validity sentence "
    "stays as written. Intermediate or power-marginal → reported as such, "
    "no adjudication, follow-up proceeds regardless.")
P3_CAUTION = (
    "Matching restricts to the length-overlap tails, which are not a "
    "random subsample — short-opposition and long-agreement rows may be "
    "systematically atypical scenarios; surviving scenarios are named so "
    "this is inspectable.")
P3_EFFECT_SCALE = ("The ~1.1 SD residualized floor (annex part 1) is the "
                   "effect scale of interest; the feasibility gate requires "
                   "the matched design to detect ~1 SD.")
MDES_NOTE = ("minimum detectable effect (standardized separation), "
             "two-sided alpha=.05, power .80: MDES = 2.802*sqrt(2/n) with "
             "n = per-group matched cells")
PAIR_TOL = 5        # tokens
STRATUM_W = 10      # tokens
GATE_MDES = 1.0     # SD


def _cells(cap_rows, acts, lengths, layer, u, u_len):
    """Order-averaged cells: (sid, cond) -> conflict projection, length
    projection, token length. AB/BA rows share token count (same words,
    options reordered)."""
    bucket = defaultdict(lambda: {"proj": [], "plen": [], "len": []})
    for r in cap_rows:
        b = bucket[(r["scenario_id"], r["condition"])]
        b["proj"].append(float(acts[r["prompt_key"]][layer] @ u))
        b["plen"].append(float(acts[r["prompt_key"]][layer] @ u_len))
        b["len"].append(lengths[r["prompt_key"]])
    return [{"sid": s, "cond": c, "proj": float(np.mean(v["proj"])),
             "proj_len": float(np.mean(v["plen"])),
             "length": float(np.mean(v["len"])),
             "opp": c.startswith("oppose")}
            for (s, c), v in sorted(bucket.items())]


def _mdes(n_per_group):
    return float(2.802 * np.sqrt(2.0 / n_per_group)) if n_per_group else None


def _greedy_pairs(cells, tol=PAIR_TOL):
    """Greedy nearest-length matching, opposition -> agreement, within
    tol tokens; same-scenario matches preferred, cross-scenario permitted
    and flagged."""
    opp = sorted([c for c in cells if c["opp"]], key=lambda c: c["length"])
    agr = [c for c in cells if not c["opp"]]
    used, pairs = set(), []
    for o in opp:
        best, best_d, best_same = None, None, False
        for i, a in enumerate(agr):
            if i in used:
                continue
            d = abs(a["length"] - o["length"])
            if d > tol:
                continue
            same = a["sid"] == o["sid"]
            key = (not same, d)
            if best is None or key < ((not best_same), best_d):
                best, best_d, best_same = i, d, same
        if best is not None:
            used.add(best)
            pairs.append({"opp": o, "agr": agr[best], "dist": best_d,
                          "same_scenario": best_same})
    return pairs


def _sep(cells_opp_proj, cells_agr_proj):
    if len(cells_opp_proj) < 2 or len(cells_agr_proj) < 2:
        return float("nan")
    pooled = np.sqrt((np.var(cells_opp_proj, ddof=1) +
                      np.var(cells_agr_proj, ddof=1)) / 2)
    return float((np.mean(cells_opp_proj) - np.mean(cells_agr_proj))
                 / pooled) if pooled > 0 else 0.0


def _stage_a(cells, family):
    opp = [c for c in cells if c["opp"]]
    agr = [c for c in cells if not c["opp"]]
    lo = max(min(c["length"] for c in opp), min(c["length"] for c in agr))
    hi = min(max(c["length"] for c in opp), max(c["length"] for c in agr))
    in_ov = [c for c in cells if lo <= c["length"] <= hi]
    strata = defaultdict(lambda: {"opp": 0, "agr": 0})
    for c in in_ov:
        b = int((c["length"] - lo) // STRATUM_W)
        strata[b]["opp" if c["opp"] else "agr"] += 1
    usable = {b: v for b, v in strata.items()
              if v["opp"] >= 2 and v["agr"] >= 2}
    n_strat = min(sum(v["opp"] for v in usable.values()),
                  sum(v["agr"] for v in usable.values()))
    pairs = _greedy_pairs(cells)
    proj_sd = float(np.std([c["proj"] for c in cells], ddof=1))
    return {
        "family": family,
        "overlap_region_tokens": [lo, hi],
        "n_cells_opp_total": len(opp), "n_cells_agr_total": len(agr),
        "n_cells_in_overlap": len(in_ov),
        "stratified": {"bin_width_tokens": STRATUM_W,
                       "strata_counts": {f"{lo + b*STRATUM_W:.0f}-"
                                         f"{lo + (b+1)*STRATUM_W:.0f}":
                                         dict(v) for b, v in
                                         sorted(strata.items())},
                       "usable_strata": len(usable),
                       "n_matched": n_strat,
                       "mdes": _mdes(n_strat)},
        "pair_matched": {"tolerance_tokens": PAIR_TOL,
                         "n_pairs": len(pairs),
                         "n_same_scenario": sum(1 for p in pairs
                                                if p["same_scenario"]),
                         "n_cross_scenario_flagged": sum(
                             1 for p in pairs if not p["same_scenario"]),
                         "mean_pair_length_dist": (float(np.mean(
                             [p["dist"] for p in pairs])) if pairs
                             else None),
                         "mdes": _mdes(len(pairs))},
        "per_row_projection_sd": proj_sd,
        "gate_mdes_threshold_SD": GATE_MDES,
        "gate_pass_pair_matched": bool(pairs and
                                       _mdes(len(pairs)) <= GATE_MDES),
        "gate_pass_stratified": bool(n_strat and
                                     _mdes(n_strat) <= GATE_MDES),
    }


def _stage_b(cells, pairs, seed=bp.SEED):
    """Matched separations + scenario-permutation null rebuilt within the
    matched set (per-scenario flips, seeded) + the diagnostic pair."""
    mo = [p["opp"] for p in pairs]
    ma = [p["agr"] for p in pairs]
    sep = _sep([c["proj"] for c in mo], [c["proj"] for c in ma])
    rng = np.random.default_rng(seed)
    scens = sorted({c["sid"] for c in mo} | {c["sid"] for c in ma})
    null = []
    for _ in range(bp.N_PERM):
        flip = {s: rng.random() < 0.5 for s in scens}
        po, pa = [], []
        for p in pairs:
            o, a = p["opp"], p["agr"]
            if flip[o["sid"]]:
                o, a = a, o
            po.append(o["proj"])
            pa.append(a["proj"])
        null.append(_sep(po, pa))
    null = np.array(null)
    return {
        "n_pairs": len(pairs),
        "matched_separation": sep,
        "matched_null_p95": float(np.percentile(null, 95)),
        "matched_null_p5": float(np.percentile(null, 5)),
        "exceeds_matched_null_p95": bool(sep > np.percentile(null, 95)),
        "diagnostic_mean_length_diff": float(
            np.mean([p["opp"]["length"] - p["agr"]["length"]
                     for p in pairs])),
        "diagnostic_length_direction_separation": _sep(
            [c["proj_len"] for c in mo], [c["proj_len"] for c in ma]),
        "surviving_scenarios": sorted(
            {c["sid"] for c in mo} | {c["sid"] for c in ma}),
    }


def check5(cap, refusal_cap, run_dir):
    lengths = prompt_lengths(run_dir)
    u_c = bp.unit(bp.fit_conflict_direction(cap, SEL_LAYER))
    lrows, _ = _length_rows(cap, lengths)
    u_l = bp.unit(_fit_length_dir(lrows, cap.acts, SEL_LAYER))

    choice_cells = _cells(cap.rows, cap.acts, lengths, SEL_LAYER, u_c, u_l)
    stage_a = {"choice": _stage_a(choice_cells, "choice")}
    tiers = {}
    for label, types in (("refusal_harm_T7_9", bp.HARM_TYPES),
                         ("refusal_intermediate_T10_12",
                          bp.INTERMEDIATE_TYPES)):
        rows = [r for r in refusal_cap.rows if int(r["type_num"]) in types]
        cells = _cells(rows, refusal_cap.acts, lengths, SEL_LAYER, u_c,
                       u_l)
        tiers[label] = cells
        stage_a[label] = _stage_a(cells, label)

    out = {"stage_a_feasibility": stage_a}
    stage_b = {}
    if stage_a["choice"]["gate_pass_pair_matched"]:
        pairs = _greedy_pairs(choice_cells)
        stage_b["choice_pair_matched"] = _stage_b(choice_cells, pairs)
    for label in tiers:
        if stage_a[label]["gate_pass_pair_matched"]:
            pairs = _greedy_pairs(tiers[label])
            stage_b[label + "_pair_matched"] = _stage_b(tiers[label],
                                                        pairs)
    out["stage_b_matched_separation"] = (stage_b if stage_b else
                                         "GATED OUT — infeasible at the "
                                         "required power")
    return out




# ---------------------------------------------------------------------------
# Part 5 (researcher-directed 2026-08-06): residual depth profile.
# Post-hoc DIAGNOSTIC — explicitly NOT layer re-selection; no shipped claim
# moves layers on this basis.
# ---------------------------------------------------------------------------

PRESTATED_P5 = (
    "a depth band where residualized separation holds up while "
    "within-condition length tracking drops is the candidate home of a "
    "genuine conflict signal — reported as a hypothesis for the follow-up "
    "battery to test at its pre-stated layer, never as a revised result. "
    "Flat residual everywhere, or residual tracking the length curve — "
    "the pessimistic arm — says the signal has no length-independent home "
    "at any depth in this capture, and the follow-up carries the whole "
    "burden.")


def _resid_on(vals, L, E):
    z = lambda x: (x - x.mean()) / (x.std(ddof=1) if x.std(ddof=1) else 1)
    X = np.column_stack([np.ones(len(vals)), z(L), z(E)])
    coef, *_ = np.linalg.lstsq(X, vals, rcond=None)
    return vals - X @ coef


def check_depth(cap, refusal_cap, run_dir):
    lengths = prompt_lengths(run_dir)
    lrows, _ = _length_rows(cap, lengths)
    ch_L = np.array([lengths[r["prompt_key"]] for r in cap.rows], float)
    ch_E = np.array([float(r["entropy"]) for r in cap.rows], float)
    curves = []
    for layer in range(cap.n_layers):
        u = bp.unit(bp.fit_conflict_direction(cap, layer))
        proj = np.array([float(cap.acts[r["prompt_key"]][layer] @ u)
                         for r in cap.rows])
        resid = _resid_on(proj, ch_L, ch_E)

        def cell_avg(vals):
            cells = defaultdict(list)
            for r, v in zip(cap.rows, vals):
                cells[(r["scenario_id"], r["condition"])].append(v)
            return {k: float(np.mean(v)) for k, v in cells.items()}
        sep_resid = scalar_separation(cell_avg(resid))

        def wr(pred):
            m = np.array([pred(r) for r in cap.rows])
            if m.sum() < 3:
                return 0.0
            return float(np.corrcoef(ch_L[m], proj[m])[0, 1])
        within_r = 0.5 * (wr(lambda r: r["condition"].startswith("agree"))
                          + wr(lambda r: r["condition"].startswith("oppose")))

        ld = _fit_length_dir(lrows, cap.acts, layer)
        cos_len = float(bp.unit(ld) @ u) if ld is not None else float("nan")

        tier_resid = {}
        for label, types in (("harm", bp.HARM_TYPES),
                             ("intermediate", bp.INTERMEDIATE_TYPES)):
            rows = [r for r in refusal_cap.rows
                    if int(r["type_num"]) in types]
            rl = np.array([lengths[r["prompt_key"]] for r in rows], float)
            re_ = np.array([float(r["entropy"]) for r in rows], float)
            pr = np.array([float(refusal_cap.acts[r["prompt_key"]][layer]
                                 @ u) for r in rows])
            rr = _resid_on(pr, rl, re_)
            by = {(r["scenario_id"], r["condition"]): v
                  for r, v in zip(rows, rr)}
            po, pa = [], []
            for (sid, cond), v in by.items():
                if cond in bp.REFUSAL_OPP:
                    partner = bp.REFUSAL_AGR[bp.REFUSAL_OPP.index(cond)]
                    if (sid, partner) in by:
                        po.append(v)
                        pa.append(by[(sid, partner)])
            if len(po) >= 2:
                pooled = np.sqrt((np.var(po, ddof=1)
                                  + np.var(pa, ddof=1)) / 2)
                tier_resid[label] = float((np.mean(po) - np.mean(pa))
                                          / pooled) if pooled else 0.0
            else:
                tier_resid[label] = float("nan")
        curves.append({"layer": layer,
                       "residualized_separation_choice": round(sep_resid, 4),
                       "within_condition_length_r": round(within_r, 4),
                       "cosine_conflict_length": round(cos_len, 4),
                       "residualized_transfer_harm":
                           round(tier_resid["harm"], 4),
                       "residualized_transfer_intermediate":
                           round(tier_resid["intermediate"], 4)})
    return curves


def depth_figure(curves, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    xs = [c["layer"] for c in curves]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, [c["residualized_separation_choice"] for c in curves],
            "o-", ms=3, color="#2c7fb8",
            label="choice separation, residualized (SD)")
    ax.plot(xs, [c["residualized_transfer_harm"] for c in curves],
            "s--", ms=3, color="#41ab5d",
            label="transfer resid., harm tier")
    ax.plot(xs, [c["residualized_transfer_intermediate"] for c in curves],
            "s:", ms=3, color="#a1d99b",
            label="transfer resid., intermediate tier")
    ax.plot(xs, [c["within_condition_length_r"] for c in curves],
            "^-", ms=3, color="#d95f0e",
            label="within-condition length r")
    ax.plot(xs, [c["cosine_conflict_length"] for c in curves],
            "v-", ms=3, color="#969696",
            label="cos(conflict, length) at L")
    for l, txt in ((8, "L8"), (4, "L4")):
        ax.axvline(l, color="grey", lw=1, ls="--")
        ax.annotate(txt, (l, ax.get_ylim()[1] * 0.95), fontsize=9)
    ax.axhline(0, color="black", lw=0.5)
    ax.set_xlabel("layer")
    ax.set_title("Residual depth profile — post-hoc diagnostic, "
                 "NOT layer re-selection")
    ax.legend(fontsize=8)
    fig.tight_layout()
    tmp = str(out_path) + ".tmp"
    fig.savefig(tmp, dpi=150, format="png")
    plt.close(fig)
    Path(tmp).replace(out_path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--comparator-dir", required=True)
    ap.add_argument("--emotion",
                    default="results/emotion_vectors_llama8b_inference.pt")
    ap.add_argument("--part", type=int, default=1, choices=(1, 2, 3, 5))
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    run_dir = Path(args.run_dir)
    out = run_dir / "analysis" / "robustness_annex"
    out.mkdir(parents=True, exist_ok=True)

    cap = bp.load_choice_capture(run_dir)
    refusal_cap = bp.load_refusal_capture(run_dir)
    comp = bp.load_competition_capture(run_dir)

    if args.part == 5:
        digests = {}
        curves = check_depth(cap, refusal_cap, run_dir)
        c6 = {"_header": header(run_dir, {
                  "check": "depth — residual profile across all layers",
                  "part": 5,
                  "NOT_layer_reselection": "post-hoc diagnostic; no "
                      "shipped claim moves layers on this basis",
                  "prestated_interpretation": PRESTATED_P5,
                  "within_condition_r_definition": "mean of r(proj, "
                      "length) within agreement-pooled and within "
                      "opposition-pooled (check 3 statistic)"}),
              "per_layer": curves}
        bp.write_artifact(out / "ANNEX_part5_depth_profile.json", {},
                          c6, digests)
        fig_path = out / "ANNEX_part5_depth_profile.png"
        depth_figure(curves, fig_path)
        sha, size = file_digest(fig_path)
        digests[fig_path.name] = {"sha256": sha, "bytes": size}
        print(f"DIGEST {sha} {size} {fig_path.name}")
        man = {"_header": header(run_dir, {"part": 5}),
               "artifacts": digests}
        atomic_write(out / "ANNEX_part5_manifest.json",
                     lambda f: f.write(json.dumps(man, indent=2) + "\n"),
                     mode="w", encoding="utf-8", newline="\n")
        sha, size = file_digest(out / "ANNEX_part5_manifest.json")
        print(f"DIGEST {sha} {size} ANNEX_part5_manifest.json")
        print("ROBUSTNESS ANNEX PART 5 COMPLETE — diagnostic only.")
        return 0

    if args.part == 3:
        digests = {}
        c5 = {"_header": header(run_dir, {
                  "check": "5 — length-matched subsample (Stage A "
                           "feasibility gates Stage B)",
                  "part": 3,
                  "prestated_interpretation": PRESTATED_P3,
                  "caution": P3_CAUTION,
                  "effect_scale": P3_EFFECT_SCALE,
                  "mdes_definition": MDES_NOTE,
                  "separation_definition": "(mean opp proj - mean agr "
                      "proj) / pooled SD over matched order-averaged "
                      "cells — the pipeline's statistic on the matched "
                      "set"}),
              **check5(cap, refusal_cap, run_dir)}
        bp.write_artifact(out / "ANNEX_check5_length_matched.json", {},
                          c5, digests)
        man = {"_header": header(run_dir, {"part": 3}),
               "artifacts": digests}
        atomic_write(out / "ANNEX_part3_manifest.json",
                     lambda f: f.write(json.dumps(man, indent=2) + "\n"),
                     mode="w", encoding="utf-8", newline="\n")
        sha, size = file_digest(out / "ANNEX_part3_manifest.json")
        print(f"DIGEST {sha} {size} ANNEX_part3_manifest.json")
        print("ROBUSTNESS ANNEX PART 3 COMPLETE — post-hoc, exploratory, "
              "no iteration.")
        return 0

    if args.part == 2:
        digests = {}
        c3 = {"_header": header(run_dir, {
                  "check": "3 — within-condition length tracking",
                  "part": 2,
                  "prestated_interpretation": PRESTATED_C3}),
              **check3(cap, refusal_cap, run_dir)}
        bp.write_artifact(out / "ANNEX_check3_within_condition.json", {},
                          c3, digests)
        c4 = {"_header": header(run_dir, {
                  "check": "4 — pure length direction as comparator",
                  "part": 2,
                  "prestated_interpretation": PRESTATED_C4}),
              **check4(cap, refusal_cap, comp, args.emotion, run_dir)}
        bp.write_artifact(out / "ANNEX_check4_length_direction.json", {},
                          c4, digests)
        man = {"_header": header(run_dir, {"part": 2}),
               "artifacts": digests}
        atomic_write(out / "ANNEX_part2_manifest.json",
                     lambda f: f.write(json.dumps(man, indent=2) + "\n"),
                     mode="w", encoding="utf-8", newline="\n")
        sha, size = file_digest(out / "ANNEX_part2_manifest.json")
        print(f"DIGEST {sha} {size} ANNEX_part2_manifest.json")
        print("ROBUSTNESS ANNEX PART 2 COMPLETE — post-hoc, exploratory, "
              "no iteration.")
        return 0

    digests = {}
    c1 = {"_header": header(run_dir, {"check": "1 — surface-feature "
                                              "regression"}),
          **check1(cap, run_dir)}
    bp.write_artifact(out / "ANNEX_check1_surface_features.json", {},
                      c1, digests)
    c2 = {"_header": header(run_dir, {"check": "2 — placebo order-contrast "
                                              "through identical pipeline"}),
          **check2(cap, refusal_cap, comp, Path(args.comparator_dir),
                   Path(args.emotion))}
    bp.write_artifact(out / "ANNEX_check2_placebo_panel.json", {},
                      c2, digests)
    man = {"_header": header(run_dir), "artifacts": digests}
    atomic_write(out / "ANNEX_manifest.json",
                 lambda f: f.write(json.dumps(man, indent=2) + "\n"),
                 mode="w", encoding="utf-8", newline="\n")
    sha, size = file_digest(out / "ANNEX_manifest.json")
    print(f"DIGEST {sha} {size} ANNEX_manifest.json")
    print("ROBUSTNESS ANNEX COMPLETE — post-hoc, exploratory, filed "
          "alongside as_designed/, never mixed into it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
