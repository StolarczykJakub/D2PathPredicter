# Phase 1.6.3 calibration and evaluation lock

**Calibration passed for the primary representation.** The frozen selection rule chose **A · Player-relative markers at 4 px** and **B · Marker constellations at 6 px**. The holdout annotation archive remains sealed. Phase 1.6.1 remains E · INCONCLUSIVE, and NEXT and WP feasibility remain separately INCONCLUSIVE. [Frozen screen plan](INDEPENDENT_LAYOUT_SCREEN_PLAN.md)

## Intake and descriptive repeatability

All six calibration returns passed archive integrity, supplied byte-count and SHA-256 checks, packet/frame identity checks against the release, and full `marker-raw-v1` validation. The validator checked unique glyph IDs, allowed statuses, status/evidence consistency, the unmasked native coordinate bounds, finite marking radii, time limit and completeness flags, and notes. Original bytes and the supplied intake manifest are preserved in the private calibration store. Reviewer IDs, dispatch and receipt times, and exposure or deviation records were unavailable. All six reported complete searches and no time-limit hit. The two moved-view returns each omit one obscured glyph span while retaining a supported centre. [Private intake and results](../local-data/phase-1-6-3/owner/calibration/results.json)

The external figures reproduced by one-to-one native-centre assignment with the V2 12 px descriptive pairing limit. There were no tied assignments. These are annotation-agreement measurements.

| Same-image reviews | Corresponding glyphs | Maximum centre disagreement |
| --- | ---: | ---: |
| Region 1 | 11/11 | 0 px |
| Moved Region 1 | 9/9 | 1.41 px |
| Region 2 | 9/9 | 0 px |

The only calibration layout is `mapa-06`. The out-of-corpus reference set uses the four `mapa-07` development RAW observations filtered to the frozen study window, with 3, 3, 6 and 6 eligible glyph centres. The six calibration views contain 9–11 centres. The source is owner-reported D2R 3.4.95032, DWR ROW, Battle.net, Normal Catacombs Level 2. The comparison is offline and uses glyph geometry and marking uncertainty. [Source and evaluator metadata](../local-data/phase-1-6-3/owner/manifest.json)

## All six calibration configurations

Each row covers 16/16 evaluable queries and 58/58 eligible directed candidate comparisons. The roster has six same-frame counterpart pairs, eight changed-player pairs, 20 verified distinct-region candidate slots within calibration, and 24 cross-layout candidate slots against development. Some wrong-region references occur in both within-layout comparison types. The false-unique denominator is the 16 completed queries.

| Representation | Cap | Same-frame compatible | Changed-player compatible | Within-layout wrong compatible | Cross-layout collisions | False unique |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | **4 px** | 6/6 | 0/8 | 0/20 | 0/24 | 0/16 |
| A | 6 px | 6/6 | 0/8 | 0/20 | 0/24 | 0/16 |
| A | 8 px | 6/6 | 0/8 | 0/20 | 0/24 | 0/16 |
| B | 4 px | 6/6 | 0/8 | 0/20 | 0/24 | 0/16 |
| B | **6 px** | 6/6 | 8/8 | 0/20 | 0/24 | 0/16 |
| B | 8 px | 6/6 | 8/8 | 0/20 | 0/24 | 0/16 |

All six configurations had zero ambiguous regions, ambiguous correspondences, unresolved 2D outcomes, unavailable results and search-budget stops. Each A configuration and B at 4 px yielded six correct unique queries and ten no-matches. B at 6 and 8 px yielded ten correct unique queries and six no-matches. All six out-of-corpus queries abstained for every configuration.

Every successful same-frame pair used all 9 or 11 glyphs on both sides and spanned 100% of both visible marker bounding boxes. At 6 and 8 px, B's changed-player matches used all **9/9** moved-view glyphs and **9/11** primary-view glyphs. The supported geometry spanned **100%** of the moved-view marker box and **77.70%** of the primary-view marker box. All eight directed pairs supported a non-collinear 2D alignment. The largest centre discrepancy after independent wall registration was **4.12 px**. Each compatible directed pair had one correspondence, and the two reviewer references in a moved-view query both supported the same physical region. These local subset fits measure coverage of the recorded glyphs. [Per-query candidates, correspondences and coverage](../local-data/phase-1-6-3/owner/calibration/results.json)

