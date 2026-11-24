> Gate definition. The spawning skill passes this file's path to the director role; that role reads it — the parent session should not.

# TD-PHASE-GATE — Technical Readiness at Phase Transition

Core role: `technical-director` | Model effort: `high` | Domain: Architecture, engine risk, performance

**Trigger**: Always at `ags-gate` (when included by `modes.workflow` panel width) — dispatch in parallel with CD-PHASE-GATE, PR-PHASE-GATE, and AD-PHASE-GATE

**Context to pass**:
- Target phase name
- Architecture document path (if exists)
- Engine reference path
- ADR list

**Prompt**:
> "Review the current project state for [target phase] gate readiness from a
> technical direction perspective. Is the architecture sound for this phase? Are
> all high-risk engine domains addressed? Are performance budgets realistic and
> documented? Are Foundation-layer decisions complete enough to begin implementation?
> Return READY, CONCERNS [list], or NOT READY [blockers]."

**Verdicts**: READY / CONCERNS / NOT READY
