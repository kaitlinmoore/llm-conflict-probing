"""Robustness annex part 4 (optional; researcher-directed 2026-08-06):
SAE feature read of the conflict direction. INTERPRETIVE — converging
evidence only, adjudicates nothing. Operative conditional per part 2:
"landed badly" — this annex CANNOT rehabilitate the direction; every
artifact says so. Feature names are auto-generated interpretations,
suggestive never dispositive.

Coverage (gate passed, reported in the artifacts): OpenMOSS Llama-Scope
Llama3_1-8B-Base-L8R-8x — base-trained, layer 8 residual (our anchor hook
verbatim), JumpReLU (theta=0.2021), d_sae=32768; labels via Neuronpedia
source llama3.1-8b/8-llamascope-res-32k. STANDING CAVEAT: base-model SAE
on instruct-model activations is an approximation. Instruct-trained
alternative (Goodfire) exists only at L19 — 11 layers from L8, outside
the signal band; base-at-L8 preferred per the brief's order.
"""
import json
import os
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from safetensors.torch import load_file

sys.path.insert(0, r"C:/dev/GitHub/llm-conflict-probing")
from src.analysis import battery_pipeline as bp
from src.analysis import robustness_annex as ra

REPO = Path(r"C:/dev/GitHub/llm-conflict-probing")
RUN = REPO / "results/battery_run/20260803_222047_llama8b"
CMP = REPO / "results/comparators/20260803_202123_llama8b_refusal_recapture"
SAE_PATH = Path(os.environ["TMP"]) / "sae_l8r" / "final.safetensors"
OUT = RUN / "analysis" / "robustness_annex"
L = 8
TOPK = 20
NP_BASE = "https://www.neuronpedia.org/api"
NP_SRC = "llama3.1-8b/8-llamascope-res-32k"

CAVEATS = {
    "ROBUSTNESS_ANNEX": True, "post_hoc": True, "part": 4,
    "date": "2026-08-06",
    "status": "INTERPRETIVE — converging evidence only, adjudicates "
              "nothing; the length checks (parts 1–3) are the decisive "
              "tests",
    "operative_conditional": "parts 1–3 LANDED BADLY (deep length "
              "confound; transfer contaminated; matched check gated out) "
              "— this annex CANNOT rehabilitate the direction",
    "label_caveat": "SAE feature names are auto-generated "
              "interpretations, suggestive never dispositive",
    "sae_caveat": "base-model SAE (Llama-Scope L8R-8x) on instruct-model "
              "activations is an approximation; instruct-trained SAE "
              "exists only at L19 (Goodfire), 11 layers off-band",
    "encode_note": "encode = jumprelu(a_scaled @ W_enc + b_enc), "
              "a_scaled = a * (6.3125 / mean ||a|| over our L8 anchors) "
              "— matches the SAE's dataset-average input norm; "
              "approximation stated",
    "attribution_note": "attribution = cosine(direction, decoder row); "
              "reconstruction quality = R^2 of the direction onto its "
              "top-20 decoder atoms (the full 32k basis is overcomplete "
              "and reconstructs anything trivially)",
}


