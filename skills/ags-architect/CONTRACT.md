# ags-architect — Architecture & ADR Contract

## Role in Pipeline

Translates approved game design documents into `docs/architecture/architecture.md`, individual Architecture Decision Records (`docs/architecture/adr-NNNN-[slug].md`), `docs/registry/architecture.yaml` stances, and `docs/architecture/control-manifest.md`. Also owns non-destructive ADR retrofitting (`adr retrofit`) and the sole authoritative acceptance transition (`adr accept ADR-NNNN`) that unblocks downstream epics and stories.

Two checks emit `NOT ASSESSED` rather than passing silently: **engine validation** when `engine.name` is unset, and **GDD sync** when referenced design docs cannot be read or `GDD Requirements Addressed` is empty/missing.

## Inputs Required

| File / Path | Required Fields / Sections | Read-Only? |
|---|---|---|
| `project.yaml` / `project.local.yaml` | `engine.name`, `engine.version`, `naming.*`, `performance.*`, `modes.*` | Yes |
| `docs/engine-reference/<engine>/VERSION.md` | Engine name, pinned version, LLM cutoff, risk levels per domain | Yes |
| `docs/engine-reference/<engine>/modules/<domain>.md` | Domain API patterns (loaded only for active domains) | Yes |
| `docs/engine-reference/<engine>/breaking-changes.md` | Post-cutoff breaking changes | Yes |
| `docs/engine-reference/<engine>/deprecated-apis.md` | Deprecated APIs (filtered for project relevance in manifest) | Yes |
| `docs/engine-reference/<engine>/current-best-practices.md` | Post-cutoff idiomatic patterns | Yes |
| `docs/registry/architecture.yaml` | State ownership, interfaces, performance budgets, forbidden patterns | Append-only (on `adr` approval) |
| `docs/architecture/adr-NNNN-[slug].md` | Existing ADRs (numbered sequentially; scanned via bounded reads) | Read-only except target `retrofit`/`accept` |
| `design/gdd/*.md` (`systems-index.md`, `game-concept.md`) | System list, dependencies, rules, formulas, edge cases (or `design/game-brief.md` at `minimal`) | Yes (unless user approves GDD sync update) |
| `.ags/rules/` | Forbidden patterns and allowed libraries/addons | Yes |

### Preconditions

- Engine must be configured (`docs/engine-reference/<engine>/VERSION.md` reachable); otherwise route to `ags-settings`.
- Architecture blueprint requires `systems-index.md` and `game-concept.md` at `standard`/`full` (`design/game-brief.md` at `minimal`).
- ADR authoring requires a decision title/subject and resolution of any stance conflict in `docs/registry/architecture.yaml` before drafting.
- ADR retrofit requires an existing target file; ADR acceptance requires a unique `adr-NNNN-*.md` match with `## Status: Proposed`, present non-`UNKNOWN` `## ADR Dependencies`, and all upstream `Depends On` ADRs already `Accepted`.
- Control manifest requires `N > 0` ADRs with valid `## Status` headings (`0` matches on `N > 0` = malformed ADRs, STOP).

## Outputs Produced

| Artifact | Guaranteed Structure & Fields | Notes |
|---|---|---|
| `docs/architecture/architecture.md` | Document Status (TD + LP sign-off), Engine Knowledge Gap Summary, System Layer Map, Module Ownership, Data Flow, API Boundaries, ADR Audit, Required ADRs, Architecture Principles, Open Questions | Written after user confirmation; scaled by `docs.density` and `modes.workflow` |
| `docs/architecture/adr-NNNN-[slug].md` | `## Status` (`Proposed` on creation), `## Date`, `## Last Verified`, `## Decision Makers`, `## Summary`, `## Engine Compatibility` (with `Domain`, `Layer`, `Knowledge Risk`), `## ADR Dependencies`, `## Context`, `## Decision` (with `### Implementation Guidelines`), `## Alternatives Considered`, `## Consequences`, `## Risks`, `## GDD Requirements Addressed`, `## Performance Implications`, `## Migration Plan`, `## Validation Criteria`, `## Related` | Created after confirmation (`Proposed`); `retrofit` appends only missing sections; `accept` sets `Accepted` + `## Date` |
| `docs/registry/architecture.yaml` | Appended stances (`state_ownership`, `interfaces`, `performance_budgets`, `forbidden_patterns`, `api_decisions`); superseded entries marked `status: superseded_by: ADR-NNNN` | Separate explicit user confirmation required before append |
| `docs/architecture/control-manifest.md` | Engine, Last Updated, `Manifest Version` (matches Last Updated), ADRs Covered, layer sections (Foundation, Core, Feature, Presentation), Global Rules | Rules extracted from 4 ADR sections (`Decision`, `Alternatives Considered`, `Performance Implications`, `Engine Compatibility`) + relevant `deprecated-apis.md` |
| `production/epics/[epic-slug]/story-*.md` | `Status: Blocked` -> `Status: Ready` for stories referencing accepted ADR | Updated ONLY by `ags-architect adr accept ADR-NNNN` after previewing exact count before confirmation |

## Hard Constraints & Authority

1. **Acceptance Authority**: Only the user, or `technical-director` upon explicit user confirmation, may transition an ADR to `Status: Accepted`. No skill or other role may infer or auto-accept an ADR.
2. **Sole Acceptance Route**: `ags-architect adr accept ADR-NNNN` is the only route from `Proposed` to `Accepted`. It always prompts the user regardless of `modes.automation` (including `autonomous`), refuses if `## ADR Dependencies` is missing/empty/`UNKNOWN` or points to any non-`Accepted` ADR, and never revives `Deprecated` or `Superseded` ADRs.
3. **Never Unblock on Authoring**: Newly authored ADRs are always `Status: Proposed`. Never flip `Blocked` stories to `Ready` during ADR authoring; report blocked story paths and direct the user to `adr accept`.
4. **Sequential ADR Numbering**: Scan all top-level `docs/architecture/adr-*.md` files before assigning the next `NNNN`; never reuse an existing number.
5. **Non-Destructive Retrofit**: `adr retrofit` appends missing sections and stamps `## Date` if absent, but never modifies or overwrites existing section content.
6. **Zero Invented Rules or Silent Skips**: Every rule in `control-manifest.md` must trace to an ADR, `project.yaml`/technical preferences, or relevant engine-reference doc; never default inconclusive dependency scans to `None`; never emit an empty manifest or clean verdict over malformed/unreadable ADRs.
7. **Fresh-Session Review Isolation**: Never execute `ags-arch-review` in the same session that authored ADRs.

## Downstream Expectations

- **`ags-arch-review`**: Reads `architecture.md`, `## Status`, `## Summary`, `## Decision`, `## Engine Compatibility`, `## ADR Dependencies`, `## GDD Requirements Addressed`, and `## Performance Implications` across all ADRs.
- **`ags-plan` (`epics`)**: Requires `Accepted` ADRs for governing references, reads `## GDD Requirements Addressed`, `## Decision`, `## Engine Compatibility` (`Layer`), and `Manifest Version:`.
- **`ags-plan` (`stories`)**: Reads `## Summary`, `## Decision` (+ `### Implementation Guidelines`), `## Engine Compatibility`, `## Last Verified` (`ADR Version` stamp), and `control-manifest.md` header + epic layer section; sets stories referencing `Proposed` ADRs to `Status: Blocked`.
- **`ags-dev` & `ags-verify`**: Read `## Status`, `## Last Verified`, `## Decision`, `## Engine Compatibility`, `## ADR Dependencies`, and manifest layer rules (`Manifest Version:` staleness check).
