# Phase 1.6 blind annotation guide

Begin with one development pilot. Assign three different reviewers to roles A, B and C. The preparatory review saw both early and late footage, so its geometry marks cannot serve as the independent Role A output.

| Role | Inputs and handoff |
| --- | --- |
| A · Early geometry | One released early-frame ZIP at a time. Return one completed annotation per stage. |
| B · Ground truth | Original clip, late automap, target clips and private registration evidence. Record verified target anchors, uncertainty and first visibility without editing Role A output. |
| C · Evaluation | Frozen Role A outputs, reviewed ground truth and the private alias map. Check independence, assemble the existing dataset schema and release the benchmark only when both splits pass. |

## Launch Role A

1. Choose a reviewer who has never seen the original clip, later frames, target coordinates or this project's previous review. Use another machine or an isolated account or session that can access only the files you supply. For an AI reviewer, start a fresh context with no previous transcript, repository, shared file tools or target evidence attached.
2. From `local-data/phase-1-6/role-a-release`, give the reviewer **only** `b16-k9w4-00.zip`. On their side, extract it to an empty directory. Open `README.txt`, view `frame.png` at native resolution or with a pixel-coordinate viewer, and fill `observation.json` in that directory. The only supplied identity is the case and frame ID.
3. Receive the completed file and record its SHA-256, the reviewer ID, frame ID and elapsed annotation minutes. Keep the returned bytes under that stage ID. Check that the original `frame_sha256`, `case_id` and `stage` were preserved and that the reply uses only visible evidence. Repeat this controlled release and return for `01`, `02` and `03`, one at a time. Earlier frozen notes may be visible to the reviewer.
4. On a subset, have a second fresh reviewer annotate the same packet in another isolated context. Compare player and entrance marks, room counts, links, boundary states and interpretation. Record disagreements in a separate review entry so returned annotations remain auditable.

The packets keep native pixel coordinates, mask two interface rectangles with the game label and portrait, and omit the clip name, source time, map folder, later stages, target labels and prior analysis. Stage-by-stage release protects against knowledge from later observations. If any reviewer sees later evidence, record the affected entries as non-blind and start again with an independent reviewer.

```powershell
# In the isolated review directory, using only the archive received for this stage
Expand-Archive -LiteralPath .\b16-k9w4-00.zip -DestinationPath .\stage-00
# After completing stage-00\observation.json, record the exact returned file hash
Get-FileHash -LiteralPath .\stage-00\observation.json -Algorithm SHA256
```

## Owner-side verification

Run from the project root. Building requires FFmpeg on PATH. Use a new output folder when reproducing a release. Before using the builder on other clips, inspect the two fixed masks against their early geometry and check for identifying text outside the masks.

```powershell
python -m research.geometry_experiment.blind_packets local-data/phase-1-6/role-a-release b16-k9w4
python -m research.geometry_experiment.blind_packets local-data/phase-1-6/rebuild b16-k9w4 --from-early local-data/mapa-07/review/early
```

The existing experiment schema receives normalized player and room positions, visible links, confirmed dead ends and directional frontiers. Preserve wall observations, visibility boundaries, original uncertainty notes and audit metadata alongside the frozen Role A response. The evaluator retains all target and private coordinate files. [Registration](REGISTRATION_VALIDATION.md) · [Quality checks](DATASET_QUALITY_REPORT.md)
