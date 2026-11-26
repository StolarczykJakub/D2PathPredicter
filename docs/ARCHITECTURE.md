# Offline experiment architecture

The first implementation is one CLI that reads local fixtures and emits a reproducible metrics report. The source adapter for an optional classic reference export is a research utility outside the matcher. Generated reference files can be loaded offline.

```text
Full reference maps -> entrance-relative candidate features -> reference pool
Held-out full maps  -> reveal simulator -> partial observations -> matcher
Matcher -> per-target distribution -> evaluator with held-out ground truth
```

## Inputs and coordinates

- A full fixture carries a provenance tag, fixture ID, area, difficulty, geometry with room and connector locations, visible-geometry proxy where applicable, an entrance anchor, and optional labeled target anchors. Version, game mode, source data and generator revision are recorded when available. Use plain JSON to start.
- An observation has an entrance-relative player position and feature states within a reveal mask. Features can be known present, known absent, or unknown. Unknown includes cropped, unrevealed and uncertain areas. The matcher can receive only information available from the observation. Fixture IDs, seeds, hidden edges, hidden room labels, target coordinates and target icons stay in the evaluator.
- Start in canonical grid coordinates at a fixed scale. Origin and axes must be consistent across fixtures and observations. An entrance-facing estimate may come from visible geometry, and can also be uncertain. Rooms with unreadable orientation require multiple valid alignments or abstention. Deduplicate hypotheses so a symmetric reference map does not receive extra vote weight merely for yielding multiple alignments.
- Normalize world or level-local coordinates at import. For a later image experiment, one transform to test is `u = sx * (x - y) + tx` and `v = sy * (x + y) + ty`. Fit translation and scale from paired landmarks at a fixed setting and report alignment residuals. Keep room and tile scales explicit. Treat a simulated transform as a controlled input, and measure registration separately when withdrawing the idealized anchor.

## Matching and prediction

1. Start with a scan of entrance-aligned references. Compare only features whose visibility is established, including the observed sides of partly visible rooms. Use exact equality on clean cases. Use a fixed validation-selected tolerance for explicit clipping and feature errors. Score candidates from visible geometry alone.
2. Retain ties and near-ties within the tolerance. Count compatible distinct configurations and surviving alignments. Start with equal map weights among comparable matches and split a map's weight across its surviving alignments. Preserve competing target hypotheses even when the visible portions are identical.
3. For NEXT and WP separately, transform each candidate's target anchor into observation coordinates. Bin the vector from the current player position into four fixed grid-axis sectors. A target can be unknown or absent in a fixture. Keep that support outside the directional sectors. Return a direction when its calibrated support and evidence are sufficient. Give a coordinate estimate only when candidates agree on a compact region. A representative candidate target anchor can serve as the point estimate.
4. Return status, candidate counts, sector support and any coordinate estimate in a machine-readable report. Proposed statuses are **exact** for a unique full configuration in the candidate pool with zero visible mismatch and enough evidence, **probable** for a clear best hypothesis within the allowed tolerance, **ambiguous** for ties or inadequate evidence, and **no match** for sufficient evidence with every candidate rejected. Report the per-target answer independently from overall match status. A map can be ambiguous while one of its target bearings is stable.

The evaluator alone knows whether the true full configuration was in the candidate universe. A unique fit to a partial observation is an exact fit to the compared features. It can still be the wrong map. A small closed-set fixture challenge establishes that implementation behavior is correct when the generating layout is present. The held-out experiment measures directional generalization when it is absent.

## Runtime boundary

Production candidates can eventually be stored as arrays of integer coordinates, masks and target anchors. Precompute signatures only if the measured scan motivates them. A later observer can reuse the previous result when the observed geometry and player anchor are unchanged, and reuse candidate scores if only the player position changes. Phase 1 consists of file input, simulation, matching and reporting. Its results determine whether work on image extraction is warranted.
