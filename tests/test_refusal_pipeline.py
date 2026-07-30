"""Tests for the refusal-comparator pipeline — stdlib + numpy, no weights.

capture_refusal.py / ablation_check.py import torch and transformer_lens at
module load, so they are exercised only where importable (skipped off-pod);
the curation, direction, and reliability logic is torch-free and always runs.
"""

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.comparators import curate_refusal_prompts as cur
from src.comparators import refusal_direction as rd


class CurationTests(unittest.TestCase):
    def test_format_filters(self):
        ok = "Write a short poem about the sea and its moods today"
        self.assertTrue(cur.format_ok(ok, 30, 160))
        self.assertFalse(cur.format_ok("Too short", 30, 160))
        self.assertFalse(cur.format_ok(ok + "\nsecond line", 30, 160))
        self.assertFalse(cur.format_ok(ok + ":", 30, 160))
        self.assertFalse(cur.format_ok(ok + " {placeholder}", 30, 160))
        self.assertFalse(cur.format_ok(ok + " café", 30, 160))

    def test_imperative_filter(self):
        self.assertTrue(cur.IMPERATIVE_RE.match("Explain how photosynthesis works"))
        self.assertIsNone(cur.IMPERATIVE_RE.match("What is photosynthesis?"))

    def test_length_match_pairs_by_length_and_is_deterministic(self):
        import random
        targets = [{"text": "x" * n, "row": i} for i, n in enumerate((40, 60, 80))]
        pool = [{"text": "y" * n, "row": i}
                for i, n in enumerate((39, 41, 59, 61, 79, 81, 100))]
        a = cur.length_match(targets, pool, random.Random(23))
        b = cur.length_match(targets, pool, random.Random(23))
        self.assertEqual([r["text"] for r in a], [r["text"] for r in b])
        for tgt, got in zip(sorted(targets, key=lambda r: r["text"]), a):
            self.assertLessEqual(abs(len(tgt["text"]) - len(got["text"])), 1)

    def test_length_match_is_without_replacement(self):
        import random
        targets = [{"text": "x" * 50, "row": i} for i in range(3)]
        pool = [{"text": "y" * 50, "row": i} for i in range(3)]
        got = cur.length_match(targets, pool, random.Random(23))
        self.assertEqual(len({r["row"] for r in got}), 3)

    def test_curated_file_is_wellformed(self):
        """The committed prompt set: schema, balance, pairing, provenance."""
        path = REPO / "data" / "comparators" / "refusal_prompts.jsonl"
        if not path.exists():
            self.skipTest("curated prompt file not present")
        recs = [json.loads(l) for l in
                path.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertEqual(len(recs), 320)
        groups = {}
        for r in recs:
            groups.setdefault((r["prompt_class"], r["split"]), []).append(r)
        self.assertEqual({k: len(v) for k, v in sorted(groups.items())},
                         {("harmful", "holdout"): 32, ("harmful", "train"): 128,
                          ("harmless", "holdout"): 32, ("harmless", "train"): 128})
        self.assertEqual(len({r["text"] for r in recs}), 320)
        self.assertEqual(len({r["prompt_key"] for r in recs}), 320)
        for r in recs:
            self.assertIn("source", r["provenance"])
            self.assertEqual(len(r["provenance"]["source_sha256"]), 64)
        # length matching held per split
        for split in ("train", "holdout"):
            hf = [len(r["text"]) for r in groups[("harmful", split)]]
            hl = [len(r["text"]) for r in groups[("harmless", split)]]
            self.assertAlmostEqual(sum(hf) / len(hf), sum(hl) / len(hl), delta=1.0)


class DirectionTests(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(23)
        self.L, self.d = 4, 16
        self.axis = self.rng.normal(size=(self.L, self.d))
        self.acts, self.pairs = {}, []
        for i in range(8):
            base = self.rng.normal(size=(self.L, self.d))
            a, b = f"harmful-train-{i:03d}", f"harmless-train-{i:03d}"
            self.acts[a] = base + self.axis
            self.acts[b] = base
            self.pairs.append((a, b))

    def test_diff_in_means_recovers_axis(self):
        np.testing.assert_allclose(rd.diff_in_means(self.acts, self.pairs),
                                   self.axis, atol=1e-12)

    def test_unit_normalize(self):
        v = rd.unit_normalize(rd.diff_in_means(self.acts, self.pairs))
        np.testing.assert_allclose(np.linalg.norm(v, axis=1), 1.0)

    def test_reliability_high_for_consistent_signal(self):
        import random
        rel, n = rd.split_half_reliability(self.acts, self.pairs, 10,
                                           random.Random(23))
        self.assertEqual(n, 10)
        self.assertTrue((rel > 0.9).all(), f"reliability {rel}")

    def test_reliability_low_for_noise(self):
        import random
        acts, pairs = {}, []
        for i in range(8):
            a, b = f"h-{i}", f"n-{i}"
            acts[a] = self.rng.normal(size=(self.L, 256))
            acts[b] = self.rng.normal(size=(self.L, 256))
            pairs.append((a, b))
        rel, _ = rd.split_half_reliability(acts, pairs, 10, random.Random(23))
        self.assertTrue((np.abs(rel) < 0.8).all(), f"reliability {rel}")

    def test_reliability_is_deterministic(self):
        import random
        r1, _ = rd.split_half_reliability(self.acts, self.pairs, 8, random.Random(23))
        r2, _ = rd.split_half_reliability(self.acts, self.pairs, 8, random.Random(23))
        np.testing.assert_allclose(r1, r2)

    def test_pair_keys_requires_balance(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "prompts.csv"
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["prompt_key", "prompt_class", "split", "n_tokens"])
                w.writerow(["harmful-train-000", "harmful", "train", "10"])
                w.writerow(["harmful-train-001", "harmful", "train", "10"])
                w.writerow(["harmless-train-000", "harmless", "train", "10"])
            with self.assertRaises(ValueError):
                rd.pair_keys(p, "train")

    def test_pair_keys_excludes_holdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "prompts.csv"
            with open(p, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, lineterminator="\n")
                w.writerow(["prompt_key", "prompt_class", "split", "n_tokens"])
                for cls in ("harmful", "harmless"):
                    for split in ("train", "holdout"):
                        w.writerow([f"{cls}-{split}-000", cls, split, "10"])
            pairs = rd.pair_keys(p, "train")
            self.assertEqual(pairs, [("harmful-train-000", "harmless-train-000")])


class AblationHelperTests(unittest.TestCase):
    def test_band_layers(self):
        try:
            from src.comparators import ablation_check as ac
        except ImportError:
            self.skipTest("torch/transformer_lens not importable (off-pod)")
        rel = np.array([0.1, 0.5, 1.0, 0.95, 0.85])
        self.assertEqual(ac.band_layers(rel, 0.9), [2, 3])

    def test_refused_flag_uses_pretest_markers(self):
        try:
            from src.comparators import ablation_check as ac
        except ImportError:
            self.skipTest("torch/transformer_lens not importable (off-pod)")
        self.assertEqual(ac.refused_flag("I can't help with that."), 1)
        self.assertEqual(ac.refused_flag("Sure! Here are three ideas."), 0)


class VerifyRunTests(unittest.TestCase):
    def test_row_count_file_key_is_honored(self):
        """Comparator manifests declare prompts.csv; pre-test ones don't and
        must keep the generations.csv default."""
        src = (REPO / "scripts" / "verify_run.py").read_text(encoding="utf-8")
        self.assertIn('manifest.get("row_count_file")', src)
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "prompts.csv").write_text(
                "prompt_key,prompt_class,split,n_tokens\nk,harmful,train,5\n",
                encoding="utf-8")
            (d / "manifest.json").write_text(json.dumps({
                "run_id": "t", "run_role": "refusal_comparator_capture",
                "model": "m", "model_tag": "tag", "probe_file_sha256": "x",
                "expected_rows": 1, "schema_version": "v1",
                "row_count_file": "prompts.csv", "screen_mode": "noact",
            }), encoding="utf-8")
            out = subprocess.run(
                [sys.executable, str(REPO / "scripts" / "verify_run.py"), str(d)],
                capture_output=True, text=True)
            self.assertIn("prompts.csv row count == expected_rows", out.stdout)
            self.assertNotIn("FAIL  prompts.csv", out.stdout)


if __name__ == "__main__":
    unittest.main()
