# Phase 1.6.3 owner handoff

The release folder contains only the twelve individual ZIPs. Keep the owner folder, manifest, plan, packet list, source recordings and other returns private. The owner manifest supplies the private calibration/holdout assignment and frame pairing.

## Universal blind annotator prompt

Use the following exact text with one ZIP in an isolated fresh session:

> Open the single attached ZIP and follow its README.txt. Use only the files in that ZIP. Return the completed raw.json from that packet and include any limitations in its notes.

## Checklist

1. Use a new isolated reviewer or session for each ZIP, with no prior frames, instructions, repository access or shared returns. Attach exactly one ZIP and use the prompt above. The ZIP contains its own complete guide and blank template.
2. Record the packet ID, reviewer or session identifier, dispatch and receipt times, and any reported exposure or deviation. Keep the returned file's original bytes and record SHA-256. Use the packet ID to associate the anonymous `raw.json` with the correct release.
3. Return the six calibration JSONs separately from the six holdout JSONs. Keep the holdout files inaccessible to calibration and evaluation until the calibration lock is written. Partial or time-limited responses are still original evidence. Keep any correction as a separate file.

[Private release folder](../local-data/phase-1-6-3/release/) · [Private owner manifest](../local-data/phase-1-6-3/owner/manifest.json) · [Frozen screen plan](INDEPENDENT_LAYOUT_SCREEN_PLAN.md)
