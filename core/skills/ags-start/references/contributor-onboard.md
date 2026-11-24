# Contributor Onboarding Document (`ags-start contributor <role>`)

Generates an orientation briefing for a new contributor or agent joining the project.

## Pre-Check: Insufficient Input Guard

Before generating any section, list required inputs and record each as `FOUND` or `ABSENT` (never assume present):
- `AGENTS.md` and `project.yaml`
- Target role definition `.ags/roles/<role>.md` (if specified)
- Area artifacts (resolved code root `src/`/`Assets/`/`Source/` for programmers; `design/` for designers; `design/narrative/` for narrative; `tests/` for QA; `production/` for producers)
- Recent `git log --oneline -20` (if git repository exists)

Rules:
- Any section whose required inputs are `ABSENT` MUST read **`NOT ASSESSED — NO DATA`** (never guess or fabricate conventions/code paths).
- If **every** required project input is `ABSENT`, stop and emit **`NOT ASSESSED — NO DATA`** as the overall verdict, naming missing files and the producing skills (`ags-start`, `ags-settings`, `ags-ideate`).

## Phase 1: Load Role & Project Context

1. Read `AGENTS.md` and `project.yaml` for project overview, engine, naming, and workflow settings.
2. If a role was specified, read `.ags/roles/<role>.md` (and any relevant domain lens in `.ags/roles/`).

## Phase 2: Scan Target Area

- **Programmer / Engine Specialist**: Resolve code root (`src/`, `Assets/`, `Source/`). Report `NOT ASSESSED — code root unresolved` if ambiguous/unset; otherwise inspect architecture patterns and key modules.
- **Game Designer / Art-UX**: Scan `design/` (or `design/narrative/`).
- **QA / Test Engineer**: Scan `tests/` and `production/qa/`.
- **Producer**: Scan `production/` (`epics/`, `sprints/`, `milestones/`, `sprint-status.yaml`).
- Check recent `git log` commits for current momentum.

## Phase 3: Draft & Confirm Onboarding Document

Draft the structured onboarding doc covering:
1. `## Project Summary`
2. `## Your Role`
3. `## Project Architecture` (`### Key Directories`, `### Key Files`)
4. `## Current Standards and Conventions`
5. `## Current State of Your Area`
6. `## Current Sprint Context`
7. `## Key Dependencies`
8. `## Common Pitfalls`
9. `## First Tasks` (read docs -> review code/content -> small starter task)
10. `## Questions to Ask`

Present the draft to the user and confirm destination `production/onboarding/onboard-[role]-[date].md` (respecting `modes.automation`). Create directory if needed and write on confirmation.

## Phase 4: Hand Off

- Suggest `ags-plan status` to inspect current sprint progress.
- Suggest `ags-start help` for next-step navigation.
