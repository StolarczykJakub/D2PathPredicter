# Repository guidance

- Use [D2R_MapPredictor_PROJECT_MASTER_PLAN_v1.2.md](docs/D2R_MapPredictor_PROJECT_MASTER_PLAN_v1.2.md) as the current master plan and write future master-plan updates there.

- Work only within the user-approved phase. Phase 0 authorizes research and documentation. Phase 1 starts after explicit user approval.
- Use observable geometry and authorized static reference data. Keep the first experiment offline and independent of the game client. The scope and phase gates are in [PROJECT_SCOPE.md](docs/PROJECT_SCOPE.md) and [FEASIBILITY.md](docs/FEASIBILITY.md).
- Keep the matcher deterministic and dependency-light. Use C# for the intended desktop implementation. An isolated Python standard-library experiment is acceptable when justified by the environment.
- Record the source, version, difficulty, asset requirements, and verification limits of every reference provider. Keep commercial assets, local recordings and save data outside version control. Do not vendor game-derived tables bundled by a third party without confirming their provenance and permissions.
- Keep development, calibration and final evaluation maps disjoint. Group duplicates before splitting. Feed only observation geometry and player position to the matcher. Preserve ambiguity and allow it to abstain.
- Label results as synthetic, classic Diablo II, or independently validated D2R. Keep benchmark setup and limitations with each result. Use [the benchmark protocol](benchmarks/PROTOCOL.md) for reporting.
