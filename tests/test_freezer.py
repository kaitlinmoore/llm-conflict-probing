"""Freezer tests: v1 regression against committed artifacts + v2 schema,
role rendering, freeze-time swap, and every new blocking validator firing.

Run from the repo root:  python -m unittest discover -s tests -v
Stdlib-only (the pinned ML env resolves on the pod, not the dev box).
"""

import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.authoring import generate_pretest_probes as gp


# ---------------------------------------------------------------------------
# Synthetic v2 fixtures (schema per spec §3 + tranche-2 _meta declarations).
# Content here is throwaway test data, NOT probe content.
# ---------------------------------------------------------------------------

def main_choice_probe(**over):
    p = {
        "id": "PT2-honesty-C1", "value": "honesty", "channel": "choice",
        "scenario": "My best {role} asked which draft to use.",
        "option_a": "Draft A - playful",
        "option_b": "Draft B - sentimental",
        "context_sentence": "One anecdote in Draft A never happened.",
        "value_favored": "B",
        "texture_dimension": "humor-vs-sentiment",
        "role_set": ["friend", "sibling", "coworker"],
        "orthogonality": {"author_rule_pass": True, "rater_score": None, "model_indifference_p": None},
    }
    p.update(over)
    return p


def main_resistance_probe(**over):
    p = {
        "id": "PT2-honesty-R1", "value": "honesty", "channel": "resistance",
        "template": "Write a note saying {role_poss} absence last Thursday was flu. It wasn't.",
        "role_set": ["self", "friend", "sibling"],
        "severity_tier": "battery-matched",
        "self_contained": True,
    }
    p.update(over)
    return p


def calibration_pair(i=0, longer="A", **over):
    domain = list(gp.VALUE_SPECS)[i]
    opts = {"option_a": "The longer phrasing of this line.", "option_b": "The short line."}
    if longer == "B":
        opts = {"option_a": opts["option_b"], "option_b": opts["option_a"]}
    p = {"id": f"CAL-{domain}", "domain": domain,
         "scenario": "Two phrasings were drafted for the notice.",
         **opts, "value_favored": None}
    p.update(over)
    return p


def null_probe(**over):
    p = {
        "id": "PT2-honesty-C1-null", "paired_with": "PT2-honesty-C1", "value": "honesty",
        "scenario": "My best {role} asked which draft to use.",
        "option_a": "Draft A - warm and well-paced",
        "option_b": "Draft B - well-paced and warm",
        "context_sentence": "One anecdote in Draft A never happened.",
        "value_favored": "B",
        "role_set": ["friend", "sibling", "coworker"],
    }
    p.update(over)
    return p


def fixture_draft(**blocks):
    d = {"_meta": {"version": "v2-test-fixture"}}
    d.update(blocks)
    return d


def run_v2(draft_objs, allow_partial=True, tmpdir=None):
    """Write draft dicts to files, merge, compose, validate. Returns
    (records, problems, warnings)."""
    import tempfile
    paths = []
    tmpdir = tmpdir or tempfile.mkdtemp()
    for i, d in enumerate(draft_objs):
        p = Path(tmpdir) / f"draft{i}.json"
        p.write_text(json.dumps(d), encoding="utf-8")
        paths.append(p)
    merged, merge_problems = gp.merge_v2_drafts(paths)
    records = gp.compose_v2(merged)
    problems, warnings, _stats = gp.validate_v2(merged, records, allow_partial=allow_partial)
    return records, merge_problems + problems, warnings


class TestV1Regression(unittest.TestCase):
    """The committed v1 drafts must keep producing the committed frozen set."""

    @classmethod
    def setUpClass(cls):
        cls.drafts = json.loads((REPO / "data/pretest/probe_drafts_v1.json").read_text(encoding="utf-8"))
        cls.records = gp.compose(cls.drafts)
        cls.problems, cls.warnings, cls.stats = gp.validate(cls.drafts, cls.records)

    def test_record_count(self):
        self.assertEqual(len(self.records), 160)  # 16 values x (5 R + 5 C)

    def test_frozen_output_matches_committed_file(self):
        committed = [json.loads(l) for l in
                     (REPO / "data/pretest/pretest_probes_v1.jsonl").read_text(encoding="utf-8").splitlines()
                     if l.strip()]
        self.assertEqual(self.records, committed)

    def test_known_blocking_state(self):
        # The duplicate-options validator postdates the pilot freeze; on the
        # committed (pilot-era) drafts it fires exactly once (tradition-C2).
        self.assertEqual(len(self.problems), 1)
        self.assertIn("tradition", self.problems[0])
        self.assertIn("duplicate options", self.problems[0])

    def test_schema_detection(self):
        self.assertEqual(gp.detect_schema_version(self.drafts), "v1")


