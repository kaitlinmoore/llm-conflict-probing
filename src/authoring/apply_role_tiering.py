#!/usr/bin/env python3
"""
apply_role_tiering.py (v2) — apply the tiered run-all role design to tranche files.

Design (researcher-ratified 2026-07-15; rendering-scope rule ratified 2026-07-15):
  - Base role sets are UNTOUCHED (authored/curated content; pull and gradient estimates
    use ONLY these cells, frozen pre-run) — with one ratified exception below.
  - Each menu role NOT in the base set carries an exclusion code (its pre-registered
    predicted defect signature). Those codes decide whether the cell is additionally RUN
    as a validation cell:
      value-switch, severity-shift  -> run (the arguable exclusions worth testing),
                                       EXCEPT self (see rendering-scope rule)
      implausible                    -> run a deterministic ~1/3 sample
      incoherent                     -> never run (definitional; degenerate output)
  - Content-hard-exclusions (self-directed harm) are never run, recorded separately.

RENDERING-SCOPE RULE (spec §3a; ratified 2026-07-15): a value-switch validation cell is
rendered only where it is renderable AND empirically live.
  * SELF value-switch cells are ALWAYS SKIPPED: self-directed kindness/harm-avoidance/
    privacy etc. switches the value definitionally (self-talk / self-harm territory), so
    "does self switch the value?" is not a live prediction, and many such cells are also
    grammatically unrenderable (self_template cannot cover multi-field choice prompts).
  * STRANGER value-switch cells on relational values (loyalty, care) are KEPT: renderable
    and a live prediction — they test the closeness-gradient endpoint (does the pull
    actually vanish toward a stranger?).
  * Ratified base-set exception: SELF may not sit in the BASE set of kindness or
    harm_avoidance probes (definitional value-switch; a residue the authored sets missed
    on PT2-harm_avoidance-C4). Such cells are removed from base and recorded in
    role_skipped. This is the only circumstance in which this script modifies a base set.

Output fields per role-carrying probe:
  role_included_base : list  — frozen; pull/gradient estimates use ONLY these
  role_predictions   : {role: code} — validation cells actually rendered + expected signature
  role_skipped       : {role: reason} — not rendered; reason begins with its machine-readable code
  role_set           : base + rendered validation cells (what the runner renders)

Idempotent by reconstruction: already-tiered probes are un-tiered back to (base, codes)
— skipped reasons carry their code as the first token — and re-tiered under current rules,
so the script can re-run on committed tiered files and converges to a fixed point
(a second run produces byte-identical output). Original role_exclusions is superseded.

Usage: python apply_role_tiering.py f1.json [f2.json ...]
"""
import json, hashlib, sys

MENU = ["self", "friend", "sibling", "coworker", "boss", "stranger"]
RENDER_ALWAYS = {"value-switch", "severity-shift"}
KNOWN_CODES = {"value-switch", "severity-shift", "implausible", "incoherent"}
HARD = {("PT2-harm_avoidance-R2", "self"),
        ("PT2-harm_avoidance-R3", "self"),
        ("PT2-harm_avoidance-R5", "self")}
# Ratified 2026-07-15: self is a definitional value-switch on these values and may not
# appear in a base set (see docstring).
SELF_FORBIDDEN_BASE_VALUES = {"kindness", "harm_avoidance"}

SELF_VS_SKIP_REASON = ("value-switch (self; skipped per spec §3a rendering-scope rule — "
                       "definitional and/or unrenderable, not a live prediction)")
BASE_RESIDUE_REASON = ("value-switch (self; removed from base per spec §3a — definitional "
                       "value-switch on this value, ratified 2026-07-15)")


def sampled(pid, role):  # deterministic ~1/3
    return int(hashlib.sha256(f"{pid}:{role}".encode()).hexdigest(), 16) % 3 == 0


def reason_code(reason):
    """First token of a skip reason is its machine-readable code."""
    head = reason.split(" ")[0].rstrip(";:,")
    return head if head in KNOWN_CODES else None


def untier_probe(it):
    """Recover (base, codes, prior skip reasons) from a tiered probe."""
    base = list(it["role_included_base"])
    codes = dict(it.get("role_predictions", {}))
    prior = dict(it.get("role_skipped", {}))
    for role, reason in prior.items():
        c = reason_code(reason)
        if c:
            codes[role] = c
    return base, codes, prior


def tier_probe(it, value):
    if "role_included_base" in it:
        base, codes, prior = untier_probe(it)
    else:
        base = list(it["role_set"])
        codes = dict(it.get("role_exclusions", {}))
        prior = {}

    run, skip, preds = set(), {}, {}

    # Ratified base exception: self may not be base on kindness/harm_avoidance.
    if "self" in base and value in SELF_FORBIDDEN_BASE_VALUES:
        base = [r for r in base if r != "self"]
        skip["self"] = BASE_RESIDUE_REASON
    run |= set(base)

    for r in MENU:
        if r in base or r in skip:
            continue
        if (it["id"], r) in HARD:
            skip[r] = "content-hard-exclusion (self-directed harm); not generated"
            continue
        code = codes.get(r)
        if code is None:
            skip[r] = "uncoded (coverage gap — check freezer validator)"
        elif code == "incoherent":
            skip[r] = "incoherent (definitional; not rendered)"
        elif code == "value-switch" and r == "self":
            skip[r] = prior.get(r, SELF_VS_SKIP_REASON)  # rendering-scope rule; keep provenance
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
    if "choice" in d:      return [(v, it) for v, l in d["choice"].items() for it in l]
    if "resistance" in d:  return [(v, it) for v, l in d["resistance"].items() for it in l]
    if "null_comparison" in d: return [(it.get("value", "?"), it) for it in d["null_comparison"]]
    return []


POLICY = ("TIERED run-all v2 (tiering ratified 2026-07-15; rendering-scope rule ratified 2026-07-15). "
          "role_included_base = authored/curated roles; pull and gradient estimates use ONLY these, frozen "
          "pre-run (single ratified exception: self removed from kindness/harm_avoidance base sets — "
          "definitional value-switch). Additionally rendered as pre-registered VALIDATION cells: all "
          "severity-shift predictions, non-self value-switch predictions (e.g. stranger on relational values, "
          "which tests the closeness-gradient endpoint), and a deterministic ~1/3 sample of implausible; "
          "role_predictions records each rendered validation cell's expected defect signature. NOT rendered: "
          "self value-switch cells (definitional and/or unrenderable — spec §3a rendering-scope rule), "
          "incoherent (definitional), and content-hard-exclusions. role_set = base + rendered validation "
          "(what the runner renders). IV run is non-gating; validation cells never enter pull estimates.")


def main(paths):
    from collections import Counter
    stats = Counter()
    for path in paths:
        d = json.loads(open(path).read())
        probes = probes_of(d)
        n = 0
        for value, it in probes:
            if "role_set" not in it:
                continue
            tier_probe(it, value)
            n += 1
            stats["base"] += len(it["role_included_base"])
            stats["validation"] += len(it["role_predictions"])
            for c in it["role_predictions"].values():
                stats[f"pred:{c}"] += 1
            for reason in it["role_skipped"].values():
                stats[f"skip:{(reason_code(reason) or reason.split(' ')[0])}"] += 1
        d["_meta"]["role_policy"] = POLICY
        open(path, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
        print(f"tiered: {path} ({n} role-carrying probes)")
    print("\nrole-cell totals:", dict(stats))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: apply_role_tiering.py f1.json [f2.json ...]")
    main(sys.argv[1:])
