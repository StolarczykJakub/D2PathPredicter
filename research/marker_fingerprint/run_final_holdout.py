"""Import, score once, or verify the owner-approved Phase 1.6.5 holdout."""

import argparse
from datetime import datetime, timezone
from io import BytesIO
from itertools import combinations
from math import dist
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

from research.annotation_retest.evaluate import read_json, require
from research.annotation_retest.prepare import digest, json_bytes
from research.marker_fingerprint import final_holdout, final_holdout_eval, holdout
from research.marker_fingerprint.calibrate import agreement, observation, preserve, validate_return
from research.marker_fingerprint.independent_packets import checked_file
from research.marker_fingerprint.partial_match import (
    MIN_SPAN, box_area, reliable_triangle, required_count, span_fraction,
)


LOCK_HASH = "877fc9c32533691f623332acb48749811b8274c5b5aa04ebdcd56fe80fd5e8c6"
ARCHIVE = Path("docs/phase_1_6_5_holdout_returns.zip")
OUTPUT = final_holdout.OWNER / "holdout"
OPENING = OUTPUT / "opening.json"
INTAKE = OUTPUT / "intake-and-eligibility.json"
STARTED = OUTPUT / "scoring-started.json"
RESULTS = OUTPUT / "results.json"
COMPLETION = OUTPUT / "completion.json"


def preflight():
    lock = read_json(checked_file(final_holdout.LOCK, LOCK_HASH))
    final_holdout.prepare(verify_only=True)
    _, _, _, development = holdout.preflight()
    holdout.verify_saved()
    manifest = read_json(checked_file(final_holdout.MANIFEST, lock["manifest_sha256"]))
    return lock, manifest, development


def import_returns(packets):
    archive = ARCHIVE.read_bytes()
    preserve(OUTPUT / "supplied.zip", archive)
    rows, audit = {}, {}
    with ZipFile(BytesIO(archive)) as zipped:
        expected = {"intake_manifest.json", *(f"{p}/raw.json" for p in packets)}
        require(len(zipped.namelist()) == len(expected) and set(zipped.namelist()) == expected
                and zipped.testzip() is None, "return archive roster or CRC")
        receipt = zipped.read("intake_manifest.json")
        preserve(OUTPUT / "supplied-intake.json", receipt)
        for packet in packets:
            member = f"{packet}/raw.json"
            preserve(OUTPUT / "returns" / member, zipped.read(member))
        supplied = read_json(receipt)
        entries = {row["packet_id"]: row for row in supplied["returns"]}
        require(supplied["phase"] == "1.6.5" and supplied["split"] == "holdout"
                and len(supplied["returns"]) == len(entries) and entries.keys() == packets.keys(),
                "intake phase or packet roster")
        for packet, released in packets.items():
            member = f"{packet}/raw.json"
            path = OUTPUT / "returns" / member
            original = path.read_bytes()
            entry = entries[packet]
            audit[packet] = record = {
                "path": path.as_posix(), "original_upload_name": entry["original_upload_name"],
                "sha256": digest(original), "bytes": len(original), "view": released["view"],
                "reviewer_id": None, "session_id": None, "dispatch_time": None, "receipt_time": None,
                "handoff_time": None, "exposure_record": None, "deviation_record": None,
            }
            try:
                require(entry["return_path"] == member and entry["sha256"] == record["sha256"]
                        and type(entry["byte_count"]) is int and entry["byte_count"] == len(original),
                        "intake path, SHA-256 or byte count")
                release = checked_file(final_holdout.RELEASE / released["filename"],
                                       released["archive_sha256"])
                with ZipFile(BytesIO(release)) as packet_zip:
                    template = read_json(packet_zip.read("raw.json"))
                    require(template["packet_id"] == packet and template["frame_sha256"] ==
                            digest(packet_zip.read("frame.png")) == released["frame_sha256"],
                            "release packet or frame identity")
                row = read_json(original)
                validate_return(row, template)
            except (ValueError, TypeError, AttributeError, KeyError) as exc:
                record.update(validation="FAIL", error=str(exc))
                continue
            rows[packet] = row
            observed = [mark for mark in row["markers"] if mark["status"] == "OBSERVED"]
            record.update(validation="PASS", frame_sha256=row["frame_sha256"],
                          complete_search=row["search_complete"]["markers"],
                          elapsed_minutes=row["elapsed_minutes"], time_limit_reached=row["time_limit_reached"],
                          player_status=row["player"]["status"], observed_markers=len(observed),
                          unresolved_markers=len(row["markers"]) - len(observed),
                          missing_spans=sum(mark["segment_px"] is None for mark in observed),
                          notes=row["notes"])
    intake = {"archive_sha256": digest(archive), "archive_bytes": len(archive),
              "supplied_intake_sha256": digest(receipt), "external_intake_note": supplied["note"],
              "returns": audit}
    preserve(OUTPUT / "intake.json", json_bytes(intake))
    require(rows.keys() == packets.keys(), "return integrity failure. See intake.json.")
    return rows, intake


