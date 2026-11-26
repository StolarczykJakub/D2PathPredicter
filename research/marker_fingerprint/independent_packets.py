"""Build and reopen the frozen Phase 1.6.3 marker-only annotation packets."""

import argparse
from itertools import combinations
from math import atan2, degrees, dist
from pathlib import Path
import re
from statistics import mean
import subprocess
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from research.annotation_retest.evaluate import offset, read_json, require
from research.annotation_retest.prepare import digest, json_bytes, response_template
from research.geometry_experiment.blind_packets import RESOLUTION, verify_image
from research.marker_fingerprint.evaluate import load_inputs


DEFAULT = Path("local-data/phase-1-6-3")
GUIDE = Path("docs/INDEPENDENT_LAYOUT_ANNOTATOR_GUIDE.md")
PLAN = Path("docs/INDEPENDENT_LAYOUT_SCREEN_PLAN.md")
HANDOFF = Path("docs/INDEPENDENT_LAYOUT_HANDOFF.md")
VERSION = "marker-raw-v1"
MEMBERS = ("README.txt", "frame.png", "raw.json")
WINDOW = (736, 364, 1184, 716)
TRANSFER_RADIUS = 6


def checked_file(path, checksum):
    data = Path(path).read_bytes()
    require(digest(data) == checksum, f"SHA-256 mismatch for {path}")
    return data


def registration(pairs):
    source, reference = ([tuple(pair[key]) for pair in pairs] for key in ("source_px", "late_ref_px"))
    require(len(source) >= 3 and len(set(source)) == len(source), "independent wall anchors")
    i, j = max(combinations(range(len(source)), 2), key=lambda edge: dist(*(source[k] for k in edge)))
    a, b = source[i], source[j]
    base = dist(a, b)
    dx, dy = offset(b, a)
    ref_dx, ref_dy = offset(reference[j], reference[i])
    scale = dist(reference[i], reference[j]) / base
    rotation = (degrees(atan2(ref_dy, ref_dx) - atan2(dy, dx)) + 180) % 360 - 180
    translation = tuple(map(mean, zip(*(offset(reference[k], source[k]) for k in (i, j)))))
    holdouts = [k for k in range(len(source)) if k not in (i, j)]
    off_axis = max(abs(dx * (source[k][1] - a[1]) - dy * (source[k][0] - a[0])) / base
                   for k in holdouts)
    residuals = [dist(tuple(x + t for x, t in zip(p, translation)), q)
                 for p, q in zip(source, reference)]
    require(base >= 64 and off_axis > 6 and 0.97 <= scale <= 1.03 and
            abs(rotation) <= 2 and max(residuals) <= 6, "wall-anchor registration screen failed")
    return {"fit_indices": [i, j], "holdout_indices": holdouts, "translation_px": translation,
            "scale_ratio": scale, "rotation_deg": rotation, "baseline_px": base,
            "max_holdout_off_axis_px": off_axis, "residuals_px": residuals,
            "max_holdout_residual_px": max(residuals[k] for k in holdouts),
            "transfer_radius_px": TRANSFER_RADIUS}


def reference_window(translation):
    return tuple(value + translation[i % 2] for i, value in enumerate(WINDOW))


def intersection(a, b):
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))


