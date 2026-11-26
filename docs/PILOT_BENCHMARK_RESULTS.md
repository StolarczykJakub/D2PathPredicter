# Phase 1.6 pilot replay results

**NEXT and WP are NOT EVALUABLE in the frozen benchmark.** One D2R development layout supplied four observations and zero independent training layouts for a leave-one-layout-out replay. There are zero eligible benchmark predictions, zero scored observations, and zero evaluation layouts for either target. The version 1 [experiment protocol](EXPERIMENT_PROTOCOL.md) fixes eight automap-plane sectors, the entrance origin and target-specific eligibility.

The pilot uses owner-reported D2R 3.4.95032, DWR ROW, on Battle.net, Normal Catacombs Level 2 entered from Level 1. The recordings are full-screen 1920×1080 at fixed automap zoom for the measured frames. The source video, locked releases, observations, and unchanged implementation are identified by hash in the private evidence files. The one-layout result measures workflow behavior.

## Ground truth and registration

The original manual arithmetic reproduces the 1.58 px maximum held-out residual. A second pixel-based check matched yellow and purple glyph centroids within 14 px of each preliminary translation, fitted the longest matched pair, and measured the remaining points. All six recomputed registrations passed the existing screen. The longest baselines were at least 107 px, an off-axis holdout was at least 44 px from each fitting line, scale ratio was 0.9996–1.0001 and absolute rotation was at most 0.111°. Maximum held-out errors by frame were 0.49, 0.14, 1.83, 1.83, 1.86 and 1.86 px across stages 0–3, NEXT and WP. These are agreement residuals for matched landmarks. The selection near prior translations and stability of the glyph centroids limit the check. [Stored pixel check and source hashes](../local-data/phase-1-6/role-c/pilot-validation/registration-recheck.json) · [Original registration rule](REGISTRATION_VALIDATION.md)

- **NEXT.** The Level 3 stairs label at 68.2788 s and the same gray automap glyph in the NEXT, WP and late reference images support the preliminary anchor near (1028, 705) native reference px. The NEXT frame mark near (1000, 515) and the WP frame check near (1422, 525) transfer to this same position to within a pixel at the precision of the marks. Retained 10 px provisional target localization radius and 1.86 px NEXT frame transfer residual as separate terms.
- **NEXT visibility.** The registered checkpoint views and a 2 Hz review of the level transition through 69.5 s support hidden through stage 3. At 52.2123 s the projection is partly obstructed by the HUD. At approximately 53.5–60 s it clears the HUD in subsequent views while the same revealed floor persists and the projected stair area is unmapped. The destination outline and glyph become recognizable around 63.5–64 s in this sampled review. This brackets discovery for the four checkpoints without assigning a frame-exact first appearance.
- **WP.** The 76.5000 s and 80.2997 s source views identify the Level 2 waypoint and its scene platform. The pixel alignment passes, but the nearby persistent gold marker has no verified anchor association to the platform and the tooltip and cursor are in scene/UI coordinates. No WP position or first visibility can be assigned. WP is excluded independently of NEXT. [Target recheck](../local-data/phase-1-6/role-c/pilot-validation/target-and-visibility.json)

Role C transformed positions to the late reference plane for audit and scoring sensitivity only. Stage 0–3 player marking radii were 5, 5, 3 and 8 px. Room-centre radii were 5–20 px. The NEXT bearing check sums the player mark, stage transfer residual, target mark, target transfer residual and rounding allowance. All four bearings resolve under this budget in the existing evaluator's `truth_bearing` function. Stage 2 can tolerate about 26.54 px of total positional radius before its E sector becomes unresolved. Its budget is 16.71 px, and even a 6 px allowance for each transfer keeps it inside E. [Registered audit](../local-data/phase-1-6/role-c/pilot-validation/registered-audit.json) · [Evaluator eligibility output](../local-data/phase-1-6/role-c/pilot-validation/truth-eligibility.json)

## Per-checkpoint results

The two real predictor functions executed unchanged against the frozen observation features in a truth-free diagnostic. The origin was the visible player marker for this execution probe. A positive player radius left the contextual player region unknown. Geometry room sectors in the probe are player-relative and cannot stand in for the required entrance-relative sectors. No late-frame transform, target coordinate or label was passed to either predictor. No real or synthetic votes were borrowed. The geometry method has table support counts and no layout candidate search.

