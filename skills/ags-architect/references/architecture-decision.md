# Architecture Decision Records (`ags-architect adr`)

Handles fresh ADR authoring, non-destructive `retrofit`, and authoritative `accept ADR-NNNN` transitions. See [../CONTRACT.md](../CONTRACT.md) for immutability and handoff guarantees.

## Mode Detection

- **`retrofit <path>`**: Non-destructive upgrade of an existing ADR missing template sections.
- **`accept ADR-NNNN`**: Sole path transitioning an ADR from `Proposed` to `Accepted` and unblocking waiting stories.
- **`<title>` (default)**: Author a new ADR (always starts `Status: Proposed`). If no title is provided, ask for a short title before loading context.

**`team.size` validation roster**: `individual` = `technical-director` + `code-reviewer (lens: lead-programmer)` + `<engine>-specialist`; `small` = + engine sub-specialist; `studio` = + adversarial alternate engine-specialist review.
**`docs.density`**: Controls prose depth in `Decision`, `Alternatives`, and `Consequences` (`terse` = bullets + 1-line rationale; `balanced` = paragraph per section; `thorough` = full trade-off prose). Structural tables (`Engine Compatibility`, `ADR Dependencies`, `GDD Requirements Addressed`) stay complete at every density.
**`workflow`**: `full` = all required ADRs; `standard` = critical Foundation-layer ADRs blocking; `minimal` = optional.

---

## Mode A: Non-Destructive Retrofit (`adr retrofit <path>`)

1. Read the target ADR completely and scan headings:
   - `## Status` — **BLOCKING if missing** (downstream story readiness cannot verify acceptance).
   - `## ADR Dependencies` — HIGH if missing (dependency graph ordering fails).
   - `## Engine Compatibility` — HIGH if missing (post-cutoff risk unknown).
   - `## GDD Requirements Addressed` — MEDIUM if missing (traceability broken).
2. Present present vs missing sections (`✓` vs `✗`). Confirm appending missing sections without altering any existing content.
3. Collect values for missing sections (`Status`, `ADR Dependencies`, `Engine Compatibility` verified against engine reference, `GDD Requirements Addressed`), append ONLY missing sections, and add `## Date` if absent.
4. Direct user to run `ags-arch-review` in a fresh session to re-validate coverage.

---

## Mode B: Acceptance (`adr accept ADR-NNNN`)

1. **Resolve unique file**: Match `docs/architecture/adr-NNNN-*.md`. If 0 matches or >1 match, stop and report. If `## Status` is missing, stop and route to `adr retrofit`.
2. **Check current status**: If already `Accepted`, report and stop. If `Deprecated` or `Superseded`, refuse (reviving requires a new ADR).
3. **Validate `## ADR Dependencies` BEFORE accepting**:
   - If `## ADR Dependencies` is absent, empty, or reads `UNKNOWN`, refuse and route to `adr retrofit`: empty/unexamined dependencies must never pass as "no dependencies".
   - If any `Depends On` ADR is not `Accepted`, refuse and name the blocking `Proposed`/missing ADR(s).
4. **Scan blocked stories BEFORE prompting**: Search `production/epics/[epic-slug]/story-*.md` (never outside `production/epics/`) for files containing BOTH `Status: Blocked` and `ADR-NNNN`. Feed the exact story count and paths (or `"no stories are waiting on this"`) into the confirmation prompt so the user authorizes the real downstream effect.
5. **Always prompt the user** (even in `autonomous` mode — acceptance authority belongs solely to the user or `technical-director` on explicit user confirmation):
   - `"Accept ADR-NNNN — [title]? ([K] story/stories will become Ready: ...)"`
   - `[A] Yes — accept it` / `[B] Not yet — leave it Proposed`
6. On confirmation: update `## Status` to `Accepted`, stamp `## Date` (adding `## Date` section if absent), flip every matched blocked story from `Status: Blocked` to `Status: Ready`, and report the ADR, new date, and unblocked story paths.

---

## Mode C: Fresh ADR Authoring (`adr <title>`)

### 1. Engine Context (Always First)
1. Read `docs/engine-reference/<engine>/VERSION.md` (name, version, cutoff, domain risk levels). If unconfigured, stop and route to `ags-settings`.
2. Identify domain (`Physics`, `Rendering`, `UI`, `Audio`, `Navigation`, `Animation`, `Networking`, `Core`, `Input`, `Scripting`) and read matching `modules/<domain>.md`, `breaking-changes.md`, and `deprecated-apis.md`.
3. Display a prominent `ENGINE KNOWLEDGE GAP WARNING` whenever the domain is `MEDIUM` or `HIGH` risk.

