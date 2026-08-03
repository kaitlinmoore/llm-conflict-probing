"""Tests for the stimulus-similarity exhibit — numpy only, no encoders."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.analysis import stimulus_similarity as ss
from src.analysis import extract_value_anchors as eva


def unit(uid, kind="cell", type_id="type1_a_vs_b", scen="S1", cond="agree_A"):
    return {"id": uid, "kind": kind, "type_id": type_id, "scenario_id": scen,
            "condition": cond, "family": "choice", "text": "t"}


class CellTextTests(unittest.TestCase):
    REC = {"stem": "Stem here.", "shared_opposition_text": "Shared conflict.",
           "condition_insert": "Tipping sentence."}

    def test_full_includes_shared_text(self):
        t = ss.cell_text(self.REC, "full")
        self.assertIn("Shared conflict.", t)
        self.assertTrue(t.startswith("Stem here."))
        self.assertTrue(t.endswith("Tipping sentence."))

    def test_stem_insert_omits_shared_text(self):
        t = ss.cell_text(self.REC, "stem_insert")
        self.assertNotIn("Shared conflict.", t)

    def test_agreement_cell_has_no_shared_text(self):
        rec = dict(self.REC, shared_opposition_text="")
        self.assertEqual(ss.cell_text(rec, "full"),
                         "Stem here. Tipping sentence.")


class SimilarityMathTests(unittest.TestCase):
    def setUp(self):
        # two tight clusters, orthogonal to each other
        a = np.tile(np.array([1.0, 0.0, 0.0]), (3, 1))
        b = np.tile(np.array([0.0, 1.0, 0.0]), (3, 1))
        self.emb = np.vstack([a, b]).astype(np.float32)
        self.units = ([unit(f"a{i}", type_id="type1_a_vs_b") for i in range(3)]
                      + [unit(f"b{i}", type_id="type2_c_vs_d") for i in range(3)])

    def test_within_group_similarity_is_one(self):
        self.assertAlmostEqual(
            ss.mean_pair_similarity(self.emb, [0, 1, 2], [0, 1, 2]), 1.0, 5)

    def test_between_orthogonal_groups_is_zero(self):
        self.assertAlmostEqual(
            ss.mean_pair_similarity(self.emb, [0, 1, 2], [3, 4, 5]), 0.0, 5)

    def test_single_item_group_is_nan(self):
        self.assertTrue(np.isnan(ss.mean_pair_similarity(self.emb, [0], [0])))

    def test_type_matrix_shape_and_symmetry(self):
        types, m = ss.type_matrix(self.units, self.emb)
        self.assertEqual(types, ["type1_a_vs_b", "type2_c_vs_d"])
        self.assertEqual(m.shape, (2, 2))
        self.assertAlmostEqual(m[0, 1], m[1, 0], 6)

    def test_type_matrix_restrict(self):
        units = [unit("a", cond="oppose_tip_A"), unit("b", cond="agree_A"),
                 unit("c", cond="oppose_tip_B")]
        emb = np.eye(3, dtype=np.float32)
        types, m = ss.type_matrix(
            units, emb, restrict=lambda u: u["condition"].startswith("oppose"))
        self.assertEqual(types, ["type1_a_vs_b"])

    def test_offdiag_values(self):
        types, m = ss.type_matrix(self.units, self.emb)
        od = ss.offdiag_values(types, m)
        self.assertEqual(len(od), 1)


class RelativeAffinityTests(unittest.TestCase):
    @staticmethod
    def twelve_types(odd_one="type12_x_vs_y", odd_value=0.50, base=0.10):
        keys = ["honesty", "care", "harm_avoidance"]
        per_type, poles = {}, {}
        for i in range(1, 13):
            t = f"type{i}_x_vs_y" if i != 12 else odd_one
            per_type[t] = {"honesty": .1, "care": .1,
                           "harm_avoidance": odd_value if t == odd_one else base}
            poles[t] = ["tradition", "autonomy"]        # never harm_avoidance
        return keys, per_type, poles

    def test_flags_only_the_outlying_type(self):
        keys, per_type, poles = self.twelve_types()
        rows = ss.relative_value_affinity(per_type, keys, poles)
        flagged = [r for r in rows if r["flagged"]]
        self.assertEqual(len(flagged), 1)
        self.assertEqual(flagged[0]["type_id"], "type12_x_vs_y")
        self.assertEqual(flagged[0]["value"], "harm_avoidance")

    def test_no_flag_when_nothing_stands_out(self):
        keys, per_type, poles = self.twelve_types(odd_value=0.10)
        rows = ss.relative_value_affinity(per_type, keys, poles)
        self.assertFalse([r for r in rows if r["flagged"]])

    def test_z_ceiling_is_bounded_by_type_count(self):
        """(n-1)/sqrt(n): with 12 types max z ≈ 3.18, so z >= 2.0 is a real
        but not extreme bar; with few types z >= 2.0 is unreachable. This
        bound is documented in the report."""
        keys, per_type, poles = self.twelve_types(odd_value=99.0)
        rows = ss.relative_value_affinity(per_type, keys, poles)
        top = max(r["z_within_value"] for r in rows)
        n = len(per_type)
        self.assertLessEqual(top, (n - 1) / np.sqrt(n) + 1e-6)

    def test_own_pole_never_flagged(self):
        keys = ["honesty", "care"]
        per_type = {"type1_honesty_vs_care": {"honesty": .9, "care": .1},
                    "type3_mercy_vs_desert": {"honesty": .1, "care": .1},
                    "type5_tradition_vs_autonomy": {"honesty": .1, "care": .1}}
        poles = {"type1_honesty_vs_care": ["honesty", "care"],
                 "type3_mercy_vs_desert": ["mercy", "desert"],
                 "type5_tradition_vs_autonomy": ["tradition", "autonomy"]}
        rows = ss.relative_value_affinity(per_type, keys, poles)
        self.assertFalse([r for r in rows if r["flagged"]])


class PairAnalysisTests(unittest.TestCase):
    def test_minimal_pair_tightness(self):
        units = [unit("a", cond="oppose_tip_A"), unit("b", cond="oppose_tip_B")]
        emb = np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float32)
        rows = ss.minimal_pair_tightness(units, emb)
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["distance"], 0.0, 6)

    def test_minimal_pair_needs_both_siblings(self):
        units = [unit("a", cond="oppose_tip_A")]
        self.assertEqual(ss.minimal_pair_tightness(units, np.eye(1)), [])

    def test_tip_symmetry_zero_when_balanced(self):
        units = [unit("a", cond="oppose_tip_A"), unit("b", cond="oppose_tip_B")]
        emb = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0]], dtype=np.float32)
        rows = ss.tip_symmetry(units, emb, {"type1_a_vs_b:S1": 2})
        self.assertAlmostEqual(rows[0]["asymmetry"], 0.0, 6)

    def test_tip_symmetry_detects_imbalance(self):
        units = [unit("a", cond="oppose_tip_A"), unit("b", cond="oppose_tip_B")]
        emb = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0]], dtype=np.float32)
        rows = ss.tip_symmetry(units, emb, {"type1_a_vs_b:S1": 2})
        self.assertAlmostEqual(rows[0]["asymmetry"], 1.0, 6)

    def test_control_placement_margin(self):
        units = [unit("c", kind="control", type_id="type1_a_vs_b"),
                 unit("x", type_id="type1_a_vs_b"),
                 unit("y", type_id="type2_c_vs_d")]
        emb = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
        rows = ss.control_placement(units, emb)
        self.assertAlmostEqual(rows[0]["sim_to_own_type"], 1.0, 5)
        self.assertAlmostEqual(rows[0]["sim_to_rest"], 0.0, 5)
        self.assertAlmostEqual(rows[0]["margin"], 1.0, 5)

    def test_outliers(self):
        rows = [{"v": x} for x in [1, 1, 1, 1, 1, 1, 1, 1, 10]]
        out, mu, sd = ss.outliers(rows, "v")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["v"], 10)

    def test_spearman_monotonic(self):
        a = np.array([1.0, 2, 3, 4, 5])
        b = np.array([10.0, 20, 30, 40, 50])
        self.assertAlmostEqual(ss.spearman(a, b), 1.0, 6)


class AnchorExtractionTests(unittest.TestCase):
    ANCHORS = REPO / "data" / "battery" / "value_anchors.json"

    def test_all_sixteen_roster_values_present(self):
        if not self.ANCHORS.exists():
            self.skipTest("anchors not extracted")
        blob = json.loads(self.ANCHORS.read_text(encoding="utf-8"))
        keys = {a["value"] for a in blob["anchors"]}
        self.assertEqual(keys, set(eva.VALUE_KEYS.values()))

    def test_anchor_text_is_full_definition_not_bare_word(self):
        if not self.ANCHORS.exists():
            self.skipTest("anchors not extracted")
        blob = json.loads(self.ANCHORS.read_text(encoding="utf-8"))
        for a in blob["anchors"]:
            self.assertGreater(len(a["anchor_text"].split()), 5, a["value"])
            # 14 verbatim; authority and mercy trimmed per researcher
            # ruling 2026-08-05 (pure deletions, recorded in provenance)
            if a["value"] in ("authority", "mercy"):
                self.assertFalse(a["provenance"]["verbatim"], a["value"])
                self.assertIn("2026-08-05", a["provenance"]["trimmed"])
            else:
                self.assertTrue(a["provenance"]["verbatim"], a["value"])

    def test_problem_anchors_trimmed_per_ruling(self):
        if not self.ANCHORS.exists():
            self.skipTest("anchors not extracted")
        blob = json.loads(self.ANCHORS.read_text(encoding="utf-8"))
        by = {a["value"]: a for a in blob["anchors"]}
        # ruled 2026-08-05: flagged non-semantic spans deleted, flags
        # resolved; the semantic definition text is intact
        self.assertNotIn("flag", by["authority"])
        self.assertNotIn("flag", by["mercy"])
        self.assertNotIn("probe design", by["authority"]["anchor_text"])
        self.assertNotIn("§6", by["mercy"]["anchor_text"])
        self.assertTrue(by["authority"]["anchor_text"].endswith(
            "evidence and expertise."))
        self.assertTrue(by["mercy"]["anchor_text"].endswith(
            "(remorse, prior record, proportionality)."))

    def test_certification_recorded(self):
        if not self.ANCHORS.exists():
            self.skipTest("anchors not extracted")
        blob = json.loads(self.ANCHORS.read_text(encoding="utf-8"))
        by = {a["value"]: a for a in blob["anchors"]}
        self.assertEqual(by["harm_avoidance"]["certification"], "certified")
        self.assertEqual(by["sanctity"]["certification"], "unenacted")


class NoLlamaTests(unittest.TestCase):
    def test_encoders_are_outside_the_llama_lineage(self):
        for spec in ss.ENCODERS.values():
            self.assertNotIn("llama", spec["name"].lower())
        self.assertEqual(len(ss.ENCODERS), 2)
        fams = {s["family"] for s in ss.ENCODERS.values()}
        self.assertEqual(len(fams), 2, "encoders must differ in family")


if __name__ == "__main__":
    unittest.main()
