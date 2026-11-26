"""Reproduce the Phase 1.6.1 annotation audit from the private local inputs."""

from collections import Counter
from functools import cache
from hashlib import sha256
import json
from math import ceil, dist, isclose, isfinite
from pathlib import Path
from statistics import mean, median, quantiles
from zipfile import ZipFile


BASE = Path("local-data/phase-1-6-1")
SOURCE = Path("docs/annotation_analysis")
PACKETS = ("h9v2c", "k4m7q", "p6r8t", "w3j5n")
POINT_STATUSES = {"OBSERVED", "UNKNOWN", "AMBIGUOUS"}
WALL_STATUSES = {"CONTINUOUS", "INTERRUPTED", "AMBIGUOUS"}
SECTORS = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"}


def require(condition, field):
    if not condition:
        raise ValueError(field)


def read_json(data):
    def object_with_unique_keys(pairs):
        value = dict(pairs)
        require(len(value) == len(pairs), "duplicate JSON key")
        return value

    def reject_constant(value):
        raise ValueError(f"nonfinite JSON number: {value}")

    return json.loads(data, object_pairs_hook=object_with_unique_keys,
                      parse_constant=reject_constant)


def shape(value, fields):
    require(isinstance(value, dict) and value.keys() == set(fields.split()), fields)


def radius(value):
    require(type(value) in (int, float) and isfinite(value) and value >= 0, "radius")


def point(value):
    require(isinstance(value, list) and len(value) == 2 and
            all(type(x) in (int, float) and isfinite(x) and 0 <= x < bound
                for x, bound in zip(value, (1920, 1080))), f"point {value}")


def segment(value):
    require(isinstance(value, list) and len(value) == 2 and value[0] != value[1],
            f"segment {value}")
    for endpoint in value:
        point(endpoint)


def note(value):
    require(isinstance(value, str) and value.strip(), "empty evidence note")


def point_mark(value):
    shape(value, "status px error_px note")
    require(value["status"] in POINT_STATUSES, "point status")
    note(value["note"])
    if value["status"] == "OBSERVED":
        point(value["px"])
        radius(value["error_px"])
    else:
        require(value["px"] is None and value["error_px"] is None, "unresolved point")


def indexed(rows, fields):
    require(isinstance(rows, list), fields)
    result = {}
    for row in rows:
        shape(row, fields)
        require(isinstance(row["id"], str) and row["id"].strip() and
                row["id"] not in result, "nonunique or invalid ID")
        note(row["note"])
        result[row["id"]] = row
    return result