def np_label(idx):
    try:
        with urllib.request.urlopen(
                f"{NP_BASE}/feature/{NP_SRC}/{idx}", timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
        ex = d.get("explanations") or []
        return (ex[0].get("description", "").strip()
                if ex else "(no label)")
    except Exception as e:
        return f"(label fetch failed: {type(e).__name__})"


def np_search(query):
    try:
        req = urllib.request.Request(
            f"{NP_BASE}/explanation/search",
            data=json.dumps({"modelId": "llama3.1-8b",
                             "layers": ["8-llamascope-res-32k"],
                             "query": query}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
        res = d.get("results", d if isinstance(d, list) else [])
        out = []
        for item in res[:10]:
            out.append({"index": int(item.get("index")),
                        "label": item.get("description", "").strip(),
                        "score": item.get("cosine_similarity",
                                          item.get("score"))})
        return out
    except Exception as e:
        return f"search unavailable: {type(e).__name__}: {e}"


def main():
    sys.stdout.reconfigure(errors="replace")
    sd = load_file(str(SAE_PATH))
    print("tensors:", {k: tuple(v.shape) for k, v in sd.items()})
    W_enc = sd["encoder.weight"].float() if "encoder.weight" in sd else None
    if W_enc is None:  # discover naming
        for k in sd:
            if "enc" in k and sd[k].dim() == 2:
                W_enc = sd[k].float()
                enc_name = k

    # naming resolved after first print; handled generically below
    def find(sub, ndim):
        for k, v in sd.items():
            if sub in k and v.dim() == ndim:
                return k, v.float()
        return None, None
    ken, W_enc = find("encoder", 2)
    kde, W_dec = find("decoder", 2)
    kbe, b_enc = find("encoder", 1)
    kbd, b_dec = find("decoder", 1)
    print("using:", ken, kde, kbe, kbd)
    # orient: W_dec rows = features [d_sae, d_model]
    if W_dec.shape[0] == 4096:
        W_dec = W_dec.T
    if W_enc.shape[0] == 4096:
        W_enc = W_enc.T          # -> [d_sae, d_model]; encode a @ W_enc.T
    d_sae = W_dec.shape[0]
    dec_unit = torch.nn.functional.normalize(W_dec, dim=1)

    cap = bp.load_choice_capture(RUN)
    refusal_cap = bp.load_refusal_capture(RUN)
    comp = bp.load_competition_capture(RUN)
    lengths = ra.prompt_lengths(RUN)

    u_c = torch.tensor(bp.unit(bp.fit_conflict_direction(cap, L)))
    lrows, _ = ra._length_rows(cap, lengths)
    u_l = torch.tensor(bp.unit(ra._fit_length_dir(lrows, cap.acts, L)))
    refd, _, _ = bp.fit_refusal_direction(CMP, L)
    u_r = torch.tensor(bp.unit(refd))

    # ---- Check "5" (brief numbering): whose features does each speak? --
    def topk_read(u, name):
        att = (dec_unit @ u.float())
        vals, idx = torch.topk(att.abs(), TOPK)
        feats = []
        for i in idx.tolist():
            feats.append({"feature": i,
                          "cosine": round(float(att[i]), 4),
                          "label": np_label(i),
                          "neuronpedia":
                              f"https://www.neuronpedia.org/{NP_SRC}/{i}"})
            time.sleep(0.4)
        A = W_dec[idx].T.numpy()
        coef, *_ = np.linalg.lstsq(A, u.numpy(), rcond=None)
        resid = u.numpy() - A @ coef
        r2 = 1.0 - float((resid ** 2).sum())
        print(f"{name}: top-{TOPK} read, R2_top20={r2:.3f}")
        return {"direction": name, "top_features": feats,
                "reconstruction_R2_top20": round(r2, 4)}

    reads = {"conflict_L8": topk_read(u_c, "conflict_L8"),
             "length_L8": topk_read(u_l, "length_L8"),
             "refusal_L8_reference": topk_read(u_r, "refusal_L8")}
    set_c = {f["feature"] for f in reads["conflict_L8"]["top_features"]}
    set_l = {f["feature"] for f in reads["length_L8"]["top_features"]}
    set_r = {f["feature"] for f in reads["refusal_L8_reference"]["top_features"]}
    overlap = {"conflict_vs_length_topk_overlap": len(set_c & set_l),
               "conflict_vs_length_shared_features": sorted(set_c & set_l),
               "conflict_vs_refusal_topk_overlap": len(set_c & set_r)}

    # ---- Check "6": feature activation by condition -------------------
    mean_norm = float(np.mean([np.linalg.norm(a[L])
                               for a in cap.acts.values()]))
    scale = 6.3125 / mean_norm
    theta = 0.2021484375

    def encode_mean(anchors, feat_ids):
        A = torch.tensor(np.stack(anchors)) * scale
        z = A @ W_enc.T + b_enc
        z = z * (z > theta)
        return z[:, feat_ids].mean(dim=0)

    top10 = [f["feature"]
             for f in reads["conflict_L8"]["top_features"][:10]]
    groups = {}
    opp = [cap.acts[r["prompt_key"]][L] for r in cap.rows
           if r["condition"].startswith("oppose")]
    agr_rows = [r for r in cap.rows if r["condition"].startswith("agree")]
    agr = [cap.acts[r["prompt_key"]][L] for r in agr_rows]
    lens_a = sorted(lengths[r["prompt_key"]] for r in agr_rows)
    cut = lens_a[int(len(lens_a) * 2 / 3)]
    agr_long = [cap.acts[r["prompt_key"]][L] for r in agr_rows
                if lengths[r["prompt_key"]] >= cut]
    torn = [comp.acts[r["prompt_key"]][L] for r in comp.rows
            if r["condition"] == "torn" and r["arm"] == "open_ended"]
    groups = {"opposition": opp, "agreement": agr,
              f"agreement_long_top_tercile(>={cut}tok)": agr_long,
              "competition_torn": torn}
    table = {}
    for g, anchors in groups.items():
        m = encode_mean(anchors, top10)
        table[g] = {str(fid): round(float(v), 4)
                    for fid, v in zip(top10, m)}
    cond_table = {"top10_conflict_features": top10,
                  "mean_activation_by_group": table,
                  "n_per_group": {g: len(v) for g, v in groups.items()},
                  "anchor_mean_norm_ours": round(mean_norm, 3),
                  "sae_dataset_norm": 6.3125,
                  "prestated_reading": "fires on opposition AND torn but "
                      "not long-agreement -> tension/deliberation-like; "
                      "tracks length tercile regardless of condition -> "
                      "the confound; opposition-only (not torn) -> "
                      "candidate value-conflict-specific, flagged not "
                      "over-claimed"}

    # ---- Amendment job 3: label-space candidate screening -------------
    screening = {}
    for q in ("dilemma", "tension", "tradeoff", "deliberation",
              "conflict between values"):
        screening[q] = np_search(q)
        time.sleep(0.6)
    # for top hits that returned indices: check-3-style within-condition
    # length regression + condition table on OUR capture
    cand = []
    for q, res in screening.items():
        if isinstance(res, list):
            cand += [r["index"] for r in res[:3]]
    cand = sorted(set(cand))[:12]
    cand_rows = {}
    if cand:
        all_rows = cap.rows
        A = torch.tensor(np.stack([cap.acts[r["prompt_key"]][L]
                                   for r in all_rows])) * scale
        z = A @ W_enc.T + b_enc
        z = (z * (z > theta))[:, cand].numpy()
        Ls = np.array([lengths[r["prompt_key"]] for r in all_rows],
                      dtype=float)
        is_opp = np.array([r["condition"].startswith("oppose")
                           for r in all_rows])
        for j, fid in enumerate(cand):
            zc = z[:, j]
            def rr(mask):
                if mask.sum() < 3 or Ls[mask].std() == 0 or \
                        zc[mask].std() == 0:
                    return None
                return round(float(np.corrcoef(Ls[mask], zc[mask])[0, 1]),
                             3)
            cand_rows[str(fid)] = {
                "label": np_label(fid),
                "mean_act_opposition": round(float(zc[is_opp].mean()), 4),
                "mean_act_agreement": round(float(zc[~is_opp].mean()), 4),
                "r_length_within_agreement": rr(~is_opp),
                "r_length_within_opposition": rr(is_opp)}
            time.sleep(0.4)

    digests = {}
    bp.write_artifact(OUT / "ANNEX_part4_sae_directions.json", {},
                      {"_header": {**CAVEATS,
                                   "check": "brief check 5 — whose "
                                            "features does each "
                                            "direction speak?"},
                       **reads, "overlap": overlap}, digests)
    bp.write_artifact(OUT / "ANNEX_part4_sae_conditions.json", {},
                      {"_header": {**CAVEATS,
                                   "check": "brief check 6 — feature "
                                            "activation by condition"},
                       **cond_table}, digests)
    bp.write_artifact(OUT / "ANNEX_part4_sae_screening.json", {},
                      {"_header": {**CAVEATS,
                                   "check": "amendment job 3 — label-"
                                            "space candidate screening"},
                       "queries": screening,
                       "candidates_evaluated": cand_rows}, digests)
    from src.pretest.runner_lib import atomic_write, file_digest
    man = {"_header": CAVEATS, "artifacts": digests,
           "sae_checkpoint": "OpenMOSS-Team/Llama3_1-8B-Base-LXR-8x / "
                             "Llama3_1-8B-Base-L8R-8x (JumpReLU, 32768 "
                             "features)",
           "labels_source": f"neuronpedia {NP_SRC}"}
    atomic_write(OUT / "ANNEX_part4_manifest.json",
                 lambda f: f.write(json.dumps(man, indent=2) + "\n"),
                 mode="w", encoding="utf-8", newline="\n")
    sha, size = file_digest(OUT / "ANNEX_part4_manifest.json")
    print(f"DIGEST {sha} {size} ANNEX_part4_manifest.json")
    print("ANNEX PART 4 COMPLETE")


if __name__ == "__main__":
    main()