def geometry_audit(trial, candidate, floor):
    views = (trial.query, candidate.view)
    point_sets = tuple(view.native.points for view in views)
    pairs = sorted(candidate.truth)
    left, right = tuple(tuple(points[pair[i]] for pair in pairs)
                        for i, points in enumerate(point_sets))
    counts = [len(points) for points in point_sets]
    areas = [span_fraction(matched, box_area(points)) if matched and points else None
             for matched, points in zip((left, right), point_sets)]
    triangle = next((triple for triple in combinations(pairs, 3)
                     if all(reliable_triangle(tuple(points[pair[i]] for pair in triple))
                            for i, points in enumerate(point_sets))), None)
    count_ok = len(pairs) >= required_count(*counts)
    area_ok = all(area is not None and area >= MIN_SPAN for area in areas)
    require(floor == (count_ok and area_ok and triangle is not None), "coverage audit disagrees with frozen floor")
    return {"visible": counts, "shared": len(pairs), "marker_index_pairs": pairs,
            "required_count": required_count(*counts), "count_fractions": [
                len(pairs) / size if size else None for size in counts],
            "area_fractions": areas, "count_floor": count_ok, "area_floor": area_ok,
            "reliable_triangle": triangle}


def eligibility(lock, manifest, rows, development):
    packets, labels = manifest["packets"], manifest["evaluator_labels"]
    views = {p: observation(rows[p], entry["layout"], entry["region"], entry["view"],
                            labels["views"][entry["view"]]["translation_px"])
             for p, entry in packets.items()}
    witnesses = labels["visibility_witnesses"]
    witness_audit = {p: {
        owner: [{"native_px": mark.point, "distance_px": distance}
                for mark in view.native.points
                if mark.hue == witness["hue"]
                and (distance := dist(final_holdout.shifted(mark.point, view.translation),
                                      witness["registered_px"])) <= 8]
        for owner, witness in witnesses.items()}
        for p, view in views.items()}
    for packet, view in views.items():
        for owner, witness in witnesses.items():
            require(len(witness_audit[packet][owner]) == final_holdout_eval.witness_hits(view, witness),
                    "witness audit disagrees with frozen witness rule")
    observations = {**views, **development}
    audits, coverage = [], []
    for kind, query, refs in lock["candidate_roster"]:
        trial, floors, audit = final_holdout_eval.build_trial(kind, query, refs, observations, witnesses)
        audits.append(audit)
        for candidate, floor, pair in zip(trial.candidates, floors, audit):
            if candidate.truth is not None:
                coverage.append({"group": kind, **pair, **geometry_audit(trial, candidate, floor)})
    return observations, {"agreement": agreement(rows, packets), "witness_hits": witness_audit,
                          "pairs": audits, "coverage": coverage}


def load_intake():
    intake = read_json((OUTPUT / "intake.json").read_bytes())
    archive = checked_file(OUTPUT / "supplied.zip", intake["archive_sha256"])
    require(len(archive) == intake["archive_bytes"] and ARCHIVE.read_bytes() == archive,
            "supplied and preserved archives differ")
    rows = {}
    with ZipFile(BytesIO(archive)) as zipped:
        require(zipped.read("intake_manifest.json") == checked_file(
            OUTPUT / "supplied-intake.json", intake["supplied_intake_sha256"]), "preserved manifest differs")
        for packet, entry in intake["returns"].items():
            data = checked_file(entry["path"], entry["sha256"])
            require(entry["validation"] == "PASS" and len(data) == entry["bytes"]
                    and data == zipped.read(f"{packet}/raw.json"), f"preserved return differs for {packet}")
            rows[packet] = read_json(data)
    return rows, intake


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("intake", "score", "verify"))
    action = parser.parse_args().action
    lock, manifest, development = preflight()
    if action == "intake" and not OPENING.exists():
        OUTPUT.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        with OPENING.open("xb") as stream:
            stream.write(json_bytes({"opened_at_utc": now.isoformat(timespec="seconds"),
                                     "opened_at_local": now.astimezone().isoformat(timespec="seconds"),
                                     "local_timezone": "Europe/Warsaw", "lock_sha256": LOCK_HASH}))
    opening = read_json(OPENING.read_bytes())
    require(opening["lock_sha256"] == LOCK_HASH, "opening lock identity")
    if action == "intake":
        require(not STARTED.exists(), "holdout scoring already started")
        rows, intake = import_returns(manifest["packets"])
    else:
        rows, intake = load_intake()
    observations, audit = eligibility(lock, manifest, rows, development)
    pre_score = {"opening": opening, "intake": intake, "audit": audit}
    if action == "intake":
        preserve(INTAKE, json_bytes(pre_score))
        print(f"Intake and pre-match eligibility recorded in {INTAKE}")
        return

    require(INTAKE.read_bytes() == json_bytes(pre_score), "saved pre-match eligibility differs")
    bound = {p.name: digest(p.read_bytes()) for p in (OPENING, INTAKE, Path(__file__))}
    if action == "score":
        require(not RESULTS.exists() and not COMPLETION.exists(), "score already saved")
        with STARTED.open("xb") as stream:
            stream.write(json_bytes(bound))
        start = perf_counter()
        result = final_holdout_eval.evaluate(lock["candidate_roster"], observations,
                                             manifest["evaluator_labels"]["visibility_witnesses"])
        elapsed = perf_counter() - start
        require(result["intake_and_truth"] == audit["pairs"], "scored roster or eligibility differs")
        preserve(RESULTS, json_bytes({**result, "elapsed_seconds": elapsed}))
        preflight()
        preserve(COMPLETION, json_bytes({**bound, RESULTS.name: digest(RESULTS.read_bytes())}))
        print(f"Gate {result['gate']['verdict']}. Scoring and evaluation took {elapsed:.3f} s.")
    else:
        expected = {**bound, RESULTS.name: digest(RESULTS.read_bytes())}
        require(read_json(STARTED.read_bytes()) == bound and
                read_json(COMPLETION.read_bytes()) == expected, "completion integrity")
        print(f"Verified saved result {expected[RESULTS.name]} and all evidence. No rescoring.")


if __name__ == "__main__":
    main()
