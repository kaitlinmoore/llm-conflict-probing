#!/usr/bin/env python3
"""
ingest_workbook.py — read per-type battery review workbooks
(data/battery/workbooks/CB_<type_id>.xlsx, sheet "Scenarios") and emit
data/battery/drafts/<type_id>.jsonl, one record per cell, schema
battery_draft_v1 (data/battery/battery_schema.md).

Columns map 1:1; reviewer_verdict / reviewer_comments are carried through as
metadata. Only rows with reviewer_verdict == "approve" will be eligible for
freezing later; the freezer is a later task and is NOT this script.

The xlsx reader is stdlib-only (zipfile + xml.etree): openpyxl is not in the
pinned dependency stack and adding dependencies is ask-first (CLAUDE.md).
It handles shared strings, inline strings, and plain values — sufficient for
the Cowork-authored review workbooks, which contain no formulas.

Normalizations (recorded in metadata, see schema doc):
  - shared_conflict_text (type-1 header) -> shared_opposition_text
  - option_A_<value> / option_B_<value> -> option_A/option_B + value_A/value_B

Text is byte-faithful: no trimming or re-encoding, so downstream
byte-identity checks (stem, shared_opposition_text) are meaningful.

Writes are atomic (tmp -> fsync -> os.replace); a DIGEST line is printed per
output and recorded in data/battery/drafts/ingest_manifest.json.

Usage:
  python src/battery/ingest_workbook.py \
      --workbooks data/battery/workbooks/CB_type1_honesty_vs_care.xlsx ... \
      [--out-dir data/battery/drafts]
  (default with no --workbooks: every CB_*.xlsx in data/battery/workbooks/)
"""

import argparse
import datetime
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:  # running as a plain script from src/battery/
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    from runner_lib import atomic_write, file_digest

SCHEMA_VERSION = "battery_draft_v1"
SHEET_NAME = "Scenarios"
CONTROL_SHEET = "Topical_controls"  # optional; ingested per researcher
                                    # direction 2026-07-30 (schema doc)
CHOICE_CONDITIONS = ("agree_A", "agree_B", "oppose_tip_A", "oppose_tip_B")
REFUSAL_CONDITIONS = ("agree_comply", "agree_refuse",
                      "oppose_tip_comply", "oppose_tip_refuse")
CONDITIONS = CHOICE_CONDITIONS          # back-compat alias (v1 callers)
EXPECTED_RESPONSES = ("comply", "refuse", "hedge")

# Canonical core headers. Anything else in the sheet lands in extra_fields
# under its original header (1:1, lossless) — that is how each type's declared
# design variables (duty_source, domain, activity_domain, standing_type,
# continuity_depth, stakes, subject, relationship, ask, structure …) are
# carried through without being normalized away.
CORE_HEADERS = {
    "scenario_id", "title", "condition", "condition_label", "stem",
    "condition_insert", "expected_pick", "expected_response", "design_note",
    "reviewer_verdict", "reviewer_comments",
}
SHARED_TEXT_HEADERS = ("shared_opposition_text", "shared_conflict_text")
OPTION_RE = re.compile(r"^option_([AB])_([a-z_]+)$")
TYPE_ID_RE = re.compile(r"^CB_(type(\d+)_[a-z0-9_]+)\.xlsx$", re.IGNORECASE)

# Family per the twelve-type slate in docs/WEEK_PLAN_stage2.md:
# types 1-6 choice family, 7-12 refusal family.
def family_for_type(type_num: int) -> str:
    return "choice" if 1 <= type_num <= 6 else "refusal"


# ---------------------------------------------------------------------------
# Minimal stdlib xlsx reading
# ---------------------------------------------------------------------------

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def _cell_ref_to_col(ref: str) -> int:
    letters = re.match(r"([A-Z]+)", ref).group(1)
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - 64)
    return idx - 1


def _shared_strings(z: zipfile.ZipFile):
    try:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(t.text or "" for t in si.iter(f"{{{_NS['m']}}}t"))
            for si in root.findall("m:si", _NS)]


def _sheet_path(z: zipfile.ZipFile, sheet_name: str) -> str:
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.get("Id"): rel.get("Target") for rel in rels}
    for sh in wb.iter(f"{{{_NS['m']}}}sheet"):
        if sh.get("name") == sheet_name:
            target = rel_map[sh.get(f"{{{_NS['r']}}}id")].lstrip("/")
            return target if target.startswith("xl/") else "xl/" + target
    raise KeyError(f"sheet {sheet_name!r} not found "
                   f"(sheets: {[s.get('name') for s in wb.iter(f'{{{_NS['m']}}}sheet')]})")


