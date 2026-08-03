#!/usr/bin/env python3
"""
apply_pending_edits.py — apply the queued stimulus-text edits from
docs/battery_validator_backlog.md to the review workbooks, re-runnably.

Why a script and not manual edits: the workbooks are live under the
researcher's review pass, so an edit applied by hand to a copy is lost the
moment the workbook is re-saved. This can be re-run against updated workbooks
at any time and is a no-op once an edit has landed.

Properties:
  - IDEMPOTENT. An edit whose `find` text is gone and whose `replace` text is
    present is reported `already applied` and skipped.
  - DRY RUN BY DEFAULT. Pass --apply to write. Without it nothing is touched.
  - REFUSES WHILE EXCEL HAS THE FILE OPEN. An Excel lock file (`~$<name>`)
    next to a workbook means unsaved changes may be in memory; writing under
    that condition can lose the researcher's in-progress review edits.
  - BACKS UP. `<workbook>.bak-<UTC stamp>` before the first write to a file.
  - ATOMIC + DIGESTED. tmp -> fsync -> os.replace, DIGEST line per file.

Mechanism: cell text lives either in `xl/sharedStrings.xml` or, as in these
Cowork-authored workbooks, inline in `xl/worksheets/sheetN.xml`. The edit is a
targeted string replacement across those parts; every other part of the
archive is copied byte-identical. Formatting, formulas, and the researcher's
reviewer_verdict cells are untouched.

Usage:
  python src/battery/apply_pending_edits.py            # dry run, shows plan
  python src/battery/apply_pending_edits.py --apply    # write
"""

import argparse
import datetime
import json
import shutil
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from src.pretest.runner_lib import atomic_write, file_digest
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pretest"))
    from runner_lib import atomic_write, file_digest

WORKBOOK_DIR = Path("data/battery/workbooks")

# Queue mirrors docs/battery_validator_backlog.md "Pending workbook edits".
# One entry per edit; add a tuple to add an edit.
EDITS = [
    {
        "workbook": "CB_type1_honesty_vs_care.xlsx",
        "find": "really cared about getting it right",
        "replace": "wanted it exactly right",
        "reason": ("bare 'cared' is discipline-only (D48), so no validator "
                   "catches it; researcher-logged 2026-07-30"),
        "backlog_ref": "Pending workbook edits #1",
    },
]


