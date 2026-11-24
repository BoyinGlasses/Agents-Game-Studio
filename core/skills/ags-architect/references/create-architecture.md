# Master Architecture Blueprint (`ags-architect architecture`)

Produces `docs/architecture/architecture.md` translating approved GDDs into a system-layer technical blueprint before sprint planning.

## Modes & Tier Scaling

- **Argument modes**: `full` (default walkthrough), `layers` (layer map only), `data-flow` (module data flows only), `api-boundaries` (API contracts only), `adr-audit` (audit existing ADRs against engine compatibility and TR baseline).
- **`workflow` tier**:
  - `full`: All layers, module ownership, data flows, API boundaries, full ADR audit, and traceability baseline.
  - `standard`: Simplified system layer map + critical (Foundation-layer) ADR list.
  - `minimal`: Optional; uses `design/game-brief.md` if invoked.
- **`docs.density`**: `terse` (layer diagrams + decision bullets), `balanced` (diagrams + paragraph explanations per layer), `thorough` (full prose with rationale, trade-offs, and alternatives per layer).

## Phase 0: Load Full Context

### 0a. Engine Context
Read all 4 project-wide engine docs in full:
1. `docs/engine-reference/<engine>/VERSION.md` -> engine name, version, LLM cutoff, post-cutoff risk levels.
2. `docs/engine-reference/<engine>/breaking-changes.md` -> HIGH and MEDIUM risk changes.
3. `docs/engine-reference/<engine>/deprecated-apis.md` -> APIs to avoid.
4. `docs/engine-reference/<engine>/current-best-practices.md` -> post-cutoff best practices.

Then list `docs/engine-reference/<engine>/modules/` and read ONLY module docs matching domains present in `design/gdd/systems-index.md` (`Physics`, `Rendering`, `UI`, `Audio`, `Navigation`, `Animation`, `Networking`, `Core`, `Input`). Skip unreferenced domains; if a domain match is ambiguous, read the module to avoid missing an engine constraint.

If no engine is configured, stop and instruct the user to run `ags-settings` (`engine` mode) first.

### 0b. Design Context & Technical Requirements Baseline
1. Verify existence and non-placeholder content of `design/gdd/game-concept.md` and `design/gdd/systems-index.md`:
   - If `systems-index.md` is missing or placeholder at `standard`/`full`: stop and route to `ags-gdd` (`map-systems`). At `minimal`, note absence and use `design/game-brief.md`.
   - If `game-concept.md` is missing or placeholder at `standard`/`full`: stop and route to `ags-ideate`. At `minimal`, read `design/game-brief.md` (stop if absent).
2. Read `naming.*` and `performance.*` from preflight (`project.yaml`), plus allowed libraries and forbidden patterns from `.ags/rules/` or project technical preferences.
3. Establish denominator `N` by listing `design/gdd/*.md`. Extract technical requirements from `^## (Detailed Rules|Detailed Design|Formulas|Dependencies|Tuning Knobs|Acceptance Criteria)` (up to 40 lines per match); accept both `Detailed Rules` and `Detailed Design`.
   - Full-read any GDD matching zero scanned sections (unstructured format) or cross-referencing external material.
   - Report any GDD that contributed zero requirements rather than dropping it silently.
4. Build the **Technical Requirements Baseline**:

```markdown
## Technical Requirements Baseline
Extracted from [N] GDDs | [X] total requirements

| Req ID | GDD | System | Requirement | Domain |
|---|---|---|---|---|
| TR-combat-001 | combat.md | Combat | Hitbox detection per-frame | Physics |
```

### 0c. Existing ADR Header Scan
Scan headers across `docs/architecture/adr-*.md` (`^## (Status|Summary)` +4 lines and `\*\*Domain\*\*`). Full-read a specific ADR only when a decision in this session collides with it.

### 0d. Engine Knowledge Gap Inventory
Display `HIGH RISK`, `MEDIUM RISK`, and `LOW RISK` domains alongside GDD systems touching HIGH/MEDIUM domains, then prompt the user (per `modes.automation`):
- `[A] Proceed — flag HIGH RISK domains throughout the output`
- `[B] Pause — let user check the engine reference first`
- `[C] Show which domains are HIGH RISK and why`

