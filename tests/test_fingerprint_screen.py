"""Tests for src/analysis/fingerprint_screen.py — numpy-only, off-pod.

The activation loader (torch) is not exercised here; math and eligibility
logic take plain dicts/ndarrays.
"""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis import fingerprint_screen as fs


def gen_row(probe_id, role, variant, mass, block="main", base="1"):
    return {"prompt_key": f"{probe_id}::{role}::{variant}",
            "probe_id": probe_id, "variant": variant, "role": role,
            "block": block, "is_base_cell": base,
            "mass_combined": str(mass)}


def cell_rows(probe_id, role, m_neutral=0.6, m_value=0.6, **kw):
    return [gen_row(probe_id, role, "neutral", m_neutral, **kw),
            gen_row(probe_id, role, "value", m_value, **kw)]


class EligibilityTests(unittest.TestCase):
    PROBE_VALUES = {"PT2-honesty-C1": "honesty", "PT2-honesty-C2": "honesty",
                    "PT2-care-C1": "care"}

    def test_basic_eligibility(self):
        rows = cell_rows("PT2-honesty-C1", "friend")
        cells, audit = fs.eligible_cells(rows, self.PROBE_VALUES, set())
        self.assertIn(("PT2-honesty-C1", "friend"), cells["honesty"])
        self.assertEqual(
            cells["honesty"][("PT2-honesty-C1", "friend")]["neutral"],
            "PT2-honesty-C1::friend::neutral")

    def test_mass_floor_excludes(self):
        rows = cell_rows("PT2-honesty-C1", "friend", m_value=0.19)
        cells, audit = fs.eligible_cells(rows, self.PROBE_VALUES, set())
        self.assertNotIn("honesty", cells)
        self.assertFalse(audit[0]["eligible"])
        self.assertAlmostEqual(audit[0]["mass_min"], 0.19)

    def test_mass_floor_boundary_inclusive(self):
        rows = cell_rows("PT2-honesty-C1", "friend", m_value=0.20)
        cells, _ = fs.eligible_cells(rows, self.PROBE_VALUES, set())
        self.assertIn("honesty", cells)

    def test_c3_excludes(self):
        rows = cell_rows("PT2-honesty-C1", "friend")
        cells, audit = fs.eligible_cells(
            rows, self.PROBE_VALUES, {("PT2-honesty-C1", "friend")})
        self.assertNotIn("honesty", cells)
        self.assertTrue(audit[0]["c3_dropped"])

    def test_incomplete_excludes(self):
        rows = [gen_row("PT2-honesty-C1", "friend", "neutral", 0.6)]
        cells, audit = fs.eligible_cells(rows, self.PROBE_VALUES, set())
        self.assertNotIn("honesty", cells)
        self.assertFalse(audit[0]["complete"])

    def test_non_main_and_non_base_excluded(self):
        rows = (cell_rows("PT2-honesty-C1", "friend", block="null_comparison")
                + cell_rows("PT2-honesty-C2", "friend", base="0"))
        cells, _ = fs.eligible_cells(rows, self.PROBE_VALUES, set())
        self.assertEqual(dict(cells), {})


class MathTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(23)
        self.L, self.d = 3, 8
        # two pairs x two roles; value acts displaced by a fixed direction
        self.direction = rng.normal(size=(self.L, self.d))
        self.acts = {}
        self.cells = {}
        for pid in ("P1", "P2"):
            for role in ("friend", "boss"):
                base = rng.normal(size=(self.L, self.d))
                self.acts[f"{pid}::{role}::neutral"] = base
                self.acts[f"{pid}::{role}::value"] = base + self.direction
                self.cells[(pid, role)] = {
                    "neutral": f"{pid}::{role}::neutral",
                    "value": f"{pid}::{role}::value"}

    def test_fingerprint_recovers_direction(self):
        fp = fs.fingerprint(self.acts, self.cells)
        np.testing.assert_allclose(fp, self.direction, atol=1e-12)

    def test_pair_subset_restricts(self):
        fp = fs.fingerprint(self.acts, self.cells, {"P1"})
        np.testing.assert_allclose(fp, self.direction, atol=1e-12)

    def test_unit_normalize(self):
        fp = fs.unit_normalize(self.direction)
        np.testing.assert_allclose(np.linalg.norm(fp, axis=1), 1.0)
        zero = fs.unit_normalize(np.zeros((2, 4)))
        self.assertTrue((zero == 0).all())

    def test_cosine_per_layer(self):
        a = np.array([[1.0, 0.0], [1.0, 0.0]])
        b = np.array([[1.0, 0.0], [0.0, 1.0]])
        np.testing.assert_allclose(fs.cosine_per_layer(a, b), [1.0, 0.0])

    def test_balanced_splits_counts(self):
        self.assertEqual(len(fs.balanced_splits(["a", "b"])), 1)
        self.assertEqual(len(fs.balanced_splits(["a", "b", "c"])), 3)
        # n=4: C(4,2)=6, halved to 3 by anchoring the first element
        self.assertEqual(len(fs.balanced_splits(list("abcd"))), 3)
        self.assertEqual(fs.balanced_splits(["only"]), [])

    def test_balanced_splits_are_partitions(self):
        for half_a, half_b in fs.balanced_splits(list("abcde")):
            self.assertEqual(half_a | half_b, set("abcde"))
            self.assertEqual(half_a & half_b, set())

    def test_split_half_reliability_perfect_signal(self):
        rel, n_pairs, n_splits = fs.split_half_reliability(self.acts, self.cells)
        self.assertEqual(n_pairs, 2)
        self.assertEqual(n_splits, 1)
        np.testing.assert_allclose(rel, 1.0, atol=1e-9)

    def test_split_half_reliability_single_pair_not_estimable(self):
        cells = {k: v for k, v in self.cells.items() if k[0] == "P1"}
        rel, n_pairs, n_splits = fs.split_half_reliability(self.acts, cells)
        self.assertIsNone(rel)
        self.assertEqual((n_pairs, n_splits), (1, 0))

    def test_noise_reliability_low(self):
        rng = np.random.default_rng(7)
        acts, cells = {}, {}
        for pid in ("P1", "P2", "P3", "P4"):
            for role in ("r1", "r2"):
                acts[f"{pid}::{role}::neutral"] = rng.normal(size=(2, 64))
                acts[f"{pid}::{role}::value"] = rng.normal(size=(2, 64))
                cells[(pid, role)] = {"neutral": f"{pid}::{role}::neutral",
                                      "value": f"{pid}::{role}::value"}
        rel, _, _ = fs.split_half_reliability(acts, cells)
        self.assertTrue((np.abs(rel) < 0.9).all())


class BatterySlateTests(unittest.TestCase):
    def test_twelve_types_eleven_unique_pairs(self):
        pairs = fs.battery_pairs()
        self.assertEqual(len(fs.BATTERY_TYPES), 12)
        self.assertEqual(len(pairs), 11)  # privacy-care appears twice (2, 10)
        self.assertEqual(pairs[frozenset(("privacy", "care"))], [2, 10])

    def test_authority_integrity_never_meet(self):
        self.assertNotIn(frozenset(("authority", "integrity")),
                         fs.battery_pairs())


if __name__ == "__main__":
    unittest.main()
