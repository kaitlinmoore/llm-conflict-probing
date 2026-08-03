#!/usr/bin/env python3
"""
freeze_battery.py — freeze the conflict battery from the validated drafts
(freeze checklist step 8; researcher order 2026-08-05).

Contract:
  - APPROVE-ONLY, exact match: a row is freeze-eligible iff
    metadata.reviewer_verdict == "approve" (case- and whitespace-sensitive,
    per the documented filter). The freezer REFUSES to run if any record
    carries any other token (including blank) — drops are never silent; the
    pre-freeze verdict-integrity report (2026-08-05) guarantees zero.
  - BOTH OPTION ORDERS for anything carrying options (choice-family cells
    and choice-family topical controls), per D36: the BA row swaps
    option_A/option_B and flips expected_pick; `order` ∈ {"AB", "BA"}.
    Refusal-family rows (no options) freeze once with order "NA".
  - DETERMINISTIC: rows sorted by (record_type, type_num, scenario/control
    id, condition, order); no timestamps inside the frozen file, so its
    sha256 is reproducible from the same drafts. Timestamp lives in the
    manifest only.
  - Output: data/battery/frozen/battery_frozen_v1.jsonl + manifest with
    input digests, verdict-integrity counts, row counts, and the frozen
    file's sha256. Atomic writes, DIGEST lines.

Usage:
  python src/battery/freeze_battery.py            # freeze
  python src/battery/freeze_battery.py --out-dir data/battery/frozen
"""

import argparse
import datetime
import json
import sys
from collections import Counter
from pathlib import Path

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    from runner_lib import atomic_write, file_digest

PRODUCED_BY = "Claude Fable 5 (model id claude-fable-5)"
SCHEMA = "battery_frozen_v1"


def load_records(drafts_dir: Path):
    records, digests = [], {}
    for p in sorted(drafts_dir.glob("*.jsonl")):
        sha, size = file_digest(p)
        digests[p.name] = {"sha256": sha, "bytes": size}
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records, digests


def verdict_integrity(records):
    """-> (counts, offenders). Freeze refuses on any offender."""
    counts = Counter()
    offenders = []
    for r in records:
        v = r.get("metadata", {}).get("reviewer_verdict", "")
        counts[v] += 1
        if v != "approve":
            rid = (f"{r.get('type_id')}:"
                   f"{r.get('scenario_id') or r.get('control_id')}:"
                   f"{r.get('condition', 'control')}")
            offenders.append((rid, repr(v)))
    return counts, offenders


def orders_for(rec):
    """Rows to freeze for one draft record: AB (as authored) and, when the
    record carries options, BA with options swapped and expected_pick
    flipped (D36). Choice-family topical controls carry options and get
    both orders; refusal cells/controls freeze once."""
    has_options = bool(rec.get("option_A") or rec.get("option_B"))
    ab = dict(rec)
    ab["order"] = "AB" if has_options else "NA"
    if not has_options:
        return [ab]
    ba = dict(rec)
    ba["order"] = "BA"
    ba["option_A"], ba["option_B"] = rec.get("option_B"), rec.get("option_A")
    if rec.get("value_A") or rec.get("value_B"):
        ba["value_A"], ba["value_B"] = rec.get("value_B"), rec.get("value_A")
    if rec.get("expected_pick") in ("A", "B"):
        ba["expected_pick"] = "B" if rec["expected_pick"] == "A" else "A"
    return [ab, ba]


def row_key(row):
    return (row.get("record_type", "battery_cell"),
            row.get("type_num", 0),
            row.get("scenario_id") or row.get("control_id", ""),
            row.get("condition", ""),
            row.get("order", ""))


def freeze(records):
    rows = []
    for rec in records:
        for row in orders_for(rec):
            row["schema_version"] = SCHEMA
            row["row_id"] = (f"{row.get('type_id')}:"
                             f"{row.get('scenario_id') or row.get('control_id')}:"
                             f"{row.get('condition', 'control')}:{row['order']}")
            rows.append(row)
    rows.sort(key=row_key)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--drafts", default="data/battery/drafts")
    ap.add_argument("--out-dir", default="data/battery/frozen")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    records, digests_in = load_records(Path(args.drafts))
    counts, offenders = verdict_integrity(records)
    print(f"records: {len(records)}; verdict tokens: "
          f"{ {repr(k): v for k, v in counts.items()} }")
    if offenders:
        print(f"FREEZE REFUSED — {len(offenders)} record(s) without exact "
              f"'approve' (drops are never silent):")
        for rid, v in offenders:
            print(f"  {rid} {v}")
        return 1

    rows = freeze(records)
    n = Counter((r.get("record_type", "battery_cell"), r["order"])
                for r in rows)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "battery_frozen_v1.jsonl"
    payload = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"
    atomic_write(out, lambda f: f.write(payload), mode="w",
                 encoding="utf-8", newline="\n")
    sha, size = file_digest(out)
    print(f"DIGEST {sha} {size} {out.name}")

    manifest = {
        "schema_version": SCHEMA,
        "produced_by": PRODUCED_BY,
        "frozen_utc": datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds"),
        "input_digests": digests_in,
        "verdict_integrity": {"approve": counts.get("approve", 0),
                              "non_approve": len(offenders)},
        "n_draft_records": len(records),
        "n_frozen_rows": len(rows),
        "rows_by_kind_order": {f"{k}:{o}": c for (k, o), c in sorted(n.items())},
        "frozen_sha256": sha,
        "frozen_bytes": size,
    }
    mpath = out_dir / "freeze_manifest.json"
    atomic_write(mpath, lambda f: f.write(json.dumps(manifest, indent=2) + "\n"),
                 mode="w", encoding="utf-8", newline="\n")
    msha, msize = file_digest(mpath)
    print(f"DIGEST {msha} {msize} {mpath.name}")
    print(f"FROZEN: {len(rows)} rows from {len(records)} approved records "
          f"({manifest['rows_by_kind_order']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
