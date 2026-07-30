#!/usr/bin/env python3
"""
validate_battery.py — scripted validation gate for battery draft files
(data/battery/drafts/<type_id>.jsonl, schema battery_draft_v1 — see
data/battery/battery_schema.md). Runs during authoring so defects surface
while the author is still in the file, not after.

Checks (task spec 2026-07-30, session 1):
  a. Lexeme blocklists (data/battery/lexeme_blocklists.json): whole-word,
     case-insensitive, over the stimulus fields (stem, option_A, option_B,
     shared_opposition_text, condition_insert) of every cell. Global list
     applies to every item; per-value lists apply where value_A/value_B
     match. BLOCKING. A rostered value with an empty/pending list is a
     researcher-decision flag, non-blocking.
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
CONDITIONS = {"agree_A", "agree_B", "oppose_tip_A", "oppose_tip_B"}
OPPOSE = ("oppose_tip_A", "oppose_tip_B")
AGREE = ("agree_A", "agree_B")
STIMULUS_FIELDS = ("stem", "option_A", "option_B",
                   "shared_opposition_text", "condition_insert")
LENGTH_FLAG_RATIO = 1.5


def load_blocklists(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    compiled = {}
    for scope, lexemes in [("global", data.get("global", []))] + \
            sorted(data.get("per_value", {}).items()):
        compiled[scope] = [(lx, re.compile(rf"\b{re.escape(lx)}\b", re.IGNORECASE))
                           for lx in lexemes]
    return data, compiled


def token_count(text: str) -> int:
    """Whitespace tokens — documented proxy for model tokens (see module doc)."""
    return len(text.split())


class Findings:
    def __init__(self):
        self.blocking = []   # (check, location, detail)
        self.warnings = []
        self.researcher_flags = []
        self.length_flags = []
        self.lines = []      # report body lines

    def block(self, check, loc, detail):
        self.blocking.append((check, loc, detail))

    def warn(self, check, loc, detail):
        self.warnings.append((check, loc, detail))


def validate_file(path: Path, blockdata, blockcompiled, f: Findings):
    records = [json.loads(l) for l in
               path.read_text(encoding="utf-8").splitlines() if l.strip()]
    f.lines.append(f"### `{path.name}` — {len(records)} cells")
    f.lines.append("")

    # -- d. structure: uniqueness, grouping, per-cell fields ----------------
    by_scenario = {}
    seen_keys = set()
    for rec in records:
        sid, cond = rec.get("scenario_id", ""), rec.get("condition", "")
        loc = f"{path.name}:{sid}:{cond}"
        if not sid:
            f.block("d.structure", loc, "empty scenario_id")
        if cond not in CONDITIONS:
            f.block("d.structure", loc, f"condition {cond!r} not in {sorted(CONDITIONS)}")
        key = (sid, cond)
        if key in seen_keys:
            f.block("d.structure", loc, "duplicate (scenario_id, condition)")
        seen_keys.add(key)
        by_scenario.setdefault(sid, []).append(rec)

        if not rec.get("option_A", ""):
            f.block("d.structure", loc, "option_A empty")
        if not rec.get("option_B", ""):
            f.block("d.structure", loc, "option_B empty")
        if rec.get("option_A") and rec.get("option_A") == rec.get("option_B"):
            f.block("d.structure", loc, "option_A == option_B (duplicate options)")
        if rec.get("expected_pick") not in ("A", "B"):
            f.block("d.structure", loc,
                    f"expected_pick {rec.get('expected_pick')!r} not in {{A, B}}")

    for sid, cells in sorted(by_scenario.items()):
        conds = sorted(c.get("condition", "") for c in cells)
        if set(conds) != CONDITIONS or len(conds) != 4:
            f.block("d.structure", f"{path.name}:{sid}",
                    f"expected exactly 4 cells {sorted(CONDITIONS)}, got {conds}")

    # -- c. stem consistency ------------------------------------------------
    for sid, cells in sorted(by_scenario.items()):
        stems = {c.get("stem", "") for c in cells}
        if len(stems) > 1:
            f.block("c.stem", f"{path.name}:{sid}",
                    f"{len(stems)} distinct stems across the scenario's cells")

    # -- b. shared opposition text ------------------------------------------
    for sid, cells in sorted(by_scenario.items()):
        opp = {c["condition"]: c.get("shared_opposition_text", "")
               for c in cells if c.get("condition") in OPPOSE}
        if len(opp) == 2 and opp[OPPOSE[0]] != opp[OPPOSE[1]]:
            f.block("b.shared_text", f"{path.name}:{sid}",
                    "oppose_tip_A vs oppose_tip_B shared_opposition_text differ "
                    "(byte comparison)")
        for c in cells:
            if c.get("condition") in AGREE and c.get("shared_opposition_text", ""):
                f.warn("b.shared_text", f"{path.name}:{sid}:{c['condition']}",
                       "nonempty shared_opposition_text on an agreement cell")

    # -- a. lexeme blocklists -----------------------------------------------
    pending = blockdata.get("pending_researcher", {})
    values_seen = set()
    for rec in records:
        va, vb = rec.get("value_A", ""), rec.get("value_B", "")
        values_seen.update([va, vb])
        scopes = ["global"] + [v for v in (va, vb) if v in blockcompiled]
        loc_base = f"{path.name}:{rec.get('scenario_id')}:{rec.get('condition')}"
        for field in STIMULUS_FIELDS:
            text = rec.get(field, "") or ""
            if not text:
                continue
            for scope in scopes:
                for lexeme, pattern in blockcompiled[scope]:
                    if pattern.search(text):
                        f.block("a.lexeme", f"{loc_base}:{field}",
                                f"blocked lexeme {lexeme!r} (list: {scope})")
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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts", nargs="*", help="draft jsonl paths "
                    "(default: data/battery/drafts/*.jsonl)")
    ap.add_argument("--blocklists", default="data/battery/lexeme_blocklists.json")
    ap.add_argument("--report", default="docs/battery_validation_report.md")
    args = ap.parse_args(argv)

    paths = ([Path(p) for p in args.drafts] if args.drafts
             else sorted(Path("data/battery/drafts").glob("*.jsonl")))
    if not paths:
        print("VALIDATE FAIL — no draft files found")
        return 1

    blockdata, blockcompiled = load_blocklists(Path(args.blocklists))
    bl_sha, _ = file_digest(Path(args.blocklists))

    f = Findings()
    inputs = []
    total_cells = 0
    for path in paths:
        sha, size = file_digest(path)
        inputs.append((path, sha, size))
        n, scenarios = validate_file(path, blockdata, blockcompiled, f)
        total_cells += n

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
                  f"{len(f.length_flags)} length flags")
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
                  "the stimulus fields listed in data/battery/battery_schema.md; "
                  "the schema doc records this as an open interpretation "
                  "question for the researcher.")
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
