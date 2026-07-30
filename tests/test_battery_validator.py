"""Tests for src/battery/validate_battery.py — stdlib only, off-pod."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.battery import validate_battery as vb


BLOCKLISTS = {
    "global": ["conflict", "torn", "value", "values"],
    "per_value": {
        "honesty": ["honest", "honesty", "truthful"],
        "care": [],
        "mercy": ["mercy", "merciful"],
        "desert": ["deserve", "deserves"],
    },
    "pending_researcher": {"care": "tbd"},
}


def make_cell(sid="CB-hc-S1", cond="agree_A", **over):
    rec = {
        "schema_version": "battery_draft_v1",
        "type_id": "type1_honesty_vs_care",
        "type_num": 1,
        "family": "choice",
        "scenario_id": sid,
        "title": "T",
        "condition": cond,
        "condition_label": "label",
        "stem": "My friend gave a toast at a wedding.",
        "option_A": "Tell her it dragged.",
        "option_B": "Tell her it landed.",
        "value_A": "honesty",
        "value_B": "care",
        "shared_opposition_text": ("It dragged badly."
                                   if cond.startswith("oppose") else ""),
        "condition_insert": "She asked me directly what I thought.",
        "expected_pick": "A",
        "design_note": "honesty note — notes may name values",
        "extra_fields": {},
        "metadata": {"reviewer_verdict": "", "reviewer_comments": "",
                     "source": {"workbook": "w.xlsx", "workbook_sha256": "0",
                                "sheet": "Scenarios", "row": 2,
                                "shared_text_header": "shared_opposition_text"}},
    }
    rec.update(over)
    return rec


def make_scenario(sid="CB-hc-S1"):
    return [make_cell(sid, c) for c in
            ("agree_A", "agree_B", "oppose_tip_A", "oppose_tip_B")]


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.blocklists = self.dir / "blocklists.json"
        self.blocklists.write_text(json.dumps(BLOCKLISTS), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_validator(self, records):
        draft = self.dir / "type1_honesty_vs_care.jsonl"
        draft.write_text("".join(json.dumps(r) + "\n" for r in records),
                         encoding="utf-8")
        report = self.dir / "report.md"
        code = vb.main([str(draft), "--blocklists", str(self.blocklists),
                        "--report", str(report)])
        return code, report.read_text(encoding="utf-8")

    def test_clean_scenario_passes(self):
        code, report = self.run_validator(make_scenario())
        self.assertEqual(code, 0)
        self.assertIn("PASS", report)

    def test_design_note_not_leakage_checked(self):
        cells = make_scenario()
        for c in cells:
            c["design_note"] = "honesty vs care, conflict tipped"
        code, _ = self.run_validator(cells)
        self.assertEqual(code, 0)

    def test_global_blocklist_hit_blocks(self):
        cells = make_scenario()
        cells[0]["stem"] = "A story about conflict at a wedding."
        for c in cells:
            c["stem"] = cells[0]["stem"]  # keep stems consistent
        code, report = self.run_validator(cells)
        self.assertEqual(code, 1)
        self.assertIn("a.lexeme", report)
        self.assertIn("'conflict'", report)

    def test_per_value_blocklist_hit_blocks(self):
        cells = make_scenario()
        cells[2]["condition_insert"] = "She wants a truthful answer."
        code, report = self.run_validator(cells)
        self.assertEqual(code, 1)
        self.assertIn("'truthful'", report)

    def test_whole_word_no_substring_match(self):
        cells = make_scenario()
        # 'valuable' contains 'value'; whole-word matching must NOT flag it
        cells[0]["condition_insert"] = "It was a valuable evening."
        code, _ = self.run_validator(cells)
        self.assertEqual(code, 0)

    def test_case_insensitive_match(self):
        cells = make_scenario()
        cells[1]["condition_insert"] = "TORN paper covered the floor."
        code, report = self.run_validator(cells)
        self.assertEqual(code, 1)
        self.assertIn("'torn'", report)

    def test_shared_text_mismatch_blocks(self):
        cells = make_scenario()
        cells[3]["shared_opposition_text"] = "It dragged badly.  "  # trailing bytes
        code, report = self.run_validator(cells)
        self.assertEqual(code, 1)
        self.assertIn("b.shared_text", report)

    def test_stem_mismatch_blocks(self):
        cells = make_scenario()
        cells[2]["stem"] = cells[2]["stem"] + " Extra sentence."
        code, report = self.run_validator(cells)
        self.assertEqual(code, 1)
        self.assertIn("c.stem", report)

    def test_missing_cell_blocks(self):
        code, report = self.run_validator(make_scenario()[:3])
        self.assertEqual(code, 1)
        self.assertIn("d.structure", report)

    def test_duplicate_cell_blocks(self):
        cells = make_scenario() + [make_cell(cond="agree_A")]
        code, report = self.run_validator(cells)
        self.assertEqual(code, 1)
        self.assertIn("duplicate", report)

    def test_duplicate_options_block(self):
        cells = make_scenario()
        for c in cells:
            c["option_B"] = c["option_A"]
        code, report = self.run_validator(cells)
        self.assertEqual(code, 1)
        self.assertIn("duplicate options", report)

    def test_bad_expected_pick_blocks(self):
        cells = make_scenario()
        cells[0]["expected_pick"] = "C"
        code, report = self.run_validator(cells)
        self.assertEqual(code, 1)
        self.assertIn("expected_pick", report)

    def test_length_flag_is_non_blocking(self):
        cells = make_scenario()
        cells[0]["condition_insert"] = " ".join(["word"] * 60)
        code, report = self.run_validator(cells)
        self.assertEqual(code, 0)
        self.assertIn("Length flags", report)

    def test_empty_pending_blocklist_flags_researcher(self):
        code, report = self.run_validator(make_scenario())
        self.assertEqual(code, 0)
        self.assertIn("Researcher decisions needed", report)
        self.assertIn("'care'", report)

    @staticmethod
    def make_control(cid="TC-1", **over):
        rec = {"schema_version": "battery_draft_v1",
               "record_type": "topical_control",
               "type_id": "type1_honesty_vs_care", "type_num": 1,
               "family": "choice", "type_values": ["honesty", "care"],
               "control_id": cid, "matched_domain": "health",
               "stem": "A stem about clinics.",
               "option_A": "The closer one.", "option_B": "The quicker one.",
               "note": "honesty may appear in notes",
               "metadata": {"reviewer_verdict": "", "reviewer_comments": "",
                            "source": {"workbook": "w.xlsx",
                                       "workbook_sha256": "0",
                                       "sheet": "Topical_controls", "row": 2}}}
        rec.update(over)
        return rec

    def test_clean_controls_pass(self):
        code, report = self.run_validator([self.make_control(),
                                           self.make_control("TC-2")])
        self.assertEqual(code, 0)
        self.assertIn("2 topical controls", report)

    def test_control_blocklist_hit_blocks(self):
        ctrl = self.make_control(stem="An honest answer about clinics.")
        code, report = self.run_validator([ctrl])
        self.assertEqual(code, 1)
        self.assertIn("'honest'", report)

    def test_control_note_not_leakage_checked(self):
        code, _ = self.run_validator([self.make_control()])
        self.assertEqual(code, 0)  # note contains 'honesty'; not stimulus

    def test_duplicate_control_id_blocks(self):
        code, report = self.run_validator([self.make_control(),
                                           self.make_control()])
        self.assertEqual(code, 1)
        self.assertIn("duplicate control_id", report)

    def test_agree_cell_with_shared_text_warns_not_blocks(self):
        cells = make_scenario()
        cells[0]["shared_opposition_text"] = "Should be empty here."
        code, report = self.run_validator(cells)
        self.assertEqual(code, 0)
        self.assertIn("Warnings", report)


if __name__ == "__main__":
    unittest.main()
