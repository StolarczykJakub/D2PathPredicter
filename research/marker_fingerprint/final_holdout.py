"""Prepare or verify the Phase 1.6.5 blind release without accessing returns."""

import argparse
from collections import Counter
from dataclasses import asdict
from hashlib import file_digest
from math import dist
from pathlib import Path
import re
import stat
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from research.annotation_retest.evaluate import read_json, require
from research.annotation_retest.prepare import digest, json_bytes
from research.geometry_experiment.blind_packets import RESOLUTION
from research.marker_fingerprint.bounded_match import LIMITS
from research.marker_fingerprint.calibrate import LOCK_PATH as CAL_LOCK, in_window, roster
from research.marker_fingerprint.evaluate import FRAME_PACKETS
from research.marker_fingerprint.evaluate_partial import LOCK_HASH
from research.marker_fingerprint.final_holdout_eval import CAPS_PX, PLANNED_PAIRS, PLANNED_QUERIES
from research.marker_fingerprint.independent_packets import (
    GUIDE, MEMBERS, TRANSFER_RADIUS, VERSION, WINDOW, checked_file, intersection, masked_frame,
    reference_window, registration, template, verify_zip,
)
from research.marker_fingerprint.partial_match import CAP, MIN_BASELINE, MIN_MATCHED, MIN_SPAN, required_count


ROOT = Path("local-data/phase-1-6-5")
OWNER, RELEASE = ROOT / "owner", ROOT / "release"
SELECTION_RULE = Path("docs/FINAL_REPRESENTATION_SELECTION.md")
PROTOCOL = Path("docs/FINAL_REPRESENTATION_PROTOCOL.md")
HANDOFF = Path("docs/FINAL_REPRESENTATION_HANDOFF.md")
LOCK = OWNER / "evaluation-lock.json"
MANIFEST = OWNER / "manifest.json"
FRESH_LAYOUTS = ("mapa-01", "mapa-02", "mapa-03", "mapa-04", "mapa-05", "mapa-08", "mapa-10")
PRIOR_DIAGNOSTIC = Path("local-data/phase-1-6-4")
PINNED = {PRIOR_DIAGNOSTIC / name: checksum for name, checksum in (
    ("initial-before-comparisons.json", "9fd03905c2355592e6d66a49eea9d453a86d9071ac968665660f2365bb06d393"),
    ("initial-results.json", "4041f1e3e98677036900e1643b4d566bdd14bea6c36b90f5ae292d2d56b18e5e"),
    ("before-comparisons.json", "b1f8d16b373c11109a4d245a7d93ab4eda3a2364e9c07d2675c499f0558cb367"),
    ("results.json", "cc89a3108196d99901fb4f39e6f9cc95bc4a14ed9ce2ae7670bf1853ccaa7bcf"),
)}


def verify_diagnostic():
    files = {p.name: read_json(checked_file(p, checksum)) for p, checksum in PINNED.items()}
    current, initial = files["results.json"], files["initial-results.json"]
    require(current["freeze"] == files["before-comparisons.json"] and
            initial["freeze"] == files["initial-before-comparisons.json"], "Phase 1.6.4 freeze")
    for path, checksum in current["freeze"].items():
        checked_file(path, checksum)
    archived = {"research/marker_fingerprint/evaluate_partial.py": "initial-evaluate_partial.py",
                "tests/test_partial_match.py": "initial-test_partial_match.py"}
    for path, checksum in initial["freeze"].items():
        checked_file(PRIOR_DIAGNOSTIC / archived[path] if path in archived else path, checksum)
    for mode in current["trials"]:
        require([row for row in current["trials"][mode] if row["group"] != "synthetic"] ==
                [row for row in initial["trials"][mode] if row["group"] != "synthetic"],
                "Phase 1.6.4 real comparison changed")
    return {path.as_posix(): checksum for path, checksum in PINNED.items()}


def shifted(point, translation):
    return tuple(value + delta for value, delta in zip(point, translation))


