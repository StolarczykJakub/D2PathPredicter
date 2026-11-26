"""Validate the dataset before handing visible observations to the predictor."""

from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path

from .coordinates import ORIENTATIONS, SECTORS, Point

TARGETS = ("NEXT", "WP")
SCENARIO = {"game": "D2R", "area": "Catacombs2", "difficulty": "Normal", "entry": "Catacombs1"}
FILES = ("metadata.json", "observations.json", "truth.json")
AXES = {"NS": {"N", "S"}, "NE_SW": {"NE", "SW"}, "EW": {"E", "W"}, "NW_SE": {"NW", "SE"}}


class DatasetError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Geometry:
    rooms: tuple[Point, ...]
    connections: tuple[tuple[Point, Point], ...]


@dataclass(frozen=True, slots=True)
class Observation:
    orientation: str | None
    player: Point | None
    player_error: float
    geometry: Geometry
    branches: tuple[tuple[Point, str], ...]
    dead_ends: tuple[Point, ...]


@dataclass(frozen=True, slots=True)
class Frame:
    layout_id: str
    observation_id: str
    stage: int
    uncertain_geometry: bool
    observation: Observation


@dataclass(frozen=True, slots=True)
class Target:
    position: Point
    error: float


@dataclass(frozen=True, slots=True)
class Dataset:
    dataset_id: str
    kind: str
    capture: dict
    splits: dict[str, str]
    frames: tuple[Frame, ...]
    targets: dict[str, dict[str, Target | None]]
    visibility: dict[str, dict[str, str]]
    hashes: dict[str, str]


def require(condition, message):
    if not condition:
        raise DatasetError(message)


def fields(value, path, *expected):
    require(isinstance(value, dict), f"{path} must be an object")
    require(set(value) == set(expected), f"{path} fields must be {', '.join(expected)}")
    return value


def rows(value, path):
    require(isinstance(value, list), f"{path} must be an array")
    return value


def nonempty(value, path):
    require(isinstance(value, str) and bool(value.strip()), f"{path} must be a nonempty string")
    return value


def point(value, path, *, pixels=False):
    require(isinstance(value, list) and len(value) == 2, f"{path} must be a pair")
    if pixels:
        return tuple(number(coord, path) for coord in value)
    require(all(type(coord) is int and abs(coord) <= 1_000_000 for coord in value),
            f"{path} must contain integer coordinates within ±1000000")
    return tuple(value)


def number(value, path):
    require(type(value) in (int, float) and abs(value) <= 1_000_000,
            f"{path} must be finite and within ±1000000")
    return float(value)


def nonnegative(value, path):
    value = number(value, path)
    require(value >= 0, f"{path} must be nonnegative")
    return value


def geometry(room_rows, connection_rows, path):
    rooms = [point(room, f"{path} room") for room in rows(room_rows, f"{path} rooms")]
    room_set = set(rooms)
    require(len(room_set) == len(rooms), f"{path} contains duplicate rooms")
    connections = []
    for link in rows(connection_rows, f"{path} connections"):
        require(isinstance(link, list) and len(link) == 2, f"{path} link must join two rooms")
        a, b = (point(end, f"{path} link endpoint") for end in link)
        require(a != b and a in room_set and b in room_set, f"{path} has an invalid connection")
        connections.append((min(a, b), max(a, b)))
    require(len(set(connections)) == len(connections), f"{path} contains duplicate connections")
    return Geometry(tuple(sorted(rooms)), tuple(sorted(connections)))


def layout_signature(complete: Geometry):
    """Group the same graph under translation and square-grid symmetries."""
    signatures = []
    for swap, sx, sy in product((False, True), (-1, 1), (-1, 1)):
        transformed = {
            (x, y): (sx * (y if swap else x), sy * (x if swap else y))
            for x, y in complete.rooms
        }
        min_x = min(x for x, _ in transformed.values())
        min_y = min(y for _, y in transformed.values())
        normalized = {key: (x - min_x, y - min_y) for key, (x, y) in transformed.items()}
        connections = [(min(normalized[a], normalized[b]), max(normalized[a], normalized[b]))
                       for a, b in complete.connections]
        signatures.append((tuple(sorted(normalized.values())), tuple(sorted(connections))))
    return min(signatures)


