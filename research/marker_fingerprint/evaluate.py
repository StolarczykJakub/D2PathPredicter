"""Run Stage 1 against the existing eight V2 returns from the project root."""

from collections import Counter
from dataclasses import asdict, dataclass
from functools import cache
from hashlib import sha256
from itertools import combinations
import json
from math import dist
from pathlib import Path
import platform
from statistics import median, quantiles
from time import perf_counter_ns
import tracemalloc
from zipfile import ZipFile

from research.annotation_retest.evaluate import BASE, read_json, require, validate
from research.geometry_experiment.blind_packets import verify_image
from research.marker_fingerprint.match import (
    Crop, Markers, constellation, match, player_markers, wall_coverage, wall_shortlist, wall_union,
)


PROTOCOL = Path("docs/MARKER_FINGERPRINT_POC_PROTOCOL.md")
V1 = BASE.parent / "phase-1-6"
LOCK = V1 / "role-c/pilot-lock.json"
REGISTRATION = V1 / "role-c/pilot-validation/registration-recheck.json"
OUTPUT = Path("local-data/phase-1-6-2")
FRAME_PACKETS = (("h9v2c", "k4m7q"), ("p6r8t", "w3j5n"))
STAGES = (0, 3)
REGISTRATION_ALLOWANCE = 6
LANDMARK_LIMIT = 8
SINGLE_DELETION_MIN = 0.80


@dataclass(frozen=True, slots=True)
class Observation:
    origin: tuple
    markers: Markers
    segments: tuple

    @property
    def walls(self):
        return wall_union(self.segments, self.origin)


def verified_bytes(path, digest):
    value = path.read_bytes()
    require(sha256(value).hexdigest() == digest, f"SHA-256 mismatch for {path}")
    return value


def load_inputs():
    """Verify before any comparison, reading the return store without changing it."""
    release = read_json((BASE / "owner/manifest.json").read_bytes())
    prior = read_json(verified_bytes(LOCK, release["prior_lock_sha256"]))
    for paths in (release["frozen_sha256"], prior["implementation_sha256"]):
        for name, checksum in paths.items():
            verified_bytes(Path(name), checksum)
    for name, checksum in prior["blind_release_sha256"].items():
        verified_bytes(V1 / "role-a-release" / name, checksum)

    intake = read_json((BASE / "owner/derived/intake.json").read_bytes())
    assignments = {entry["packet_id"]: entry for entry in release["assignments"]}
    observations = {"raw": {}, "semantic": {}}
    raw_rows = {}
    for stage, packets in zip(STAGES, FRAME_PACKETS):
        for packet in packets:
            item = assignments[packet]
            require(item["source_stage"] == stage, f"unexpected stage for {packet}")
            archive = BASE / "release" / item["filename"]
            verified_bytes(archive, item["archive_sha256"])
            with ZipFile(archive) as zipped:
                frame = zipped.read("frame.png")
                require(sha256(frame).hexdigest() == item["frame_sha256"], f"frame hash for {packet}")
                verify_image(frame)
                for task in observations:
                    entry, = (row for row in intake if (row["packet_id"], row["pass"]) == (packet, task))
                    frozen_path = BASE / "returns" / packet / (task + ".json")
                    require(frozen_path.as_posix() == entry["original"], f"frozen return path for {packet}")
                    original = verified_bytes(frozen_path, entry["sha256"])
                    require(original == Path(entry["source"]).read_bytes() and
                            len(original) == entry["byte_count"], f"return bytes for {packet} {task}")
                    row = read_json(original)
                    validate(row, read_json(zipped.read(task + ".json")), task)
                    player = row["player"]
                    require(player["status"] == "OBSERVED", f"unobserved player in frozen {packet} {task}")
                    item_segments = tuple(w["segment_px"] for w in row["walls"])
                    observations[task][packet] = Observation(
                        tuple(player["px"]), player_markers(row["markers"], player), item_segments)
                    if task == "raw":
                        raw_rows[packet] = row

    registration = read_json(REGISTRATION.read_bytes())["checkpoints"]
    registration = [registration[f"stage-{stage}"]["pixel_check"] for stage in STAGES]
    for check in registration:
        require(check["matches"] >= 3 and check["longest_baseline_px"] >= 64 and
                check["off_axis_max_px"] > 6 and 0.97 <= check["scale_ratio"] <= 1.03 and
                abs(check["rotation_degrees"]) <= 2 and
                max(check["max_fitted_residual_px"], check["max_holdout_residual_px"]) <= 6,
                "frozen registration does not pass")
    return observations, raw_rows, {entry["original"]: entry["sha256"] for entry in intake}, [
        tuple(check["translation"]) for check in registration]


