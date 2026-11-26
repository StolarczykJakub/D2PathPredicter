# Real-data benchmark

**The pilot replay is complete and the real benchmark remains gated.** Four blind returns are frozen. NEXT passes visibility and bearing review across all four checkpoints. WP lacks a verified anchor. The existing predictors both abstained with zero independent development support in a truth-free execution probe. The real validator requires both development and evaluation partitions. The private `local-data/phase-1-6/role-c/pilot-lock.json` records the version 1 implementation and protocol hashes. [Pilot results](PILOT_BENCHMARK_RESULTS.md) · [Experiment protocol](EXPERIMENT_PROTOCOL.md)

After the pilot passes, freeze assignments and all three dataset input files. Keep all observations from a layout in its group. A geometry-ambiguous case belongs in the coverage and abstention analysis when its hidden target has independent eligible truth. Discovery, unresolved position, unknown visibility and uncertain bearing have separate consequences for eligibility. The report must retain matched and standalone denominators. [Quality checks](DATASET_QUALITY_REPORT.md)

```powershell
python -m research.geometry_experiment validate local-data/real
if ($LASTEXITCODE -ne 0) { throw "Real dataset validation failed" }
python -m research.geometry_experiment benchmark local-data/real --profile --output local-data/phase1-real.json
```

Run from the repository root only after reviewer sign-off and manifest hash verification. For NEXT and WP separately, use the report's stage, three-room and fixed-cohort summaries. Report independent layouts, eligible observations, predictions, conditional accuracy, coverage, abstention, median and p90 angular error, paired lift and intervals, and warm prediction latency. Review incorrect predictions alongside their uncalibrated vote shares. A small real replay supports feasibility estimates and exposes measurement problems. A decisive result needs independent evaluation at the planned precision.
