---
name: ags-gdd
description: "Use when decomposing a game concept into a systems index, authoring or retrofitting a per-system GDD section by section, or writing a lightweight quick design spec. Do NOT use when brainstorming initial concepts (-> ags-ideate), authoring art/UX specs (-> ags-art-ux), or reviewing existing GDDs (-> ags-design-review)."
---

# Systems Mapping & GDD Authoring

Decomposes concepts into dependency-ordered systems (`map-systems`), authors or retrofits per-system GDDs incrementally (`design-system`), and specs sub-week tuning or feature changes (`quick-design`).

## Contract

- **Inputs**: `design/gdd/game-concept.md` (or `design/game-brief.md` at minimal), `design/gdd/game-pillars.md`, `design/gdd/systems-index.md`, `design/registry/entities.yaml`, `docs/consistency-failures.md`, `docs/architecture/adr-*.md`, `docs/engine-reference/<engine>/VERSION.md`, `design/quick-specs/*.md`, `assets/data/`, `project.yaml`.
- **Roles**: `game-designer` (lenses: `systems-designer`, `economy-designer`, `narrative-director`, `writer`, `level-designer`, `world-builder`), `creative-director` (CD-SYSTEMS, CD-GDD-ALIGN, Player Fantasy), `technical-director` (TD-SYSTEM-BOUNDARY), `producer` (PR-SCOPE), `qa-lead` (Acceptance Criteria), `art-ux-director` (lenses: `art-director`, `ux-designer`), `tech-artist` (lenses: `audio-director`, `sound-designer`), `gameplay-coder` (lenses: `ai-programmer`, `ui-programmer`, `engine-programmer`).
- **Outputs**: `design/gdd/systems-index.md`, `design/gdd/<system>.md`, `design/registry/entities.yaml` (created/updated on confirmation), `design/quick-specs/<title>-<YYYY-MM-DD>.md`, `production/session-state/active.md`.
- **Verification**: Run `python .ags/cli.py check gdd design/gdd/<system>.md` after GDD authoring; preserve fixed Systems Enumeration columns (`#`, `System Name`, `Category`, `Priority`, `Status`, `Design Doc`, `Depends On`); author `## Summary` at every tier; verify registry conflicts on Sections C and D; hand off to fresh-session `ags-design-review` (never inline).
- **Next Skill**: `ags-design-review` (fresh session for completed GDDs, or `consistency` mode), `ags-art-ux` (`asset-spec` or `ux-design` when flagged), `ags-architect` (once MVP GDDs are reviewed), `ags-dev` / `ags-plan` (after quick spec), `ags-gate`.

## Preflight

Run once at startup and hold resolved values for the run:

```bash
python .ags/cli.py preflight ags-gdd [mode-or-target]
```

- Resolve `modes.workflow` (`workflow_overrides.system_overrides.<stem>` where `<stem>` is the `design/gdd/<stem>.md` filename stem, `TR-[system]-NNN` alias fallback only -> `modes.workflow` -> `modes.rigor`), `workflow_overrides.tuning_knobs`, `workflow_overrides.edge_cases`, `docs.density`, `modes.automation`, and `modes.review_mode` (`--review [full|lean|solo]` overrides).
- Read `engine.name` and `engine.version` from `project.yaml` (fall back to legacy `technical-preferences.md` if present; treat `[TO BE CONFIGURED]` as unset).

| Mode | Trigger | Reference |
|---|---|---|
| `map-systems` | `map`, `map-systems`, or `next` (auto-select next undesigned system) | [references/map-systems.md](references/map-systems.md) |
| `design-system` | `<system-name>`, `design <system>`, or `retrofit design/gdd/<file>.md` | [references/design-system.md](references/design-system.md) |
| `quick-design` | `quick <change>` (Tuning, Tweak, Addition, New Small System <= 1 week) | [references/quick-design.md](references/quick-design.md) |

## Phases

### 1. Systems Decomposition (`map-systems` / `next`)
- Follow [references/map-systems.md](references/map-systems.md).
- **`next` mode**: Read `design/gdd/systems-index.md`, select highest-priority undesigned system in design order, confirm, and hand off to `design-system`.
- **Full decomposition**: Read `game-concept.md` (or `design/game-brief.md` at minimal) -> enumerate explicit + implicit systems -> map dependency layers (Foundation -> Core -> Feature -> Presentation -> Polish) + cycle checks -> `technical-director` (`TD-SYSTEM-BOUNDARY`, `.ags/gates/td-system-boundary.md`) -> assign priorities (MVP / Vertical Slice / Alpha / Full Vision) + `producer` (`PR-SCOPE`, `.ags/gates/pr-scope.md`) -> draft `.ags/templates/systems-index.md` preserving exact column names (never drop/rename `Category`; `docs.density` prose lives in `## Overview` + `## Dependency Map`) -> `creative-director` (`CD-SYSTEMS`, `.ags/gates/cd-systems.md`; place concerns directly beneath `## Priority Tiers`) -> update `active.md`.

