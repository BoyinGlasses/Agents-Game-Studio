---
name: ags-ideate
description: "Use when brainstorming a game concept or lean game brief, building a throwaway concept prototype or --spike, or building a pre-production vertical slice. Do NOT use when decomposing systems into a systems index (-> ags-gdd), authoring full system GDDs (-> ags-gdd), or planning production sprints (-> ags-plan)."
---

# Game Ideation, Prototyping & Vertical Slice

Guides early concept exploration (`brief` / `brainstorm`), rapid hypothesis testing (`prototype` / `--spike`), and pre-production loop validation (`vertical-slice`).

## Contract

- **Inputs**: Optional genre/theme hint, mechanic question, or `--spike` / `--path [html|engine|paper]` flags; `project.yaml` / `project.local.yaml`; `design/game-brief.md` (`minimal`); `design/gdd/{game-concept,game-pillars,systems-index}.md`; `docs/architecture/{architecture,control-manifest}.md`; existing `prototypes/{index,GRAVEYARD}.md` and `PIVOT-NOTE.md`.
- **Roles**: `creative-director` (CD-PILLARS, CD-PLAYTEST), `art-ux-director` (lens: `art-director`; AD-CONCEPT-VISUAL), `technical-director` (TD-FEASIBILITY), `producer` (PR-SCOPE), `prototyper`, `scout` (optional lookup).
- **Outputs**: `design/game-brief.md` (`minimal` tier) or `design/gdd/game-concept.md` (`standard`/`full` tier); `prototypes/[name]-concept/` (`prototype.html`, engine project, or `rules.md` + `play-log.md`, `REPORT.md`, `PIVOT-NOTE.md`); `prototypes/[name]-spike-[date]/SPIKE-NOTE.md`; `prototypes/[name]-vertical-slice/` (`REPORT.md`, `PIVOT-NOTE.md`); `prototypes/index.md`; `prototypes/GRAVEYARD.md`; `production/session-state/active.md`.
- **Verification**: Concept selection and engine commitment explicitly confirmed with the user regardless of `modes.automation`; `design/game-brief.md` or `design/gdd/game-concept.md` aligns with `.ags/templates/game-brief.md` or `.ags/templates/game-concept.md`; prototype/slice source carries `NOT FOR PRODUCTION` header and zero imports from or into production code; playtest debrief captures specific observed evidence before generating `REPORT.md`.
- **Next Skill**: `ags-settings` (only when `engine.name` is unset), `ags-art-ux` (`art-bible`), `ags-gdd` (`map-systems` / `design-system`), `ags-design-review`, `ags-plan` (`create-stories` at `minimal`, `create-epics` after vertical slice `PROCEED`), or `ags-gate`.

## Preflight

Run once at startup and hold the resolved config for the run:

```bash
python .ags/cli.py preflight ags-ideate [mode-or-target]
```

- Apply `modes.workflow`, `docs.density` (`terse` / `balanced` / `thorough`), `modes.automation`, `modes.automation_always_ask`, and `modes.review_mode` (`--review [full|lean|solo]` overrides for this run).
- Read `engine.name`, `engine.language`, and `naming.*` from `project.yaml` (fall back to legacy `technical-preferences.md` if present; treat `[TO BE CONFIGURED]` as unset).

| Mode | Trigger | Reference |
|---|---|---|
| `brainstorm` | Concept ideation, pitch, pillars, or `minimal` lean brief | [references/brainstorm.md](references/brainstorm.md) |
| `prototype` | Throwaway single-mechanic build or `--spike` (~4h cap) | [references/prototype.md](references/prototype.md) |
| `vertical-slice` | Pre-production 3-5 min end-to-end loop + velocity log | [references/vertical-slice.md](references/vertical-slice.md) |

## Phases

### 1. Brainstorm (`brainstorm` / Lean Brief)
- **Tier branch first**:
  - `workflow: minimal`: Run the **Lean Brief** flow in [references/brainstorm.md](references/brainstorm.md) to write `design/game-brief.md` from `.ags/templates/game-brief.md`, list `ags-settings` in next steps ONLY if `engine.name` is absent/empty, and **STOP** (skip Phases 1-6, all director gates, and `game-concept.md`).
  - `workflow: standard` or `full`: Run Phases 1-6 interactively in [references/brainstorm.md](references/brainstorm.md) (Creative Discovery -> 3 concepts via Verb-First, Mashup, MDA Backward -> 30s/5m/Session/Progression loops + SDT -> 3-5 Pillars & 3+ Anti-Pillars -> Bartle/Quantic validation -> Scope & Feasibility) and write `design/gdd/game-concept.md` from `.ags/templates/game-concept.md` including the Visual Identity Anchor.
