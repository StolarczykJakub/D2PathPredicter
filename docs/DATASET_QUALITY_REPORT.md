# Phase 1.6 dataset quality

Ten recordings are available. Nine clips contain both target labels, and the second clip confirms NEXT only. These are footage counts. The completed workflow pilot covers one development layout, `mapa-07`. The remaining recordings await a follow-up decision. [Pilot findings](PILOT_FINDINGS.md)

| Check | Pilot outcome |
| --- | --- |
| Context and capture | Normal Catacombs Level 2 via Level 1 stairs. Owner-reported D2R 3.4.95032, DWR ROW, Battle.net online. Four chronological early checkpoints at 1920×1080. The offline replay works with the extracted files. |
| Blind inputs | Four verified standalone ZIPs. Each contains one neutral PNG, a blank observation JSON and neutral instructions. ZIP entries and PNG chunks are allowlisted. A rebuild matched the release byte for byte. Pixel comparison confirmed geometry outside the two masks is identical. |
| Annotation integrity | Four owner-supplied blind returns frozen byte for byte. All passed packet identity, schema and reference checks. Reviewer IDs and chronological handoff records are unavailable. All four omit entrance centre and orientation. Stage 3 has one dead-end record that fails the dataset frame parser. |
| Ground truth | NEXT has a verified pilot anchor, was hidden through all four checkpoints, and has resolved bearings. WP identity is verified, and its automap position and early visibility remain uncertain. |
| Registration | Reproduced the 1.58 px manual maximum held-out error. The six pixel-based rechecks passed, with maximum held-out error of 1.86 px. Repeat-review marking accuracy remains unmeasured. |
| Layout integrity and partition | This map is assigned to development as a workflow pilot. Frozen complete layout inspection and deduplication precede any remaining split assignments. |
| Existing validator | Accepted the synthetic fixture with 10 layouts and 39 frames. All 17 tests passed. The validator rejected the one-layout gate probe because both splits are required. |

The four return files report 5.31 minutes of annotation in total. Repeat-review disagreement and end-to-end manual effort remain unmeasured. [Blind procedure](BLIND_ANNOTATION_GUIDE.md) · [Intake details](PILOT_ANNOTATION_VALIDATION.md)

## Release to Role C

1. Lock raw recordings, packet hashes, returned answers, source-frame identifiers, reviewer roles and association of the anonymous ID to the original map in the private store. Use a fresh reviewer when independence is broken.
2. Reconcile geometry inside the available visibility mask. Keep unknown, clipped and inconsistent cases explicit. Normalize coordinates from confirmed anchors. Use only Role A features to construct observation inputs and check that target files cannot enter those inputs. Preserve conflicts and adjudication notes separately.
3. Audit actual target identity, anchors and first appearance using Role B evidence. Map only VERIFIED target positions to the existing `{position, error}` shape. Map UNCERTAIN, MISSING and INVALID to an explicit null for that target. A map with verified NEXT may contribute NEXT if its other quality checks pass. Retain all source and uncertainty notes outside the model input.
4. Validate complete geometry, sequence, duplicate frames and capture context. Deduplicate by layout before selecting development and evaluation groups. Freeze assignments, normalized files, protocol and implementation hashes before evaluation. Report eligible layouts and observations separately by target.

Pilot totals released for real scoring are **0 layouts and 0 observations for each target**. NEXT passes four target-side checks on one layout. Both methods abstain in the empty-table diagnostic. The missing canonical origin, graph conflict and disjoint split remain blockers. [Pilot replay](PILOT_BENCHMARK_RESULTS.md) · [Benchmark gate](REAL_DATA_BENCHMARK.md)
