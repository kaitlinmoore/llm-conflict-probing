#!/usr/bin/env python3
"""
validate_battery.py — scripted validation gate for battery draft files
(data/battery/drafts/<type_id>.jsonl, schema battery_draft_v1 — see
data/battery/battery_schema.md). Runs during authoring so defects surface
while the author is still in the file, not after.

Checks (task spec 2026-07-30, session 1):
  a. Lexeme blocklists (data/battery/lexeme_blocklists.json): whole-word,
     case-insensitive, over the stimulus fields (stem, option_A, option_B,
     shared_opposition_text, condition_insert) of every cell. BLOCKING.
     **Scope is GLOBAL** (researcher, 2026-07-31): every type is checked
     against the `global` list AND all nine ratified per-value lists, not
     only its own poles. Rationale on record: third-value lexemes are held
     to the same standard as third-value pressure (authoring rules 1 and 6);
     the workbook READMEs already said prior lists "apply globally" — own-
     pole scoping was this validator's interpretation, never a ratified
     decision. The `discipline_only` section stays unenforced everywhere.
     Per-instance exemptions (data/battery/blocklist_exemptions.json)
     downgrade a single documented hit to informational; they are always
     printed in the report and never silently suppress. A rostered value
     with an empty/pending list is a researcher-decision flag, non-blocking.
  b. Shared-text verbatim: within each scenario, the two oppose_tip_* cells'
     shared_opposition_text must be byte-identical. BLOCKING. Nonempty
     shared text on agree_* cells is a WARNING (schema says empty there).
  c. Stem-consistency: stem byte-identical across all 4 cells. BLOCKING.
  d. Structural completeness: exactly 4 cells per scenario, labels exactly
     {agree_A, agree_B, oppose_tip_A, oppose_tip_B}; options nonempty and
     non-duplicate; expected_pick in {A, B}. BLOCKING.
  e. Length report: per-cell condition_insert token counts; any cell
     > 1.5x its scenario's median insert length is flagged. NON-BLOCKING.
     Token counts are whitespace-split tokens (documented proxy — the model
     tokenizer is not loadable off-pod; the 1.5x ratio criterion is
     insensitive to the proxy choice at these lengths).

Exit nonzero on any blocking failure. Full report to stdout AND
docs/battery_validation_report.md (atomic write; DIGEST line printed).

Usage:
  python src/battery/validate_battery.py [drafts...] \
      [--blocklists data/battery/lexeme_blocklists.json] \
      [--report docs/battery_validation_report.md]
  (default drafts: data/battery/drafts/*.jsonl)
"""

import argparse
import datetime
import json
import re
import statistics
import sys
from pathlib import Path

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:  # running as a plain script from src/battery/
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    from runner_lib import atomic_write, file_digest

PRODUCED_BY = "Claude Fable 5 (model id claude-fable-5)"

# Family-specific condition sets (D45). Choice cells resolve to an option;
# refusal cells resolve to a response channel and carry no options.
CHOICE_CONDITIONS = {"agree_A", "agree_B", "oppose_tip_A", "oppose_tip_B"}
REFUSAL_CONDITIONS = {"agree_comply", "agree_refuse",
                      "oppose_tip_comply", "oppose_tip_refuse"}
CONDITIONS = CHOICE_CONDITIONS          # back-compat alias
CHOICE_OPPOSE = ("oppose_tip_A", "oppose_tip_B")
REFUSAL_OPPOSE = ("oppose_tip_comply", "oppose_tip_refuse")
EXPECTED_RESPONSES = {"comply", "refuse", "hedge"}
STIMULUS_FIELDS = ("stem", "option_A", "option_B",
                   "shared_opposition_text", "condition_insert")
LENGTH_FLAG_RATIO = 1.5