A's caps tied on the six compatible controls and zero wrong-region matches, so the smaller cap won. A's moved-view abstentions are a measured limitation of the comparison baseline. For B, 6 and 8 px both retained all 14 directed same-region controls and tied at zero wrong-region candidates, so 6 px won. B at 4 px retained only the six same-frame controls. All required primary pairs were evaluable and supported at the selected cap. These results come from one calibration layout and one development layout. They establish neither a population collision rate nor novel-layout accuracy.

## Execution cost and bounds

Timings are per query over the calibration roster of 3–4 references, from parsed geometry on Windows 10 and Python 3.11.5. Each row has 1,600 calls after ten warm-ups per query case. Peak traced allocation is for a single execution. Image extraction, process working set and production runtime were outside the measurement.

| Configuration | p50 / p95 | Peak traced bytes | Max pair / query prefixes |
| --- | ---: | ---: | ---: |
| A 4 px | 0.124 / 0.186 ms | 6,624 | 12 / 14 |
| A 6 px | 0.123 / 0.185 ms | 6,352 | 12 / 14 |
| A 8 px | 0.124 / 0.190 ms | 6,352 | 12 / 14 |
| B 4 px | 0.459 / 0.815 ms | 43,960 | 22 / 54 |
| B 6 px | 0.490 / 0.870 ms | 46,512 | 22 / 70 |
| B 8 px | 0.479 / 0.858 ms | 47,376 | 22 / 70 |

At the frozen 8 px diagnostic cap, the synthetic reference sweep used one triangle query and two repeated translated copies per reference. It had zero truncations.

| References | A prefixes / hypotheses | A p50 / p95 | B prefixes / hypotheses | B p50 / p95 |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 4 / 1 | 0.017 / 0.019 ms | 11 / 2 | 0.106 / 0.215 ms |
| 2 | 8 / 2 | 0.033 / 0.080 ms | 22 / 4 | 0.199 / 0.322 ms |
| 4 | 16 / 4 | 0.064 / 0.114 ms | 44 / 8 | 0.392 / 0.575 ms |
| 8 | 32 / 8 | 0.126 / 0.181 ms | 88 / 16 | 0.786 / 0.962 ms |
| 16 | 64 / 16 | 0.256 / 0.319 ms | 176 / 32 | 1.664 / 1.851 ms |
| 24 | 96 / 24 | 0.406 / 0.545 ms | 264 / 48 | 2.451 / 2.988 ms |

The new evaluator uses the exact ceilings of 24 markers per view, 24 references per query, 100,000 prefixes per pair, 256 retained hypotheses per pair and 600,000 prefixes per query. A prefix count includes the root. Synthetic stress tests reached both prefix ceilings and observed a 257th complete hypothesis while retaining 256. In each truncated case the query outcome was unresolved, including cases with a retained partial candidate and cases with none. Tests also covered unrelated and repeated motifs, bounded versus Stage 1 parity at 8 px, and insufficient point or 2D support. [Bounded evaluator](../research/marker_fingerprint/bounded_match.py) · [Tests](../tests/test_bounded_match.py)

## Lock and next authorized action

The write-once lock is read-only and its SHA-256 is `97ce79e547ef756100fe93e0aee838f65500ac893fdae3b0d466181d73e8773a`. It records the selected caps, input hashes, sealed holdout packet-manifest and evaluator-label hashes, candidate rosters, match and eligibility rules, search budgets, exact source and test hashes, and the calibration decision and results digest. All six scoring configurations reproduced exactly apart from execution timings. [Private calibration lock](../local-data/phase-1-6-3/owner/calibration-lock.json)

`python -m unittest discover -s tests -v` passed **32 tests**. `python -m research.geometry_experiment validate fixtures/synthetic` accepted **10 layouts and 39 frames**. Pinned V1 files, V1 originals and frozen copies, V2 returns, Stage 1 artifacts, and all 12 Phase 1.6.3 **release** packets verified. The holdout annotation archive's contents were never opened.

After separate owner approval, verify the lock, pinned code and holdout packet/label hashes before accessing holdout returns. Record the opening time separately from the immutable lock. Preserve and validate the six holdout returns, then run the frozen holdout roster once at A 4 px and B 6 px. Report both fully visible region pairs, the changed-player overlap, collisions and false unique outcomes under the existing advance criteria. [Holdout comparators and acceptance criteria](INDEPENDENT_LAYOUT_SCREEN_PLAN.md#acceptance-criteria)