def verify_inputs(selection):
    require(selection["layout"] in FRESH_LAYOUTS and selection["resolution"] == list(RESOLUTION)
            and tuple(selection["window_xyxy"]) == WINDOW, "fresh layout or native canvas")
    intake_path = Path("local-data/pilot-intake/manifest.json")
    intake = read_json(checked_file(intake_path, selection["intake_sha256"]))
    recorded, = (entry for entry in intake["datasets"] if entry["id"] == selection["layout"])
    video = (intake_path.parent / recorded["recording"]).resolve()
    require(video == Path(selection["recording"]).resolve()
            and recorded["sha256"] == selection["recording_sha256"]
            and selection["capture_context"] == intake["scope"], "recording provenance")
    with video.open("rb") as stream:
        require(file_digest(stream, "sha256").hexdigest() == recorded["sha256"], "source recording hash")
    for artifact in selection["review_evidence"]:
        checked_file(artifact["path"], artifact["sha256"])
    reference, = selection["references"]
    checked_file(reference["path"], reference["sha256"])
    views = selection["views"]
    require([view["view"] for view in views] == ["r1", "r1b", "r2"]
            and [view["region"] for view in views] == ["region-1", "region-1", "region-2"]
            and len({v["source_sha256"] for v in views}) == 3, "three distinct source images and two regions")
    entries, images, evidence = {}, {}, {}
    for view in views:
        name = view["view"]
        image = masked_frame(checked_file(view["source"], view["source_sha256"]))
        require(len(view["packet_ids"]) == 2 and in_window(view["evaluator_player_px"])
                and view["late_ref"] == reference["id"],
                "needs two packet IDs and a readable in-window player")
        shift = registration(view["wall_anchor_pairs"])
        translation = shift["translation_px"]
        evidence[name] = {"registration": shift, "translation_px": translation,
                          "registered_window_xyxy": reference_window(translation),
                          "registered_player_px": shifted(view["evaluator_player_px"], translation)}
        for packet in view["packet_ids"]:
            require(re.fullmatch(r"[0-9a-f]{10}", packet) and packet not in entries, "opaque unique packet ID")
            entries[packet] = {"packet_id": packet, "filename": packet + ".zip", "layout": selection["layout"],
                               "view": name, "region": view["region"], "frame_sha256": digest(image),
                               "source_sha256": view["source_sha256"]}
            images[packet] = image
    a, b, c = (evidence[name]["registered_window_xyxy"] for name in ("r1", "r1b", "r2"))
    overlap = intersection(a, b)
    require(overlap[0] < overlap[2] and overlap[1] < overlap[3], "no registered primary/moved overlap")
    displacement = dist(evidence["r1"]["registered_player_px"], evidence["r1b"]["registered_player_px"])
    radius = sum(v["evaluator_player_radius_px"] + TRANSFER_RADIUS for v in views[:2])
    gaps = {name: max(c[0] - window[2], window[0] - c[2], c[1] - window[3], window[1] - c[3])
            for name, window in (("r1", a), ("r1b", b))}
    require(displacement > radius and min(gaps.values()) > 2 * TRANSFER_RADIUS,
            "changed player or distinct region not resolved")
    witnesses = {}
    require([w["view"] for w in selection["visibility_witnesses"]] == ["r1", "r1b"],
            "one independent visibility witness per view")
    for witness, other in zip(selection["visibility_witnesses"], ("r1b", "r1")):
        name = witness["view"]
        point = shifted(witness["source_px"], evidence[name]["translation_px"])
        transferred = shifted(point, tuple(-x for x in evidence[other]["translation_px"]))
        require(in_window(witness["source_px"]) and in_window(transferred)
                and witness["hue"] in ("purple", "yellow") and bool(witness["evidence"]),
                "visibility witness is absent from study overlap or unsupported")
        witnesses[name] = {**witness, "registered_px": point, "opposite_source_px": transferred}
    labels = {"views": evidence, "shared_window_xyxy": overlap, "player_displacement_px": displacement,
              "summed_player_transfer_radius_px": radius, "distinct_window_gaps_px": gaps,
              "visibility_witnesses": witnesses}
    return entries, images, labels