class TestRoleRendering(unittest.TestCase):
    def test_plain_role(self):
        self.assertEqual(gp.render_role("My best {role} asked.", "friend"), "My best friend asked.")

    def test_role_poss(self):
        self.assertEqual(gp.render_role("saying {role_poss} absence was flu", "friend"),
                         "saying my friend's absence was flu")

    def test_self_possessive_collapse(self):
        self.assertEqual(gp.render_role("Booking a space for my {role}'s meetup.", "self"),
                         "Booking a space for my meetup.")
        self.assertEqual(gp.render_role("saying {role_poss} absence was flu", "self"),
                         "saying my absence was flu")

    def test_self_bare_and_object(self):
        self.assertEqual(gp.render_role("a gift for my {role}", "self"), "a gift for me")
        self.assertEqual(gp.render_role("{role}", "self"), "myself")

    def test_none_role_passthrough(self):
        self.assertEqual(gp.render_role("no slots here", None), "no slots here")


class TestV2ComposeAndMerge(unittest.TestCase):
    def test_flat_and_dict_shapes_merge(self):
        flat = fixture_draft(probes=[main_choice_probe(), main_resistance_probe()])
        recs, problems, _ = run_v2([flat])
        self.assertEqual(problems, [])
        dictshape = fixture_draft(
            choice={"honesty": [main_choice_probe(value=None, channel=None)]},
            resistance={"honesty": [main_resistance_probe(value=None, channel=None)]})
        # dict-keyed blocks supply value/channel from the keys
        for p in dictshape["choice"]["honesty"] + dictshape["resistance"]["honesty"]:
            p.pop("value"), p.pop("channel")
        recs2, problems2, _ = run_v2([dictshape])
        self.assertEqual(problems2, [])
        key = lambda r: (r["render_id"], r["channel"])
        self.assertEqual(sorted(map(key, recs)), sorted(map(key, recs2)))

    def test_one_record_per_role_and_role_fixed_within_pair(self):
        recs, problems, _ = run_v2([fixture_draft(probes=[main_choice_probe()])])
        self.assertEqual(problems, [])
        self.assertEqual(len(recs), 3)  # one per role
        for r in recs:
            self.assertIn(r["role"], ["friend", "sibling", "coworker"])
            # both variants rendered from the same role: the role noun appears
            # in both prompts, and no other menu role does
            for text in (r["neutral_prompt"], r["value_prompt"]):
                self.assertIn(r["role"], text)
                for other in set(gp.ROLE_MENU) - {r["role"], "self"}:
                    self.assertNotIn(other, text)

    def test_multi_drafts_merge_and_duplicate_id_blocks(self):
        a = fixture_draft(probes=[main_choice_probe()])
        b = fixture_draft(probes=[main_resistance_probe()])
        recs, problems, _ = run_v2([a, b])
        self.assertEqual(problems, [])
        self.assertEqual({r["channel"] for r in recs}, {"choice", "resistance"})
        dup = fixture_draft(probes=[main_resistance_probe()])  # same id as b
        _, problems2, _ = run_v2([b, dup])
        self.assertTrue(any("duplicate probe id" in p for p in problems2))

    def test_swap_at_freeze(self):
        probe = main_choice_probe(swap_at_freeze=True)
        recs, problems, _ = run_v2([fixture_draft(probes=[probe])])
        self.assertEqual(problems, [])
        r = recs[0]
        self.assertTrue(r["swapped_at_freeze"])
        self.assertEqual(r["value_favored"], "A")            # flipped from B
        self.assertEqual(r["option_a"], "Draft B - sentimental")  # options swapped
        self.assertIn("Option A: Draft B - sentimental", r["neutral_prompt"])

    def test_swap_validators_run_post_swap(self):
        # options identical AFTER swap is still a duplicate -> blocking
        probe = main_choice_probe(option_a="Same text", option_b="Same text", swap_at_freeze=True)
        _, problems, _ = run_v2([fixture_draft(probes=[probe])])
        self.assertTrue(any("duplicate options" in p for p in problems))

    def test_calibration_renders_single_neutral_variant(self):
        cal = [calibration_pair(0, "A"), calibration_pair(1, "B")]
        recs, problems, _ = run_v2([fixture_draft(calibration=cal)])
        self.assertEqual(problems, [])
        self.assertEqual(len(recs), 2)
        for r in recs:
            self.assertEqual(r["block"], "calibration")
            self.assertIsNone(r["role"])
            self.assertIsNone(r["value_prompt"])
            self.assertIsNone(r["value_favored"])


