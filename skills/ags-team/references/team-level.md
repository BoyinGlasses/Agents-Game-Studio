# Team Playbook: Level (`ags-team level`)

Orchestrates narrative, lore, visual direction, spatial layout, encounter systems, accessibility, and QA planning for a game level or area.

## Argument, Context & Role Mapping

- **Argument check**: Target level or area (e.g., `tutorial`, `forest dungeon`, `hub town`, `final boss arena`).
- **Context gather**:
  - `design/gdd/game-concept.md`
  - `design/gdd/game-pillars.md`
  - Existing level docs in `design/levels/`
  - Relevant narrative docs in `design/narrative/`
  - Regional/faction world-building docs
- **Active-set (`team.size`)**:
  - **`individual`** (default): `game-designer` (`level-designer` lens) + `gameplay-coder`. Other roles routed through these two.
  - **`small`**: + `systems-designer` + `art-director` (via `art-ux-director`).
  - **`studio`**: + `narrative-director` + `world-builder` + `accessibility-specialist`.
- **Role map**:
  - `narrative-director` lens -> `game-designer` (`.ags/roles/narrative-director.md`)
  - `world-builder` lens -> `game-designer` (`.ags/roles/world-builder.md`)
  - `level-designer` lens -> `game-designer` (`.ags/roles/level-designer.md`)
  - `systems-designer` lens -> `game-designer` (`.ags/roles/systems-designer.md`)
  - `art-director` lens -> `art-ux-director` (`.ags/roles/art-director.md`)
  - `accessibility-specialist` lens -> `art-ux-director` (`.ags/roles/accessibility-specialist.md`)
  - `test-engineer` -> `.ags/roles/test-engineer.md`

Announce the active roster and unspawned roles before Step 1.

## Pipeline

### Step 1: Narrative + Visual Direction (Parallel)

Spawn all three concurrently when active:
1. **`narrative-director`**: Define narrative purpose, story beats, characters, dialogue triggers, and emotional arc (entering, during, leaving).
2. **`world-builder`**: Supply lore context (history, factions, ecology), environmental storytelling hooks, and area-specific world rules affecting gameplay.
3. **`art-director`**: Establish **directional** visual targets as explicit inputs to layout (not outputs of it): color temperature, lighting mood differentiated from adjacent areas, shape language direction, primary visual landmarks for wayfinding, anchored in `design/art/art-bible.md` if present.

**Gate 1**: Present narrative brief, lore foundation, and visual direction targets to the user and confirm before Step 2. Pass Step 1 visual targets explicitly as constraints to Step 2.

### Step 2: Layout and Encounter Design (`level-designer`)

Delegate to `level-designer` with full Step 1 outputs:
- Design spatial layout (critical path, optional paths, secrets) aligned with Step 1 visual landmarks.
- Define pacing curve (tension peaks, rest zones, exploration) aligned with Step 1 emotional arc.
- Place encounters with difficulty progression, environmental puzzles, and navigation challenges.
- Specify entry/exit connections to adjacent areas.

**Adjacent Area Dependency Check**: Search `design/levels/` for every adjacent area referenced. For any missing `design/levels/[area-name].md`, surface the gap without inventing content for the missing area and prompt the user:
- `(a)` Proceed with an explicit `UNRESOLVED` placeholder reference and record it in cross-level dependencies.
- `(b)` Pause and run `ags-team level [area-name]` first.

**Gate 2**: Present Step 2 layout (and any `UNRESOLVED` adjacent area dependencies) for user confirmation before Step 3.

### Step 3: Systems Integration (`systems-designer`)

Delegate to `systems-designer` to specify:
- Enemy compositions and encounter formulas
- Loot tables and reward placement
- Difficulty balance relative to expected player level/gear
- Area-specific mechanics or environmental hazards
- Resource distribution (health pickups, save points, shops)

**Gate 3**: Present Step 3 outputs and confirm before Step 4.

### Step 4: Production Concepts + Accessibility (Parallel)

Issue both delegations simultaneously and wait for both:
1. **`art-director`** (location-specific production pass from finalized Step 2 layout):
   - Produce concept specs for key spaces (entrance, encounters, landmarks, exits).
   - Separate unique vs shared pool assets.
   - Define layout-informed sight-line and lighting setups plus area VFX (weather volumes, particles, atmospherics).
   - Flag any locations where layout conflicts with Step 1 visual targets as production risks.
2. **`accessibility-specialist`**:
   - Verify non-color-dependent navigation clarity (shape/icon/sound cues reinforcing color on critical paths).
   - Flag puzzles exceeding a cognitive load of 3 simultaneous states.
   - Verify contrast in key gameplay areas for colorblind players.
   - Output severity-tagged concerns (`BLOCKING` / `RECOMMENDED` / `NICE TO HAVE`).

**Gate 4**: Present both Step 4 outputs. If any `BLOCKING` accessibility concern exists, do NOT advance until the user explicitly selects:
- `(a)` Return to `level-designer` and `art-director` to redesign flagged elements before Step 5.
- `(b)` Log the concern as an accepted accessibility gap in the final report and proceed to Step 5.

### Step 5: QA Planning (`test-engineer`)

Delegate to `test-engineer` to write critical-path test cases, boundary/edge cases (sequence breaks, softlocks), playtest checklist, and completion acceptance criteria (to `production/qa/test-cases/[level-name]-cases.md`).

### Step 6: Compile & Save Level Design Document

1. The orchestrator already holds all role outputs — compile the unified document directly against `.ags/templates/level-design-document.md` (do not re-spawn `level-designer` just to re-transmit context).
2. Request explicit user confirmation before writing `design/levels/[level-name].md`.
3. Output summary: area overview, encounter count, asset list, narrative beats, cross-team dependencies, `UNRESOLVED` adjacent level connections, accessibility concern resolution status, and active/skipped roster.

## Verdicts & Next Steps

- **COMPLETE**: Compiled level design document approved and written; no unacknowledged `BLOCKING` accessibility concerns.
- **CONCERNS**: Completed with logged `UNRESOLVED` adjacent areas or user-accepted accessibility gaps.
- **NOT ASSESSED**: Accessibility or art-bible alignment could not be checked due to missing baseline specs.
- **BLOCKED**: Unresolved prerequisite or user-halted `BLOCKING` accessibility/lore issue.
- **Next Skills**: `ags-design-review` on `design/levels/[level-name].md`, `ags-dev` to implement level stories, `ags-qa qa-plan` for level QA planning.
