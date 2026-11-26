# Phase 1.6.2 marker fingerprint proof of concept

**Recommendation B · Advance marker constellations to the small independent-layout screen, subject to owner approval.** All three representations retained the corresponding view in 4/4 full-view and 40/40 single-marker deletion trials per pass. The constellation was the only variant that recovered all three registered common glyphs across the two player positions, about 448 px apart. It kept both compatible views in those cross-frame trials. Use the simpler player-relative score as the comparison baseline in any approved follow-up. [Frozen experiment protocol](MARKER_FINGERPRINT_POC_PROTOCOL.md) · [Independent-layout proposal](REPRESENTATION_DECISION.md#2-small-independent-layout-screen-only-if-the-first-stage-passes)

## Scope and inputs

The D2R development sample is two 1920×1080 frames from one owner-reported 3.4.95032 DWR ROW Battle.net layout, Catacombs Level 2 on Normal after arrival from Level 1. Four separately reported reviews supplied four RAW and four SEMANTIC returns. The two intended SEMANTIC-first reviewers ran RAW first. SEMANTIC is a sensitivity check with shared session context. Only the frozen JSON, release images and existing evaluator-side registration were required. There are zero independent calibration or evaluation layouts, and no static reference provider was used. Phase 1.6.1's official verdict remains E · INCONCLUSIVE. [Annotation retest and provenance](ANNOTATION_RETEST_RESULTS.md)

The matcher receives player-relative geometry, observed hue groups and marking radii. Walls also use the known screen and crop bounds. Evaluator-only registration and labels determine which outputs count as distinct-region comparisons. A and B below refer to representations unless the table says Frame A or Frame B.

| Variant | Implemented |
| --- | --- |
| A · Player-relative markers | Centres in native axes, observed hue, marker and player radii. One-to-one matching with the player origin held fixed. |
| B · Marker constellations | Directed inter-marker vectors encode distances and relative angles. Enumerates compatible assignments and candidate translation offsets at fixed zoom. Retains native axes and requires a non-collinear triangle for 2D alignment. |
| C · Markers and walls | A with optional wall support from the observed centreline union in a masked 120 px player-relative disk. A provisional shortlist requires positive, bidirectional wall support. |

## Full-view matching and registration

All four full-view cross-frame pairings in each pass are physically overlapping under the existing fixed-zoom registration. The registered player positions differ by 447.59–448.37 px in RAW. Each of the four RAW constellation correspondences aligns the same three registered glyphs to within 1.06–3.24 px. The constellation's query-to-reference translation hypotheses account for this offset, around (+391 to +393, +217 to +219) px from Frame A to B. Reversing the query reverses the shift. The marker-only anchored and hybrid variants retain their same-frame matches and yield zero compatible cross-frame matches at that displacement. The constellation recovered shared geometry after the player moved. The annotations provide no controlled arbitrary-teleport trial. [Existing registration recheck](PILOT_BENCHMARK_RESULTS.md#ground-truth-and-registration)

Lower scores indicate closer geometry under the specified tolerances. In both passes every compatible full-view pair has one correspondence. A and C have four compatible pairs per pass, all same-frame. B has eight, four same-frame and four overlapping cross-frame.

| RAW query | A/C same / cross | B same / cross | B cross minus same |
| --- | ---: | ---: | ---: |
| Frame A · h9v2c | 0.2324 / — | 0.3998 / 0.0000 | −0.3998 |
| Frame A · k4m7q | 0.2324 / — | 0.3998 / 0.3801 | −0.0197 |
| Frame B · p6r8t | 0.3852 / — | 0.1186 / 0.3801 | +0.2615 |
| Frame B · w3j5n | 0.3852 / — | 0.1186 / 0.0000 | −0.1186 |

An incompatible pair has no score or finite margin. The SEMANTIC same-frame scores are 0.1765 and 0.2950 for A/C and 0.2845 and 0.0412 for B, by Frame A and B. SEMANTIC B margins range from −0.1423 to +0.2825. All four B full-view trials per pass retain both references, including when the overlapping reference scores better. The scores are similarity measures. Calibrated probabilities require separate evidence.

## Size and visibility controls

Each pass had 2,796 directed trials, 2,788 eligible, with two references per eligible trial (5,576 logical candidate comparisons per representation per pass). The hybrid reuses the A correspondences. The three-marker control uses all 680 subsets in each B observation and all four query directions. The tested cross-frame match uses three markers on each side. The corresponding independently reviewed same-frame reference stays complete, with 17 marks for B queries. Of the 2,720 size-matched trials, 1,456 were verified distinct under the registration rule, 728 per query frame. All three variants retained the same-frame candidate and excluded the verified distinct candidate in all those trials. The remaining 1,264 size-matched trials overlap on a registered landmark. [Private trial data and correspondences](../local-data/phase-1-6-2/results.json)

Each entry below is per pass, with the same counts in RAW and SEMANTIC. The two-marker row is a subset of deletion and crop trials.

| Query condition | Eligible / attempted | Same-frame compatible A / B / C | Verified distinct controls | B compatible cross-frame candidates |
| --- | ---: | ---: | ---: | ---: |
| Full view | 4/4 | 4 / 4 / 4 | 0 | 4/4 overlapping controls |
| Size-matched three | 2,720/2,720 | 2,720 / 2,720 / 2,720 | 1,456 | 4/1,264 overlapping controls |
| Every single deletion | 40/40 | 40 / 40 / 40 | 0 | 34/40 overlapping controls |
| Contiguous ~25% crop | 16/16 | 16 / 16 / 16 | 4 | 12/12 overlapping controls |
| Contiguous ~50% crop | 8/16 | 8 / 8 / 8 | 4 | 4/4 overlapping controls |
| Two visible markers | 14/14 | 14 / 14 / 14 | 0 | 14/14 overlapping controls |

The 25% crops removed one Frame A marker and three or four Frame B markers. The 50% crops removed two Frame A markers and seven to nine Frame B markers in RAW, and two and eight to nine in SEMANTIC. Directional crops retain all points tied at the specified edge. The eight ineligible cases per pass were one-marker Frame A crops. In every two-marker case, A/C retained a sole reference. B found one pairwise correspondence to each reference and left the 2D alignment unresolved. Simulated deletion and crops leave the player position fixed and give no estimate for actual visual occlusion, changes in zoom, or teleport coverage.

| Outcome among 2,788 eligible trials per pass | A/C RAW | B RAW | A/C SEMANTIC | B SEMANTIC |
| --- | ---: | ---: | ---: | ---: |
| Same-frame compatible | 2,788 | 2,788 | 2,788 | 2,788 |
| Correct unique in the two-reference trial | 2,788 | 2,548 | 2,788 | 2,556 |
| Ambiguous between references | 0 | 58 | 0 | 58 |
| Ambiguous correspondences to one reference | 0 | 40 | 0 | 40 |
| Sole candidate with unresolved 2D alignment | 0 | 142 | 0 | 134 |
| No match | 0 | 0 | 0 | 0 |
| False unique on verified distinct controls | 0/1,464 | 0/1,464 | 0/1,464 | 0/1,464 |
| Wrong-region compatible on verified distinct controls | 0/1,464 | 0/1,464 | 0/1,464 | 0/1,464 |

B retains 2,828 same-frame correspondences and 58 cross-frame correspondences per pass. Every cross-frame correspondence was from the overlapping group, 58/1,324. A and C retain 2,788 same-frame correspondences and zero cross-frame correspondences per pass. The 40 within-reference ambiguous trials for B arise in the three-marker size control. One subset can fit several arrangements, and an approximately collinear triple can support pairwise matches while leaving 2D alignment unresolved. Each reported offset represents one feasible correspondence hypothesis with marking uncertainty. A correct unique outcome means the same-frame counterpart was the sole resolved candidate among the two supplied references. The masks and subsets are reused views from one map. These counts describe the controlled trials. The sample cannot establish fingerprint uniqueness or a population collision rate.

## Wall results and acceptance gates

Synthetic splitting and endpoint reversal reproduced an identical 412-pixel union and 100% coverage in both directions. RAW coverage at 3 px inside the common 120 px window passed in both directions on both frames. The uncropped Stage 3 asymmetry remains. It reflects the different traces admitted by the eight-trace cap in addition to local segmentation and marking differences. The measured coverage concerns recorded wall points. Unrecorded stretches are spatially unknown.

| Pass/frame | Observed points in shared disk | Within 3 px, disk | Within 3 px, entire sampled union |
| --- | ---: | ---: | ---: |
| RAW A | 358 / 351 | 83.24% / 84.05% | 80.76% / 81.82% |
| RAW B | 617 / 595 | 90.60% / 92.27% | 62.02% / 87.02% |
| SEMANTIC A | 359 / 349 | 83.01% / 82.52% | 80.54% / 80.28% |
| SEMANTIC B | 613 / 592 | 92.17% / 94.43% | 63.07% / 88.50% |

The hybrid's shortlist excluded zero verified wrong candidates and dropped zero same-frame candidates. A had no verified wrong-region matches for the walls to resolve. The measured incremental wall requirement therefore fails. These values are player-relative. Phase 1.6.1's earlier wall diagnostic used the native image grid. [Phase 1.6.1 wall diagnostic](ANNOTATION_RETEST_RESULTS.md#walls-and-the-nearest-eight-selection)

| Preregistered check | A | B | C |
| --- | --- | --- | --- |
| Full-view same-frame compatibility, 4/4 RAW and 4/4 SEMANTIC | PASS | PASS | PASS |
| Zero false unique RAW matches on verified distinct controls, 0/1,464 | PASS | PASS | PASS |
| Strict same-region advantage on verified distinct full views | NOT EVALUABLE | NOT EVALUABLE | NOT EVALUABLE |
| Strict same-region advantage on verified distinct size controls, 1,456/1,456 RAW | PASS | PASS | PASS |
| Eligible single-deletion compatibility ≥80%, 40/40 RAW | PASS | PASS | PASS |
| Synthetic split/merge invariance | — | — | PASS |
| Common-window RAW wall coverage ≥75% both ways on both frames | — | — | PASS |
| Incremental wall discrimination without loss of compatible same-frame candidates | — | — | FAIL |

## Execution cost

Python 3.11.5 on Windows 10 build 19045, AMD Ryzen 9 5900X. Execution-only timings cover descriptor construction from parsed RAW data and pair scoring on four directed same-frame and four cross-frame pairs. Ten warm-up and 100 timed repetitions per case gave 400 construction calls and 800 comparisons per variant. Sizes are compact JSON for the measured descriptors. Traced peak is the largest fresh Python allocation peak in a separate run of one corresponding operation, excluding already loaded inputs, the Python process, and the full experiment's trial cache and output.

| Variant | Descriptor bytes, 3 / 17 markers | Build p50 / p95 µs | Pair p50 / p95 µs | Peak traced build / pair, bytes |
| --- | ---: | ---: | ---: | ---: |
| A | 165 / 816 | 20.5 / 38.9 | 13.9 / 157.0 | 2,360 / 5,300 |
| B | 263 / 3,679–3,680 | 87.0 / 194.6 | 59.7 / 501.0 | 16,608 / 17,576 |
| C | 3,280–3,343 / 5,987–6,212 | 348.5 / 968.1 | 4,214.7 / 5,438.8 | 103,912 / 78,192 |

A stores O(m) marker records and takes O(m log m) to sort. B constructs and stores O(m²) directed vectors. Both consider up to mn point pairs initially. The exhaustive one-to-one search can visit permutations of the larger set up to the smaller set's size, with early pruning on hue and geometry. Time and memory rise with repeated features and the number of retained hypotheses. B checks each new point against prior assigned vectors and may examine triples to resolve alignment. A retained correspondence stores O(m) point pairs. C additionally rasterizes O(L) sample steps along annotated lines and stores O(w) union points. Each wall comparison uses up to 29 bounded neighbor probes per occupied point. Image extraction, index sizes beyond two references, and production CPU, RAM and latency remain unmeasured.

## Decision and reproduction

An independent-layout annotation screen is justified for **B**, with A scored as the simpler baseline. A is sufficient for the measured same-player repeatability and size-controlled separation. Its fixed origin could not reuse the verified common glyphs at a substantially changed player position. B resolves that measured limitation and retains ambiguous matches. The next approved screen should test whether that advantage survives unrelated layouts, changed player positions and genuine clipping, counting false unique fits and collisions. The pilot used a static recorded zoom and one layout. It provides no evidence on regional fingerprint uniqueness across layouts. The hybrid costs more in this sample and did not improve candidate discrimination. [Existing independent-layout gate](REPRESENTATION_DECISION.md#2-small-independent-layout-screen-only-if-the-first-stage-passes)

```powershell
python -m research.marker_fingerprint.evaluate
python -m unittest discover -s tests -v
python -m research.geometry_experiment validate fixtures/synthetic
```

The runner reads the eight preserved files and verifies their SHA-256 hashes, the V2 release and frozen protocols, and the pinned V1 files and release archives. The protocol, source and benchmark protocol hashes recorded before comparisons matched after execution. Both non-timing trial replays were identical. All **24 tests passed**, including 17 existing tests and 7 PoC tests. The synthetic validator accepted **10 layouts and 39 frames**. [Pre-comparison hashes](../local-data/phase-1-6-2/before-comparisons.json) · [Evaluator](../research/marker_fingerprint/evaluate.py)

**NEXT feasibility · INCONCLUSIVE.** Zero scored D2R target predictions.

**WP feasibility · INCONCLUSIVE.** Zero scored D2R target predictions. The waypoint anchor and discovery history still require independent verification. [WP capture protocol](WAYPOINT_CAPTURE_PROTOCOL.md)

Stage 1 is complete. Stage 2 annotation and later project phases require separate owner approval.