def prepare_truth(selection):
    require(selection["resolution"] == list(RESOLUTION) and tuple(selection["window_xyxy"]) == WINDOW,
            "window or resolution mismatch")
    require(selection["development"] == "mapa-07", "development split changed")
    require({layout["split"] for layout in selection["layouts"]} == {"calibration", "holdout"} and
            len(selection["layouts"]) == 2 and
            len({item["layout"] for item in selection["layouts"]} | {selection["development"]}) == 3,
            "layout split")
    checked_file(selection["development_review"]["path"], selection["development_review"]["sha256"])
    checked_file(selection["deduplication"]["review_image"], selection["deduplication"]["sha256"])
    ids, frame_hashes, evidence = set(), set(), []
    for layout in selection["layouts"]:
        checked_file(layout["recording"], layout["recording_sha256"])
        checked_file(layout["late_reference"], layout["late_reference_sha256"])
        require([view["view"] for view in layout["views"]] == ["r1", "r1b", "r2"] and
                [view["region"] for view in layout["views"]] == ["region-1", "region-1", "region-2"],
                "each layout needs two regions and a changed view")
        bounds, players = {}, {}
        for view in layout["views"]:
            checked_file(view["source"], view["source_sha256"])
            require(view["source_sha256"] not in frame_hashes, "duplicate source image")
            frame_hashes.add(view["source_sha256"])
            require(len(view["packet_ids"]) == 2, "two independent packages per view")
            for id_ in view["packet_ids"]:
                require(re.fullmatch(r"[0-9a-f]{10}", id_) and id_ not in ids, "invalid packet ID")
                ids.add(id_)
            try:
                fit = registration(view["wall_anchor_pairs"])
            except ValueError as error:
                raise ValueError(f"{layout['layout']} {view['view']}: {error}") from error
            bounds[view["view"]] = reference_window(fit["translation_px"])
            players[view["view"]] = tuple(x + t for x, t in zip(
                view["evaluator_player_px"], fit["translation_px"]))
            evidence.append({"layout": layout["layout"], "view": view["view"],
                             "registration": fit, "registered_window_xyxy": bounds[view["view"]],
                             "registered_player_px": players[view["view"]]})
        overlap = intersection(bounds["r1"], bounds["r1b"])
        require(overlap[2] > overlap[0] and overlap[3] > overlap[1], "no registered repeat-view overlap")
        displacements = dist(players["r1"], players["r1b"])
        uncertainty = sum(v["evaluator_player_radius_px"] + TRANSFER_RADIUS for v in layout["views"][:2])
        require(displacements > uncertainty, "changed player position unresolved")
        gaps = {}
        for name in ("r1", "r1b"):
            a, b = bounds[name], bounds["r2"]
            separation = max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])
            require(separation > 2 * TRANSFER_RADIUS, f"{layout['layout']} {name}: regions not disjoint")
            gaps[name] = separation
        evidence.append({"layout": layout["layout"], "shared_window_xyxy": overlap,
                         "repeat_view_displacement_px": displacements, "summed_radius_px": uncertainty,
                         "region_2_axis_gaps_px": gaps})
    require(len(ids) == 12 and len({item["recording_sha256"] for item in selection["layouts"]}) == 2,
            "package count or duplicate recording")
    return evidence


def ffmpeg(frame, options):
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
            "-f", "image2pipe", "-c:v", "png", "-i", "pipe:0", "-map_metadata", "-1",
            "-frames:v", "1", "-pix_fmt", "rgb24", "-threads", "1"]
    return subprocess.run(args + options + ["pipe:1"], input=frame, capture_output=True,
                          check=True).stdout


def masked_frame(source):
    verify_image(source)
    x0, y0, x1, y1 = WINDOW
    width, height = RESOLUTION
    filter_ = f"crop={x1-x0}:{y1-y0}:{x0}:{y0},pad={width}:{height}:{x0}:{y0}:black"
    frame = ffmpeg(source, ["-vf", filter_, "-c:v", "png", "-f", "image2pipe"])
    verify_image(frame)
    before, after = (ffmpeg(img, ["-f", "rawvideo"]) for img in (source, frame))
    stride = width * 3
    require(len(before) == len(after) == stride * height, "decoded PNG size")
    for y in range(height):
        first = y * stride
        if y0 <= y < y1:
            left, right = (first + x * 3 for x in (x0, x1))
            require(before[left:right] == after[left:right] and
                    not any(after[first:left]) and not any(after[right:first+stride]),
                    "window mask changed source pixels or leaked exterior pixels")
        else:
            require(not any(after[first:first+stride]), "nonblack exterior row")
    return frame


def template(packet_id, frame):
    draft = response_template(packet_id, frame, "raw")
    draft["protocol_version"] = VERSION
    del draft["walls"]
    del draft["search_complete"]["walls"]
    return draft


