"""Session-3 additions: refusal-family ingest/validation, name uniqueness,
cross-type lexeme tier, and the pending-edits script. Stdlib only."""

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.battery import ingest_workbook as iw
from src.battery import validate_battery as vb
from src.battery import apply_pending_edits as ape
from tests.test_ingest_workbook import write_xlsx

BLOCKLISTS = {
    "global": ["conflict", "torn"],
    "per_value": {"harm": ["danger", "risk"], "autonomy": ["autonomy"],
                  "desert": ["deserves"], "care": []},
    "discipline_only": {}, "pending_researcher": {},
}

REFUSAL_HEADERS = ["scenario_id", "title", "structure", "activity_domain",
                   "subject", "condition", "condition_label", "stem",
                   "shared_opposition_text", "condition_insert",
                   "expected_response", "design_note", "reviewer_verdict",
                   "reviewer_comments"]
REFUSAL_CONDS = ["agree_comply", "agree_refuse",
                 "oppose_tip_comply", "oppose_tip_refuse"]


def refusal_rows(sid="CB-hva-S1", shared="Shared opposition facts."):
    rows = []
    for cond in REFUSAL_CONDS:
        rows.append([sid, "The traverse", "assistance-request", "mountaineering",
                     "self", cond, f"label {cond}", "Stem text.",
                     shared if cond.startswith("oppose") else "",
                     f"Insert for {cond}.",
                     "comply" if cond.endswith("comply") else "refuse",
                     "note", "", ""])
    return rows


class RefusalIngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make(self, name="CB_type7_harm_vs_autonomy.xlsx", rows=None,
             headers=None, extra=None):
        sheets = {"README": [["r"]],
                  "Scenarios": [headers or REFUSAL_HEADERS] + (rows or refusal_rows())}
        sheets.update(extra or {})
        p = self.dir / name
        write_xlsx(p, sheets)
        return p

    def test_refusal_family_ingests(self):
        tid, recs = iw.ingest_workbook(self.make())
        self.assertEqual(tid, "type7_harm_vs_autonomy")
        self.assertEqual(len(recs), 4)
        self.assertEqual({r["condition"] for r in recs}, set(REFUSAL_CONDS))
        self.assertEqual(recs[0]["family"], "refusal")
        self.assertEqual(recs[0]["expected_response"], "comply")
        self.assertEqual(recs[0]["option_A"], "")
        self.assertEqual(recs[0]["type_values"], ["harm", "autonomy"])

    def test_declared_design_vars_survive_as_metadata(self):
        _, recs = iw.ingest_workbook(self.make())
        self.assertEqual(recs[0]["extra_fields"]["subject"], "self")
        self.assertEqual(recs[0]["extra_fields"]["activity_domain"],
                         "mountaineering")

    def test_refusal_sheet_with_options_raises(self):
        headers = REFUSAL_HEADERS + ["option_A_harm"]
        rows = [r + ["should not be here"] for r in refusal_rows()]
        with self.assertRaises(ValueError):
            iw.ingest_workbook(self.make(headers=headers, rows=rows))

    def test_choice_type_missing_options_raises(self):
        with self.assertRaises(ValueError):
            iw.ingest_workbook(self.make(name="CB_type1_honesty_vs_care.xlsx"))

    def test_annotated_control_stem_header_normalized(self):
        ctrl_headers = ["control_id", "matched_domain",
                        "stem (assistance ask, no condition)", "note",
                        "reviewer_verdict", "reviewer_comments"]
        p = self.make(extra={"Topical_controls": [
            ctrl_headers, ["TC-1", "logistics", "A benign ask.", "n", "", ""]]})
        _, controls = iw.ingest_controls(p)
        self.assertEqual(len(controls), 1)
        self.assertEqual(controls[0]["stem"], "A benign ask.")
        self.assertEqual(controls[0]["metadata"]["source"]["stem_header"],
                         "stem (assistance ask, no condition)")


class RefusalValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.bl = self.dir / "bl.json"
        self.bl.write_text(json.dumps(BLOCKLISTS), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def cell(self, cond, sid="CB-hva-S1", **over):
        rec = {"schema_version": "battery_draft_v1", "record_type": "battery_cell",
               "type_id": "type7_harm_vs_autonomy", "type_num": 7,
               "family": "refusal", "type_values": ["harm", "autonomy"],
               "scenario_id": sid, "title": "T", "condition": cond,
               "condition_label": "l", "stem": "Stem text.",
               "option_A": "", "option_B": "", "value_A": "", "value_B": "",
               "shared_opposition_text": ("Shared." if cond.startswith("oppose") else ""),
               "condition_insert": f"Insert {cond}.",
               "expected_pick": "",
               "expected_response": "comply" if cond.endswith("comply") else "refuse",
               "design_note": "", "extra_fields": {}, "metadata": {}}
        rec.update(over)
        return rec

    def run_v(self, recs, name="type7_harm_vs_autonomy.jsonl"):
        d = self.dir / name
        d.write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
        rep = self.dir / "rep.md"
        code = vb.main([str(d), "--blocklists", str(self.bl), "--report", str(rep)])
        return code, rep.read_text(encoding="utf-8")

    def test_clean_refusal_scenario_passes(self):
        code, rep = self.run_v([self.cell(c) for c in REFUSAL_CONDS])
        self.assertEqual(code, 0)
        self.assertIn("refusal family", rep)

    def test_choice_conditions_rejected_in_refusal_file(self):
        cells = [self.cell(c) for c in REFUSAL_CONDS]
        cells[0]["condition"] = "agree_A"
        code, rep = self.run_v(cells)
        self.assertEqual(code, 1)
        self.assertIn("d.structure", rep)

    def test_bad_expected_response_blocks(self):
        cells = [self.cell(c) for c in REFUSAL_CONDS]
        cells[1]["expected_response"] = "maybe"
        code, rep = self.run_v(cells)
        self.assertEqual(code, 1)
        self.assertIn("expected_response", rep)

    def test_missing_condition_blocks(self):
        code, rep = self.run_v([self.cell(c) for c in REFUSAL_CONDS[:3]])
        self.assertEqual(code, 1)
        self.assertIn("expected exactly 4 cells", rep)

    def test_shared_text_mismatch_blocks_refusal_family(self):
        cells = [self.cell(c) for c in REFUSAL_CONDS]
        cells[3]["shared_opposition_text"] = "Shared. "
        code, rep = self.run_v(cells)
        self.assertEqual(code, 1)
        self.assertIn("b.shared_text", rep)

    def test_own_pole_lexeme_blocks(self):
        cells = [self.cell(c) for c in REFUSAL_CONDS]
        cells[0]["condition_insert"] = "There is real danger here."
        code, rep = self.run_v(cells)
        self.assertEqual(code, 1)
        self.assertIn("'danger'", rep)

    def test_other_type_lexeme_is_flag_not_block(self):
        cells = [self.cell(c) for c in REFUSAL_CONDS]
        for c in cells:
            c["stem"] = "She deserves the full celebration."
        code, rep = self.run_v(cells)
        self.assertEqual(code, 0)
        self.assertIn("Cross-type lexeme flags", rep)
        self.assertIn("'deserves'", rep)

    def test_refusal_cell_with_options_blocks(self):
        cells = [self.cell(c) for c in REFUSAL_CONDS]
        cells[0]["option_A"] = "An option"
        code, rep = self.run_v(cells)
        self.assertEqual(code, 1)
        self.assertIn("carries option text", rep)


class NameCheckTests(unittest.TestCase):
    def test_cross_type_name_flagged(self):
        f = vb.Findings()
        recs = [
            {"type_id": "type1_x_vs_y", "scenario_id": "S1",
             "stem": "My friend Dana called me about it."},
            {"type_id": "type4_a_vs_b", "scenario_id": "S2",
             "stem": "Later Dana mentioned the same thing."},
        ]
        vb.cross_type_name_check(recs, f)
        self.assertTrue(any("Dana" in x for x in f.name_flags))

    def test_same_type_reuse_not_flagged(self):
        f = vb.Findings()
        recs = [{"type_id": "type1_x_vs_y", "scenario_id": "S1",
                 "stem": "My friend Dana called."},
                {"type_id": "type1_x_vs_y", "scenario_id": "S1",
                 "stem": "My friend Dana waited."}]
        vb.cross_type_name_check(recs, f)
        self.assertFalse([x for x in f.name_flags if "appears in" in x])

    def test_near_collision_flagged(self):
        f = vb.Findings()
        recs = [{"type_id": "type4_a_vs_b", "scenario_id": "S1",
                 "stem": "My cousin Priya asked."},
                {"type_id": "type10_c_vs_d", "scenario_id": "S2",
                 "stem": "My cousin Priyanka asked."}]
        vb.cross_type_name_check(recs, f)
        self.assertTrue(any("near-collision" in x for x in f.name_flags))


class PendingEditsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        write_xlsx(self.dir / "CB_type1_honesty_vs_care.xlsx",
                   {"Scenarios": [["scenario_id", "stem"],
                                  ["S1", "she really cared about getting it right today"]]})

    def tearDown(self):
        self.tmp.cleanup()

    def test_dry_run_writes_nothing(self):
        before = (self.dir / "CB_type1_honesty_vs_care.xlsx").read_bytes()
        code = ape.main(["--workbook-dir", str(self.dir)])
        self.assertEqual(code, 0)
        self.assertEqual((self.dir / "CB_type1_honesty_vs_care.xlsx").read_bytes(),
                         before)

    def test_apply_then_idempotent(self):
        self.assertEqual(ape.main(["--workbook-dir", str(self.dir), "--apply"]), 0)
        parts = ape.text_parts(self.dir / "CB_type1_honesty_vs_care.xlsx")
        joined = " ".join(parts.values())
        self.assertIn("wanted it exactly right", joined)
        self.assertNotIn("really cared about getting it right", joined)
        self.assertTrue(list(self.dir.glob("*.bak-*")))
        # second run is a no-op
        self.assertEqual(ape.main(["--workbook-dir", str(self.dir), "--apply"]), 0)

    def test_refuses_while_excel_lock_present(self):
        (self.dir / "~$CB_type1_honesty_vs_care.xlsx").write_text("lock")
        self.assertEqual(ape.main(["--workbook-dir", str(self.dir), "--apply"]), 2)
        parts = ape.text_parts(self.dir / "CB_type1_honesty_vs_care.xlsx")
        self.assertIn("really cared", " ".join(parts.values()))


if __name__ == "__main__":
    unittest.main()
