# Project decisions

## Phase 0

| Decision | Rationale and review trigger |
| --- | --- |
| Catacombs Level 2 on Normal, entering by the stairs from Level 1 | Both NEXT and WP can begin hidden. Classic generator source documents special presets for both. Add other difficulties or areas after establishing utility in this one scenario. |
| Test early bearing before full layout identity | Many plausible maps can agree on the next direction. Four sectors and explicit abstention let the first experiment measure user-visible value even with imperfect layout identification. |
| Start with an entrance-conditioned baseline and embedded geometry scan | Both work on the same observations and are easy to inspect. Add indexing or neighbor fingerprints if measured corpus size and update time warrant them. |
| Use `libd2` as an optional, classic-only reference provider | Its offline generation interface and reported classic collision validation make it the strongest candidate reviewed. Keep its assets and toolchain out of the matcher. Pin the version and verify landmark export and data provenance before using it. |
| Use synthetic fixtures when a compatible verified reference is unavailable | Synthetic cases validate the matcher and evaluation protocol under known conditions. Classic references can then test the same method on classic layouts. |
| Use C# / .NET 10 LTS for production, Python standard library for the first experiment on this host | The installed Python is sufficient for the CLI. The modern .NET SDK is absent, and the current Windows edition is outside the documented supported matrix. The fixture format allows a later C# implementation to replay the same cases. [Environment](../research/ENVIRONMENT.md) |
| Require a separate, labeled D2R dataset before a D2R verdict | Collision agreement in classic 1.14d and a working synthetic predictor leave layout parity, image fidelity and early prediction utility open. |

## Phase 1.6 representation decisions

| Decision | Rationale and review trigger |
| --- | --- |
| 1.6.1 · E · INCONCLUSIVE | The counterbalanced pass order failed. The descriptive results supported glyph repeatability but missed the semantic and RAW readiness gates. [Retest decision](REPRESENTATION_DECISION.md) |
| 1.6.2 Stage 1 · Recommend B for the next approved screen | Marker constellations recovered three registered common glyphs across a roughly 448 px player displacement. The player-relative baseline passed its measured within-view and size-controlled checks but missed that overlap. Optional walls improved no candidate outcomes. Review both marker representations on a small, deduplicated, independent-layout sample only after owner approval. [PoC evidence](MARKER_FINGERPRINT_POC_RESULTS.md) |
| 1.6.3 locked holdout · Advancement gate failed. Investigate bilateral partial visibility | The 6 px constellation and 4 px baseline passed same-frame checks and missed all eight directed moved-view pairs. Wall registration found three shared non-collinear glyphs. Each view had a different fourth, preventing a complete smaller-set assignment. Propose a bounded partial-overlap diagnostic on synthetic, development and calibration evidence after owner approval. Reserve a fresh independent holdout for any changed rule. NEXT and WP feasibility remain separately INCONCLUSIVE. [Locked holdout evidence](INDEPENDENT_LAYOUT_HOLDOUT_RESULTS.md) |
| 1.6.4 · A · Recommend advancing one partial-correspondence configuration to a fresh independent holdout | The 6 px configuration with bilateral two-thirds count coverage, 25% spatial coverage and reliable triangular support passed the diagnostic. It recovered 16/16 eligible masked pairs versus strict matching's 8/16, with zero collisions in 148 real negative slots. The same floors excluded eight sparse asymmetric development fits. Wait for owner approval. The 1.6.3 gate remains FAILED. NEXT and WP feasibility remain separately INCONCLUSIVE. [Diagnostic results](PARTIAL_CONSTELLATION_RESULTS.md) |
| 1.6.5 · INCONCLUSIVE · Close the representation-only track | All eight moved slots confirmed bilateral visibility changes. Each shared eight glyphs against a floor of thirteen, leaving zero eligible moved slots in either direction. C recovered all six eligible same-frame slots, with zero false or unverified unique outcomes in sixteen queries. The prior 1.6.3 gate remains FAILED. [Final locked results](FINAL_REPRESENTATION_RESULTS.md) |
| Strategic proposal · Direct NEXT pilot, pending owner approval | Audit existing footage for independently verified hidden Level 3 stair bearings on distinct layouts. Test directional priors and, if labeled references support it, direction agreement among compatible candidates. NEXT and WP remain separately INCONCLUSIVE. WP requires separate verified truth and scoring. [Strategic decision and evidence requirements](FINAL_REPRESENTATION_RESULTS.md#strategic-decision) |

## Phase 1.7 direct NEXT preparation

| Decision | Rationale and review trigger |
| --- | --- |
| Fixed Stage 0 arrival and four-sector player-relative bearing | Reuse all ten indexed arrival frames without moving the checkpoint for any layout. Use dominant signed grid components with a conservative native-pixel boundary test. Straight-line bearing is the only scored endpoint planned. [Pilot convention](NEXT_PREDICTION_PILOT_PLAN.md#bearing-and-eligibility) |
| Three verified development labels and four proposed evaluation layouts | Keep `mapa-01`, `mapa-02` and `mapa-07` in development. Keep `mapa-04`, `mapa-06` and `mapa-09` in their historical roles for this pilot. Seal the potential evaluation layouts' later outcomes. Require independent eligibility, deduplication and access checks before approving the evaluation split. [Audit](NEXT_GROUND_TRUTH_AUDIT.md) |
| Approve only the next evidence gate after owner review | Use existing footage to establish at least three eligible target-blind evaluation layouts. Freeze fixed priors and allow geometry consensus only with adequate labeled references under the unchanged matcher. NEXT and WP remain separately INCONCLUSIVE. The representation-only track is closed. [Pilot readiness and decision criteria](NEXT_PREDICTION_PILOT_PLAN.md#metrics-and-proposed-decision-criteria) |

## Phase 1.7.2 independent NEXT qualification

| Decision | Rationale and review trigger |
| --- | --- |
| Verify the execution lock before independent ground-truth access | The owner approved existing-footage qualification. All source and Stage 0 hashes, the proposed assignments, opaque query IDs, methods, code, tests, contracts and decision rules were pinned before evaluator access. Retain the Stage 0 identity and all exclusion reasons. Scoring requires separate owner approval. [Qualification](NEXT_EVALUATION_QUALIFICATION.md#execution-lock) |
| Freeze the unconditional baseline and preserve abstention | A has the fixed two-of-three development vote. B lacks a verified entrance throat and retains `UNKNOWN`. C has two usable development references, while the reserve's observable Stage 0 geometry falls below the pilot's minimum geometry coverage. Preserve the unchanged matcher and thresholds. [Method readiness](NEXT_EVALUATION_QUALIFICATION.md#method-readiness) |
| B · Recommend a limited A-only exploratory comparison after separate approval | Qualify `mapa-03`, `mapa-05` and `mapa-10` from existing footage. Retain the excluded `mapa-08` row for a post-departure arrival frame with an unreadable player. Historical access allows only the documented target-blind exploratory claim. Three independent evaluation layouts meet the minimum. A can be measured descriptively, while geometry lift and NEXT and WP feasibility remain INCONCLUSIVE. [Cohort and access findings](NEXT_EVALUATION_QUALIFICATION.md#evaluation-cohort) |
