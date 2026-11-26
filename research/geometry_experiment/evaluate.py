"""Join observed frames and hidden labels for training and scoring."""

from collections import Counter, defaultdict
from math import sqrt
from random import Random
from statistics import median
from time import perf_counter_ns

from .coordinates import angular_error, bearing, sector
from .dataset import SCENARIO, TARGETS, Dataset, Frame
from .predict import METHODS, fit, player_region, predict

STAGES = range(4)
SHUFFLE_SEED = 2718


def fit_stages(dataset, frames, shuffle):
    stages = {stage: [] for stage in STAGES}
    for frame in frames:
        stages[frame.stage].append((frame.observation, training_labels(dataset, frame)))
    if shuffle:
        rng = Random(SHUFFLE_SEED)
        for samples in stages.values():
            for target in TARGETS:
                strata = defaultdict(list)
                for obs, labels in samples:
                    if labels.get(target) is not None:
                        strata[(obs.orientation, player_region(obs))].append(labels)
                for rows in strata.values():
                    permuted = [labels[target] for labels in rows]
                    rng.shuffle(permuted)
                    for labels, label in zip(rows, permuted):
                        labels[target] = label
    return {stage: fit(samples) for stage, samples in stages.items()}


def truth_bearing(dataset: Dataset, frame: Frame, target: str) -> tuple[str, float | None]:
    visibility = dataset.visibility[frame.observation_id][target]
    label = dataset.targets[frame.layout_id][target]
    obs = frame.observation
    if visibility != "hidden":
        return visibility, None
    if label is None:
        return "missing_target", None
    if obs.player is None:
        return "missing_player", None
    angle = bearing(obs.player, label.position, obs.player_error + label.error)
    return ("eligible", angle) if angle is not None else ("uncertain_bearing", None)


def training_labels(dataset: Dataset, frame: Frame) -> dict[str, str | None]:
    labels = {}
    for target, state in dataset.visibility[frame.observation_id].items():
        if state == "hidden":
            _, angle = truth_bearing(dataset, frame, target)
            labels[target] = sector(angle) if angle is not None else None
    return labels


def replay_frame(dataset, frame, model):
    obs = frame.observation
    estimates = {method: predict(model, obs, method) for method in METHODS}
    results = {}
    for target in TARGETS:
        eligibility, angle = truth_bearing(dataset, frame, target)
        result = {"eligibility": eligibility}
        if angle is not None:
            actual = sector(angle)
            result["true_sector"] = actual
            outcomes = {}
            for method, pair in estimates.items():
                prediction = pair[target]
                direction = prediction["direction"]
                outcomes[method] = {
                    **prediction,
                    "correct": direction == actual if direction else None,
                    "angular_error_deg": angular_error(direction, angle) if direction else None,
                }
            result["methods"] = outcomes
        results[target] = result
    return {
        "layout_id": frame.layout_id,
        "observation_id": frame.observation_id,
        "stage": frame.stage,
        "visible_rooms": len(obs.geometry.rooms),
        "visible_connections": len(obs.geometry.connections),
        "uncertain_geometry": frame.uncertain_geometry,
        "targets": results,
    }


def fraction(count, total):
    return count / total if total else None


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * fraction
    below = int(index)
    above = min(below + 1, len(ordered) - 1)
    return ordered[below] + (ordered[above] - ordered[below]) * (index - below)


def wilson_interval(correct, n):
    if not n:
        return None
    proportion = correct / n
    z = 1.96
    denominator = 1 + z * z / n
    centre = (proportion + z * z / (2 * n)) / denominator
    half_width = z / denominator * sqrt(proportion * (1 - proportion) / n + z * z / (4 * n * n))
    return [max(0, centre - half_width), min(1, centre + half_width)]


def method_metrics(eligible, target, method):
    outcomes = [row["targets"][target]["methods"][method] for row in eligible]
    errors = [item["angular_error_deg"] for item in outcomes if item["direction"] is not None]
    count = len(errors)
    correct = sum(item["correct"] is True for item in outcomes)
    total = len(outcomes)
    return {
        "predictions": count,
        "correct": correct,
        "coverage": fraction(count, total),
        "accuracy": fraction(correct, count),
        "accuracy_wilson_95": wilson_interval(correct, count),
        "incorrect_per_prediction": fraction(count - correct, count),
        "incorrect_per_eligible": fraction(count - correct, total),
        "correct_per_eligible": fraction(correct, total),
        "abstention": fraction(total - count, total),
        "angular_error_median_deg": median(errors) if errors else None,
        "angular_error_p90_deg": percentile(errors, 0.9),
        "statuses": dict(Counter(item["status"] for item in outcomes)),
        "sources": dict(Counter(item["source"] for item in outcomes if "source" in item)),
    }


def paired_comparison(eligible, target, method):
    differences = []
    for row in eligible:
        estimates = row["targets"][target]["methods"]
        baseline, experimental = estimates["entrance"]["correct"], estimates[method]["correct"]
        if baseline is not None and experimental is not None:
            differences.append(int(experimental) - int(baseline))
    count = len(differences)
    interval = None
    if count >= 2:
        rng = Random(117)
        resamples = [sum(rng.choices(differences, k=count)) / count for _ in range(2000)]
        interval = [percentile(resamples, 0.025), percentile(resamples, 0.975)]
    return {
        "paired_layouts": count,
        "common_coverage": fraction(count, len(eligible)),
        "accuracy_lift": fraction(sum(differences), count),
        "lift_bootstrap_95": interval,
    }


