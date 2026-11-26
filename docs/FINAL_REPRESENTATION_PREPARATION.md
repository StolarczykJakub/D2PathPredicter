# Phase 1.6.5 holdout preparation

**Six blind packets and the read-only evaluation lock are ready for owner handoff.** The selected D2R layout is `mapa-04`, from the existing owner-reported 3.4.95032 DWR ROW Battle.net Normal Catacombs Level 2 recording series. The new holdout is awaiting six independent returns. The Phase 1.6.3 advancement gate remains **FAILED**. NEXT and WP remain separately **INCONCLUSIVE**. [Owner handoff and exact prompt](FINAL_REPRESENTATION_HANDOFF.md)

## Owner-side selection evidence

The prospective rule was hashed before re-inspecting candidate footage. The seven remaining footage-only layouts were screened in recording-ID order. On `mapa-01` the early moving reveal added wall glyphs, while the apparent reverse losses included glyphs still visible beyond the imposed window. On `mapa-02` the short stair tooltip trimmed yellow spans that remained readable and a second genuine direction was unverified. On `mapa-03` the screened changes exposed new branches or clipped the old ones, and the reciprocal visibility requirement was unverified. `mapa-04` gave the first qualifying pair. The recording has a distinct session and a long descending exterior wall through its entrance neighbourhood with a closed-room chain beneath it. The corresponding historical neighbourhoods on `mapa-06`, `mapa-07` and `mapa-09` have visibly different connected wall structures. This is visual deduplication of the reviewed neighbourhoods. [Frozen selection rule](FINAL_REPRESENTATION_SELECTION.md) · [Private selection and capture provenance](../local-data/phase-1-6-5/owner/selection.json)

| View | Source PTS / 30,000 | Time | Wall anchors | Fitted baseline | Largest held-out residual |
| --- | ---: | ---: | ---: | ---: | ---: |
| Primary region | 1,508,110 | 50.2703 s | 4 | 699.58 px | 0.00 px |
| Moved-player revisit | 2,222,688 | 74.0896 s | 4 | 699.58 px | 0.00 px |
| Distinct region | 1,080,767 | 36.0256 s | 6 | 602.29 px | 0.00 px |

The earliest readable player frame in the selected early neighbourhood precedes the confirmed cursor crossing on the revisit. The distinct control is the first readable contact-sheet sample with sufficient separation. Each view registers directly to the 82.0004 s frame through non-glyph wall corners and junctions. The shared study windows cover 378 × 280 px in registered coordinates and include the same wall intersection. Registered player movement is **100.42 px** against a **20 px** combined player and transfer allowance. The distinct study window has horizontal gaps of 115 px and 185 px from the two repeat windows, against a combined 12 px wall-transfer allowance. Rounded anchor picks reproduced integer translation. The 6 px per-view transfer allowance applies despite zero measured residual. [Private evaluator labels and registration](../local-data/phase-1-6-5/owner/manifest.json)

- The raw primary frame shows a yellow glyph beside the study window's upper edge. Its lower span is clearly visible inside the window. The centre of the complete glyph is approximately 1 px above the edge. The evaluator records the visible span for independent confirmation. At the same registered site in the moved source, the native cursor covers the glyph. The immediately preceding same-position frame shows the glyph before the cursor crosses. This makes the reverse visibility change observable in the original recording.
- The revisit shows a second yellow glyph on an overlay wall that the primary raw frame did not render at the registered location. Both projections are inside the fixed window. The later registration frame also shows the second glyph on that wall.

The earlier visible span is clipped, so its status as a usable centre and the existence of eligible bilateral pairs remain pending the independent annotations. Frames were selected using the recorded mechanisms, movement and walls. The 25% spatial floor stays fixed. [Private visibility evidence](../local-data/phase-1-6-5/owner/review/bilateral-visibility-evidence.png) · [Native study windows](../local-data/phase-1-6-5/owner/review/selected-window-review.png) · [Frozen evaluation protocol](FINAL_REPRESENTATION_PROTOCOL.md)

## Release and integrity

The lock covers the original source hashes and selected layout, the manifest and evaluator labels, the selection and evaluation protocols, both archived 1.6.4 diagnostic runs, all three frozen matcher configurations, the code and tests, and the exact 16-query, 58-slot roster. The scorer will distinguish the eight planned moved pairs from the operational, independently confirmed bilateral, and floor-eligible denominators. Below-floor pairs stay in the operational denominator. [Evaluation lock](../local-data/phase-1-6-5/owner/evaluation-lock.json)

**Lock SHA-256** `877fc9c32533691f623332acb48749811b8274c5b5aa04ebdcd56fe80fd5e8c6`.

- [0176b827c2.zip](../local-data/phase-1-6-5/release/0176b827c2.zip)
- [1dcc1ff640.zip](../local-data/phase-1-6-5/release/1dcc1ff640.zip)
- [63e3850229.zip](../local-data/phase-1-6-5/release/63e3850229.zip)
- [93f1396654.zip](../local-data/phase-1-6-5/release/93f1396654.zip)
- [b3b8fc8f4e.zip](../local-data/phase-1-6-5/release/b3b8fc8f4e.zip)
- [f26adb61ba.zip](../local-data/phase-1-6-5/release/f26adb61ba.zip)

All six ZIPs were reopened and verified for the exact three entries, CRC, neutral metadata, native PNG, blank template and original guide. The two packets per view share byte-identical images. The unmasked pixels match the source and the exterior is black. Each native source PNG reproduced byte for byte from its exact recording PTS. All 41 tests passed and the synthetic dataset validator accepted 10 layouts and 39 frames. The historical holdout and report hashes verified without rescoring. Both Phase 1.6.4 runs and their pinned source snapshots verified, with identical real comparison rows.

The Phase 1.6.4 control corrections also passed independent arithmetic checks. Exhaustive three-point assignment found one exact zero-radius fit in the original fixture, comprising point IDs 0, 2 and 3. The corrected negative contained no exact triple. The highest shortest altitude among the near-collinear fixture's triangles was 1.515 px, below the 6 px summed radius, so ambiguous weak hypotheses correctly abstain from resolved 2D alignment.

Dispatch one ZIP per isolated session using the exact universal prompt. Keep audit material private. The six actual returns and their intake records are the pending inputs. [Owner handoff](FINAL_REPRESENTATION_HANDOFF.md)
