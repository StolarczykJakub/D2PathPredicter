from dataclasses import asdict
import unittest

from research.marker_fingerprint.bounded_match import LIMITS, Limits, match_query
from research.marker_fingerprint.calibrate import Observation, trial_result
from research.marker_fingerprint.match import Marker, Markers, constellation, match


def marks(points, radius=4):
    return Markers(tuple(sorted(Marker(p, "yellow", radius) for p in points)), 1)


class BoundedMatchTests(unittest.TestCase):
    def test_frozen_caps_and_repeat_motifs(self):
        self.assertEqual(tuple(asdict(LIMITS).values()), (24, 24, 100_000, 256, 600_000))
        points = ((0, 0), (25, 1), (6, 30))
        q = marks(points)
        r = marks(tuple((x + s, y) for s in (0, 120) for x, y in points))
        result = match_query(q, (r,), "B", 8)
        self.assertIsNone(result.stop)
        self.assertEqual({h.offset_px for h in result.pairs[0].hypotheses}, {(0, 0), (120, 0)})
        self.assertTrue(all(h.alignment_2d for h in result.pairs[0].hypotheses))
        q_view = Observation("pilot", "a", "q", (0, 0), q, q, True)
        r_view = Observation("pilot", "a", "r", (0, 0), r, r, True)
        view = trial_result("B", "same_frame", "q", ("r",), {"q": q_view, "r": r_view}, result)
        self.assertEqual(view["candidate_region_count"], 1)
        self.assertEqual(view["outcome"], "ambiguous_correspondences")

    def test_bounded_matches_stage1_at_original_cap(self):
        q = marks(((0, 0), (20, -3), (3, 30)))
        r = marks(((25, -2), (7, 31), (4, 2), (120, 70)))
        for mode in ("A", "B"):
            a, b = (constellation(q), constellation(r)) if mode == "B" else (q, r)
            for left, right, original_left, original_right in ((q, r, a, b), (r, q, b, a)):
                current = match_query(left, (right,), mode, 8).pairs[0]
                self.assertEqual(tuple(asdict(h) for h in current.hypotheses), match(original_left, original_right))

    def test_insufficient_point_support_and_two_point_alignment(self):
        q = marks(((0, 0), (30, 0)))
        self.assertEqual(match_query(marks(((0, 0),)), (q,), "B", 8).stop, "insufficient_query")
        self.assertEqual(match_query(q, (None,), "A", 8).pairs[0].stop, "insufficient_reference")
        match_ = match_query(q, (q,), "B", 8)
        view = Observation("pilot", "a", "q", (0, 0), q, q, True)
        self.assertEqual(trial_result("B", "same_frame", "q", ("r",), {"q": view, "r": view}, match_)["outcome"],
                         "unresolved_2d")

    def test_marker_and_reference_limits(self):
        q = marks(((0, 0), (30, 0)))
        self.assertEqual(match_query(q, (q,) * 25, "A", 8).stop, "references")
        self.assertEqual(match_query(q, (marks(((0, 0),) * 25),), "A", 8).stop, "markers")

    def test_hypothesis_limit_keeps_partial_evidence_but_abstains(self):
        q = marks(((0, 0),) * 6)
        result = match_query(q, (q,), "B", 8)
        self.assertEqual(result.stop, "pair_hypotheses")
        self.assertEqual((result.pairs[0].hypotheses_seen, len(result.pairs[0].hypotheses)), (257, 256))
        view = Observation("pilot", "a", "q", (0, 0), q, q, True)
        evaluated = trial_result("B", "same_frame", "q", ("r",), {"q": view, "r": view}, result)
        self.assertEqual(evaluated["outcome"], "unresolved_search_budget")

    def test_pair_prefix_limit_never_becomes_no_match(self):
        q = marks(((0, 0),) * 9)
        r = marks(((0, 0),) * 8 + ((100, 100),))
        result = match_query(q, (r,), "A", 8)
        self.assertEqual((result.stop, result.prefixes), ("pair_prefixes", 100_000))
        self.assertFalse(result.pairs[0].hypotheses)
        a = Observation("pilot", "a", "q", (0, 0), q, q, True)
        b = Observation("pilot", "b", "r", (0, 0), r, r, True)
        evaluated = trial_result("A", "same_frame", "q", ("r",), {"q": a, "r": b}, result)
        self.assertEqual(evaluated["outcome"], "unresolved_search_budget")

    def test_query_budget_is_shared_across_completed_pairs(self):
        q = marks(((-8, 0),) + ((0, 0),) * 8)
        r = marks(((0, 0),) * 7 + ((8, 0), (100, 100)))
        result = match_query(q, (r,) * 8, "A", 8)
        self.assertEqual((result.stop, result.prefixes), ("query_prefixes", 600_000))
        self.assertEqual(sum(p.stop is None for p in result.pairs), 6)
        self.assertEqual(len(result.pairs), 7)

    def test_exact_limit_with_complete_search_is_allowed(self):
        q = marks(((0, 0), (30, 0)))
        cfg = Limits(pair_prefixes=3, query_prefixes=3, pair_hypotheses=1)
        result = match_query(q, (q,), "A", 8, limits=cfg)
        self.assertIsNone(result.stop)
        self.assertEqual(result.prefixes, 3)
        self.assertEqual(len(result.pairs[0].hypotheses), 1)


if __name__ == "__main__":
    unittest.main()
