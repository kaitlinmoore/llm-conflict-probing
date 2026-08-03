#!/usr/bin/env python3
"""
run_battery.py — the battery session runner (Pod B; run_configuration.md).
Administers the FROZEN battery (both arms) plus the competition battery and
writes exactly the capture contract documented in
src/analysis/battery_pipeline.py — capture_rows.csv (row_id on every row,
p_A/p_B on answer-only options rows, generation, entropy) and
activations.pt (all-layer fp16 anchors keyed by prompt_key).

Hard preconditions (checked before the model loads):
  - battery_frozen_v1.jsonl sha256 matches freeze_manifest.json.
  - competition file present; its sha recorded in the run manifest.
    Provenance note: data/comparators/competition_battery_draft.jsonl is
    the POST-FIX version (hazard items replaced, aquarium reworded —
    commit e61829f) despite the "draft" filename; the manifest records
    this so the filename smell is on the record.

Mechanics (run_configuration.md): greedy everywhere, <=128 new tokens;
regeneration with a longer budget (256) for label-blocking cutoffs;
seed-fixed shuffled item order (types interleave); anchor discipline per
CLAUDE.md (template-verified anchor, prepend_bos never added — templated()
owns bos; first-row bitwise-identity check per arm); incremental atomic
writes with activation checkpoints every 25 rows (`partial` flag);
resumable (rerun skips completed prompt_keys); in-session automatic
labeler pass (rubric v1.3 §9, digest-locked at run time); 5-sample
stability shard (temp 0.7, seeds 0..4) for refusal rows whose auto label
disagrees with the designed resolution or is uncertain.

Arms: open_ended administers every row; answer_only administers
options-bearing rows only (choice cells + choice-family controls +
competition) — its p_A/p_B come from the anchor's next-token distribution
(sum over tokenizations of "A"/" A" etc., method recorded in the
manifest). Refusal rows have no options and no answer-only arm; the
answer-only fallback in run_configuration is defined for choice items.

⚠ PROMPT TEMPLATE NEEDS RESEARCHER SIGN-OFF BEFORE THE REAL RUN: no
rendering spec exists in the repo (battery_schema.md deliberately left
rendering to the runner). The template below is minimal — stimulus text
verbatim in authored order (stem, shared opposition text, condition
insert), options as "A: … / B: …" lines, and the only added instruction
is the answer-only arm's one line. It is recorded VERBATIM in the run
manifest; approve or amend it before B3 (smoke runs don't gate).

Usage (pod):
  python src/battery/run_battery.py --model meta-llama/Llama-3.1-8B-Instruct \
      --run-dir results/battery_run/<id> [--smoke] [--shard i/N]
"""

import argparse
import csv
import datetime
import hashlib
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.battery import labeler as battery_labeler  # noqa: E402

try:
    from src.pretest import runner_lib as rl
except ImportError:
    sys.path.insert(0, str(REPO_ROOT / "src" / "pretest"))
    import runner_lib as rl

PRODUCED_BY = "Claude Fable 5 (model id claude-fable-5)"
SEED = 23
MAX_NEW_TOKENS = 128
REGEN_TOKENS = 256
STABILITY_SAMPLES = 5
STABILITY_TEMP = 0.7
CHECKPOINT_EVERY = 25

CAPTURE_FIELDS = ["prompt_key", "row_id", "type_id", "type_num", "family",
                  "scenario_id", "condition", "order", "arm",
                  "expected_pick", "expected_response", "prompt_sha256",
                  "entropy", "p_A", "p_B", "generation"]
LABEL_FIELDS = ["row_id", "prompt_key", "label", "uncertain",
                "disclaimer_reluctance", "basis", "regenerated"]
ANSWER_ONLY_INSTRUCTION = "Answer with exactly one letter: A or B."


# ---------------------------------------------------------------------------
# Pure, testable pieces (no torch)
# ---------------------------------------------------------------------------

