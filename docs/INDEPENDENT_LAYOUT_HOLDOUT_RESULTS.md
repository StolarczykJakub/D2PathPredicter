# Phase 1.6.3 locked holdout evaluation

**The primary representation failed the frozen advancement gate.** At the locked 6 px cap, marker constellations matched both fully visible region pairs in both review directions, then returned no match in **all eight** changed-player pairings. Wall registration confirms three shared, non-collinear glyphs. Each view also contains a different fourth glyph. The locked rule requires a full assignment of the smaller set, which in this case means all four. The 4 px player-relative baseline also missed every moved-view pairing. [Frozen screen plan](INDEPENDENT_LAYOUT_SCREEN_PLAN.md)

## Lock and intake

The read-only calibration lock's SHA-256 was verified before opening the archive and again after scoring. It is `97ce79e547ef756100fe93e0aee838f65500ac893fdae3b0d466181d73e8773a`. The preflight verified calibration and development inputs, eligibility and matching rules, tolerance caps, candidate rosters, search budgets, exact evaluator and test files, release packets, and the hashes of the holdout packet manifest and evaluator labels. It also recomputed the wall-anchor registrations from the frozen selection. The separate opening receipt records **2026-11-26 15:59:48 CET (Europe/Warsaw)**, or **14:59:48 UTC**. [Calibration lock](../local-data/phase-1-6-3/owner/calibration-lock.json) · [Opening receipt](../local-data/phase-1-6-3/owner/holdout/opening.json)

All six returns passed `marker-raw-v1` validation, including field shapes, statuses, unique glyph IDs, player and glyph coordinates inside the unmasked native window, radii, and timing and search flags. Packet IDs and frame hashes match the owner manifest. The archive, supplied intake manifest and six original JSONs were preserved byte for byte. Each JSON's size and SHA-256 match the supplied intake manifest. Every reviewer reported a complete window search and no time-limit hit. Reviewer IDs, dispatch and receipt timestamps, and exposure or deviation records were unavailable. [Saved intake and results](../local-data/phase-1-6-3/owner/holdout/results.json)

The owner-reported capture is D2R 3.4.95032, DWR ROW, Battle.net, Normal Catacombs Level 2. The holdout was `mapa-09`. Out-of-corpus references were the four frozen `mapa-07` development observations, filtered to the same support window, with 3, 3, 6 and 6 glyphs. The `mapa-06` calibration returns were verified for integrity. The matcher received only glyph geometry, appearance groups, marking radii and, for the baseline, annotated player offsets. Layout and region IDs and wall registrations were used for evaluation after matching. [Private selection and labels](../local-data/phase-1-6-3/owner/selection.json)

## Outcomes under the two locked caps

Each representation completed 16/16 queries and 58/58 directed candidate comparisons, with zero ineligible queries or pairs. There were six same-frame counterpart pairs, eight changed-player pairs, 20 verified distinct-region candidate slots within the holdout layout, and 24 cross-layout slots against development. The 20 within-layout slots include repeated directed controls from the two query types.

| Measure | A · Player-relative, 4 px | B · Constellations, 6 px |
| --- | ---: | ---: |
| Same-frame counterpart compatibility | 6/6 | 6/6 |
| Changed-player compatibility | 0/8 | 0/8 |
| Correct unique region queries | 6/16 | 6/16 |
| Ambiguous region sets | 0/16 | 0/16 |
| Ambiguous correspondences within one region | 0/16 | 0/16 |
| Wrong-region compatible candidates within holdout | 0/20 | 0/20 |
| Cross-layout compatible candidates | 0/24 | 0/24 |
| Verified false unique results | 0/16 | 0/16 |
| No-match queries | 10/16 | 10/16 |
| Out-of-corpus no-match queries | 6/6 | 6/6 |
| Unresolved 2D query outcomes | No 2D transform estimated | 0/16 |
| Unavailable alignments | 0/16 | 0/16 |
| Search-budget stops | 0/16 | 0/16 |

The same-frame counterpart was the sole compatible reference in each of the six successful queries, yielding one physical region per query. The four moved queries each offered two reviewer references to the same physical region and two references to the other region. None of those references was compatible. A moved-view no-match is a failure to retain the known region. The six out-of-corpus no-matches are valid abstentions. The absence of collisions describes only the tested candidates from these layouts.

### Per-case outcomes

The outcome in each cell applies to both A and B. The private result preserves every candidate slot, its prefixes and checks, retained hypotheses, and any similarity scores. All successful cases had one hypothesis per candidate and no finite wrong-candidate margin. [Per-candidate results](../local-data/phase-1-6-3/owner/holdout/results.json)

| Query packet | Physical view | Same-frame outcome | Changed-player outcome | Against development |
| --- | --- | --- | --- | --- |
| `28b18eccd3` | Region 1 | Correct unique via `3b64fdaa08` | 0/2 correct references compatible | No match, 0/4 |
| `3b64fdaa08` | Region 1 | Correct unique via `28b18eccd3` | 0/2 correct references compatible | No match, 0/4 |
| `a1ffbf5c78` | Moved Region 1 | Correct unique via `b97006605e` | 0/2 correct references compatible | No match, 0/4 |
| `b97006605e` | Moved Region 1 | Correct unique via `a1ffbf5c78` | 0/2 correct references compatible | No match, 0/4 |
| `0f649f0e1f` | Region 2 | Correct unique via `dc31afa2fa` | — | No match, 0/4 |
| `dc31afa2fa` | Region 2 | Correct unique via `0f649f0e1f` | — | No match, 0/4 |