- **Unconditional prompts**: Concept selection (Phase 2) and Engine experience (Phase 6) ALWAYS prompt the user even in `autonomous` mode; never silently auto-select an engine.
- **Director gates** (`full` review mode only; announce skips in `lean`/`solo`): Spawn `creative-director` (`CD-PILLARS` -> `.ags/gates/cd-pillars.md`) and `art-ux-director` (lens: `art-director`; `AD-CONCEPT-VISUAL` -> `.ags/gates/ad-concept-visual.md`) in **parallel** after pillars lock; resolve CD blockers before visual anchor choice. Later in Phase 6, spawn `technical-director` (`TD-FEASIBILITY` -> `.ags/gates/td-feasibility.md`) and `producer` (`PR-SCOPE` -> `.ags/gates/pr-scope.md`).

### 2. Concept Prototype & Spike (`prototype` / `--spike`)
- Follow [references/prototype.md](references/prototype.md).
- **`--spike` / Mid-production spike**: Single technical or design question (or 60fps scene-load **performance spike**), hard 4h cap, outputs `prototypes/[name]-spike-[date]/SPIKE-NOTE.md` and updates `active.md`. No `CD-PLAYTEST`, no `PROCEED/PIVOT/KILL`.
- **Concept prototype**: Confirm intent (build, skip with recorded evidence, or spike) -> define a falsifiable hypothesis (`If player does X, feel Y, signal Z`) + riskiest assumption -> choose path (`HTML`, `Engine`, or `Paper` per genre table; note 50-133ms HTML latency and 2h engine sunk-cost rule) -> test ONE mechanic with `// PROTOTYPE - NOT FOR PRODUCTION` headers -> checkpoint `active.md` -> run 5-question playtest debrief -> write `REPORT.md` from `.ags/templates/prototype-report.md` and update `prototypes/index.md` -> run `CD-PLAYTEST` (`.ags/gates/cd-playtest.md`) in `full` mode when pillars exist.
- **Branching**: `PROCEED` (rewrite production from scratch; never refactor prototype code), `PIVOT` (write `PIVOT-NOTE.md`; **3 PIVOTs force a KILL decision**), or `KILL` (5-point confirmation checklist + append to `prototypes/GRAVEYARD.md`).

### 3. Vertical Slice (`vertical-slice`)
- Follow [references/vertical-slice.md](references/vertical-slice.md).
- Load concept, `systems-index.md`, `architecture.md`, `control-manifest.md`, and key GDDs -> define falsifiable validation question covering **3-5 minutes** of continuous core-loop gameplay (cut scope, never quality; 1-3 week cap) -> build with `// VERTICAL SLICE - NOT FOR PRODUCTION` headers and daily `active.md` updates -> enforce **Day 3 sunk-cost checkpoint** -> run 6-question debrief -> write `REPORT.md` from `.ags/templates/vertical-slice-report.md` with actual day-by-day **Velocity Log** -> update `prototypes/index.md` -> run `CD-PLAYTEST` (`full` mode) -> handle `PROCEED` / `PIVOT` (`PIVOT-NOTE.md`) / `KILL` (`GRAVEYARD.md`).
- **Multiplayer constraint**: Local prototypes and slices cannot validate network feel (0ms vs 80ms delay requires real peers or simulated latency).

## Gate & Verdict

- **`COMPLETE`** (`brainstorm`) / **`PROCEED`** (`prototype`, `vertical-slice`): Deliverable written and verified; concept, hypothesis, or full loop validated.
- **`SPIKE COMPLETE`** (`--spike`) / **`SKIPPED`** (proven evidence recorded): Question answered or prototype waived with explicit evidence.
- **`PIVOT`**: Direction invalidated; `PIVOT-NOTE.md` written (escalate to `KILL` check at 3+ pivots).
- **`NOT ASSESSED`** *(ranks above `COMPLETE`/`PROCEED` and below `BLOCKED`/`KILL`)*: Required context (`game-concept.md`, `systems-index.md`, `control-manifest.md`), preflight config, or user playtest observations were unavailable or uncollected; state exact missing evidence and remediation — never emit `PROCEED` without observed playtest evidence.
- **`KILL`** / **`BLOCKED`**: Concept terminated (`GRAVEYARD.md` updated), user declined write, hypothesis too vague, or director gate returned `REJECT`.
