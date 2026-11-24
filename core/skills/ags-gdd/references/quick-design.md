# Quick Design Spec Workflow (`ags-gdd`)

Lightweight design path (`design/quick-specs/<title>-<YYYY-MM-DD>.md`) for changes under ~1 week that do not warrant a full GDD. Bypasses `ags-design-review` by design.

## 1. Classify the Change

- **Tuning**: Numeric/balance adjustments in an existing system with zero behavioral change (e.g., jump height 5 -> 6, patrol speed -10%).
- **Tweak**: Small behavioral adjustment in an existing system introducing no new states, branches, or systems.
- **Addition**: Small mechanic added to an existing system introducing at most 1-2 new states or interactions.
- **New Small System**: Standalone feature with no existing GDD and under ~1 week of implementation.
- **Redirect rule (`REDIRECTED`)**: If the change adds an index-level system, alters cross-system contracts, reshapes core MDA balance, or exceeds ~1 week -> STOP and redirect to `ags-gdd design-system`.

Confirm inferred classification with the user (`[A] Yes` / `[B] Tuning` / `[C] Tweak` / `[D] Addition` / `[E] New Small System` / `[F] Too large — redirect to ags-gdd design-system`).

## 2. Context Scan

- Read relevant sections of the target GDD in `design/gdd/`.
- Check `design/gdd/systems-index.md` for tier/dependency context (note skip if absent).
- Check `design/quick-specs/` for prior specs touching the same system to avoid contradictions.
- For **Tuning**, inspect `assets/data/` for the backing config file.

## 3. Draft Templates by Category

### Tuning
```markdown
# Quick Design Spec: [Title]
**Type**: Tuning | **System**: [System] | **GDD Reference**: `design/gdd/[file].md` — Tuning Knobs | **Date**: [YYYY-MM-DD]
## Change
| Parameter | Old Value | New Value | Rationale |
|-----------|-----------|-----------|-----------|
## Tuning Knob Mapping
Maps to GDD Tuning Knob: [knob + range]. New value is [within / at edge of / outside] range.
## Acceptance Criteria
- [ ] [Parameter] reads [new value] from `assets/data/[file]`
- [ ] Behavior difference observable in [context]
- [ ] No regression in [related behavior]
```

### Tweak / Addition
```markdown
# Quick Design Spec: [Title]
**Type**: [Tweak / Addition] | **System**: [System] | **GDD Reference**: `design/gdd/[file].md` | **Date**: [YYYY-MM-DD]
## Change Summary
[1-2 sentences.]
## Motivation
[Player problem / MDA alignment.]
## Design Delta
Current GDD (`design/gdd/[file].md`, [section]):
> [exact quote]
Replacement specification:
[Unambiguous Detailed-Rules-grade behavior.]
## New Rules / Values
[Replacement rules, states, parameter ranges.]
## Affected Systems
| System | Impact | Action Required |
|--------|--------|-----------------|
## Acceptance Criteria
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]
- [ ] No regression: [original behavior]
## GDD Update Required?
[Yes / No — file, section, proposed edit.]
```

### New Small System
```markdown
# Quick Design Spec: [Title]
**Type**: New Small System | **Scope**: [1-2 sentences] | **Date**: [YYYY-MM-DD] | **Estimated Implementation**: [hours]
## Overview
[One clear paragraph.]
## Core Rules
[Numbered sequential behavior + bullet conditions.]
## Tuning Knobs
| Knob | Default | Range | Category | Rationale |
|------|---------|-------|----------|-----------|
All values live in `assets/data/[file].json`, never hardcoded.
## Acceptance Criteria
- [ ] [Functional criterion]
- [ ] [Edge-case criterion]
- [ ] [Experiential feel criterion]
- [ ] [Regression criterion]
## Systems Index
[Note layer/priority if adding, or "Below systems-index tracking threshold — quick spec is sufficient."]
```

## 4. Approval, Filing & Handoff

1. Present draft (`[A] Approve` / `[B] Revise` / `[C] Redirect to ags-gdd design-system`).
2. On approval, confirm write to `design/quick-specs/[kebab-case-title]-[YYYY-MM-DD].md` (honor `modes.automation`), create directory if absent, and write file.
3. If a GDD edit is required, show exact old vs new diff and confirm updating `design/gdd/[filename].md` separately before editing.
4. Hand off to `ags-dev` (`readiness [story-path]`), referencing the quick spec path in the story's GDD Reference field.
