"""Run the frozen Phase 1.6.4 diagnostic using development and calibration only."""

import argparse
from collections import Counter
from dataclasses import asdict, dataclass, replace
from itertools import product
from math import dist
from pathlib import Path
import platform

from research.annotation_retest.evaluate import read_json, require
from research.annotation_retest.prepare import digest, json_bytes
from research.marker_fingerprint.bounded_match import LIMITS, Limits, match_query as strict
from research.marker_fingerprint.calibrate import LOCK_PATH, OWNER, Observation, hypothesis_evidence, observation
from research.marker_fingerprint.evaluate import FRAME_PACKETS, STAGES, load_inputs, timings
from research.marker_fingerprint.independent_packets import checked_file
from research.marker_fingerprint.match import Marker, Markers, player_markers
from research.marker_fingerprint.partial_match import (
    BUDGET_STOPS, alignment_supported, box_area, classify, match_query, required_count, span_fraction,
)


OUTPUT = Path("local-data/phase-1-6-4")
FREEZE = OUTPUT / "before-comparisons.json"
SOURCES = (
    "docs/PARTIAL_CONSTELLATION_PROTOCOL.md",
    "research/marker_fingerprint/partial_match.py",
    "research/marker_fingerprint/evaluate_partial.py",
    "tests/test_partial_match.py",
)
LOCK_HASH = "97ce79e547ef756100fe93e0aee838f65500ac893fdae3b0d466181d73e8773a"


@dataclass(frozen=True, slots=True)
class Candidate:
    id: str
    view: Observation
    truth: frozenset | None = None


@dataclass(frozen=True, slots=True)
class Trial:
    group: str
    id: str
    query: Observation
    candidates: tuple[Candidate, ...]
    expected: str = ""
    limits: Limits = LIMITS


def region(view):
    return view.layout, view.region


def geometry_support(query, reference, pairs):
    if pairs is None or len(pairs) < required_count(len(query.points), len(reference.points)):
        return False
    left, right = zip(*((query.points[i], reference.points[j]) for i, j in sorted(pairs)))
    return alignment_supported(left, right, (span_fraction(left, box_area(query.points)),
                                              span_fraction(right, box_area(reference.points))))


def registered_truth(query, reference):
    """Use the frozen wall-derived shifts to label markers independently of the matcher."""
    registered = [tuple((tuple(x + t for x, t in zip(m.point, v.translation)), m.hue)
                        for m in v.native.points) for v in (query, reference)]
    pairs = [(i, j) for i, (a, ah) in enumerate(registered[0])
             for j, (b, bh) in enumerate(registered[1]) if ah == bh != "unknown" and dist(a, b) <= 8]
    left, right = Counter(i for i, _ in pairs), Counter(j for _, j in pairs)
    require(all(n == 1 for n in (*left.values(), *right.values())), "ambiguous registered truth")
    return frozenset(pairs)


def subset(view, indices):
    native = view.native.select(indices)
    # Native and player-relative lists are sorted in the same order after translation.
    return replace(view, native=native, relative=view.relative.select(indices) if view.relative else None)