def validate(row, template, task):
    require(row.keys() == template.keys(), "top-level schema")
    for k in ("packet_id", "frame_sha256", "resolution", "protocol_version"):
        require(row[k] == template[k], k)
    require(type(row["protocol_version"]) is int and
            all(type(dimension) is int for dimension in row["resolution"]), "numeric metadata")
    point_mark(row["player"])
    shape(row["search_complete"], "walls markers")
    require(all(type(flag) is bool for flag in row["search_complete"].values()), "search flags")
    require(type(row["time_limit_reached"]) is bool, "time-limit flag")
    duration = row["elapsed_minutes"]
    require(type(duration) in (int, float) and isfinite(duration) and 0 <= duration <= 8,
            "elapsed minutes")
    require(isinstance(row["notes"], list), "notes")
    for value in row["notes"]:
        note(value)

    wall_fields = "id segment_px error_px status note"
    walls = indexed(row["walls"], wall_fields + (" room_id" if task == "semantic" else ""))
    require(len(walls) <= 8, "wall sample cap")
    for wall in walls.values():
        segment(wall["segment_px"])
        radius(wall["error_px"])
        require(wall["status"] in WALL_STATUSES, "wall status")
    markers = indexed(row["markers"], "id status appearance center_px segment_px error_px note")
    for mark in markers.values():
        require(mark["status"] in POINT_STATUSES, "marker status")
        note(mark["appearance"])
        if mark["status"] == "OBSERVED":
            point(mark["center_px"])
            radius(mark["error_px"])
        else:
            require(mark["center_px"] is None and mark["segment_px"] is None and
                    mark["error_px"] is None, "unresolved marker")
        if mark["segment_px"] is not None:
            segment(mark["segment_px"])
            radius(mark["error_px"])
    if task == "raw":
        return

    shape(row["entrance"], "staircase_scene automap_glyph arrival_room_center player_arrival")
    for value in row["entrance"].values():
        point_mark(value)
    orientation = row["orientation"]
    shape(orientation, "status direction segment_px error_px note")
    note(orientation["note"])
    require(orientation["status"] in POINT_STATUSES, "orientation status")
    require(orientation["direction"] in SECTORS | {"NS", "NE_SW", "EW", "NW_SE", None},
            "orientation direction")
    if orientation["segment_px"] is None:
        require(orientation["direction"] is None and orientation["error_px"] is None,
                "orientation without evidence")
    else:
        segment(orientation["segment_px"])
        radius(orientation["error_px"])
    if orientation["status"] != "OBSERVED":
        require(orientation["direction"] is None, "unresolved orientation direction")

    regions = indexed(row["regions"], "id class center perimeter note")
    for region in regions.values():
        require(region["class"] in {"ROOM", "ENCLOSED_FEATURE", "UNRESOLVED"}, "region class")
        require(region["perimeter"] in {"COMPLETE", "INCOMPLETE", "UNKNOWN", "AMBIGUOUS"},
                "region perimeter")
        point_mark(region["center"])
    rooms = {key for key, region in regions.items() if region["class"] == "ROOM"}
    for wall in walls.values():
        require(wall["room_id"] is None or wall["room_id"] in rooms, "wall room")
    opening_fields = ("id marker_id room_id segment_px error_px geometry passage "
                      "destination_room_id frontier_direction note")
    openings = indexed(row["openings"], opening_fields)
    for opening in openings.values():
        for field, references in (("marker_id", markers), ("room_id", rooms),
                                  ("destination_room_id", rooms)):
            require(opening[field] is None or opening[field] in references, field)
        if opening["segment_px"] is None:
            require(opening["error_px"] is None, "opening radius without segment")
        else:
            segment(opening["segment_px"])
            radius(opening["error_px"])
        require(opening["geometry"] in {"OPEN_GAP", "WALL_AT_MARK", "UNKNOWN", "AMBIGUOUS"},
                "opening geometry")
        require(opening["passage"] in {"CONFIRMED", "UNKNOWN", "AMBIGUOUS"}, "passage status")
        frontier = opening["frontier_direction"]
        require(frontier is None or (frontier in SECTORS and opening["passage"] == "CONFIRMED"
                                    and opening["destination_room_id"] is None), "frontier")
    require(isinstance(row["connections"], list), "connections")
    edges = set()
    for link in row["connections"]:
        shape(link, "rooms opening_id")
        pair = frozenset(link["rooms"])
        require(isinstance(link["rooms"], list) and len(link["rooms"]) == len(pair) == 2 and
                pair <= rooms and pair not in edges, "connection rooms")
        opening = openings.get(link["opening_id"])
        require(opening is not None and opening["passage"] == "CONFIRMED", "connection opening")
        require({opening["room_id"], opening["destination_room_id"]} - {None} <= pair,
                "connection opening rooms")
        edges.add(pair)
    require(isinstance(row["terminal_assessments"], list), "terminal assessments")
    assessed = set()
    for terminal in row["terminal_assessments"]:
        shape(terminal, "room_id status departure_opening_ids note")
        room = terminal["room_id"]
        require(room in rooms and room not in assessed, "terminal room")
        assessed.add(room)
        note(terminal["note"])
        status = terminal["status"]
        require(status in {"TERMINAL", "ONE_DEPARTURE_ONLY", "NON_TERMINAL",
                           "INCOMPLETE", "UNKNOWN", "AMBIGUOUS"}, "terminal status")
        departures = terminal["departure_opening_ids"]
        require(isinstance(departures, list) and len(departures) == len(set(departures)),
                "departure list")
        require(all(key in openings and openings[key]["passage"] == "CONFIRMED" and
                    room in (openings[key]["room_id"], openings[key]["destination_room_id"])
                    for key in departures), "departure reference")
        require(status not in {"TERMINAL", "ONE_DEPARTURE_ONLY"} or len(departures) == 1,
                "single departure required")
        require(status != "NON_TERMINAL" or len(departures) >= 2, "multiple departures required")
        require(status != "INCOMPLETE" or not departures, "incomplete departure count")
        require(status != "TERMINAL" or regions[room]["perimeter"] == "COMPLETE",
                "terminal perimeter")


