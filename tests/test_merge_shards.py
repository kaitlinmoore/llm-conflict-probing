"""merge_shards tests: shard-set verification logic (torch-free) and, where
torch is available (the pod), the full merge including activations.

Run from the repo root:  python -m unittest discover -s tests -v
"""

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.pretest import runner_lib as rl
from src.pretest import merge_shards as ms

try:
    import torch
    HAVE_TORCH = True
except ImportError:
    HAVE_TORCH = False

SAMPLE_K = 2


def frozen_records():
    recs = []
    for i, role in enumerate(["friend", "sibling", "coworker"]):
        recs.append({"schema_version": "v2", "probe_id": "PT2-t-R1",
                     "render_id": f"PT2-t-R1::{role}", "value": "honesty",
                     "channel": "resistance", "block": "main", "role": role,
                     "prompt": f"Do the thing for my {role}."})
    recs.append({"schema_version": "v2", "probe_id": "PT2-t-C1",
                 "render_id": "PT2-t-C1::friend", "value": "honesty",
                 "channel": "choice", "block": "main", "role": "friend",
                 "neutral_prompt": "n", "value_prompt": "v", "value_favored": "B",
                 "scenario": "s", "option_a": "a", "option_b": "b",
                 "context_sentence": "c", "texture_dimension": "x"})
    return recs


def rows_for_task(task):
    if task["kind"] == "resistance":
        rows = [{"prompt_key": task["prompt_key"], "variant": "sample", "seed": str(s),
                 "response": "ok"} for s in range(SAMPLE_K)]
        rows.append({"prompt_key": task["prompt_key"], "variant": "greedy_ref", "seed": "",
                     "response": "ok"})
        return rows
    return [{"prompt_key": task["prompt_key"], "variant": task["variant"], "seed": "",
             "response": ""}]


