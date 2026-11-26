from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research.geometry_experiment.coordinates import angular_error, bearing, sector
from research.geometry_experiment.dataset import DatasetError, Geometry, Observation, load_dataset
from research.geometry_experiment.evaluate import run, training_labels, truth_bearing
from research.geometry_experiment.predict import fit, predict

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic"


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset(FIXTURES)
        cls.frames = {frame.observation_id: frame for frame in cls.dataset.frames}

    def with_changes(self, filename, change):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            for fixture in FIXTURES.glob("*.json"):
                data = json.loads(fixture.read_text(encoding="utf-8"))
                if fixture.name == filename:
                    change(data)
                (path / fixture.name).write_text(json.dumps(data), encoding="utf-8")
            return load_dataset(path)

    def test_duplicate_observation_id_is_rejected(self):
        with self.assertRaisesRegex(DatasetError, "duplicate observation ID"):
            self.with_changes("observations.json", lambda rows: rows.append(rows[0]))

    def test_duplicate_frame_under_new_id_is_rejected(self):
        with self.assertRaisesRegex(DatasetError, "duplicate frame"):
            self.with_changes("observations.json", lambda rows: rows.append({**rows[0], "observation_id": "new"}))

    def test_repeated_geometry_in_later_frame_is_valid(self):
        report, _, _ = run(self.dataset)
        replay = next(row for row in report["observations"] if row["observation_id"] == "audit-b-3")
        self.assertEqual(self.frames["audit-b-2"].observation, self.frames["audit-b-3"].observation)
        self.assertEqual((replay["stage"], replay["new_rooms"], replay["new_connections"]), (3, 0, 0))

    def test_invalid_coordinate_transformations(self):
        for key, value in (
            ("px_per_unit", 0), ("px_per_unit", float("inf")), ("px_per_unit", 1e-320),
            ("origin_px", [2]), ("residual_px", -1), ("anchor_count", 1),
        ):
            with self.subTest(key=key, value=value), self.assertRaisesRegex(DatasetError, "registration"):
                def change(rows):
                    rows[0]["registration"][key] = value
                    if value == 1e-320:
                        rows[0]["registration"]["residual_px"] = 1

                self.with_changes("observations.json", change)

    def test_conflicting_observations_are_rejected(self):
        def change(rows):
            rows[1]["observation"]["entrance_orientation"] = "NS"

        with self.assertRaisesRegex(DatasetError, "conflicting entrance"):
            self.with_changes("observations.json", change)

        def impossible_dead_end(rows):
            rows[2]["observation"]["dead_ends"] = [[0, 0]]

        with self.assertRaisesRegex(DatasetError, "conflicting dead end"):
            self.with_changes("observations.json", impossible_dead_end)

    def test_missing_target_label_is_excluded(self):
        self.assertEqual(truth_bearing(self.dataset, self.frames["held-d-1"], "WP"), ("missing_target", None))
        with self.assertRaisesRegex(DatasetError, r"targets fields"):
            self.with_changes("truth.json", lambda rows: rows[0]["targets"].pop("WP"))

    def test_discovered_targets_are_excluded_independently(self):
        report, _, _ = run(self.dataset)
        frame = next(row for row in report["observations"] if row["observation_id"] == "audit-b-3")
        self.assertEqual(frame["targets"]["NEXT"], {"eligibility": "visible"})
        self.assertEqual(frame["targets"]["WP"]["eligibility"], "eligible")
        with self.assertRaisesRegex(DatasetError, "forgets discovered NEXT"):
            def change(rows):
                rows[0]["visibility"]["dev-01-1"]["NEXT"] = "visible"

            self.with_changes("truth.json", change)

    def test_cross_split_group_and_transformed_layout_leakage(self):
        def reuse_group(meta):
            meta["layouts"][-1]["group_id"] = meta["layouts"][0]["group_id"]

        def rotate_and_translate(point):
            return [19 - point[1], 71 + point[0]]

        def reuse_geometry(rows):
            source = rows[0]["complete_geometry"]
            rows[-1]["complete_geometry"] = {
                "rooms": [rotate_and_translate(point) for point in source["rooms"]],
                "connections": [[rotate_and_translate(point) for point in edge] for edge in source["connections"]],
            }

        with self.assertRaisesRegex(DatasetError, "group .* reused"):
            self.with_changes("metadata.json", reuse_group)
        with self.assertRaisesRegex(DatasetError, "equivalent geometry"):
            self.with_changes("truth.json", reuse_geometry)

    def test_prediction_excludes_future_observations_and_evaluation_truth(self):
        before, _, _ = run(self.dataset)
        changed = self.with_changes("truth.json",
            lambda rows: rows[6]["targets"]["NEXT"].update(position=[-9, 0]))
        after_truth, _, _ = run(changed)

        def change_future(rows):
            frame = next(row for row in rows if row["observation_id"] == "audit-a-3")
            frame["observation"]["player_position"] = [-1, 0]
            frame["observation"]["visible_rooms"].append([2, 4])

        after_future, _, _ = run(self.with_changes("observations.json", change_future))

        def early_next(report):
            row = next(row for row in report["observations"] if row["observation_id"] == "audit-a-2")
            return row["targets"]["NEXT"]

        before_next, after_next = early_next(before), early_next(after_truth)
        self.assertNotEqual(before_next["true_sector"], after_next["true_sector"])
        for method, old in before_next["methods"].items():
            new = after_next["methods"][method]
            for key in ("status", "direction", "source", "support", "votes"):
                self.assertEqual(old[key], new[key])
        self.assertEqual(before_next, early_next(after_future))
        with self.assertRaisesRegex(DatasetError, "fields must be"):
            self.with_changes("observations.json", lambda rows: rows[0]["observation"].update(seed=123))

    def test_report_is_deterministic_and_shuffle_keeps_baseline(self):
        report, _, _ = run(self.dataset)
        repeated, _, _ = run(self.dataset)
        shuffled, _, _ = run(self.dataset, shuffle=True)
        self.assertEqual(report, repeated)
        self.assertEqual(report["three_room_checkpoint"]["layouts"], {"exactly_three": 3, "overshot_three": 1})
        for stage in report["stages"]:
            for target in ("NEXT", "WP"):
                original = report["stages"][stage]["targets"][target]["methods"]["entrance"]
                control = shuffled["stages"][stage]["targets"][target]["methods"]["entrance"]
                self.assertEqual(original, control)

    def test_position_disagreement_can_share_a_sector(self):
        def change(rows):
            for row in rows:
                if row["layout_id"] in ("audit-a", "audit-b"):
                    x = 3 if row["layout_id"] == "audit-a" else 4
                    row["targets"]["WP"]["position"] = [x, 0]

        data = self.with_changes("truth.json", change)
        report, _, _ = run(data)
        ambiguity = report["three_room_checkpoint"]["targets"]["WP"]["ambiguous_inputs"]
        self.assertEqual(ambiguity["conflicting_position_groups"], 1)
        self.assertEqual(ambiguity["conflicting_sector_groups"], 0)


class PredictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset(FIXTURES)
        cls.frames = {frame.observation_id: frame for frame in cls.dataset.frames}

    def test_empty_observation_insufficient(self):
        obs = self.frames["held-d-0"].observation
        for method in ("entrance", "geometry"):
            self.assertEqual(predict(fit([]), obs, method)["NEXT"]["status"], "INSUFFICIENT_DATA")

    def test_unknown_orientation_falls_back(self):
        obs = self.frames["held-d-1"].observation
        frames = [self.frames[f"{layout}-1"] for layout in ("dev-03", "dev-04")]
        samples = [(frame.observation, training_labels(self.dataset, frame)) for frame in frames]
        baseline = predict(fit(samples), obs, "entrance")
        self.assertEqual(baseline["NEXT"]["source"], "unconditional")
        self.assertEqual(baseline["NEXT"]["direction"], "N")
        axis_prior = predict(fit(samples), replace(obs, orientation="E"), "entrance")
        self.assertEqual((axis_prior["NEXT"]["source"], axis_prior["NEXT"]["direction"]), ("entrance", "N"))

    def test_phase_05_counterexample_geometry_and_targets(self):
        a, b = (self.frames[f"audit-{letter}-2"] for letter in "ab")
        self.assertEqual(a.observation, b.observation)
        self.assertEqual(a.observation.geometry.rooms, ((-1, 0), (0, 0), (1, 0)))
        self.assertEqual(a.observation.player, (0, 0))
        labels_a, labels_b = (self.dataset.targets[frame.layout_id] for frame in (a, b))
        self.assertEqual([label.position for label in labels_a.values()], [(1, 2), (3, 0)])
        self.assertEqual([label.position for label in labels_b.values()], [(1, -2), (1, -3)])
        sectors_a, sectors_b = (training_labels(self.dataset, frame) for frame in (a, b))
        model = fit([(a.observation, sectors_a), (b.observation, sectors_b)])
        for target in ("NEXT", "WP"):
            first = sector(truth_bearing(self.dataset, a, target)[1])
            second = sector(truth_bearing(self.dataset, b, target)[1])
            self.assertNotEqual(first, second)
            ambiguous = predict(model, b.observation, "geometry")[target]
            self.assertEqual(ambiguous["status"], "AMBIGUOUS")
            self.assertEqual(ambiguous["votes"], {first: 1, second: 1})
            self.assertIsNone(ambiguous["direction"])
            unique_fit = predict(fit([(a.observation, sectors_a)]), b.observation, "geometry")[target]
            self.assertEqual(unique_fit["status"], "UNKNOWN")
            self.assertIsNone(unique_fit["direction"])

    def test_symmetric_geometry_does_not_resolve_polarity(self):
        obs = self.frames["audit-b-2"].observation
        symmetric = Observation(None, obs.player, 0, obs.geometry, (), ())
        model = fit([
            (symmetric, training_labels(self.dataset, self.frames["audit-a-2"])),
            (symmetric, training_labels(self.dataset, self.frames["audit-b-2"])),
        ])
        self.assertIsNone(predict(model, symmetric, "geometry")["NEXT"]["direction"])

    def test_unknown_geometry_falls_back_or_abstains_when_unsupported(self):
        query = Observation("EW", (0, 0), 0, Geometry(((0, 0), (7, 3)), ()), (), ())
        frames = [self.frames[f"{layout}-2"] for layout in ("dev-03", "dev-04")]
        examples = [(frame.observation, training_labels(self.dataset, frame)) for frame in frames]
        supported = predict(fit(examples), query, "geometry")["NEXT"]
        self.assertEqual((supported["source"], supported["direction"]), ("entrance", "N"))
        self.assertEqual(predict(fit([]), query, "geometry")["NEXT"]["status"], "UNKNOWN")

    def test_unresolved_votes_and_boundary_uncertainty(self):
        obs = self.frames["dev-03-2"].observation
        north = {"NEXT": "N"}
        samples = [(obs, north), (obs, north), (obs, {"NEXT": None}), (obs, {"NEXT": None})]
        prediction = predict(fit(samples), obs, "geometry")["NEXT"]
        self.assertEqual((prediction["status"], prediction["unresolved"], prediction["support_share"]),
                         ("UNKNOWN", 2, 0.5))
        self.assertEqual(sector(22.5), "NE")
        self.assertEqual(sector(337.5), "N")
        self.assertIsNone(bearing((0, 0), (0, 0)))
        self.assertIsNone(bearing((0, 0), (4, -10), uncertainty=1))
        self.assertEqual(angular_error("N", 359), 1)


if __name__ == "__main__":
    unittest.main()
