# Systems Mapping Workflow (`ags-gdd`)

Decomposes a game concept into explicit and implicit systems, dependency layers, milestone priorities, and `design/gdd/systems-index.md` (`map-systems`), or routes the next undesigned system (`next`).

## Mode & Density Controls

- **Arguments**: Blank runs full decomposition (Phases 1-5); `next` picks the highest-priority undesigned system and hands off to `design-system` (Phase 6).
- **Workflow tier**: `full` / `standard` require `systems-index.md` before `design-system`; `minimal` skips it (game brief replaces the index), though `map-systems` can still run voluntarily.
- **`docs.density`**:
  - `terse`: table plus one-paragraph `## Overview`.
  - `balanced`: brief paragraph per system in `## Overview` + dependency notes (default).
  - `thorough`: full system-by-system rationale + relationship analysis in `## Overview` and `## Dependency Map`.
- **Fixed table contract (`.ags/templates/systems-index.md`)**: NEVER add a `Why` or description column to **Systems Enumeration** (`# | System Name | Category | Priority | Status | Design Doc | Depends On`) or **Recommended Design Order** (`Order | System | Priority | Layer | Agent(s) | Est. Effort`). Consumers key on the **`Category`** column by name — never rename or drop `Category`. All rationale prose lives in conversation and in `## Overview` / `## Dependency Map`.

## Phase 1: Read Concept & Resume Check

- **Required**: Read `design/gdd/game-concept.md` (or `design/game-brief.md` at `minimal`). If neither exists, fail clearly and direct user to `ags-ideate brainstorm`.
- **Optional**: Read `design/gdd/game-pillars.md`; search `design/gdd/*.md` for already-authored GDDs; read `design/gdd/systems-index.md` if present.
- **If `systems-index.md` exists**: Summarize `[N]` systems (`[M]` designed, `[K]` not started) and prompt: `Update the index with new systems` / `Design the next undesigned system` / `Review and revise priorities`.

## Phase 2: Systems Enumeration

1. **Extract explicit systems** from Core Mechanics, Core Loop, Technical Considerations, and MVP Definition.
2. **Infer implicit systems**:
   - Inventory -> item database, equipment slots, weight/capacity rules, inventory UI, save serialization.
   - Combat -> damage calculation, health, hit detection, status effects, enemy AI, combat UI, death/respawn.
   - Open world -> streaming/chunking, LOD, fast travel, map/minimap, POI tracking, world persistence.
   - Multiplayer -> networking layer, lobby/matchmaking, state sync, anti-cheat, network UI.
   - Crafting -> recipe DB, gathering, crafting UI, success/failure, discovery.
   - Dialogue -> dialogue trees, dialogue UI, choice tracking, NPC state, localization hooks.
   - Progression -> XP, leveling, skill tree, unlock tracking, progression UI, progression save data.
3. **User review**: Present grouped by Category (`Core | Gameplay | Progression | Economy | Persistence | UI | Audio | Narrative | Meta`), showing Name, Category, 1-sentence description, Explicit vs Implicit. Prompt for missing systems, splits/merges, or cuts.
   - `collaborative`: loop until approved. `guided`: ask once, apply, proceed. `autonomous`: log via decision log and proceed.

## Phase 3: Dependency Mapping & Technical Boundary Gate

1. Map I/O, structural Framework, and UI dependencies (`UI` depends on gameplay, designed after it).
2. Sort into 5 layers: **Foundation** (zero deps) -> **Core** (Foundation deps only) -> **Feature** (Core deps) -> **Presentation** (UI/feedback) -> **Polish** (meta, tutorials, analytics, accessibility).
3. Detect circular dependencies; propose interface abstraction, simultaneous design, or contract split.
4. Highlight cycles, high-fan-in bottlenecks, and leaf nodes; confirm with user.
5. **Director gate `TD-SYSTEM-BOUNDARY`** (apply `modes.review_mode`: announce skip in `solo`/`lean`; in `full`, spawn `technical-director` reading `.ags/gates/td-system-boundary.md` with dependency map, layers, bottlenecks, cycle resolutions). On `REJECT`, revise boundaries before continuing; note `CONCERNS` inline.

## Phase 4: Priority Assignment & Scope Gate

1. Initial tiers: **MVP** (core loop + Foundation deps) -> **Vertical Slice** -> **Alpha** -> **Full Vision**.
2. Present tables and justify priorities in conversation combining technical necessity + player experience + specific game pillar (populate with THIS project's names/pillars, never generic placeholders). Prompt user to adjust tiers.
3. **Director gate `PR-SCOPE`** (apply `modes.review_mode`; in `full`, spawn `producer` reading `.ags/gates/pr-scope.md` with system counts per tier, estimated volume, team size, project timeline). On `UNREALISTIC`, adjust tiers before writing.
4. Compute final **Recommended Design Order** (dependency sort within each priority tier: MVP Foundation -> MVP Core -> MVP Feature -> Vertical Slice...).

## Phase 5: Draft, Write & Vision Check

1. Draft from `.ags/templates/systems-index.md` (Enumeration, Dependency Map, Design Order, High-Risk Systems, Progress Tracker). Present summary (totals by category, MVP count, first 3 in order, high-risk items).
2. Confirm write to `design/gdd/systems-index.md` per `modes.automation` (`collaborative` waits for explicit approval; `guided` summarizes destination and writes directly; `autonomous` writes and logs). If user declines -> **`BLOCKED`**.
3. **Director gate `CD-SYSTEMS`** (apply `modes.review_mode`; in `full`, spawn `creative-director` reading `.ags/gates/cd-systems.md` with systems index path, pillars, core fantasy, MVP system list). On `REJECT`, revise system set. On `CONCERNS`, record `> **Creative Director Note** (<Tier>): ...` **directly beneath `## Priority Tiers`** (there are no per-tier sections).
4. Update `production/session-state/active.md` (`Task: Systems decomposition`, `Status: Systems index created`, `File: design/gdd/systems-index.md`).

## Phase 6 & Phase 7: Handoff to `design-system` & Next Steps

- On `next` or user confirmation: pick highest-priority undesigned system and transition cleanly to `design-system` (do NOT duplicate its section cycle here), then prompt to continue to next system, pick another, or stop.
- Closing prompt options: `[A]` `ags-gdd design-system [first-system]` | `[B]` `ags-gate systems-design` (triggers `CD-SYSTEMS` + `TD-SYSTEM-BOUNDARY` formal sign-off) | `[C]` Stop here.
- Remind user to run `ags-design-review` in a **fresh session** after completing each GDD.
- **Context Window Awareness**: At >=70% context usage, advise opening a fresh session and running `ags-gdd map-systems next`.
