> Gate definition. The spawning skill passes this file's path to the director role; that role reads it — the parent session should not.

# AD-PHASE-GATE — Visual Readiness at Phase Transition

Core role: `art-ux-director` | Lens role: `art-director` | Model effort: `medium` | Domain: Visual identity, art bible, visual production readiness

**Trigger**: Always at `ags-gate` (when included by `modes.workflow` panel width) — dispatch in parallel with CD-PHASE-GATE, TD-PHASE-GATE, and PR-PHASE-GATE

**Context to pass**:
- Target phase name
- List of all art/visual artifacts present (file paths)
- Visual identity anchor from `design/gdd/game-concept.md` (if present)
- Art bible path if it exists (`design/art/art-bible.md`)

**Prompt**:
> "Review the current project state for [target phase] gate readiness from a visual
> direction perspective. Is the visual identity established and documented at the
> level this phase requires? Are the right visual artifacts in place? Would visual
> teams be able to begin their work without visual direction gaps that cause costly
> rework later? Are there visual decisions that are being deferred past their latest
> responsible moment? Return READY, CONCERNS [specific visual direction gaps that
> could cause production rework], or NOT READY [visual blockers that must exist
> before this phase can succeed — specify what artifact is missing and why it
> matters at this stage]."

**Verdicts**: READY / CONCERNS / NOT READY
