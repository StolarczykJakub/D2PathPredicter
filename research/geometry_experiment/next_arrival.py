"""Fixed Stage 0 NEXT pilot adapter. Callers supply development data and early observations only."""

from collections import Counter
from dataclasses import dataclass
from math import dist

from research.marker_fingerprint.match import Markers, offset
from research.marker_fingerprint.partial_match import classify, match_query

from .coordinates import bearing
from .dataset import AXES


SECTORS = ("-Y", "+X", "+Y", "-X")
MIN_VOTES = 2
ROUNDING_PX = 1


@dataclass(frozen=True)
class Observation:
    player_px: tuple[float, float]
    player_radius_px: float
    orientation: str | None = None
    markers: Markers | None = None


@dataclass(frozen=True)
class Reference:
    # Supply one reference per independently verified development layout.
    observation: Observation
    sector: str
    target_px: tuple[float, float] | None = None
    target_radius_px: float = 0


def stable_sector(player, target, radius):
    du, dv = offset(target, player)
    if radius >= min(abs(du), abs(dv)):
        return None
    return SECTORS[int(bearing(player, target) // 90)]


def prior(votes):
    counts = Counter(votes)
    total = counts.total()
    most = max(counts.values(), default=0)
    winners = [sector for sector, count in counts.items() if count == most]
    reason = None
    if len(winners) > 1:
        reason = "tied_support"
    elif most < MIN_VOTES or 3 * most < 2 * total:
        reason = "insufficient_support"
    return {"sector": None if reason else winners[0], "reason": reason,
            "votes": dict(counts), "support": most, "total": total,
            "support_share": most / total if total else None}


def unconditional(references):
    return prior(ref.sector for ref in references)


def axis(orientation):
    return next((key for key, headings in AXES.items() if orientation in headings), orientation)


def entrance(references, observation):
    orientation = observation.orientation
    if orientation is None:
        return {**prior(()), "reason": "unresolved_orientation", "bucket": None}
    signed = [ref.sector for ref in references if ref.observation.orientation == orientation]
    if orientation not in AXES and len(signed) >= MIN_VOTES:
        return {**prior(signed), "bucket": orientation}
    pool = axis(orientation)
    return {**prior(ref.sector for ref in references if axis(ref.observation.orientation) == pool),
            "bucket": pool}


def geometry(references, observation):
    """Retain all matcher hypotheses and aggregate at most one vote per reference layout."""
    matches = match_query(observation.markers, [ref.observation.markers for ref in references])
    reasons = set()
    if matches.stop:
        reasons.add(matches.stop)
    evidence = []
    votes = Counter()
    competing_sectors = set()
    for ref, pair in zip(references, matches.pairs):
        if pair.stop:
            reasons.add(pair.stop)
        sectors = []
        for hypothesis in pair.hypotheses:
            if not hypothesis.alignment_2d:
                reasons.add("weak_alignment")
                sectors.append(None)
                continue
            if ref.target_px is None:
                reasons.add("missing_target")
                sectors.append(None)
                continue
            translation = hypothesis.offset_px
            queries = observation.markers.points
            targets = ref.observation.markers.points
            bound = max(dist(offset(targets[j].point, queries[i].point), translation)
                        + queries[i].radius + targets[j].radius for i, j in hypothesis.pairs)
            radius = bound + ref.target_radius_px + observation.player_radius_px + ROUNDING_PX
            sector = stable_sector(observation.player_px, offset(ref.target_px, translation), radius)
            if sector is None:
                reasons.add("uncertain_sector")
            sectors.append(sector)
        evidence.append(tuple(sectors))
        distinct = set(sectors)
        competing_sectors.update(distinct - {None})
        if len(distinct) == 1 and None not in distinct:
            votes[sectors[0]] += 1
    if len(competing_sectors) > 1:
        reasons.add("competing_sectors")
    if max(votes.values(), default=0) < MIN_VOTES:
        reasons.add("insufficient_support")
    return {"sector": None if reasons else next(iter(votes)), "reasons": tuple(sorted(reasons)),
            "votes": dict(votes), "competing_sectors": tuple(sorted(competing_sectors)),
            "hypothesis_sectors": tuple(evidence), "matches": matches, "alignment_status": classify(matches)}