Same-frame native-centre agreement was **4/4** for Region 1, **4/4** for moved Region 1 and **5/5** for Region 2, each with maximum disagreement **1.00 px** and no tied assignment. In all six successful directed matches, each representation used all 4 or 5 glyphs on both sides and covered **100% of both visible marker bounding boxes**. B had non-collinear 2D support in all six. No moved-view or cross-layout candidate produced a locked coverage measurement because no match was retained.

## Why the moved-view comparisons failed

Independent wall anchors measured the player displacement at **133.67 px** against a **28 px** summed allowance. The maximum held-out wall-anchor residual was **2.92 px**. Across the four reviewer combinations, the geometry registered independently of the matcher identifies the same three shared glyphs on both sides. The three span **3/4 glyphs per view (75%)**, **21.81–22.05%** of the original view's recorded marker bounding box and **32.90%** of the moved view's. All four shared triples support 2D alignment. The maximum registered centre difference is **1.58 px** and the maximum shared directed-vector difference is **1.41 px**, within the locked 6 px cap and stated marking radii. The table reports geometric diagnostics on the frozen returns. No subset was submitted to the locked matcher.

| Original review | Moved review | Registered shared | Max centre / vector difference | Locked B in both directions |
| --- | --- | ---: | ---: | --- |
| `28b18eccd3` | `a1ffbf5c78` | 3/4 and 3/4 | 0.71 / 1.00 px | No match |
| `28b18eccd3` | `b97006605e` | 3/4 and 3/4 | 1.58 / 1.41 px | No match |
| `3b64fdaa08` | `a1ffbf5c78` | 3/4 and 3/4 | 0.71 / 1.00 px | No match |
| `3b64fdaa08` | `b97006605e` | 3/4 and 3/4 | 0.71 / 0.00 px | No match |

- The original-only glyph at `(803, 453)` projects to `(707.5, 360.5)` in the moved frame. It is visible in the uncropped source. The imposed window masks it, with its projected centre 28.5 px beyond the left boundary.
- The moved-only glyph at `(993, 537)` projects to `(1088.5, 629.5)` in the original frame, inside the imposed window. The earlier source has no discernible corresponding automap trace or glyph at that position. This is a change in visible evidence within the window. The precise cause of the visibility change is unverified. [Private pixel review](../local-data/phase-1-6-3/owner/holdout/crop-and-reveal-review.png)

B is translation invariant over the supplied shared geometry. Its all-of-smaller-set support rule cannot accommodate one different glyph on **each** side of equally sized visible sets. This explains the failure despite repeatable marks and a tight shared triple. The baseline additionally holds the player origin fixed. The zero budget stops and completed candidate searches rule out truncation as an explanation.

## Frozen advancement gate

| Primary B gate | Observed | Result |
| --- | --- | --- |
| Fully visible Region 1 counterpart | 2/2 directed pairs compatible | PASS |
| Fully visible Region 2 counterpart | 2/2 directed pairs compatible | PASS |
| Changed-player compatibility with non-collinear 2D support | 0/8 directed pairs retained | **FAIL** |
| Zero verified false unique results | 0/16 evaluable queries | PASS |
| Representation advancement | One required condition failed | **FAIL** |

## Computational cost

The locked evaluator performed one classified pass. The established timing harness separately measured 1,600 executions per representation from parsed geometry, ten warm-ups and 100 measurements for each of the 16 query rosters with 3–4 references. Timings include candidate testing and descriptor work in the locked search. The host ran Windows 10 and Python 3.11.5. Image extraction and production runtime were outside the measurement.

| Representation | Query p50 / p95 | Peak Python traced bytes | Total / max query / max pair prefixes | Retained hypotheses |
| --- | ---: | ---: | ---: | ---: |
| A · 4 px | 0.035 / 0.072 ms | 5,392 | 84 / 8 / 6 | 6 |
| B · 6 px | 0.096 / 0.228 ms | 10,304 | 177 / 17 / 10 | 6 |

## Decision and next experiment

**Investigate partial overlap when both views contain unmatched glyphs.** A focused, owner-approved follow-up would use synthetic and existing development and calibration data to test a bounded, translation-only partial-correspondence diagnostic against paired controls. Include cases with distinct missing glyphs on each side, repeated non-collinear motifs from different regions, and insufficient support. Freeze minimum matched geometry, coverage on both sides, and ambiguity and abstention handling before testing. The diagnostic must retain valid shared geometry while keeping competing fits visible and avoiding verified false unique matches. Reserve a fresh independent holdout before any confirmatory test of a changed rule.

Same-frame geometry proved repeatable on the held-out layout. Neither variant demonstrated robust matching after both sides' observable sets changed. Local motif compatibility alone is insufficient evidence for unique map identity or an unseen target bearing. A separate NEXT-only protocol can address predictive information when the representation is ready. Its target eligibility is independent of WP's unresolved anchor and discovery history. **NEXT feasibility remains INCONCLUSIVE. WP feasibility remains INCONCLUSIVE.**

## Reproduction and audit

The recorded command was `python -m research.marker_fingerprint.holdout`. The runner consumes the immutable lock, records the opening receipt first, and rejects a second scored run. The saved results SHA-256 is `9a9f3d657edcc50cdc8524d9812680e3c99c3c154af5f84d5f7e83a3f9c839c4`. The verification mode reads the saved evidence and frozen inputs without scoring.

```powershell
python -m research.marker_fingerprint.holdout --verify
python -m unittest discover -s tests -v
python -m research.geometry_experiment validate fixtures/synthetic
```

All **32 tests passed**. Synthetic validation accepted **10 layouts and 39 frames**. The calibration lock, prior frozen V1/V2/Stage 1 artifacts, source frames and all 12 release packets verified. [Completion record](../local-data/phase-1-6-3/owner/holdout/completion.json) · [Project decision record](DECISIONS.md#phase-16-representation-decisions)
