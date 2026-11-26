# Project scope

Estimate where to look for **NEXT**, the exit to the designated next area, and **WP**, the area's waypoint. A target is eligible only while it is still hidden. The eventual desktop assistant can update its estimate as visible geometry changes and display a direction when the evidence supports one. A bearing can point across a wall and carries no routing or teleport guarantee.

## Constraints

- Local, deterministic where possible, and CPU-only. The eventual desktop targets are below 2% CPU on the target machine, under 100 MB RAM, and a prediction update under 100 ms. Prefer offline precomputation and run updates when the observation changes.
- Permitted inputs are visible game imagery and legally accessible static game data. The first experiment consumes offline fixtures and simulated observations. There is no game launch, live capture, GUI, overlay, real-time processing, server, or AI model in the experiment.
- Game process memory reading, DLL injection, game file modification, packet interception, anti-cheat bypass, movement or input automation, combat, item and monster detection, loot filtering, and health, mana or potion monitoring are out of scope.
- Phase 0 covers source review, feasibility, methodology and implementation planning. Phase 1 is an approval gate. Production UI and seed recovery are outside Phase 1.

## First test area

| Area | Evidence and implications |
| --- | --- |
| Forgotten Tower, Cellar Levels 1–5 | Blizzard lists five cellar levels and no waypoint. Levels 1–4 can test progression down to the next cellar. Level 5 is the terminal floor for this definition of NEXT. The `diablo2-maps` Tower Level 4 experiment provides a classic-data example of room and orientation identification, with a detailed manual observation protocol. [Blizzard's Act I area map](https://classic.battle.net/diablo2exp/maps/act1.shtml), [Tower experiment](https://github.com/emmericp/diablo2-maps#using-the-seed-finder) |
| **Catacombs Level 2** | Has both a waypoint and an exit to Level 3. The reconstructed classic maze code explicitly selects next-level and waypoint presets. Start at the up stairs from Level 1 so both targets can still be hidden. Use one difficulty and one arrival context. [Blizzard's Act I area map](https://classic.battle.net/diablo2exp/maps/act1.shtml), [classic Catacombs maze branch](https://github.com/ThePhrozenKeep/D2MOO/blob/master/source/D2Common/src/Drlg/DrlgMaze.cpp#L652-L685) |
| Durance of Hate Level 2 | Also has both targets. The reconstructed classic generator searches for matching existing presets and has fallback room placement in its dedicated routine. The Catacombs branch gives a shorter path to inspect for the initial experiment. Durance is a useful second-area transfer test. [Blizzard's Act III area map](https://classic.battle.net/diablo2exp/maps/act3.shtml), [classic Durance placement routine](https://github.com/ThePhrozenKeep/D2MOO/blob/master/source/D2Common/src/Drlg/DrlgMaze.cpp#L2370-L2465) |

Catacombs Level 2 exercises the full target contract in one area. **Normal and stairs arrival** are fixed experimental choices. Record any later D2R sample's exact build, game mode and difficulty. Classic area listings and code establish the rationale for selecting the area. Direct D2R validation is still open.