def trim(view, axis, low):
    values = [m.point[axis] for m in view.native.points]
    sign = 1 if low else -1
    boundary = sorted(sign * x for x in values)[len(values) // 4]
    return tuple(i for i, x in enumerate(values) if sign * x >= boundary)


def masked_trials(trial):
    q = trial.query
    wrong = tuple(c for c in trial.candidates if c.truth is None)
    for candidate in trial.candidates:
        if candidate.truth is None:
            continue
        r = candidate.view
        truth = sorted(candidate.truth)
        require(len(truth) >= 4, "moved-view truth cannot support the frozen masks")
        masks = [
            ("removal", tuple(i for i in range(len(q.native.points)) if i != truth[0][0]),
             tuple(j for j in range(len(r.native.points)) if j != truth[-1][1])),
            ("two_shared", tuple(sorted(i for i, _ in truth[:3])),
             tuple(sorted(truth[k][1] for k in (0, 1, 3)))),
        ]
        masks.extend((f"crop_{axis}_{int(low)}", trim(q, axis, low), trim(r, axis, not low))
                     for axis, low in product(range(2), (True, False)))
        for kind, qi, ri in masks:
            q_indices = {old: new for new, old in enumerate(qi)}
            r_indices = {old: new for new, old in enumerate(ri)}
            shared = frozenset((q_indices[i], r_indices[j]) for i, j in truth
                               if i in q_indices and j in r_indices)
            masked = replace(candidate, view=subset(r, ri), truth=shared)
            yield Trial("crop" if kind.startswith("crop") else kind,
                        f"{trial.id}/{candidate.id}/{kind}", subset(q, qi), (masked, *wrong))


def real_trials():
    lock = read_json(checked_file(LOCK_PATH, LOCK_HASH))
    owner = read_json(checked_file(OWNER / "manifest.json", lock["owner_manifest_sha256"]))
    _, raw, v2_hashes, shifts = load_inputs()
    require({p: h for p, h in v2_hashes.items() if p.endswith("/raw.json")} == lock["development_input_hashes"],
            "development returns differ from the lock")
    dev, full, cal = {}, {}, {}
    for n, packets in enumerate(FRAME_PACKETS):
        for packet in packets:
            staged = observation(raw[packet], "mapa-07", f"window-{n}", f"stage-{STAGES[n]}", shifts[n])
            dev[packet] = staged
            full[packet] = replace(
                staged, region="registered-overlap",
                native=player_markers(raw[packet]["markers"], {"px": (0, 0), "error_px": 0}),
                relative=player_markers(raw[packet]["markers"], raw[packet]["player"]),
            )
    for packet, audit in lock["calibration_input_hashes"]["returns"].items():
        entry, = (p for p in owner["packets"] if p["split"] == "calibration" and p["packet_id"] == packet)
        status, = (r for r in owner["registration"] if r["layout"] == "mapa-06" and r.get("view") == entry["view"])
        row = read_json(checked_file(Path(audit["path"]), audit["received_sha256"]))
        require(audit["validation"] == "PASS" and audit["complete_search"] and entry["layout"] == "mapa-06",
                "ineligible calibration observation")
        cal[packet] = observation(row, entry["layout"], entry["region"], entry["view"],
                                  status["registration"]["translation_px"])

    def trial(kind, query_id, ref_ids, observations):
        query = observations[query_id]
        candidates = tuple(Candidate(ref_id, observations[ref_id],
                                     registered_truth(query, observations[ref_id])
                                     if region(query) == region(observations[ref_id]) else None)
                           for ref_id in ref_ids)
        return Trial(kind, f"{kind}/{query_id}", query, candidates)

    for group, query_id, references in lock["frozen_candidate_roster"]["calibration"]:
        comparison = trial(f"cal_{group}", query_id, references, {**cal, **dev})
        yield comparison
        if group == "moved":
            yield from masked_trials(comparison)
    for a, b in (FRAME_PACKETS, FRAME_PACKETS[::-1]):
        for n, query_id in enumerate(a):
            yield trial("dev_same_frame", query_id, (a[1 - n], *b), dev)
            yield trial("dev_moved", query_id, b, full)


def marks(points, shift=(0, 0), hue="yellow", radius=2):
    return Markers(tuple(Marker((x + shift[0], y + shift[1]), hue, radius) for x, y in points), 0)


def synthetic_trials():
    shape = ((0, 0), (33, 9), (11, 41), (56, 47))
    extended = (*shape, (83, 2), (24, 109))
    q = marks(shape)
    r = marks(shape, (213, -82))

    def identity(n):
        return frozenset((i, i) for i in range(n))

    def fixture(name, query, refs, expected="positive", limits=LIMITS):
        def view(geometry, name):
            return Observation("synthetic", name, "", (0, 0), geometry, geometry, True)
        return Trial("synthetic", name, view(query, "correct"),
                     tuple(Candidate(str(i), view(geometry, "correct" if truth is not None else str(i)), truth)
                           for i, (geometry, truth) in enumerate(refs)), expected, limits)

    for name, left, right, common in (
        ("identical", q, q, 4),
        ("translated", q, r, 4),
        ("missing_query", q, marks(extended, (213, -82)), 4),
        ("missing_reference", marks(extended), r, 4),
        ("bilateral_removal", marks(extended[:5]), marks((*shape, extended[5]), (213, -82)), 4),
        ("bilateral_addition_equal", marks((*shape, (12, 101), (87, 94))),
         marks((*shape, (86, 3), (29, 105)), (213, -82)), 4),
        ("bilateral_unequal", marks(extended[:5]), marks((*shape, (87, 108), (4, 106))), 4),
        ("noise_within_cap", q, marks(((0, 0), (39, 9), (11, 41), (56, 47)), (213, -82)), 4),
    ):
        yield fixture(name, left, ((right, identity(common)),))

    rectangle = ((0, 0), (30, 0), (0, 41), (30, 41))
    repeated = marks((*rectangle, (60, 0), (60, 41)))
    yield fixture("repeated_within_reference", marks(rectangle), ((repeated, identity(4)),), "ambiguous_correspondences")
    yield fixture("repeated_across_regions", q, ((q, identity(4)), (r, None)), "ambiguous_regions")
    line = marks(((0, 0), (30, 1), (62, -1), (96, 0)))
    tiny = marks(((0, 0), (5, 0), (0, 5)), radius=0)
    local = marks((*shape, (350, 350), (370, 370)))
    yield fixture("near_collinear", line, ((line, identity(4)),), "insufficient")
    yield fixture("short_baseline", tiny, ((tiny, identity(3)),), "insufficient")
    yield fixture("small_spatial_span", local, ((marks(extended), identity(4)),), "insufficient")
    yield fixture("one_marker", q.select((0,)), ((r.select((0,)), identity(1)),), "insufficient")
    yield fixture("two_markers", q.select((0, 1)), ((r, identity(2)),), "insufficient")
    yield fixture("bilateral_count_floor", q, ((marks((*extended, (210, 81))), identity(4)),), "insufficient")
    far_noise = marks(tuple((x, y + i * 9) for i, (x, y) in enumerate(shape)))
    yield fixture("noise_beyond_cap", q, ((far_noise, None),), "no_match")
    exact_query = marks(shape, radius=0)
    one_noisy = marks(((0, 0), (39, 9), (11, 41), (56, 47)), radius=0)
    yield fixture("exact_subset_despite_noisy_point", exact_query,
                  ((one_noisy, frozenset((i, i) for i in (0, 2, 3))),))
    all_noisy = marks(tuple((x, y + i) for i, (x, y) in enumerate(shape)), radius=0)
    yield fixture("noise_beyond_radii", exact_query, ((all_noisy, identity(4)),), "no_match")
    yield fixture("hue_disagreement", q, ((marks(shape, hue="purple"), None),), "no_match")
    yield fixture("out_of_corpus", q, ((marks(((0, 0), (150, 7), (2, 155), (170, 191))), None),), "no_match")
    for name, limits in (
        ("pair_prefixes", replace(LIMITS, pair_prefixes=1)),
        ("query_prefixes", replace(LIMITS, query_prefixes=1)),
        ("pair_hypotheses", replace(LIMITS, pair_hypotheses=1)),
        ("references", replace(LIMITS, references=0)),
        ("markers", replace(LIMITS, markers=3)),
    ):
        yield fixture(name, marks(rectangle), ((repeated, identity(4)),), "budget", limits)

    dense = marks(tuple(point for point in shape for _ in range(3)))
    yield fixture("default_hypothesis_ceiling", dense, ((dense, identity(12)),), "budget")


def operation(trial, mode):
    q = trial.query.geometry(mode)
    refs = tuple(c.view.geometry(mode) for c in trial.candidates)
    if mode == "partial":
        return lambda: match_query(q, refs, limits=trial.limits)
    return lambda: strict(q, refs, mode, 4 if mode == "A" else 6, limits=trial.limits)


def eligibility(trial):
    return tuple(trial.query.complete and candidate.view.complete
                 and geometry_support(trial.query.native, candidate.view.native, candidate.truth)
                 for candidate in trial.candidates)


def score(trial, mode, result, eligible):
    comparisons = []
    for i, candidate in enumerate(trial.candidates):
        q, r = trial.query, candidate.view
        pair = result.pairs[i] if i < len(result.pairs) else None
        hypotheses = []
        for hypothesis in pair.hypotheses if pair else ():
            detail = hypothesis_evidence(hypothesis, q, r)
            if trial.group == "synthetic":
                detail.pop("max_registered_centre_distance_px", None)
                detail.pop("within_registered_radii", None)
            pairs = frozenset(hypothesis.pairs)
            detail["verified_assignment"] = candidate.truth is not None and pairs <= candidate.truth
            detail["exact_shared"] = pairs == candidate.truth
            hypotheses.append(detail)
        comparisons.append({
            "reference": candidate.id, "region": region(r), "correct_region": region(q) == region(r),
            "expected_pairs": sorted(candidate.truth) if candidate.truth is not None else None,
            "visible_markers": [len(q.native.points), len(r.native.points)],
            "eligible_truth": eligible[i],
            "hypotheses": hypotheses, "stop": (pair.stop or "complete") if pair else "not_run",
            "prefixes": pair.prefixes if pair else 0, "checks": pair.checks if pair else 0,
            "seen": pair.hypotheses_seen if pair else 0,
        })
    compatible = [pair for pair in comparisons if pair["hypotheses"]]
    regions = {tuple(pair["region"]) for pair in compatible}
    resolved = [h for pair in compatible for h in pair["hypotheses"] if mode == "A" or h["alignment_2d"]]
    if result.stop in BUDGET_STOPS:
        outcome = "unresolved_search_budget"
    elif result.stop or any(pair.stop for pair in result.pairs):
        outcome = "unavailable_alignment"
    elif len(regions) > 1:
        outcome = "ambiguous_regions"
    elif not regions:
        outcome = "no_match"
    elif any(len(pair["hypotheses"]) > 1 for pair in compatible):
        outcome = "ambiguous_correspondences"
    elif not resolved:
        outcome = "unresolved_2d"
    elif not any(pair["correct_region"] for pair in compatible):
        outcome = "false_unique"
    elif not all(h["verified_assignment"] for h in resolved):
        outcome = "unverified_unique_alignment"
    else:
        outcome = "correct_unique"
    return {"id": trial.id, "group": trial.group, "expected": trial.expected, "outcome": outcome,
            "reference_outcome": classify(result) if mode == "partial" else None,
            "stop": result.stop, "prefixes": result.prefixes, "comparisons": comparisons,
            "resolved_candidates": len(resolved)}


def recovered(pair, mode, exact=False):
    return any(h["exact_shared" if exact else "verified_assignment"] and (mode == "A" or h["alignment_2d"])
               for h in pair["hypotheses"])


def summary(rows, mode):
    counts = Counter()
    for row in rows:
        counts[f'outcome/{row["outcome"]}'] += 1
        if row["reference_outcome"]:
            counts[f'reference_outcome/{row["reference_outcome"]}'] += 1
        for pair in row["comparisons"]:
            counts["checks"] += pair["checks"]
            counts["prefixes"] += pair["prefixes"]
            counts["retained"] += len(pair["hypotheses"])
            counts["seen"] += pair["seen"]
            counts[f'pair/{pair["stop"]}'] += 1
            counts["correct_slots" if pair["correct_region"] else "wrong_slots"] += 1
            if pair["eligible_truth"]:
                counts["eligible_truth"] += 1
                counts["eligible_recovery"] += recovered(pair, mode)
            if not pair["correct_region"]:
                counts["wrong_compatible"] += bool(pair["hypotheses"])
            else:
                counts["correct_compatible"] += bool(pair["hypotheses"])
                counts["correct_recovery"] += recovered(pair, mode)
                counts["exact_shared"] += recovered(pair, mode, exact=True)
    return dict(counts)


def screening(runs, sweep):
    partial = runs["partial"]
    real = [row for row in partial if row["group"] != "synthetic"]
    synthetic = [row for row in partial if row["group"] == "synthetic"]
    comparisons = {row["id"]: row for row in runs["B"]}
    masked = [row for row in real if row["group"] in ("removal", "crop") and row["comparisons"][0]["eligible_truth"]]
    eligible_queries = [row for row in real if any(c["eligible_truth"] for c in row["comparisons"])]
    ambiguous = {"ambiguous_correspondences", "ambiguous_regions"}
    incremental_ambiguity = sum(row["outcome"] in ambiguous and comparisons[row["id"]]["outcome"] not in ambiguous
                                for row in eligible_queries)
    gain = sum(recovered(row["comparisons"][0], "partial")
               and not recovered(comparisons[row["id"]]["comparisons"][0], "B") for row in masked)
    preservation = {}
    for kind in ("cal_same_frame", "cal_moved", "dev_same_frame"):
        pairs = [(p, b) for row in real if row["group"] == kind
                 for p, b in zip(row["comparisons"], comparisons[row["id"]]["comparisons"])
                 if p["correct_region"] and (kind != "dev_same_frame" or p["eligible_truth"] and recovered(b, "B"))]
        preservation[kind] = [sum(recovered(p, "partial") for p, _ in pairs), len(pairs)]
    synthetic_checks = {}
    for row in synthetic:
        name = row["id"]
        expected = row["expected"]
        if expected == "positive":
            passed = row["outcome"] == "correct_unique" and recovered(row["comparisons"][0], "partial", exact=True)
        elif expected == "insufficient":
            passed = not row["resolved_candidates"] and row["stop"] not in BUDGET_STOPS
        elif expected == "budget":
            stop = "pair_hypotheses" if name == "default_hypothesis_ceiling" else name
            passed = row["outcome"] == "unresolved_search_budget" and row["stop"] == stop
        else:
            passed = row["outcome"] == expected
        synthetic_checks[name] = passed
    insufficient = [row for row in real if row["group"] == "two_shared"]
    wrong = summary(real, "partial").get("wrong_compatible", 0)
    strict_wrong = summary([comparisons[row["id"]] for row in real], "B").get("wrong_compatible", 0)
    false_unique = sum(row["outcome"] == "false_unique" for row in partial)
    unverified_unique = sum(row["outcome"] == "unverified_unique_alignment" for row in partial)
    recovered_masked = sum(recovered(row["comparisons"][0], "partial") for row in masked)
    gates = {
        "preserve": preservation["cal_same_frame"] == [6, 6] and preservation["cal_moved"] == [8, 8]
        and preservation["dev_same_frame"][0] == preservation["dev_same_frame"][1],
        "partial_recovery": all(synthetic_checks[row["id"]] for row in synthetic if row["expected"] == "positive")
        and 5 * recovered_masked >= 4 * len(masked) and gain >= 4,
        "collisions_ambiguity": not (false_unique or unverified_unique) and wrong - strict_wrong <= 1
        and 10 * incremental_ambiguity <= len(eligible_queries),
        "abstention": all(synthetic_checks[row["id"]] for row in synthetic if row["expected"] != "positive")
        and len(insufficient) == 8 and all(not row["resolved_candidates"] for row in insufficient),
        "cost": not any(row["stop"] in BUDGET_STOPS for row in partial if row["expected"] != "budget")
        and all(not row["stop"] for row in sweep.values()) and sweep[24]["timing"]["p95_us"] <= 100_000,
    }
    decision = "D"
    if len(masked) >= 4:
        if all(gates.values()):
            decision = "A"
        elif all(passed for gate, passed in gates.items() if gate != "collisions_ambiguity"):
            decision = "B"
        else:
            decision = "C"
    return {"decision": decision, "gates": gates, "preservation": preservation, "synthetic": synthetic_checks,
            "masked_recovery": [recovered_masked, len(masked)], "gain_vs_strict": gain,
            "incremental_ambiguity": [incremental_ambiguity, len(eligible_queries)],
            "wrong_compatible": {"partial": wrong, "strict": strict_wrong},
            "false_unique": false_unique, "unverified_unique_alignment": unverified_unique}


def sweep_repeats(mode):
    base = next(trial for trial in synthetic_trials() if trial.id == "repeated_within_reference")
    output = {}
    for count in (1, 2, 4, 8, 16, 24):
        trial = replace(base, candidates=base.candidates * count)
        run = operation(trial, mode)
        result = run()
        output[count] = {"prefixes": result.prefixes, "checks": sum(p.checks for p in result.pairs),
                         "retained": sum(len(p.hypotheses) for p in result.pairs),
                         "seen": sum(p.hypotheses_seen for p in result.pairs), "stop": result.stop,
                         "timing": timings([run])}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true", help="record comparison inputs before running any matcher")
    args = parser.parse_args()
    hashes = {path: digest(Path(path).read_bytes()) for path in SOURCES}
    if args.freeze:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        with FREEZE.open("xb") as handle:
            handle.write(json_bytes(hashes))
        print(f"Frozen diagnostic inputs in {FREEZE}")
        return
    require(read_json(FREEZE.read_bytes()) == hashes, "diagnostic source or protocol changed since freeze")
    trials = (*real_trials(), *synthetic_trials())
    eligible = [eligibility(trial) for trial in trials]
    rows, metrics, sweeps = {}, {}, {}
    for mode in ("A", "B", "partial"):
        runs = [operation(trial, mode) for trial in trials]
        rows[mode] = [score(trial, mode, run(), expected)
                      for trial, run, expected in zip(trials, runs, eligible)]
        cohorts = {"real_full": [i for i, t in enumerate(trials) if t.group.startswith(("cal_", "dev_"))],
                   "real_masked": [i for i, t in enumerate(trials) if t.group in ("crop", "removal", "two_shared")]}
        metrics[mode] = {group: timings([runs[i] for i in indices]) for group, indices in cohorts.items()}
        sweeps[mode] = sweep_repeats(mode)
    groups = sorted({trial.group for trial in trials})
    totals = {mode: {group: summary([row for row in reports if row["group"] == group], mode) for group in groups}
              for mode, reports in rows.items()}
    decision = screening(rows, sweeps["partial"])
    data = {"freeze": hashes, "platform": platform.platform(), "python": platform.python_version(),
            "limits": asdict(LIMITS), "decision": decision, "summary": totals, "trials": rows,
            "timings": metrics, "sweeps": sweeps}
    path = OUTPUT / "results.json"
    pending = path.with_suffix(".pending.json")
    pending.write_bytes(json_bytes(data))
    pending.replace(path)
    print(json_bytes(decision).decode())
    print(path)


if __name__ == "__main__":
    main()