def text_parts(path: Path):
    """{part_name: xml_text} for every archive part that can hold cell text."""
    out = {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name == "xl/sharedStrings.xml" or (
                    name.startswith("xl/worksheets/") and name.endswith(".xml")):
                out[name] = z.read(name).decode("utf-8")
    return out


def xml_forms(text: str):
    """The forms a cell string can take inside sheet XML, most likely first.

    Non-ASCII storage is NOT uniform across the battery workbooks: sheets
    Excel has re-saved hold raw UTF-8 (T1–T10 after the review pass), while
    untouched Cowork-authored sheets hold decimal character references like
    `&#8212;` (T11/T12, measured 2026-08-04). A needle built from the plain
    text therefore has up to two valid encodings; matching must try both or
    an edit whose text contains an em dash reports a false UNMATCHED.
    """
    esc = escape(text)
    ent = "".join(f"&#{ord(c)};" if ord(c) > 0x7F else c for c in esc)
    return [esc] if ent == esc else [esc, ent]


def count_in_parts(parts, text):
    """Occurrences of `text` across parts, summed over its XML encodings
    (a given stretch of XML matches at most one encoding, so the sum never
    double-counts)."""
    return sum(xml.count(form)
               for xml in parts.values() for form in xml_forms(text))


def replace_in_xml(xml: str, find: str, repl: str) -> str:
    """Replace every occurrence of `find` (in any of its XML encodings) with
    `repl`, written in the encoding style the part already uses."""
    forms_f, forms_r = xml_forms(find), xml_forms(repl)
    f_esc, f_ent = forms_f[0], forms_f[-1]
    r_esc, r_ent = forms_r[0], forms_r[-1]
    entity_style = "&#" in xml
    if f_ent != f_esc:
        xml = xml.replace(f_ent, r_ent)
    return xml.replace(f_esc, r_ent if entity_style else r_esc)


def rewrite_parts(path: Path, replacements: dict, out_path: Path):
    """Copy the archive, substituting the given {part: new_xml}."""
    with zipfile.ZipFile(path) as src:
        items = src.infolist()
        payload = {i.filename: src.read(i.filename) for i in items}
    for name, xml in replacements.items():
        payload[name] = xml.encode("utf-8")

    def _write(fh):
        with zipfile.ZipFile(fh, "w", zipfile.ZIP_DEFLATED) as out:
            for i in items:
                out.writestr(i, payload[i.filename])
    atomic_write(out_path, _write, mode="wb")


def lock_files(directory: Path):
    return sorted(p.name for p in directory.glob("~$*"))


def main(argv=None):
    # Windows consoles default to cp1252; edit text is UTF-8 (em dashes,
    # arrows). Degrade unprintable characters instead of crashing mid-report.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write changes (default: dry run)")
    ap.add_argument("--workbook-dir", default=str(WORKBOOK_DIR))
    ap.add_argument("--edits",
                    help="JSON edit batch (object with an 'edits' list of "
                         "{workbook, find, replace, reason, ref}); replaces "
                         "the built-in queue for this run")
    args = ap.parse_args(argv)

    edits = EDITS
    if args.edits:
        blob = json.loads(Path(args.edits).read_text(encoding="utf-8"))
        edits = blob["edits"] if isinstance(blob, dict) else blob
        for i, e in enumerate(edits):
            for k in ("workbook", "find", "replace"):
                if not e.get(k):
                    print(f"BAD EDIT #{i}: missing {k!r}")
                    return 2

    wdir = Path(args.workbook_dir)
    locks = lock_files(wdir)
    if locks and args.apply:
        print(f"REFUSING TO WRITE — Excel lock files present: {locks}")
        print("Close the workbooks in Excel (unsaved review edits would be "
              "lost) and re-run.")
        return 2
    if locks:
        print(f"note: lock files present ({locks}); --apply would refuse")

    planned, applied, already, missing = [], [], [], []
    for edit in edits:
        path = wdir / edit["workbook"]
        if not path.exists():
            missing.append((edit, "workbook not found"))
            continue
        parts = text_parts(path)
        n_find = count_in_parts(parts, edit["find"])
        n_repl = count_in_parts(parts, edit["replace"])
        if n_find:
            planned.append((edit, path, n_find, parts))
        elif n_repl:
            already.append((edit, n_repl))
        else:
            missing.append((edit, "neither original nor replacement text "
                                  "found — workbook may have been reworded"))

    def ref(edit):
        return edit.get("backlog_ref") or edit.get("ref", "?")

    print(f"pending edits: {len(edits)} | to apply: {len(planned)} | "
          f"already applied: {len(already)} | unmatched: {len(missing)}")
    for edit, n in already:
        print(f"  [already] {edit['workbook']}: {ref(edit)} "
              f"({n} occurrence(s) of replacement)")
    for edit, why in missing:
        print(f"  [UNMATCHED] {edit['workbook']}: {ref(edit)} — {why}")
        print(f"      find: {edit['find']!r}")
    for edit, path, n, *_ in planned:
        print(f"  [{'apply' if args.apply else 'would apply'}] "
              f"{edit['workbook']}: {ref(edit)} — {n} occurrence(s)")
        print(f"      {edit['find']!r}")
        print(f"   -> {edit['replace']!r}")
        if edit.get("reason"):
            print(f"      reason: {edit['reason']}")

    if not args.apply:
        if planned:
            print("\nDRY RUN — nothing written. Re-run with --apply when the "
                  "workbooks are closed in Excel.")
        return 0

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backed_up = set()
    for edit, path, n, parts in planned:
        if path not in backed_up:
            shutil.copy2(path, path.with_suffix(path.suffix + f".bak-{stamp}"))
            backed_up.add(path)
        # re-read so consecutive edits to one workbook stack instead of
        # clobbering each other via stale part text
        parts = text_parts(path)
        changed = {}
        for name, xml in parts.items():
            new = replace_in_xml(xml, edit["find"], edit["replace"])
            if new != xml:
                changed[name] = new
        rewrite_parts(path, changed, path)
        sha, size = file_digest(path)
        applied.append(edit)
        print(f"applied: {edit['workbook']} ({n} occurrence(s))")
        print(f"DIGEST {sha} {size} {path.name}")

    if applied:
        print(f"\n{len(applied)} edit(s) applied; backups written as "
              f"*.bak-{stamp}.")
        print("Next: re-run the ingest and the validator —")
        print("  python src/battery/ingest_workbook.py")
        print("  python src/battery/validate_battery.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
