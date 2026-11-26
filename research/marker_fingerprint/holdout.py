"""Run the locked independent-layout holdout once, or verify the saved run."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from io import BytesIO
from itertools import combinations
from math import dist, inf
from pathlib import Path
import stat
from zipfile import ZipFile

from research.annotation_retest.evaluate import assignment, read_json, require
from research.annotation_retest.prepare import digest, json_bytes
from research.marker_fingerprint.bounded_match import CAPS, LIMITS
from research.marker_fingerprint.calibrate import (
    ARCHIVE as CALIBRATION_ARCHIVE, LOCK_PATH, OUTPUT as CALIBRATION_OUTPUT, OWNER, PLAN,
    agreement, in_window, observation, preserve, roster, screen, validate_return,
)
from research.marker_fingerprint.evaluate import FRAME_PACKETS, STAGES, load_inputs, region_relation
from research.marker_fingerprint.independent_packets import DEFAULT, WINDOW, checked_file, prepare_truth
from research.marker_fingerprint.match import compatible_hue, resolved_triangle


LOCK_SHA256 = "97ce79e547ef756100fe93e0aee838f65500ac893fdae3b0d466181d73e8773a"
ARCHIVE = Path("docs/phase_1_6_3_holdout_returns.zip")
OUTPUT = OWNER / "holdout"
OPENING = OUTPUT / "opening.json"
RESULTS = OUTPUT / "results.json"
COMPLETION = OUTPUT / "completion.json"
MATCHING_RULES = {
    "A": "player-relative centred offsets", "B": "directed pair vectors",
    "hue_and_residual": "frozen Stage 1", "support": "complete one-to-one smaller set",
    "ambiguity": "preserve all hypotheses; no best-score-only resolutions",
}
ELIGIBILITY = {
    "valid_complete_window_search": True, "minimum_markers": 2,
    "resolved_B_alignment": "supported non-collinear triple",
    "A_requires_observed_player": True, "window_xyxy": list(WINDOW),
}


def preflight():
    lock = read_json(checked_file(LOCK_PATH, LOCK_SHA256))
    require(not LOCK_PATH.stat().st_mode & stat.S_IWRITE and lock["holdout_opened_at"] is None and
            lock["phase"] == "1.6.3" and lock["calibration_decision"]["lock_eligible"],
            "calibration lock state")
    require(lock["selected_caps"] == {"A": 4, "B": 6} and
            lock["calibration_decision"]["selected_caps"] == lock["selected_caps"] and
            lock["candidate_caps"] == list(CAPS) and lock["matching_rules"] == MATCHING_RULES and
            lock["eligibility"] == ELIGIBILITY and lock["budgets"] == asdict(LIMITS), "locked rules or limits")
    checked_file(PLAN, lock["plan_sha256"])
    for path, checksum in lock["source_and_test_sha256"].items():
        checked_file(path, checksum)

    owner = read_json(checked_file(OWNER / "manifest.json", lock["owner_manifest_sha256"]))
    selection = read_json(checked_file(OWNER / "selection.json", lock["evaluator_selection_sha256"]))
    require(owner["selection_sha256"] == lock["evaluator_selection_sha256"], "selection integrity")
    for path, checksum in owner["frozen_sha256"].items():
        checked_file(path, checksum)
    require(json_bytes(prepare_truth(selection)) == json_bytes(owner["registration"]), "registration changed")
    stage1 = Path("local-data/phase-1-6-2")
    for path, checksum in read_json((stage1 / "before-comparisons.json").read_bytes()).items():
        checked_file(path, checksum)
    checked_file(stage1 / "results.json", owner["stage1_local_results_sha256"])

    calibrated = read_json(checked_file(lock["calibration_results"], lock["calibration_results_sha256"]))
    intake = lock["calibration_input_hashes"]
    require(intake == calibrated["intake"] and calibrated["decision"] == lock["calibration_decision"],
            "calibration results do not match the lock")
    checked_file(CALIBRATION_ARCHIVE, intake["archive_sha256"])
    checked_file(CALIBRATION_OUTPUT / "supplied-intake.json", intake["supplied_intake_sha256"])
    for row in intake["returns"].values():
        data = checked_file(row["path"], row["received_sha256"])
        require(row["expected_sha256"] == row["received_sha256"] and len(data) == row["received_bytes"] and
                row["validation"] == "PASS", "calibration return identity")

    prior = Path("local-data/phase-1-6/role-c/pilot-validation/intake-manifest.json")
    for row in read_json(prior.read_bytes())["returns"]:
        for field in ("supplied_file", "frozen_file"):
            checked_file(row[field], row["annotation_sha256"])
    _, development, v2_hashes, shifts = load_inputs()
    require({p: h for p, h in v2_hashes.items() if p.endswith("/raw.json")} ==
            lock["development_input_hashes"], "development hashes")
    dev = {p: observation(development[p], "mapa-07", f"window-{i}", f"stage-{STAGES[i]}", shifts[i])
           for i, group in enumerate(FRAME_PACKETS) for p in group}
    clouds = [tuple((tuple(x + t for x, t in zip(m.point, v.translation)), m.hue, m.radius)
                    for m in v.native.points) for v in (dev[group[0]] for group in FRAME_PACKETS)]
    require(region_relation(*clouds) == "distinct", "development region labels")
    releases = {}
    for split in ("calibration", "holdout"):
        packets = {e["packet_id"]: e for e in owner["packets"] if e["split"] == split}
        require(json_bytes(roster(packets, tuple(dev))) == json_bytes(lock["frozen_candidate_roster"][split]),
                f"{split} roster")
        releases[split] = packets
        for entry in packets.values():
            checked_file(DEFAULT / "release" / entry["filename"], entry["archive_sha256"])
    require(digest(json_bytes(releases["holdout"])) == lock["holdout_packet_manifest_sha256"],
            "holdout release manifest")
    holdout_layout, = (item for item in selection["layouts"] if item["split"] == "holdout")
    labels = {"layout": holdout_layout, "registration": [
        r for r in owner["registration"] if r["layout"] == holdout_layout["layout"]]}
    require(digest(json_bytes(labels)) == lock["holdout_evaluator_labels_sha256"], "holdout labels")
    return lock, releases["holdout"], labels, dev


def intake_holdout(released):
    archive = ARCHIVE.read_bytes()
    preserve(OUTPUT / "supplied.zip", archive)
    rows, audit = {}, {}
    with ZipFile(BytesIO(archive)) as zipped:
        expected = {"intake_manifest.json", *(f"{p}/raw.json" for p in released)}
        require(len(zipped.namelist()) == len(expected) and set(zipped.namelist()) == expected and
                zipped.testzip() is None, "holdout archive roster or CRC")
        receipt = zipped.read("intake_manifest.json")
        preserve(OUTPUT / "supplied-intake.json", receipt)
        for packet in released:
            member = f"{packet}/raw.json"
            path = OUTPUT / "returns" / member
            preserve(path, zipped.read(member))
        supplied = read_json(receipt)
        require(supplied["phase"] == "1.6.3" and supplied["split"] == "holdout", "holdout intake manifest")
        declared = {row["packet_id"]: row for row in supplied["returns"]}
        require(len(supplied["returns"]) == len(declared) == 6 and
                declared.keys() == released.keys(), "holdout intake packet roster")
        for packet, release in released.items():
            member = f"{packet}/raw.json"
            path = OUTPUT / "returns" / member
            original = path.read_bytes()
            declaration = declared[packet]
            item = {"path": path.as_posix(), "sha256": digest(original), "bytes": len(original),
                    "expected_sha256": declaration.get("sha256"),
                    "original_upload_name": declaration.get("original_upload_name"),
                    **{f: declaration.get(f) for f in ("reviewer_id", "dispatch_time", "receipt_time",
                                                      "exposure_record", "deviation_record")}}
            audit[packet] = item
            try:
                require(declaration["return_path"] == member and
                        item["sha256"] == declaration["sha256"] and len(original) == declaration["byte_count"],
                        "return manifest path, SHA-256 or size")
                release_bytes = checked_file(DEFAULT / "release" / release["filename"], release["archive_sha256"])
                with ZipFile(BytesIO(release_bytes)) as packet_zip:
                    template = read_json(packet_zip.read("raw.json"))
                    require(digest(packet_zip.read("frame.png")) == template["frame_sha256"] ==
                            release["frame_sha256"] and template["packet_id"] == packet, "owner frame/packet identity")
                row = read_json(original)
                validate_return(row, template)
                rows[packet] = row
                item.update(validation="PASS", complete_search=row["search_complete"]["markers"],
                            time_limit_reached=row["time_limit_reached"], elapsed_minutes=row["elapsed_minutes"],
                            observed_markers=sum(m["status"] == "OBSERVED" for m in row["markers"]),
                            observed_without_span=sum(m["status"] == "OBSERVED" and m["segment_px"] is None
                                                      for m in row["markers"]))
            except (ValueError, TypeError, AttributeError, KeyError) as exc:
                item.update(validation="FAIL", error=str(exc))
    return rows, {"archive_sha256": digest(archive), "supplied_intake_sha256": digest(receipt),
                  "returns": audit}


def holdout_gate(trials, observations):
    required = {"r1": [], "r2": [], "moved": []}
    false_unique = 0
    incomplete = 0
    for trial in trials:
        outcome = trial["outcome"]
        false_unique += outcome == "false_unique"
        unavailable = outcome in ("unavailable_alignment", "unresolved_search_budget")
        incomplete += unavailable
        query = observations[trial["query"]]
        kind = trial["kind"]
        if kind == "out_of_corpus" or (kind == "same_frame" and query.view == "r1b"):
            continue
        group = "moved" if kind == "moved" else query.view
        for pair in trial["comparisons"]:
            if not pair["correct_region"]:
                continue
            flag = "PASS" if pair["hypotheses"] else "FAIL"
            if unavailable or pair["status"] != "complete":
                flag = "NOT EVALUABLE"
            elif group == "moved":
                ref = observations[pair["reference"]]
                supported = all(any(resolved_triangle(triangle)
                                    for triangle in combinations(view.native.points, 3))
                                for view in (query, ref))
                flag = ("NOT EVALUABLE" if not supported else
                        "PASS" if any(h["alignment_2d"] for h in pair["hypotheses"]) else "FAIL")
            required[group].append({"query": trial["query"], "reference": pair["reference"], "status": flag})
    require([len(v) for v in required.values()] == [2, 2, 8], "unexpected primary gate denominators")
    checks = {name: ("FAIL" if any(p["status"] == "FAIL" for p in values) else
                     "NOT EVALUABLE" if any(p["status"] == "NOT EVALUABLE" for p in values) else "PASS")
              for name, values in required.items()}
    checks["zero_false_unique"] = "FAIL" if false_unique else "NOT EVALUABLE" if incomplete else "PASS"
    status = ("FAIL" if "FAIL" in checks.values() else
              "NOT EVALUABLE" if "NOT EVALUABLE" in checks.values() else "PASS")
    return {"status": status, "checks": checks, "required_pairs": required}


def registered_overlap(trials, observations):
    """Describe physical overlap from wall registration after the scored pass."""
    pairs = {}
    for kind, query, references in trials:
        if kind != "moved":
            continue
        q = observations[query]
        for reference in references:
            r = observations[reference]
            if q.region != r.region or q.native is None or r.native is None:
                continue
            key = "|".join(sorted((query, reference)))
            if key in pairs:
                continue
            a, b = ([{"id": i, "marker": m,
                      "ref_px": tuple(x + t for x, t in zip(m.point, v.translation))}
                     for i, m in enumerate(v.native.points)] for v in (q, r))

            def cost(left, right):
                m, n = left["marker"], right["marker"]
                d = dist(left["ref_px"], right["ref_px"])
                if compatible_hue(m.hue, n.hue) and d <= m.radius + n.radius + 12:
                    return d
                return inf

            found, alternatives = assignment(a, b, cost, max(
                (p["marker"].radius + t["marker"].radius + 12 for p in a for t in b), default=12))
            largest_vector_error = max((
                dist(tuple(y - x for x, y in zip(a[i]["ref_px"], a[k]["ref_px"])),
                     tuple(y - x for x, y in zip(b[j]["ref_px"], b[l]["ref_px"])))
                for (i, j), (k, l) in combinations(found, 2)), default=None)
            pairs[key] = {"packets": [query, reference], "visible_counts": [len(a), len(b)],
                          "shared": len(found), "tied_assignment": bool(alternatives),
                          "max_registered_distance_px": max((cost(a[i], b[j]) for i, j in found), default=None),
                          "max_shared_vector_error_px": largest_vector_error,
                          "shared_2d": any(
                              resolved_triangle([a[i]["marker"] for i, _ in triangle]) and
                              resolved_triangle([b[j]["marker"] for _, j in triangle])
                              for triangle in combinations(found, 3)),
                          "unmatched": [
                              [{"native_px": m["marker"].point,
                                "transfers_inside_other_window": in_window(tuple(
                                    x - t for x, t in zip(m["ref_px"], other.translation)))}
                               for i, m in enumerate(side) if i not in {p[k] for p in found}]
                              for k, (side, other) in enumerate(((a, r), (b, q)))]}
    return pairs


def verify_saved():
    if not OPENING.exists():
        print("Preflight verified the lock, pinned files, release roster and registration. No scored run exists.")
        return
    completed = read_json(COMPLETION.read_bytes())
    receipt = read_json(checked_file(OPENING, completed["opening_sha256"]))
    require(receipt["lock_sha256"] == LOCK_SHA256 and
            digest(Path(__file__).read_bytes()) == receipt["runner_sha256"], "opening receipt")
    result = read_json(checked_file(RESULTS, completed["results_sha256"]))
    require(result["opening"] == receipt, "results opening receipt")
    expected = result["intake"]
    checked_file(OUTPUT / "supplied.zip", expected["archive_sha256"])
    checked_file(OUTPUT / "supplied-intake.json", expected["supplied_intake_sha256"])
    for item in expected["returns"].values():
        require(len(checked_file(item["path"], item["sha256"])) == item["bytes"], "saved original length")
    print(f"Verified saved holdout result {completed['results_sha256']} and preserved inputs. No rescoring.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="verify lock and existing evidence without scoring")
    args = parser.parse_args()
    lock, released, labels, dev = preflight()
    if args.verify:
        verify_saved()
        return
    require(not RESULTS.exists() and not COMPLETION.exists(), "one-time evaluation already recorded")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    opening = {"opened_at_utc": now.isoformat(timespec="seconds"),
               "opened_at_local": now.astimezone().isoformat(timespec="seconds"),
               "lock_sha256": LOCK_SHA256, "runner_sha256": digest(Path(__file__).read_bytes())}
    with OPENING.open("xb") as f:
        f.write(json_bytes(opening))
        f.flush()
    rows, intake = intake_holdout(released)
    shifts = {r["view"]: tuple(r["registration"]["translation_px"]) for r in labels["registration"] if "view" in r}
    obs = {p: observation(rows.get(p), entry["layout"], entry["region"], entry["view"], shifts[entry["view"]])
           for p, entry in released.items()}
    observations = {**obs, **dev}
    trials = lock["frozen_candidate_roster"]["holdout"]
    scores = {mode: screen(mode, cap, trials, observations) for mode, cap in lock["selected_caps"].items()}
    results = {"opening": opening, "intake": intake, "caps": lock["selected_caps"], "roster": trials,
               "agreement": agreement(rows, released), "screens": scores,
               "primary_gate": holdout_gate(scores["B"]["trials"], observations),
               "registered_overlap_diagnostic": registered_overlap(trials, observations)}
    preserve(RESULTS, json_bytes(results))
    preflight()
    preserve(COMPLETION, json_bytes({"opening_sha256": digest(OPENING.read_bytes()),
                                    "results_sha256": digest(RESULTS.read_bytes())}))
    print(f"Holdout opened {opening['opened_at_local']}. Primary gate: {results['primary_gate']['status']}.")
    print(f"{RESULTS.resolve()} SHA-256 {digest(RESULTS.read_bytes())}")


if __name__ == "__main__":
    main()