def registration_error(value, path, has_positions):
    if value is None:
        require(not has_positions, f"{path} is required for annotated positions")
        return 0.0
    reg = fields(value, path, "origin_px", "px_per_unit", "residual_px", "anchor_count")
    point(reg["origin_px"], f"{path}.origin_px", pixels=True)
    scale = number(reg["px_per_unit"], f"{path}.px_per_unit")
    require(scale > 0, f"{path}.px_per_unit must be positive")
    require(type(reg["anchor_count"]) is int and reg["anchor_count"] >= 2,
            f"{path} needs at least two visible anchors")
    error = nonnegative(reg["residual_px"], f"{path}.residual_px") / scale
    require(math.isfinite(error) and error <= 1_000_000, f"{path} has an invalid converted residual")
    return error


def parse_frame(value):
    row = fields(value, "frame", "layout_id", "observation_id", "stage", "frame", "registration", "observation")
    layout_id = nonempty(row["layout_id"], "frame.layout_id")
    observation_id = nonempty(row["observation_id"], "frame.observation_id")
    timestamp = nonempty(row["frame"], f"{observation_id}.frame")
    stage = row["stage"]
    require(type(stage) is int and 0 <= stage <= 3, f"{observation_id}.stage must be 0–3")
    obs = fields(row["observation"], observation_id, "entrance_orientation", "player_position",
                 "player_error", "visible_rooms", "visible_connections", "unexplored_branches",
                 "dead_ends", "uncertain_geometry")
    orientation = obs["entrance_orientation"]
    require(orientation is None or orientation in ORIENTATIONS, f"{observation_id} has an invalid orientation")
    player = obs["player_position"]
    if player is not None:
        player = point(player, f"{observation_id}.player_position")
    error = nonnegative(obs["player_error"], f"{observation_id}.player_error")
    require(player is not None or error == 0, f"{observation_id} has error for an unknown position")
    visible = geometry(obs["visible_rooms"], obs["visible_connections"], observation_id)
    residual = registration_error(row["registration"], f"{observation_id}.registration",
                                  player is not None or bool(visible.rooms))
    if player is not None:
        error += residual
    branches = []
    for branch in rows(obs["unexplored_branches"], f"{observation_id}.unexplored_branches"):
        require(isinstance(branch, list) and len(branch) == 2, f"{observation_id} has an invalid branch")
        room, direction = point(branch[0], f"{observation_id} branch"), branch[1]
        require(room in visible.rooms and direction in SECTORS, f"{observation_id} has an invalid branch")
        branches.append((room, direction))
    require(len(set(branches)) == len(branches), f"{observation_id} contains duplicate branches")
    dead_ends = [point(room, f"{observation_id} dead end")
                 for room in rows(obs["dead_ends"], f"{observation_id}.dead_ends")]
    require(len(set(dead_ends)) == len(dead_ends), f"{observation_id} contains duplicate dead ends")
    for room in dead_ends:
        departures = sum(room in link for link in visible.connections) + sum(room == a for a, _ in branches)
        require(room in visible.rooms and departures == 1, f"{observation_id} has a conflicting dead end")
    uncertain = obs["uncertain_geometry"]
    require(type(uncertain) is bool, f"{observation_id}.uncertain_geometry must be boolean")
    observation = Observation(orientation, player, error, visible, tuple(sorted(branches)), tuple(sorted(dead_ends)))
    return Frame(layout_id, observation_id, stage, uncertain, observation), timestamp


def read_metadata(value):
    meta = fields(value, "metadata", "schema_version", "dataset_id", "kind", "scenario", "capture", "layouts")
    require(type(meta["schema_version"]) is int and meta["schema_version"] == 1, "unsupported schema_version")
    nonempty(meta["dataset_id"], "dataset_id")
    require(meta["kind"] in ("synthetic", "real"), "kind must be synthetic or real")
    require(meta["scenario"] == SCENARIO, "unsupported scenario")
    capture = fields(meta["capture"], "capture", "build", "mode", "automap_mode", "graphics", "resolution", "zoom")
    for key in ("build", "mode", "automap_mode", "graphics", "zoom"):
        nonempty(capture[key], f"capture.{key}")
    require(all(v > 0 for v in point(capture["resolution"], "capture.resolution")), "invalid capture.resolution")
    groups = set()
    splits = {}
    for value in rows(meta["layouts"], "layouts"):
        row = fields(value, "layout", "layout_id", "group_id", "split", "recording")
        layout_id = nonempty(row["layout_id"], "layout_id")
        group_id = nonempty(row["group_id"], f"{layout_id}.group_id")
        nonempty(row["recording"], f"{layout_id}.recording")
        require(row["split"] in ("development", "evaluation"), f"{layout_id} has an invalid split")
        require(layout_id not in splits, f"duplicate layout ID {layout_id}")
        require(group_id not in groups, f"dataset leakage or repeated visit: group {group_id} reused")
        groups.add(group_id)
        splits[layout_id] = row["split"]
    require(set(splits.values()) == {"development", "evaluation"}, "both dataset splits are required")
    return meta, splits


