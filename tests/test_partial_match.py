import unittest
from dataclasses import replace
from itertools import combinations, permutations
from math import dist

from research.marker_fingerprint.bounded_match import LIMITS
from research.marker_fingerprint.evaluate_partial import eligibility, marks, operation, score, synthetic_trials
from research.marker_fingerprint.partial_match import classify, match_query


class PartialMatchTests(unittest.TestCase):
    def test_deterministic_synthetic_controls(self):
        for trial in synthetic_trials():
            with self.subTest(trial=trial.id):
                eligible = eligibility(trial)
                result = operation(trial, "partial")()
                row = score(trial, "partial", result, eligible)
                if trial.expected == "positive":
                    self.assertEqual(row["outcome"], "correct_unique")
                    self.assertTrue(row["comparisons"][0]["hypotheses"][0]["exact_shared"])
                    self.assertEqual(classify(result), "unique_reference")
                elif trial.expected == "insufficient":
                    self.assertIn(row["outcome"], ("unavailable_alignment", "unresolved_2d", "no_match",
                                                   "ambiguous_correspondences"))
                    self.assertEqual(row["resolved_candidates"], 0)
                elif trial.expected == "budget":
                    self.assertEqual(classify(result), "unresolved_search_budget")
                    stop = "pair_hypotheses" if trial.id == "default_hypothesis_ceiling" else trial.id
                    self.assertEqual(result.stop, stop)
                else:
                    self.assertEqual(row["outcome"], trial.expected)
                if trial.id == "bilateral_addition_equal":
                    hypothesis, = result.pairs[0].hypotheses
                    self.assertEqual(hypothesis.matched_fraction, (4 / 6, 4 / 6))
                    self.assertTrue(all(0.25 <= span < 1 for span in hypothesis.span_fraction))
                if trial.id == "translated":
                    self.assertEqual(result.pairs[0].hypotheses[0].offset_px, (213, -82))
                if trial.id == "repeated_within_reference":
                    self.assertEqual({h.offset_px for h in result.pairs[0].hypotheses}, {(0, 0), (30, 0)})
                if trial.id == "repeated_across_regions":
                    self.assertEqual(classify(result), "ambiguous_references")
                    self.assertTrue(row["comparisons"][1]["hypotheses"])
                if trial.id == "default_hypothesis_ceiling":
                    pair, = result.pairs
                    self.assertEqual((len(pair.hypotheses), pair.hypotheses_seen), (256, 257))

    def test_maximal_assignments_against_brute_force(self):
        # This fixture has a five-point fit plus a four-point fit at a different translation.
        q = marks(((0, 0), (33, 0), (66, 0), (0, 40), (33, 40)))
        r = marks(((0, 0), (33, 0), (66, 0), (0, 40), (33, 40), (66, 40)))
        feasible = set()
        for n in (4, 5):
            for ii in combinations(range(5), n):
                for jj in permutations(range(6), n):
                    shifts = [(r.points[j].point[0] - q.points[i].point[0],
                               r.points[j].point[1] - q.points[i].point[1]) for i, j in zip(ii, jj)]
                    if all(dist(a, b) <= 6 for a, b in combinations(shifts, 2)):
                        feasible.add(frozenset(zip(ii, jj)))
        expected = {p for p in feasible if not any(p < other for other in feasible)}
        self.assertEqual({len(p) for p in expected}, {4, 5})
        result = match_query(q, (r,))
        self.assertEqual({frozenset(h.pairs) for h in result.pairs[0].hypotheses}, expected)

    def test_truncation_after_complete_reference_with_candidate(self):
        q = marks(((0, 0), (33, 0), (0, 42)))
        complete = match_query(q, (q,))
        truncated = match_query(q, (q, q), limits=replace(LIMITS, query_prefixes=complete.prefixes))
        self.assertTrue(truncated.pairs[0].hypotheses)
        self.assertEqual(truncated.prefixes, complete.prefixes)
        self.assertEqual(classify(truncated), "unresolved_search_budget")

    def test_unknown_hue_and_player_uncertainty_do_not_change_translation(self):
        q = marks(((0, 0), (31, 0), (7, 42)), hue="unknown")
        r = replace(marks(((0, 0), (31, 0), (7, 42)), (50, -70), hue="purple"), player_radius=999)
        result = match_query(q, (r,))
        self.assertEqual(classify(result), "unique_reference")
        self.assertEqual(result.pairs[0].hypotheses[0].offset_px, (50, -70))
