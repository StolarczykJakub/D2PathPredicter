# Phase 1.6.5 final locked representation evaluation

**INCONCLUSIVE.** The six same-frame comparisons passed for all three representations. Both independent visibility witnesses were confirmed on all eight directed moved-view comparisons. All eight fell below C's frozen count floor, leaving no eligible moved comparisons in either direction to test partial versus strict recovery. The final representation-only holdout is closed. NEXT and WP remain separately **INCONCLUSIVE**. [Frozen protocol](FINAL_REPRESENTATION_PROTOCOL.md)

This is independently annotated D2R recording evidence from one physical layout and one moved-view event. The source is the owner's `mapa-04` footage, reported as D2R build 3.4.95032 DWR ROW, Battle.net, Normal, Catacombs Level 2 entered from Level 1. The offline run used three native screenshot windows and the four pinned windowed development observations from `mapa-07`. Calibration `mapa-06` remained calibration evidence. Matching required no game client, installed game assets or static generator. Layout distinctness rests on the recording provenance and visible wall geometry in the reviewed neighbourhoods. [Preparation and provenance](FINAL_REPRESENTATION_PREPARATION.md) · [Benchmark protocol](../benchmarks/PROTOCOL.md)

## Integrity and intake

The read-only evaluation lock matched the owner-specified SHA-256 `877fc9c32533691f623332acb48749811b8274c5b5aa04ebdcd56fe80fd5e8c6` before opening. Verification covered the recording and native sources, study windows and release packets, evaluator labels and wall registration, the 24 pinned files, the prior diagnostic snapshots, calibration and development data, matcher configurations and search budgets, and the exact opaque-ID roster. The opening receipt records **2026-11-26 18:09:44 CET (Europe/Warsaw)**, or **17:09:44 UTC**, in a separate file. [Evaluation lock](../local-data/phase-1-6-5/owner/evaluation-lock.json) · [Opening receipt](../local-data/phase-1-6-5/owner/holdout/opening.json)

The supplied archive, intake manifest and six original JSON byte streams were preserved in the private holdout directory. The 8,502-byte archive's SHA-256 is `8e761812de1bd19ea97e8544c09010d7a1af98b8fa4a2ce230f4f72a9675a652`. The intake manifest's SHA-256 is `07c93a757a8d8c4fca8a22cd3ad3cb0cabbf1135b3d93b796013b36cab15dad0`. ZIP roster and CRC passed. Each return matched its declared byte count and SHA-256, released packet ID and frame hash. All six passed the complete `marker-raw-v1` validator, including native canvas and study-window bounds for observed player positions, centres and endpoints. All six declared complete searches and observed players, with zero time-limit hits. Each revisit reviewer reported one readable centre with an obstructed, unreadable span. [Intake with per-return hashes and notes](../local-data/phase-1-6-5/owner/holdout/intake.json) · [Marker RAW contract](INDEPENDENT_LAYOUT_ANNOTATOR_GUIDE.md)

The owner supplied the actual independent returns for the six intended sessions. Reviewer and session IDs, dispatch, receipt and handoff times, and exposure and deviation records are unknown. No independence breach was reported. The supplied intake log describes metadata validation and same-frame centre agreement only, with no matcher execution. All operational counts were set before matching. [Pre-match record](../local-data/phase-1-6-5/owner/holdout/intake-and-eligibility.json)

## Descriptive annotation agreement

The existing same-frame centre assignment over observed glyphs reproduced the external counts and maxima. It uses a 12 px distance bound and returned zero tied assignments.

| View | Review packets | Centres paired | Maximum separation |
| --- | --- | ---: | ---: |
| Primary `r1` | `0176b827c2` / `93f1396654` | 10/10 | 1.414 px |
| Revisit `r1b` | `63e3850229` / `f26adb61ba` | 19/19 | 1.414 px |
| Distinct region `r2` | `1dcc1ff640` / `b3b8fc8f4e` | 6/6 | 1.000 px |

Both primary reviewers recorded a clipped yellow glyph near the upper study-window edge and marked the centre of its visible portion. The same-frame comparison describes repeatability. The separate evaluator checks below establish the visibility evidence. [Descriptive and evaluator audit](../local-data/phase-1-6-5/owner/holdout/intake-and-eligibility.json)

## Independent visibility and eligibility