## Phase 1: System Layer Mapping
Map every system from `systems-index.md` into the 5-layer stack (`Platform` -> `Foundation` -> `Core` -> `Feature` -> `Presentation`), defining module boundaries and exclusive ownership. Flag Core/Foundation systems touching HIGH/MEDIUM risk domains with inline engine-reference excerpts. Confirm approval before proceeding and write incrementally.

## Phase 2: Module Ownership Map
Define per-module **Owns**, **Exposes**, **Consumes**, and **Engine APIs used** (with version and risk level) as tables per layer + ASCII dependency diagram. Flag any post-cutoff API:
`⚠️ [ClassName.method()] — [Engine Version] (post-cutoff, HIGH risk)` with `Verified against:` and `Behaviour confirmed: [yes / NEEDS VERIFICATION]`. Confirm approval before writing.

## Phase 3: Data Flow
Document frame update path, event/signal path, save/load path, and initialization order using ASCII sequence diagrams where helpful. Name transferred data, producer/consumer, mechanism (sync call / signal / shared state), and thread-boundary crossings. Confirm per scenario before writing.

## Phase 4: API Boundaries
Define public module interfaces, entry points (functions/signals/properties), caller invariants, module guarantees, and engine-type signature checks against the pinned engine version.

## Phase 5: ADR Audit + Traceability Check
1. Audit existing ADRs for `Engine Compatibility`, pinned version, post-cutoff API flags, `GDD Requirements Addressed`, conflicts with Phases 1–4, and current-version validity.
2. Map every `TR-<slug>-NNN` baseline item to ADRs (`✅` covered vs `❌ GAP`) and emit `Required New ADRs` grouped Foundation-first with `ags-architect adr "<title>"`.

## Phase 6: Missing ADR List
Group outstanding ADRs by priority:
- **Must have before coding starts (Foundation & Core)**
- **Should have before the relevant system is built**
- **Can defer to implementation**

## Phase 7: Write Master Architecture & Sign-Off
1. Summarize sections and confirm write to `docs/architecture/architecture.md` (with `[A] Write now`, `[B] Show full draft first`, `[C] Not yet`).
2. **Document structure**: `# [Game Name] — Master Architecture` containing `## Document Status`, `## Engine Knowledge Gap Summary`, `## System Layer Map`, `## Module Ownership`, `## Data Flow`, `## API Boundaries`, `## ADR Audit`, `## Required ADRs`, `## Architecture Principles`, and `## Open Questions`.
3. **Gates (Phase 7b)**:
   - Run `TD-ARCHITECTURE` as `technical-director` self-review against `.ags/gates/td-architecture.md`.
   - Check `review_mode` before `LP-FEASIBILITY`: skip with note `"LP-FEASIBILITY skipped — Solo/Lean mode."` when `solo` or `lean`; in `full`, spawn `code-reviewer` (with `.ags/roles/lead-programmer.md` lens) pointing to `.ags/gates/lp-feasibility.md` (pass architecture path, TR baseline summary, and ADR list — parent must not read the gate file).
   - Present both assessments side by side, resolve concerns per `modes.automation`, confirm update, and record sign-off in `## Document Status`:
     `- Technical Director Sign-Off: [date] — APPROVED / APPROVED WITH CONDITIONS`
     `- Lead Programmer Feasibility: FEASIBLE / CONCERNS ACCEPTED / REVISED`

## Phase 8: Session State & Structured Handoff
1. Update `production/session-state/active.md` (preserving `STATUS`/`CHECKPOINT` bounds) with artifact written, TD/LP verdicts, blockers, remaining required ADRs, and next step.
2. Output the exact structured handoff:
   - `## Architecture Complete` (`docs/architecture/architecture.md` v1.0 — verdict + 1-sentence summary)
   - `## Run These ADRs Next` (top 3 priority ADRs using `ags-architect adr "[Title]"`)
   - `## Gate-Check Readiness` (Accept ADRs, Write ADRs, `ags-qa setup`, `ags-art-ux ux-design`, then `ags-gate [stage]`; or `No blockers — run ags-gate [stage] now.`)
   - `## Open Questions to Watch` (`ID | Summary | Priority | Resolution Path` — omit if none)
