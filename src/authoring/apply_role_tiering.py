#!/usr/bin/env python3
"""
apply_role_tiering.py — apply the tiered run-all role design to committed tranche files.

Design (researcher-ratified 2026-07-09):
  - Base role sets are UNTOUCHED (they came from authored/curated content; the pull and
    gradient estimates use ONLY these cells, frozen pre-run).
  - Each menu role NOT in the base set carries an exclusion code (its pre-registered
    predicted defect signature). Those codes decide whether the cell is additionally RUN
    as a validation cell:
      value-switch, severity-shift  -> ALWAYS run (the arguable exclusions worth testing)
      implausible                    -> run a deterministic ~1/3 sample
      incoherent                     -> never run (definitional; degenerate output)
  - Content-hard-exclusions (self-directed harm) are never run, recorded separately.

Output fields added per role-carrying probe:
  role_included_base : list  — frozen; pull/gradient estimates use ONLY these
  role_predictions   : {role: code} — validation cells actually rendered + expected signature
  role_skipped       : {role: reason} — not rendered (incoherent / implausible-not-sampled / hard)
  role_set           : rewritten to base + rendered validation cells (what the runner renders)
Original role_exclusions is removed (superseded by the three fields above).

Idempotent: refuses to run if role_included_base already present (already tiered).
Usage: python apply_role_tiering.py f1.json [f2.json ...]
"""
import json, hashlib, sys

MENU = ["self", "friend", "sibling", "coworker", "boss", "stranger"]
RENDER_ALWAYS = {"value-switch", "severity-shift"}
HARD = {("PT2-harm_avoidance-R2", "self"),
        ("PT2-harm_avoidance-R3", "self"),
        ("PT2-harm_avoidance-R5", "self")}


def sampled(pid, role):  # deterministic ~1/3
    return int(hashlib.sha256(f"{pid}:{role}".encode()).hexdigest(), 16) % 3 == 0


def tier_probe(it):
    base = list(it["role_set"])                 # UNTOUCHED authored base
    codes = dict(it.get("role_exclusions", {})) # predicted signatures for excluded roles
    run, skip, preds = set(base), {}, {}
    for r in MENU:
        if r in base:
            continue
        if (it["id"], r) in HARD:
            skip[r] = "content-hard-exclusion (self-directed harm); not generated"
            continue
        code = codes.get(r)
        if code is None:
            # menu role neither in base nor coded — coverage gap; skip and note (validator will catch upstream)
            skip[r] = "uncoded (coverage gap — check freezer validator)"
        elif code == "incoherent":
            skip[r] = "incoherent (definitional; not rendered)"
        elif code in RENDER_ALWAYS:
            run.add(r); preds[r] = code
        elif code == "implausible":
            if sampled(it["id"], r):
                run.add(r); preds[r] = "implausible"
            else:
                skip[r] = "implausible (not in validation sample)"
        else:
            run.add(r); preds[r] = code
    it["role_included_base"] = [r for r in MENU if r in base]
    it["role_set"] = [r for r in MENU if r in run]
    it["role_predictions"] = preds
    it["role_skipped"] = skip
    it.pop("role_exclusions", None)


def probes_of(d):
    if "choice" in d:      return [it for v in d["choice"].values() for it in v]
    if "resistance" in d:  return [it for v in d["resistance"].values() for it in v]
    if "null_comparison" in d: return list(d["null_comparison"])
    return []


POLICY = ("TIERED run-all (researcher-ratified 2026-07-09). role_included_base = authored/curated roles; "
          "pull and gradient estimates use ONLY these, frozen pre-run. Additionally rendered as pre-registered "
          "VALIDATION cells: all value-switch & severity-shift predictions + a deterministic ~1/3 sample of "
          "implausible; role_predictions records each rendered validation cell's expected defect signature. NOT "
          "rendered: incoherent (definitional) and content-hard-exclusions. role_set = base + rendered validation "
          "(what the runner renders). IV run is non-gating; validation cells never enter pull estimates.")


def main(paths):
    from collections import Counter
    stats = Counter()
    for path in paths:
        d = json.loads(open(path).read())
        probes = probes_of(d)
        for it in probes:
            if "role_set" not in it:
                continue
            if "role_included_base" in it:
                sys.exit(f"{path}: already tiered (role_included_base present) — aborting to stay idempotent.")
            tier_probe(it)
            stats["base"] += len(it["role_included_base"])
            stats["validation"] += len(it["role_predictions"])
            for c in it["role_predictions"].values():
                stats[f"pred:{c}"] += 1
        d["_meta"]["role_policy"] = POLICY
        open(path, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
        print(f"tiered: {path} ({len(probes)} probes)")
    print("\nrole-cell totals:", dict(stats))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: apply_role_tiering.py f1.json [f2.json ...]")
    main(sys.argv[1:])
