# Team Playbook: Narrative (`ags-team narrative`)

Orchestrates narrative direction, lore foundation, dialogue drafting, visual storytelling, level integration, consistency review, and i18n polish.

## Argument, Paths & Role Mapping

- **Argument check**: Requires `[narrative content description]` (e.g., `boss encounter cutscene`, `faction intro dialogue`, `tutorial narrative`). If omitted, output usage (`ags-team narrative <narrative content description>`) and stop without spawning roles.
- **Active-set (`team.size`)**:
  - **`individual`** (default): `writer` lens (via `game-designer`) only; escalate `narrative-director` only on an explicit pillar conflict. Other roles consulted through `game-designer`.
  - **`small`**: `narrative-director` + `writer` + (per `modes.review_mode`) `localization-lead`, `world-builder`.
  - **`studio`**: All narrative roles active + per-system writer reviews.
- **Role map**:
  - `narrative-director` lens -> `game-designer` (`.ags/roles/narrative-director.md`)
  - `writer` lens -> `game-designer` (`.ags/roles/writer.md`)
  - `world-builder` lens -> `game-designer` (`.ags/roles/world-builder.md`, template `.ags/templates/faction-design.md`)
  - `art-director` lens -> `art-ux-director` (`.ags/roles/art-director.md`)
  - `level-designer` lens -> `game-designer` (`.ags/roles/level-designer.md`)
  - `localization-lead` lens -> `producer` (`.ags/roles/localization-lead.md`)

Announce the active roster and unspawned roles before Phase 1.

### Concrete Output Paths (`design/narrative/`)

Every narrative deliverable must land under `design/narrative/` (consumed by `ags-art-ux`, `ags-design-review`, `ags-localize`, `ags-start`, `ags-team level`, and `.ags/gates/cd-narrative.md`):

| Role | Destination Path |
|---|---|
| `narrative-director` | `design/narrative/[content-slug]-brief.md` |
| `world-builder` | `design/narrative/lore/[topic].md` |
| `writer` | `design/narrative/dialogue/[scene-slug].md` |
| `art-director` | `design/narrative/[content-slug]-visual-direction.md` |

Because these paths are under `design/`, present compiled drafts or ensure explicit user confirmation before writing `design/narrative/` deliverables.

## Pipeline

### Phase 1: Narrative Direction (`narrative-director`)

- Define narrative purpose and story beat served.
- Identify participating characters, motivations, and fit in the overall arc (reference `.ags/templates/narrative-character-sheet.md` when profiling characters).
- Set emotional tone and pacing targets.
- List lore dependencies or new lore introduced.
- Output: narrative brief (`design/narrative/[content-slug]-brief.md`).

### Phase 2: World Foundation (Parallel)

Spawn all three concurrently when active:
- **`world-builder`**: Author/update lore entries for relevant factions, locations, and history; cross-reference existing lore for contradictions; assign canon levels (`design/narrative/lore/[topic].md`).
- **`writer`**: Draft character dialogue matching voice profiles; enforce lines under 120 characters, named variable placeholders (`{name}`), and localization-ready structure (`design/narrative/dialogue/[scene-slug].md`).
- **`art-director`**: Define visual direction for key characters (silhouette, archetype, distinguishing traits), environmental storytelling elements per space (props, lighting, spatial arrangement), and cutscene/scripted tone palette (`design/narrative/[content-slug]-visual-direction.md`).

**Phase Gate**: Collect all three Phase 2 outputs and capture user confirmation (per `modes.automation`) before Phase 3.

### Phase 3: Level Narrative Integration (`level-designer`)

Review the narrative brief and lore foundation; design environmental storytelling beats in level space; place narrative triggers, dialogue zones, and discovery points; ensure pacing serves both gameplay and story.

### Phase 4: Review and Consistency (`narrative-director`)

- Audit all dialogue against character voice profiles.
- Verify lore consistency across new and existing entries.
- Confirm narrative pacing matches level design.
- Verify all narrative mysteries have documented "true answers".
- Apply `.ags/gates/cd-narrative.md` when `modes.review_mode` is `full`.

### Phase 5: Polish (Parallel)

- **`writer`**: Final self-review — confirm dialogue box line limits, string keys (zero raw hardcoded UI/dialogue strings), and consistent named placeholder variables.
- **`localization-lead`**: Validate i18n readiness — string-key naming conventions, flag hardcoded formatting that breaks translation, verify >=30% character expansion headroom (e.g., German/Finnish), and check cultural assumptions needing locale variants.
- **`world-builder`**: Finalize canon levels for all new lore entries.

## Verdicts & Next Steps

- **COMPLETE**: Narrative brief, lore, dialogue, visual direction, integration, and i18n polish delivered with zero unresolved contradictions.
- **CONCERNS / NOT ASSESSED**: Localization or `cd-narrative` review skipped due to `team.size` / `modes.review_mode` (disclose explicitly).
- **BLOCKED**: Unresolved lore contradiction, missing GDD/pillar context, or `Proposed` ADR.
- **Next Skills**: `ags-design-review` on narrative docs, `ags-localize extract` to extract dialogue string keys, `ags-dev` to implement dialogue triggers.
