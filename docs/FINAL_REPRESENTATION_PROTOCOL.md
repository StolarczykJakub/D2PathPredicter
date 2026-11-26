# Phase 1.6.5 final representation holdout protocol

One new layout, three source images and two independent `marker-raw-v1` returns per image. The unit of evidence is one physical layout and one moved-view event. Directed pairs reuse the same views and reviewers. The Phase 1.6.3 gate remains FAILED. The Phase 1.6.4 diagnostic motivates this one prospective check. NEXT and WP are independently INCONCLUSIVE. [Prospective selection rule](FINAL_REPRESENTATION_SELECTION.md) · [Phase 1.6.4 results](PARTIAL_CONSTELLATION_RESULTS.md)

## Fixed matchers and inputs

| Method | Frozen implementation |
| --- | --- |
| A · player-relative | 4 px, offsets relative to an observed player, existing combined radii and hue predicate |
| B · strict constellation | 6 px, native-axis vectors, complete smaller-set correspondence, frozen 2D check |
| C · partial constellation | 6 px, native-axis vectors, all admissible maximal assignments, at least three matched markers and two-thirds count coverage on both sides. Resolution also requires at least 25% bounding-box area on each side and a reliable corresponding triangle with a baseline of at least 24 px and altitude greater than the summed marker radii in each view |

Reuse the frozen Phase 1.6.4 evaluator's assignment verification, coverage and uniqueness logic. All methods consume marker-only geometry and uncertainty, plus the observed player offset and uncertainty for A. B and C can use native marker observations when the player is unresolved. Unobserved geometry is unknown. The marker-only guide, study window and native axes remain fixed. The matcher never receives frame identities, shifts, visibility labels, physical regions or expected correspondences. The earlier approximately 22% spatial support case motivates documenting below-floor rates. The 25% threshold is frozen. [Frozen partial matching rules](PARTIAL_CONSTELLATION_PROTOCOL.md)

The limits are 24 markers per view, 24 reference observations per query, 100,000 expanded pair prefixes, 256 retained hypotheses per pair and 600,000 query prefixes. Budget exhaustion marks the whole query unresolved even if retained evidence includes a candidate. Report compatible candidates and all retained hypotheses under their stop status.

## Frozen roster and intake

| Query group | Queries | Candidate slots | Expected positive slots |
| --- | ---: | ---: | ---: |
| Same-frame counterpart | 6 | 18 | 6 |
| Moved-view, both directions, all reviewer pairings | 4 | 16 | 8 |
| Cross-layout and out-of-corpus | 6 | 24 | 0 |
| Total | 16 | 58 | 14 |

Same-frame reference lists contain the other review of the query's frame and both reviews of the independently distinct region. Region 2 queries use both primary region 1 reviews as distinct controls. Moved-view reference lists contain both opposite-view reviews and both region 2 reviews. Cross-layout reference lists contain the four frozen windowed development RAW observations from `mapa-07`. Calibration `mapa-06` stays calibration evidence. There are 20 within-layout distinct-region slots, including repeated controls, and 24 cross-layout slots. Each slot and direction is locked by opaque packet ID.

Before opening any returns, verify the read-only lock and every referenced hash. Preserve the six original return byte streams, supplied manifest and archive. Require exact packet and frame identity, CRC, byte count, SHA-256, valid `marker-raw-v1` shape, and observed points inside the original study window. Retain partial and failed returns and reported deviations. An operational pair needs valid, declared complete searches from both intended independent sessions and no known independence breach. Record unknown provenance fields as unknown. Marker count, player status or search limits do not remove an operational pair. These can make an individual method unavailable. Search validity and operational denominators are fixed from intake, before invoking the matchers.

## Evaluation and decision

After intake and before matching, use the locked wall translations with the existing reciprocal unambiguous matching rule for observed centres within 8 px and equal known hue. Record ambiguous identity evidence separately. Where the two raw views register to the same region, label the observable shared identities using that rule. The evaluator requires independent confirmation of two predeclared visibility witnesses, one visible in each respective source image and unreadable or unrendered in the other. Use the locked wall-registered witness positions and hue, a unique reported observed centre within 8 px, and no same-hue observed centre within 8 px in the opposite annotation. The original recording and wall labels establish the mechanism. An annotation omission by itself establishes no visibility change. Compute eligibility and witness confirmation for each of the eight operational moved-pair slots before invoking any matcher.

Report all eight planned moved pairs and their operational denominator, label availability, confirmed genuine bilateral denominator, and the subset meeting C's frozen geometry floor on the independently shared identities. Report every below-floor pair and any compatible unresolved hypothesis separately. A verified resolved pair has a 2D hypothesis composed entirely of independently verified pairs. Report exact recovery, both count fractions, both area fractions and the admitted correspondence count. A below-floor case can demonstrate appropriate abstention. It does not count as positive recovery or as a win over B. For each method report correct local geometry, reference ambiguity, within-reference correspondence ambiguity, labeled-region ambiguity, candidate region uniqueness after grouping review duplicates, all compatible wrong slots, false unique regions, unique outcomes with unverified correspondence support, no-match and explicit budget or input abstention. The historical uniqueness logic remains frozen. Corpus outcomes describe the tested reference roster. This protocol makes no hidden-target prediction claim.

The primary gate applies to C. A and B provide comparison outcomes. Require all of the following:

- All six same-frame and eight moved slots operational with unambiguous evaluator truth, all three same-frame views represented by eligible checks, and at least one genuine bilateral floor-eligible moved pair in each query direction. Missing prerequisites leave the local recovery hypothesis INCONCLUSIVE.
- Recover all eligible same-frame and all genuine bilateral floor-eligible moved pairs with verified 2D support. Count a gain only on a completed identical floor-eligible bilateral slot recovered by C and missed by strict B. Require at least one paired gain and more recoveries by C than strict B on this denominator. An incomplete required search, including a budget stop, leaves the gate INCONCLUSIVE.
- Zero C false unique regions and zero C unique outcomes with unverified correspondence support across the 16 queries. Any such safety failure fails the gate even if positive eligibility is incomplete. Require no incompatible ambiguity suppression or truncated unique/no-match verdict. Report collisions even where ambiguity correctly prevents uniqueness.

A complete evaluable run that misses an eligible required recovery or shows zero advantage fails the advancement gate. A below-floor-only or unconfirmed bilateral cohort is INCONCLUSIVE. Report the verified local alignment claim and the separate corpus outcome. One independent run cannot estimate a population collision rate or hidden-target accuracy. After evaluation, discuss a direct NEXT predictive-information experiment or a strategic pivot with the owner.

Preparation ends after verifying the release and lock. Intake and scoring require the actual owner-supplied independent returns in a later phase.
