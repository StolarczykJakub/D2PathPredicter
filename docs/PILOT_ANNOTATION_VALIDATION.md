# Phase 1.6 pilot annotation validation

The owner supplied four independent blind returns for `b16-k9w4` (`mapa-07`). All four pass the packet-format, integrity and reference checks. The dataset adapter exposes one additional semantic conflict at stage 3. The workspace contains no Git metadata, so a branch or commit could not be established. All six files pinned in the version 1 pilot lock and all four release archives match their recorded SHA-256 exactly.

## Frozen originals

The files in `docs/annotation_analysis/` were copied byte for byte to `local-data/phase-1-6/role-a-return/b16-k9w4/` under their frame IDs. The private [intake manifest](../local-data/phase-1-6/role-c/pilot-validation/intake-manifest.json) records source names and all three digests for each return.

| Frame | Supplied file | Returned JSON SHA-256 |
| --- | --- | --- |
| b16-k9w4-00 | `observation.json` | `86ca876241d28ed6c3300fc02992eaaf5bc165580a00d2d40b74d36a61d78f79` |
| b16-k9w4-01 | `observation (1).json` | `e968a6ab6d5a276c9afd93ae8403e68b37078176e6f0ffb75212c8f6a2e0ef26` |
| b16-k9w4-02 | `observation (2).json` | `b83889cd074ac3cb1f1f008aa8be34c075a83bdc31d888f477d72c711ae08413` |
| b16-k9w4-03 | `observation (3).json` | `24d0adb22a8edf0411d0885a17d33feca8c03d9d58800dab69063def3c1d7295` |

Every JSON decoded with unique keys and contained the draft's exact field set. Case, stage, frame ID, SHA-256 of the released PNG and 1920×1080 dimensions all match the appropriate draft. The existing release verifier passed archive membership and CRC, template, instructions and PNG checks. Applying the two documented masks to the four native early PNGs reproduced every released RGB pixel. The recording SHA-256 matches the intake manifest. [Native frame check](../local-data/phase-1-6/role-c/pilot-validation/native-frame-check.json)

All point coordinates are in bounds. Room IDs are unique within each frame. Links join distinct listed rooms and are unique as undirected pairs. Boundary and dead-end references resolve to listed rooms. All boundary statuses and directions are allowed. Segments have two distinct endpoints. Player and room marking radii and elapsed minutes are finite and nonnegative. All four returns set `uncertain_geometry` and include explanatory notes. All four leave entrance position and orientation null. Reviewer IDs, timestamps for the release and return history, and same-frame repeat annotations are unavailable. Blind collection is owner-reported and the packet association is verified from bytes.

## Investigation of the ten findings

| ID | Result |
| --- | --- |
| ANN-001 | Confirmed missing entrance marks. Stage 0 shows the labeled Level 1 stairs in the scene and an ambiguous purple mark on the automap. The scene label identifies the arrival context. The released view and instructions do not establish a reproducible room centre, facing or axis. Each method accepts null orientation and uses a pooled lookup. |
| ANN-002 | Counts are 1/1/2/7 room centres and 0/0/1/2 undirected links. Stages 0 and 1 carry counts and provisional centres with no graph edges. The stage 3 graph has five components including three isolated vertices and no degree-three junction. The predictors can compute sparse features. The usual entrance-relative features still need a valid origin, and the value of sparse features is unmeasured. |
| ANN-003 | Early ambiguous records and later confirmed records include visually similar yellow wall markers in their respective release frames. Some late markers visibly lie on boundaries between two measured outlines, which adds evidence for a link. The released instructions name statuses but supply no color legend or rule for confirming traversability from a glyph alone. The change in certainty across frames is observable. Individual passage claims need a fresh, same-frame-only adjudication before changing any labels. |
| ANN-004 | IDs are frame-local. Stage 2 `r01` and `r02` align with stage 3 `r06` and `r05`: late-reference centres agree within 1 px and the same shared yellow opening lies along the registered Stage 2 edge. This audit used the outlines and opening independently of room IDs. The stage 0 and 1 `r01` centres refer to different regions. No cross-frame ID mapping entered predictor inputs. |
| ANN-005 | Visibly drawn wall runs remain outside room records, including lower/right fragments in stage 1 and the right-hand network in stage 3. The geometry signature discards raw boundary segments, individual room-centre radii and ambiguous wall evidence. Sparse links leave much of the visible image unrepresented. |
| ANN-006 | Stage 2 has 4 directed confirmed-passage records and 3 distinct endpoint pairs. Stage 3 has 11 and 9. Each shared opening with an explicit graph link contributes one undirected edge regardless of boundary multiplicity. These deduplicated segment counts describe the annotation claims. |
| ANN-007 | Stage 2 `r02` and Stage 3 `r05` are the same closed outline, with a single yellow glyph and one room link in each source. The terminal label depends on the glyph convention. Stage 3 `r01` has one marked opening to a region without a confirmed centre. The frozen row records zero explicit links or unexplored branches for it. The existing parser therefore rejects that dead end. The visible annotation does not justify an invented connection. |
| ANN-008 | Stage 3 `r04` and `r07` have small, enclosed wall circuits with no confirmed opening. Each could be a room or an enclosed architectural feature. They remain in the original return as reported with unresolved identities. |
| ANN-009 | The Stage 2 confirmed segments measure 71.6–72.5 px and visibly include adjoining unmarked wall, whereas Stage 3 marks localized 16.1–20.1 px openings. This is a confirmed extent inconsistency for using the segment as the location or width of an opening. The packet example provides endpoints but has no rule for measuring glyph width. The current graph predictor ignores segment length. |
| ANN-010 | Stage 2 NEXT is closest to a directional boundary at 1.89°. The measured uncertainty budget preserves its E sector. Room-centre uncertainty affects predictor features such as the stage 3 `r02`–`r03` link axis, whose allowed centre displacements can cross a sector boundary. The evaluator uses player and target error for truth bearing. [Bearing sensitivity](PILOT_BENCHMARK_RESULTS.md#ground-truth-and-registration) |

This was a validation review. No adjudicated replacement labels were created. The private registration output is evaluator-only. The truth-free execution copy preserves declared room centres and links in player-relative pixels and omits the stage 3 parser-conflicting dead-end claim from that copy only. It does not promote ambiguous boundaries or a passage with unknown destination into a frontier. [Predictor replay](PILOT_BENCHMARK_RESULTS.md)
