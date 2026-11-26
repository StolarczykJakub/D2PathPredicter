"""Small frequency tables fitted from independent development observations."""

from collections import Counter, defaultdict
from collections.abc import Iterable

from .coordinates import SECTORS, bearing, sector
from .dataset import AXES, TARGETS, Observation

FEATURES = ("room_count", "room_sectors", "connectivity", "corridor_axes", "frontier", "dead_ends")
METHODS = ("unconditional", "entrance", "geometry", *(f"entrance+{feature}" for feature in FEATURES))
MIN_SUPPORT = 2

Sample = tuple[Observation, dict[str, str | None]]
Tables = dict[str, dict[tuple, Counter]]


def features(obs: Observation) -> tuple:
    rooms, links = obs.geometry.rooms, obs.geometry.connections
    room_sectors = {sector(bearing((0, 0), room)) for room in rooms if room != (0, 0)}
    degree = Counter(room for link in links for room in link)
    corridor_axes = {SECTORS.index(sector(bearing(a, b))) % 4 for a, b in links}
    return (
        min(4, len(rooms)),
        tuple(sorted(room_sectors)),
        (min(3, len(links)), any(count >= 3 for count in degree.values())),
        tuple(sorted(corridor_axes)),
        tuple(sorted({direction for _, direction in obs.branches})),
        min(2, len(obs.dead_ends)),
    )


def player_region(obs: Observation) -> str | None:
    if obs.player is None:
        return None
    if obs.player == (0, 0) and not obs.player_error:
        return "origin"
    angle = bearing((0, 0), obs.player, obs.player_error)
    return sector(angle) if angle is not None else None


def contexts(obs: Observation):
    orientation = obs.orientation
    axis = next((name for name, directions in AXES.items() if orientation in directions), orientation)
    orientations = dict.fromkeys((orientation, axis, None))
    regions = dict.fromkeys((player_region(obs), None))
    return [(heading, region) for heading in orientations for region in regions]


def fit(samples: Iterable[Sample]) -> Tables:
    tables = {target: defaultdict(Counter) for target in TARGETS}
    for obs, labels in samples:
        variants = [("prior", None)]
        if obs.geometry.rooms:
            signature = features(obs)
            variants.append(("geometry", signature))
            variants.extend((f"entrance+{feature}", value) for feature, value in zip(FEATURES, signature))
        for context in contexts(obs):
            for method, value in variants:
                for target, label in labels.items():
                    tables[target][(method, context, value)][label] += 1
    return tables


def summarize_votes(counts, source):
    votes = {direction: counts[direction] for direction in SECTORS if counts.get(direction)}
    total = counts.total()
    most = max(votes.values(), default=0)
    winners = [direction for direction, count in votes.items() if count == most]
    supported = len(winners) == 1 and most >= MIN_SUPPORT and 3 * most >= 2 * total
    if supported:
        status = "PREDICTED"
    else:
        status = "AMBIGUOUS" if len(votes) > 1 else "UNKNOWN"
    return {
        "status": status,
        "direction": winners[0] if supported else None,
        "source": source,
        "support": total,
        "votes": votes,
        "unresolved": counts.get(None, 0),
        "support_share": most / total if votes else None,
    }


def predict(tables: Tables, obs: Observation, method: str) -> dict:
    if method not in METHODS:
        raise ValueError(f"unknown prediction method {method}")
    uses_geometry = method not in ("unconditional", "entrance")
    if obs.player is None or (uses_geometry and not obs.geometry.rooms):
        return {target: {"status": "INSUFFICIENT_DATA", "direction": None} for target in TARGETS}
    available = contexts(obs)
    keys = []
    if uses_geometry:
        signature = features(obs)
        value = signature if method == "geometry" else signature[FEATURES.index(method.split("+", 1)[1])]
        keys.extend((method, context, value) for context in available if bool(context[0]) == bool(obs.orientation))
    keys.extend(("prior", context, None) for context in available if method != "unconditional" or context[0] is None)
    predictions = {}
    for target in TARGETS:
        table = tables[target]
        chosen = next((key for key in keys if key in table and table[key].total() >= MIN_SUPPORT), keys[-1])
        source = chosen[0] if chosen[0] != "prior" else ("entrance" if chosen[1][0] else "unconditional")
        predictions[target] = summarize_votes(table.get(chosen, Counter()), source)
    return predictions
