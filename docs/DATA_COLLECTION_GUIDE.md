# Recording and annotation guide

## Record 10–15 independent layouts

1. Use D2R Catacombs Level 2 on Normal. Enter by the stairs from Level 1. Record the exact game build, game mode, automap mode, graphics mode, zoom and capture resolution. Keep these settings fixed across the pilot.
2. Start recording before taking the stairs. Save a clear automap frame at arrival and one after each of the first three discovery attempts. Keep the player marker visible. Record the timestamp even when an attempt reveals no new geometry or reveals several rooms. Use a route chosen without previously knowing the targets.
3. Keep recording through the first recognizable cue for each target. Show the actual transition to Level 3 and the waypoint interaction or label. Save a fully explored view, or overlapping views that cover the floor at the same settings. Keep enough overlap to align frames from landmarks already seen.
4. Assign a neutral ID to each layout. Retain which visits shared a layout. Use one representative per independent layout or known layout family. Split whole layouts into development and evaluation before analysis. Keep recordings and annotations in `local-data/` or another private location.

For the initial pilot, supply the footage or paired early and complete screenshots with timestamps, plus the build, settings and layout IDs. Use continuous footage where timestamps alone leave discovery uncertain. With screenshots alone, annotate uncertain discovery when the order cannot be established.

## Register and annotate

Fix screen axes with X right and Y down. Use the centre of the visible arrival room as the origin when it can be established from early frames. Register each frame using two separated landmarks with known locations from that frame or previously seen frames. Check a third visible landmark when available. If the anchors disagree because of camera movement, clipping or a settings change, flag the affected points as uncertain. A separate annotator can use later imagery to align complete geometry and truth to the same frame.

The manually estimated `origin_px` is the pixel position of the experiment origin in that image, and `px_per_unit` is the frame scale. Convert each point with `x = round((px_x - origin_px_x) / px_per_unit)` and the analogous formula for Y. Choose a fixed scale across the dataset, preferably one unit per pixel at the reference zoom. Keep the isometric projection already present in the image. These values measure positions and bearings on the automap plane. World coordinates and tile distances have different units.

Blind the early annotator to later frames. Record only recognizable room centres, connections visibly joining annotated rooms, confirmed dead ends and the direction of observed outgoing paths that disappear into unrevealed space. Omit traces whose interpretation is uncertain and mark the uncertainty. Annotate the stair-facing direction only if visible, or the axis alone if its polarity is unclear. Use a second independent reader on a subset of early frames. Record discrepancies in room/connection recovery, position, orientation and target discovery before using the data for a decision.

Count a target as discovered as soon as a recognizable stair or waypoint marker, label, geometry or interaction identifies it. Use `visible` from then onward, including after panning or clipping. Use `uncertain` whenever the sequence cannot establish whether the target had already been discovered. Verify the **Level 3** destination and annotate the stair entrance or waypoint glyph/interactable centre. Include the truth annotation's registration, rounding and marking error in the target's uncertainty radius. Leave unverifiable target anchors as `null`.

## Dataset files

The CLI accepts a directory containing the following UTF-8 JSON files. Copy the structure of the small [synthetic dataset](../fixtures/synthetic/metadata.json) and change its contents to the actual observations.

| File | Contents |
| --- | --- |
| `metadata.json` | `schema_version` (1), `dataset_id`, `kind` (`real` or `synthetic`), `scenario`, `capture` and `layouts`. The scenario is `{"game":"D2R","area":"Catacombs2","difficulty":"Normal","entry":"Catacombs1"}`. Capture fields are `build`, `mode`, `automap_mode`, `graphics`, `resolution` (width/height) and `zoom`. Each layout has `layout_id`, `group_id`, `split` (`development` or `evaluation`) and a `recording` reference. |
| `observations.json` | Array of rows with `layout_id`, `observation_id`, `stage` (0–3), `frame` (unique timestamp or still reference within the layout), `registration`, and `observation`. Registration contains `origin_px`, `px_per_unit`, `residual_px` (check residual), and `anchor_count`. Use null registration for wholly unreadable frames. |
| `truth.json` | Array with one row per layout. Include `layout_id`, `complete_geometry` with `rooms` and `connections`, `targets` keyed by NEXT and WP, and `visibility` keyed by observation ID and then target. Each known target has `position` and `error` in experiment units. Null means unavailable truth. |

### Observation fields

- `entrance_orientation` as one of `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW`, the axes `NS`, `NE_SW`, `EW`, `NW_SE`, or `null`.
- `player_position` as an integer point or `null` and `player_error` as an uncertainty radius in experiment units (use zero when the position is unavailable). For annotated positions, include marking and rounding error. The loader adds the registration residual converted to experiment units.
- `visible_rooms` as unique integer points and `visible_connections` as pairs of those points. Point order is arbitrary, and links are undirected.
- `unexplored_branches` as pairs like `[[2, 3], "NE"]`, and `dead_ends` as room points with exactly one observed departure. Use `uncertain_geometry: true` when reliable features were lost or the visible mask was unclear.

Record each frame once. A separate later frame with identical geometry is valid and contributes only at its own checkpoint. Use `validate` before benchmarking. The validator checks annotation consistency and layout isolation. Confirm the content and independence of the recording manually. [CLI commands](../README.md#uruchomienie-i-użycie)
