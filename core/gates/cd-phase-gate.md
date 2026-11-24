> Gate definition. The spawning skill passes this file's path to the director role; that role reads it — the parent session should not.

# CD-PHASE-GATE — Creative Readiness at Phase Transition

Core role: `creative-director` | Model effort: `high` | Domain: Vision, pillars, player experience

**Trigger**: Always at `ags-gate` (when included by `modes.workflow` panel width) — dispatch in parallel with TD-PHASE-GATE, PR-PHASE-GATE, and AD-PHASE-GATE

**Context to pass**:
- Target phase name
- List of all artifacts present (file paths)
- Game pillars and core fantasy

**Prompt**:
> "Review the current project state for [target phase] gate readiness from a
> creative direction perspective. Are the game pillars faithfully represented in
> all design artifacts? Does the current state preserve the core fantasy? Are there
> any design decisions across GDDs or architecture that compromise the intended
> player experience? Return READY, CONCERNS [list], or NOT READY [blockers]."

**Verdicts**: READY / CONCERNS / NOT READY
