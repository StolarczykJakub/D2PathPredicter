# D2R MapPredictor current status

**2026-11-26 · Phase 1.7.2 qualification complete. Recommendation B for a limited baseline comparison. NEXT and WP remain separately INCONCLUSIVE.** The independent evaluator qualified `mapa-03`, `mapa-05` and `mapa-10` for a target-blind exploratory evaluation. The fixed `mapa-08` image was captured after departure from the landing and its current-player outline was unreadable. All four remain in the qualification record. The historical recording series has incomplete access provenance. The execution lock verified before evaluator access. [Qualification report](NEXT_EVALUATION_QUALIFICATION.md)

- `mapa-01`, `mapa-02` and `mapa-07` remain the development set. Method A is ready. B preserves `UNKNOWN` because the entrance orientation is unresolved, and C lacks qualifying Stage 0 query geometry. The approved phase produced zero scored predictions. [Method readiness](NEXT_EVALUATION_QUALIFICATION.md#method-readiness)
- The next owner decision is whether to approve locked A-only scoring. The baseline needs no additional gameplay footage or blind Stage 0 annotations. All 46 tests passed, the synthetic validator accepted 10 layouts and 39 frames, and the historical artifacts verified without rescoring. [Next action and verification](NEXT_EVALUATION_QUALIFICATION.md#minimum-remaining-work-and-recommendation)

## Phase 1.6.5 final representation holdout

**2026-11-26 · Phase 1.6.5 complete. Frozen advancement gate INCONCLUSIVE.** All six blind returns passed validation, and both visibility witnesses were confirmed in all eight operational moved comparisons. Each pair shared 8 of 10 and 19 observed glyphs and fell below the frozen 13-correspondence count floor. Zero moved pairs qualified for the strict versus partial recovery comparison. [Final results](FINAL_REPRESENTATION_RESULTS.md)

- All three methods recovered 6/6 same-frame slots and returned no match in 8/8 moved slots. Each had zero compatible wrong candidates in 44 negative slots, zero false unique results in 16 queries and zero budget stops. The lock, original returns and historical artifacts verified. All 41 tests passed and the synthetic validator accepted 10 layouts and 39 frames. [Evaluation protocol](FINAL_REPRESENTATION_PROTOCOL.md) · [Run verification](FINAL_REPRESENTATION_RESULTS.md#reproduction-and-preservation)
- The representation-only track is closed. A small direct NEXT pilot is proposed for owner review, contingent on verified hidden stair bearings on distinct layouts. NEXT and WP remain separately **INCONCLUSIVE**. WP still needs its own verified automap anchor and early visibility. [Strategic decision](FINAL_REPRESENTATION_RESULTS.md#strategic-decision)

## Phase 1.6.4 diagnostic

**2026-11-26 · Phase 1.6.4 diagnostic complete. Recommendation A is to test the frozen partial matcher on a fresh independent holdout, subject to owner approval.** Partial matching preserved 6/6 calibration same-frame pairs and 8/8 calibration moved-view pairs. It recovered 16/16 eligible masked pairs versus strict matching's 8/16, with zero verified false unique results and zero wrong-region candidates in 148 negative slots. Both constellations recovered 34 real pairs overall. Partial gained eight bilateral-deletion fits and lost eight sparse asymmetric development fits. [Diagnostic results](PARTIAL_CONSTELLATION_RESULTS.md)

- Synthetic repeated motifs remained ambiguous. All 36 tests passed, the synthetic validator accepted 10 layouts and 39 frames, and the historical artifacts verified. The diagnostic used two existing real layouts with dependent masks. NEXT and WP feasibility remain separately INCONCLUSIVE. [Project decisions](DECISIONS.md#phase-16-representation-decisions)

## Phase 1.6.3 locked holdout

**The locked representation advancement gate remains FAILED.** All six holdout returns passed validation. At 6 px, marker constellations retained both fully visible region pairs and missed 8/8 changed-player pairs. The 4 px player-relative baseline also missed all eight. [Holdout results](INDEPENDENT_LAYOUT_HOLDOUT_RESULTS.md)

- Registration verified three shared, non-collinear glyphs out of four on each view. Each side had a different fourth glyph due to imposed cropping or a within-window visibility change. Both methods returned zero verified false unique outcomes in 16 queries, zero cross-layout compatible candidates in 24 slots, and zero search-budget stops.
- The original holdout bytes, opening receipt and one-time scored results are preserved. The calibration lock and prior frozen files verified. All 32 tests passed. Synthetic validation accepted 10 layouts and 39 frames.

## Phase 1.6.3 calibration

Calibration selected **4 px** for player-relative markers and **6 px** for marker constellations. All six calibration returns passed validation. [Calibration results](INDEPENDENT_LAYOUT_CALIBRATION_RESULTS.md) · [Read-only lock](../local-data/phase-1-6-3/owner/calibration-lock.json)

- Both selected representations retained 6/6 directed same-frame pairs. The primary constellation also retained 8/8 changed-player pairs with non-collinear 2D support. All six configurations had zero verified false unique outcomes, cross-layout collisions or budget stops on the calibrated sample.
- All 32 tests passed, the synthetic validator accepted 10 layouts and 39 frames, and prior pinned files verified. The lock SHA-256 is `97ce79e547ef756100fe93e0aee838f65500ac893fdae3b0d466181d73e8773a`.

## Phase 1.6.3 packet preparation

Marker constellations are primary, with player-relative markers as baseline. The wall hybrid is suspended. Twelve separate verified ZIPs supported the blind handoff. [Owner handoff](INDEPENDENT_LAYOUT_HANDOFF.md)

| Split · private | Source | Selected source times | Verified repeat-view movement | Largest held-out wall-anchor residual |
| --- | --- | --- | ---: | ---: |
| Development | mapa-07 | Existing Stage 1 observations | Existing evidence | Existing evidence |
| Calibration | mapa-06 | 45.0253 s and 46.0159 s, repeated region. 90.0129 s, distinct region. | 82.93 px | 2.06 px |
| Holdout | mapa-09 | 49.0006 s and 49.8112 s, repeated region. 62.5244 s, distinct region. | 133.67 px | 2.92 px |

- Distinct runs and positive wall patterns distinguish the three layouts in the reviewed recording neighbourhoods. The evaluator registered the selected views with non-glyph wall anchors. The closest distinct-region image windows are 19 px apart on one axis against a combined 12 px transfer allowance. Both repeat-view pairs show shared local geometry and recorded visual obstructions. The motion is verified from registration. The footage does not identify the exact skill input. [Private selection and evidence](../local-data/phase-1-6-3/owner/selection.json) · [Private manifest and registration residuals](../local-data/phase-1-6-3/owner/manifest.json)
- Each reopened ZIP contains exactly `README.txt`, one native `frame.png` and a blank `raw.json` under `marker-raw-v1`. All 12 archives passed CRC, metadata, exact template and image checks. Both packets per view use identical image bytes. Pixels inside the common study window match the source exactly. Outside pixels are masked.
- `python -m research.marker_fingerprint.independent_packets --verify` reverified the 12 archives, frozen hashes and evaluator-side metadata. All 24 existing tests passed, and synthetic validation accepted 10 layouts and 39 frames. Pinned V1 files and returns, V2 return bytes and Stage 1 frozen files verified.
- Calibration and holdout packets used separate cohorts and the same RAW marker guide. [Release folder](../local-data/phase-1-6-3/release/)

## Phase 1.6.2 Stage 1

**Recommendation B · Marker constellations.** The Stage 1 results use only the two frozen development views. [Proof of concept results](MARKER_FINGERPRINT_POC_RESULTS.md)

- All three variants retained the same-frame candidate in 4/4 full views and 40/40 single deletions per pass. All rejected the verified distinct candidate in 1,456/1,456 size-matched controls per pass. Only the constellation recovered the three overlapping registered glyphs after the player position shifted about 448 px. It retained both references when they were compatible.
- The 120 px wall coverage checks passed. Walls added zero verified wrong-candidate removals. The independent-layout screen uses the constellation with player-relative markers as its baseline. [Stage 2 criteria](REPRESENTATION_DECISION.md#2-small-independent-layout-screen-only-if-the-first-stage-passes)
- `python -m unittest discover -s tests -v` passed 24 tests. The synthetic validator accepted 10 layouts and 39 frames. The eight V2 return hashes and pinned V1 files verified, and the marker comparison reproduced deterministically. [Reproduction](MARKER_FINGERPRINT_POC_RESULTS.md#decision-and-reproduction)

## Phase 1.6.1 retest

The official verdict remains **E · INCONCLUSIVE**. The two SEMANTIC-first assignees did RAW first, leaving zero formally eligible counterbalanced pairs. The external 10 px figures reproduced and glyph centres and extents passed in both formats. Stage 0 lacked an arrival-room centre, Stage 3 yielded zero confirmed links or terminal rooms, and Stage 3 RAW walls matched two traces against four required. [Retest results](ANNOTATION_RETEST_RESULTS.md) · [Representation decision](REPRESENTATION_DECISION.md)

## Phase 1.6 pilot

NEXT and WP remain **INCONCLUSIVE**. The real benchmark has no scored comparisons.

- Four blind returns passed intake, were copied byte for byte into the private store and have recorded hashes. Stages 0–2 pass the normalized structural parser. Stage 3's `r01` dead-end record conflicts with its zero declared departures. All four returns lack an entrance centre and orientation. [Annotation validation](PILOT_ANNOTATION_VALIDATION.md)
- NEXT has four target-side eligible checkpoints on one layout. WP has zero because its automap anchor and visibility remain unresolved. The benchmark has zero eligible observations for each target. Both unchanged predictors produced `UNKNOWN` with zero votes in the diagnostic. [Replay results](PILOT_BENCHMARK_RESULTS.md)
- The existing synthetic fixture passed dataset validation with 10 layouts and 39 frames. `python -m unittest discover -s tests -v` passed 17 tests. The real gate probe was rejected with exit code 2 because both dataset splits are required. [Commands and timing](PILOT_BENCHMARK_RESULTS.md#validator-and-timing)