def verify_zip(path, image, guide):
    packet_id = path.stem
    with ZipFile(path) as zipped:
        require(tuple(zipped.namelist()) == MEMBERS and zipped.testzip() is None, str(path))
        require(not zipped.comment and
                all(not m.comment and not m.extra and m.date_time == (1980, 1, 1, 0, 0, 0)
                    and m.create_system == 0 and m.compress_type == ZIP_STORED
                    for m in zipped.infolist()), f"unexpected ZIP metadata in {path}")
        frame = zipped.read("frame.png")
        verify_image(frame)
        require(frame == image and zipped.read("README.txt") == guide and
                zipped.read("raw.json") == json_bytes(template(packet_id, image)),
                f"wrong image, guide or template in {path}")
    return digest(path.read_bytes())


def prepare(root, verify_only=False):
    load_inputs()
    lock_dir = Path("local-data/phase-1-6-2")
    for file, checksum in read_json((lock_dir / "before-comparisons.json").read_bytes()).items():
        checked_file(file, checksum)
    results_sha256 = digest((lock_dir / "results.json").read_bytes())
    owner, release = root / "owner", root / "release"
    selection_path = owner / "selection.json"
    selection = read_json(selection_path.read_bytes())
    truth = prepare_truth(selection)
    guide = GUIDE.read_bytes()
    if verify_only:
        require(release.is_dir(), "missing release directory")
    else:
        require(not release.exists() and not (owner / "manifest.json").exists(),
                "existing release. Verify it instead of overwriting.")
    entries = []
    images = {}
    for layout in selection["layouts"]:
        for view in layout["views"]:
            frame = masked_frame(Path(view["source"]).read_bytes())
            for packet_id in view["packet_ids"]:
                images[packet_id] = frame
                entries.append({"packet_id": packet_id, "filename": packet_id + ".zip",
                                "layout": layout["layout"], "split": layout["split"],
                                "view": view["view"], "region": view["region"],
                                "source_sha256": view["source_sha256"], "frame_sha256": digest(frame)})
    if not verify_only:
        release.mkdir()
        for item in sorted(entries, key=lambda row: row["filename"]):
            name = item["filename"]
            id_ = item["packet_id"]
            with ZipFile(release / name, "x", compression=ZIP_STORED) as zipped:
                for member, data in zip(MEMBERS, (guide, images[id_], json_bytes(template(id_, images[id_])))):
                    entry = ZipInfo(member)
                    entry.create_system = 0
                    zipped.writestr(entry, data)
    require({p.name for p in release.iterdir()} == {row["filename"] for row in entries},
            "unexpected files in release directory")
    for item in entries:
        item["archive_sha256"] = verify_zip(release / item["filename"], images[item["packet_id"]], guide)
    freeze = (GUIDE, PLAN, HANDOFF, Path(__file__).resolve().relative_to(Path.cwd()),
              Path("docs/REPRESENTATION_DECISION.md"), Path("benchmarks/PROTOCOL.md"),
              Path("research/marker_fingerprint/match.py"))
    manifest = {"phase": "1.6.3", "status": "awaiting_annotation_returns",
                "annotation_protocol": VERSION, "archive_members": MEMBERS,
                "selection_sha256": digest(selection_path.read_bytes()),
                "stage1_local_results_sha256": results_sha256,
                "frozen_sha256": {p.as_posix(): digest(p.read_bytes()) for p in freeze},
                "registration": truth,
                "packets": sorted(entries, key=lambda row: row["packet_id"])}
    output = owner / "manifest.json"
    if verify_only:
        require(output.read_bytes() == json_bytes(manifest), "manifest or frozen inputs changed")
    else:
        with output.open("xb") as handle:
            handle.write(json_bytes(manifest))
    for item in manifest["packets"]:
        print(f"{(release / item['filename']).resolve()}  {item['archive_sha256']}")
    print(f"Verified {len(entries)} archives from {len(set(digest(data) for data in images.values()))} images.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    prepare(args.root, args.verify)
