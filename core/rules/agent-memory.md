---
paths:
  - ".ags/state/**"
  - ".ags/memory/**"
---

# Agent Memory & Scratch State Rules

`.ags/state/` and `.ags/memory/` are workspace-local scratch/state locations. Never use scratch notes to bypass project design docs, ADRs, or story checkpoints.

## Never Record a Temporary Absence as a Durable Fact

AGS ships as a template initialized into a fresh game repo. Early in a project, `src/` / `Assets/` / `Source/`, GDDs, or `tests/` may be absent — and every one of those absences will stop being true as the game grows.

- **Prefer recording a method over an absence state.** Record `"Verify configured engine and existing profile before profiling; return NOT ASSESSED naming missing inputs"` rather than `"This repo has no game code."`
- **If a state snapshot is recorded, state what invalidates it on the same line:**
  `INVALIDATED WHEN: project.yaml configures engine.name or code root contains game source.`
- **Never record absence of game code, assets, tests, or config as a permanent project property.**

## Disclose & Verify

- Any durable note written outside explicit story/doc deliverables must be disclosed in the response with its path.
- Before acting on a recalled note naming a file, path, setting, or count, verify the target on disk first. Memory is a starting point, never verification evidence (see `.ags/rules/skill-authoring.md`).
