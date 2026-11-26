# Findings

P0 blocks the proposed D2R utility decision. P1 can invalidate results or force substantial rework. P2 needs attention before or during a narrowed Phase 1. P3 can wait. P4 is optional. A confirmed observation about a design or interface gives evidence of a risk without implying a defect in code that does not exist.

<a id="f-01"></a>

## F-01 · P0 · Independent D2R evidence is missing

- **Description and evidence.** The workspace has no eligible D2R captures, manifests, labeled geometry or verified reference provider. It documents classic evidence and a planned synthetic experiment. This is a confirmed prerequisite gap. [Workspace inventory and source review](PHASE_0_AUDIT.md#what-exists-and-what-was-checked) · [Existing D2R gate](../FEASIBILITY.md#go-and-no-go-criteria)
- **Affected and impact.** The D2R utility gate, label contract and Phase 1 roadmap. The project cannot measure application accuracy, estimate early ambiguity in D2R, or support product claims.
- **Action and verification.** Identify a source of authorized offline recordings for one build, mode and difficulty. Inspect a small paired early/later sample with independently verified NEXT and WP and distinct-layout tracking. If the source is unavailable, record the D2R decision as blocked.
- **Confidence.** High for the workspace gap. The availability of recordings outside it is unknown.

<a id="f-02"></a>

## F-02 · P1 · Synthetic work precedes the most consequential test

- **Description and evidence.** The roadmap can complete a generator, reveal simulator, matcher and large synthetic benchmark before obtaining real geometry. Targets and topology in an invented maze family can share correlations introduced by the fixture author. A perfectly repeatable synthetic success can coexist with chance-level D2R prediction. This is a sequencing risk. [Roadmap](../ROADMAP.md#implementation-sequence) · [Algorithm gate](../FEASIBILITY.md#go-and-no-go-criteria)
- **Affected and impact.** Phase 1 sequencing and synthetic reporting. The largest unknown can remain unresolved after all planned engineering is finished.
- **Action and verification.** Put a small D2R annotation and early-signal pilot before broad harness work. Limit synthetic cases to explicit contract checks covering ambiguity, masks, false uniqueness and abstention. Run an adversarial case with target sectors shuffled within comparable entrance/checkpoint strata to confirm the evaluator does not invent lift.
- **Confidence.** High in the design risk. Actual signal in D2R remains unknown.

<a id="f-03"></a>

## F-03 · P1 · The classic export contract can supply the wrong landmark

- **Description and evidence.** The C ABI labels bridge coordinates as centres of warp-flagged rooms. Preset records use level-local subtile coordinates and provide a warp ID or object row, a distinct contract. The classic root documentation reports collision validation. Neither collision comparisons nor bridge centres validate an interactive stair position or waypoint. This is a confirmed upstream interface constraint. [C ABI](https://github.com/jaenster/libd2/blob/main/packages/drlg/include/d2drlg.h#L146-L186) · [Upstream verification](https://github.com/jaenster/libd2/blob/main/docs/VERIFICATION.md)
- **Affected and impact.** Optional `libd2` exporter, truth labels, discovery and position/sector scoring. A room-centre substitution can move a target across a sector boundary or score it after it became visible.
- **Action and verification.** For one pinned classic build and Normal seed, repeat the export, resolve the stair destination to Level 3 and waypoint object identity, and compare both actual anchors against independently authorized observations. Check tile/subtile conversion, subtraction of origins, marker offsets and exported warning states. If labels remain unverified, keep that provider outside ground truth.
- **Confidence.** High in field semantics. Catacombs anchor error magnitude is unmeasured.

<a id="f-04"></a>

## F-04 · P1 · A collision/room proxy can overstate visible signal

- **Description and evidence.** The proposed canonical grid has known alignment and access to simulated visibility. Real pixels depend on automap cell and object mapping, reveal, view settings, background and scale. The classic lookup can omit a tile or choose a variant. Blizzard confirms presentation differences and multiple viewport modes. D2R registration and feature survival have never been measured. [Architecture](../ARCHITECTURE.md#inputs-and-coordinates) · [Classic automap lookup](https://github.com/jaenster/libd2/blob/main/packages/render/src/automap.zig#L82-L116) · [Blizzard automap notes](https://news.blizzard.com/en-gb/article/23695734/technical-alpha-learnings)
- **Affected and impact.** Reference projection, observation masks, room counts and geometry features. A clean simulation could depend on connectors users cannot see or report false contradictions on clipped lines.
- **Action and verification.** Annotate D2R images at one fixed setting. Measure independent annotation agreement, visible-connector recoverability, player origin/axis uncertainty and held-out paired landmark residuals when testing a projection. Measure feature and prediction degradation with alternate settings only after the fixed-setting check.
- **Confidence.** High in the representation mismatch. Test accuracy and the size of any transfer gap are unverified.

<a id="f-05"></a>

## F-05 · P1 · Exact visible fit can give a false impression of identity

- **Description and evidence.** The design's `exact` status names a unique full configuration in the pool when compared features have zero mismatch. Its caveat is correct, but the bare status can be propagated as confirmation. The audit counterexample yields both wrong bearings from such a fit. A single world can also yield several compatible alignments, and they can predict different bearings. This is a confirmed inference failure under the stated inputs and a design risk for API interpretation. [Architecture statuses](../ARCHITECTURE.md#matching-and-prediction) · [Counterexample](PHASE_0_AUDIT.md#what-early-imagery-can-identify)
- **Affected and impact.** Matcher status, aggregation and downstream display. Exact visible agreement can silently turn an out-of-corpus observation into an apparently confirmed prediction.
- **Action and verification.** Record match diagnostics separately from a per-target decision. Present calibrated predicted sectors or `UNKNOWN` / `INSUFFICIENT_DATA`. Exercise repeated prefixes, symmetric alignments with conflicting bearings, and a query whose true completion is absent from the pool. Evaluate false unique fits in the closed-set diagnostic.
- **Confidence.** High in the counterexample. Real prevalence is unknown.

<a id="f-06"></a>

## F-06 · P1 · Target eligibility can leak future information or hide attrition

- **Description and evidence.** The protocol defines simulated discovery from the target anchor being within a reveal model. Real identification may occur by icon, text, stair tile or interaction while another cue is clipped. A future frame may support labels and duplicate grouping. Using it to register the entrance, infer the early room graph, repair visibility, or set the model's player position would reveal future information. Conditioning comparisons on increasingly late eligible sets can also create apparent improvement. These are design risks, with no implemented leakage observed. [Protocol](../../benchmarks/PROTOCOL.md#observations)
- **Affected and impact.** D2R annotation, replay, stage comparisons and the input contract. Biased eligibility or leaked geometry could inflate lift for both targets.
- **Action and verification.** Freeze early annotations before reviewing later truth, use the same checkpoint and mask for all methods, record observable discovery rules per target, and distinguish fixed-cohort comparisons from stage-specific denominators. Audit that changing evaluator labels or later frames leaves earlier matcher inputs byte-identical.
- **Confidence.** High in the failure mechanism. No project data pipeline exists to measure exposure.

<a id="f-07"></a>

## F-07 · P1 · Equal configuration votes do not estimate occurrence probabilities

- **Description and evidence.** Grouping geometry duplicates prevents leakage. Equal weighting of distinct compatible maps is a separate modeling choice. In an audit illustration with two outcomes and a 9:1 frequency ratio, equal layout votes imply 50% support where occurrence weighting implies 90%. Reference selection, symmetry and missing target labels can distort support as well. [Benchmark grouping](../../benchmarks/PROTOCOL.md#fixture-provenance-and-isolation) · [Architecture voting](../ARCHITECTURE.md#matching-and-prediction)
- **Affected and impact.** Reference sampling, hybrid support and confidence. Overconfident or biased predictions can survive a synthetic benchmark with uniform sampling.
- **Action and verification.** Split by full-geometry group and preserve observed multiplicities for weighting when they are representative. Count a map once across alignments, track unresolved label mass, and calibrate with independent groups. Compare weighted and unweighted priors under repeat-layout and frequency-shift tests.
- **Confidence.** High in the weighting mismatch. The direction and size of any actual bias are unknown.

<a id="f-08"></a>

## F-08 · P2 · Bearings and failure states need explicit contracts

- **Description and evidence.** The dominant-axis tie rule is deterministic. Under that rule, moving the player from `(0,0)` to `(1,0)` flips the sector for target `(5,5)`. A zero vector has no bearing. The current architecture groups absent targets and unknown labels outside directional mass but leaves zero vectors and the precise per-target statuses ambiguous. This is a confirmed boundary sensitivity and a specification gap. [Sector definition](../../benchmarks/PROTOCOL.md#comparison-and-metrics) · [Target contract](../ARCHITECTURE.md#matching-and-prediction)
- **Affected and impact.** Scoring, calibration and prediction output. Angular quality can improve with unchanged sector accuracy. Unknown labels can be mistaken for absent landmarks, and small coordinate errors can flip near-boundary output.
- **Action and verification.** Define zero-vector handling, abstain when credible anchor or player uncertainty crosses a sector boundary, and record wrapped absolute angular error alongside sector accuracy where a continuous bearing is emitted. Test both sides of axes and diagonals, zero displacement and missing player. Map `NOT_APPLICABLE` only from established context, and keep unresolved labels and low evidence distinct.
- **Confidence.** High in the mathematics and specification gap.

<a id="f-09"></a>

## F-09 · P2 · The 150-map target is a pilot scale for modest lift

- **Description and evidence.** The protocol proposes 150 eligible independent maps per target. In a favorable illustration with 150 already paired scored cases, 20% discordance and true +5 percentage points, the approximate 95% half-width is 7.1 points. A rough 80%-power calculation is about 620 paired scored cases for detecting that effect against zero. Selective coverage, differing predicted subsets and group weights change variance. This is an illustrative power limitation, with no claim about actual discordance. [Protocol](../../benchmarks/PROTOCOL.md#fixture-provenance-and-isolation) · [Evaluation plan](PHASE_1_RECOMMENDATIONS.md#measurement-and-decision)
- **Affected and impact.** D2R sample budget and go/no-go interpretation. A useful effect may go unresolved. Treating a noisy point estimate as decisive can produce a false go or a false stop.
- **Action and verification.** Use pilot estimates to pre-register a group-level sample or precision plan before final evaluation. Simulate the exact matched-coverage statistic and report mutually predicted and full-eligible views. Treat wide intervals as inconclusive.
- **Confidence.** High in the illustrative calculation, low in the unknown real variance.

<a id="f-10"></a>

## F-10 · P2 · Area, mode and visibility changes need explicit invalidation

- **Description and evidence.** The plan caches state when geometry and player position are unchanged and initially fixes one area, difficulty and arrival. Identical geometry can recur after a transition. A future caller could reuse stale hypotheses or apply priors to the wrong area. Some unsupported fixtures already appear in the protocol, but the runtime boundary has no reset/identity contract. [Runtime boundary](../ARCHITECTURE.md#runtime-boundary) · [Scope](../PROJECT_SCOPE.md)
- **Affected and impact.** Replay and any later observer/cache. Stale estimates can persist into a new floor or game, or target a side exit.
- **Action and verification.** Scope the offline run explicitly, with caller-supplied session boundaries. In a later observer, clear cached predictions on uncertain or changed session/area/difficulty/arrival, and fail closed on unknown modes. Exercise the edge cases in the [validation matrix](PHASE_1_RECOMMENDATIONS.md#edge-case-validation).
- **Confidence.** High in the contract gap. No cache exists yet.

<a id="f-11"></a>

## F-11 · P2 · The reference size needed for utility is unknown

- **Description and evidence.** The 10,000-map calculation is a packed payload estimate. Neither effective D2R seed space, distinct configurations nor early prefix buckets are counted. A 100,000-map scan in the audit model costs 240 ms and holds 64 MB of geometry at favorable assumed packing, before process overhead. Identical prefixes often make filtering least selective when predictions are most valuable. [Existing cost model](../FEASIBILITY.md) · [Sensitivity estimates](PHASE_0_AUDIT.md#search-space-and-cost-sensitivity)
- **Affected and impact.** Candidate scan, index and runtime resource budget. Exact whole-map retrieval may remain sparse, while larger indexes increase working set without resolving conflicting observations.
- **Action and verification.** Compare a compact local histogram and bounded scan on fixed held-out data. Record distinct prefixes, memory, p95 and worst bucket, no-match and risk–coverage curves as training size grows. Expand only if new data adds measurable held-out lift.
- **Confidence.** High in the absence of measurements and arithmetic. Real resource consumption and required corpus size are unknown.

<a id="f-12"></a>

## F-12 · P2 · Classic dependency reuse needs a reproducible provenance check

- **Description and evidence.** `libd2`'s MIT code license excludes game-derived assets. Source embeds or refers to data and assets, and the reviewed Zig manifest and prose differ. `d2mapapi`'s code license grant is unverified. The inspected MapAssist wrapper requests maps with a known seed and launches its packaged binary with a classic LoD path. The binary implementation and exact asset inventory remain unverified. These constraints leave the asset-bearing provider build and redistribution entitlement open. [Provider inventory](PHASE_0_AUDIT.md#external-sources-and-compatibility) · [MapAssist wrapper](https://raw.githubusercontent.com/lucas-gp/MapAssist/refs/heads/main/Helpers/MapApi.cs) · [Repository guidance](../../AGENTS.md)
- **Affected and impact.** Optional research adapters and repeatability. An unpinned provider or unverified asset inventory can invalidate reproducibility or make distribution unworkable.
- **Action and verification.** Before using a provider, record commit, native ABI and managed package, toolchain, per-file input provenance and local usage rights. Hash the resulting audit manifest and verify a clean, authorized repeat export. Keep commercial inputs and derived files whose permissions are unverified outside version control.
- **Confidence.** High that the workspace lacks these proof artifacts. Actual rights and runtime asset requirements depend on the pinned provider.

<a id="f-13"></a>

## F-13 · P2 · Supported desktop target and current host are misaligned

- **Description and evidence.** The environment records Windows 10 Pro 22H2 and no modern .NET SDK. No `dotnet` command was available in the audit. Microsoft's support matrix lists qualifying Windows 10 LTSC/Enterprise editions for .NET 10. Execution on this Pro host has not been tested. [Environment](../../research/ENVIRONMENT.md) · [Microsoft Windows matrix](https://learn.microsoft.com/en-us/dotnet/core/install/windows)
- **Affected and impact.** Eventual C# desktop build and performance verification. A Python experiment can run locally, and it cannot establish deployed C# resource usage.
- **Action and verification.** Confirm the target OS support requirement and select a supported build and test host before committing to desktop delivery. Replay the same fixtures in release configuration and measure real working set and warm latency.
- **Confidence.** High in the documented support mismatch and missing command. Compatibility in practice is unverified.

<a id="f-14"></a>

## F-14 · P3 · Direction accuracy is a proxy for navigation value

- **Description and evidence.** The scope correctly allows a bearing through walls. The benchmark measures sector and position accuracy. A correct relative bearing might still favor a dead-end corridor if interpreted as the next turn. [Scope](../PROJECT_SCOPE.md) · [Metrics](../../benchmarks/PROTOCOL.md#comparison-and-metrics)
- **Affected and impact.** Product interpretation of a positive offline result. Bearing lift alone leaves detour reduction and human decision value unknown.
- **Action and verification.** If a D2R bearing gate passes, replay a small common set of navigation decisions against a simple manually applied rule. Record correct branch selections or distance/time to discovery under the same route policy before investing in UI.
- **Confidence.** High in the difference between the metrics. User benefit is unmeasured.
