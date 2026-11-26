"""Release one anonymized early frame per archive for manual blind annotation."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, ZipInfo

STAGES = range(4)
RESOLUTION = (1920, 1080)
MASKS = ((0, 0, 140, 335), (1680, 0, 240, 155))
MEMBERS = ("README.txt", "frame.png", "observation.json")

INSTRUCTIONS = """Blind geometry annotation

Open frame.png at 100% or use an image viewer that reports the pixel coordinates.
X increases rightward, Y downward. Black edge rectangles cover interface text.
Fill observation.json using this frame and any already submitted earlier stages.
Use null for a position or direction you cannot read. Return the completed JSON
before opening any next-stage file. Record the minutes you spent annotating.

- player_px is the bright player marker on the automap, with player_error_px
  as the estimated radius of marking error.
- entrance_px is the centre of the arrival room when visible. For orientation,
  use N, NE, E, SE, S, SW, W, NW, NS, NE_SW, EW, NW_SE or null. Use an axis
  when only the axis is clear. Use consistent room IDs for recognizable rooms.
- rooms take objects like {"id":"r01","center_px":[x,y],"error_px":5}.
  connections take pairs like ["r01","r02"] for a visible passage between rooms.
- boundaries take objects like {"room":"r01","direction":"NE","segment_px":
  [[x1,y1],[x2,y2]],"status":"unexplored_direction","note":"path clipped"}.
  Use confirmed_passage, confirmed_wall, confirmed_dead_end,
  unexplored_direction or ambiguous_geometry. Add room IDs to dead_ends only
  when all exits are visible and there is a single confirmed departure.
- Set uncertain_geometry when some features are unreadable or ambiguous.
  Describe partial outlines or obstructions in uncertainty_notes. Include
  only confirmed room centres and links in the corresponding lists.
"""


def draft(case_id, stage, frame):
    return {
        "schema_version": 1,
        "case_id": case_id,
        "stage": stage,
        "frame_id": f"{case_id}-{stage:02}",
        "frame_sha256": sha256(frame).hexdigest(),
        "resolution": list(RESOLUTION),
        "player_px": None,
        "player_error_px": None,
        "entrance_px": None,
        "entrance_orientation": None,
        "rooms": [],
        "connections": [],
        "boundaries": [],
        "dead_ends": [],
        "uncertain_geometry": None,
        "uncertainty_notes": [],
        "elapsed_minutes": None,
    }


def png_size(frame):
    if frame[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR":
        raise ValueError("Invalid PNG header")
    return struct.unpack(">II", frame[16:24])


def verify_image(frame):
    if png_size(frame) != RESOLUTION:
        raise ValueError("Unexpected release image dimensions")
    offset = 8
    while offset < len(frame):
        size, kind = struct.unpack(">I4s", frame[offset:offset + 8])
        if kind not in (b"IHDR", b"pHYs", b"IDAT", b"IEND"):
            raise ValueError(f"Unexpected release PNG chunk {kind!r}")
        offset += size + 12
        if kind == b"IEND" and offset == len(frame):
            return
    raise ValueError("Invalid release PNG terminator")


def sanitized_frame(source):
    if png_size(source.read_bytes()) != RESOLUTION:
        raise ValueError(f"Review the text masking for the resolution of {source}")
    masks = ",".join(f"drawbox=x={x}:y={y}:w={w}:h={h}:color=black:t=fill" for x, y, w, h in MASKS)
    run = subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
        "-i", str(source), "-vf", masks, "-map_metadata", "-1", "-an",
        "-frames:v", "1", "-pix_fmt", "rgb24", "-threads", "1",
        "-f", "image2pipe", "-c:v", "png", "pipe:1",
    ], capture_output=True, check=True)
    return run.stdout


def archive_name(case_id, stage):
    return f"{case_id}-{stage:02}.zip"


def verify(folder, case_id):
    for stage in STAGES:
        path = folder / archive_name(case_id, stage)
        with ZipFile(path) as packet:
            entries = packet.infolist()
            if tuple(packet.namelist()) != MEMBERS or packet.testzip() is not None:
                raise ValueError(f"Unexpected archive contents or CRC in {path.name}")
            if packet.comment or any(
                entry.comment or entry.extra or entry.date_time != (1980, 1, 1, 0, 0, 0)
                for entry in entries
            ):
                raise ValueError(f"Unexpected archive metadata in {path.name}")
            frame = packet.read("frame.png")
            verify_image(frame)
            if json.loads(packet.read("observation.json")) != draft(case_id, stage, frame):
                raise ValueError(f"Wrong frame or annotation template in {path.name}")
            if packet.read("README.txt") != INSTRUCTIONS.encode("ascii"):
                raise ValueError(f"Unexpected instructions in {path.name}")
        print(f"{path.name}  {sha256(path.read_bytes()).hexdigest()}")


def build(source, folder, case_id):
    for stage in STAGES:
        if (folder / archive_name(case_id, stage)).exists():
            raise ValueError("A release already exists. Use a new output directory to rebuild.")
    frames = [sanitized_frame(source / f"stage-{stage}.png") for stage in STAGES]
    for frame in frames:
        verify_image(frame)
    folder.mkdir(parents=True, exist_ok=True)
    for stage, frame in enumerate(frames):
        template = (json.dumps(draft(case_id, stage, frame), indent=2) + "\n").encode("ascii")
        with ZipFile(folder / archive_name(case_id, stage), "x") as packet:
            for name, data in zip(MEMBERS, (INSTRUCTIONS.encode("ascii"), frame, template)):
                packet.writestr(ZipInfo(name), data, compress_type=ZIP_DEFLATED)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="folder containing the four small release archives")
    parser.add_argument("case_id", help="anonymous case identifier")
    parser.add_argument("--from-early", type=Path, help="generate from four reviewed stage-0.png through stage-3.png files")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,23}", args.case_id):
        parser.error("case_id must be an anonymous lowercase identifier")
    try:
        if args.from_early:
            build(args.from_early, args.folder, args.case_id)
        verify(args.folder, args.case_id)
        return 0
    except (BadZipFile, OSError, ValueError, struct.error, subprocess.CalledProcessError) as error:
        print(f"Blind packet error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
