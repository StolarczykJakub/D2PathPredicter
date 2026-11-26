# Phase 1 roadmap

This is the preliminary Phase 0 roadmap. The owner-approved offline experiment follows the narrower [Phase 1 plan](PHASE_1_PLAN.md) and [experiment protocol](EXPERIMENT_PROTOCOL.md).

## Implementation sequence

| Step | Work and acceptance check |
| --- | --- |
| 1. Freeze the case and data format | Use Catacombs Level 2, Normal, stairs arrival from Level 1. Define the canonical point, adjacency, visibility and target-label records. Record units and reproducibility inputs. Use the installed Python standard library for the first experiment on this machine. Use C# / .NET 10 LTS if starting on a supported Windows host with the SDK available. |
| 2. Establish fixture provenance | Prepare a tiny set of hand-authored synthetic cases and a deterministic, original maze fixture generator for disjoint splits. If authorized classic data and a matching `libd2` build are available, time-box a local export check on one Act I case. Verify repeatability, units, the Level 3 destination and the waypoint anchor before building a classic corpus. Eligible pre-existing D2R captures or fixtures can support a D2R evaluation when they include independently labeled ground truth. |
| 3. Build the reveal simulator and baseline | Reveal partial geometry from a fixed entrance and a target-blind path or teleport schedule. Implement the orientation-conditioned direction prior and verify that unknown and discovered targets are handled according to the protocol. |
| 4. Build the matcher and tests | Implement the embedded geometry scan, deterministic comparison and per-target candidate aggregation. Test exact and probable fits, multiple competing completions, alignment ties, absent targets, noisy observations and rejection. Check that image-independent ground-truth fields cannot reach the matcher. |
| 5. Execute and document the benchmark | Freeze splits, calibrate, then run the held-out evaluation. Compare early accuracy, coverage, coordinate errors, candidate counts, confidence calibration, latency and memory. Publish failure examples and enough configuration to reproduce the numbers. |
| 6. Decide whether to continue | Apply the gates per target. A synthetic or classic pass can justify seeking D2R evidence. A D2R result requires independent D2R fixtures. Consider an image-level registration experiment only if the geometry-stage result and the fixture path justify it. |

## Deliverables after approval

- A small CLI under `src/`, deterministic checks under `tests/`, and labeled, redistributable synthetic cases under `fixtures/`.
- A reproducible benchmark command, split manifest and report under `benchmarks/`.
- A decision for each target, with findings and blockers tied to the evaluated data sources. [Feasibility gates](FEASIBILITY.md#go-and-no-go-criteria), [benchmark protocol](../benchmarks/PROTOCOL.md)
