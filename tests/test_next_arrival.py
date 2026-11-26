import unittest

from research.geometry_experiment.next_arrival import (
    Observation, Reference, entrance, geometry, stable_sector, unconditional,
)
from research.marker_fingerprint.match import Marker, Markers


def observation(orientation=None, shift=(0, 0)):
    markers = Markers(tuple(Marker((x + shift[0], y + shift[1]), hue, 2)
                            for x, y, hue in ((0, 0, "yellow"), (60, 0, "purple"),
                                              (0, 70, "unknown"))), 5)
    return Observation(shift, 5, orientation, markers)


class NextArrivalTests(unittest.TestCase):
    def test_prior_requires_two_votes_and_two_thirds(self):
        refs = [Reference(observation(), sector) for sector in ("-Y", "-Y", "+Y", "+X")]
        self.assertIsNone(unconditional(refs[:1])["sector"])
        self.assertEqual(unconditional(refs[:3])["sector"], "-Y")
        self.assertIsNone(unconditional(refs)["sector"])

    def test_entrance_pools_axis_without_unconditional_fallback(self):
        refs = [Reference(observation(h), "-Y") for h in ("NE", "NE_SW", "SW")]
        self.assertEqual(entrance(refs, observation("NE"))["bucket"], "NE_SW")
        self.assertEqual(entrance(refs, observation("SW"))["sector"], "-Y")
        self.assertIsNone(entrance(refs, observation("N"))["sector"])
        self.assertIsNone(entrance(refs, observation())["sector"])
        tied = [Reference(observation("NE"), s) for s in ("-Y", "+Y")]
        self.assertIsNone(entrance(tied + refs[1:], observation("NE"))["sector"])

    def test_sector_requires_strict_boundary_clearance(self):
        self.assertEqual([stable_sector((0, 0), p, 2) for p in
                          ((3, -3), (3, 3), (-3, 3), (-3, -3))],
                         ["-Y", "+X", "+Y", "-X"])
        self.assertIsNone(stable_sector((0, 0), (2, -3), 2))

    def test_geometry_inverts_offset_and_abstains_on_conflict(self):
        query = observation(shift=(400, 600))
        a = Reference(observation(shift=(100, 250)), "-Y", (180, 160), 5)
        b = Reference(observation(shift=(200, 300)), "-Y", (280, 210), 5)
        self.assertEqual(geometry([a, b], query)["sector"], "-Y")
        self.assertIsNone(geometry([a], query)["sector"])
        c = Reference(b.observation, "+Y", (120, 390), 5)
        self.assertIn("competing_sectors", geometry([a, b, c], query)["reasons"])

    def test_geometry_carries_missing_truth_and_search_status(self):
        query = observation()
        a = Reference(observation(), "-Y", (80, -90), 5)
        b = Reference(observation(), "-Y")
        self.assertIn("missing_target", geometry([a, a, b], query)["reasons"])
        self.assertIn("references", geometry([a] * 25, query)["reasons"])
