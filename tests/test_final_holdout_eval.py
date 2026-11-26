import unittest
from copy import deepcopy

from research.marker_fingerprint.calibrate import Observation
from research.marker_fingerprint.evaluate_partial import marks
from research.marker_fingerprint.final_holdout_eval import bilateral_confirmed, decision


class FinalHoldoutGateTests(unittest.TestCase):
    def evidence(self):
        audits, partial, strict = [], [], []
        for group, views in (("same_frame", ("r1", "r1", "r1b", "r1b", "r2", "r2")),
                             ("moved", ("r1", "r1") * 2 + ("r1b", "r1b") * 2)):
            for view in views:
                audits.append([{"query_view": view, "operational": True, "geometry_floor": True,
                                "identity_truth": "available", "expected_region": True,
                                "genuine_bilateral": group == "moved"}])
                fit = {"stop": "complete", "hypotheses": [{"alignment_2d": True, "verified_assignment": True}]}
                partial.append({"group": group, "outcome": "correct_unique", "resolved_candidates": 1,
                                "comparisons": [fit]})
                strict.append({"outcome": "no_match", "comparisons": [{"stop": "complete", "hypotheses": []}]})
        return {"C": partial, "B": strict}, audits

    def test_gate_requires_a_gain_on_completed_eligible_bilateral_pairs(self):
        runs, audits = self.evidence()
        result = decision(runs, audits)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["paired_gain_vs_strict"], 8)
        runs["B"] = deepcopy(runs["C"])
        self.assertEqual(decision(runs, audits)["verdict"], "FAILED")

    def test_below_floor_trials_stay_in_operational_denominator(self):
        runs, audits = self.evidence()
        for audit in audits[6:]:
            audit[0]["geometry_floor"] = False
        result = decision(runs, audits)
        self.assertEqual(result["verdict"], "INCONCLUSIVE")
        self.assertEqual(result["moved_denominators"]["operational"], 8)
        self.assertEqual(result["moved_denominators"]["below_floor"], 8)
        self.assertEqual(result["paired_gain_vs_strict"], 0)

    def test_budget_evidence_never_counts_as_recovery(self):
        runs, audits = self.evidence()
        runs["C"][-1]["outcome"] = "unresolved_search_budget"
        result = decision(runs, audits)
        self.assertEqual(result["verdict"], "INCONCLUSIVE")
        self.assertFalse(result["moved"][-1]["partial_recovered"])

    def test_false_or_unverified_unique_fails_even_with_missing_prerequisites(self):
        for outcome in ("false_unique", "unverified_unique_alignment"):
            with self.subTest(outcome=outcome):
                runs, audits = self.evidence()
                audits[-1][0]["operational"] = False
                runs["C"][-1]["outcome"] = outcome
                self.assertEqual(decision(runs, audits)["verdict"], "FAILED")

    def test_witnesses_require_positive_confirmation_in_both_views(self):
        primary = Observation("x", "one", "r1", (0, 0), marks(((10, 20),)), None, True)
        moved = Observation("x", "one", "r1b", (-14, 8), marks(((44, 32),)), None, True)
        a = {"registered_px": (10, 20), "hue": "yellow"}
        b = {"registered_px": (30, 40), "hue": "yellow"}
        self.assertTrue(bilateral_confirmed(primary, moved, {"r1": a, "r1b": b}))
        self.assertFalse(bilateral_confirmed(primary, moved, {"r1": a, "r1b": a}))