def registered_cloud(markers, origin, translation):
    return tuple((tuple(x + p + t for x, p, t in zip(mark.point, origin, translation)),
                  mark.hue, mark.radius) for mark in markers.points)


def region_relation(query, other):
    if any(qa == ra != "unknown" and dist(q, r) <= LANDMARK_LIMIT
           for q, qa, _ in query for r, ra, _ in other):
        return "overlap"
    for axis in (0, 1):
        a, b = ((min(p[axis] - r - REGISTRATION_ALLOWANCE for p, _, r in marks),
                 max(p[axis] + r + REGISTRATION_ALLOWANCE for p, _, r in marks))
                for marks in (query, other))
        if a[1] < b[0] or b[1] < a[0]:
            return "distinct"
    return "unresolved"


def control_trials(markers, other, frame_index):
    n = len(markers.points)
    yield "full", markers, other, None, ()
    b = other if frame_index == 0 else markers
    for indices in combinations(range(len(b.points)), 3):
        subset = b.select(indices)
        yield "size_3", markers if frame_index == 0 else subset, (
            subset if frame_index == 0 else other), None, indices
    for i in range(n):
        yield "delete_1", markers.select(j for j in range(n) if j != i), other, None, (i,)
    for name, fraction in (("crop_25", 0.25), ("crop_50", 0.50)):
        remove = int(n * fraction + 0.5)
        for axis in (0, 1):
            coordinates = sorted(point.point[axis] for point in markers.points)
            for high in (False, True):
                edge = coordinates[remove if high else n - remove - 1]
                crop = Crop(axis, high, edge)
                indices = tuple(i for i, point in enumerate(markers.points) if crop.contains(point.point))
                yield name, markers.select(indices), other, crop, indices


def outcome(alignments, candidates, relation, require_2d=False):
    if not candidates:
        return "no_match"
    if len(candidates) > 1:
        return "ambiguous_regions"
    i = candidates[0]
    if len(alignments[i]) > 1:
        return "ambiguous_alignments"
    if require_2d and not alignments[i][0]["alignment_2d"]:
        return "unresolved_alignment"
    if i == 0:
        return "correct_unique"
    return "false_unique" if relation == "distinct" else "unverified_cross_only"


def result_view(alignments, candidates, relation, require_2d=False):
    scores = [side[0]["score"] if side else None for side in alignments]
    same, cross = (index in candidates for index in (0, 1))
    margin = scores[1] - scores[0] if None not in scores else None
    better = same and (not cross or (margin is not None and margin > 0))
    return {
        "compatible": (same, cross), "scores": scores, "margin": margin, "same_better": better,
        "outcome": outcome(alignments, candidates, relation, require_2d),
        "alignments": [len(a) for a in alignments],
    }


def experiment(observations, translations):
    @cache
    def hypotheses(mode, left, right):
        if mode == "B":
            return match(descriptors(left), descriptors(right))
        return match(left, right)

    descriptors = cache(constellation)
    footprints = {packet: observation.walls for packet, observation in observations.items()}

    @cache
    def compare_walls(left, right, crop):
        return wall_coverage(footprints[left], footprints[right],
                             (observations[left].origin, observations[right].origin), crop)

    trials = []
    for f, packets in enumerate(FRAME_PACKETS):
        for i, query_id in enumerate(packets):
            same_id = packets[1 - i]
            other_id = FRAME_PACKETS[1 - f][1 - i]
            query, same, other = (observations[p] for p in (query_id, same_id, other_id))
            for kind, selected, other_selected, crop, indices in control_trials(query.markers, other.markers, f):
                eligible = len(selected.points) >= 2 and len(other_selected.points) >= 2
                record = {
                    "kind": kind, "query": query_id, "reference": [same_id, other_id],
                    "frame": "AB"[f], "indices": indices, "crop": asdict(crop) if crop else None,
                    "markers": [len(s.points) for s in (selected, same.markers, other_selected)],
                    "removed_from_query": len(query.markers.points) - len(selected.points),
                    "eligible": eligible,
                }
                trials.append(record)
                if not eligible:
                    continue
                relation = region_relation(registered_cloud(selected, query.origin, translations[f]),
                                           registered_cloud(other_selected, other.origin, translations[1 - f]))
                record["relation"] = relation
                for mode in ("A", "B"):
                    alignments = (hypotheses(mode, selected, same.markers),
                                  hypotheses(mode, selected, other_selected))
                    candidates = tuple(j for j, a in enumerate(alignments) if a)
                    record[mode] = result_view(alignments, candidates, relation, mode == "B")
                    record[mode]["correspondences"] = alignments
                    if mode == "A":
                        evidence = tuple(compare_walls(query_id, ref, crop) for ref in (same_id, other_id))
                        shortlist = wall_shortlist(candidates, tuple(v["supports"] for v in evidence))
                        record["C"] = result_view(alignments, shortlist, relation)
                        record["C"]["wall_evidence"] = evidence
    return trials