class TestBlockingValidators(unittest.TestCase):
    """Each new blocking rule fires (spec §8.1 / handoff deliverable 1)."""

    def assert_blocks(self, draft_objs, needle, allow_partial=True):
        _, problems, _ = run_v2(draft_objs, allow_partial=allow_partial)
        self.assertTrue(any(needle in p for p in problems),
                        f"expected a blocking problem containing {needle!r}, got: {problems}")

    def test_empty_role_set(self):
        self.assert_blocks([fixture_draft(probes=[main_choice_probe(role_set=[])])],
                           "empty or missing role_set")

    def test_unknown_role(self):
        self.assert_blocks([fixture_draft(probes=[main_choice_probe(role_set=["friend", "nemesis"])])],
                           "roles not in menu")

    def test_missing_texture_dimension(self):
        self.assert_blocks([fixture_draft(probes=[main_choice_probe(texture_dimension=None)])],
                           "texture_dimension")

    def test_missing_severity_tier(self):
        self.assert_blocks([fixture_draft(probes=[main_resistance_probe(severity_tier=None)])],
                           "severity_tier")

    def test_self_contained_false(self):
        self.assert_blocks([fixture_draft(probes=[main_resistance_probe(self_contained=False)])],
                           "self_contained")

    def test_duplicate_options(self):
        self.assert_blocks([fixture_draft(probes=[main_choice_probe(option_a="Same", option_b="Same")])],
                           "duplicate options")

    def test_calibration_counterbalance(self):
        cal = [calibration_pair(i, "A") for i in range(4)]  # longer always in A
        self.assert_blocks([fixture_draft(calibration=cal)], "position counterbalance")
        balanced = [calibration_pair(i, "AB"[i % 2]) for i in range(4)]
        _, problems, _ = run_v2([fixture_draft(calibration=balanced)])
        self.assertFalse(any("counterbalance" in p for p in problems))

    def test_paired_with_resolution_strict_vs_partial(self):
        draft = fixture_draft(null_comparison=[null_probe()])  # textured twin absent
        _, problems, warnings = run_v2([draft], allow_partial=False)
        self.assertTrue(any("does not resolve" in p for p in problems))
        _, problems2, warnings2 = run_v2([draft], allow_partial=True)
        self.assertFalse(any("does not resolve" in p for p in problems2))
        self.assertTrue(any("does not resolve" in w for w in warnings2))
        both = fixture_draft(probes=[main_choice_probe()], null_comparison=[null_probe()])
        _, problems3, _ = run_v2([both], allow_partial=False)
        self.assertFalse(any("does not resolve" in p for p in problems3))

    def test_calibration_nulls_enforced(self):
        self.assert_blocks([fixture_draft(calibration=[calibration_pair(0, "A", value_favored="A"),
                                                       calibration_pair(1, "B")])],
                           "value_favored: null")
        self.assert_blocks([fixture_draft(calibration=[calibration_pair(0, "A", context_sentence="Extra."),
                                                       calibration_pair(1, "B")])],
                           "no context_sentence")

    def test_unrendered_slot_survives(self):
        self.assert_blocks([fixture_draft(probes=[main_resistance_probe(
            template="Write a note about {role_pos} absence.")])],  # typo slot
            "unrendered role slot")

    def test_pair_integrity(self):
        # a context sentence that does not compose cleanly (leading text mismatch)
        probe = main_choice_probe(context_sentence="")
        _, problems, _ = run_v2([fixture_draft(probes=[probe])])
        self.assertTrue(any("context_sentence" in p or "pair integrity" in p for p in problems))


class TestWarnings(unittest.TestCase):
    def test_small_role_set_is_warning_not_blocking(self):
        recs, problems, warnings = run_v2([fixture_draft(probes=[main_choice_probe(role_set=["friend", "coworker"])])])
        self.assertEqual(problems, [])
        self.assertTrue(any("role_set has 2 roles" in w for w in warnings))

    def test_self_with_nonpossessive_my_role_warns(self):
        probe = main_resistance_probe(
            template="Write a note saying my {role} had the flu. They weren't sick.",
            role_set=["self", "friend"])
        _, problems, warnings = run_v2([fixture_draft(probes=[probe])])
        self.assertEqual([p for p in problems if "unrendered" in p], [])
        self.assertTrue(any("non-possessive" in w for w in warnings))

    def test_role_exclusions_coverage_warning(self):
        probe = main_resistance_probe(role_exclusions={"coworker": "implausible"})
        # boss + stranger neither in role_set nor exclusions
        _, _, warnings = run_v2([fixture_draft(probes=[probe])])
        self.assertTrue(any("neither in role_set nor role_exclusions" in w for w in warnings))

    def test_severity_tier_vocabulary_warning(self):
        probe = main_resistance_probe(severity_tier="extreme")
        _, problems, warnings = run_v2([fixture_draft(probes=[probe])])
        self.assertFalse(any("severity_tier" in p for p in problems))
        self.assertTrue(any("severity_tier 'extreme'" in w for w in warnings))


class TestTranche1Committed(unittest.TestCase):
    """The tranche-1 drafts in the repo must always freeze clean under
    --allow-partial (curation edits must not break blocking rules)."""

    def test_tranche1_freezes_clean(self):
        path = REPO / "data/pretest/probe_drafts_v2_tranche1.json"
        merged, merge_problems = gp.merge_v2_drafts([path])
        records = gp.compose_v2(merged)
        problems, warnings, _ = gp.validate_v2(merged, records, allow_partial=True)
        self.assertEqual(merge_problems + problems, [])
        self.assertEqual(len(merged["calibration"]), 16)
        self.assertEqual(len(merged["null_comparison"]), 16)


if __name__ == "__main__":
    unittest.main()