def intake():
    manifest = read_json((BASE / "owner/manifest.json").read_bytes())
    rows, entries = {}, []
    for index, packet in enumerate(PACKETS):
        assignment = next(item for item in manifest["assignments"] if item["packet_id"] == packet)
        archive = BASE / "release" / assignment["filename"]
        require(sha256(archive.read_bytes()).hexdigest() == assignment["archive_sha256"], packet)
        for task in ("raw", "semantic"):
            suffix = f" ({index})" if index else ""
            source = SOURCE / f"{task}{suffix}.json"
            original = source.read_bytes()
            destination = BASE / "returns" / packet / f"{task}.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                with destination.open("xb") as output:
                    output.write(original)
            require(destination.read_bytes() == original, f"frozen return mismatch: {destination}")
            row = read_json(original)
            with ZipFile(archive) as release:
                template = read_json(release.read(f"{task}.json"))
                require(sha256(release.read("frame.png")).hexdigest() == row["frame_sha256"] ==
                        assignment["frame_sha256"], "frame digest")
            try:
                validate(row, template, task)
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"{source}: {error}") from error
            rows[packet, task] = row
            entries.append({
                "packet_id": packet, "pass": task, "source": source.as_posix(),
                "original": destination.as_posix(), "sha256": sha256(original).hexdigest(),
                "byte_count": len(original), "validation": "PASS",
                "assigned_order": assignment["pass_order"],
                "reported_order": ["raw", "semantic"] if packet in {"k4m7q", "p6r8t"} else None,
                "reviewer_id": None, "released_at": None, "received_at": None,
                "external_exposure": None,
            })
    return rows, entries


def endpoint_errors(left, right):
    choices = [tuple(dist(a, b) for a, b in zip(left, ordered))
               for ordered in (right, right[::-1])]
    return min(choices, key=lambda pair: (max(pair), sum(pair)))


def assignment(left, right, cost, limit):
    """Maximize count, then minimize cost. A tie retains two witness assignments."""
    candidates = [tuple((j, delta) for j, b in enumerate(right)
                        if (delta := cost(a, b)) <= limit) for a in left]

    @cache
    def solve(i, used):
        if i == len(left):
            return 0, 0.0, ((),)
        count, total, paths = solve(i + 1, used)
        for j, delta in candidates[i]:
            bit = 1 << j
            if used & bit:
                continue
            tail_count, tail_total, tail_paths = solve(i + 1, used | bit)
            trial_count, trial_total = 1 + tail_count, delta + tail_total
            trial_paths = tuple(((i, j),) + path for path in tail_paths)
            same_cost = isclose(total, trial_total, rel_tol=0, abs_tol=1e-9)
            if trial_count > count or (trial_count == count and trial_total < total and not same_cost):
                count, total, paths = trial_count, trial_total, trial_paths
            elif trial_count == count and same_cost:
                paths = (paths + trial_paths)[:2]
        return count, total, paths

    _, _, paths = solve(0, 0)
    return paths[0], [[(left[i]["id"], right[j]["id"]) for i, j in p] for p in paths[1:]]


def offset(point_px, player_px):
    return [x - origin for x, origin in zip(point_px, player_px)]