def prepare(verify_only=False):
    if not verify_only:
        require(not any(p.exists() for p in (RELEASE, MANIFEST, LOCK)),
                "release already exists. Use --verify.")
    selection_path = OWNER / "selection.json"
    selection_bytes = selection_path.read_bytes()
    selection = read_json(selection_bytes)
    freeze_path = OWNER / "review/selection-rule-freeze.json"
    selection_freeze = read_json(freeze_path.read_bytes())
    checked_file(SELECTION_RULE, selection_freeze[SELECTION_RULE.as_posix()])
    historical = verify_diagnostic()
    cal = read_json(checked_file(CAL_LOCK, LOCK_HASH))
    sources = (*cal["source_and_test_sha256"], *(
        "research/marker_fingerprint/partial_match.py", "research/marker_fingerprint/evaluate_partial.py",
        "research/marker_fingerprint/final_holdout.py", "research/marker_fingerprint/final_holdout_eval.py",
        "tests/test_partial_match.py", "tests/test_final_holdout_eval.py"))
    for path, checksum in cal["source_and_test_sha256"].items():
        checked_file(path, checksum)
    entries, images, labels = verify_inputs(selection)
    ids = tuple(packet for group in FRAME_PACKETS for packet in group)
    candidates = roster(entries, ids)
    pair_counts = Counter()
    for kind, q, refs in candidates:
        for ref in refs:
            if ref not in entries:
                pair_counts["wrong_cross_layout"] += 1
            elif entries[q]["region"] != entries[ref]["region"]:
                pair_counts["wrong_within_layout"] += 1
            else:
                pair_counts[kind] += 1
    require(Counter(row[0] for row in candidates) == PLANNED_QUERIES
            and pair_counts == PLANNED_PAIRS, "unexpected roster denominators")
    guide = GUIDE.read_bytes()
    if not verify_only:
        RELEASE.mkdir()
        for packet, entry in sorted(entries.items()):
            with ZipFile(RELEASE / entry["filename"], "x", compression=ZIP_STORED) as zipped:
                contents = guide, images[packet], json_bytes(template(packet, images[packet]))
                for name, data in zip(MEMBERS, contents):
                    member = ZipInfo(name)
                    member.create_system = 0
                    zipped.writestr(member, data)
    require({p.name for p in RELEASE.iterdir()} == {entry["filename"] for entry in entries.values()},
            "release contains files outside the six ZIPs")
    for packet, entry in entries.items():
        entry["archive_sha256"] = verify_zip(RELEASE / entry["filename"], images[packet], guide)

    manifest = {"phase": "1.6.5", "annotation_protocol": VERSION, "archive_members": MEMBERS,
                "selection_sha256": digest(selection_bytes), "packets": entries, "evaluator_labels": labels}
    manifest_bytes = json_bytes(manifest)
    require(CAPS_PX["C"] == CAP == 6 and MIN_MATCHED == 3 and MIN_SPAN == .25 and MIN_BASELINE == 24
            and all(required_count(n, 0) == max(3, (2 * n + 2) // 3) for n in range(LIMITS.markers + 1)),
            "partial support thresholds changed")
    freeze = (*map(Path, sources), SELECTION_RULE, PROTOCOL, HANDOFF, GUIDE, freeze_path,
              Path("docs/PARTIAL_CONSTELLATION_PROTOCOL.md"), Path("benchmarks/PROTOCOL.md"))
    lock = {"phase": "1.6.5", "status": "awaiting_six_independent_returns", "holdout_opened_at": None,
            "selection_sha256": manifest["selection_sha256"], "manifest_sha256": digest(manifest_bytes),
            "evaluator_labels_sha256": digest(json_bytes(labels)), "packet_manifest_sha256": digest(json_bytes(entries)),
            "frozen_sha256": {p.as_posix(): digest(p.read_bytes()) for p in freeze},
            "historical_diagnostics_sha256": historical, "calibration_lock_sha256": LOCK_HASH,
            "development_input_sha256": cal["development_input_hashes"],
            "layout": selection["layout"], "capture_context": selection["capture_context"],
            "recording_sha256": selection["recording_sha256"],
            "source_images_sha256": {v["source"]: v["source_sha256"] for v in selection["views"]},
            "candidate_roster": candidates, "caps_px": CAPS_PX, "limits": asdict(LIMITS),
            "planned_queries": PLANNED_QUERIES, "planned_pairs": PLANNED_PAIRS}
    lock_bytes = json_bytes(lock)
    if verify_only:
        require(MANIFEST.read_bytes() == manifest_bytes and LOCK.read_bytes() == lock_bytes
                and not LOCK.stat().st_mode & stat.S_IWRITE, "manifest or read-only evaluation lock changed")
    else:
        for path, data in ((MANIFEST, manifest_bytes), (LOCK, lock_bytes)):
            with path.open("xb") as stream:
                stream.write(data)
        LOCK.chmod(stat.S_IREAD)
    for entry in sorted(entries.values(), key=lambda row: row["filename"]):
        print(f'{(RELEASE / entry["filename"]).resolve()}  {entry["archive_sha256"]}')
    print(f"Verified six blind archives from three native images. {LOCK.resolve()}  SHA-256 {digest(lock_bytes)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="reopen and verify an existing release and lock")
    prepare(parser.parse_args().verify)
