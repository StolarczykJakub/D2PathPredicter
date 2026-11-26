"""Experimental translation-only matching between partially visible constellations."""

from dataclasses import dataclass
from itertools import combinations
from math import dist
from statistics import mean

from research.marker_fingerprint.bounded_match import LIMITS, PairResult, QueryResult, error
from research.marker_fingerprint.match import compatible_hue, constellation, offset, resolved_triangle


CAP = 6
MIN_MATCHED = 3
MIN_BASELINE = 24
MIN_SPAN = 0.25
BUDGET_STOPS = frozenset(("markers", "references", "pair_prefixes", "pair_hypotheses", "query_prefixes"))


def required_count(query_count, reference_count):
    return max(MIN_MATCHED, (2 * max(query_count, reference_count) + 2) // 3)


def box_area(markers):
    x, y = zip(*(marker.point for marker in markers))
    return (max(x) - min(x)) * (max(y) - min(y))


def span_fraction(matched, visible_area):
    return box_area(matched) / visible_area if visible_area else None


def reliable_triangle(triangle):
    return (max(dist(a.point, b.point) for a, b in combinations(triangle, 2)) >= MIN_BASELINE
            and resolved_triangle(triangle))


def alignment_supported(left, right, span):
    return (all(value is not None and value >= MIN_SPAN for value in span)
            and any(reliable_triangle(a) and reliable_triangle(b)
                    for a, b in zip(combinations(left, 3), combinations(right, 3))))


@dataclass(frozen=True, slots=True)
class PartialHypothesis:
    pairs: tuple
    score: float
    offset_px: tuple
    alignment_2d: bool
    matched_fraction: tuple
    span_fraction: tuple
    max_translation_residual_px: float


def bit_indices(bits):
    while bits:
        bit = bits & -bits
        yield bit.bit_length() - 1
        bits ^= bit


def enumerate_pair(query, reference, q_vectors, limits, remaining):
    left, right = query.points, reference.points
    minimum = required_count(len(left), len(right))
    result = PairResult()
    if minimum > min(len(left), len(right)):
        return result

    r_vectors = constellation(reference).vectors
    vertices = [(i, j) for i, a in enumerate(left) for j, b in enumerate(right)
                if compatible_hue(a.hue, b.hue)]
    adjacent = [0] * len(vertices)

    def vector_error(a, b):
        i, j = a
        k, l = b
        radii = left[i].radius + left[k].radius + right[j].radius + right[l].radius
        return error(dist(q_vectors[i][k], r_vectors[j][l]), radii, CAP)

    for v, (i, j) in enumerate(vertices):
        for w in range(v):
            k, l = vertices[w]
            if i == k or j == l:
                continue
            result.checks += 1
            if vector_error((i, j), (k, l)) is not None:
                adjacent[v] |= 1 << w
                adjacent[w] |= 1 << v

    areas = box_area(left), box_area(right)
    found = []

    def retain(indices):
        result.hypotheses_seen += 1
        if len(found) == limits.pair_hypotheses:
            result.stop = "pair_hypotheses"
            return
        pairs = tuple(sorted(vertices[v] for v in indices))
        q_matched = tuple(left[i] for i, _ in pairs)
        r_matched = tuple(right[j] for _, j in pairs)
        shifts = [offset(b.point, a.point) for a, b in zip(q_matched, r_matched)]
        translation = tuple(map(mean, zip(*shifts)))
        span = tuple(span_fraction(points, area) for points, area in zip((q_matched, r_matched), areas))
        found.append(PartialHypothesis(
            pairs, mean(vector_error(a, b) for a, b in combinations(pairs, 2)), translation,
            alignment_supported(q_matched, r_matched, span),
            (len(pairs) / len(left), len(pairs) / len(right)), span,
            max(dist(shift, translation) for shift in shifts),
        ))

    def visit(indices, possible, excluded):
        # Bron–Kerbosch enumerates inclusion-maximal assignments, including ties and smaller alternatives.
        if result.prefixes == remaining:
            result.stop = "query_prefixes"
            return
        if result.prefixes == limits.pair_prefixes:
            result.stop = "pair_prefixes"
            return
        result.prefixes += 1
        if len(indices) + possible.bit_count() < minimum:
            return
        if not (possible | excluded):
            retain(indices)
            return
        pivot = max(bit_indices(possible | excluded), key=lambda v: (possible & adjacent[v]).bit_count())
        for v in bit_indices(possible & ~adjacent[pivot]):
            visit(indices + (v,), possible & adjacent[v], excluded & adjacent[v])
            if result.stop:
                return
            possible ^= 1 << v
            excluded |= 1 << v

    visit((), (1 << len(vertices)) - 1, 0)
    result.hypotheses = tuple(sorted(found, key=lambda hypothesis: hypothesis.pairs))
    return result


def match_query(query, references, *, limits=LIMITS):
    """Return candidate evidence using only marker centres, hue and uncertainty."""
    if len(references) > limits.references:
        return QueryResult(stop="references")
    if any(view is not None and len(view.points) > limits.markers for view in (query, *references)):
        return QueryResult(stop="markers")
    if query is None or len(query.points) < MIN_MATCHED:
        return QueryResult(stop="insufficient_query")
    vectors = constellation(query).vectors
    pairs = []
    remaining = limits.query_prefixes
    for reference in references:
        if reference is None or len(reference.points) < MIN_MATCHED:
            pairs.append(PairResult(stop="insufficient_reference"))
            continue
        pair = enumerate_pair(query, reference, vectors, limits, remaining)
        pairs.append(pair)
        remaining -= pair.prefixes
        if pair.stop:
            return QueryResult(tuple(pairs), pair.stop)
    return QueryResult(tuple(pairs))


def classify(result):
    """Classify evidence in the supplied reference list without physical-region labels."""
    if result.stop in BUDGET_STOPS:
        return "unresolved_search_budget"
    if result.stop or any(pair.stop for pair in result.pairs):
        return "unavailable_alignment"
    candidates = [pair for pair in result.pairs if pair.hypotheses]
    if len(candidates) > 1:
        return "ambiguous_references"
    if not candidates:
        return "no_match"
    hypotheses = candidates[0].hypotheses
    if len(hypotheses) > 1:
        return "ambiguous_correspondences"
    return "unique_reference" if hypotheses[0].alignment_2d else "unresolved_2d"
