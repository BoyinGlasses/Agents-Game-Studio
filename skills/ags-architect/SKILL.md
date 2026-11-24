---
name: ags-architect
description: "Use when designing the master architecture blueprint, authoring, retrofitting, or accepting Architecture Decision Records (ADRs), or generating the control manifest. Do NOT use when auditing ADR coverage, cross-ADR conflicts, or scope/tech debt (-> ags-arch-review), or decomposing into epics and stories (-> ags-plan)."
---

# Studio Architect

Translates approved game design documents into the master technical blueprint (`docs/architecture/architecture.md`), point Architecture Decision Records (`docs/architecture/adr-NNNN-[slug].md`), and the flat programmer Control Manifest (`docs/architecture/control-manifest.md`).

## Contract

- **Inputs**: `project.yaml`, `project.local.yaml`, `docs/engine-reference/<engine>/{VERSION,breaking-changes,deprecated-apis,current-best-practices}.md`, matching `docs/engine-reference/<engine>/modules/*.md`, `design/gdd/game-concept.md` (or `design/game-brief.md` at `minimal`), `design/gdd/systems-index.md`, `design/gdd/*.md`, `docs/registry/architecture.yaml`, `docs/architecture/adr-*.md`, `.ags/rules/` (forbidden patterns and allowed libraries), `production/epics/[epic-slug]/story-*.md` (for `adr accept`)
- **Roles**: `technical-director` (read-only architecture, ADR, and manifest gates), `code-reviewer` (read-only feasibility gate via lens `lead-programmer`), `scout` (optional lookup), `godot-specialist`, `unity-specialist`, `unreal-specialist`, plus engine sub-specialists per team size
- **Outputs**: `docs/architecture/architecture.md`, `docs/architecture/adr-NNNN-[slug].md`, `docs/registry/architecture.yaml` (append-only), `docs/architecture/control-manifest.md`, `production/epics/[epic-slug]/story-*.md` (`Blocked` -> `Ready` on `adr accept`), `production/session-state/active.md`, `production/session-logs/decision-log.md` (`autonomous` mode)
- **Verification**: `python .ags/cli.py preflight ags-architect [system]`, engine reference verification against `VERSION.md`, GDD sync 3-outcome check, ADR dependency/status validation, and director gates (`TD-ARCHITECTURE`, `LP-FEASIBILITY`, `TD-ADR`, `TD-MANIFEST`) per `modes.review_mode`
- **Next Skill**: `ags-arch-review` (in a fresh session after authoring ADRs), `ags-plan` (epics/stories once ADRs are Accepted and manifest generated), `ags-qa` (`setup`), `ags-art-ux` (`ux-design`), or `ags-gate`

## Preflight

Run once at startup and hold the resolved configuration for the session:

```bash
python .ags/cli.py preflight ags-architect [target]
```

Read `review_mode`, `automation`, `workflow`, `docs.density`, `team.size`, `engine.*`, and `automation_always_ask`. An inline `--review [full|lean|solo]` flag overrides `modes.review_mode` for this run. Apply automation rules (`collaborative` prompts at every decision and write; `guided` prompts on major decisions and new files only; `autonomous` logs non-`always_ask` decisions to `production/session-logs/decision-log.md` — except **`adr accept`, which ALWAYS prompts the user regardless of automation mode**).

## Phases

### Phase 1: Route Mode

Select sub-mode from arguments or user intent (load ONLY the active reference file and `CONTRACT.md` when in `adr` mode):

| Argument / Trigger | Mode | Reference |
|---|---|---|
| `architecture` (`full` \| `layers` \| `data-flow` \| `api-boundaries` \| `adr-audit`) or no args for system blueprint | **Master Architecture** | [references/create-architecture.md](references/create-architecture.md) |
| `adr <title>` (fresh ADR), `adr retrofit <path>` (non-destructive append), or `adr accept ADR-NNNN` | **Architecture Decision Record** | [references/architecture-decision.md](references/architecture-decision.md) + [CONTRACT.md](CONTRACT.md) |
| `manifest` (`new` \| `update`) | **Control Manifest** | [references/create-control-manifest.md](references/create-control-manifest.md) |

If no mode or title is clear, prompt the user to select `architecture`, `adr <title|retrofit|accept>`, or `manifest`.

### Phase 2: Execute Mode Workflow