def build_shard_dirs(tmp, probes_path, n_shards, mutate=None):
    """Create shard run dirs with manifests + CSVs consistent with the frozen
    set. `mutate(shard_index, manifest, rows)` can corrupt one for tests."""
    records = frozen_records()
    tasks = rl.enumerate_tasks(records)
    sha = hashlib.sha256(probes_path.read_bytes()).hexdigest()
    dirs = []
    for i in range(1, n_shards + 1):
        d = Path(tmp) / f"run_shard{i}of{n_shards}"
        d.mkdir(parents=True)
        shard_tasks = rl.shard_slice(tasks, i, n_shards)
        rows = [r for t in shard_tasks for r in rows_for_task(t)]
        manifest = {
            "run_id": d.name, "run_role": "instrument_validation",
            "model": "meta-llama/Llama-3.1-8B-Instruct", "model_tag": "llama8b",
            "dtype": "bfloat16", "max_new_tokens": 16,
            "probe_file": str(probes_path), "probe_file_sha256": sha,
            "schema_version": "v2", "sample_k": SAMPLE_K, "temperature": 0.7,
            "shard": f"{i}/{n_shards}", "shard_index": i, "shard_total": n_shards,
            "screen_mode": None,
            "anchor_verification_samples": [{"tail_decoded": "model\n", "ok": True}],
        }
        if mutate:
            mutate(i, manifest, rows)
        (d / "manifest.json").write_text(json.dumps(manifest))
        with open(d / "generations.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["prompt_key", "variant", "seed", "response"])
            w.writeheader(); w.writerows(rows)
        dirs.append(d)
    return dirs, tasks


class TestVerifyShards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.probes_path = Path(self.tmp) / "frozen.jsonl"
        with open(self.probes_path, "w", encoding="utf-8", newline="\n") as f:
            for r in frozen_records():
                f.write(json.dumps(r) + "\n")
        self.sha = hashlib.sha256(self.probes_path.read_bytes()).hexdigest()

    def verify(self, dirs, tasks):
        shards = [ms.load_shard(d) for d in dirs]
        return ms.verify_shards(shards, self.probes_path, self.sha, tasks)

    def test_clean_shard_set_passes(self):
        dirs, tasks = build_shard_dirs(self.tmp, self.probes_path, 2)
        sample_k, problems = self.verify(dirs, tasks)
        self.assertEqual(problems, [])
        self.assertEqual(sample_k, SAMPLE_K)

    def test_wrong_probe_file_refused(self):
        dirs, tasks = build_shard_dirs(self.tmp, self.probes_path, 2)
        other = Path(self.tmp) / "other.jsonl"
        other.write_text(self.probes_path.read_text() + "\n")
        shards = [ms.load_shard(d) for d in dirs]
        _, problems = ms.verify_shards(shards, other,
                                       hashlib.sha256(other.read_bytes()).hexdigest(),
                                       tasks)
        self.assertTrue(any("does not match" in p for p in problems))

    def test_missing_shard_refused(self):
        dirs, tasks = build_shard_dirs(self.tmp, self.probes_path, 3)
        sample_k, problems = self.verify(dirs[:2], tasks)
        self.assertTrue(any("cover exactly 1..3" in p or "shard dirs given" in p for p in problems))

    def test_row_count_mismatch_refused(self):
        def drop_a_row(i, manifest, rows):
            if i == 1:
                rows.pop()
        dirs, tasks = build_shard_dirs(self.tmp, self.probes_path, 2, mutate=drop_a_row)
        _, problems = self.verify(dirs, tasks)
        self.assertTrue(any("expected" in p for p in problems))

    def test_duplicate_rows_across_shards_refused(self):
        records = frozen_records()
        tasks = rl.enumerate_tasks(records)
        all_rows = [r for t in tasks for r in rows_for_task(t)]

        def same_rows_everywhere(i, manifest, rows):
            rows[:] = all_rows
        dirs, _ = build_shard_dirs(self.tmp, self.probes_path, 2, mutate=same_rows_everywhere)
        _, problems = self.verify(dirs, tasks)
        self.assertTrue(any("already seen in another shard" in p or "duplicate row" in p
                            for p in problems))

    def test_param_mismatch_refused(self):
        def bump_temp(i, manifest, rows):
            if i == 2:
                manifest["temperature"] = 1.0
        dirs, tasks = build_shard_dirs(self.tmp, self.probes_path, 2, mutate=bump_temp)
        _, problems = self.verify(dirs, tasks)
        self.assertTrue(any("temperature" in p for p in problems))

    def test_screen_run_refused(self):
        def mark_screen(i, manifest, rows):
            if i == 1:
                manifest["screen_mode"] = "indifference"
        dirs, tasks = build_shard_dirs(self.tmp, self.probes_path, 2, mutate=mark_screen)
        _, problems = self.verify(dirs, tasks)
        self.assertTrue(any("screen" in p for p in problems))

    def test_canonical_row_order_covers_every_row(self):
        records = frozen_records()
        tasks = rl.enumerate_tasks(records)
        order = ms.canonical_row_order(tasks, SAMPLE_K)
        all_rows = [r for t in tasks for r in rows_for_task(t)]
        keys = [(r["prompt_key"], r["variant"], r["seed"]) for r in all_rows]
        self.assertEqual(sorted(order.keys()), sorted(keys))
        self.assertEqual(sorted(order.values()), list(range(len(all_rows))))


@unittest.skipUnless(HAVE_TORCH, "torch unavailable (dev box) — run on the pod")
class TestFullMerge(unittest.TestCase):
    def test_end_to_end_merge(self):
        tmp = tempfile.mkdtemp()
        probes_path = Path(tmp) / "frozen.jsonl"
        with open(probes_path, "w", encoding="utf-8", newline="\n") as f:
            for r in frozen_records():
                f.write(json.dumps(r) + "\n")
        dirs, tasks = build_shard_dirs(tmp, probes_path, 2)
        for d in dirs:  # activations: one tensor per prompt_key in that shard
            manifest = json.loads((d / "manifest.json").read_text())
            i, n = rl.parse_shard(manifest["shard"])
            acts = {t["prompt_key"]: torch.zeros(2, 4)
                    for t in rl.shard_slice(tasks, i, n)}
            torch.save({"activations": acts, "partial": False,
                        "layout": "test", "n_layers": 2, "d_model": 4},
                       d / "activations_llama8b.pt")
        out = Path(tmp) / "merged"
        argv = sys.argv
        sys.argv = ["merge_shards.py", "--shards", *map(str, dirs),
                    "--probes", str(probes_path), "--out", str(out)]
        try:
            ms.main()
        finally:
            sys.argv = argv
        with open(out / "generations.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), rl.expected_total_rows(tasks, SAMPLE_K))
        merged = torch.load(out / "activations_llama8b.pt", weights_only=False)
        self.assertFalse(merged["partial"])
        self.assertEqual(set(merged["activations"]), {t["prompt_key"] for t in tasks})
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertTrue(manifest["merged"])
        self.assertEqual(len(manifest["shards"]), 2)
        for s in manifest["shards"]:
            for key in ("generations_csv_sha256", "activations_pt_sha256", "manifest_sha256"):
                self.assertRegex(s[key], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
