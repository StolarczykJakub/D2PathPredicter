# Pilot registration validation

This document records the preliminary manual trial. The Phase 1.6 recheck reproduces its residuals, adds a separate pixel measurement and resolves NEXT visibility at the four released checkpoints. WP placement remains uncertain. [Final pilot recheck](PILOT_BENCHMARK_RESULTS.md#ground-truth-and-registration)

Pilot case is `mapa-07`, with the final automap at **96.3288 s** as a reference. Inspect the earlier [registration trial](../local-data/mapa-07/review/registration-check.json) alongside the [Role B measurements](../local-data/phase-1-6/role-b/registration-validation.json). Keep both files out of Role A releases.

## Acceptance rule before scoring

Use three or more visually identified shared features. The longest pair must span at least 64 native pixels and a held-out point must be over 6 pixels off that line. Compute the ratio of the pair's lengths and its rotation from the source to the reference. Use pure translation at fixed zoom when the ratio is 0.97–1.03, rotation is at most 2°, and every fitted and held-out residual is at most 6 native pixels. If the criteria fail or labels are ambiguous, record the frame as uncertain. These are screening limits for 1920×1080 manual marks. Target-position uncertainty also includes the mark and transfer error. Recheck a sector if its uncertainty crosses a boundary.

For two fitting anchors, average the two `reference - source` deltas. Compute each residual as the Euclidean distance between `source + delta` and the reference mark. The role-private JSON stores the original point pairs, fitting and held-out indices, distances, headings and errors for reproduction. X increases to the right and Y down. Image translation accounts for automap movement with the camera. The view retains its isometric diagonals. Convert image points into one map-relative frame first, then subtract the observed player position to score a bearing. World tile units require a separate transform.

## Manual checks at the same zoom

| Source frame | Translation into reference in px | Scale ratio | Rotation delta | Largest held-out error |
| --- | ---: | ---: | ---: | ---: |
| Stage 0 · 40.1734 s | (+424.5, −32.5) | 0.99601 | +0.711° | 1.58 px |
| Stage 1 · 44.1856 s | (+44, −160) | 1.00000 | 0° | 0 px |
| Stage 2 · 48.2108 s | (−688, −110) | 1.00000 | 0° | 0 px |
| Stage 3 · 52.2123 s | (+34, −252) | 0.99834 | +0.005° | 1.00 px |
| NEXT · 68.2788 s | (+28, +190) | 1.00000 | 0° | 0 px |
| WP · 80.2997 s | (−394, +181.5) | 0.99996 | −0.048° | 1.50 px |

All six checks pass the screening rule. Stage 2 initially had an almost collinear third point. A separately recognizable corner of the western wing provided an off-axis check. The measured errors describe agreement on manually picked landmarks from one recording. Zero residual can arise from rounded, coherent picks. The preparatory reviewer had access to both early and late imagery, so these results call for a second read before the dataset is frozen.

## Target decisions in the reference frame

| Target | Role B preliminary status | Evidence and coordinates |
| --- | --- | --- |
| NEXT | VERIFIED | The staircase label at 68.2788 s identifies Catacombs Level 3. The gray automap marker transfers to approximately **(1028, 705)** px in the 96.3288 s frame. The same marker is visible in the waypoint clip. Use a provisional 10 px marking radius pending independent review. |
| WP | UNCERTAIN | The named Level 2 waypoint is visible at 76.5000 s and 80.2997 s. The matched geometry establishes the frame alignment. The corresponding automap anchor could not be reliably distinguished, so the coordinate remains null. |

The Role B file keeps provisional visibility by checkpoint. NEXT is provisionally hidden at arrival. Its later early-stage first-appearance audit remains open, including the stage 3 area clipped by the HUD. WP visibility remains unresolved. Review the intervening footage before changing a stage to `hidden` or `visible`. [Target evidence](../local-data/phase-1-6/role-b/ground-truth-review.json)