The locked wall translations into the late reference plane are `r1 = (−79, +42)`, `r1b = (−9, −30)` and `r2 = (−642, −210)` native px. Player displacement was 100.42 px against a 20 px combined allowance. The distinct-region study window is separated from the two registered repeat windows by 115 px and 185 px. Shared identities use reciprocal unambiguous centres of equal known hue within 8 px after translation. All six same-frame and eight moved slots were operational and had available, unambiguous identity labels. The matcher received marker geometry and uncertainty, with observed player-relative geometry for A. The evaluator kept the physical-region labels, visibility witnesses, truth correspondences and wall shifts. [Locked labels](../local-data/phase-1-6-5/owner/manifest.json) · [Per-slot identity indices](../local-data/phase-1-6-5/owner/holdout/intake-and-eligibility.json)

| Witness | Locked registered site | Owner-side positive evidence | Opposite-side and recording evidence |
| --- | --- | --- | --- |
| Primary visible, revisit cursor-covered | Yellow at (1084, 409) | Exactly one in each primary return. `0176b827c2` at (1163, 366), 1.000 px away. `93f1396654` at (1164, 366), 1.414 px away. Both refer to the clipped visible portion. | Zero same-hue centres within 8 px in either revisit review. The recording shows the glyph immediately before the native cursor crosses and covers it at the revisit frame. |
| Revisit visible, primary undrawn | Yellow at (1023, 534) | Exactly one in each revisit return. Both at (1031, 563), 1.414 px away. | Zero same-hue centres within 8 px in either primary review. The primary frame lacks the wall and glyph at the transferred in-window site (1102, 492). Both are visible on the revisit and in the later wall reference. |

Both witness rules passed in every reviewer combination and direction, making **8/8 genuine bilateral moved slots**. The mechanisms come from the recording and wall registration. [Locked visibility evidence](../local-data/phase-1-6-5/owner/review/bilateral-visibility-evidence.png) · [Returned centre audit](../local-data/phase-1-6-5/owner/holdout/intake-and-eligibility.json)

### All eight operational moved slots

Each row has eight independently verified shared identities and reliable corresponding triangle support. C requires at least three correspondences, two-thirds count coverage and 25% bounding-box area on both sides, and a reliable corresponding triangle with a baseline of at least 24 px and altitude above the summed radii in each view. All eight rows require **13** correspondences by count, even though the smaller view has **10** observed markers. All eight had a completed search that returned no match under A, B and C. The percentages below come from the verified shared geometry. The matchers admitted zero correspondences on each row.

| Query → reference | Shared counts (query / reference) | Shared area (query / reference) | Floor failures | A / B / C |
| --- | --- | --- | --- | --- |
| `0176b827c2` → `63e3850229` | 8/10 (80.00%) / 8/19 (42.11%) | 30.44% / 24.87% | Count and area | No match / no match / no match |
| `0176b827c2` → `f26adb61ba` | 8/10 (80.00%) / 8/19 (42.11%) | 30.44% / 25.04% | Count | No match / no match / no match |
| `93f1396654` → `63e3850229` | 8/10 (80.00%) / 8/19 (42.11%) | 30.56% / 24.87% | Count and area | No match / no match / no match |
| `93f1396654` → `f26adb61ba` | 8/10 (80.00%) / 8/19 (42.11%) | 30.56% / 25.04% | Count | No match / no match / no match |
| `63e3850229` → `0176b827c2` | 8/19 (42.11%) / 8/10 (80.00%) | 24.87% / 30.44% | Count and area | No match / no match / no match |
| `63e3850229` → `93f1396654` | 8/19 (42.11%) / 8/10 (80.00%) | 24.87% / 30.56% | Count and area | No match / no match / no match |
| `f26adb61ba` → `0176b827c2` | 8/19 (42.11%) / 8/10 (80.00%) | 25.04% / 30.44% | Count | No match / no match / no match |
| `f26adb61ba` → `93f1396654` | 8/19 (42.11%) / 8/10 (80.00%) | 25.04% / 30.56% | Count | No match / no match / no match |

Moved denominators are 8 planned, 8 operational, 8 unambiguously labeled, 8 genuine bilateral, 8 with reliable triangles, 4 at the area floor, 0 at the count floor, 0 at the combined floor and 8 below floor. Each direction has four operational and bilateral slots and zero floor-eligible slots. The six same-frame slots all passed the combined floor across all three views. Their verified overlaps were 10/10, 19/19 and 6/6 in each direction, with full area coverage and reliable triangles. [Eligibility and triangle indices](../local-data/phase-1-6-5/owner/holdout/intake-and-eligibility.json)

## Matching outcomes

The frozen run evaluated **16 queries and 58 candidate slots per method** once: six same-frame queries with 18 slots, four moved queries with 16 slots, and six out-of-corpus queries with 24 slots. There were 14 expected positives and 44 negative slots, including 20 distinct-region slots from the holdout layout and 24 cross-layout slots against `mapa-07`. All searches completed. [Full roster and all comparison rows](../local-data/phase-1-6-5/owner/holdout/results.json)

