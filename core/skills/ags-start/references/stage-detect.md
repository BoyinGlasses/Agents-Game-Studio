# Project Stage Detection (`ags-start stage [role]`)

Full project state scan, artifact-vs-config cross-check, tier-scoped gap analysis, and stage report writer.

## Phase 1: Deterministic & Qualitative Scans

Run the full artifact check first:

```bash
python .ags/cli.py check artifacts
```

Treat `NO_CHECK` totals as the explicit bound on what existence checks can verify. Then inspect content quality and counts:

- **Design (`design/`)**: Count system GDDs in `design/gdd/*.md`; check `game-concept.md` (or `design/game-brief.md` at `minimal`), `game-pillars.md`, `systems-index.md` (total vs designed), GDD section completeness (`Overview`, `Detailed Rules`/`Detailed Design`, `Edge Cases`, etc.), `design/narrative/`, `design/levels/`.
- **Source Code**: Resolve code root from `engine.name` (`src/` Godot, `Assets/` Unity, `Source/` Unreal). **If code root is unresolved, report `NOT ASSESSED — code root unresolved` rather than reporting zero files.** Count source files, modules with 5+ files, core/gameplay/ai/networking/ui folders, rough scale.
- **Production (`production/`)**: Active sprint plans, milestones, roadmap docs.
- **Prototypes (`prototypes/`)**: Count directories, documented (`REPORT.md`/`README.md`) vs undocumented.
- **Architecture (`docs/architecture/`)**: Count ADRs (`adr-*.md`) and `architecture.md`.
- **Tests (`tests/`)**: Count test files and rough coverage scope.

## Phase 2: Classify Stage & Compare Against Config

Read `project.stage` from preflight (`project.yaml` -> `production/stage.txt` fallback). **Always run the artifact heuristics even when `project.stage` is configured, then compare both:**

| Stage | Heuristic Indicators |
|---|---|
| `Concept` | No concept doc / game brief |
| `Systems Design` | Concept exists; `systems-index.md` missing or incomplete |
| `Technical Setup` | `systems-index.md` exists; engine not configured |
| `Pre-Production` | Engine configured; resolved code root has `<10` source files |
| `Production` | Resolved code root has `10+` source files, active sprints/dev |
| `Polish` | Explicit via `ags-gate` Production -> Polish |
| `Release` | Explicit via `ags-gate` Polish -> Release |

When configured stage and artifact heuristics disagree, state BOTH explicitly (e.g., `"Configured stage: Release. Observed artifacts indicate Pre-Production (...). These disagree — configured stage may be stale or work lives outside this repo."`) and set Stage Confidence to `CONCERNS`.

## Phase 3: Tier-Scoped Collaborative Gap Questions

Surface gaps strictly per resolved `modes.workflow`:
- **`full`**: Flag every missing doc type (`game-concept.md`, GDDs, art bible, UX specs, ADRs) as a gap.
- **`standard`**: Flag missing GDDs for built systems and missing Foundation/critical ADRs; do NOT flag absent art bible unless visual-asset stories exist, and do NOT flag non-core UX specs.
- **`minimal`**: `design/game-brief.md` + configured engine is the healthy state; do NOT flag absent GDDs, art bible, UX specs, or ADRs as gaps.

Ask clarifying questions for surfaced gaps rather than blindly listing files (e.g., code exists without GDD -> prototyped first or `ags-adopt reverse`? ADRs without overview -> create via `ags-architect`? No sprints -> external tracker? Concept without systems index -> `ags-gdd map`?).

If a role filter argument was passed (`programmer`, `designer`, `producer`, `general`), focus recommendations on that role's domain.

## Phase 4: Present Summary & Confirm Write

Build the report using `.ags/templates/project-stage-report.md` (with `Stage Confidence`: `PASS` | `CONCERNS` | `NOT ASSESSED` | `FAIL`), show the summary, gaps, and priority next steps inline, then confirm with the user (respecting `modes.automation`) before writing `production/project-stage-report.md`.

## Phase 5: Tier-Filtered Next Steps

Recommend follow-ups ONLY for gaps allowed by `modes.workflow` (do not recommend `ags-adopt reverse` for missing GDDs at `minimal`):
- Missing systems index -> `ags-gdd map`
- Missing design/architecture/concept docs from existing code/prototypes -> `ags-adopt reverse <design|architecture|concept> <path>`
- Missing ADRs -> `ags-architect`
- Missing sprint plan -> `ags-plan sprint`
- Milestone checkpoint -> `ags-plan milestone`
