"""Import the authorized calibration archive, run the screen, and lock if qualified."""

from collections import Counter
from dataclasses import asdict, dataclass
from io import BytesIO
from math import dist
from pathlib import Path
import stat
from zipfile import ZipFile

from research.annotation_retest.evaluate import assignment, read_json, require, shape, validate
from research.annotation_retest.prepare import digest, json_bytes
from research.marker_fingerprint.bounded_match import CAPS, LIMITS, match_query
from research.marker_fingerprint.evaluate import FRAME_PACKETS, STAGES, load_inputs, region_relation, timings
from research.marker_fingerprint.independent_packets import DEFAULT, VERSION, WINDOW, checked_file
from research.marker_fingerprint.match import Marker, Markers, player_markers


ARCHIVE = Path("docs/phase_1_6_3_calibration_returns.zip")
OWNER = DEFAULT / "owner"
OUTPUT = OWNER / "calibration"
LOCK_PATH = OWNER / "calibration-lock.json"
PLAN = Path("docs/INDEPENDENT_LAYOUT_SCREEN_PLAN.md")


def in_window(p):
    x0, y0, x1, y1 = WINDOW
    return x0 <= p[0] < x1 and y0 <= p[1] < y1


def validate_return(row, template):
    shape(row, " ".join(template))
    require(row["protocol_version"] == template["protocol_version"] == VERSION, "protocol_version")
    shape(row["search_complete"], "markers")

    def v2_view(record):
        # Reuse the shared player/glyph checks. Wall fields exist only in this temporary adapter.
        return {**record, "protocol_version": 2, "walls": [],
                "search_complete": {**record["search_complete"], "walls": False}}

    validate(v2_view(row), v2_view(template), "raw")
    points = [row["player"]["px"]]
    for marker in row["markers"]:
        points.extend([marker["center_px"], *(marker["segment_px"] or [])])
    require(all(p is None or in_window(p) for p in points), "position outside unmasked study window")