| Outcome | A · player-relative, 4 px | B · strict, 6 px | C · partial, 6 px |
| --- | ---: | ---: | ---: |
| Expected same-frame slots compatible / verified exact | 6/6 / 6/6 | 6/6 / 6/6 | 6/6 / 6/6 |
| Same-frame slots with verified resolved 2D alignment | Uses observed player anchor | 6/6 | 6/6 |
| Expected moved slots compatible / verified exact | 0/8 / 0/8 | 0/8 / 0/8 | 0/8 / 0/8 |
| Verified resolved 2D moved slots | Uses observed player anchor | 0/8 | 0/8 |
| Distinct-region slots compatible | 0/20 | 0/20 | 0/20 |
| Cross-layout slots compatible | 0/24 | 0/24 | 0/24 |
| Correct unique regions after grouping review duplicates | 6/16 | 6/16 | 6/16 |
| False unique regions / unique with unverified support | 0/16 / 0/16 | 0/16 / 0/16 | 0/16 / 0/16 |
| Ambiguous references / within-reference correspondences / labeled regions | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Compatible unresolved alignments | 0 | 0 | 0 |
| Completed no-match queries | 10/16 | 10/16 | 10/16 |
| Budget / input abstentions | 0 / 0 | 0 / 0 | 0 / 0 |

Each of the six retained hypotheses per method exactly matched the independent same-frame identities, with admitted counts of 10, 19 and 6 by view and 100% count and area coverage on each side. B and C verified two-dimensional correspondence in those six slots. A compared offsets around the observed player. The six correct unique outcomes per method apply to the labeled regions in this roster. All four moved queries and all six out-of-corpus queries returned no match. C's eight below-floor positive slots are appropriate no-match outcomes with zero geometry recoveries. Its count precheck completed those pairs with zero prefix expansion because 13 correspondences cannot fit into 10 observations. The evaluator's independently registered overlap remains observable on all eight slots. [Saved hypotheses and stops](../local-data/phase-1-6-5/owner/holdout/results.json)

## Computational cost

One scoring and evaluation pass took 0.082 s total on Python 3.11.5, Windows 10 build 19045 and an AMD Ryzen 9 5900X. This single-run time covers the frozen evaluator call, including preparation and result classification. Preflight, intake and disk writes were outside the timed call. The deterministic counters below describe the work of each search. The check counters follow each method's own matching implementation.

| Method | Candidate slots completed | Expanded prefixes, total | Peak per query / pair | Recorded checks | Hypotheses retained / seen | Peak hypotheses per pair |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 58/58 | 128 | 22 / 20 | 5,406 | 6 / 6 | 1 |
| B | 58/58 | 784 | 82 / 42 | 15,930 | 6 / 6 | 1 |
| C | 58/58 | 1,140 | 362 / 362 | 127,764 | 6 / 6 | 1 |

The frozen limits were 24 markers per view, 24 references per query, 100,000 prefixes per pair, 256 retained hypotheses per pair and 600,000 prefixes per query. No limit was hit. Peak memory and production update latency were unmeasured. [Saved computational counters](../local-data/phase-1-6-5/owner/holdout/results.json)

## Frozen advancement gate

| Requirement | Observed outcome |
| --- | --- |
| All positive slots operational with unambiguous evaluator truth and all three same-frame views eligible | Met. 6/6 same-frame and 8/8 moved slots operational and labeled. All three same-frame views represented. |
| Genuine bilateral floor-eligible moved support in both query directions | Missing. Witnesses passed 8/8. Combined floor passed 0/8, with 0/4 in each direction. |
| Verified 2D recovery on all eligible required slots, with completed required searches | C recovered 6/6 eligible same-frame slots. Zero eligible moved slots. Both B and C completed all 58 slots. |
| At least one paired C gain over B and more C recoveries on the identical eligible bilateral cohort | Unevaluable. Zero paired gains on zero eligible moved slots. The two recovery rates are undefined. |
| Zero C false unique regions, zero unverified unique alignments, and no suppression or truncated verdicts | Met on the roster. 0/16 false unique, 0/16 unverified unique, 0/16 budget stops, zero ambiguous or unresolved compatible candidates and zero collisions in 44 negative slots. |

**INCONCLUSIVE.** The required bilateral floor-eligible evidence is absent in both directions. The run verifies same-frame local alignment and records the genuine moved-view overlap, but provides no eligible moved-view test of C's advantage over B. The directed comparisons reuse two source views and four reviewers from a single moved-view event. Same-frame and negative-control results are roster-specific. They give no estimate of a population collision rate, general layout identification or hidden-target accuracy. The Phase 1.6.3 gate remains **FAILED**. [Frozen protocol](FINAL_REPRESENTATION_PROTOCOL.md) · [Prior holdout](INDEPENDENT_LAYOUT_HOLDOUT_RESULTS.md)

