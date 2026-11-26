import unittest

from research.marker_fingerprint.evaluate import control_trials, invariance, outcome, region_relation
from research.marker_fingerprint.match import (
    Marker, Markers, constellation, match, player_markers, wall_coverage, wall_shortlist, wall_union,
)


def marks(points, radius=0):
    return Markers(tuple(sorted(Marker(p, "yellow", radius) for p in points)), 0)


class FingerprintTests(unittest.TestCase):
    def test_marker_ids_and_input_order_do_not_change_descriptor(self):
        player = {"px": [10, 20], "error_px": 4}
        def mark(x, y, id_):
            return {"center_px": (x, y), "id": id_, "appearance": "yellow",
                    "error_px": 2, "status": "OBSERVED"}
        a = player_markers([mark(2, 3, "m1"), mark(7, 9, "m2")], player)
        b = player_markers([mark(7, 9, "k"), mark(2, 3, "j")], player)
        self.assertEqual(a, b)
        self.assertEqual(a.points[0].point, (-8, -17))
        self.assertEqual(match(a, b)[0]["score"], 0.0)

    def test_position_hue_gate_and_combined_uncertainty(self):
        a = Markers((Marker((0, 0), "yellow", 1), Marker((0, 40), "purple", 1)), 1)
        b = Markers((Marker((4, 0), "yellow", 1), Marker((4, 40), "purple", 1)), 1)
        self.assertEqual(match(a, b)[0]["score"], 1.0)
        self.assertFalse(match(a, Markers(b.points, 0)))
        swapped = Markers((Marker((4, 0), "purple", 1), Marker((4, 40), "yellow", 1)), 1)
        self.assertFalse(match(a, swapped))

    def test_constellation_preserves_axes_and_all_translations(self):
        a = marks(((0, 0), (15, 0), (4, 10)))
        b = marks(tuple((x + i, y + 30) for i in (20, 80)
                        for x, y in ((0, 0), (15, 0), (4, 10))))
        self.assertFalse(match(a, b))
        alignments = match(constellation(a), constellation(b))
        self.assertEqual({alignment["offset_px"] for alignment in alignments}, {(20, 30), (80, 30)})
        self.assertTrue(all(alignment["alignment_2d"] for alignment in alignments))
        self.assertEqual(outcome((alignments, ()), (0,), "distinct", True), "ambiguous_alignments")
        reversed_query = match(constellation(b), constellation(a))
        self.assertEqual({alignment["offset_px"] for alignment in reversed_query}, {(-20, -30), (-80, -30)})
        for transformed in (
            tuple((5 - y, x + 40) for x, y in ((0, 0), (15, 0), (4, 10))),
            tuple((5 - x, y + 40) for x, y in ((0, 0), (15, 0), (4, 10))),
        ):
            self.assertFalse(match(constellation(a), constellation(marks(transformed))))

    def test_two_points_can_match_without_2d_alignment(self):
        a = constellation(marks(((0, 0), (15, 0))))
        b = constellation(marks(((20, 5), (35, 5))))
        alignments = match(a, b)
        self.assertEqual(len(alignments), 1)
        self.assertFalse(alignments[0]["alignment_2d"])
        self.assertEqual(outcome((alignments, ()), (0,), "distinct", True), "unresolved_alignment")
        self.assertFalse(match(constellation(marks(((0, 0),))), b))

    def test_crop_and_size_control_enumeration(self):
        a = marks(((0, 0), (1, 1), (2, 2)))
        b = marks(tuple((i, 2 * i) for i in range(5)))
        runs = list(control_trials(a, b, 0))
        self.assertEqual(sum(kind == "size_3" for kind, *_ in runs), 10)
        self.assertEqual([len(selected.points) for kind, selected, *_ in runs if kind == "delete_1"], [2] * 3)
        self.assertEqual([len(selected.points) for kind, selected, *_ in runs if kind == "crop_50"], [1] * 4)

    def test_wall_invariance_bounds_gap_and_missing_evidence(self):
        self.assertTrue(invariance()["identical"])
        occupied = wall_union((((-4, 0), (-2, 0)), ((2, 0), (128, 0))))
        self.assertNotIn((0, 0), occupied)
        self.assertNotIn((121, 0), occupied)
        original = frozenset({(0, 0), (20, 0)})
        other = frozenset({(3, 0)})
        coverage = wall_coverage(original, other, ((960, 540), (960, 540)))
        self.assertEqual(coverage["fractions"], (0.5, 1.0))
        self.assertIsNone(wall_coverage(original, frozenset(), ((960, 540), (960, 540)))["fractions"])
        self.assertEqual(wall_shortlist((0,), (False, True)), (0,))
        self.assertEqual(wall_shortlist((0, 1), (False, True)), (1,))

    def test_evaluator_distinguishes_overlap_and_unverified_cross_only(self):
        a = (((0, 0), "yellow", 2),)
        self.assertEqual(region_relation(a, (((4, 0), "yellow", 2),)), "overlap")
        self.assertEqual(region_relation(a, (((16, 0), "purple", 2),)), "unresolved")
        self.assertEqual(region_relation(a, (((17, 0), "yellow", 2),)), "distinct")
        alignment = ({"alignment_2d": True},)
        self.assertEqual(outcome(((), alignment), (1,), "overlap"), "unverified_cross_only")
        self.assertEqual(outcome(((), alignment), (1,), "distinct"), "false_unique")


if __name__ == "__main__":
    unittest.main()
