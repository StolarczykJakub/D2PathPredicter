# Single-image marker annotation

Use only `frame.png` and the blank `raw.json` in this packet. Open the image at native size or use a viewer that reports native coordinates. The canvas is 1920 × 1080. X increases rightward and Y downward from its top-left pixel. A black border masks pixels outside the study window. Use the original canvas coordinates even if you zoom or crop in your viewer.

Start timing when you open this guide. Use up to eight active minutes, including image inspection and JSON entry. Keep `protocol_version`, `packet_id`, `frame_sha256` and `resolution` unchanged. Fill the existing fields and return only the completed `raw.json`.

- In `player`, mark the visible current-player automap marker. Fill `status`, `px`, `error_px` and `note`. Use `OBSERVED` for a visible, localizable feature, `UNKNOWN` for insufficient evidence or `AMBIGUOUS` for competing readings. For an unresolved position, use null for `px` and `error_px` and write a short note.
- Search the entire unmasked window for distinct coloured glyphs drawn on automap wall traces or gaps. Record each visible physical glyph once. Exclude player marks, spell effects, scene lighting and interface or scene objects. Describe only visible appearance, such as “yellow vertical bar.”
- For each glyph use `id`, `status`, `appearance`, `center_px`, `segment_px`, `error_px` and `note`. Use a unique local ID such as `m1`. Mark the glyph centre and two endpoints of the visible coloured span along the trace. Exclude the adjoining wall. Use null for the span if only the centre is readable, and explain the obstruction. If the feature's position is unresolved, leave the centre, span and radius null and explain the uncertainty.
- Estimate a pixel radius for each observed player or glyph. For a glyph with measured extent, the same radius bounds the centre and either endpoint. Describe obstructions, suspected overlays, clipping or unreadable spans in `note` or `notes`.
- Fill `search_complete.markers` and `time_limit_reached` with Boolean values. Completeness refers to the unmasked visible window. Record elapsed time in `elapsed_minutes`. If you reach the limit, save the entries you have and describe unfinished areas in `notes`.

Point example

```json
{"status":"OBSERVED","px":[1010,480],"error_px":4,"note":"Readable blue automap outline"}
```

Glyph example

```json
{"id":"m1","status":"OBSERVED","appearance":"yellow bar","center_px":[828,576],"segment_px":[[824,573],[832,579]],"error_px":4,"note":"Visible coloured span"}
```
