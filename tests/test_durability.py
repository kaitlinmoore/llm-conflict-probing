"""Durability-layer tests (2026-07-17 shard-1 truncation incident):
atomic tmp-then-fsync-then-rename semantics and the verify_run.py smoke.

Run from the repo root:  python -m unittest discover -s tests -v
"""

import csv
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.pretest import runner_lib as rl

try:
    import torch
    HAVE_TORCH = True
except ImportError:
    HAVE_TORCH = False


def load_verify_run():
    spec = importlib.util.spec_from_file_location("verify_run", REPO / "scripts" / "verify_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestAtomicWrite(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.target = self.tmp / "artifact.json"

    def test_success_replaces_and_leaves_no_tmp(self):
        rl.atomic_write(self.target, lambda f: f.write('{"v": 1}'), mode="w")
        self.assertEqual(self.target.read_text(), '{"v": 1}')
        self.assertFalse((self.tmp / "artifact.json.tmp").exists())
        rl.atomic_write(self.target, lambda f: f.write('{"v": 2}'), mode="w")
        self.assertEqual(self.target.read_text(), '{"v": 2}')

    def test_exception_mid_write_preserves_prior_and_leaves_tmp(self):
        # the incident scenario: the real file must never be truncated by a
        # failed rewrite; the .tmp stays behind as evidence
        rl.atomic_write(self.target, lambda f: f.write("COMPLETE PRIOR VERSION"), mode="w")

        def failing_write(f):
            f.write("partial garbage")
            raise RuntimeError("simulated mid-write failure")

        with self.assertRaises(RuntimeError):
            rl.atomic_write(self.target, failing_write, mode="w")
        self.assertEqual(self.target.read_text(), "COMPLETE PRIOR VERSION")
        self.assertTrue((self.tmp / "artifact.json.tmp").exists())

    def test_binary_mode_roundtrip(self):
        payload = bytes(range(256)) * 3
        rl.atomic_write(self.target, lambda f: f.write(payload))  # default "wb"
        self.assertEqual(self.target.read_bytes(), payload)

    def test_file_digest_rereads_persisted_bytes(self):
        payload = b"digest me\n" * 100
        (self.tmp / "x.bin").write_bytes(payload)
        sha, size = rl.file_digest(self.tmp / "x.bin")
        self.assertEqual(sha, hashlib.sha256(payload).hexdigest())
        self.assertEqual(size, len(payload))


def synthetic_screen_run(tmp, n_rows=3, break_rows=False, break_digest=False):
    """A minimal screen-run directory that verify_run.py should PASS."""
    run_dir = Path(tmp) / "20260717_000000_llama8b_instrument_validation_screen-rebalance"
    run_dir.mkdir(parents=True)
    csv_path = run_dir / "screen_rebalance.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["prompt_key", "p_metric"])
        w.writeheader()
        for i in range(n_rows):
            w.writerow({"prompt_key": f"P{i}", "p_metric": 0.5})
    sha, size = rl.file_digest(csv_path)
    if break_digest:
        sha = "0" * 64
    manifest = {
        "run_id": run_dir.name, "run_role": "instrument_validation",
        "model": "meta-llama/Llama-3.1-8B-Instruct", "model_tag": "llama8b",
        "probe_file_sha256": "f" * 64, "schema_version": "v2",
        "screen_mode": "rebalance",
        "expected_rows": n_rows + (1 if break_rows else 0),
        "output_digests": {"screen_rebalance.csv": {"sha256": sha, "bytes": size}},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    return run_dir


class TestVerifyRunSmoke(unittest.TestCase):
    def run_verify(self, run_dir):
        mod = load_verify_run()
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = mod.main([str(run_dir)])
        return code, buf.getvalue()

    def test_clean_screen_run_passes(self):
        run_dir = synthetic_screen_run(tempfile.mkdtemp())
        code, out = self.run_verify(run_dir)
        self.assertEqual(code, 0, out)
        self.assertIn("VERIFY PASS", out)
        self.assertIn("SKIP  activations", out)          # screen run: none expected
        self.assertNotIn("FAIL ", out.replace("VERIFY PASS", ""))

    def test_row_count_mismatch_fails(self):
        run_dir = synthetic_screen_run(tempfile.mkdtemp(), break_rows=True)
        code, out = self.run_verify(run_dir)
        self.assertEqual(code, 1)
        self.assertIn("FAIL  screen_rebalance.csv row count", out)

    def test_digest_mismatch_fails(self):
        run_dir = synthetic_screen_run(tempfile.mkdtemp(), break_digest=True)
        code, out = self.run_verify(run_dir)
        self.assertEqual(code, 1)
        self.assertIn("FAIL  digest screen_rebalance.csv", out)

    def test_unparseable_manifest_fails(self):
        run_dir = synthetic_screen_run(tempfile.mkdtemp())
        (run_dir / "manifest.json").write_text("{truncated")
        code, out = self.run_verify(run_dir)
        self.assertEqual(code, 1)
        self.assertIn("FAIL  manifest.json parses", out)

    @unittest.skipUnless(HAVE_TORCH, "torch unavailable (dev box) — run on the pod")
    def test_generation_run_with_activations_passes(self):
        tmp = tempfile.mkdtemp()
        run_dir = Path(tmp) / "20260717_000000_llama8b_instrument_validation"
        run_dir.mkdir(parents=True)
        csv_path = run_dir / "generations.csv"
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["prompt_key", "response"])
            w.writeheader()
            w.writerow({"prompt_key": "P0", "response": "ok"})
        act_path = run_dir / "activations_llama8b.pt"
        rl.atomic_write(act_path, lambda f: torch.save(
            {"activations": {"P0": torch.zeros(2, 4)}, "partial": False}, f))
        digests = {}
        for p in (csv_path, act_path):
            sha, size = rl.file_digest(p)
            digests[p.name] = {"sha256": sha, "bytes": size}
        manifest = {
            "run_id": run_dir.name, "run_role": "instrument_validation",
            "model": "meta-llama/Llama-3.1-8B-Instruct", "model_tag": "llama8b",
            "probe_file_sha256": "f" * 64, "schema_version": "v2",
            "screen_mode": None, "expected_rows": 1, "output_digests": digests,
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest))
        code, out = self.run_verify(run_dir)
        self.assertEqual(code, 0, out)
        self.assertIn("PASS  activations partial flag is False", out)


if __name__ == "__main__":
    unittest.main()
