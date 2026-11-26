"""Prepare Phase 1.6.1 handoff files from the locked Stage 0 and Stage 3 release frames."""

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from research.geometry_experiment import blind_packets


ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "docs/ANNOTATION_PROTOCOL_V2.md"
PLAN = ROOT / "docs/ANNOTATION_RETEST_PLAN.md"
V1 = ROOT / "local-data/phase-1-6"
CASE = "b16-k9w4"
ASSIGNMENTS = (
    ("k4m7q", 0, ("semantic", "raw")),
    ("h9v2c", 0, ("raw", "semantic")),
    ("p6r8t", 3, ("semantic", "raw")),
    ("w3j5n", 3, ("raw", "semantic")),
)


def digest(data):
    return sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def point_mark():
    return {"status": None, "px": None, "error_px": None, "note": ""}


def response_template(packet_id, frame, task):
    response = {
        "protocol_version": 2,
        "packet_id": packet_id,
        "frame_sha256": digest(frame),
        "resolution": list(blind_packets.RESOLUTION),
        "player": point_mark(),
        "walls": [],
        "markers": [],
        "search_complete": {"walls": None, "markers": None},
        "elapsed_minutes": None,
        "time_limit_reached": None,
        "notes": [],
    }
    if task == "semantic":
        response.update(
            entrance={name: point_mark() for name in (
                "staircase_scene", "automap_glyph", "arrival_room_center", "player_arrival"
            )},
            orientation={"status": None, "direction": None, "segment_px": None,
                         "error_px": None, "note": ""},
            regions=[],
            openings=[],
            connections=[],
            terminal_assessments=[],
        )
    return response


def read_frame(stage, archive_digests):
    name = blind_packets.archive_name(CASE, stage)
    source = (V1 / "role-a-release" / name).read_bytes()
    if digest(source) != archive_digests[name]:
        raise ValueError(f"Version 1 release hash differs for {name}")
    with ZipFile(BytesIO(source)) as packet:
        if tuple(packet.namelist()) != blind_packets.MEMBERS or packet.testzip() is not None:
            raise ValueError(f"Invalid version 1 archive {name}")
        image = packet.read("frame.png")
        blind_packets.verify_image(image)
        template = json.loads(packet.read("observation.json"))
        if template != blind_packets.draft(CASE, stage, image):
            raise ValueError(f"Version 1 template differs for {name}")
    return image, name, template["frame_id"]


def reviewer_sections(guide):
    sections = {}
    for heading in ("Reviewer instructions", "Semantic pass", "Raw pass"):
        section = guide.split(f"\n## {heading}\n", 1)[1].split("\n## ", 1)[0].strip()
        sections[heading] = section.replace("`", "") + "\n"
    return sections


def make_packet(packet_id, order, frame, sections):
    instructions = [
        "Single-frame annotation",
        "",
        f"Packet {packet_id}",
        "",
        f"First pass  {order[0]}-guide.txt and {order[0]}.json",
        f"Second pass {order[1]}-guide.txt and {order[1]}.json",
        "",
        "Return semantic.json and raw.json. Keep this image and your measurements private.",
        "",
        sections["Reviewer instructions"],
    ]
    members = {
        "README.txt": "\n".join(instructions).encode("utf-8"),
        "frame.png": frame,
        "semantic-guide.txt": sections["Semantic pass"].encode("utf-8"),
        "raw-guide.txt": sections["Raw pass"].encode("utf-8"),
        "semantic.json": json_bytes(response_template(packet_id, frame, "semantic")),
        "raw.json": json_bytes(response_template(packet_id, frame, "raw")),
    }
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_STORED) as packet:
        for name, data in members.items():
            entry = ZipInfo(name)
            entry.create_system = 0
            packet.writestr(entry, data)
    archive = buffer.getvalue()
    with ZipFile(BytesIO(archive)) as packet:
        if tuple(packet.namelist()) != tuple(members) or packet.testzip() is not None:
            raise ValueError(f"Could not verify packet {packet_id}")
        if packet.comment or any(entry.extra or entry.comment or entry.date_time != (1980, 1, 1, 0, 0, 0)
                                 for entry in packet.infolist()):
            raise ValueError(f"Unexpected archive metadata in {packet_id}")
    return archive


def prepare(output):
    if output.exists():
        raise ValueError("Choose a new output directory for this release")
    guide = GUIDE.read_bytes()
    plan = PLAN.read_bytes()
    v1_lock = (V1 / "role-c/pilot-lock.json").read_bytes()
    archive_digests = json.loads(v1_lock)["blind_release_sha256"]
    frames = {stage: read_frame(stage, archive_digests) for stage in (0, 3)}
    sections = reviewer_sections(guide.decode("utf-8-sig"))
    archives = {}
    assignments = []
    for packet_id, stage, order in ASSIGNMENTS:
        frame, source_archive, source_frame = frames[stage]
        name = f"{packet_id}.zip"
        archive = make_packet(packet_id, order, frame, sections)
        archives[name] = archive
        assignments.append({
            "packet_id": packet_id,
            "filename": name,
            "archive_sha256": digest(archive),
            "frame_sha256": digest(frame),
            "v1_archive": source_archive,
            "v1_archive_sha256": archive_digests[source_archive],
            "v1_frame": source_frame,
            "source_stage": stage,
            "pass_order": order,
        })
    manifest = {
        "phase": "1.6.1",
        "protocol_version": 2,
        "distribution": "Send one ZIP only to each fresh reviewer. Keep this manifest private.",
        "prior_lock_sha256": digest(v1_lock),
        "frozen_sha256": {
            GUIDE.relative_to(ROOT).as_posix(): digest(guide),
            PLAN.relative_to(ROOT).as_posix(): digest(plan),
            Path(__file__).resolve().relative_to(ROOT).as_posix(): digest(Path(__file__).read_bytes()),
        },
        "assignments": assignments,
    }
    output.mkdir(parents=True, exist_ok=False)
    release = output / "release"
    release.mkdir()
    owner = output / "owner"
    owner.mkdir()
    for name, data in archives.items():
        (release / name).write_bytes(data)
    (owner / "manifest.json").write_bytes(json_bytes(manifest))
    print(f"{len(archives)} isolated packets from {len(frames)} frames in {release}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new directory for packets and private alias manifest")
    args = parser.parse_args()
    try:
        prepare(args.output)
    except (OSError, KeyError, ValueError) as exc:
        parser.exit(2, f"Packet preparation failed: {exc}\n")