| Stage | Visible features and omissions | NEXT truth | WP truth | Baseline, NEXT and WP | Geometry, NEXT and WP |
| ---: | --- | --- | --- | --- | --- |
| 0 | Player, 1 provisional centre, 0 links, 0 frontiers, 0 dead ends. Arrival-room centre and orientation absent. | Hidden · SW 239.77° · 17.42 px radius | Uncertain visibility and anchor | UNKNOWN · 0 votes | UNKNOWN · 0 votes |
| 1 | Player, 1 provisional centre, 0 links, 0 frontiers, 0 dead ends. Arrival-room centre and orientation absent. | Hidden · S 175.72° · 17.04 px | Uncertain visibility and anchor | UNKNOWN · 0 votes | UNKNOWN · 0 votes |
| 2 | Player, 2 centres, 1 link, 0 frontiers, 1 reported dead end. Arrival-room centre and orientation absent. | Hidden · E 110.61° · 16.71 px | Uncertain visibility and anchor | UNKNOWN · 0 votes | UNKNOWN · 0 votes |
| 3 | Player, 7 centres, 2 links, 0 frontiers, 2 reported dead ends. One dead end fails the parser and was omitted from the execution copy. Arrival-room centre and orientation absent. | Hidden · S 175.18° · 21.71 px | Uncertain visibility and anchor | UNKNOWN · 0 votes | UNKNOWN · 0 votes |

All four NEXT checkpoints pass the target visibility and bearing checks. None clears the end-to-end dataset gate. WP clears neither gate. The first checkpoint at or above three annotated centres is stage 3 with seven, a primary-checkpoint overshoot under version 1. Both methods fell back to an empty unconditional table. The baseline permits null orientation and backs off to pooled priors. The geometry method tries an orientation-pooled signature, followed by prior lookup when support is below two. Both need at least two consistent votes and the specified vote share to emit a direction. Their `UNKNOWN` outputs reflect zero independent support.

| Target | Target-side eligible observations | Predictions in diagnostic, either method | Official benchmark coverage | Accuracy, angular error and correctness |
| --- | ---: | ---: | --- | --- |
| NEXT | 4 on 1 development layout | 0/4 (0% diagnostic prediction coverage) | Undefined, 0 scored observations | Undefined, 0 predictions |
| WP | 0 | 0 across 4 attempted calls per method | Undefined, 0 scored observations | Undefined, 0 predictions |

## Validator and timing

- `python -m research.geometry_experiment.blind_packets local-data/phase-1-6/role-a-release b16-k9w4` verified all four releases. `python -m research.geometry_experiment validate fixtures/synthetic` accepted the existing synthetic fixture with 10 layouts and 39 frames. `python -m unittest discover -s tests -v` passed all 17 tests, including the null-orientation fallback.
- `python -m research.geometry_experiment validate local-data/phase-1-6/role-c/pilot-validation/dataset-gate-probe` returned exit code 2 and `both dataset splits are required`. Invoking the existing `parse_frame` separately on the evaluator-only registered rows accepted stages 0–2 and rejected stage 3 with `b16-k9w4-03 has a conflicting dead end`. The full benchmark requires a frozen second split and complete, deduplicated layout truth. [Gate probe](../local-data/phase-1-6/role-c/pilot-validation/dataset-gate-probe/)
- Warm execution-only timings in Windows 10 and Python 3.11.5 are in microseconds, 250 calls per method and stage. These measure an empty-table prediction with no annotation, registration, fit or Windows scheduling correction.

| Stage | Baseline p50 / p95 µs | Geometry p50 / p95 µs |
| ---: | ---: | ---: |
| 0 | 10.75 / 15.57 | 14.30 / 26.65 |
| 1 | 11.00 / 14.65 | 17.80 / 26.01 |
| 2 | 11.30 / 14.02 | 21.00 / 44.56 |
| 3 | 11.60 / 17.34 | 24.10 / 42.45 |
| Pooled p50 / p95 / max | 11.20 / 15.01 / 380.30 | 19.30 / 33.82 / 290.60 |

[Raw replay outputs and timings](../local-data/phase-1-6/role-c/pilot-validation/predictor-diagnostic.json)
