> Gate definition. The spawning skill passes this file's path to the director role; that role reads it — the parent session should not.

# PR-PHASE-GATE — Production Readiness at Phase Transition

Core role: `producer` | Model effort: `medium` | Domain: Scope, timeline, dependencies, production risk

**Trigger**: Always at `ags-gate` (when included by `modes.workflow` panel width) — dispatch in parallel with CD-PHASE-GATE, TD-PHASE-GATE, and AD-PHASE-GATE

**Context to pass**:
- Target phase name
- Sprint and milestone artifacts present
- Team size and capacity
- Current blocked story count

**Prompt**:
> "Review the current project state for [target phase] gate readiness from a
> production perspective. Is the scope realistic for the stated timeline and team
> size? Are dependencies properly ordered so the team can actually execute in
> sequence? Are there milestone or sprint risks that could derail the phase within
> the first two sprints? Return READY, CONCERNS [list], or NOT READY [blockers]."

**Verdicts**: READY / CONCERNS / NOT READY
