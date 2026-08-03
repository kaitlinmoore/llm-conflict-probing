#!/usr/bin/env python3
"""
make_smoke_shard.py — synthetic smoke-shard fixture matching the capture
contract in battery_pipeline.py (analysis_pipeline_brief.md: 10–15 items
end-to-end incl. an automatic-labeler pass). Deterministic (seed 23).

Planted structure so the analyses produce sane numbers on a toy scale:
a conflict signal concentrated at PLANT_LAYER in choice opposition cells,
carried at reduced strength in refusal opposition cells (transfer),
an independent refusal direction in the comparator sets, and a difficulty
direction in competition torn items. n_layers=8, d=64.
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

SEED = 23
N_LAYERS, D = 8, 64
PLANT_LAYER = 5

GEN = {
    "agree_comply": 'Here\'s the reply: "Dear friend, as you asked..."',
    "agree_refuse": "I can't help with this. I'd encourage you to "
                    "reconsider the plan itself.",
    "oppose_tip_comply": "I should note the risk to her privacy. Here's "
                         'the draft: "Dear committee..."',
    # decline-with-delivery: hedge via lower-rung tie-break, UNCERTAIN
    # flagged — exercises the boundary-adjacent path end-to-end
    "oppose_tip_refuse": 'I must decline to do this fully, but here\'s a '
                         'version: "Dear Hana, a shorter note..."',
}


def make(run_dir: Path, comparator_dir: Path, seed=SEED):
    rng = np.random.default_rng(seed)
    conflict = rng.normal(size=D)
    conflict /= np.linalg.norm(conflict)
    refusal = rng.normal(size=D)
    refusal -= (refusal @ conflict) * conflict
    refusal /= np.linalg.norm(refusal)
    difficulty = rng.normal(size=D)
    difficulty /= np.linalg.norm(difficulty)

    rows, acts = [], {}

    def emit(key, vec_by_layer, **meta):
        acts[key] = np.stack(vec_by_layer).astype(np.float16)
        row = {"prompt_key": key, "row_id": key, "prompt_sha256": key,
               "entropy": f"{rng.uniform(0.5, 3.0):.4f}",
               "p_A": "", "p_B": "", "generation": ""}
        row.update(meta)
        rows.append(row)

    def base():
        return [rng.normal(scale=1.0, size=D) for _ in range(N_LAYERS)]

    # choice: 2 types x 4 scenarios x 4 conditions x 2 orders
    for t, tid in ((1, "type1_honesty_vs_care"), (3, "type3_mercy_vs_desert")):
        for s in range(1, 5):
            sid = f"SM-t{t}-S{s}"
            for cond in ("agree_A", "agree_B", "oppose_tip_A", "oppose_tip_B"):
                for order in ("AB", "BA"):
                    v = base()
                    if cond.startswith("oppose"):
                        v[PLANT_LAYER] = v[PLANT_LAYER] + 3.0 * conflict
                    emit(f"{tid}:{sid}:{cond}:{order}:open", v,
                         row_id=f"{tid}:{sid}:{cond}:{order}",
                         type_id=tid, type_num=t, family="choice",
                         scenario_id=sid, condition=cond, order=order,
                         arm="open_ended", expected_pick="A",
                         expected_response="")
    # refusal: one harm-anchored + one intermediate type, 3 scenarios each
    for t, tid in ((7, "type7_harm_vs_autonomy"),
                   (10, "type10_privacy_vs_care")):
        for s in range(1, 4):
            sid = f"SM-t{t}-S{s}"
            for cond in ("agree_comply", "agree_refuse",
                         "oppose_tip_comply", "oppose_tip_refuse"):
                v = base()
                if cond.startswith("oppose"):
                    v[PLANT_LAYER] = v[PLANT_LAYER] + 1.5 * conflict
                rows_meta = dict(row_id=f"{tid}:{sid}:{cond}:NA",
                                 type_id=tid, type_num=t, family="refusal",
                                 scenario_id=sid, condition=cond, order="NA",
                                 arm="open_ended", expected_pick="",
                                 expected_response=("comply" if "comply"
                                                    in cond else "refuse"))
                emit(f"{tid}:{sid}:{cond}:NA:open", v, **rows_meta)
                rows[-1]["generation"] = GEN[cond]
    # answer-only arm rows (choice, with option-token probabilities)
    for i, r in enumerate([r for r in rows if r["family"] == "choice"][:8]):
        key = r["prompt_key"].replace(":open", ":ao")
        acts[key] = acts[r["prompt_key"]]
        ao = dict(r)
        ao.update({"prompt_key": key, "arm": "answer_only",
                   "p_A": f"{rng.uniform(0.2, 0.8):.4f}"})
        ao["p_B"] = f"{1 - float(ao['p_A']):.4f}"
        rows.append(ao)
    # competition: 4 torn + 4 easy
    for i in range(4):
        for cond, boost in (("torn", 2.0), ("easy", 0.0)):
            v = base()
            v[PLANT_LAYER] = v[PLANT_LAYER] + boost * difficulty
            emit(f"competition:CT-{cond}-{i}:NA:open", v,
                 row_id=f"competition:CT-{cond}-{i}",
                 type_id=f"competition_{cond}", type_num=0,
                 family="competition", scenario_id=f"CT-{cond}-{i}",
                 condition=cond, order="NA", arm="open_ended",
                 expected_pick="", expected_response="")

    run_dir.mkdir(parents=True, exist_ok=True)
    fields = ["prompt_key", "row_id", "type_id", "type_num", "family",
              "scenario_id", "condition", "order", "arm", "expected_pick",
              "expected_response", "prompt_sha256", "entropy", "p_A", "p_B",
              "generation"]
    with (run_dir / "capture_rows.csv").open("w", encoding="utf-8",
                                             newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    import torch
    torch.save({"activations": {k: torch.from_numpy(v)
                                for k, v in acts.items()},
                "partial": False}, run_dir / "activations.pt")

    # comparator capture: 16 harmful / 16 harmless with refusal direction
    crows, cacts = [], {}
    for setname, boost in (("harmful", 2.5), ("harmless", 0.0)):
        for i in range(16):
            v = base()
            v[PLANT_LAYER] = v[PLANT_LAYER] + boost * refusal
            key = f"cmp:{setname}:{i}"
            cacts[key] = np.stack(v).astype(np.float16)
            crows.append({"prompt_key": key, "set": setname})
    comparator_dir.mkdir(parents=True, exist_ok=True)
    with (comparator_dir / "capture_rows.csv").open(
            "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["prompt_key", "set"])
        w.writeheader()
        w.writerows(crows)
    torch.save({"activations": {k: torch.from_numpy(v)
                                for k, v in cacts.items()},
                "partial": False}, comparator_dir / "activations.pt")

    # toy per-layer emotion artifact matching the Phase-0 structure
    emo = {"vec": {e: {l: torch.from_numpy(
        np.random.default_rng(hash(e) % 2**31 + l).normal(
            size=D).astype(np.float32))
        for l in range(N_LAYERS)} for e in ("happy", "sad", "anxious")},
        "cfg": {"model_name": "smoke", "n_layers": N_LAYERS}}
    torch.save(emo, run_dir / "emotion_smoke.pt")
    print(f"smoke shard: {len(rows)} capture rows, {len(crows)} comparator "
          f"rows -> {run_dir}")


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1
               else "results/battery_run/smoke")
    make(out, out / "comparator")
