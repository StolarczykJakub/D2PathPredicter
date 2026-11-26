"""Geometry-only descriptors for the frozen, fixed-zoom PoC."""

from dataclasses import dataclass
from itertools import combinations
from math import dist
from statistics import mean

from research.annotation_retest.evaluate import offset, raster
from research.geometry_experiment.blind_packets import MASKS, RESOLUTION


POSITION_CAP = 8
WALL_RADIUS = 120
WALL_TOLERANCE = 3
WALL_MIN_COVERAGE = 0.75
WALL_NEIGHBORS = tuple(sorted(
    ((dx, dy) for dx in range(-WALL_TOLERANCE, WALL_TOLERANCE + 1)
     for dy in range(-WALL_TOLERANCE, WALL_TOLERANCE + 1)
     if dx * dx + dy * dy <= WALL_TOLERANCE ** 2),
    key=lambda p: (p[0] ** 2 + p[1] ** 2, p),
))


def hue(description):
    text = description.lower()
    if "yellow" in text:
        return "yellow"
    if "purple" in text or "magenta" in text:
        return "purple"
    return "unknown"


def compatible_hue(a, b):
    return a == b or "unknown" in (a, b)


@dataclass(frozen=True, order=True, slots=True)
class Marker:
    point: tuple
    hue: str
    radius: float


@dataclass(frozen=True, slots=True)
class Markers:
    points: tuple[Marker, ...]
    player_radius: float

    def select(self, indices):
        return Markers(tuple(self.points[i] for i in indices), self.player_radius)


@dataclass(frozen=True, slots=True)
class Constellation:
    markers: Markers
    vectors: tuple


@dataclass(frozen=True, slots=True)
class Crop:
    axis: int
    high: bool
    edge: float

    def contains(self, point):
        return point[self.axis] >= self.edge if self.high else point[self.axis] <= self.edge


def player_markers(marks, player):
    points = (Marker(tuple(offset(mark["center_px"], player["px"])),
                     hue(mark["appearance"]), mark["error_px"])
              for mark in marks if mark["status"] == "OBSERVED")
    return Markers(tuple(sorted(points)), player["error_px"])


def constellation(markers):
    # Signed dx/dy is the lossless Cartesian encoding of length and native bearing.
    vectors = tuple(tuple(tuple(offset(b.point, a.point)) for b in markers.points)
                    for a in markers.points)
    return Constellation(markers, vectors)


def normalized_error(delta, radius):
    limit = min(POSITION_CAP, radius)
    if delta > limit:
        return None
    return delta / limit if limit else 0.0


def resolved_triangle(points):
    a, b, c = (p.point for p in points)
    dx, dy = offset(b, a)
    ex, ey = offset(c, a)
    longest = max(dist(a, b), dist(a, c), dist(b, c))
    return bool(longest and abs(dx * ey - dy * ex) > longest * sum(p.radius for p in points))


def match(query, reference):
    """Enumerate all compatible one-to-one correspondences of the smaller set."""
    shifted = isinstance(query, Constellation)
    left, right = (query.markers, reference.markers) if shifted else (query, reference)
    reverse = len(left.points) > len(right.points)
    if reverse:
        left, right = right, left
        query, reference = reference, query
    if len(left.points) < 2:
        return ()

    player_radius = left.player_radius + right.player_radius
    choices = []
    for a in left.points:
        candidates = []
        for j, b in enumerate(right.points):
            if not compatible_hue(a.hue, b.hue):
                continue
            error = 0.0 if shifted else normalized_error(
                dist(a.point, b.point), a.radius + b.radius + player_radius)
            if error is not None:
                candidates.append((j, error))
        if not candidates:
            return ()
        choices.append(candidates)

    correspondences = []

    def visit(indices, used, errors):
        i = len(indices)
        if i == len(choices):
            pairs = tuple(enumerate(indices))
            displacement = (0, 0)
            alignment_2d = False
            if shifted:
                displacement = tuple(map(mean, zip(*(
                    offset(right.points[k].point, left.points[h].point) for h, k in pairs))))
                alignment_2d = any(
                    resolved_triangle([left.points[h] for h, _ in triple]) and
                    resolved_triangle([right.points[k] for _, k in triple])
                    for triple in combinations(pairs, 3))
            if reverse:
                pairs = tuple(sorted((k, h) for h, k in pairs))
                displacement = tuple(-x for x in displacement)
            correspondences.append({
                "pairs": pairs, "score": mean(errors),
                "offset_px": displacement, "alignment_2d": alignment_2d,
            })
            return

        for j, error in choices[i]:
            bit = 1 << j
            if used & bit:
                continue
            new_errors = () if shifted else (error,)
            if shifted:
                for previous_i, previous_j in enumerate(indices):
                    radius = (left.points[i].radius + left.points[previous_i].radius +
                              right.points[j].radius + right.points[previous_j].radius)
                    vector_error = normalized_error(
                        dist(query.vectors[previous_i][i], reference.vectors[previous_j][j]),
                        radius)
                    if vector_error is None:
                        break
                    new_errors += (vector_error,)
                else:
                    visit(indices + (j,), used | bit, errors + new_errors)
                continue
            visit(indices + (j,), used | bit, errors + new_errors)

    visit((), 0, ())
    return tuple(sorted(correspondences, key=lambda item: (item["score"], item["pairs"])))


def wall_union(segments, origin=(0, 0), bounded=True):
    points = set()
    for a, b in segments:
        points.update(raster((offset(a, origin), offset(b, origin))))
    if bounded:
        return frozenset(p for p in points if p[0] ** 2 + p[1] ** 2 <= WALL_RADIUS ** 2)
    return frozenset(points)


def visible(point, origin):
    x, y = (p + o for p, o in zip(point, origin))
    width, height = RESOLUTION
    return (0 <= x < width and 0 <= y < height and not
            any(left <= x < left + w and top <= y < top + h for left, top, w, h in MASKS))


def wall_coverage(query, reference, origins, crop=None, full_sample=False):
    def keep(p):
        return ((crop is None or crop.contains(p)) and
                (full_sample or all(visible(p, origin) for origin in origins)))

    a, b = ({p for p in side if keep(p)} for side in (query, reference))
    covered = None
    if a and b:
        covered = tuple(
            sum(any((x + dx, y + dy) in target for dx, dy in WALL_NEIGHBORS) for x, y in source)
            / len(source) for source, target in ((a, b), (b, a)))
    return {"samples": (len(a), len(b)), "fractions": covered,
            "supports": covered is not None and min(covered) >= WALL_MIN_COVERAGE}


def wall_shortlist(candidates, support):
    supported = tuple(i for i in candidates if support[i])
    return supported if len(candidates) > 1 and supported else candidates