## Strategic decision

Close the representation-only track. The evidence justifies a small, direct **NEXT predictive-information pilot**, subject to owner approval and verified ground truth. The pilot can ask whether visible geometry at a fixed early checkpoint improves the bearing to the still-hidden Level 3 stairs over a simple directional prior. The holdout measured same-frame repeatability and moved-view overlap. It contains no scored hidden NEXT predictions. Ten recordings contain a labeled NEXT sighting. Only one development layout has verified hidden NEXT bearings, across four checkpoints. The existing real prediction benchmark has zero scored observations. [Dataset quality report](DATASET_QUALITY_REPORT.md) · [NEXT ground-truth pilot](PILOT_BENCHMARK_RESULTS.md)

- **Use a baseline first.** Predeclare one primary early checkpoint and bearing convention. Compare an unconditional development-set prior and an entrance-orientation prior when that orientation is observable. A simple validated directional rule can join those baselines. Authorized static research could establish the destination, warp anchor or an orientation constraint for a pinned source, build and difficulty. A classic-only finding can guide a hypothesis. D2R bearing utility requires independent validation against the captured D2R scenario. [Feasibility](FEASIBILITY.md) · [Static reference research](RESEARCH.md)
- **Test directional agreement across candidates if the reference evidence supports it.** Transfer the labeled NEXT position of each distinct compatible reference and its retained alignments into the observable player frame. Reference layouts can agree on a sector while remaining region-ambiguous. Group duplicate layouts before counting support. Keep all admissible sectors, allow abstention on disagreement or insufficient support, and evaluate on unseen layout groups. Include out-of-corpus cases because candidate agreement can be wrong. Compare correct predictions per eligible layout, coverage and accuracy at matched coverage against the directional priors. [Benchmark protocol](../benchmarks/PROTOCOL.md)
- **Require minimum verified NEXT evidence per layout.** Identify the Level 3 stair by its destination, link it to a later registered automap anchor, establish that it is still hidden at the chosen checkpoint using the surrounding footage, and register the observed player and target in a common coordinate frame using independent landmarks. Record localization and transfer error and require a bearing that remains in one predeclared sector under that uncertainty. Record the build, mode, difficulty, arrival context and checkpoint. Retain labels and later footage evaluator-side. A lift check needs verified targets on distinct development and evaluation layouts, and a separate calibration split for any tuned rules. Audit the existing footage for this minimum before committing to a scoring pilot. [Ground-truth recheck](PILOT_BENCHMARK_RESULTS.md#ground-truth-and-registration) · [Benchmark protocol](../benchmarks/PROTOCOL.md)

WP remains independently **INCONCLUSIVE**. Its automap anchor and early visibility are unresolved, so it needs its own verified ground truth and predictive evaluation. NEXT remains **INCONCLUSIVE** pending direct scoring. Phase 1.6.5 stops here for owner approval. [Target-specific findings](PILOT_FINDINGS.md)

## Reproduction and preservation

Run from the repository root with the approved private inputs. The one-time driver uses the frozen evaluator and saves the intake and eligibility record before scoring. The preserved record uses the original opening receipt. The completion receipt binds the opening, pre-match audit, driver and scored results.

```powershell
# Original authorization sequence in a fresh holdout directory.
python -B -m research.marker_fingerprint.run_final_holdout intake
python -B -m research.marker_fingerprint.run_final_holdout score

# Verify the recorded run and pinned history without rescoring.
python -B -m research.marker_fingerprint.run_final_holdout verify
python -B -m unittest discover -s tests -v
python -B -m research.geometry_experiment validate fixtures/synthetic
```

With the saved run present, use `verify`. The evaluator ran once and all 41 existing tests passed. The synthetic validator accepted 10 layouts and 39 frames. Post-run hash verification confirmed the pinned artifacts, original return bytes and saved result. The historical `mapa-09` result still verifies at SHA-256 `9a9f3d657edcc50cdc8524d9812680e3c99c3c154af5f84d5f7e83a3f9c839c4` and was verified without rescoring. The Phase 1.6.5 result SHA-256 is `05cf64c5d5ef000028d8d4db5f88263cb15221ba3d40cde466c095a38ba069b4`. [Runner](../research/marker_fingerprint/run_final_holdout.py) · [Completion receipt](../local-data/phase-1-6-5/owner/holdout/completion.json)
