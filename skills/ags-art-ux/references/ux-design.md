# UX, HUD, Interaction Patterns & Accessibility Authoring (`ags-art-ux`)

Section-by-section authoring for screen/flow UX specs, HUD design, interaction pattern library, and project-wide accessibility requirements.

## 1. Mode Resolution, Workflow & Density

| Argument | Mode | Output File | Section Guide (load ONLY active mode) |
|---|---|---|---|
| `hud` | HUD design | `design/ux/hud.md` | [sections-hud.md](sections-hud.md) |
| `patterns` | Interaction pattern library | `design/ux/interaction-patterns.md` | [sections-patterns.md](sections-patterns.md) |
| `accessibility` | Project-wide accessibility requirements | `design/accessibility-requirements.md` | `.ags/templates/guidance/accessibility-requirements-guide.md` (load active section only) |
| `<screen-name>` | Screen or flow UX spec (kebab-case) | `design/ux/[argument].md` | [sections-ux-spec.md](sections-ux-spec.md) |

- **`accessibility` path invariant**: MUST write to `design/accessibility-requirements.md` (project-wide standard referenced by `.ags/workflow-catalog.yaml`, gates, and architecture reviews — NEVER under `design/ux/`).
- **No argument**: Prompt user (`Specific screen or flow` / `Game HUD` / `Interaction pattern library` / `Accessibility requirements` / `Help me decide`).
- **`workflow` scope**: `full` (per screen), `standard` (core screens: main menu, HUD, primary gameplay loop), `minimal` (optional, can run voluntarily).
- **`docs.density`**: `terse` (wireframe descriptions + interaction bullets), `balanced` (wireframes + flow paragraphs), `thorough` (full prose + user-research summaries + alternatives).

## 2. Gather Context (Before Any Questions)

- **2a Game concept**: Read `design/gdd/game-concept.md` (warn and recommend `ags-ideate brainstorm` if missing; continue if user requests).
- **2b Player journey**: Read `design/player-journey.md` (phase, emotional arrival state, player need, critical moments). If missing, proceed with warning and add an Open Question recommending authoring it from `.ags/templates/player-journey.md` (no skill generates it; never create a circular self-reference).
- **2c GDD UI Requirements**: Search `design/gdd/*.md` for `^#+ .*UI Requirements`.
  - **In `hud` mode**: Count total GDD files **N** first and compare against matched files. A GDD without a `UI Requirements` heading is NOT automatically headless — list all unmatched GDDs and confirm with the user which are genuinely headless before excluding them from the HUD inventory.
- **2d Existing UX specs**: Check `design/ux/*.md` for linked screens' entry/exit points.
- **2e Pattern library**: Read catalog index only of `design/ux/interaction-patterns.md` if present.
- **2f-2g Art & Accessibility**: Read visual direction in `design/art/art-bible.md` and committed tier in `design/accessibility-requirements.md` if present.
- **2h Platform & Input Methods**: Read `platform.*` from `project.yaml` (`targets`, `primary_input`, `gamepad_support`, `touch_support`; derive input methods from `PC`/`Web` -> keyboard/mouse + Full/Partial gamepad/touch + `primary_input`), falling back to legacy `technical-preferences.md` (`Input Methods`). If neither is configured, ask ONCE (`Keyboard/Mouse only` / `Gamepad only` / `Both (PC + Console)` / `Touch (mobile)` / `All of the above`) and recommend `ags-settings`; never re-ask per section.
- **2i Context Summary**: Present collected summary and confirm if anything else needs reading.

## 2b. Retrofit Mode Detection

If target output file already exists:
- Read file, build per-section status table (`Complete` / `Empty` / `Placeholder` for non-`[To be designed]` bodies), and state that only `[N]` incomplete sections will be authored.
- Skip Section 3 skeleton creation; edit placeholders in-place only — NEVER overwrite existing content.

## 3. Create File Skeleton (Fresh Authoring)

Confirm target path creation (`design/ux/[filename].md`, or `design/accessibility-requirements.md` for `accessibility`), write skeleton immediately, and update `production/session-state/active.md`.

- **UX Spec Skeleton**: Header (`Status: In Design`, `Author`, `Last Updated`, `Journey Phase(s)`, `Template: UX Spec`) + `## Purpose & Player Need`, `## Player Context on Arrival`, `## Navigation Position`, `## Entry & Exit Points`, `## Layout Specification` (`### Information Hierarchy`, `### Layout Zones`, `### Component Inventory`, `### ASCII Wireframe`), `## States & Variants`, `## Interaction Map`, `## Events Fired`, `## Transitions & Animations`, `## Data Requirements`, `## Accessibility`, `## Localization Considerations`, `## Acceptance Criteria`, `## Open Questions` (all initialized with `[To be designed]`).
- **HUD Design Skeleton**: Header + `## HUD Philosophy`, `## Information Architecture` (`### Full Information Inventory`, `### Categorization`), `## Layout Zones`, `## HUD Elements`, `## Dynamic Behaviors`, `## Platform & Input Variants`, `## Accessibility`, `## Open Questions`.
- **Interaction Pattern Library Skeleton**: Header + `## Overview`, `## Pattern Catalog`, `## Patterns`, `## Gaps & Patterns Needed`, `## Open Questions`.
- **Accessibility Requirements Skeleton** (mirrors `.ags/templates/accessibility-requirements.md` — author `## Accessibility Tier Definition` first because downstream gates require an explicit committed tier, not `[To be designed]`): `## Accessibility Tier Definition`, `## Visual Accessibility`, `## Motor Accessibility`, `## Cognitive Accessibility`, `## Auditory Accessibility`, `## Platform Accessibility API Integration`, `## Per-Feature Accessibility Matrix`, `## Accessibility Test Plan`, `## Known Intentional Limitations`, `## Audit History`, `## External Resources`, `## Open Questions`.

## 4-8. Section Authoring, Cross-Reference, Specialist Coordination & Handoff

1. **Section cycle** (load **only** the single guidance file matching active mode): `Context -> Questions -> Options -> Decision -> Draft -> Approval -> Write -> update active.md`. Respect `modes.automation` (`collaborative` approves & confirms writes per section; `guided` writes approved sections directly; `autonomous` logs and writes).
2. **Cross-reference check (Phase 5)**: Verify (1) GDD UI Requirements coverage, (2) Pattern library alignment (flag new invented patterns), (3) Navigation entry/exit symmetry across specs, (4) Accessibility tier compliance, (5) Empty states defined for every data-dependent element.
3. **Specialist coordination**: `art-ux-director` (`ux-designer` primary; `art-director` aesthetics/layout feel), `gameplay-coder` (`ui-programmer` implementation feasibility), `game-designer` (`game-designer` data ownership; `narrative-director` lore/item text). All file writes stay in main session; uphold aesthetic deference (ask user on taste choices) and conflict surfacing (never silently drop GDD reqs or bloat layouts).
4. **Handoff & resume**: Update `active.md`, cross-link related specs without silent edits, and direct to `ags-art-ux ux-review` before `ags-team ui` or `ags-gate pre-production`. On interruption, resume from `active.md` and remaining `[To be designed]` headings.
