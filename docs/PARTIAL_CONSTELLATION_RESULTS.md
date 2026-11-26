# Phase 1.6.4 bilateral partial constellation results

**Recommendation A · Advance the frozen partial-correspondence configuration to a fresh independent holdout, subject to owner approval.** Partial matching recovered all 16 eligible masked pairs, including eight bilateral deletions missed by strict matching. It produced zero verified false unique regions and zero compatible wrong-region references across 148 real negative slots. It also lost eight local fits in the highly asymmetric development views. The Phase 1.6.3 advancement gate remains **FAILED**. NEXT and WP remain separately **INCONCLUSIVE**. [Frozen diagnostic protocol](PARTIAL_CONSTELLATION_PROTOCOL.md) · [Phase 1.6.3 holdout result](INDEPENDENT_LAYOUT_HOLDOUT_RESULTS.md)

## Evidence and method

The diagnostic used independently constructed synthetic marker fixtures, four existing development RAW returns from `mapa-07` and six calibration RAW returns from `mapa-06`. The real fixtures contain independently wall-registered observations of Catacombs Level 2 on Normal at fixed native automap zoom. The owner reported D2R 3.4.95032, DWR ROW, Battle.net and arrival from Level 1. The real trial count comes from two physical layouts. The 48 masks reuse eight directed comparisons from one region in the calibration layout. The development crop uses the existing 448×352 px window in 1920×1080 images. There was no static asset or active client dependency. [Development provenance](MARKER_FINGERPRINT_POC_RESULTS.md#scope-and-inputs) · [Calibration provenance](INDEPENDENT_LAYOUT_CALIBRATION_RESULTS.md#intake-and-descriptive-repeatability)

The experimental matcher builds hue-compatible point assignments and links mutually consistent pairs using the locked 6 px vector cap and marking radii. An exhaustive bounded maximal-clique search retains distinct one-to-one assignments. Each assignment proposes a translation from its mean offset. A candidate needs three or more matched markers and at least two-thirds coverage on each side. To resolve in 2D, it also needs 25% of each visible marker bounding box and a corresponding triangle with a baseline of at least 24 px and altitude above the summed marking radii. A lower residual never suppresses another candidate. The evaluator uses independent wall registration and the deterministic masks to verify shared marker identities after matching. [Implementation](../research/marker_fingerprint/partial_match.py) · [Evaluator](../research/marker_fingerprint/evaluate_partial.py)

## Real observations and masks

The table counts correct directed pair recoveries verified against shared marker identities. All listed recoveries included every surviving expected identity. The constellation methods also required 2D support. The denominator in the first column includes below-floor controls.

| Control | Player-relative A · 4 px | Strict B · 6 px | Partial · 6 px |
| --- | ---: | ---: | ---: |
| Development same frame, study window | 4/4 | 4/4 | 4/4 |
| Calibration same frame | 6/6 | 6/6 | 6/6 |
| Calibration moved view | 0/8 | 8/8 | 8/8 |
| Development moved view, full observations | 0/8 | 8/8 | 0/8 |
| Simulated bilateral point removal | 0/8 | 0/8 | 8/8 |
| Simulated independent crops | 0/32 | 8/32 | 8/32 |
| Exactly two shared points, three observations per side | 0/8 | 0/8 | 0/8 |
| Compatible wrong-region references, all real queries | 0/148 | 0/148 | 0/148 |
| Verified false unique regions | 0/72 | 0/72 | 0/72 |

The 148 negative slots include 24 cross-layout slots, 28 full-view within-layout distinct-region slots and 96 masked within-layout distinct-region slots. All six real out-of-corpus queries yielded no-match for all three methods. Of the 32 crop pairs, eight shared seven markers and met the bilateral floor. The remaining 24 shared five markers out of seven and nine, below the two-thirds floor on the larger side. The strict matcher recovered eight of the 16 eligible masked pairs. Partial recovered 16/16 and abstained on all eight two-shared controls. Both constellations recovered 34 correct real pairs overall. The partial rule traded eight sparse development fits for eight bilateral-deletion fits.

| Partial recovery | Matched / visible markers | Matched bounding-box area on each side | Max translation residual |
| --- | --- | --- | ---: |
| Development and calibration same frame | 3/3, 6/6, 9/9 or 11/11 on both sides | 100% and 100% | 2.85 px |
| Calibration moved view | 9/11 and 9/9 | 77.70% and 100% | 4.62 px |
| Bilateral removal | 7/10 and 7/8 | 40.78–50.00% and 66.67–71.39% | 0.81 px |
| Eligible crops | 7/9 and 7/7 | 52.97% and 100% | 0.81 px |

Both directions were tested. The lost full-development fits used 3/3 and 3/17 markers, spanning 100% and 1.81–1.85% of the respective clouds. The full and masked results quantify how the coverage rule trades sparse local recall against stronger bilateral support.

| Real query outcome | Player-relative | Strict | Partial |
| --- | ---: | ---: | ---: |
| Verified sole region in tested corpus | 10 | 26 | 30 |
| No-match abstention | 62 | 46 | 42 |
| Ambiguous regions, ambiguous correspondences, or unresolved alignment | 0 | 0 | 0 |

Partial produced 26 geometry-only unique references and four ambiguous reference lists. In each of the four lists, two separately annotated reference observations had one verified correspondence each to the same physical region. Evaluator labels group these duplicate observations for comparison with the historical region counts. A unique compatible corpus reference is conditional on the supplied candidates. A three-point triangle can support a local alignment even when physical identity remains unresolved. [Per-trial evidence](../local-data/phase-1-6-4/results.json)

## Synthetic controls and screening gate

Partial recovered all nine declared positive controls exactly. The equal-sized bilateral-addition control matched 4/6 markers per side, spanning 29.95% and 29.15% of the observed marker boxes. Strict matching missed that case and the other bilateral positive cases. The repeated-translation reference retained both offsets, `(0, 0)` and `(30, 0)` px. The indistinguishable motif in two labeled regions produced one deliberate wrong-region compatible slot under both constellation methods, with region ambiguity and zero false unique outcomes. The nearly collinear fixture retained three weak assignments and resolved none. One- and two-marker views, area and baseline failures, out-of-corpus geometry, hue disagreement and excessive vector disagreement all abstained. Across 27 partial control queries, the outcomes were nine correct unique, one ambiguous region, two ambiguous correspondence, two unresolved 2D, two unavailable, five no-match and six forced budget stops.

| Prospective requirement | Measured result | Gate |
| --- | --- | --- |
| Preserve eligible full same-frame and calibration moved-view fits | 4/4 development same frame, 6/6 calibration same frame, 8/8 calibration moved | Pass |
| All synthetic positives and ≥80% eligible real masks, including ≥4 more pair recoveries than strict | 9/9 synthetic, 16/16 real masks, eight additional mask recoveries | Pass |
| Zero false unique regions or unverified unique alignments, ≤1 extra real wrong slot, ≤10% incremental ambiguity | Zero false unique regions, zero unverified unique alignments, zero additional wrong slots, 0/30 additional ambiguous region or correspondence outcomes | Pass |
| Repeated motifs remain ambiguous, insufficient geometry abstains, and forced budget stops stay unresolved | Both deliberate repeat controls ambiguous, all eight two-shared real controls abstained, all synthetic abstention checks passed | Pass |
| Zero ordinary or sweep budget stops and ≤100 ms p95 at 24 repeated references | 0/72 real queries, 0/21 ordinary synthetic queries, 0/600 timed repeated-reference calls, 8.822 ms p95 at 24 references | Pass |

## Execution cost

Python 3.11.5 on Windows 10 build 19045, AMD Ryzen 9 5900X. Timings cover parsed geometry through correspondence search with 10 warm-ups and 100 timed calls per query. Peak traced allocation comes from a separate execution and excludes loaded inputs and process working set. The full cohort has 2–4 references per query. The masked cohort has three per query.

| Cohort and method | Timed calls | p50 / p95 ms | Peak traced bytes | Total prefixes / checks / retained | Max pair / query prefixes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full · A | 2,400 | 0.122 / 0.274 | 6,352 | 154 / 4,880 / 10 | 12 / 14 |
| Full · strict | 2,400 | 0.503 / 1.260 | 44,712 | 910 / 11,128 / 26 | 22 / 70 |
| Full · partial | 2,400 | 1.558 / 11.279 | 54,104 | 3,694 / 131,956 / 18 | 122 / 396 |
| Masked · A | 4,800 | 0.108 / 0.221 | 4,736 | 144 / 9,064 / 0 | 1 / 3 |
| Masked · strict | 4,800 | 0.398 / 0.760 | 33,792 | 1,604 / 20,552 / 8 | 18 / 45 |
| Masked · partial | 4,800 | 4.257 / 6.437 | 39,324 | 8,496 / 242,064 / 16 | 89 / 259 |

The repeated-motif sweep used a four-point query and two admissible translations per six-point reference. Prefixes and retained hypotheses are per query. Both constellation methods retained two alignments per reference at every sweep size, and every search completed.

| References | Strict prefixes / retained | Strict p50 / p95 ms | Strict peak bytes | Partial prefixes / retained | Partial p50 / p95 ms | Partial peak bytes |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 15 / 2 | 0.159 / 0.357 | 5,560 | 28 / 2 | 0.291 / 0.500 | 8,200 |
| 2 | 30 / 4 | 0.368 / 0.578 | 8,432 | 56 / 4 | 0.559 / 0.837 | 11,984 |
| 4 | 60 / 8 | 0.582 / 0.885 | 15,312 | 112 / 8 | 1.118 / 1.635 | 21,200 |
| 8 | 120 / 16 | 1.255 / 1.684 | 27,760 | 224 / 16 | 2.444 / 3.357 | 37,384 |
| 16 | 240 / 32 | 2.484 / 3.152 | 36,192 | 448 / 32 | 4.913 / 6.466 | 49,544 |
| 24 | 360 / 48 | 3.654 / 4.362 | 66,736 | 672 / 48 | 7.415 / 8.822 | 73,904 |

With `n` and `m` markers, a pair has up to `nm` graph vertices and `O((nm)²)` adjacency construction time and bit storage. Maximal-clique enumeration is exponential in the worst case. A retained hypothesis with `k` pairs can take `O(k³)` support verification and uses `O(k)` result storage. The five historical ceilings apply, including 100,000 pair prefixes and 600,000 query prefixes. The stress fixture exercising the default hypothesis ceiling saw a 257th assignment, retained 256 and returned unresolved after 1,129 prefixes. Forced prefix limits also yielded unresolved with and without previously retained candidates. Repeated references and real inputs here are small. Production-scale collision, latency and memory behavior remain open.

## Reproduction and limits

The first frozen run exposed two control-bookkeeping errors. Its zero-radius test changed one point and left a valid exact triangle but marked the reference as wrong. That unchanged geometry is now a positive with the exact three expected pairs. A separate negative perturbs all four offsets by distinct amounts at zero uncertainty. The first check also marked a near-collinear result as a failure despite zero resolved hypotheses. The corrected check accepts ambiguity while requiring all candidates to remain unresolved in 2D. Both freezes and result sets are preserved. The matcher, protocol, numerical gates and all real trial records were identical across runs. [Initial freeze](../local-data/phase-1-6-4/initial-before-comparisons.json) · [Initial results](../local-data/phase-1-6-4/initial-results.json) · [Final freeze](../local-data/phase-1-6-4/before-comparisons.json)

```powershell
python -B -m research.marker_fingerprint.evaluate_partial
python -B -m unittest discover -s tests -v
python -B -m research.geometry_experiment validate fixtures/synthetic
python -B -m research.marker_fingerprint.holdout --verify
```

With the approved private inputs available, use `evaluate_partial --freeze` once for a new diagnostic directory. All 36 tests passed. The synthetic dataset validator accepted 10 layouts and 39 frames. Both locked comparators reproduced the archived calibration outcomes, reference ordering and prefix counts. Historical verification matched the frozen artifacts and saved holdout SHA-256 `9a9f3d657edcc50cdc8524d9812680e3c99c3c154af5f84d5f7e83a3f9c839c4` without rescoring. The final diagnostic JSON SHA-256 is `cc89a3108196d99901fb4f39e6f9cc95bc4a14ed9ce2ae7670bf1853ccaa7bcf`. The diagnostic stopped at the recommendation.

Real masks are correlated and reuse marking errors from one calibration region. They cannot estimate a population collision rate or represent genuine visibility changes independently. The synthetic repeat controls show that local glyph geometry can be identical in distinct regions or recur under different translations. The screening result warrants testing this configuration on a fresh holdout after owner approval. Hidden-target prediction utility remains unmeasured for both NEXT and WP.