def preserve(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(content)
    except FileExistsError:
        require(path.read_bytes() == content, f"frozen bytes differ for {path}")
    require(path.read_bytes() == content, f"preservation failed for {path}")


def import_calibration(released):
    data = ARCHIVE.read_bytes()
    rows, audit = {}, {}
    with ZipFile(BytesIO(data)) as zipped:
        receipt = zipped.read("intake_manifest.json")
        intake = read_json(receipt)
        require(intake["phase"] == "1.6.3" and intake["split"] == "calibration", "wrong intake manifest")
        records = {row["packet_id"]: row for row in intake["returns"]}
        require(len(intake["returns"]) == len(records) == len(released) == 6 and
                records.keys() == released.keys(), "unexpected calibration packet roster")
        expected = {"intake_manifest.json", *(f"{packet}/raw.json" for packet in records)}
        require(len(zipped.namelist()) == len(expected) and set(zipped.namelist()) == expected and
                zipped.testzip() is None, "unexpected calibration ZIP members or CRC")
        preserve(OUTPUT / "supplied-intake.json", receipt)
        for packet, owner_entry in released.items():
            entry = records[packet]
            name = f"{packet}/raw.json"
            original = zipped.read(name)
            private_path = OUTPUT / "returns" / name
            preserve(private_path, original)
            received = {"packet_id": packet, "path": private_path.as_posix(),
                        "received_sha256": digest(original), "expected_sha256": entry["sha256"],
                        "received_bytes": len(original), "original_upload_name": entry["original_upload_name"],
                        "reviewer_id": None, "dispatch_time": None, "receipt_time": None,
                        "exposure_record": None, "deviation_record": None}
            audit[packet] = received
            try:
                require(entry["return_path"] == name and received["received_sha256"] == entry["sha256"] and
                        len(original) == entry["byte_count"], "intake hash, path or length mismatch")
                release_bytes = checked_file(DEFAULT / "release" / owner_entry["filename"],
                                             owner_entry["archive_sha256"])
                with ZipFile(BytesIO(release_bytes)) as release:
                    template = read_json(release.read("raw.json"))
                    require(digest(release.read("frame.png")) == template["frame_sha256"] ==
                            owner_entry["frame_sha256"] and template["packet_id"] == packet,
                            "owner frame/packet mismatch")
                row = read_json(original)
                validate_return(row, template)
                rows[packet] = row
                received.update(validation="PASS", visible_markers=sum(
                    m["status"] == "OBSERVED" for m in row["markers"]),
                    missing_observed_spans=sum(m["status"] == "OBSERVED" and m["segment_px"] is None
                                               for m in row["markers"]),
                    complete_search=row["search_complete"]["markers"],
                    elapsed_minutes=row["elapsed_minutes"], time_limit_reached=row["time_limit_reached"])
            except (ValueError, TypeError, AttributeError, KeyError) as exc:
                received.update(validation="FAIL", error=str(exc))
    return rows, {"archive_sha256": digest(data), "supplied_intake_sha256": digest(receipt),
                  "returns": audit}


@dataclass(frozen=True, slots=True)
class Observation:
    layout: str
    region: str
    view: str
    translation: tuple
    native: Markers | None
    relative: Markers | None
    complete: bool

    def geometry(self, mode):
        return (self.relative if mode == "A" else self.native) if self.complete else None


def observation(row, layout, region, view, translation):
    if row is None:
        return Observation(layout, region, view, translation, None, None, False)
    markers = [m for m in row["markers"] if m["status"] == "OBSERVED" and in_window(m["center_px"])]
    native = player_markers(markers, {"px": (0, 0), "error_px": 0})
    player = row["player"]
    relative = player_markers(markers, player) if player["status"] == "OBSERVED" else None
    return Observation(layout, region, view, translation, native, relative, row["search_complete"]["markers"])


def roster(packet_entries, development_ids):
    views = {view: sorted(p for p, entry in packet_entries.items() if entry["view"] == view)
             for view in ("r1", "r1b", "r2")}
    require(all(len(packets) == 2 for packets in views.values()), "view roster needs two reviews")
    trials = []
    for view, packets in views.items():
        distinct = views["r1" if view == "r2" else "r2"]
        for i, packet in enumerate(packets):
            trials.append(("same_frame", packet, (packets[1 - i], *distinct)))
    for view, other in (("r1", "r1b"), ("r1b", "r1")):
        for packet in views[view]:
            trials.append(("moved", packet, (*views[other], *views["r2"])))
    trials.extend(("out_of_corpus", packet, tuple(development_ids))
                  for packet in sorted(packet_entries))
    return trials


def agreement(rows, packets):
    results = {}
    for view in ("r1", "r1b", "r2"):
        pair = sorted(p for p, entry in packets.items() if entry["view"] == view)
        if not all(p in rows for p in pair):
            results[view] = {"status": "NOT EVALUABLE", "packets": pair}
            continue
        a, b = ([m for m in rows[p]["markers"] if m["status"] == "OBSERVED"] for p in pair)
        def centre_error(q, r):
            return dist(q["center_px"], r["center_px"])
        matches, alternatives = assignment(a, b, centre_error, 12)
        results[view] = {
            "packets": pair, "visible_counts": [len(a), len(b)], "matches": len(matches),
            "max_centre_px": max((centre_error(a[i], b[j]) for i, j in matches), default=None),
            "tied_assignment": bool(alternatives),
        }
    return results


def bounds_area(points):
    x, y = zip(*points)
    return (max(x) - min(x)) * (max(y) - min(y))


def hypothesis_evidence(hypothesis, query, reference):
    left, right = ([view.native.points[pair[index]] for pair in hypothesis.pairs]
                   for index, view in enumerate((query, reference)))
    marker_box = []
    for view, matched in ((query, left), (reference, right)):
        total_area = bounds_area([p.point for p in view.native.points])
        marker_box.append(bounds_area([p.point for p in matched]) / total_area if total_area else None)
    detail = asdict(hypothesis)
    detail.update(matched_markers=len(left), span_fraction=marker_box,
                  matched_fraction=[len(left) / len(view.native.points) for view in (query, reference)])
    if query.layout == reference.layout:
        discrepancies = [dist(tuple(x + t for x, t in zip(q.point, query.translation)),
                              tuple(x + t for x, t in zip(r.point, reference.translation)))
                         for q, r in zip(left, right)]
        detail["max_registered_centre_distance_px"] = max(discrepancies)
        detail["within_registered_radii"] = sum(
            d <= q.radius + r.radius + 12 for d, q, r in zip(discrepancies, left, right)) / len(left)
    return detail


def trial_result(mode, kind, query_id, ref_ids, observations, result):
    query = observations[query_id]
    comparisons = []
    for i, reference_id in enumerate(ref_ids):
        reference = observations[reference_id]
        match = result.pairs[i] if i < len(result.pairs) else None
        hypotheses = tuple(hypothesis_evidence(h, query, reference) for h in match.hypotheses) if match else ()
        comparisons.append({"reference": reference_id, "region": [reference.layout, reference.region],
                            "correct_region": (query.layout, query.region) == (reference.layout, reference.region),
                            "status": (match.stop or "complete") if match else "not_run",
                            "prefixes": match.prefixes if match else 0, "checks": match.checks if match else 0,
                            "hypotheses_seen": match.hypotheses_seen if match else 0,
                            "hypotheses": hypotheses,
                            "best_score": hypotheses[0]["score"] if hypotheses else None})
    compatible = [row for row in comparisons if row["hypotheses"]]
    regions = sorted({tuple(row["region"]) for row in compatible})
    correct_scores = [row["best_score"] for row in compatible if row["correct_region"]]
    wrong_scores = [row["best_score"] for row in compatible if not row["correct_region"]]
    budget = result.stop in ("markers", "references", "pair_prefixes", "pair_hypotheses", "query_prefixes")
    if budget:
        outcome = "unresolved_search_budget"
    elif result.stop or any(p["status"] != "complete" for p in comparisons):
        outcome = "unavailable_alignment"
    elif len(regions) > 1:
        outcome = "ambiguous_regions"
    elif not regions:
        outcome = "no_match"
    elif any(len(row["hypotheses"]) > 1 for row in compatible):
        outcome = "ambiguous_correspondences"
    elif mode == "B" and not any(h["alignment_2d"] for row in compatible for h in row["hypotheses"]):
        outcome = "unresolved_2d"
    else:
        outcome = "correct_unique" if correct_scores else "false_unique"
    return {"kind": kind, "query": query_id, "outcome": outcome, "stop": result.stop,
            "prefixes": result.prefixes, "completed_references": sum(r["status"] == "complete" for r in comparisons),
            "candidate_region_count": len(regions), "compatible_regions": regions,
            "score_margin": min(wrong_scores) - min(correct_scores) if correct_scores and wrong_scores else None,
            "comparisons": comparisons}


def summarize(trials):
    output = {}
    for kind in ("same_frame", "moved", "out_of_corpus"):
        selected = [t for t in trials if t["kind"] == kind]
        complete = [t for t in selected if t["outcome"] not in ("unresolved_search_budget", "unavailable_alignment")]
        pairs = [pair for t in selected for pair in t["comparisons"]]
        counts = Counter()
        for pair in pairs:
            label = "correct" if pair["correct_region"] else "wrong"
            counts[f"{label}_planned"] += 1
            if pair["status"] == "complete":
                counts[f"{label}_eligible"] += 1
                if pair["hypotheses"]:
                    counts[f"{label}_compatible"] += 1
                    if any(h["alignment_2d"] for h in pair["hypotheses"]):
                        counts[f"{label}_compatible_2d"] += 1
        output[kind] = {"query_count": len(selected), "eligible_queries": len(complete),
                        "pairs": dict(counts), "outcomes": dict(Counter(t["outcome"] for t in selected)),
                        "prefixes": sum(t["prefixes"] for t in selected),
                        "max_query_prefixes": max((t["prefixes"] for t in selected), default=0),
                        "max_pair_prefixes": max((p["prefixes"] for p in pairs), default=0)}
    return output


def screen(mode, cap, trials, observations):
    operations = []
    results = []
    for kind, query, references in trials:
        q = observations[query].geometry(mode)
        refs = tuple(observations[r].geometry(mode) for r in references)
        operation = lambda q=q, refs=refs: match_query(q, refs, mode, cap)
        operations.append(operation)
        results.append(trial_result(mode, kind, query, references, observations, operation()))
    returns = summarize(results)
    return {"summary": returns, "trials": results, "timings": timings(operations)}


def synthetic_sweep(mode, cap):
    q = Markers(tuple(Marker(p, "yellow", 2) for p in ((0, 0), (12, 30), (31, 2))), 3)
    r = Markers(tuple(Marker((m.point[0] + shift, m.point[1]), m.hue, m.radius)
                      for shift in (0, 120) for m in q.points), 3)
    output = {}
    for n in (1, 2, 4, 8, 16, 24):
        references = (r,) * n
        run = lambda: match_query(q, references, mode, cap)
        result = run()
        output[n] = {"prefixes": result.prefixes, "hypotheses": sum(len(p.hypotheses) for p in result.pairs),
                     "stop": result.stop, "timings": timings([run])}
    return output


def select_caps(screens):
    chosen = {}
    blockers = []
    rankings = {}
    for mode, configs in screens.items():
        ranking = []
        for cap, screen in configs.items():
            groups = screen["summary"]
            compatible = sum(g["pairs"].get("correct_compatible", 0) for g in groups.values())
            wrong = sum(g["pairs"].get("wrong_compatible", 0) for g in groups.values())
            false_unique = sum(g["outcomes"].get("false_unique", 0) for g in groups.values())
            ranking.append({"cap": cap, "compatible": compatible, "wrong_compatible": wrong,
                            "false_unique": false_unique})
        ranking.sort(key=lambda r: (bool(r["false_unique"]), -r["compatible"], r["wrong_compatible"], r["cap"]))
        rankings[mode] = ranking
        if ranking[0]["false_unique"]:
            blockers.append(f"{mode}: all caps have verified false unique outcomes")
            continue
        cap = ranking[0]["cap"]
        chosen[mode] = cap
        groups = configs[cap]["summary"]
        for name, group in groups.items():
            if group["eligible_queries"] != group["query_count"]:
                blockers.append(f"{mode} {cap} px {name}: {group['eligible_queries']}/{group['query_count']} evaluable")
        # Moved-view compatibility is the primary representation's gate. A is the comparison baseline.
        if mode == "B":
            for name in ("same_frame", "moved"):
                counts = groups[name]["pairs"]
                support = counts.get("correct_compatible_2d", 0)
                if support != counts["correct_planned"]:
                    blockers.append(f"B {cap} px {name}: {support}/{counts['correct_planned']} required pairs retained with 2D support")
    return {"selected_caps": chosen, "rankings": rankings, "blockers": blockers,
            "lock_eligible": not blockers}


def main():
    require(not LOCK_PATH.exists(), "a write-once calibration lock already exists")
    manifest_bytes = (OWNER / "manifest.json").read_bytes()
    owner = read_json(manifest_bytes)
    selection_bytes = checked_file(OWNER / "selection.json", owner["selection_sha256"])
    selection = read_json(selection_bytes)
    for path, hash_ in owner["frozen_sha256"].items():
        checked_file(path, hash_)
    stage1 = Path("local-data/phase-1-6-2")
    for path, hash_ in read_json((stage1 / "before-comparisons.json").read_bytes()).items():
        checked_file(path, hash_)
    checked_file(stage1 / "results.json", owner["stage1_local_results_sha256"])
    _, development, v2_hashes, shifts = load_inputs()
    calibration_release = {item["packet_id"]: item for item in owner["packets"] if item["split"] == "calibration"}
    holdout_release = {item["packet_id"]: item for item in owner["packets"] if item["split"] == "holdout"}
    rows, intake = import_calibration(calibration_release)
    cal = {p: observation(rows.get(p), item["layout"], item["region"], item["view"],
                         next(r["registration"]["translation_px"] for r in owner["registration"]
                              if r["layout"] == item["layout"] and r.get("view") == item["view"]))
           for p, item in calibration_release.items()}
    dev = {p: observation(development[p], "mapa-07", f"window-{i}", f"stage-{STAGES[i]}", shifts[i])
           for i, group in enumerate(FRAME_PACKETS) for p in group}
    dev_clouds = [tuple((tuple(x + t for x, t in zip(m.point, view.translation)), m.hue, m.radius)
                        for m in view.native.points) for view in (dev[FRAME_PACKETS[i][0]] for i in range(2))]
    require(region_relation(*dev_clouds) == "distinct", "development region labels unresolved")
    trials = roster(calibration_release, tuple(dev))
    screens = {mode: {cap: screen(mode, cap, trials, {**cal, **dev}) for cap in CAPS} for mode in ("A", "B")}
    decision = select_caps(screens)
    results = {"intake": intake, "agreement": agreement(rows, calibration_release), "roster": trials,
               "visible_markers": {p: len(o.native.points) if o.native is not None else None
                                   for p, o in {**cal, **dev}.items()},
               "budgets": asdict(LIMITS), "screens": screens, "decision": decision,
               "synthetic_repeated_motif_sweep": {mode: synthetic_sweep(mode, 8) for mode in ("A", "B")}}
    results_path = OUTPUT / "results.json"
    pending = OUTPUT / "results.pending.json"
    pending.write_bytes(json_bytes(results))
    pending.replace(results_path)
    if decision["lock_eligible"]:
        support_files = (
            "research/marker_fingerprint/calibrate.py", "research/marker_fingerprint/bounded_match.py",
            "research/marker_fingerprint/match.py", "research/marker_fingerprint/evaluate.py",
            "research/marker_fingerprint/independent_packets.py", "research/annotation_retest/evaluate.py",
            "research/annotation_retest/prepare.py", "research/geometry_experiment/blind_packets.py",
            "tests/test_bounded_match.py", "tests/test_marker_fingerprint.py", "tests/test_geometry_experiment.py",
        )
        holdout_labels = {"layout": next(x for x in selection["layouts"] if x["split"] == "holdout"),
                          "registration": [x for x in owner["registration"] if x["layout"] == "mapa-09"]}
        lock = {
            "phase": "1.6.3", "status": "locked_awaiting_owner_approval", "holdout_opened_at": None,
            "plan_sha256": digest(PLAN.read_bytes()), "owner_manifest_sha256": digest(manifest_bytes),
            "evaluator_selection_sha256": digest(selection_bytes),
            "holdout_packet_manifest_sha256": digest(json_bytes(holdout_release)),
            "holdout_evaluator_labels_sha256": digest(json_bytes(holdout_labels)),
            "matching_rules": {"A": "player-relative centred offsets", "B": "directed pair vectors",
                               "hue_and_residual": "frozen Stage 1", "support": "complete one-to-one smaller set",
                               "ambiguity": "preserve all hypotheses; no best-score-only resolutions"},
            "eligibility": {"valid_complete_window_search": True, "minimum_markers": 2,
                            "resolved_B_alignment": "supported non-collinear triple",
                            "A_requires_observed_player": True, "window_xyxy": WINDOW},
            "budgets": asdict(LIMITS), "candidate_caps": CAPS, "selected_caps": decision["selected_caps"],
            "calibration_decision": decision, "calibration_input_hashes": intake,
            "development_input_hashes": {path: value for path, value in v2_hashes.items()
                                         if path.endswith("/raw.json")},
            "frozen_candidate_roster": {
                "calibration": trials, "holdout": roster(holdout_release, tuple(dev))},
            "source_and_test_sha256": {p: digest(Path(p).read_bytes()) for p in support_files},
            "calibration_results": results_path.as_posix(),
            "calibration_results_sha256": digest(results_path.read_bytes()),
        }
        with LOCK_PATH.open("xb") as f:
            f.write(json_bytes(lock))
        LOCK_PATH.chmod(stat.S_IREAD)
        print(f"{LOCK_PATH.resolve()}  SHA-256 {digest(LOCK_PATH.read_bytes())}")
    else:
        print("Calibration lock not created. " + " · ".join(decision["blockers"]))
    print(f"{results_path.resolve()}")


if __name__ == "__main__":
    main()