# Cross-type character-name uniqueness (backlog item 1). Capitalized tokens
# that are not names: sentence openers and domain proper nouns would swamp the
# signal, so only tokens appearing mid-sentence are considered, minus this
# stoplist. Non-blocking by design — reuse is a design smell, not an error.
NAME_STOPWORDS = {
    "I", "I'm", "I've", "I'd", "I'll", "A", "An", "The", "This", "That",
    "These", "Those", "He", "She", "They", "We", "You", "It", "My", "His",
    "Her", "Their", "Our", "Your", "Its", "But", "And", "Or", "So", "If",
    "When", "While", "After", "Before", "Then", "Now", "Option", "Both",
    "Neither", "Either", "One", "Two", "Three", "Four", "Five", "Six",
    "Seven", "Eight", "Nine", "Ten", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday", "January", "February",
    "March", "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "Dr", "Mr", "Mrs", "Ms", "St",
}
NAME_RE = re.compile(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]{2,})\b")


def load_blocklists(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    compiled = {}
    for scope, lexemes in [("global", data.get("global", []))] + \
            sorted(data.get("per_value", {}).items()):
        compiled[scope] = [(lx, re.compile(rf"\b{re.escape(lx)}\b", re.IGNORECASE))
                           for lx in lexemes]
    return data, compiled


def load_exemptions(path: Path):
    """Per-instance blocklist exemptions (researcher-granted).

    Each record: cell (type_id:scenario_id:condition — `*` allowed in the
    condition slot, since a stem hit appears in all four cells of a
    scenario), lexeme, rationale, date, granted_by; `field` optional.
    Returns (records, matched_counter) where the counter is filled during
    validation so stale exemptions can be reported."""
    if not path.exists():
        return [], {}
    data = json.loads(path.read_text(encoding="utf-8"))
    recs = data.get("exemptions", [])
    return recs, {i: 0 for i in range(len(recs))}


def exemption_for(exemptions, matched, cell_id, field, lexeme):
    """Index of the exemption covering this hit, or None. Records a match."""
    for i, ex in enumerate(exemptions):
        if ex.get("lexeme", "").lower() != lexeme.lower():
            continue
        if ex.get("field") and ex["field"] != field:
            continue
        want = ex.get("cell", "")
        if want == cell_id:
            matched[i] = matched.get(i, 0) + 1
            return i
        # wildcard condition slot: type_id:scenario_id:*
        if want.endswith(":*") and cell_id.startswith(want[:-1]):
            matched[i] = matched.get(i, 0) + 1
            return i
    return None


def check_lexemes(rec, fields, blockcompiled, exemptions, matched, f,
                  cell_id):
    """Global-scope lexeme check for one record over the given fields."""
    for field in fields:
        text = rec.get(field, "") or ""
        if not text:
            continue
        for scope, pats in blockcompiled.items():
            for lexeme, pattern in pats:
                if not pattern.search(text):
                    continue
                own = scope == "global" or scope in (rec.get("type_values") or [])
                idx = exemption_for(exemptions, matched, cell_id, field, lexeme)
                detail = (f"blocked lexeme {lexeme!r} (list: {scope}"
                          f"{'' if own else ', cross-type'})")
                if idx is None:
                    f.block("a.lexeme", f"{cell_id}:{field}", detail)
                else:
                    ex = exemptions[idx]
                    f.exempted.append(
                        f"{cell_id}:{field} — {detail} — EXEMPT "
                        f"({ex.get('date', 'no date')}, "
                        f"{ex.get('granted_by', 'unattributed')}): "
                        f"{ex.get('rationale', 'no rationale recorded')}")


def token_count(text: str) -> int:
    """Whitespace tokens — documented proxy for model tokens (see module doc)."""
    return len(text.split())


class Findings:
    def __init__(self):
        self.blocking = []   # (check, location, detail)
        self.warnings = []
        self.researcher_flags = []
        self.length_flags = []
        self.name_flags = []
        self.exempted = []          # documented per-instance exemptions applied
        self.lines = []      # report body lines

    def block(self, check, loc, detail):
        self.blocking.append((check, loc, detail))

    def warn(self, check, loc, detail):
        self.warnings.append((check, loc, detail))


CONTROL_STIMULUS_FIELDS = ("stem", "option_A", "option_B")


def validate_controls(path, records, blockdata, blockcompiled, f,
                      exemptions, matched):
    """topical_control records: id uniqueness, option sanity, leakage via
    global + the type's value lists (schema doc, researcher 2026-07-30).
    No 4-cell structure / stem / shared-text / length checks — different
    item class."""
    f.lines.append(f"### `{path.name}` — {len(records)} topical controls")
    f.lines.append("")
    seen_ids = set()
    for rec in records:
        cid = rec.get("control_id", "")
        loc = f"{path.name}:{cid or '<no id>'}"
        if not cid:
            f.block("d.structure", loc, "empty control_id")
        elif cid in seen_ids:
            f.block("d.structure", loc, "duplicate control_id")
        seen_ids.add(cid)
        if not (rec.get("stem", "") or "").strip():
            f.block("d.structure", loc, "stem empty")
        # Choice-family controls are two-option items; refusal-family controls
        # are single assistance asks with no options at all (T8/T9/T10).
        if rec.get("family") == "choice":
            if not rec.get("option_A", ""):
                f.block("d.structure", loc, "option_A empty")
            if not rec.get("option_B", ""):
                f.block("d.structure", loc, "option_B empty")
            if rec.get("option_A") and rec.get("option_A") == rec.get("option_B"):
                f.block("d.structure", loc,
                        "option_A == option_B (duplicate options)")
        elif rec.get("option_A") or rec.get("option_B"):
            f.block("d.structure", loc,
                    "refusal-family control carries option text")
        check_lexemes(rec, CONTROL_STIMULUS_FIELDS, blockcompiled, exemptions,
                      matched, f, f"{rec.get('type_id')}:{cid}")


def validate_file(path: Path, blockdata, blockcompiled, f: Findings,
                  exemptions, matched):
    records = [json.loads(l) for l in
               path.read_text(encoding="utf-8").splitlines() if l.strip()]
    controls = [r for r in records
                if r.get("record_type") == "topical_control"]
    records = [r for r in records
               if r.get("record_type", "battery_cell") == "battery_cell"]
    if controls:
        validate_controls(path, controls, blockdata, blockcompiled, f,
                          exemptions, matched)
    if not records:
        return len(controls), []
    family = records[0].get("family", "choice")
    conditions = REFUSAL_CONDITIONS if family == "refusal" else CHOICE_CONDITIONS
    oppose = REFUSAL_OPPOSE if family == "refusal" else CHOICE_OPPOSE
    f.lines.append(f"### `{path.name}` — {len(records)} cells ({family} family)")
    f.lines.append("")

    # -- d. structure: uniqueness, grouping, per-cell fields ----------------
    by_scenario = {}
    seen_keys = set()
    for rec in records:
        sid, cond = rec.get("scenario_id", ""), rec.get("condition", "")
        loc = f"{path.name}:{sid}:{cond}"
        if not sid:
            f.block("d.structure", loc, "empty scenario_id")
        if cond not in conditions:
            f.block("d.structure", loc,
                    f"condition {cond!r} not in {sorted(conditions)}")
        if rec.get("family", "choice") != family:
            f.block("d.structure", loc,
                    f"mixed families in one file ({rec.get('family')!r} vs {family!r})")
        key = (sid, cond)
        if key in seen_keys:
            f.block("d.structure", loc, "duplicate (scenario_id, condition)")
        seen_keys.add(key)
        by_scenario.setdefault(sid, []).append(rec)

        if family == "choice":
            # options-uniformity applies to the choice family only
            if not rec.get("option_A", ""):
                f.block("d.structure", loc, "option_A empty")
            if not rec.get("option_B", ""):
                f.block("d.structure", loc, "option_B empty")
            if rec.get("option_A") and rec.get("option_A") == rec.get("option_B"):
                f.block("d.structure", loc,
                        "option_A == option_B (duplicate options)")
            if rec.get("expected_pick") not in ("A", "B"):
                f.block("d.structure", loc,
                        f"expected_pick {rec.get('expected_pick')!r} not in {{A, B}}")
        else:
            if rec.get("option_A") or rec.get("option_B"):
                f.block("d.structure", loc,
                        "refusal-family cell carries option text")
            er = rec.get("expected_response")
            if er not in EXPECTED_RESPONSES:
                f.block("d.structure", loc,
                        f"expected_response {er!r} not in "
                        f"{sorted(EXPECTED_RESPONSES)}")

    for sid, cells in sorted(by_scenario.items()):
        conds = sorted(c.get("condition", "") for c in cells)
        if set(conds) != conditions or len(conds) != 4:
            f.block("d.structure", f"{path.name}:{sid}",
                    f"expected exactly 4 cells {sorted(conditions)}, got {conds}")

    # -- c. stem consistency ------------------------------------------------
    for sid, cells in sorted(by_scenario.items()):
        stems = {c.get("stem", "") for c in cells}
        if len(stems) > 1:
            f.block("c.stem", f"{path.name}:{sid}",
                    f"{len(stems)} distinct stems across the scenario's cells")

    # -- b. shared opposition text ------------------------------------------
    for sid, cells in sorted(by_scenario.items()):
        opp = {c["condition"]: c.get("shared_opposition_text", "")
               for c in cells if c.get("condition") in oppose}
        if len(opp) == 2 and opp[oppose[0]] != opp[oppose[1]]:
            f.block("b.shared_text", f"{path.name}:{sid}",
                    f"{oppose[0]} vs {oppose[1]} shared_opposition_text differ "
                    "(byte comparison)")
        for c in cells:
            if (c.get("condition", "").startswith("agree")
                    and c.get("shared_opposition_text", "")):
                f.warn("b.shared_text", f"{path.name}:{sid}:{c['condition']}",
                       "nonempty shared_opposition_text on an agreement cell")

    # -- a. lexeme blocklists -----------------------------------------------
    # Scope = global + the type's own two poles (from type_values, which is
    # reliable where option-header suffixes are not). The READMEs also say
    # "prior lists apply globally"; that stricter cross-type reading is
    # computed separately as a non-blocking tier — see cross_type_lexemes().
    pending = blockdata.get("pending_researcher", {})
    values_seen = set()
    for rec in records:
        tvals = rec.get("type_values") or [rec.get("value_A", ""),
                                           rec.get("value_B", "")]
        values_seen.update(tvals)
        cell_id = (f"{rec.get('type_id')}:{rec.get('scenario_id')}:"
                   f"{rec.get('condition')}")
        check_lexemes(rec, STIMULUS_FIELDS, blockcompiled, exemptions,
                      matched, f, cell_id)
    for v in sorted(values_seen - {""}):
        if v not in blockcompiled:
            f.researcher_flags.append(
                f"value {v!r} appears in drafts but has no entry in "
                f"lexeme_blocklists.json per_value — add a list (may be empty "
                f"by decision)")
        elif not blockcompiled[v]:
            note = pending.get(v, "empty list")
            f.researcher_flags.append(
                f"value {v!r} blocklist is empty/pending: {note}")

    # -- e. length report (non-blocking) ------------------------------------
    f.lines.append("| scenario | cell | insert tokens | scenario median | flag |")
    f.lines.append("|---|---|---|---|---|")
    for sid, cells in sorted(by_scenario.items()):
        counts = {c["condition"]: token_count(c.get("condition_insert", "") or "")
                  for c in cells}
        med = statistics.median(counts.values()) if counts else 0
        for cond in sorted(counts):
            n = counts[cond]
            flagged = med > 0 and n > LENGTH_FLAG_RATIO * med
            if flagged:
                f.length_flags.append(
                    f"{path.name}:{sid}:{cond} insert {n} tokens "
                    f"> {LENGTH_FLAG_RATIO}x scenario median {med:g}")
            f.lines.append(f"| {sid} | {cond} | {n} | {med:g} | "
                           f"{'FLAG' if flagged else ''} |")
    f.lines.append("")
    return len(records), sorted(by_scenario)


def extract_names(records):
    """{name: {(type_id, scenario_id)}} over stimulus text. Heuristic: a
    mid-sentence capitalized word that isn't a stoplisted function word or
    calendar term. Over-collects domain proper nouns (place names); that is
    why the check is non-blocking."""
    found = {}
    for rec in records:
        for field in STIMULUS_FIELDS:
            for m in NAME_RE.finditer(rec.get(field, "") or ""):
                tok = m.group(1)
                if tok in NAME_STOPWORDS:
                    continue
                found.setdefault(tok, set()).add(
                    (rec.get("type_id", "?"), rec.get("scenario_id", "?")))
    return found


def cross_type_name_check(all_records, f):
    """Backlog item 1: the same character name in more than one type. Reuse
    risks cross-item association during administration and muddies per-type
    similarity readings. WARNING only."""
    names = extract_names(all_records)
    for name, where in sorted(names.items()):
        types = sorted({t for t, _ in where})
        if len(types) > 1:
            f.name_flags.append(
                f"{name!r} appears in {len(types)} types: "
                + ", ".join(f"{t}({sum(1 for tt, _ in where if tt == t)} cells)"
                            for t in types))
    # near-collisions: same first 4 letters, different names, different types
    keys = sorted(names)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a[:4].lower() == b[:4].lower() and a != b:
                ta = {t for t, _ in names[a]}
                tb = {t for t, _ in names[b]}
                if ta != tb or len(ta | tb) > 1:
                    f.name_flags.append(
                        f"near-collision {a!r} ({', '.join(sorted(ta))}) vs "
                        f"{b!r} ({', '.join(sorted(tb))})")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts", nargs="*", help="draft jsonl paths "
                    "(default: data/battery/drafts/*.jsonl)")
    ap.add_argument("--blocklists", default="data/battery/lexeme_blocklists.json")
    ap.add_argument("--exemptions",
                    default="data/battery/blocklist_exemptions.json",
                    help="documented per-instance blocklist exemptions; "
                         "always reported, never silent")
    ap.add_argument("--report", default="docs/battery_validation_report.md")
    args = ap.parse_args(argv)

    paths = ([Path(p) for p in args.drafts] if args.drafts
             else sorted(Path("data/battery/drafts").glob("*.jsonl")))
    if not paths:
        print("VALIDATE FAIL — no draft files found")
        return 1

    blockdata, blockcompiled = load_blocklists(Path(args.blocklists))
    bl_sha, _ = file_digest(Path(args.blocklists))
    exemptions, matched = load_exemptions(Path(args.exemptions))

    f = Findings()
    inputs = []
    total_cells = 0
    all_records = []
    for path in paths:
        sha, size = file_digest(path)
        inputs.append((path, sha, size))
        n, scenarios = validate_file(path, blockdata, blockcompiled, f,
                                     exemptions, matched)
        total_cells += n
        all_records.extend(
            json.loads(l) for l in
            path.read_text(encoding="utf-8").splitlines() if l.strip())
    cross_type_name_check(all_records, f)
    stale_exemptions = [ex for i, ex in enumerate(exemptions)
                        if not matched.get(i)]

    f.researcher_flags = list(dict.fromkeys(f.researcher_flags))
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    verdict = "FAIL (blocking)" if f.blocking else "PASS"
    report = []
    report.append("# Battery validation report")
    report.append("")
    report.append(f"Produced by: {PRODUCED_BY}")
    report.append(f"Generated: {now} — `src/battery/validate_battery.py`")
    report.append(f"Blocklists: `{args.blocklists}` sha256 `{bl_sha[:12]}…`")
    report.append("")
    report.append("Inputs:")
    for path, sha, size in inputs:
        report.append(f"- `{path}` — sha256 `{sha[:12]}…`, {size} bytes")
    report.append("")
    report.append(f"## Verdict: **{verdict}** — {total_cells} cells checked, "
                  f"{len(f.blocking)} blocking, {len(f.warnings)} warnings, "
                  f"{len(f.researcher_flags)} researcher flags, "
                  f"{len(f.length_flags)} length flags, "
                  f"{len(f.name_flags)} name flags, "
                  f"{len(f.exempted)} exempted hits")
    report.append("")
    report.append("Lexeme scope: **global** — every type is checked against "
                  "the global list and all ratified per-value lists "
                  "(researcher, 2026-07-31). `discipline_only` entries are "
                  "not enforced anywhere.")
    report.append("")
    if f.blocking:
        report.append("## BLOCKING failures")
        for check, loc, detail in f.blocking:
            report.append(f"- **{check}** `{loc}` — {detail}")
        report.append("")
    if f.warnings:
        report.append("## Warnings (non-blocking)")
        for check, loc, detail in f.warnings:
            report.append(f"- {check} `{loc}` — {detail}")
        report.append("")
    if f.researcher_flags:
        report.append("## Researcher decisions needed (non-blocking)")
        for flag in f.researcher_flags:
            report.append(f"- {flag}")
        report.append("")
    if f.name_flags:
        report.append("## Cross-type character-name flags (non-blocking)")
        report.append("")
        report.append("Reused names risk cross-item association at "
                      "administration and muddy per-type similarity readings. "
                      "The extractor over-collects proper nouns (place names, "
                      "brands), so entries need a human glance.")
        report.append("")
        for flag in f.name_flags:
            report.append(f"- {flag}")
        report.append("")
    if f.exempted:
        report.append("## Granted exemptions (informational — hits downgraded)")
        report.append("")
        report.append("Each line is a real blocklist hit that a documented "
                      "researcher exemption downgraded. Exemptions never "
                      "suppress silently: if this section is non-empty, the "
                      "text still contains the lexeme.")
        report.append("")
        for line in f.exempted:
            report.append(f"- {line}")
        report.append("")
    if stale_exemptions:
        report.append("## Stale exemptions (matched nothing)")
        report.append("")
        report.append("Granted but no longer matching any hit — the text was "
                      "probably rewritten. Remove them so the exemption list "
                      "stays an accurate record of what is being tolerated.")
        report.append("")
        for ex in stale_exemptions:
            report.append(f"- {ex.get('cell', '?')} / {ex.get('lexeme', '?')!r} "
                          f"({ex.get('date', 'no date')})")
        report.append("")
    if f.length_flags:
        report.append("## Length flags (non-blocking, check e)")
        for flag in f.length_flags:
            report.append(f"- {flag}")
        report.append("")
    report.append("## Per-file detail")
    report.append("")
    report.extend(f.lines)
    report.append("Notes: token counts are whitespace-split tokens (proxy — "
                  "model tokenizer not loadable off-pod). Blocklist scope is "
                  "the stimulus fields listed in data/battery/battery_schema.md "
                  "(researcher-confirmed 2026-07-30). Bare 'care/cared/caring' "
                  "is authoring discipline, not blocklisted — see "
                  "docs/battery_validator_backlog.md for pending edits.")
    report.append("")
    text = "\n".join(report)

    print(text)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(report_path, lambda fh: fh.write(text),
                 mode="w", encoding="utf-8", newline="\n")
    sha, size = file_digest(report_path)
    print(f"DIGEST {sha} {size} {report_path.name}")
    return 1 if f.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
