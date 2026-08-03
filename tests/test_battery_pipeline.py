"""Pipeline tests per analysis_pipeline_brief.md §Tests: refusal-loader
blindness (negative), estimator identity, permutation reproducibility,
tier separation (verified refuses pre-lock), smoke end-to-end.
Needs numpy/torch (skips off-stack)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    import numpy as np
    import torch  # noqa: F401
    HAVE_STACK = True
except ImportError:
    HAVE_STACK = False

if HAVE_STACK:
    from src.analysis import battery_pipeline as bp
    from src.analysis import label_lock as ll
    from src.analysis import make_smoke_shard as sm


@unittest.skipUnless(HAVE_STACK, "numpy/torch not installed")
class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.run_dir = Path(cls.tmp.name) / "smoke"
        cls.cmp_dir = cls.run_dir / "comparator"
        sm.make(cls.run_dir, cls.cmp_dir)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_selection_rejects_refusal_capture(self):
        ref = bp.load_refusal_capture(self.run_dir)
        with self.assertRaises(TypeError):
            bp.select_layer(ref)

    def test_selection_rejects_smuggled_refusal_rows(self):
        cap = bp.load_choice_capture(self.run_dir)
        ref = bp.load_refusal_capture(self.run_dir)
        cap.rows.append(ref.rows[0])
        cap.acts[ref.rows[0]["prompt_key"]] = \
            ref.acts[ref.rows[0]["prompt_key"]]
        with self.assertRaises(ValueError):
            bp.select_layer(cap)

    def test_estimator_identity_every_fit_routes_through_diff_of_means(self):
        calls = []
        orig = bp.diff_of_means

        def spy(a, b):
            calls.append(1)
            return orig(a, b)

        bp.diff_of_means = spy
        try:
            cap = bp.load_choice_capture(self.run_dir)
            comp = bp.load_competition_capture(self.run_dir)
            bp.fit_conflict_direction(cap, sm.PLANT_LAYER)
            n1 = len(calls)
            bp.fit_refusal_direction(self.cmp_dir, sm.PLANT_LAYER)
            n2 = len(calls)
            bp.fit_difficulty_direction(comp, sm.PLANT_LAYER)
            n3 = len(calls)
        finally:
            bp.diff_of_means = orig
        self.assertTrue(n1 >= 1 and n2 > n1 and n3 > n2,
                        "every construct fit must call diff_of_means")

    def test_gate_ratified_default_and_stricter_disclosure(self):
        cap = bp.load_choice_capture(self.run_dir)
        layer, curve, meta = bp.select_layer(cap)
        self.assertIn("ratified 2026-08-05", meta["gate"])
        self.assertNotIn("OPEN", meta["gate"])
        self.assertTrue(all("gate_pass" in r for r in curve))
        # stricter criterion: selection re-runs, BOTH results reported
        layer2, curve2, meta2 = bp.select_layer(cap, gate_threshold=0.99)
        self.assertEqual(layer2, layer)  # default-gate selection unchanged
        self.assertIn("stricter_criterion", meta2)
        self.assertIn("selected_layer", meta2["stricter_criterion"])
        self.assertTrue(all("gate_pass_stricter" in r for r in curve2))

    def test_permutation_null_reproducible_under_fixed_seed(self):
        cap = bp.load_choice_capture(self.run_dir)
        a = bp.analysis_existence(cap, sm.PLANT_LAYER, seed=99)
        b = bp.analysis_existence(cap, sm.PLANT_LAYER, seed=99)
        self.assertEqual(a, b)
        c = bp.analysis_existence(cap, sm.PLANT_LAYER, seed=100)
        self.assertNotEqual(a["null_mean"], c["null_mean"])

    def test_verified_tier_refuses_without_lock(self):
        with self.assertRaises(SystemExit):
            bp.run_verified(None, Path("x"), Path(self.tmp.name))
        with self.assertRaises(SystemExit):
            bp.run_verified(Path(self.tmp.name) / "missing_lock.json",
                            Path("x"), Path(self.tmp.name))

    def test_lock_roundtrip_and_mismatch(self):
        labels = Path(self.tmp.name) / "labels_final.csv"
        labels.write_text("row_id,label\nx,comply\n", encoding="utf-8")
        lock = Path(self.tmp.name) / "label_lock.json"
        ll.write_lock(labels, lock)
        self.assertTrue(ll.verify_lock(lock, labels))
        labels.write_text("row_id,label\nx,refuse\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            ll.verify_lock(lock, labels)

    def test_smoke_end_to_end_as_designed(self):
        out_root = Path(self.tmp.name) / "analysis"
        layer = bp.run_as_designed(self.run_dir, self.cmp_dir,
                                   self.run_dir / "emotion_smoke.pt",
                                   out_root)
        self.assertEqual(layer, sm.PLANT_LAYER)   # planted signal recovered
        out = out_root / "as_designed"
        for name in ("a1_existence.json", "a2_layer_selection.json",
                     "a3_distinctness.json", "a4_reducibility.json",
                     "a5_transfer.json", "a2_layer_curve.png",
                     "manifest.json"):
            self.assertTrue((out / name).exists(), name)
        a1 = json.loads((out / "a1_existence.json").read_text())
        self.assertTrue(a1["exceeds_null_p95"])
        a3 = json.loads((out / "a3_distinctness.json").read_text())
        self.assertLess(
            abs(a3["at_selected_layer"]["cosine_conflict_refusal"]), 0.35)
        a5 = json.loads((out / "a5_transfer.json").read_text())
        self.assertIn("harm_anchored_confirmatory", a5)
        self.assertIn("intermediate_exploratory", a5)
        hdr = a1["_header"]
        for k in ("pipeline_commit", "freeze_sha256",
                  "statistic_definitions", "seed"):
            self.assertIn(k, hdr)

    def test_smoke_provisional_and_audit_export(self):
        out_root = Path(self.tmp.name) / "analysis2"
        bp.run_provisional(self.run_dir, out_root)
        prov = out_root / "provisional"
        names = [p.name for p in prov.iterdir()]
        self.assertTrue(all(n.startswith("PROVISIONAL") for n in names))
        table = json.loads(
            (prov / "PROVISIONAL_manipulation_table.json").read_text())
        self.assertIn("comply", table["expected_vs_labeled"])
        audit = Path(self.tmp.name) / "audit.txt"
        ll.export_audit(self.run_dir, audit)
        text = audit.read_text(encoding="utf-8")
        self.assertIn("UNCERTAIN", text + " ")  # flags present or none — file exists
        for kw in ll.FORBIDDEN_IN_AUDIT:
            self.assertNotIn(f"{kw}=", text)


if __name__ == "__main__":
    unittest.main()