### 2. Next ADR Number & Stance Registry Check (BLOCKING)
1. Scan top-level `docs/architecture/adr-*.md` to determine the next sequential `NNNN`.
2. Search `docs/registry/architecture.yaml` by domain/system/state keywords before opening prior ADRs. Present relevant `State Ownership`, `Interface Contracts`, `Performance Budgets`, and `Forbidden Patterns`. Any contradiction with a registered stance is **BLOCKING** until the user chooses `(1) Align`, `(2) Supersede ADR-NNNN`, or `(3) Explicit exception`.
3. **Bounded prior reads (3b)**: Only open a prior ADR if the registry surfaced it and reasoning is needed:
   - Map `^## ` headings first.
   - `<50KB`: full read allowed. `>=50KB`: bounded-read ONLY `## Context`, `## Decision`, and `## Consequences`.
   - Read only directly relevant GDD sections (`^## (Dependencies|Formulas|Edge Cases)`). Skip 3b if the registry answers everything.

### 3. Derive Assumptions & Design Collaboratively
Before prompting, infer Problem, 2–3 Alternatives, GDD linkage, and Dependencies:
- **Dependencies rule**: Scan existing ADRs; if the scan is inconclusive, present `UNKNOWN — scan inconclusive, please confirm` — **never default an inconclusive scan to `None`**. Resolve `UNKNOWN` during confirmation before writing (never write `UNKNOWN` to file).
- **Status rule**: Always `Proposed` for new ADRs — never ask status at authoring time.
- Separate **Assumptions confirmation** (`[A] Proceed` / `[B] Change alternatives` / `[C] Adjust GDD linkage` / `[D] Add budget` / `[E] Change other`) from **Schema/Data Design questions** (separate multi-option prompt if needed).

### 4. Draft ADR Template Sections
Generate with exact headings:
- `# ADR-[NNNN]: [Title]`
- `## Status` (`Proposed`) · `## Date` · `## Last Verified` (`YYYY-MM-DD`) · `## Decision Makers`
- `## Summary` (2 sentences for tiered loading: problem + chosen approach)
- `## Engine Compatibility` (`Engine`, `Domain`, `Layer` [`Foundation|Core|Feature|Presentation`], `Knowledge Risk`, `References Consulted`, `Post-Cutoff APIs Used`, `Verification Required`)
- `## ADR Dependencies` (`Depends On`, `Enables`, `Blocks`, `Ordering Note` — explicit `"None"` only once confirmed)
- `## Context` (`### Problem Statement`, `### Constraints`, `### Requirements`)
- `## Decision` (`### Architecture Diagram`, `### Key Interfaces`, `### Implementation Guidelines` written as concrete `"must / must never"` mandates)
- `## Alternatives Considered` (each with Description, Pros, Cons, Rejection Reason)
- `## Consequences` (`Positive`, `Negative`) · `## Risks` · `## GDD Requirements Addressed` (`GDD System | Requirement | How This ADR Addresses It`) · `## Performance Implications` · `## Migration Plan` · `## Validation Criteria` · `## Related`

### 5. Specialist Validation, `TD-ADR`, and GDD Sync
1. **Engine Specialist Validation**: Derive `<engine>-specialist` from `project.yaml` `engine.name` (else legacy fallback). If unconfigured, skip and explicitly emit: `Engine validation: NOT ASSESSED — no engine configured (engine.name unset in project.yaml)`. Otherwise spawn specialist with `Engine Compatibility`, `Decision`, `Key Interfaces`, and engine docs path; resolve any blocking API/version issues before proceeding.
2. **Technical Director Review (`TD-ADR`)**: Check `review_mode` (`solo`/`lean` -> skip with note `"TD-ADR skipped — Solo/Lean mode."`; `full` -> spawn `technical-director` pointing to `.ags/gates/td-adr.md`).
3. **GDD Sync Check (3 mandatory outcomes — always report)**:
   Compare ADR `Key Interfaces` / `Decision` names against referenced GDDs:
   - **Mismatch found**: Emit prominent `⚠️ GDD SYNC REQUIRED` table before write confirmation.
   - **None found**: Emit `"GDD sync: checked [N] referenced GDD(s), no naming inconsistencies."`
   - **Could not check** (missing `GDD Requirements Addressed`, no GDDs named, or missing GDD file): Emit `"GDD sync: NOT ASSESSED — [reason and files]"` (never report clean).

### 6. Write Confirmation, Registry Append & Fresh-Session Notice
1. Confirm write of `docs/architecture/adr-[NNNN]-[slug].md` (including option `[A] Write ADR + update GDD` if sync mismatches exist).
2. Scan the written ADR for new `state_ownership`, `interfaces`, `performance_budgets`, `api_decisions`, and `forbidden_patterns`. Confirm separately before appending to `docs/registry/architecture.yaml` (read current file, append after last entry in each section, mark overridden stances `status: superseded_by: ADR-[NNNN]`).
3. **Always emit fixed closing notices**:
   - Direct user to open a **fresh session** and run `ags-arch-review` (never run `ags-arch-review` in the same session that authored ADRs).
   - Never unblock stories here: list waiting `Blocked` stories by path and state `"ADR-NNNN is written and Proposed. Run ags-architect adr accept ADR-NNNN once settled to move waiting stories to Ready."`
