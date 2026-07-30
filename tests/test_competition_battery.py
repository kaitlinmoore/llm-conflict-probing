"""Tests for the competition battery draft (Task 4) — stdlib only."""

import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.comparators import build_competition_battery as cb

DRAFT = REPO / "data" / "comparators" / "competition_battery_draft.jsonl"
BLOCKLISTS = REPO / "data" / "battery" / "lexeme_blocklists.json"


class BuilderTests(unittest.TestCase):
    def test_counts_and_balance(self):
        self.assertEqual(len(cb.TORN), 40)
        self.assertEqual(len(cb.EASY), 40)

    def test_every_item_has_two_distinct_nonempty_options(self):
        for kind, items in (("torn", cb.TORN), ("easy", cb.EASY)):
            for item in items:
                body, a, b, domain = item[:4]
                self.assertTrue(body.strip(), kind)
                self.assertTrue(a.strip() and b.strip(), kind)
                self.assertNotEqual(a, b)
                self.assertTrue(domain.strip())

    def test_screen_detects_global_blocklist(self):
        blocklist = cb.load_global_blocklist(BLOCKLISTS)
        blocking, _ = cb.screen("This is a conflict of some kind.", blocklist)
        self.assertIn("conflict", blocking)
        blocking, _ = cb.screen("A steady practical tradeoff.", blocklist)
        self.assertEqual(blocking, [])

    def test_screen_detects_adjacency(self):
        blocklist = cb.load_global_blocklist(BLOCKLISTS)
        _, flags = cb.screen("She asked me to keep it secret.", blocklist)
        self.assertTrue(any(f.startswith("privacy:") for f in flags))

    def test_build_marks_authoring_doubt(self):
        blocklist = cb.load_global_blocklist(BLOCKLISTS)
        items = [("Situation body.", "A.", "B.", "dom", "why I am unsure")]
        out, problems = cb.build("easy", items, blocklist)
        self.assertEqual(problems, [])
        self.assertEqual(out[0]["review_flag"],
                         ["authoring_doubt:why I am unsure"])


class DraftFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DRAFT.exists():
            raise unittest.SkipTest("draft not built")
        cls.recs = [json.loads(l) for l in
                    DRAFT.read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_80_items_40_each(self):
        self.assertEqual(len(self.recs), 80)
        by = {}
        for r in self.recs:
            by[r["condition"]] = by.get(r["condition"], 0) + 1
        self.assertEqual(by, {"torn": 40, "easy": 40})

    def test_ids_unique_and_stems_unique(self):
        self.assertEqual(len({r["item_id"] for r in self.recs}), 80)
        self.assertEqual(len({r["stem"] for r in self.recs}), 80)

    def test_format_matched_question(self):
        for r in self.recs:
            self.assertTrue(r["stem"].endswith("Which should I choose?"),
                            r["item_id"])

    def test_global_blocklist_clean(self):
        data = json.loads(BLOCKLISTS.read_text(encoding="utf-8"))
        pats = [(lx, re.compile(rf"\b{re.escape(lx)}\b", re.I))
                for lx in data["global"]]
        for r in self.recs:
            text = " ".join([r["stem"], r["option_A"], r["option_B"]])
            for lx, pat in pats:
                self.assertIsNone(pat.search(text),
                                  f"{r['item_id']} contains {lx!r}")

    def test_domain_spread(self):
        domains = {r["domain"] for r in self.recs}
        self.assertGreaterEqual(len(domains), 30)
        # no single domain dominates
        counts = {}
        for r in self.recs:
            counts[r["domain"]] = counts.get(r["domain"], 0) + 1
        self.assertLessEqual(max(counts.values()), 6)

    def test_flags_are_present_and_shaped(self):
        flagged = [r for r in self.recs if r["review_flag"]]
        self.assertTrue(flagged, "expected authored review flags")
        for r in flagged:
            self.assertIsInstance(r["review_flag"], list)

    def test_no_second_person_or_moral_framing_markers(self):
        """Cheap guard: items are first-person practical decisions."""
        banned = ["should I tell", "the right thing", "morally", "ought to"]
        for r in self.recs:
            low = r["stem"].lower()
            for b in banned:
                self.assertNotIn(b, low, r["item_id"])


if __name__ == "__main__":
    unittest.main()