def summarize(trials):
    summaries = {}
    for group in ("full", "size_3", "delete_1", "crop_25", "crop_50", "two_markers", "all"):
        if group == "all":
            selected = trials
        elif group == "two_markers":
            selected = [r for r in trials if r["markers"][0] == 2]
        else:
            selected = [r for r in trials if r["kind"] == group]
        eligible = [r for r in selected if r["eligible"]]
        result = {"trials": len(selected), "eligible": len(eligible),
                  "ineligible": len(selected) - len(eligible),
                  "removals": Counter(r["removed_from_query"] for r in selected),
                  "relations": Counter(r["relation"] for r in eligible)}
        for mode in ("A", "B", "C"):
            distinct = [r for r in eligible if r["relation"] == "distinct"]
            compat = [r for r in eligible if r[mode]["compatible"][0]]
            collisions = [r for r in eligible if r[mode]["compatible"][1]]
            result[mode] = {
                "same_compatible": len(compat),
                "cross_compatible": Counter(r["relation"] for r in collisions),
                "distinct_same_better": sum(r[mode]["same_better"] for r in distinct),
                "distinct_trials": len(distinct),
                "outcomes": Counter(r[mode]["outcome"] for r in eligible),
                "alignments": [sum(r[mode]["alignments"][i] for r in eligible) for i in (0, 1)],
                "max_cross_alignments": max((r[mode]["alignments"][1] for r in eligible), default=0),
                "distinct_cross_only": sum(r[mode]["compatible"] == (False, True) for r in distinct),
            }
        summaries[group] = result
    return summaries


def gates(passes, synthetic):
    def gate(passed):
        return "PASS" if passed else "FAIL"

    raw = passes["raw"]["summary"]
    semantic = passes["semantic"]["summary"]
    compared = passes["raw"]["trials"]
    removed = [row for row in compared if row["eligible"] and
               row["relation"] == "distinct" and row["A"]["compatible"][1] and
               not row["C"]["compatible"][1]]
    lost = [row for row in compared if row["eligible"] and row["A"]["compatible"][0] and
            not row["C"]["compatible"][0]]
    walls = [row["disk"] for row in passes["raw"]["walls"].values()]
    output = {
        "synthetic_split_merge": gate(synthetic["identical"]),
        "raw_wall_repeatability": (gate(all(row["supports"] for row in walls))
                                   if all(row["fractions"] is not None for row in walls)
                                   else "NOT EVALUABLE"),
        "incremental_wall_discrimination": gate(bool(removed) and not lost),
        "wrong_candidates_dropped": len(removed), "same_candidates_dropped": len(lost),
    }
    for mode in ("A", "B", "C"):
        def discrimination(group):
            comparable = raw[group][mode]["distinct_trials"]
            return (gate(raw[group][mode]["distinct_same_better"] == comparable)
                    if comparable else "NOT EVALUABLE")

        deletions = raw["delete_1"]["eligible"]
        output[mode] = {
            "full_raw": gate(raw["full"][mode]["same_compatible"] == 4),
            "full_semantic": gate(semantic["full"][mode]["same_compatible"] == 4),
            "raw_false_unique": (gate(raw["all"][mode]["outcomes"].get("false_unique", 0) == 0)
                                 if raw["all"][mode]["distinct_trials"] else "NOT EVALUABLE"),
            "raw_distinct_full_margin": discrimination("full"),
            "raw_distinct_size_3_margin": discrimination("size_3"),
            "raw_single_deletion": (
                gate(raw["delete_1"][mode]["same_compatible"] / deletions >= SINGLE_DELETION_MIN)
                if deletions else "NOT EVALUABLE"),
        }
    return output