def read_sheet(xlsx_path, sheet_name):
    """-> list of rows, each {header: str_value}, using row 1 as the header.
    Values are strings, byte-faithful; missing cells are ''."""
    with zipfile.ZipFile(xlsx_path) as z:
        shared = _shared_strings(z)
        root = ET.fromstring(z.read(_sheet_path(z, sheet_name)))
        raw = {}  # row_num -> {col_idx: value}
        for row in root.iter(f"{{{_NS['m']}}}row"):
            rnum = int(row.get("r"))
            for c in row.findall("m:c", _NS):
                col = _cell_ref_to_col(c.get("r"))
                t = c.get("t")
                v = c.find("m:v", _NS)
                if t == "s" and v is not None:
                    val = shared[int(v.text)]
                elif t == "inlineStr":
                    is_el = c.find("m:is", _NS)
                    val = ("".join(tt.text or "" for tt in
                                   is_el.iter(f"{{{_NS['m']}}}t"))
                           if is_el is not None else "")
                else:
                    val = v.text if v is not None else ""
                raw.setdefault(rnum, {})[col] = val
    if 1 not in raw:
        raise ValueError(f"{xlsx_path}: sheet {sheet_name!r} has no header row")
    headers = raw.pop(1)
    rows = []
    for rnum in sorted(raw):
        cells = raw[rnum]
        if not any(str(v).strip() for v in cells.values()):
            continue  # fully empty row
        rows.append(({h: cells.get(i, "") for i, h in headers.items()}, rnum))
    return rows


# ---------------------------------------------------------------------------
# Workbook -> records
# ---------------------------------------------------------------------------

def parse_type_id(workbook_name: str):
    m = TYPE_ID_RE.match(workbook_name)
    if not m:
        raise ValueError(
            f"workbook name {workbook_name!r} does not match CB_<type_id>.xlsx")
    return m.group(1), int(m.group(2))


def type_values(type_id: str):
    """['privacy', 'care'] from 'type2_privacy_vs_care' — the '_vs_'
    separator is unambiguous even for underscore value names."""
    body = type_id.split("_", 1)[1]
    if "_vs_" not in body:
        raise ValueError(f"type_id {type_id!r} has no _vs_ separator")
    return body.split("_vs_", 1)


def ingest_workbook(xlsx_path: Path):
    """-> (type_id, [records]). Raises on structural problems that make the
    mapping ambiguous (unknown option headers, missing shared-text column)."""
    type_id, type_num = parse_type_id(xlsx_path.name)
    wb_sha, _ = file_digest(xlsx_path)
    rows = read_sheet(xlsx_path, SHEET_NAME)

    records = []
    for row, rnum in rows:
        option, values, extra = {}, {}, {}
        shared_text, shared_header = None, None
        for header, val in row.items():
            if header in CORE_HEADERS:
                continue
            m = OPTION_RE.match(header)
            if m:
                option[m.group(1)] = val
                values[m.group(1)] = m.group(2)
            elif header in SHARED_TEXT_HEADERS:
                if shared_header is not None:
                    raise ValueError(f"{xlsx_path.name} row {rnum}: both "
                                     f"shared-text headers present")
                shared_text, shared_header = val, header
            else:
                extra[header] = val
        family = family_for_type(type_num)
        # Family is declared by type number; the sheet must agree with it.
        # Choice sheets carry option columns + expected_pick; refusal sheets
        # carry neither and use expected_response instead (no options, no
        # order counterbalance).
        if family == "choice":
            if set(option) != {"A", "B"}:
                raise ValueError(
                    f"{xlsx_path.name} row {rnum}: choice-family type expects "
                    f"option_A_<x> and option_B_<x> columns, got {sorted(option)}")
        else:
            if option:
                raise ValueError(
                    f"{xlsx_path.name} row {rnum}: refusal-family type must "
                    f"not carry option columns, got {sorted(option)}")
            if "expected_response" not in row:
                raise ValueError(
                    f"{xlsx_path.name} row {rnum}: refusal-family type "
                    f"requires an expected_response column")
        if shared_header is None:
            raise ValueError(f"{xlsx_path.name} row {rnum}: no "
                             f"shared_opposition_text/shared_conflict_text column")
        # Blocklist scoping uses the value pair parsed from type_id, not the
        # option-column suffixes: types 5 and 6 name their options by stance
        # (option_A_hold, option_A_directive) rather than by value, so header
        # suffixes cannot identify the poles. Suffixes are kept below as
        # descriptive metadata where they exist.
        tvals = type_values(type_id)
        records.append({
            "schema_version": SCHEMA_VERSION,
            "record_type": "battery_cell",
            "type_id": type_id,
            "type_num": type_num,
            "family": family,
            "type_values": tvals,
            "scenario_id": row.get("scenario_id", ""),
            "title": row.get("title", ""),
            "condition": row.get("condition", ""),
            "condition_label": row.get("condition_label", ""),
            "stem": row.get("stem", ""),
            "option_A": option.get("A", ""),
            "option_B": option.get("B", ""),
            "value_A": values.get("A", ""),
            "value_B": values.get("B", ""),
            "shared_opposition_text": shared_text,
            "condition_insert": row.get("condition_insert", ""),
            "expected_pick": row.get("expected_pick", ""),
            "expected_response": row.get("expected_response", ""),
            "design_note": row.get("design_note", ""),
            "extra_fields": extra,
            "metadata": {
                "reviewer_verdict": row.get("reviewer_verdict", ""),
                "reviewer_comments": row.get("reviewer_comments", ""),
                "source": {
                    "workbook": xlsx_path.name,
                    "workbook_sha256": wb_sha,
                    "sheet": SHEET_NAME,
                    "row": rnum,
                    "shared_text_header": shared_header,
                },
            },
        })
    return type_id, records