1. **Master Architecture (`architecture`)**: Follow [references/create-architecture.md](references/create-architecture.md).
   - Load engine reference docs (`VERSION.md`, `breaking-changes.md`, `deprecated-apis.md`, `current-best-practices.md`) and ONLY matching `modules/` files (ambiguous domain matches are read). Stop and route to `ags-settings` if no engine is configured.
   - Verify `game-concept.md` and `systems-index.md` exist (`minimal` uses `design/game-brief.md`). Extract `TR-[gdd-slug]-[NNN]` Technical Requirements Baseline across all `N` GDDs via targeted section search (full-read only unstructured/cross-referenced GDDs), scan ADR headers (`Status`, `Summary`, `Domain`), and present the Engine Knowledge Gap Inventory.
   - Walk through System Layers (Platform, Foundation, Core, Feature, Presentation), Module Ownership, Data Flow, API Boundaries, ADR Audit + Traceability Check, and Missing ADR List scaled by `docs.density` and `modes.workflow`.
   - Confirm and write `docs/architecture/architecture.md`, run `TD-ARCHITECTURE` + `LP-FEASIBILITY` (`code-reviewer` with lens `lead-programmer`) per `review_mode`, update `active.md`, and emit the structured handoff.

2. **Architecture Decision Record (`adr`)**: Follow [references/architecture-decision.md](references/architecture-decision.md) and [CONTRACT.md](CONTRACT.md).
   - **Fresh authoring**: Load engine context (`VERSION.md`, matching module, `breaking-changes.md`, `deprecated-apis.md`), check `docs/registry/architecture.yaml` first (BLOCKING on unresolved conflict), bounded-read relevant prior ADRs (`<50KB` full; `>=50KB` heading map + `## Context`/`## Decision`/`## Consequences` only), derive assumptions (always `Status: Proposed`; `## ADR Dependencies` defaults to `UNKNOWN — scan inconclusive` rather than `None` until confirmed), draft all required sections including `## Last Verified` and `## Summary`, validate with `<engine>-specialist` (or record `NOT ASSESSED` if unconfigured) and `TD-ADR`, run the 3-outcome GDD sync check, confirm write, optionally append `docs/registry/architecture.yaml`, and direct user to a **fresh session** for `ags-arch-review`.
   - **Non-destructive `retrofit <path>`**: Scan headings; `## Status` missing is `BLOCKING`. Append missing sections only (`## Status`, `## ADR Dependencies`, `## Engine Compatibility`, `## GDD Requirements Addressed`, `## Date`); never alter existing sections.
   - **`accept ADR-NNNN`**: Sole path setting `Accepted`. Refuse `Deprecated`/`Superseded`, missing/empty/`UNKNOWN` `## ADR Dependencies`, or unaccepted upstream dependencies. Scan `production/epics/[epic-slug]/story-*.md` for `Status: Blocked` + ADR ID BEFORE prompting, always confirm with the user regardless of `modes.automation`, stamp `## Status: Accepted` + `## Date`, and unblock matching stories to `Ready`.

3. **Control Manifest (`manifest`)**: Follow [references/create-control-manifest.md](references/create-control-manifest.md).
   - Count `docs/architecture/adr-*.md` (`N`), scan `^## Status` first: `0` matches with `N > 0` = malformed ADRs (STOP — run `ags-architect adr retrofit`).
   - Extract from the 4 sections (`Decision`, `Alternatives Considered`, `Performance Implications`, `Engine Compatibility` — never `Implementation Guidelines` alone) per Accepted ADR, merge naming/performance config and relevance-filtered `deprecated-apis.md` rules, preview counts, run `TD-MANIFEST` per `review_mode`, confirm write to `docs/architecture/control-manifest.md` with `Manifest Version` date stamp matching `Last Updated`.

### Phase 3: Cross-Session Integrity & Handoff

- Never mark a new ADR `Accepted` during authoring or unblock `Blocked` stories until explicit `adr accept ADR-NNNN`.
- Never run `ags-arch-review` in the same session that authored ADRs; instruct the user to open a fresh session.

## Gate & Verdict

- **`COMPLETE` / `PASS`**: Target artifact (`architecture.md`, `adr-NNNN-*.md`, accepted ADR + unblocked stories, or `control-manifest.md`) written/updated cleanly with all required gates resolved (`APPROVE` / `FEASIBLE` or accepted `CONCERNS`).
- **`CONCERNS`**: Director or specialist raised non-blocking concerns accepted by the user, `Proposed` ADRs remain unaccepted, or non-critical requirements lack ADRs.
- **`NOT ASSESSED`** *(ranks above `COMPLETE`/`PASS` and below `CONCERNS`/`BLOCKED`/`REJECT`)*: Engine validation skipped (`engine.name` unconfigured), GDD sync skipped (missing/empty `GDD Requirements Addressed` or missing GDD file), or ADR `## Status` / `## ADR Dependencies` missing/unreadable (`UNKNOWN`). Name the exact skipped check and remediation; never report an unrun check as clean.
- **`BLOCKED` / `REJECT`**: Missing `engine.name`, missing `systems-index.md` / concept (at `standard`/`full`), unresolved registry stance conflict, `adr accept` on `Deprecated`/`Superseded`/unresolved-dependency ADR, `0` ADR `## Status` matches when `N > 0` (malformed ADRs), director `REJECT`/`INFEASIBLE`, or user declined write.