def assess(left, right, kind, limit):
    a, b = left[kind], right[kind]
    players = (left["player"], right["player"])
    have_players = all(mark["status"] == "OBSERVED" for mark in players)
    player_points = [mark["px"] for mark in players] if have_players else None
    player_radius = sum(mark["error_px"] for mark in players) if have_players else None
    if kind == "walls":
        cost = lambda x, y: max(endpoint_errors(x["segment_px"], y["segment_px"]))
    elif kind == "markers":
        cost = lambda x, y: point_distance(x["center_px"], y["center_px"])
    else:
        cost = lambda x, y: point_distance(x["center"]["px"], y["center"]["px"])
    pairs, alternatives = assignment(a, b, cost, limit)
    matched_left, matched_right = set(), set()
    results = []
    for i, j in pairs:
        x, y = a[i], b[j]
        matched_left.add(i)
        matched_right.add(j)
        record = {"left": x["id"], "right": y["id"], "distance_px": cost(x, y)}
        if kind == "regions":
            radii = x["center"]["error_px"] + y["center"]["error_px"]
            record.update(classes=[x["class"], y["class"]], summed_radius_px=radii,
                          in_radius=record["distance_px"] <= radii)
            if have_players:
                relative = [offset(p, player) for p, player in
                            zip((x["center"]["px"], y["center"]["px"]), player_points)]
                record.update(relative_centres=relative, relative_error_px=dist(*relative),
                              relative_radius_px=radii + player_radius)
        else:
            radii = x["error_px"] + y["error_px"]
            record.update(summed_radius_px=radii, dispositions=[x["status"], y["status"]])
            x_span, y_span = x["segment_px"], y["segment_px"]
            if x_span is not None and y_span is not None:
                ends = endpoint_errors(x_span, y_span)
                span_delta = abs(dist(*x_span) - dist(*y_span))
                record.update(endpoint_errors_px=ends, span_delta_px=span_delta)
                if have_players:
                    relative = [[offset(p, player) for p in mark]
                                for mark, player in zip((x_span, y_span), player_points)]
                    record.update(relative_segments=relative,
                                  relative_endpoint_errors_px=endpoint_errors(*relative),
                                  relative_radius_px=radii + player_radius)
            if kind == "walls":
                record.update(reproducible=max(ends) <= min(12, radii),
                              room_ids=[x.get("room_id"), y.get("room_id")])
            else:
                center_pass = record["distance_px"] <= min(8, radii)
                extent_pass = None if x_span is None or y_span is None else (
                    max(ends) <= min(8, radii) and span_delta <= min(8, 2 * radii))
                record.update(appearances=[x["appearance"], y["appearance"]],
                              center_pass=center_pass, extent_pass=extent_pass,
                              both_pass=center_pass and extent_pass is True)
                if have_players:
                    relative = [offset(mark["center_px"], player)
                                for mark, player in zip((x, y), player_points)]
                    record.update(relative_centres=relative, relative_center_error_px=dist(*relative),
                                  relative_radius_px=radii + player_radius)
        results.append(record)
    return {"left_count": len(a), "right_count": len(b),
            "symmetric_agreement": 2 * len(pairs) / (len(a) + len(b)) if a or b else None,
            "pairs": results, "tied_alternative": alternatives,
            "unmatched_left": [m["id"] for i, m in enumerate(a) if i not in matched_left],
            "unmatched_right": [m["id"] for j, m in enumerate(b) if j not in matched_right]}


def point_distance(left, right):
    return dist(left, right) if left is not None and right is not None else float("inf")


def raster(segment_px):
    a, b = segment_px
    steps = ceil(max(abs(b[0] - a[0]), abs(b[1] - a[1])))
    return {(round(a[0] + (b[0] - a[0]) * i / steps),
             round(a[1] + (b[1] - a[1]) * i / steps)) for i in range(steps + 1)}