def verify_frozen(frozen_path: Path, manifest_path: Path):
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    h = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    if h != m["frozen_sha256"]:
        raise SystemExit(f"FROZEN SHA MISMATCH: file {h[:12]}… vs manifest "
                         f"{m['frozen_sha256'][:12]}… — refuse to run")
    return h


def render_stimulus(row) -> str:
    """Stimulus text verbatim, authored order (matches the exhibit's
    administered-text composition): stem, shared opposition text (oppose
    cells), condition insert. Controls/competition: stem only."""
    parts = [row.get("stem", "")]
    if row.get("shared_opposition_text"):
        parts.append(row["shared_opposition_text"])
    if row.get("condition_insert"):
        parts.append(row["condition_insert"])
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def render_prompt(row, arm: str) -> str:
    """The administered user message. Recorded verbatim in the manifest;
    researcher sign-off required before the real run (see module header)."""
    text = render_stimulus(row)
    has_options = bool(row.get("option_A") or row.get("option_B"))
    if has_options:
        text += f"\n\nA: {row['option_A']}\nB: {row['option_B']}"
    if arm == "answer_only":
        if not has_options:
            raise ValueError("answer_only arm is defined for options-bearing "
                             "rows only")
        text += f"\n\n{ANSWER_ONLY_INSTRUCTION}"
    return text


def administered_rows(frozen_rows, competition_rows, smoke=False,
                      shard=None, seed=SEED):
    """(row, arm) work list: open_ended for every row; answer_only for
    options-bearing rows. Seed-fixed shuffle (types interleave). --smoke
    keeps a scenario-balanced 10–15 item slice. --shard 'i/N' takes every
    N-th unit deterministically AFTER ordering."""
    units = []
    for r in frozen_rows:
        units.append((r, "open_ended"))
        if r.get("option_A") or r.get("option_B"):
            units.append((r, "answer_only"))
    for r in competition_rows:
        row = {"row_id": f"competition:{r['item_id']}",
               "type_id": f"competition_{r['condition']}", "type_num": 0,
               "family": "competition", "scenario_id": r["item_id"],
               "condition": r["condition"], "order": "NA",
               "stem": r["stem"], "option_A": r["option_A"],
               "option_B": r["option_B"], "expected_pick":
                   r.get("expected_pick", ""), "expected_response": ""}
        units.append((row, "open_ended"))
        units.append((row, "answer_only"))
    if smoke:
        scen_seen, keep = set(), []
        for r, arm in units:
            k = (r.get("family"), r.get("type_id"), r.get("scenario_id"))
            if len(scen_seen) < 4 or k in scen_seen:
                scen_seen.add(k)
                keep.append((r, arm))
        units = keep
    rng = random.Random(seed)
    rng.shuffle(units)
    if shard:
        i, n = (int(x) for x in shard.split("/"))
        units = units[i::n]
    return units


def prompt_key(row, arm):
    return f"{row['row_id']}:{arm}"


def needs_regeneration(generation: str, label_info, cap=MAX_NEW_TOKENS,
                       n_tokens=None):
    """Label-blocking cutoff: hit the token cap AND the label is uncertain
    (a truncated artifact can't be judged delivered-in-full)."""
    hit_cap = (n_tokens is not None and n_tokens >= cap)
    return bool(hit_cap and label_info and label_info.get("uncertain"))


def needs_stability(row, label_info):
    """Refusal rows where the auto label disagrees with the designed
    resolution or is uncertain (run_configuration sampling audit)."""
    if row.get("family") != "refusal" or not label_info:
        return False
    if label_info["uncertain"]:
        return True
    return not battery_labeler.matches_expected(
        label_info["label"], row.get("expected_response", ""))