def read_frames(values, splits):
    by_layout = {layout: [] for layout in splits}
    ids = set()
    captures = set()
    for value in rows(values, "observations"):
        frame, timestamp = parse_frame(value)
        require(frame.layout_id in splits, f"unknown layout {frame.layout_id}")
        require(frame.observation_id not in ids, f"duplicate observation ID {frame.observation_id}")
        capture = frame.layout_id, timestamp
        require(capture not in captures, f"duplicate frame {timestamp} for {frame.layout_id}")
        ids.add(frame.observation_id)
        captures.add(capture)
        by_layout[frame.layout_id].append(frame)
    for layout, frames in by_layout.items():
        frames.sort(key=lambda frame: frame.stage)
        require(bool(frames) and [f.stage for f in frames] == list(range(len(frames))),
                f"{layout} needs consecutive unique stages beginning at 0")
        possible = set(SECTORS)
        for frame in frames:
            direction = frame.observation.orientation
            if direction is not None:
                possible &= AXES.get(direction, {direction})
        require(bool(possible), f"{layout} has conflicting entrance orientations")
    return by_layout


def read_truth(values, by_layout):
    known_signatures = {}
    targets, visibility = {}, {}
    for value in rows(values, "truth"):
        row = fields(value, "truth row", "layout_id", "complete_geometry", "targets", "visibility")
        layout = nonempty(row["layout_id"], "truth.layout_id")
        require(layout in by_layout and layout not in targets, f"unknown or duplicate truth layout {layout}")
        complete = fields(row["complete_geometry"], f"{layout}.complete_geometry", "rooms", "connections")
        complete = geometry(complete["rooms"], complete["connections"], f"{layout}.complete_geometry")
        require(bool(complete.rooms), f"{layout} needs complete geometry for layout isolation")
        signature = layout_signature(complete)
        require(signature not in known_signatures,
                f"dataset leakage or repeated visit: equivalent geometry for {layout} and {known_signatures.get(signature)}")
        known_signatures[signature] = layout
        targets[layout] = {}
        labels = fields(row["targets"], f"{layout}.targets", *TARGETS)
        for target, label in labels.items():
            if label is not None:
                label = fields(label, f"{layout}.{target}", "position", "error")
                label = Target(point(label["position"], f"{layout}.{target}.position"),
                               nonnegative(label["error"], f"{layout}.{target}.error"))
            targets[layout][target] = label
        frames = by_layout[layout]
        labels_by_frame = fields(row["visibility"], f"{layout}.visibility", *(f.observation_id for f in frames))
        discovered = set()
        for frame in frames:
            key = frame.observation_id
            states = fields(labels_by_frame[key], f"{key}.visibility", *TARGETS)
            for target, state in states.items():
                require(state in ("hidden", "visible", "uncertain"), f"{key} has an invalid visibility")
                require(target not in discovered or state == "visible", f"{key} forgets discovered {target}")
                if state == "visible":
                    discovered.add(target)
            visibility[key] = states
    require(targets.keys() == by_layout.keys(), "each layout needs a truth record")
    return targets, visibility


def unique_keys(pairs):
    obj = dict(pairs)
    require(len(obj) == len(pairs), "duplicate JSON object key")
    return obj


def load_dataset(directory: Path) -> Dataset:
    texts = {name: (directory / name).read_bytes() for name in FILES}
    metadata, observation_rows, truth_rows = (
        json.loads(texts[name].decode("utf-8-sig"), object_pairs_hook=unique_keys) for name in FILES
    )
    meta, splits = read_metadata(metadata)
    by_layout = read_frames(observation_rows, splits)
    targets, visibility = read_truth(truth_rows, by_layout)
    frames = tuple(frame for layout in sorted(by_layout) for frame in by_layout[layout])
    return Dataset(meta["dataset_id"], meta["kind"], meta["capture"], splits, frames, targets, visibility,
                   {name: sha256(content).hexdigest() for name, content in texts.items()})