def ingest_controls(xlsx_path: Path):
    """Topical_controls sheet -> topical_control records ([] if the sheet is
    absent — types without control sheets are normal)."""
    type_id, type_num = parse_type_id(xlsx_path.name)
    wb_sha, _ = file_digest(xlsx_path)
    try:
        rows = read_sheet(xlsx_path, CONTROL_SHEET)
    except KeyError:
        return type_id, []
    tvals = type_values(type_id)
    records = []
    for row, rnum in rows:
        # Refusal-family control sheets annotate the stem header with the
        # control's design intent, e.g.
        #   "stem (assistance ask, no condition, no concealment)".
        # Normalize to `stem` and record the original header rather than
        # reading an empty value silently.
        stem_header = next((h for h in row
                            if h == "stem" or h.startswith("stem ")), None)
        records.append({
            "schema_version": SCHEMA_VERSION,
            "record_type": "topical_control",
            "type_id": type_id,
            "type_num": type_num,
            "family": family_for_type(type_num),
            "type_values": tvals,
            "control_id": row.get("control_id", ""),
            "matched_domain": row.get("matched_domain", ""),
            "stem": row.get(stem_header, "") if stem_header else "",
            "option_A": row.get("option_A", ""),
            "option_B": row.get("option_B", ""),
            "note": row.get("note", ""),
            "metadata": {
                "reviewer_verdict": row.get("reviewer_verdict", ""),
                "reviewer_comments": row.get("reviewer_comments", ""),
                "source": {
                    "workbook": xlsx_path.name,
                    "workbook_sha256": wb_sha,
                    "sheet": CONTROL_SHEET,
                    "row": rnum,
                    "stem_header": stem_header,
                },
            },
        })
    return type_id, records


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbooks", nargs="*", default=None,
                    help="xlsx paths; default: data/battery/workbooks/CB_*.xlsx")
    ap.add_argument("--out-dir", default="data/battery/drafts")
    args = ap.parse_args(argv)

    paths = ([Path(p) for p in args.workbooks] if args.workbooks
             else sorted(Path("data/battery/workbooks").glob("CB_*.xlsx")))
    if not paths:
        print("INGEST FAIL — no workbooks found")
        return 1
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "ingest_manifest.json"
    manifest = (json.loads(manifest_path.read_text(encoding="utf-8"))
                if manifest_path.exists() else {"files": {}})

    status = 0
    for path in paths:
        try:
            type_id, records = ingest_workbook(path)
            _, controls = ingest_controls(path)
        except Exception as e:
            print(f"INGEST FAIL — {path.name}: {e}")
            status = 1
            continue
        wb_sha, wb_size = file_digest(path)
        outputs = [(out_dir / f"{type_id}.jsonl", records)]
        if controls:
            outputs.append((out_dir / f"{type_id}.controls.jsonl", controls))
        for out_path, recs in outputs:
            payload = "".join(json.dumps(r, ensure_ascii=False) + "\n"
                              for r in recs)
            atomic_write(out_path, lambda f, p=payload: f.write(p),
                         mode="w", encoding="utf-8", newline="\n")
            sha, size = file_digest(out_path)
            manifest["files"][out_path.name] = {
                "sha256": sha, "bytes": size, "n_records": len(recs),
                "source_workbook": path.name,
                "source_workbook_sha256": wb_sha,
                "source_workbook_bytes": wb_size,
                "ingested_utc": datetime.datetime.now(
                    datetime.timezone.utc).isoformat(timespec="seconds"),
                "schema_version": SCHEMA_VERSION,
            }
            print(f"Wrote {out_path} ({len(recs)} records)")
            print(f"DIGEST {sha} {size} {out_path.name}")

    atomic_write(manifest_path,
                 lambda f: f.write(json.dumps(manifest, indent=2) + "\n"),
                 mode="w", encoding="utf-8", newline="\n")
    m_sha, m_size = file_digest(manifest_path)
    print(f"DIGEST {m_sha} {m_size} {manifest_path.name}")
    return status


if __name__ == "__main__":
    sys.exit(main())
