# GDD vs Implementation Content Audit (`ags-design-review`)

Audits planned content counts in GDDs against implemented artifacts on disk.

## Tier Applicability, Modes & Insufficient-Input Gate

- **Modes**: Blank (full audit across all systems) | `[system-name]` (single system) | `--summary` (inline Gap Table only, no file write).
- **`workflow` scope**: `full` (all GDD specs), `standard` (required sections only), `minimal` (N/A — no systems index).
- **Insufficient-Input Gate (check BEFORE computing gaps)**:
  - Record `FOUND` or `ABSENT` for `design/gdd/systems-index.md`, `design/registry/entities.yaml`, system GDDs, `assets/data/`, and resolved code root.
  - When `systems-index.md` or source GDDs are `ABSENT`, emit **`NOT ASSESSED — NO DATA`** (never divide by zero over unspecified counts, and never report missing files as `0` gap / clean `COMPLETE`).

## Phase 1: Context & Dual L0 Pre-Scan

1. Read `design/gdd/systems-index.md`.
2. **Registry-first count**: If `design/registry/entities.yaml` has live entries, extract names strictly under `entities:` and `items:` (NOT `formulas:`/`constants:`) as the planned named-content baseline.
3. **Dual L0 pre-scans across `design/gdd/*.md`** (never combine into one regex):
   - **Scan A (Denominator check)**: Count total system GDDs **N** and match `^## Summary` (fail open — unmatched GDDs predate `## Summary` and stay in scope for full reads).
   - **Scan B (Content-count narrowing)**: Match `[0-9]+[[:space:]]+(enemies|enemy types|levels|areas|maps|stages|items|weapons|equipment|abilities|skills|spells|cutscenes|conversations|dialogue scenes|bosses|quests)|(enemy|item|weapon|ability|level) types:`.
   - For full audit, full-read only GDDs matched by Scan B (or predating Summary) not already covered by `entities.yaml`. Note pure-mechanics GDDs with no count language without full reads.
4. Build Content Inventory Table (`System | Content Type | Specified Count/List | Source GDD`); flag qualitative-only entries as `Unspecified`.

## Phase 2: Implementation Scan (Code Root Required)

1. **Resolve code root** (`src/` Godot, `Assets/` Unity, `Source/<Module>/` Unreal) from `project.yaml` `engine.name` (else legacy `technical-preferences.md`, else single unambiguous tree root). **If unresolved: report `NOT ASSESSED — code root unresolved` for code-root checks — NEVER default to `src/` and NEVER report zero hits.**
2. Scan by content category:
   - **Levels / Maps**: `assets/**/*.{tscn,unity,umap}` + resolved code root scene files in `levels/`, `areas/`, `maps/`, `worlds/`, `stages/` (note UI vs gameplay scene caveat).
   - **Enemies / Characters / NPCs**: `assets/data/**/{enemies,characters}/**` + `<code_root>/**/{enemies,characters}/**` (`.json`, `.tres`, `.asset`, `.yaml`, prefabs/scenes).
   - **Items / Equipment / Loot**: `assets/data/**/{items,equipment,loot}/**`.
   - **Abilities / Skills / Spells**: `assets/data/**/{abilities,skills,spells}/**`.
   - **Dialogue / Cutscenes**: `assets/**/*.{dialogue,csv,ink}` + `assets/data/` dialogue files.
   - **Quests / Missions**: `assets/data/**/{quests,missions}/**`.

## Phase 3-5: Gap Table, Output & Follow-Up

1. Compute status per row: `COMPLETE` (`Found >= Specified`), `IN PROGRESS` (50-99%), `EARLY` (1-49%), `NOT STARTED` (0%). Flag `HIGH PRIORITY` if `NOT STARTED`/`EARLY` AND MVP/Vertical Slice/blocking downstream. Overall gap `% = (Specified - Found) / Specified * 100`.
2. For `--summary`, print Gap Table + Summary inline without writing files. Otherwise confirm writing `docs/content-audit-[YYYY-MM-DD].md` (Summary, caveat note, Gap Table, HIGH PRIORITY Gaps, Per-System Breakdown, Recommendations, Unspecified Content Counts).
3. Offer backlog story creation via `ags-plan` (`create-stories`) or `ags-gdd` (`quick-design`), and suggest `ags-plan sprint-plan` if gap >50%. Verdict: **`COMPLETE`** or **`NOT ASSESSED`**.