SYNTHETIC_SEGMENTS = (
    ((-70, -20), (-30, -20), (30, -20)),
    ((0, -80), (0, -20), (0, 20)),
    ((-72, -36), (-36, -18), (60, 30)),
    ((-72, 40), (-64, 44), (-40, 56)),
    ((-28, 62), (-20, 66), (-4, 74)),
    ((84, -42), (90, -45), (132, -66)),
)


def invariance():
    merged = wall_union(tuple((start, end) for start, _, end in SYNTHETIC_SEGMENTS))
    split = wall_union(tuple(edge for start, mid, end in reversed(SYNTHETIC_SEGMENTS)
                             for edge in ((end, mid), (mid, start))))
    return {"identical": merged == split, "union_pixels": len(merged),
            "synthetic_coverage": wall_coverage(merged, split, ((960, 540), (960, 540)))}


def timings(functions):
    values = []
    for f in functions:
        for _ in range(10):
            f()
        for _ in range(100):
            start = perf_counter_ns()
            f()
            values.append((perf_counter_ns() - start) / 1_000)
    peak = 0
    for f in functions:
        tracemalloc.start()
        try:
            f()
            peak = max(peak, tracemalloc.get_traced_memory()[1])
        finally:
            tracemalloc.stop()
    return {"calls": len(values), "p50_us": median(values),
            "p95_us": quantiles(values, n=20, method="inclusive")[-1], "peak_traced_bytes": peak}


def performance(observations, raw_rows):
    def construct(mode, packet):
        row = raw_rows[packet]
        markers = player_markers(row["markers"], row["player"])
        if mode == "B":
            return constellation(markers)
        if mode == "C":
            walls = wall_union(observations[packet].segments, observations[packet].origin)
            return markers, walls
        return markers

    def shortlist_pair(q, r):
        qm, qw = built[q]
        rm, rw = built[r]
        return match(qm, rm), wall_coverage(qw, rw, (observations[q].origin, observations[r].origin))

    def encoded_size(value):
        if isinstance(value, tuple):
            markers, wall = value
            data = [asdict(markers), sorted(wall)]
        else:
            data = asdict(value)
        return len(json.dumps(data, separators=(",", ":")).encode())

    results = {}
    pairs = [(p, r) for f, packets in enumerate(FRAME_PACKETS) for i, p in enumerate(packets)
             for r in (packets[1 - i], FRAME_PACKETS[1 - f][1 - i])]
    for mode in ("A", "B", "C"):
        built = {packet: construct(mode, packet) for packet in observations}
        operations = [(lambda q=q, r=r: shortlist_pair(q, r)) if mode == "C"
                      else (lambda q=q, r=r: match(built[q], built[r])) for q, r in pairs]
        results[mode] = {
            "construction": timings([lambda p=p: construct(mode, p) for p in observations]),
            "pair_comparison": timings(operations),
            "descriptor_bytes": {p: encoded_size(value) for p, value in built.items()},
        }
    return results


def main():
    observations, raw_rows, hashes, translations = load_inputs()
    results = {
        "protocol_sha256": sha256(PROTOCOL.read_bytes()).hexdigest(),
        "registration_sha256": sha256(REGISTRATION.read_bytes()).hexdigest(),
        "v2_sha256": hashes, "pinned_v1_files_verified": True,
        "synthetic_split_merge": invariance(), "translations_px": translations,
        "python": platform.python_version(), "platform": platform.platform(),
        "processor": platform.processor(), "passes": {},
    }
    for task, figures in observations.items():
        trials = experiment(figures, translations)
        walls = {}
        for f, (p, r) in enumerate(FRAME_PACKETS):
            a, b = figures[p], figures[r]
            full_a, full_b = (wall_union(row.segments, row.origin, bounded=False) for row in (a, b))
            walls["AB"[f]] = {
                "disk": wall_coverage(a.walls, b.walls, (a.origin, b.origin)),
                "full_sample": wall_coverage(full_a, full_b, (a.origin, b.origin), full_sample=True),
            }
        results["passes"][task] = {"summary": summarize(trials), "walls": walls, "trials": trials}
    results["gates"] = gates(results["passes"], results["synthetic_split_merge"])
    results["performance"] = performance(observations["raw"], raw_rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    output = OUTPUT / "results.json"
    with output.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
