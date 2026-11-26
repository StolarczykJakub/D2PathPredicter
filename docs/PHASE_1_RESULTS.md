# Phase 1 results

**The D2R verdict is INCONCLUSIVE for NEXT and WP.** The offline harness passed its synthetic checks. Real pilot footage has been reviewed and is ready for manual annotation.

## Hypothesis and data

Additional visible geometry may improve directional predictions over an entrance-orientation baseline while NEXT and WP are still hidden. The test scenario is Catacombs Level 2, Normal, arriving from Level 1.

The hand-authored `synthetic-contract-v1` dataset has six development layouts, four disjoint evaluation layouts and 39 observations. It includes both audit completions, an unreadable frame, an unknown orientation, a missing label, early discovery and a checkpoint that jumped past three rooms. The CLI records hashes of the three inputs. [Audit counterexample](audit/PHASE_0_AUDIT.md#what-early-imagery-can-identify)

## Real footage review

The owner supplied ten 1080p Battle.net recordings for the Normal Catacombs Level 2 pilot on D2R 3.4.95032, DWR ROW. Both NEXT and WP have visible confirmation in nine clips. The second clip confirms NEXT and remains partial. The local inventory in `local-data/pilot-intake/manifest.json` records evidence frames, source hashes and where overlapping end views are needed. Phase 1.6 prepared staged blind releases for one pilot layout. Frozen annotations, formal deduplication and target eligibility remain pending. [Phase 1.6 guide](BLIND_ANNOTATION_GUIDE.md) · [Pilot status](DATASET_QUALITY_REPORT.md)

## Methods

The baseline counts recorded development bearings by entrance facing or axis, checkpoint and observable player region, with broader priors for sparse buckets. The geometry method adds visible room count and positions, links, corridor axes, branches and dead ends. Both use the same evidence threshold and report support as uncalibrated counts. The evaluator converts coordinates into labels and scores eight screen-plane sectors. The predictors receive only annotated visible input and direction counts. [Frozen experiment protocol](EXPERIMENT_PROTOCOL.md)

## Synthetic results

Cells show **correct predictions / predictions made / eligible cases**. The standard comparison uses held-out full layouts.

| Observation stage | NEXT baseline | NEXT geometry | WP baseline | WP geometry |
| --- | ---: | ---: | ---: | ---: |
| Arrival | 1 / 3 / 3 | 1 / 1 / 3 | 2 / 3 / 3 | 1 / 1 / 3 |
| First additional frame | 1 / 4 / 4 | 1 / 2 / 4 | 2 / 3 / 3 | 1 / 1 / 3 |
| Second additional frame | 1 / 3 / 3 | 1 / 1 / 3 | 2 / 3 / 3 | 1 / 1 / 3 |
| Third additional frame | 1 / 2 / 2 | 1 / 1 / 2 | 1 / 2 / 2 | 1 / 2 / 2 |

- **Three-room comparison.** Three layouts qualified and one overshot. Geometry withheld two of three predictions for each target. It agreed with the baseline on the only mutually predicted layout for each target, giving an observed paired lift of zero and too few pairs for an interval. Median sector-centre error was 26.6° for baseline NEXT and 0° for baseline WP. Geometry's single prediction had 0° error for each target.
- **Feature and exploration checks.** Room sectors and corridor axes individually reproduced the geometry result at three rooms. The other single features reproduced the baseline totals there. On the two-layout fixed eligible cohort for each target, each method produced one correct result at every checkpoint. The synthetic replay showed no increase in correct predictions with additional observations on those cohorts.
- **Controls.** All 17 tests passed, including the leak, coordinate, discovery and repeat-layout checks. Two reports from fresh invocations without profiling were byte-identical. The shuffled-label control reproduced the baseline totals at three rooms and yielded zero paired lift for either target there. The leave-one-layout-out development replay also yielded zero paired lift at that checkpoint.

## Failure cases and limits

`audit-a` and `audit-b` share the same visible three-room geometry and player position. NEXT lies SE in one and NE in the other. WP lies E in one and N in the other. The regression verifies that a table containing both examples reports conflicting votes for both targets, and that a single local fit cannot authorize a prediction. A matching feature signature gives limited evidence for an unseen completion.

Later frames also exposed a wrong WP prediction on an unseen layout when geometry fell back to the entrance prior. Already discovered targets were excluded independently. The sample is too small and its labels too deliberately constructed to estimate real ambiguity, accuracy, calibration or feature value.

## Runtime and reproduction

On Windows 10 build 19045, Python 3.11.5 and an AMD Ryzen 9 5900X, one fresh synthetic replay took 4.74 ms to load and validate and 1.65 ms to fit. After one warm-up sweep, 375 timed calls per method gave baseline p50/p95/max of 0.015/0.018/0.030 ms and geometry p50/p95/max of 0.021/0.035/0.116 ms. Peak process working set through scoring and profiling was 20.3 MB, before writing the JSON report. These measurements cover the small offline fixture.

```powershell
python -m research.geometry_experiment validate fixtures/synthetic
python -m unittest discover -s tests -v
New-Item -ItemType Directory -Path local-data -Force | Out-Null
python -m research.geometry_experiment benchmark fixtures/synthetic --profile --output local-data/phase1-synthetic.json
python -m research.geometry_experiment benchmark fixtures/synthetic --shuffle-training --output local-data/phase1-null.json
python -m research.geometry_experiment benchmark fixtures/synthetic --development --output local-data/phase1-development.json
```

## Decision and next evidence

Annotate the early checkpoint geometry from the early-only index. Separately register the late views and target anchors, resolve discovery time and deduplicate complete layouts. Check agreement between annotators before estimating lift and sizing a larger independent evaluation. The current evidence supports deferring Phase 2 static data, template matching and procedural generation until that pilot shows a reason to investigate them. [Recording and annotation guide](DATA_COLLECTION_GUIDE.md)