### 2. Per-System GDD Authoring & Retrofit (`design-system`)
- Follow [references/design-system.md](references/design-system.md).
- **Tier & retrofit**:
  - **Minimal project override rule**: Check **project** tier first for required reads; if project is `minimal`, read `design/game-brief.md`, skip `systems-index.md` (never create a stub), and derive `Category` / `Layer` / `Priority` from the brief marked inferred — even if `system_overrides` bumps this system to `standard`/`full`.
  - **Retrofit mode** (`retrofit` or existing `design/gdd/<file>.md`): Report missing vs optional-to-add sections per effective tier; edit only placeholders/missing sections and NEVER overwrite existing content.
- **Required sections**: `## Summary` at **every** tier. `full`: all 8 sections. `standard`: 5 required (`Overview`, `Detailed Rules`/`Detailed Design` alias, `Edge Cases`, `Dependencies`, `Acceptance Criteria`) + conditional `Formulas` whenever the system **defines numeric rules** (Category is hint only, not the test; `Source` column required in Formulas) + `Tuning Knobs` if `workflow_overrides.tuning_knobs: true`. `minimal` (voluntary): 5 standard sections; conditional `Formulas` does NOT re-apply and optional category rules (`Visual/Audio`, `Game Feel`) do not force sections.
- **Context & feasibility pre-check**: Load `entities.yaml` (live keys only, ignore commented examples), `docs/consistency-failures.md` matching domain, bounded dependency section searches (`Dependencies|Formulas|Edge Cases|Tuning Knobs`), and engine feasibility (`VERSION.md`, `modules/<domain>.md` — announce explicitly if absent such as `scripting` or `core`, `breaking-changes.md`, domain-matching ADRs).
- **Skeleton-first & section cycle**: Create `design/gdd/<system>.md` matching `.ags/templates/game-design-document.md` section set/order (`BLOCKED` if declined), then walk required + category-mandatory sections (`Visual/Audio` required for `Gameplay|UI|Narrative|Audio`; `Game Feel` required for `Gameplay|UI`; `Cross-References` required when Dependencies names another GDD) using `Context -> Questions -> Options -> Decision -> Draft -> Approval -> Write -> Registry Conflict Check (C & D)`, updating `active.md` after each section.
- **Post-design**: Author `## Summary` + Quick reference -> verify on disk via `python .ags/cli.py check gdd design/gdd/<system>.md` against effective tier (never hardcoded `/8`) -> `creative-director` (`CD-GDD-ALIGN`, `.ags/gates/cd-gdd-align.md`) -> guarded `entities.yaml` update -> direct user to **fresh-session** `ags-design-review` (NEVER inline) -> guarded `systems-index.md` & `active.md` updates.

### 3. Lightweight Quick Spec (`quick-design`)
- Follow [references/quick-design.md](references/quick-design.md).
- Classify change (`Tuning | Tweak | Addition | New Small System`; redirect work >1 week or cross-system rule changes to `design-system` -> verdict `REDIRECTED`) -> scan GDDs, `systems-index.md`, prior `design/quick-specs/`, and `assets/data/` -> draft spec -> confirm & write `design/quick-specs/<title>-<YYYY-MM-DD>.md` (and confirm any GDD edit separately) -> hand off to `ags-dev` (`readiness`).

## Gate & Verdict

- **`COMPLETE`**: Systems index, GDD (`check gdd` verified against effective tier), or quick spec written with required checks and gates completed.
- **`REDIRECTED`**: Quick-design change exceeded small-spec scope and redirected to `design-system`.
- **`NOT ASSESSED`** *(ranks above `COMPLETE` and below `BLOCKED`)*: Required upstream input (`game-concept.md`, `game-brief.md`, `systems-index.md`) or pinned engine domain reference (`docs/engine-reference/<engine>/modules/<domain>.md`) was absent, or verification could not run; announce gaps by name and never claim unverified feasibility/checks passed.
- **`BLOCKED`**: Missing concept/index outside minimal brief flow, user declined skeleton/index write, or unresolved director `REJECT`.