def wall_union(left, right):
    parts = [[(w["id"], raster(w["segment_px"])) for w in row["walls"]] for row in (left, right)]
    unions = [set().union(*(pixels for _, pixels in side)) for side in parts]
    directed = []
    for row, source, target, traces in zip((left, right), unions, reversed(unions), parts):
        midpoint_distances = {}
        for wall in row["walls"]:
            a, b = wall["segment_px"]
            midpoint = [(x + y) / 2 for x, y in zip(a, b)]
            midpoint_distances[wall["id"]] = dist(midpoint, (960, 540))
        direction = {
            "pixels": len(source),
            "midpoint_ranks": sorted(midpoint_distances.items(), key=lambda item: item[1]),
        }
        directed.append(direction)
        if not source or not target:
            continue
        distances = {p: min(dist(p, q) for q in target) for p in source}
        direction.update({
            "coverage_within_3px": mean(delta <= 3 for delta in distances.values()),
            "mean_nearest_px": mean(distances.values()),
            "p95_nearest_px": (quantiles(distances.values(), n=20, method="inclusive")[-1]
                               if len(distances) > 1 else next(iter(distances.values()))),
            "per_trace_coverage_within_3px": {
                key: mean(distances[p] <= 3 for p in pixels) for key, pixels in traces},
        })
    united = unions[0] | unions[1]
    return {"exact_iou": len(unions[0] & unions[1]) / len(united) if united else None,
            "directed": directed, "symmetric_chamfer_px": (
                mean(d["mean_nearest_px"] for d in directed) if all(unions) else None)}


def compare(left, right):
    players = [row["player"] for row in (left, right)]
    player_distance = point_distance(*(mark["px"] for mark in players))
    result = {"players": players,
              "player_distance_px": player_distance if isfinite(player_distance) else None,
              "markers": assess(left, right, "markers", 12), "walls": assess(left, right, "walls", 15)}
    if "regions" in left:
        result["regions"] = assess(left, right, "regions", 20)
        result["entrance"] = {}
        for field, left_mark in left["entrance"].items():
            marks = [left_mark, right["entrance"][field]]
            distance = point_distance(*(m["px"] for m in marks))
            result["entrance"][field] = {"marks": marks,
                                         "distance_px": distance if isfinite(distance) else None}
        result["orientation"] = [left["orientation"], right["orientation"]]
    else:
        result["exploratory_10px"] = {kind: assess(left, right, kind, 10) for kind in ("walls", "markers")}
        result["wall_union"] = wall_union(left, right)
    return result


def main():
    rows, entries = intake()
    result = {"comparisons": {}, "returns": {}, "within_packet": {}}
    for frame, packets in (("A", PACKETS[:2]), ("B", PACKETS[2:])):
        result["comparisons"][frame] = {
            task: compare(*(rows[packet, task] for packet in packets)) for task in ("raw", "semantic")}
    for (packet, task), row in rows.items():
        result["returns"].setdefault(packet, {})[task] = {
            k: row[k] for k in ("elapsed_minutes", "time_limit_reached", "search_complete")}
        if task == "semantic":
            result["returns"][packet][task].update(
                region_classes=Counter(r["class"] for r in row["regions"]),
                region_perimeters=Counter(r["perimeter"] for r in row["regions"]),
                opening_geometry=Counter(r["geometry"] for r in row["openings"]),
                passage=Counter(r["passage"] for r in row["openings"]),
                connections=row["connections"],
                terminal_assessments=row["terminal_assessments"])
    for packet in PACKETS:
        raw, semantic = (rows[packet, task] for task in ("raw", "semantic"))
        result["within_packet"][packet] = {
            "walls": assess(raw, semantic, "walls", 15),
            "markers": assess(raw, semantic, "markers", 12)}
    result["median_minutes"] = {
        task: median(rows[packet, task]["elapsed_minutes"] for packet in PACKETS)
        for task in ("raw", "semantic")}
    output = BASE / "owner/derived"
    output.mkdir(parents=True, exist_ok=True)
    for name, value in (("intake.json", entries), ("agreement.json", result)):
        (output / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
    print(f"{len(entries)} byte-identical returns validated. Calculations saved to {output}.")


if __name__ == "__main__":
    main()
