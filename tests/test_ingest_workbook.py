"""Tests for src/battery/ingest_workbook.py — stdlib only, off-pod.

Builds minimal .xlsx files by hand (zipfile + inline-string XML) so the
stdlib reader is exercised without openpyxl.
"""

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.battery import ingest_workbook as iw


def _col_name(idx):
    name = ""
    idx += 1
    while idx:
        idx, rem = divmod(idx - 1, 26)
        name = chr(65 + rem) + name
    return name


def write_xlsx(path, sheets):
    """sheets: {name: [[cell, ...], ...]} — all cells inline strings."""
    sheet_names = list(sheets)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/workbook.xml",
            '<?xml version="1.0"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets>' + "".join(
                f'<sheet name="{escape(n)}" sheetId="{i+1}" r:id="rId{i+1}"/>'
                for i, n in enumerate(sheet_names)) + '</sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",
            '<?xml version="1.0"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(
                f'<Relationship Id="rId{i+1}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                f'relationships/worksheet" Target="worksheets/sheet{i+1}.xml"/>'
                for i in range(len(sheet_names))) + '</Relationships>')
        for i, name in enumerate(sheet_names):
            rows_xml = []
            for rnum, row in enumerate(sheets[name], start=1):
                cells = "".join(
                    f'<c r="{_col_name(ci)}{rnum}" t="inlineStr">'
                    f'<is><t xml:space="preserve">{escape(str(v))}</t></is></c>'
                    for ci, v in enumerate(row))
                rows_xml.append(f'<row r="{rnum}">{cells}</row>')
            z.writestr(f"xl/worksheets/sheet{i+1}.xml",
                '<?xml version="1.0"?>'
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f'<sheetData>{"".join(rows_xml)}</sheetData></worksheet>')


HEADERS_T1 = ["scenario_id", "title", "structure", "investment", "ask",
              "relationship", "condition", "condition_label", "stem",
              "option_A_honesty", "option_B_care", "shared_conflict_text",
              "condition_insert", "expected_pick", "design_note",
              "reviewer_verdict", "reviewer_comments"]


def scenario_rows(sid="CB-hc-S1", shared="Shared opposition facts."):
    rows = []
    for cond in ("agree_A", "agree_B", "oppose_tip_A", "oppose_tip_B"):
        rows.append([
            sid, "The toast", "retrospective", "moderate", "direct",
            "friend (close)", cond, f"label {cond}", "Stem text.",
            "Option A text.", "Option B text.",
            shared if cond.startswith("oppose") else "",
            f"Insert for {cond}.", "A" if cond.endswith("A") else "B",
            "note", "approve" if cond == "agree_A" else "", "",
        ])
    return rows


class IngestTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make_workbook(self, name="CB_type1_honesty_vs_care.xlsx",
                      headers=None, rows=None, extra_sheets=None):
        sheets = {"README": [["readme"]],
                  "Scenarios": [headers or HEADERS_T1] + (rows or scenario_rows())}
        sheets.update(extra_sheets or {})
        path = self.dir / name
        write_xlsx(path, sheets)
        return path

    def test_ingest_produces_four_cells(self):
        type_id, records = iw.ingest_workbook(self.make_workbook())
        self.assertEqual(type_id, "type1_honesty_vs_care")
        self.assertEqual(len(records), 4)
        self.assertEqual({r["condition"] for r in records},
                         {"agree_A", "agree_B", "oppose_tip_A", "oppose_tip_B"})

    def test_option_headers_split_into_values(self):
        _, records = iw.ingest_workbook(self.make_workbook())
        rec = records[0]
        self.assertEqual(rec["value_A"], "honesty")
        self.assertEqual(rec["value_B"], "care")
        self.assertEqual(rec["option_A"], "Option A text.")
        self.assertEqual(rec["option_B"], "Option B text.")

    def test_shared_conflict_text_normalized_with_provenance(self):
        _, records = iw.ingest_workbook(self.make_workbook())
        opp = [r for r in records if r["condition"] == "oppose_tip_A"][0]
        self.assertEqual(opp["shared_opposition_text"], "Shared opposition facts.")
        self.assertEqual(opp["metadata"]["source"]["shared_text_header"],
                         "shared_conflict_text")

    def test_reviewer_columns_carried_as_metadata(self):
        _, records = iw.ingest_workbook(self.make_workbook())
        agree_a = [r for r in records if r["condition"] == "agree_A"][0]
        self.assertEqual(agree_a["metadata"]["reviewer_verdict"], "approve")
        self.assertNotIn("reviewer_verdict", agree_a)  # metadata only

    def test_extra_fields_lossless(self):
        _, records = iw.ingest_workbook(self.make_workbook())
        self.assertEqual(records[0]["extra_fields"]["investment"], "moderate")
        self.assertEqual(records[0]["extra_fields"]["structure"], "retrospective")

    def test_family_from_type_number(self):
        self.assertEqual(iw.family_for_type(1), "choice")
        self.assertEqual(iw.family_for_type(6), "choice")
        self.assertEqual(iw.family_for_type(7), "refusal")
        self.assertEqual(iw.family_for_type(12), "refusal")

    def test_missing_scenarios_sheet_raises(self):
        path = self.dir / "CB_type9_x_vs_y.xlsx"
        write_xlsx(path, {"README": [["only sheet"]]})
        with self.assertRaises(KeyError):
            iw.ingest_workbook(path)

    def test_bad_filename_raises(self):
        path = self.make_workbook()
        renamed = self.dir / "notes.xlsx"
        renamed.write_bytes(path.read_bytes())
        with self.assertRaises(ValueError):
            iw.ingest_workbook(renamed)

    def test_text_is_byte_faithful(self):
        rows = scenario_rows()
        rows[0][8] = "Stem with trailing spaces.   "
        for r in rows[1:]:
            r[8] = rows[0][8]
        _, records = iw.ingest_workbook(
            self.make_workbook(rows=rows))
        self.assertTrue(all(r["stem"].endswith("   ") for r in records))

    def test_main_writes_jsonl_and_manifest(self):
        wb = self.make_workbook()
        out_dir = self.dir / "drafts"
        code = iw.main(["--workbooks", str(wb), "--out-dir", str(out_dir)])
        self.assertEqual(code, 0)
        out = out_dir / "type1_honesty_vs_care.jsonl"
        self.assertTrue(out.exists())
        records = [json.loads(l) for l in
                   out.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(records), 4)
        manifest = json.loads((out_dir / "ingest_manifest.json")
                              .read_text(encoding="utf-8"))
        entry = manifest["files"]["type1_honesty_vs_care.jsonl"]
        self.assertEqual(entry["n_records"], 4)
        self.assertEqual(entry["source_workbook"], wb.name)
        self.assertEqual(len(entry["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
