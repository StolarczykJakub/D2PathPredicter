"""Frozen scoring functions for future, validated Phase 1.6.5 returns."""

from collections import Counter
from math import dist

from research.marker_fingerprint.evaluate_partial import (
    Candidate, Trial, eligibility, operation, recovered, region, registered_truth, score, summary,
)


METHODS = {"A": "A", "B": "B", "C": "partial"}
CAPS_PX = {"A": 4, "B": 6, "C": 6}
PLANNED_QUERIES = {"same_frame": 6, "moved": 4, "out_of_corpus": 6}
PLANNED_PAIRS = {"same_frame": 6, "moved": 8, "wrong_within_layout": 20, "wrong_cross_layout": 24}


def witness_hits(view, witness):
    return sum(marker.hue == witness["hue"] and
               dist(tuple(x + t for x, t in zip(marker.point, view.translation)), witness["registered_px"]) <= 8
               for marker in view.native.points)


def bilateral_confirmed(query, reference, witnesses):
    by_view = {query.view: query, reference.view: reference}
    return all(witness_hits(by_view[owner], witness) == 1
               and witness_hits(by_view[other], witness) == 0
               for owner, other in (("r1", "r1b"), ("r1b", "r1"))
               for witness in (witnesses[owner],))


def build_trial(kind, query_id, references, views, witnesses):
    query = views[query_id]
    candidates, audit = [], []
    for ref in references:
        reference = views[ref]
        operational = query.complete and reference.complete
        expected = region(query) == region(reference)
        truth = None
        identity_status = "distinct_region" if not expected else "unavailable"
        if operational and expected:
            try:
                truth = registered_truth(query, reference)
            except ValueError:
                identity_status = "ambiguous"
            else:
                identity_status = "available"
        bilateral = (kind == "moved" and identity_status == "available"
                     and bilateral_confirmed(query, reference, witnesses))
        candidates.append(Candidate(ref, reference, truth))
        audit.append({"query": query_id, "reference": ref, "query_view": query.view,
                      "reference_view": reference.view, "expected_region": expected,
                      "operational": operational, "identity_truth": identity_status,
                      "genuine_bilateral": bilateral})
    trial = Trial(kind, f"{kind}/{query_id}", query, tuple(candidates))
    floor = eligibility(trial)
    for pair, eligible in zip(audit, floor):
        pair["geometry_floor"] = eligible
    return trial, floor, audit


def decision(runs, pair_audits):
    same, moved = [], []
    for c_row, b_row, audit in zip(runs["C"], runs["B"], pair_audits):
        if c_row["group"] not in ("same_frame", "moved"):
            continue
        group = same if c_row["group"] == "same_frame" else moved
        for c, b, pair in zip(c_row["comparisons"], b_row["comparisons"], audit):
            if not pair["expected_region"]:
                continue
            complete = c["stop"] == "complete" and c_row["outcome"] != "unresolved_search_budget"
            strict_complete = b["stop"] == "complete" and b_row["outcome"] != "unresolved_search_budget"
            group.append({**pair, "partial_complete": complete, "strict_complete": strict_complete,
                          "partial_recovered": complete and recovered(c, "partial"),
                          "strict_recovered": strict_complete and recovered(b, "B"),
                          "partial_weak_compatible": any(not h["alignment_2d"] for h in c["hypotheses"]),
                          "partial_resolved_candidate": bool(c_row["resolved_candidates"])})
    same_eligible = [pair for pair in same if pair["geometry_floor"]]
    bilateral = [pair for pair in moved if pair["genuine_bilateral"]]
    eligible_moved = [pair for pair in bilateral if pair["geometry_floor"]]
    operational_moved = [pair for pair in moved if pair["operational"]]
    floor_moved = [pair for pair in moved if pair["geometry_floor"]]
    below_floor = [pair for pair in operational_moved if pair["identity_truth"] == "available"
                   and not pair["geometry_floor"]]
    missing_required = (len(same) != PLANNED_PAIRS["same_frame"] or len(moved) != PLANNED_PAIRS["moved"]
                        or any(not p["operational"] or p["identity_truth"] != "available" for p in (*same, *moved))
                        or {p["query_view"] for p in same_eligible} != {"r1", "r1b", "r2"}
                        or {p["query_view"] for p in eligible_moved} != {"r1", "r1b"}
                        or any(not p["partial_complete"] for p in (*same_eligible, *eligible_moved))
                        or any(not p["strict_complete"] for p in eligible_moved)
                        or any(row["outcome"] == "unresolved_search_budget" for row in runs["C"]))
    outcomes = Counter(row["outcome"] for row in runs["C"])
    false_unique = outcomes["false_unique"]
    unverified_unique = outcomes["unverified_unique_alignment"]
    losses = sum(not p["partial_recovered"] for p in (*same_eligible, *eligible_moved))
    gains = sum(p["partial_recovered"] and not p["strict_recovered"] for p in eligible_moved)
    partial_count = sum(p["partial_recovered"] for p in eligible_moved)
    strict_count = sum(p["strict_recovered"] for p in eligible_moved)
    if false_unique or unverified_unique:
        verdict = "FAILED"
    elif missing_required:
        verdict = "INCONCLUSIVE"
    elif losses or not gains or partial_count <= strict_count:
        verdict = "FAILED"
    else:
        verdict = "PASS"
    return {"verdict": verdict, "missing_required_evidence": missing_required,
            "same_frame": same, "moved": moved,
            "moved_denominators": {"planned": len(moved), "operational": len(operational_moved),
                                   "truth_labeled": sum(p["identity_truth"] == "available" for p in moved),
                                   "genuine_bilateral": len(bilateral), "geometry_floor": len(floor_moved),
                                   "genuine_bilateral_at_floor": len(eligible_moved), "below_floor": len(below_floor)},
            "required_misses": losses, "paired_gain_vs_strict": gains,
            "partial_recovered_bilateral_at_floor": partial_count, "strict_recovered_bilateral_at_floor": strict_count,
            "false_unique": false_unique, "unverified_unique_alignment": unverified_unique}


def evaluate(roster, observations, witnesses):
    """Score a locked roster only after external intake and provenance validation."""
    prepared = [build_trial(kind, q, refs, observations, witnesses) for kind, q, refs in roster]
    pair_audits = [audit for _, _, audit in prepared]
    runs = {label: [score(trial, mode, operation(trial, mode)(), floor) for trial, floor, _ in prepared]
            for label, mode in METHODS.items()}
    return {"runs": runs, "intake_and_truth": pair_audits,
            "summary": {label: summary(rows, METHODS[label]) for label, rows in runs.items()},
            "gate": decision(runs, pair_audits)}
