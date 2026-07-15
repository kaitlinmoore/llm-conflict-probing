"""runner_lib tests: stubbed-logits choice readout, stub-tokenizer token-variant
collection, task enumeration, screen construction, shard split integrity.

Run from the repo root:  python -m unittest discover -s tests -v
Torch-free by design (runner_lib is the torch-free half of the runner).
"""

import json
import math
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.pretest import runner_lib as rl


class StubTokenizer:
    """Single-token encodings for a controlled subset of surface forms;
    everything else encodes to two tokens (and must be excluded)."""
    SINGLE = {"A": 10, " A": 11, "a": 12, '"A': 13,
              "B": 20, " B": 21, "b": 22, '"B': 23}

    def encode(self, text, add_special_tokens=False):
        assert add_special_tokens is False
        if text in self.SINGLE:
            return [self.SINGLE[text]]
        return [99, 98]  # multi-token: not attributable to the first position


def v2_choice_record(i=0, roles=("friend",), block="main", with_value_prompt=True):
    recs = []
    for role in roles:
        recs.append({
            "schema_version": "v2", "probe_id": f"PT2-test-C{i}",
            "render_id": f"PT2-test-C{i}::{role}", "value": "honesty",
            "channel": "choice", "block": block, "role": role,
            "scenario": "A scenario.", "option_a": f"Opt A {i}", "option_b": f"Opt B {i}",
            "context_sentence": "Context." if with_value_prompt else None,
            "neutral_prompt": f"A scenario. {i}\nOption A\nOption B\nWhich?",
            "value_prompt": f"A scenario. Context. {i}\nOption A\nOption B\nWhich?" if with_value_prompt else None,
            "value_favored": "B",
        })
    return recs


def v2_resistance_record(i=0, roles=("friend",)):
    return [{
        "schema_version": "v2", "probe_id": f"PT2-test-R{i}",
        "render_id": f"PT2-test-R{i}::{role}", "value": "honesty",
        "channel": "resistance", "block": "main", "role": role,
        "prompt": f"Do the thing {i} for my {role}.",
    } for role in roles]


class TestChoiceReadout(unittest.TestCase):
    def test_token_variant_collection_single_token_only(self):
        tok = StubTokenizer()
        ids_a, forms_a = rl.collect_letter_token_ids(tok, "A")
        ids_b, forms_b = rl.collect_letter_token_ids(tok, "B")
        self.assertEqual(sorted(ids_a), [10, 11, 12, 13])
        self.assertEqual(sorted(ids_b), [20, 21, 22, 23])
        self.assertIn("A", forms_a)
        self.assertIn(" A", forms_a)
        self.assertNotIn("'A", forms_a)  # multi-token in the stub -> excluded
        self.assertEqual(len(ids_a), len(set(ids_a)))  # deduped

    def test_renormalization_against_known_softmax(self):
        # vocab of 30; logits 2.0 on one A-token, 1.0 on one B-token, 0 elsewhere
        logits = [0.0] * 30
        logits[10], logits[20] = 2.0, 1.0
        r = rl.choice_readout(logits, [10, 11, 12, 13], [20, 21, 22, 23])
        z = 26 * math.exp(0) + math.exp(2.0) + math.exp(1.0) + 2 * math.exp(0)  # ids 11,12,13,21,22,23 are exp(0) too
        # direct check instead: renormalized ratio of the summed masses
        mass_a = (math.exp(2.0) + 3 * 1.0)
        mass_b = (math.exp(1.0) + 3 * 1.0)
        self.assertAlmostEqual(r["p_a"], mass_a / (mass_a + mass_b), places=10)
        self.assertAlmostEqual(r["p_a"] + r["p_b"], 1.0, places=12)

    def test_mass_logging_and_low_mass_flag(self):
        # concentrated on A/B tokens -> high mass, no flag
        logits = [-20.0] * 30
        logits[10], logits[20] = 5.0, 5.0
        r = rl.choice_readout(logits, [10], [20])
        self.assertGreater(r["mass_combined"], 0.99)
        self.assertFalse(r["low_mass_flag"])
        # mass spread over non-letter tokens -> flag fires (fallback trigger)
        logits2 = [5.0] * 30
        r2 = rl.choice_readout(logits2, [10], [20])
        self.assertAlmostEqual(r2["mass_combined"], 2 / 30, places=10)
        self.assertTrue(r2["low_mass_flag"])
        self.assertAlmostEqual(r2["p_a"], 0.5, places=10)  # renormalized still defined

    def test_zero_mass_edge(self):
        logits = [0.0] * 8
        logits[0] = 60.0  # everything else numerically underflows vs max-shift? no — softmax never exactly 0
        r = rl.choice_readout(logits, [1], [2])
        self.assertTrue(r["low_mass_flag"])
        # p values stay defined (tiny but nonzero masses renormalize)
        self.assertAlmostEqual(r["p_a"], 0.5, places=6)