def summarize(details, target, by_id, truth):
    counts = Counter(row["targets"][target]["eligibility"] for row in details)
    eligible = [row for row in details if row["targets"][target]["eligibility"] == "eligible"]
    equivalent = defaultdict(list)
    for row in eligible:
        obs = by_id[row["observation_id"]].observation
        label = truth[row["layout_id"]][target]
        equivalent[(row["stage"], obs)].append((label.position, row["targets"][target]["true_sector"]))
    repeated = [group for group in equivalent.values() if len(group) > 1]
    position_conflicts = [group for group in repeated if len({position for position, _ in group}) > 1]
    sector_conflicts = [group for group in repeated if len({direction for _, direction in group}) > 1]
    return {
        "eligibility": dict(counts),
        "ambiguous_inputs": {
            "repeated_groups": len(repeated),
            "conflicting_position_groups": len(position_conflicts),
            "layouts_in_position_conflicts": sum(map(len, position_conflicts)),
            "conflicting_sector_groups": len(sector_conflicts),
            "layouts_in_sector_conflicts": sum(map(len, sector_conflicts)),
        },
        "methods": {method: method_metrics(eligible, target, method) for method in METHODS},
        "paired_vs_entrance": {
            method: paired_comparison(eligible, target, method)
            for method in METHODS if method != "entrance"
        },
    }


def exploration_report(by_layout, by_id, truth):
    milestones = []
    reached = Counter()
    first_predictions = {}
    for layout, details in by_layout.items():
        primary = next((row for row in details if row["visible_rooms"] >= 3), None)
        if primary is None:
            reached["under_three"] += 1
        elif primary["visible_rooms"] == 3:
            milestones.append(primary)
            reached["exactly_three"] += 1
        else:
            reached["overshot_three"] += 1
        first_predictions[layout] = {}
        for target in TARGETS:
            first_predictions[layout][target] = {}
            for method in ("entrance", "geometry"):
                selected = next((row for row in details
                                 if row["targets"][target].get("methods", {}).get(method, {}).get("direction")), None)
                first_predictions[layout][target][method] = (
                    {key: selected[key] for key in ("stage", "visible_rooms")} if selected else None
                )
    fixed_cohort = {}
    for target in TARGETS:
        layouts = [
            details for details in by_layout.values() if len(details) == len(STAGES)
            and all(row["targets"][target]["eligibility"] == "eligible" for row in details)
        ]
        fixed_cohort[target] = {
            "layouts": len(layouts),
            "stages": {
                str(stage): summarize([rows[stage] for rows in layouts], target, by_id, truth)
                for stage in STAGES
            },
        }
    return {
        "three_room_checkpoint": {
            "layouts": dict(reached),
            "targets": {target: summarize(milestones, target, by_id, truth) for target in TARGETS},
        },
        "fixed_eligible_cohort": fixed_cohort,
        "first_predictions": first_predictions,
    }


def run(dataset: Dataset, *, development=False, shuffle=False):
    training = [frame for frame in dataset.frames if dataset.splits[frame.layout_id] == "development"]
    testing = [
        frame for frame in dataset.frames
        if dataset.splits[frame.layout_id] == ("development" if development else "evaluation")
    ]
    start = perf_counter_ns()
    test_layouts = sorted({frame.layout_id for frame in testing})
    if development:
        models = {
            layout: fit_stages(dataset, [frame for frame in training if frame.layout_id != layout], shuffle)
            for layout in test_layouts
        }
    else:
        fitted = fit_stages(dataset, training, shuffle)
        models = dict.fromkeys(test_layouts, fitted)
    fit_ms = (perf_counter_ns() - start) / 1_000_000
    by_id = {frame.observation_id: frame for frame in testing}
    by_layout = {layout: [] for layout in test_layouts}
    by_stage = {stage: [] for stage in STAGES}
    previously_seen = {}
    for frame in testing:
        detail = replay_frame(dataset, frame, models[frame.layout_id][frame.stage])
        old_rooms, old_connections = previously_seen.setdefault(frame.layout_id, (set(), set()))
        geo = frame.observation.geometry
        detail["new_rooms"] = len(set(geo.rooms) - old_rooms)
        detail["new_connections"] = len(set(geo.connections) - old_connections)
        old_rooms.update(geo.rooms)
        old_connections.update(geo.connections)
        by_layout[frame.layout_id].append(detail)
        by_stage[frame.stage].append(detail)
    report = {
        "protocol_version": 1,
        "dataset_id": dataset.dataset_id,
        "kind": dataset.kind,
        "scenario": SCENARIO,
        "capture": dataset.capture,
        "input_sha256": dataset.hashes,
        "split": "development_leave_one_layout_out" if development else "evaluation",
        "shuffled_training_labels": shuffle,
        "shuffle_seed": SHUFFLE_SEED if shuffle else None,
        "development_layouts": len({frame.layout_id for frame in training}),
        "scored_split_layouts": len(test_layouts),
        "calibrated_confidence": False,
        "stages": {
            str(stage): {
                "frames": len(details),
                "absent_frames": len(test_layouts) - len(details),
                "uncertain_geometry_frames": sum(row["uncertain_geometry"] for row in details),
                "targets": {target: summarize(details, target, by_id, dataset.targets) for target in TARGETS},
            }
            for stage, details in by_stage.items()
        },
        **exploration_report(by_layout, by_id, dataset.targets),
        "observations": [detail for details in by_layout.values() for detail in details],
    }
    profiling_cases = [(models[frame.layout_id][frame.stage], frame.observation) for frame in testing]
    return report, fit_ms, profiling_cases
