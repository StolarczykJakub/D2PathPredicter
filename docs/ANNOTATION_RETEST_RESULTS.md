# Phase 1.6.1 annotation retest results

**Decision E · INCONCLUSIVE under the frozen gate.** All eight returns passed structural validation. Both frame pairs lost counterbalancing, so the comparisons below are exploratory, including where they apply the frozen numerical thresholds. Player and marker measurements passed those thresholds in both passes. The Stage 0 arrival-room centre, Stage 3 semantic graph and Stage 3 RAW wall match count failed their respective readiness checks. [Representation decision](REPRESENTATION_DECISION.md) · [Frozen protocol](ANNOTATION_RETEST_PLAN.md)

This repeatability study used two 1920×1080 frames from **one development layout**. The pilot source is owner-reported D2R 3.4.95032, DWR ROW, Battle.net, Catacombs Level 2 on Normal, entered from Level 1. Source frames are byte-identical to the masked V1 release frames. The evaluation required only the frozen PNG and JSON inputs. The study has zero independent evaluation layouts and zero target predictions. [Pilot provenance and eligibility](PILOT_BENCHMARK_RESULTS.md)

## Intake and pass order

All eight files from `docs/annotation_analysis` were copied byte for byte into the private `local-data/phase-1-6-1/returns/<packet>/<pass>.json` store. SHA-256 and byte counts are in the private intake file. The supplied copies remain unedited. The evaluator checks duplicate JSON keys, expected fields and nested record shapes, protocol version 2, packet and release-image digests, native coordinate bounds, radii, local IDs and links, allowed statuses, Boolean search and timing flags, the eight-trace cap, and finite elapsed time within the eight-minute limit. All eight pass. No observed or measured feature lacks its required radius. Neither reviewer identities nor release and receipt times were available. Search completeness, timing, and reviewer exposure are self-reported or unverified as applicable. [Private intake and hashes](../local-data/phase-1-6-1/owner/derived/intake.json)

| Frame | Packet | Input file suffix | README first | Actual first from returns | RAW min | SEMANTIC min |
| --- | --- | --- | --- | --- | ---: | ---: |
| A · Stage 0 | h9v2c | No suffix | RAW | Unstated | 0.87 | 0.66 |
| A · Stage 0 | k4m7q | (1) | SEMANTIC | RAW, explicit in both files | 0.70 | 0.64 |
| B · Stage 3 | p6r8t | (2) | SEMANTIC | RAW, explicit in both files | 1.21 | 1.13 |
| B · Stage 3 | w3j5n | (3) | RAW | Unstated | 0.75 | 0.87 |
| **Median** | | | | | **0.810** | **0.765** |

All eight passes report both searches complete and the time limit unreached. Each wall sample reaches the eight-trace cap. Completeness is scoped to the visible glyph search and capped wall selection. The four release ZIPs, README orders, frame SHA-256 values, image dimensions and blank-template metadata match the owner manifest. The prior V1 lock, six V1 implementation and protocol files, four V1 releases, four V1 originals and their frozen copies, and three V2 frozen files match their pinned SHA-256 values. [Private release manifest](../local-data/phase-1-6-1/owner/manifest.json)