# ---------------------------------------------------------------------------
# Pod-side main (torch/transformer_lens imports deferred)
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--frozen",
                    default="data/battery/frozen/battery_frozen_v1.jsonl")
    ap.add_argument("--freeze-manifest",
                    default="data/battery/frozen/freeze_manifest.json")
    ap.add_argument("--competition",
                    default="data/comparators/competition_battery_draft.jsonl")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--max-new-tokens", type=int, default=MAX_NEW_TOKENS)
    ap.add_argument("--smoke", action="store_true",
                    help="scenario-balanced 10–15 unit end-to-end shard")
    ap.add_argument("--shard", default=None, help="i/N deterministic split")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    frozen_path = Path(args.frozen)
    frozen_sha = verify_frozen(frozen_path, Path(args.freeze_manifest))
    comp_path = Path(args.competition)
    comp_sha, _ = rl.file_digest(comp_path)
    print(f"frozen sha OK {frozen_sha[:12]}…; competition sha "
          f"{comp_sha[:12]}… (post-fix per e61829f; 'draft' filename is "
          f"historical)")

    frozen_rows = [json.loads(l) for l in
                   frozen_path.read_text(encoding="utf-8").splitlines()
                   if l.strip()]
    comp_rows = [json.loads(l) for l in
                 comp_path.read_text(encoding="utf-8").splitlines()
                 if l.strip()]
    units = administered_rows(frozen_rows, comp_rows, smoke=args.smoke,
                              shard=args.shard, seed=args.seed)
    print(f"work list: {len(units)} administered prompts "
          f"({'smoke' if args.smoke else 'full'})")

    import torch
    from transformer_lens import HookedTransformer
    from src.pretest.run_pretest import MODEL_REGISTRY, templated, \
        verify_anchor
    if args.model not in MODEL_REGISTRY:
        print(f"RUN FAIL — {args.model!r} not in MODEL_REGISTRY")
        return 1
    spec = MODEL_REGISTRY[args.model]

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    csv_path = run_dir / "capture_rows.csv"
    act_path = run_dir / "activations.pt"
    labels_path = run_dir / "labels_auto.csv"
    done = set()
    activations = {}
    if csv_path.exists():   # resume
        done = {r["prompt_key"] for r in csv.DictReader(
            csv_path.open(encoding="utf-8", newline=""))}
        if act_path.exists():
            blob = torch.load(act_path, map_location="cpu",
                              weights_only=False)
            activations = blob["activations"]
        print(f"RESUME: {len(done)} prompts already captured")
    mode = "a" if done else "w"
    csv_f = open(csv_path, mode, newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_f, fieldnames=CAPTURE_FIELDS)
    if not done:
        writer.writeheader()
    lab_f = open(labels_path, mode, newline="", encoding="utf-8")
    lab_writer = csv.DictWriter(lab_f, fieldnames=LABEL_FIELDS)
    if not done:
        lab_writer.writeheader()
    # Every administered user message, verbatim, for template sign-off and
    # provenance (capture_rows.csv carries only the prompt sha). The chat
    # template wraps this per MODEL_REGISTRY; the anchor suffix is asserted.
    prompts_txt = open(run_dir / "rendered_prompts.txt", mode,
                       encoding="utf-8", newline="\n")

    dtype = getattr(torch, args.dtype)
    model = HookedTransformer.from_pretrained(args.model,
                                              device=args.device,
                                              dtype=dtype)
    tokenizer = model.tokenizer
    anchor_samples = []

    def token_variants(letter):
        out = set()
        for s in (letter, " " + letter):
            ids = tokenizer.encode(s, add_special_tokens=False)
            if len(ids) == 1:
                out.add(ids[0])
        return sorted(out)

    a_ids, b_ids = token_variants("A"), token_variants("B")

    def checkpoint(partial=True):
        rl.atomic_write(act_path, lambda f: torch.save(
            {"activations": activations, "partial": partial,
             "n_layers": model.cfg.n_layers,
             "d_model": model.cfg.d_model}, f))

    label_rows, capture_meta = [], {}
    identity_checked = set()
    with torch.no_grad():
        for i, (row, arm) in enumerate(units, 1):
            key = prompt_key(row, arm)
            if key in done:
                continue
            user_msg = render_prompt(row, arm)
            prompts_txt.write(f"=== {key}\n{user_msg}\n\n")
            prompts_txt.flush()
            prompt_str = templated(tokenizer, user_msg)
            ids = verify_anchor(tokenizer, prompt_str,
                                spec["anchor_expect_decoded_suffix"],
                                anchor_samples)
            batch = ids.unsqueeze(0).to(args.device)
            logits, cache = model.run_with_cache(
                batch, return_type="logits",
                names_filter=lambda n: n.endswith("hook_resid_post"))
            anchor = torch.stack(
                [cache[f"blocks.{l}.hook_resid_post"][0, -1]
                 for l in range(model.cfg.n_layers)]).to(torch.float16).cpu()
            if arm not in identity_checked:   # invariant #2 spot check
                _, cache2 = model.run_with_cache(
                    batch, return_type=None,
                    names_filter=lambda n: n.endswith("hook_resid_post"))
                anchor2 = torch.stack(
                    [cache2[f"blocks.{l}.hook_resid_post"][0, -1]
                     for l in range(model.cfg.n_layers)]
                ).to(torch.float16).cpu()
                assert torch.equal(anchor, anchor2), \
                    "anchor not bitwise-identical across rollouts — " \
                    "pipeline broken (CLAUDE.md invariant #2); do not patch " \
                    "this assertion"
                identity_checked.add(arm)
            activations[key] = anchor
            probs = torch.softmax(logits[0, -1].float(), dim=-1)
            entropy = float(-(probs * (probs + 1e-12).log()).sum())
            p_a = p_b = ""
            if arm == "answer_only":
                p_a = f"{sum(float(probs[t]) for t in a_ids):.6f}"
                p_b = f"{sum(float(probs[t]) for t in b_ids):.6f}"
            gen_budget = (4 if arm == "answer_only"
                          else args.max_new_tokens)
            out = model.generate(batch, max_new_tokens=gen_budget,
                                 do_sample=False, verbose=False)
            gen_ids = out[0, ids.shape[0]:]
            generation = tokenizer.decode(gen_ids, skip_special_tokens=True)

            label_info = None
            if row.get("family") == "refusal" and arm == "open_ended":
                label_info = battery_labeler.prelabel_response(generation)
                if needs_regeneration(generation, label_info,
                                      cap=gen_budget,
                                      n_tokens=len(gen_ids)):
                    out = model.generate(batch, max_new_tokens=REGEN_TOKENS,
                                         do_sample=False, verbose=False)
                    gen_ids = out[0, ids.shape[0]:]
                    generation = tokenizer.decode(gen_ids,
                                                  skip_special_tokens=True)
                    label_info = battery_labeler.prelabel_response(generation)
                    label_info["regenerated"] = True
                lab_writer.writerow({
                    "row_id": row["row_id"], "prompt_key": key,
                    "label": label_info["label"],
                    "uncertain": int(label_info["uncertain"]),
                    "disclaimer_reluctance":
                        label_info["disclaimer_reluctance"],
                    "basis": label_info["basis"],
                    "regenerated": int(bool(label_info.get("regenerated")))})
                lab_f.flush()
                label_rows.append((row, key, label_info))

            writer.writerow({
                "prompt_key": key, "row_id": row["row_id"],
                "type_id": row.get("type_id", ""),
                "type_num": row.get("type_num", ""),
                "family": row.get("family", ""),
                "scenario_id": row.get("scenario_id", ""),
                "condition": row.get("condition", ""),
                "order": row.get("order", ""), "arm": arm,
                "expected_pick": row.get("expected_pick", ""),
                "expected_response": row.get("expected_response", ""),
                "prompt_sha256":
                    hashlib.sha256(prompt_str.encode()).hexdigest(),
                "entropy": f"{entropy:.6f}", "p_A": p_a, "p_B": p_b,
                "generation": generation})
            csv_f.flush()
            if i % CHECKPOINT_EVERY == 0:
                checkpoint(partial=True)
                print(f"  [{i}/{len(units)}] captured (checkpoint)")

        # stability shard: disputed refusal labels, 5 samples, temp 0.7
        stab_path = run_dir / "stability_shard.csv"
        with open(stab_path, "w", newline="", encoding="utf-8") as sf:
            sw = csv.DictWriter(sf, fieldnames=["row_id", "seed",
                                                "generation", "label",
                                                "uncertain"])
            sw.writeheader()
            targets = [(r, k) for r, k, li in label_rows
                       if needs_stability(r, li)]
            print(f"stability shard: {len(targets)} disputed refusal rows")
            for row, key in targets:
                user_msg = render_prompt(row, "open_ended")
                prompt_str = templated(tokenizer, user_msg)
                ids = verify_anchor(tokenizer, prompt_str,
                                    spec["anchor_expect_decoded_suffix"],
                                    anchor_samples)
                batch = ids.unsqueeze(0).to(args.device)
                for s in range(STABILITY_SAMPLES):
                    torch.manual_seed(s)
                    out = model.generate(batch,
                                         max_new_tokens=args.max_new_tokens,
                                         do_sample=True,
                                         temperature=STABILITY_TEMP,
                                         verbose=False)
                    g = tokenizer.decode(out[0, ids.shape[0]:],
                                         skip_special_tokens=True)
                    li = battery_labeler.prelabel_response(g)
                    sw.writerow({"row_id": row["row_id"], "seed": s,
                                 "generation": g, "label": li["label"],
                                 "uncertain": int(li["uncertain"])})
                    sf.flush()

    csv_f.close()
    lab_f.close()
    prompts_txt.close()
    checkpoint(partial=False)

    digests = {}
    for p in (csv_path, labels_path, run_dir / "stability_shard.csv",
              run_dir / "rendered_prompts.txt", act_path):
        if p.exists():
            sha, size = rl.file_digest(p)
            digests[p.name] = {"sha256": sha, "bytes": size}
            print(f"DIGEST {sha} {size} {p.name}")
    manifest = {
        "run_role": "battery_session", "produced_by": PRODUCED_BY,
        "model": args.model, "seed": args.seed,
        "greedy": True, "max_new_tokens": args.max_new_tokens,
        "regen_tokens": REGEN_TOKENS,
        "smoke": args.smoke, "shard": args.shard,
        "frozen_file": str(frozen_path), "frozen_sha256": frozen_sha,
        "competition_file": str(comp_path),
        "competition_sha256": comp_sha,
        "competition_provenance": "post-fix version (hazard easy items "
                                  "replaced, aquarium reworded; commit "
                                  "e61829f) — 'draft' filename is "
                                  "historical",
        "prompt_template": {
            "stimulus_order": "stem, shared_opposition_text, "
                              "condition_insert (verbatim, \\n\\n-joined)",
            "options_block": "A: {option_A}\\nB: {option_B}",
            "answer_only_instruction": ANSWER_ONLY_INSTRUCTION,
            "sign_off": "REQUIRED before the real run (module header)"},
        "p_ab_method": {"A_token_ids": a_ids, "B_token_ids": b_ids,
                        "rule": "sum of single-token encodings of 'A'/' A' "
                                "(resp. B) in the anchor's next-token "
                                "distribution"},
        "labeler": "src/battery/labeler.py (rubric v1.3 §9); labels "
                   "digest-locked at run time via labels_auto.csv digest",
        "anchor_samples": anchor_samples[:5],
        "n_units": len(units),
        "timestamp_utc": datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds"),
        "output_digests": digests,
    }
    rl.atomic_write(run_dir / "manifest.json",
                    lambda f: f.write(json.dumps(manifest, indent=2) + "\n"),
                    mode="w", encoding="utf-8", newline="\n")
    sha, size = rl.file_digest(run_dir / "manifest.json")
    print(f"DIGEST {sha} {size} manifest.json")
    print(f"BATTERY {'SMOKE ' if args.smoke else ''}RUN COMPLETE — "
          f"{len(units)} prompts. Next: scripts/verify_run.py, mirror, "
          f"commit, STOP the pod.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
