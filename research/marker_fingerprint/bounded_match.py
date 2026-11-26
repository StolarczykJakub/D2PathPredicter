"""Bounded Stage 2 matching with the frozen Stage 1 predicates."""

from dataclasses import dataclass
from itertools import combinations
from math import dist
from statistics import mean

from research.marker_fingerprint.match import compatible_hue, constellation, offset, resolved_triangle


@dataclass(frozen=True, slots=True)
class Limits:
    markers: int = 24
    references: int = 24
    pair_prefixes: int = 100_000
    pair_hypotheses: int = 256
    query_prefixes: int = 600_000


LIMITS = Limits()
CAPS = (4, 6, 8)


def error(delta, radius, cap):
    limit = min(cap, radius)
    return None if delta > limit else delta / limit if limit else 0.0


@dataclass(frozen=True, slots=True)
class Hypothesis:
    pairs: tuple
    score: float
    offset_px: tuple
    alignment_2d: bool


@dataclass(slots=True)
class PairResult:
    prefixes: int = 0
    checks: int = 0
    hypotheses_seen: int = 0
    hypotheses: tuple = ()
    stop: str | None = None


@dataclass(slots=True)
class QueryResult:
    pairs: tuple[PairResult, ...] = ()
    stop: str | None = None

    @property
    def prefixes(self):
        return sum(pair.prefixes for pair in self.pairs)


def enumerate_pair(query, reference, use_vectors, cap, limits, remaining, query_geometry):
    reverse = len(query.points) > len(reference.points)
    left, right = (reference, query) if reverse else (query, reference)
    if use_vectors:
        reference_geometry = constellation(reference).vectors
        left_vectors, right_vectors = ((reference_geometry, query_geometry) if reverse
                                       else (query_geometry, reference_geometry))
    result = PairResult()
    player_radius = left.player_radius + right.player_radius
    choices = []
    for a in left.points:
        allowed = []
        for j, b in enumerate(right.points):
            result.checks += 1
            if compatible_hue(a.hue, b.hue):
                residual = 0.0 if use_vectors else error(
                    dist(a.point, b.point), a.radius + b.radius + player_radius, cap)
                if residual is not None:
                    allowed.append((j, residual))
        choices.append(allowed)

    found = []

    def visit(indices, used, errors):
        if result.prefixes == remaining:
            result.stop = "query_prefixes"
            return
        if result.prefixes == limits.pair_prefixes:
            result.stop = "pair_prefixes"
            return
        result.prefixes += 1
        i = len(indices)
        if i == len(choices):
            result.hypotheses_seen += 1
            if len(found) == limits.pair_hypotheses:
                result.stop = "pair_hypotheses"
                return
            pairs = tuple(enumerate(indices))
            displacement = (0, 0)
            alignment_2d = False
            if use_vectors:
                displacement = tuple(map(mean, zip(*(offset(right.points[k].point, left.points[h].point)
                                                     for h, k in pairs))))
                alignment_2d = any(
                    resolved_triangle([left.points[h] for h, _ in triple]) and
                    resolved_triangle([right.points[k] for _, k in triple])
                    for triple in combinations(pairs, 3))
            if reverse:
                pairs = tuple(sorted((k, h) for h, k in pairs))
                displacement = tuple(-x for x in displacement)
            found.append(Hypothesis(pairs, mean(errors), displacement, alignment_2d))
            return
        if i == 0 and not all(choices):
            return
        for j, residual in choices[i]:
            bit = 1 << j
            if used & bit:
                continue
            new_errors = (residual,)
            if use_vectors:
                vector_errors = []
                for h, k in enumerate(indices):
                    result.checks += 1
                    radii = (left.points[i].radius + left.points[h].radius +
                             right.points[j].radius + right.points[k].radius)
                    residual = error(dist(left_vectors[h][i], right_vectors[k][j]), radii, cap)
                    if residual is None:
                        break
                    vector_errors.append(residual)
                else:
                    new_errors = tuple(vector_errors)
                    visit(indices + (j,), used | bit, errors + new_errors)
                if result.stop:
                    return
                continue
            visit(indices + (j,), used | bit, errors + new_errors)
            if result.stop:
                return

    visit((), 0, ())
    result.hypotheses = tuple(sorted(found, key=lambda hypothesis: (hypothesis.score, hypothesis.pairs)))
    return result


def match_query(query, references, representation, cap, *, limits=LIMITS):
    """Match geometry only and leave physical-region classification to the evaluator."""
    if representation not in ("A", "B") or cap not in CAPS:
        raise ValueError("unknown representation or cap")
    if len(references) > limits.references:
        return QueryResult(stop="references")
    if max((len(m.points) for m in (query, *references) if m is not None), default=0) > limits.markers:
        return QueryResult(stop="markers")
    if query is None or len(query.points) < 2:
        return QueryResult(stop="insufficient_query")
    use_vectors = representation == "B"
    geometry = constellation(query).vectors if use_vectors else None
    results = []
    remaining = limits.query_prefixes
    for ref in references:
        if ref is None or len(ref.points) < 2:
            results.append(PairResult(stop="insufficient_reference"))
            continue
        pair = enumerate_pair(query, ref, use_vectors, cap, limits, remaining, geometry)
        results.append(pair)
        remaining -= pair.prefixes
        if pair.stop:
            return QueryResult(tuple(results), pair.stop)
    return QueryResult(tuple(results))