class TestEnumeration(unittest.TestCase):
    def test_v1_enumeration_matches_pilot(self):
        records = [json.loads(l) for l in
                   (REPO / "data/pretest/pretest_probes_v1.jsonl").read_text(encoding="utf-8").splitlines()
                   if l.strip()]
        tasks = rl.enumerate_tasks(records)
        self.assertEqual(len(tasks), 240)  # pilot manifest n_prompt_texts
        self.assertEqual(tasks[0]["prompt_key"], "PT-honesty-R1")
        self.assertTrue(all(t["kind"] == "v1_generate" for t in tasks))

    def test_v2_enumeration(self):
        records = (v2_choice_record(0, roles=("friend", "sibling"))
                   + v2_choice_record(1, roles=("friend",), block="calibration", with_value_prompt=False)
                   + v2_resistance_record(0, roles=("friend", "coworker")))
        tasks = rl.enumerate_tasks(records)
        # choice pair: 2 roles x 2 variants; calibration: 1; resistance: 2
        self.assertEqual(len(tasks), 4 + 1 + 2)
        kinds = [t["kind"] for t in tasks]
        self.assertEqual(kinds.count("choice"), 5)
        self.assertEqual(kinds.count("resistance"), 2)
        self.assertEqual(rl.expected_total_rows(tasks, sample_k=10), 5 + 2 * 11)

    def test_mixed_schema_rejected(self):
        v1 = {"probe_id": "PT-x-R1", "channel": "resistance", "prompt": "x"}
        with self.assertRaises(ValueError):
            rl.enumerate_tasks([v1, v2_resistance_record(0)[0]])


class TestScreens(unittest.TestCase):
    def test_screen_targets_textured_main_choice_only(self):
        records = (v2_choice_record(0) + v2_choice_record(1, block="null_comparison")
                   + v2_choice_record(2, block="calibration", with_value_prompt=False)
                   + v2_resistance_record(0))
        tasks = rl.enumerate_screen_tasks(records, "indifference")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["probe_id"], "PT2-test-C0")

    def test_indifference_prompt_wording(self):
        tasks = rl.enumerate_screen_tasks(v2_choice_record(0), "indifference")
        text = tasks[0]["user_text"]
        self.assertIn("Which option is more honest?", text)
        self.assertIn("Opt A 0", text)
        self.assertNotIn("Context.", text)  # no context sentence in screens

    def test_rebalance_uses_neutral_prompt(self):
        recs = v2_choice_record(0)
        tasks = rl.enumerate_screen_tasks(recs, "rebalance")
        self.assertEqual(tasks[0]["user_text"], recs[0]["neutral_prompt"])

    def test_unknown_mode_and_missing_adjective(self):
        recs = v2_choice_record(0)
        with self.assertRaises(ValueError):
            rl.enumerate_screen_tasks(recs, "vibes")
        recs2 = [dict(recs[0], value="not_a_value")]
        with self.assertRaises(ValueError):
            rl.enumerate_screen_tasks(recs2, "indifference")

    def test_screens_reject_v1(self):
        v1 = [{"probe_id": "PT-x-C1", "channel": "choice", "neutral_prompt": "n",
               "value_prompt": "v"}]
        with self.assertRaises(ValueError):
            rl.enumerate_screen_tasks(v1, "indifference")


class TestSharding(unittest.TestCase):
    def test_parse_shard(self):
        self.assertEqual(rl.parse_shard("2/3"), (2, 3))
        for bad in ("0/3", "4/3", "a/3", "3", "1/2/3"):
            with self.assertRaises(ValueError, msg=bad):
                rl.parse_shard(bad)

    def test_partition_is_disjoint_covering_and_deterministic(self):
        records = (v2_choice_record(0, roles=("friend", "sibling", "coworker"))
                   + v2_resistance_record(0, roles=("friend", "sibling"))
                   + v2_choice_record(1, roles=("boss",)))
        tasks = rl.enumerate_tasks(records)
        for n in (1, 2, 3, 5, len(tasks) + 2):
            shards = [rl.shard_slice(tasks, i, n) for i in range(1, n + 1)]
            merged = [t["prompt_key"] for s in shards for t in s]
            self.assertEqual(sorted(merged), sorted(t["prompt_key"] for t in tasks), f"N={n}")
            self.assertEqual(len(merged), len(set(merged)), f"N={n}: overlap")
            # deterministic: same call, same result
            self.assertEqual(shards[0], rl.shard_slice(tasks, 1, n))

    def test_a_prompts_rows_stay_in_one_shard(self):
        # sharding is over tasks (rendered prompts); expected_rows accounts for
        # a resistance task's k+1 rows as an atomic unit
        tasks = rl.enumerate_tasks(v2_resistance_record(0, roles=("friend", "sibling", "coworker")))
        s1, s2 = rl.shard_slice(tasks, 1, 2), rl.shard_slice(tasks, 2, 2)
        self.assertEqual(rl.expected_total_rows(s1, 4) + rl.expected_total_rows(s2, 4),
                         rl.expected_total_rows(tasks, 4))


if __name__ == "__main__":
    unittest.main()
