"""emit_prompt_join tests: prompt_key -> rendered-text mapping goes through
runner_lib.enumerate_tasks (the runner's own rendering path), the join is
exact and unambiguous, and the end-to-end CLI writes prompt_join.csv, fails
closed on sha mismatch, and records the digest in the manifest.

Run from the repo root:  python -m unittest discover -s tests -v
Torch-free by design.
"""

import csv
import json
import tempfile
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.pretest import emit_prompt_join as epj
from src.pretest import runner_lib as rl

V2_RECORDS = [
    {"schema_version": "v2", "probe_id": "PT2-x-C1", "render_id": "PT2-x-C1::friend",
     "value": "honesty", "channel": "choice", "block": "main", "role": "friend",
     "option_a": "the blue door", "option_b": "the red door",
     "neutral_prompt": "Pick.\nOption A: the blue door\nOption B: the red door\nAnswer 'A' or 'B'.",
     "value_prompt": "Pick carefully.\nOption A: the blue door\nOption B: the red door\nAnswer 'A' or 'B'."},
    {"schema_version": "v2", "probe_id": "PT2-x-R1", "render_id": "PT2-x-R1::self",
     "value": "honesty", "channel": "resistance", "block": "main", "role": "self",
     "prompt": "Write the note."},
]


class TestPromptMap(unittest.TestCase):
    def test_map_matches_enumerate_tasks(self):
        mapping = epj.build_prompt_map(V2_RECORDS)
        tasks = rl.enumerate_tasks(V2_RECORDS)
        self.assertEqual(set(mapping), {t["prompt_key"] for t in tasks})
        for t in tasks:
            self.assertEqual(mapping[t["prompt_key"]], t["user_text"])

    def test_duplicate_key_with_differing_text_raises(self):
        clash = [dict(V2_RECORDS[1]), dict(V2_RECORDS[1], prompt="Different text.")]
        with self.assertRaises(ValueError):
            epj.build_prompt_map(clash)

    def test_choice_record_lookup_strips_variant(self):
        by_render = {r["render_id"]: r for r in V2_RECORDS if "render_id" in r}
        rec = epj.choice_record_for_key(by_render, "PT2-x-C1::friend::value")
        self.assertEqual(rec["probe_id"], "PT2-x-C1")

    def test_distinct_keys_preserve_first_appearance_order(self):
        rows = [{"prompt_key": k} for k in ["b", "a", "b", "c", "a"]]
        self.assertEqual(epj.distinct_keys_in_order(rows), ["b", "a", "c"])


class TestEndToEnd(unittest.TestCase):
    def _make_run(self, tmp, probe_sha_override=None):
        probes = tmp / "probes.jsonl"
        probes.write_bytes("\n".join(json.dumps(r) for r in V2_RECORDS).encode() + b"\n")
        run_dir = tmp / "run"
        run_dir.mkdir()
        sha, _ = rl.file_digest(probes)
        (run_dir / "manifest.json").write_text(json.dumps(
            {"probe_file_sha256": probe_sha_override or sha, "output_digests": {}}))
        tasks = rl.enumerate_tasks(V2_RECORDS)
        with open(run_dir / "generations.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["prompt_key", "needs_manual_label"])
            w.writeheader()
            for t in tasks:
                w.writerow({"prompt_key": t["prompt_key"], "needs_manual_label": "no"})
            # flagged choice row duplicated: distinctness must still hold
            w.writerow({"prompt_key": "PT2-x-C1::friend::value", "needs_manual_label": "yes"})
        return probes, run_dir

    def test_writes_join_and_manifest_digest(self):
        with tempfile.TemporaryDirectory() as d:
            probes, run_dir = self._make_run(Path(d))
            rc = epj.main(["--run-dir", str(run_dir), "--probes", str(probes)])
            self.assertEqual(rc, 0)
            out = run_dir / "prompt_join.csv"
            with open(out, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual([r["prompt_key"] for r in rows],
                             [t["prompt_key"] for t in rl.enumerate_tasks(V2_RECORDS)])
            self.assertIn("Option A: the blue door", rows[1]["prompt_text"])
            manifest = json.loads((run_dir / "manifest.json").read_text())
            sha, size = rl.file_digest(out)
            self.assertEqual(manifest["output_digests"]["prompt_join.csv"],
                             {"sha256": sha, "bytes": size})

    def test_fails_closed_on_probe_sha_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            probes, run_dir = self._make_run(Path(d), probe_sha_override="0" * 64)
            rc = epj.main(["--run-dir", str(run_dir), "--probes", str(probes)])
            self.assertEqual(rc, 1)
            self.assertFalse((run_dir / "prompt_join.csv").exists())


if __name__ == "__main__":
    unittest.main()
