"""Tests for run_battery.py's pure (off-pod) pieces: frozen-sha gate,
rendering, work-list construction, regeneration/stability selection.
Model-dependent capture paths are exercised by the pod smoke run (B2).
Stdlib only."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.battery import run_battery as rb


def frozen_row(order="AB", family="choice", **over):
    r = {"row_id": f"type1:CB-hc-S1:agree_A:{order}",
         "type_id": "type1_honesty_vs_care", "type_num": 1,
         "family": family, "scenario_id": "CB-hc-S1",
         "condition": "agree_A" if family == "choice" else "agree_comply",
         "order": order, "stem": "Stem text.",
         "shared_opposition_text": "", "condition_insert": "Insert text.",
         "option_A": "Do A." if family == "choice" else "",
         "option_B": "Do B." if family == "choice" else "",
         "expected_pick": "A" if family == "choice" else "",
         "expected_response": "" if family == "choice" else "comply"}
    r.update(over)
    return r


def comp_row(i=0, cond="torn"):
    return {"item_id": f"CMP-{cond}-{i}", "condition": cond,
            "stem": "Pick one.", "option_A": "Sand.", "option_B": "Gravel.",
            "expected_pick": ""}


class FrozenGate(unittest.TestCase):
    def test_sha_mismatch_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "frozen.jsonl"
            f.write_text('{"x":1}\n', encoding="utf-8")
            m = Path(d) / "freeze_manifest.json"
            m.write_text(json.dumps({"frozen_sha256": "0" * 64}),
                         encoding="utf-8")
            with self.assertRaises(SystemExit):
                rb.verify_frozen(f, m)
            good = hashlib.sha256(f.read_bytes()).hexdigest()
            m.write_text(json.dumps({"frozen_sha256": good}),
                         encoding="utf-8")
            self.assertEqual(rb.verify_frozen(f, m), good)


class Rendering(unittest.TestCase):
    def test_stimulus_order_and_verbatim(self):
        r = frozen_row(condition="oppose_tip_A",
                       shared_opposition_text="Shared text.")
        s = rb.render_stimulus(r)
        self.assertEqual(s, "Stem text.\n\nShared text.\n\nInsert text.")

    def test_choice_prompt_open_ended_has_options_no_instruction(self):
        p = rb.render_prompt(frozen_row(), "open_ended")
        self.assertIn("A: Do A.\nB: Do B.", p)
        self.assertNotIn(rb.ANSWER_ONLY_INSTRUCTION, p)

    def test_answer_only_adds_single_instruction_line(self):
        p = rb.render_prompt(frozen_row(), "answer_only")
        self.assertTrue(p.endswith(rb.ANSWER_ONLY_INSTRUCTION))

    def test_refusal_has_no_options_and_no_answer_only(self):
        r = frozen_row(family="refusal", order="NA")
        p = rb.render_prompt(r, "open_ended")
        self.assertNotIn("A:", p)
        with self.assertRaises(ValueError):
            rb.render_prompt(r, "answer_only")


class WorkList(unittest.TestCase):
    def rows(self):
        frozen = [frozen_row("AB"), frozen_row("BA"),
                  frozen_row(family="refusal", order="NA")]
        comp = [comp_row(0, "torn"), comp_row(0, "easy")]
        return frozen, comp

    def test_arm_assignment(self):
        frozen, comp = self.rows()
        units = rb.administered_rows(frozen, comp)
        # 2 choice rows x 2 arms + 1 refusal x 1 + 2 competition x 2
        self.assertEqual(len(units), 9)
        ao = [(r["row_id"], a) for r, a in units if a == "answer_only"]
        self.assertEqual(len(ao), 4)
        self.assertFalse([1 for r, a in units
                          if r["family"] == "refusal" and a == "answer_only"])

    def test_order_deterministic_and_seed_sensitive(self):
        frozen, comp = self.rows()
        u1 = [rb.prompt_key(r, a) for r, a in
              rb.administered_rows(frozen, comp, seed=23)]
        u2 = [rb.prompt_key(r, a) for r, a in
              rb.administered_rows(frozen, comp, seed=23)]
        u3 = [rb.prompt_key(r, a) for r, a in
              rb.administered_rows(frozen, comp, seed=24)]
        self.assertEqual(u1, u2)
        self.assertNotEqual(u1, u3)

    def test_shard_partitions_without_overlap(self):
        frozen, comp = self.rows()
        all_keys = {rb.prompt_key(r, a) for r, a in
                    rb.administered_rows(frozen, comp)}
        got = []
        for i in range(3):
            got += [rb.prompt_key(r, a) for r, a in
                    rb.administered_rows(frozen, comp, shard=f"{i}/3")]
        self.assertEqual(sorted(got), sorted(all_keys))

    def test_smoke_is_bounded(self):
        frozen = [frozen_row("AB", scenario_id=f"S{i}",
                             row_id=f"t:S{i}:agree_A:AB")
                  for i in range(40)]
        units = rb.administered_rows(frozen, [], smoke=True)
        self.assertLess(len(units), 20)


class RegenAndStability(unittest.TestCase):
    def test_regeneration_only_on_capped_uncertain(self):
        li_unc = {"uncertain": True}
        li_ok = {"uncertain": False}
        self.assertTrue(rb.needs_regeneration("x", li_unc, cap=128,
                                              n_tokens=128))
        self.assertFalse(rb.needs_regeneration("x", li_ok, cap=128,
                                               n_tokens=128))
        self.assertFalse(rb.needs_regeneration("x", li_unc, cap=128,
                                               n_tokens=50))

    def test_stability_selection(self):
        refusal = frozen_row(family="refusal", order="NA")  # expected comply
        # disclaimer matches expected comply (rubric §9.4b) -> no shard
        self.assertFalse(rb.needs_stability(
            refusal, {"label": "disclaimer", "uncertain": False}))
        # hedge disagrees with expected comply -> shard
        self.assertTrue(rb.needs_stability(
            refusal, {"label": "hedge", "uncertain": False}))
        # uncertain always shards
        self.assertTrue(rb.needs_stability(
            refusal, {"label": "comply", "uncertain": True}))
        # choice family never shards
        self.assertFalse(rb.needs_stability(
            frozen_row(), {"label": "refuse", "uncertain": True}))


if __name__ == "__main__":
    unittest.main()