The owner reports that an external prompt overrode the README with a RAW-first instruction and that the last reviewer was told to follow the README. The two SEMANTIC-first assignees explicitly report switching to RAW first. Their SEMANTIC notes say they started from the blank template without consulting the saved RAW, and disclose shared model context. Neither RAW-first assignee states actual order in the returns. The order contrast failed on both frames, even if both RAW-first assignees followed their README. Two passes within a session may share visual memory. Four separate sessions were reported, with no independent exposure log. The frozen plan admits only compliant frame pairs for formal evaluation, leaving **0/2 eligible pairs**. Timing is descriptive. Pass-order effects and independent modality-effort differences are unmeasured. [Frozen handoff rules](ANNOTATION_RETEST_PLAN.md#frames-and-independent-handoff)

## External 10 px check

| RAW agreement | Frame A | Frame B |
| --- | ---: | ---: |
| Player displacement | 1.00 px | 2.24 px |
| Matched wall segments | 8/8 | 2/8 |
| Mean / maximum of matched walls’ larger endpoint errors | 3.49 / 7.62 px | 2.70 / 3.16 px |
| Matched glyphs | 3/3 | 17/17 |
| Mean / maximum glyph-centre error | 2.22 / 3.00 px | 1.15 / 2.24 px |

Every external figure reproduces at its reported precision. This calculation uses Euclidean distances, geometric one-to-one assignment and the smaller maximum endpoint error over the two endpoint orders. The external brief specifies the tolerance and endpoint invariance but leaves its scalar wall cost unspecified. The calculation above uses the sum of pairwise maximum endpoint errors to break assignments with equal match counts. There were no tied optimal assignments. [Pair-by-pair values](../local-data/phase-1-6-1/owner/derived/agreement.json)

## Frozen criteria applied to returned values

| Check | Returned values and threshold outcome |
| --- | --- |
| Player · ≤8 px and ≤summed radii | **Pass** in all four pairs. RAW A/B 1.00/2.24 px. SEMANTIC A/B 1.41/2.24 px. Each summed radius 10 px. |
| Stage 0 arrival room · two observed centres, each radius ≤12 px, ≤12 px apart and within summed radii | **Fail.** Both centres `UNKNOWN`. Scene stairs agree to 6.00 px, within the separate 12 px displacement and summed-radius checks. The individual scene radii, 16 and 18 px, exceed the arrival-centre precision limit. The entrance glyph and player arrival are both `UNKNOWN`. All four Stage 3 entrance fields are `UNKNOWN` on both returns. |
| Orientation | `UNKNOWN` in all four SEMANTIC returns. No measured centreline, directed sector or axis. Directed and axial agreement are unavailable. The shared unresolved state permits the V1 pooled-orientation path. |
| Stage 3 regions · ≥3 matched ROOM centres in radius, ≥75% symmetric region match, ≥80% matched class agreement | Four ROOM–ROOM centres in radius and 7/8 matched classes agree (87.5%). **Fail** for overall region match, 16/25 (64%). |
| Stage 3 graph · ≥1 shared confirmed link, ≥1 shared supported terminal and V1 projection | **Fail.** Zero shared or one-sided confirmed edges, terminals, or frontiers. The empty sets agree. There are zero terminal claims to project and no parser conflict to count. Without a confirmed departure there is no link or frontier to encode as V1 terminal evidence. |
| RAW markers · ≥2 matches at A and ≥5 at B, ≥80% symmetric agreement and ≥80% of matches pass centre and extent, complete searches | **Pass.** 3/3 at A and 17/17 at B. Both rates are 100% in both frames. |
| SEMANTIC markers · same criteria | **Pass.** 3/3 at A and 17/17 at B. Both rates are 100% in both frames. |
| Stage 3 RAW walls · ≥4 matches within 15 px, ≥75% of matches reproducible within 12 px and summed radii | **Fail.** 2/8 matched and both reproduce (100% of matches). The count stays at two when the matching limit rises from 10 to 15 px. |
| RAW information advantage · ≥2 reproduced marks outside the V1 graph or missing from both SEMANTIC returns | **Pass for retention.** Frame A has eight jointly reproduced walls with no supported room assignment and three measured glyphs with no supported room or departure. These marks are retained in V2 SEMANTIC too. Frame B has one of the two reproduced walls unassigned on both sides. **Zero RAW-only marks** at the frozen matching limits when each RAW pass is compared with its paired SEMANTIC pass. |

SEMANTIC and RAW readiness both fail on the returned measurements. Those failures stand apart from formal eligibility. The 10 px diagnostic has no effect on the official thresholds. [Frozen decision and readiness rules](ANNOTATION_RETEST_PLAN.md#readiness-thresholds)

### Glyph positions and extents

| Frame/pass | Centre mean / max, px | Larger endpoint error, mean / max, px | Absolute span difference, max px | Player-relative centre max, px | Player-relative endpoint max, px |
| --- | ---: | ---: | ---: | ---: | ---: |
| A RAW | 2.22 / 3.00 | 3.02 / 4.00 | 3.08 | 3.16 | 4.12 |
| A SEMANTIC | 1.41 / 2.24 | 1.55 / 2.24 | 1.36 | 2.24 | 3.61 |
| B RAW | 1.15 / 2.24 | 1.70 / 2.83 | 2.72 | 4.24 | 5.00 |
| B SEMANTIC | 0.18 / 1.00 | 1.12 / 2.24 | 2.72 | 3.16 | 4.00 |

No unmatched glyphs or missing glyph extents. All 40 pairs agree on appearance when yellow and purple/magenta are grouped by visible hue. Frame A has two yellow and one purple/magenta per return. Frame B has 16 yellow and one purple/magenta per return. Phrasing varies among bars, panels and patches. The comparisons establish colour and location repeatability on these frames. Glyph identities, functions, full-map uniqueness and automatic extraction remain unverified.

### SEMANTIC regions, openings and uncertainty

| Packet | ROOM / UNRESOLVED | Complete / incomplete perimeters | Opening geometry AMBIGUOUS / UNKNOWN | Passage UNKNOWN | Terminal AMBIGUOUS / UNKNOWN |
| --- | ---: | ---: | ---: | ---: | ---: |
| h9v2c | 0 / 3 | 0 / 3 | 3 / 0 | 3 | 0 / 0 |
| k4m7q | 0 / 3 | 0 / 3 | 3 / 0 | 3 | 0 / 0 |
| p6r8t | 4 / 9 | 7 / 6 | 18 / 0 | 18 | 3 / 1 |
| w3j5n | 5 / 7 | 7 / 5 | 18 / 1 | 19 | 0 / 5 |

There are no `ENCLOSED_FEATURE` regions, confirmed passages, connections or terminal rooms. Frame A has three matched `UNRESOLVED` centres, all inside summed radii, with offsets of 3.00, 3.61 and 18.38 px. Both reviewers record three candidate openings under the matched glyphs. k4m7q leaves their opening spans unresolved. Glyph spans are a separate field and are measured. On Frame B the 17 aligned glyph-associated opening candidates all have `UNKNOWN` passage status. Their geometry agrees as `AMBIGUOUS` at 16 glyphs, with one `AMBIGUOUS` versus `UNKNOWN`. Both record a possible break near two exposed trace ends. w3j5n leaves that opening span unresolved and records a second unsupported break on the right with no span. All omitted opening radii accompany omitted spans.

| Stage 3 match · p6r8t / w3j5n | Class pair | Centre difference / summed radius, px |
| --- | --- | ---: |
| r1 / r1 | ROOM / ROOM | 11.18 / 36 |
| r2 / r2 | ROOM / ROOM | 4.47 / 14 |
| r3 / r3 | ROOM / ROOM | 4.24 / 14 |
| r4 / r4 | ROOM / ROOM | 3.61 / 14 |
| r5 / r5 | UNRESOLVED / ROOM | 5.00 / 19 |
| r6 / r6 | UNRESOLVED / UNRESOLVED | 10.05 / 24 |
| r7 / r7 | UNRESOLVED / UNRESOLVED | 3.16 / 17 |
| r12 / r11 | UNRESOLVED / UNRESOLVED | 12.21 / 49 |

Unmatched Stage 3 records are p6r8t r8, r9, r10, r11, r13 and w3j5n r8, r9, r10, r12. All are incomplete unresolved candidates. Across the four matched ROOM pairs, three terminal assessments differ in status (`AMBIGUOUS` vs `UNKNOWN`). The fourth agrees on `UNKNOWN`. All four agree on zero confirmed departures. The r5 class difference comes from a similarly located outline where one reviewer found visible tiled floor and the other judged the dark interior insufficient. Other unmatched centres may denote different portions of partly visible outlines, given the 20 px criterion.

The released pixels and notes show opaque colour over wall bands, scene lighting and mist over some traces, and dark interiors or incomplete perimeters elsewhere. The V2 passage rule requires coherent continuity beyond a colour patch, and the terminal rule requires a confirmed departure and a readable perimeter. The source pixels offer insufficient evidence for those positive claims under the current rules. A verified glyph mapping might resolve some candidates if independently supported for this build. The repeated unknowns coexist with real annotation differences about footprint extents and floor evidence. The results describe what could be supported from these two images. [Native crops, private](../local-data/phase-1-6-1/owner/derived/) · [Semantic rules](ANNOTATION_PROTOCOL_V2.md#semantic-pass)

### Walls and the nearest-eight selection

Both Frame A passes reproduce all eight traces with matching dispositions (six interrupted, two continuous). The longest RAW endpoint discrepancy is 7.62 px with summed radius 14 px. Both Frame B passes match the same two physical traces at the frozen limit. RAW p6r8t w2 / w3j5n w4 has endpoint errors 1.00 and 3.16 px against 11 px summed radii and matching `CONTINUOUS` dispositions. RAW w4 / w7 has errors 1.00 and 2.24 px against 14 px and matching `AMBIGUOUS` dispositions. Their SEMANTIC equivalents are w2 / s5 (1.00 and 2.83 px, summed 12 px, unassigned in both) and w4 / s7 (1.41 and 2.24 px, summed 15 px, assigned to matched ROOM r1 in both). Unmatched walls and each pair’s endpoint errors, dispositions and player-relative offsets are in the derived output.

| RAW wall-union diagnostic | Frame A · h9v2c / k4m7q | Frame B · p6r8t / w3j5n |
| --- | ---: | ---: |
| Exact one-pixel IoU | 5.32% | 0.17% |
| Directional occupancy covered within 3 px | 83.20% / 83.75% | 61.72% / 87.29% |
| Mean nearest distance by direction | 1.89 / 1.89 px | 22.28 / 4.84 px |
| Symmetric Chamfer, average of the two means | 1.89 px | 13.56 px |
| Directional 95th-percentile nearest distance | 5.66 / 5.83 px | 113.60 / 29.77 px |

- **Segmentation.** The release overlay shows p6r8t w1 continuing through the junction where w3j5n splits w1 and w5. The w3j5n spans together cover 100% of p6r8t w1 within 3 px. p6r8t w3 and w7 extend beyond the overlapping w3j5n w6 and w2–w3 portions. This is direct evidence for some split or merged traces.
- **Sample selection.** The capped samples cover 1,032 and 724 raster pixels. Frame B has different midpoint ranks under the two segmentation conventions. Under w3j5n’s splits, w2 and w3 rank first and third at 22.8 and 70.4 px from the fixed midpoint. The much longer corresponding p6r8t w7 ranks seventh at 133.3 px. p6r8t w5 and w8 and w3j5n w8 have zero 3 px coverage from the other sample. On the source overlay these are separate visible runs or a short ambiguous offset. The split convention plus the sample cap plausibly accounts for part of this different selection. The uncapped candidate lists were never recorded, so ranking causality for every omission cannot be recovered.
- **Endpoint localization.** The shared physical traces sit a few pixels apart. The thin-raster exact IoU penalizes parallel shifts much more than a tolerant coverage measure. Small localization differences explain low exact overlap on corresponding runs and are insufficient to explain the large uncovered stretches.
- **Physical geometry.** Both reviewers saw the same source PNG. The overlay supports shared underlying geometry for the collinear runs and identifies differences in how visible lines entered the sample. The short `AMBIGUOUS` offset coincides with a post. The image leaves some offset extent and the interpretation of partially obscured bands unresolved. There is no evidence here for a different layout. [Private source overlay](../local-data/phase-1-6-1/owner/derived/frame-B-wall-review.png)

## Reproduction

From the repository root:

```powershell
python -m research.annotation_retest.evaluate
python -m unittest discover -s tests -v
python -m research.geometry_experiment validate fixtures/synthetic
```

The evaluator uses the Python standard library. It verifies the original-copy bytes on rerun and generates a separate intake and detailed comparison JSON. Point matching uses Euclidean distance. Segment matching uses the endpoint orientation with the lower maximum endpoint error, then lower summed endpoint error if tied. The assignment maximizes cardinality before minimizing summed cost. An equally optimal assignment is reported as ambiguous. Frozen candidate limits are 20 px for matched region centres, 12 px for glyph centres and 15 px at each wall endpoint. Reproducibility limits and summed marking radii are applied after assignment. The relative copy subtracts each annotator’s player point and sums the two player and two feature radii. The raw-wall diagnostic rasterizes the exact union of the recorded segments, counts directional coverage within 3 px and uses inclusive quantiles of nearest-pixel distances. The 3 px value is a diagnostic tolerance. [Evaluator](../research/annotation_retest/evaluate.py) · [Private derived results](../local-data/phase-1-6-1/owner/derived/agreement.json)

All **17 existing tests passed**. The existing synthetic fixture validated with **10 layouts and 39 frames**. NEXT and WP still have zero scored D2R benchmark predictions, and WP anchor and discovery history still require independent confirmation. [Pilot benchmark](PILOT_BENCHMARK_RESULTS.md) · [WP capture protocol](WAYPOINT_CAPTURE_PROTOCOL.md)
