# Phase 1 implementation plan

Test whether early, manually observable geometry adds useful directional information for NEXT and WP in D2R Catacombs Level 2, Normal, arriving from Level 1. The installed Python 3.11 and its standard library cover the offline analysis.

| Open audit finding | Phase 1 treatment |
| --- | --- |
| F-01 · P0 · Missing independent D2R evidence | The workspace and supplied attachment contain no eligible recordings, screenshots or annotations. Implement the collection path, validator and synthetic contract checks. Real evaluation remains blocked. |
| F-02 · P1 · Synthetic shortcuts | Use hand-authored cases for behavior, including a shuffled-label control. Evaluate the actual hypothesis on independently annotated development and evaluation layouts when supplied. |
| F-03 · P1 · Exported anchors may be room centres | Label the actual Level 3 stairs and waypoint from footage. Classic exports and generator validation are deferred. |
| F-04 · P1 · Geometry from real images may be unreliable | Register fixed-setting frames using visible landmarks. Independently annotate a subset and measure disagreement during the real pilot. |
| F-05 · P1 · A perfect local fit can be wrong | Reproduce both audit completions. Use directional support and abstention. Evaluate field usefulness with simple feature comparisons on disjoint layouts. |
| F-06 · P1 · Future information and selection bias | Keep observations, metadata and hidden labels in separate files. Exclude each discovered target independently. Report attrition and compare checkpoints on the same eligible layouts as well. |
| F-07 · P1 · Vote shares can misstate confidence | Use independent layouts as samples, retain unresolved label mass, and report empirical support as an uncalibrated score. A pilot leaves population frequencies and calibration open. |

Implement in this order.

1. Freeze the protocol and write the collection and annotation guide.
2. Implement the dataset validator and the entrance-conditioned baseline.
3. Add small lookup tables for visible geometry and single-feature comparisons.
4. Run the synthetic regression cases, a held-out replay, and the shuffled-label control. Publish results and the exact input required to unblock the real pilot.
5. Once real data is available, check annotation quality, run grouped development replay, then evaluate held-out layouts with the frozen rules. Keep NEXT and WP decisions independent.

The Phase 1 protocol supersedes the preliminary algorithm and thresholds in the Phase 0 roadmap for this experiment. [Audit findings](audit/FINDINGS.md) · [Experiment protocol](EXPERIMENT_PROTOCOL.md) · [Data collection guide](DATA_COLLECTION_GUIDE.md)
