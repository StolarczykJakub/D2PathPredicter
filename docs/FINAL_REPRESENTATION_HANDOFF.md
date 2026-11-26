# Phase 1.6.5 owner handoff

Send only one individual ZIP per fresh, isolated reviewer or session. The private manifest, evaluation lock, footage, other packets and earlier returns stay owner-side. Keep each package independent of all other packets, sources and context.

## Universal annotator prompt

> Open the single attached ZIP and follow its README.txt. Use only the files in that ZIP. Return the completed raw.json from that packet and include any limitations in its notes.

Use this exact text for each package. Each ZIP provides the original single-image marker guide, one native screenshot and one blank `marker-raw-v1` template. The measurement conventions and eight-minute limit come from the README.

## Returns

Record the opaque packet ID, reviewer and session identifiers where available, dispatch and receipt times with timezone, exposure or deviation, original filename, byte count and SHA-256. Leave unavailable fields unknown. Each reviewer returns the completed `raw.json` from their packet. Preserve the original bytes, including incomplete or time-limited returns. Attribute any later correction to its own file. Keep the six raw files separate using their packet IDs. On handoff, provide the six originals and the owner-side intake records so the frozen roster can be reconciled before scoring.

```powershell
python -B -m research.marker_fingerprint.final_holdout --verify
```

Use the verified release and evaluation lock together. Preparation ends at this handoff. The protocol requires six actual independent returns for intake. [Frozen evaluation protocol](FINAL_REPRESENTATION_PROTOCOL.md)
