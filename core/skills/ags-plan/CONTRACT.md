# ags-plan — Epics & Stories Contract

## Role in Pipeline

Translates approved GDDs, ADRs, architecture docs (or `design/game-brief.md` at `workflow: minimal`) into layer-ordered epics (`production/epics/[epic-slug]/EPIC.md`) and atomic implementable stories (`production/epics/[epic-slug]/story-NNN-[slug].md`), bridging technical architecture and `ags-dev`.

## Inputs Required

### Epics (`epics` mode)
| File | Required Fields / Sections | Read-Only? |
|---|---|---|
| `design/gdd/systems-index.md` | System list, layer assignments, priority order (`standard`/`full`) | Yes |
| `design/gdd/[system].md` | `## Summary` (if present), `## Overview`, `## Acceptance Criteria`, tier sections | Yes |
| `design/game-brief.md` | Pitch, MVP features, **Build order** (`minimal` fallback) | Yes |
| `docs/architecture/architecture.md` | Module ownership and API boundaries (`standard`/`full`) | Yes |
| `docs/architecture/adr-NNNN-[slug].md` | `## Status`, `## GDD Requirements Addressed`, `## Decision`, `## Engine Compatibility` | Yes |
| `docs/architecture/control-manifest.md` | `Manifest Version:` date in header (`full` required; `standard` if present) | Yes |
| `docs/architecture/tr-registry.yaml` | `id`, `system`, `requirement` (`full`) | Yes |
| `docs/engine-reference/<engine>/VERSION.md` | Engine name, pinned version, risk levels | Yes |

### Stories (`stories` mode)
| File | Required Fields / Sections | Read-Only? |
|---|---|---|
| `production/epics/[epic-slug]/EPIC.md` | `Layer`, `GDD`, `Architecture Module`, `## Governing ADRs`, `## GDD Requirements` (`standard`/`full`; synthesized from `design/game-brief.md` at `minimal`) | Updated with `## Stories` |
| `design/gdd/[filename].md` or `design/game-brief.md` | Acceptance criteria, formulas, edge cases (or brief pitch/MVP/fail state at `minimal`) | Yes |
| `docs/architecture/adr-NNNN-[slug].md` | `## Status`, `## Last Verified`/`## Date`, `## Summary`, `## Decision` (+ `### Implementation Guidelines`), `## Engine Compatibility` (`standard`/`full`) | Yes |
| `docs/architecture/control-manifest.md` | Header `Manifest Version:` + epic's `## <Layer> Layer Rules` (`standard`/`full`) | Yes |
| `docs/architecture/tr-registry.yaml` | Target system's `TR-<slug>-NNN` entries (`standard`/`full`) | Yes |
| `docs/engine-reference/<engine>/VERSION.md` | Engine version and risk rating (always checked, including `minimal`) | Yes |

### Preconditions
- **`epics` (`standard`/`full`)**: `architecture-review` completed (`full`), `control-manifest.md` present (`full`), in-scope GDDs `Approved` or `Designed` in `systems-index.md`, Foundation before Core before Feature before Presentation. (`minimal` needs only `design/game-brief.md` and is optional.)
- **`stories` (`standard`/`full`)**: Target `EPIC.md` exists (`Status: Ready`) with `## GDD Requirements`; all referenced ADRs exist at `full` (or critical Foundation ADRs at `standard`). Zero epics under `production/epics/` stops and routes to `ags-plan epics`.
- **`stories` (`minimal`)**: `design/game-brief.md` exists; `stories` synthesizes an implicit `EPIC.md` (Option A) and reads `VERSION.md` for engine risk.

## Outputs Produced

| File | Guaranteed Fields / Sections | Notes |
|---|---|---|
| `production/epics/[epic-slug]/EPIC.md` | `Layer`, `GDD`, `Architecture Module`, `Status: Ready`, `Stories`, `## Overview`, `## Governing ADRs`, `## GDD Requirements` (`TR-ID` + `ADR Coverage`), `## Definition of Done`, `## Next Step` | Created by `epics` (or synthesized by `stories` at `minimal`); updated with `## Stories` table by `stories` |
| `production/epics/index.md` | `Epic`, `Layer`, `System`, `GDD`, `Stories`, `Status` | Created/updated by `epics`; `Stories` updated to `[N] stories` by `stories` |
| `production/epics/[epic-slug]/story-NNN-[slug].md` | Header (`Epic`, `Status: Ready\|Blocked`, `Layer`, `Type`, `Handoff Class`, `Estimate`, `Manifest Version`, `Last Updated`), `## Context` (`GDD`, `Requirement`, `ADR Governing Implementation`, `ADR Decision Summary`, `ADR Version`, `Engine \| Risk`, `Engine Notes`, `Control Manifest Rules`), `## Acceptance Criteria`, `## Implementation Notes`, `## Out of Scope`, `## QA Test Cases`, `## Test Evidence` (`Verification Method`, `Story Type`, `Required evidence`, `Status`), `## Dependencies` | Created per approved story; stories referencing `Proposed` ADRs get `Status: Blocked` |

### Output Guarantees
- Every story sets `Handoff Class: Player-facing | Technical | Mixed` from acceptance criteria (never inferred `Technical` solely from `Type: Logic`) and `Verification Method:` naming concrete build/test/manual steps and expected evidence path (mandatory even when `qa.level: minimal` waives automated tests).
- Every story sets `Engine` and `Risk` from `docs/engine-reference/<engine>/VERSION.md` (at `minimal`) or governing ADRs; if `VERSION.md` is missing or assigns no level, emit `NOT ASSESSED (no VERSION.md risk rating)` — never guess. Downstream `ags-dev` treats `NOT ASSESSED` as `HIGH` for specialist spawns.
- `ADR Version` stamps `## Last Verified`, falling back to `## Date`, else `unversioned`.
- Never mark a `TR-ID` covered by an ADR unless its `## Status` is `Accepted`; never set a story `Ready` if its governing ADR is `Proposed`.

## Hard Constraints & Immutability

- Never edit GDDs, ADRs, `tr-registry.yaml`, or `control-manifest.md` during planning.
- Never write implementation code or begin coding inside `ags-plan`.
- Never invent acceptance criteria, implementation notes, or manifest rules unsourced from GDD/brief/ADRs/manifest.
- Never reuse an existing story number `NNN` in an epic directory; check existing files before numbering.
- Never write `EPIC.md` or `story-*.md` files without presenting the summary and confirming per `modes.automation`.

## Downstream (`ags-dev`, `ags-verify`, `ags-plan sprint`)

- **`ags-dev` / `ags-verify`**: Read `Status`, `Type`, `Handoff Class`, `Manifest Version`, `ADR Version`, `Engine` / `Risk`, `TR-ID`, `ADR Governing Implementation`, `## Acceptance Criteria`, `## Implementation Notes`, `## Test Evidence` (`Verification Method`), and `## Dependencies`.
- **`ags-plan sprint`**: Reads `production/epics/**/story-*.md` (`Status: Ready`) and `EPIC.md` index to schedule sprints.
