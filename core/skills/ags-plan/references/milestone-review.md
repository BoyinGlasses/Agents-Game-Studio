# Milestone Review (`ags-plan milestone`)

Evaluates milestone completeness, quality metrics, code health, velocity trend, and go/no-go status with `PR-MILESTONE` review.

## Insufficient Input Guard (Always Check First)

Before drafting any report section:
1. Inventory required inputs (`milestone definition`, `sprint reports`, `sprint-status.yaml`, `bug tracker / QA metrics`, `resolved code root`) and mark each `FOUND` or `ABSENT`.
2. Any section whose input is `ABSENT` MUST read **`NOT ASSESSED — NO DATA`** (never infer or estimate from unrelated files).
3. If **all** required inputs are `ABSENT`, STOP immediately and emit overall verdict **`NOT ASSESSED — NO DATA`**, naming the missing files and the producing skill (`ags-plan sprint`, `ags-bugs`, etc.).

---

## Phase 1: Load Milestone & Sprint Reports

1. Parse argument (`current` or `<milestone-name>`).
2. Read `production/milestones/` if present. When selecting `current`, pick the most recently modified definition file **skipping files ending in `-review.md`** (previous outputs from this skill). If `production/milestones/` is absent or empty, state so explicitly and review against sprint reports alone without inventing a milestone definition.
3. **Bounded sprint report scan**: Establish denominator **N** across `production/sprints/sprint-*.md`, then pattern-search exact headings emitted by `ags-plan sprint`:
   `^## (Sprint Goal|Capacity|Tasks|Carryover|Risks|Progress|Burndown Assessment|Emerging Risks|Definition of Done)` (+12 lines).
   Full-read any sprint report matching zero sections (older format) or referencing external files; report any sprint contributing zero data rather than silently omitting it.

---

## Phase 2: Codebase Health & Risk Register

- **Code health**: Resolve code root (`src/`, `Assets/`, `Source/`) via preflight. If unresolved or empty, record Code Health as `NOT ASSESSED`; otherwise count `TODO`, `FIXME`, and `HACK` markers across resolved code root.
- **Risk register**: Check `production/risk-register/` if present (manually authored from `.ags/templates/risk-register-entry.md`). If absent, note explicitly rather than skipping silently.

---

## Phase 3: Review Report & `PR-MILESTONE` Gate

Structure `# Milestone Review: [Name]` with: `## Overview`, `## Feature Completeness` (`Fully Complete`, `Partially Complete`, `Not Started`), `## Quality Metrics` (`S1/S2/S3` bugs, Test Coverage, Performance), `## Code Health`, `## Risk Assessment`, `## Velocity Analysis`, `## Scope Recommendations` (`Protect`, `At Risk`, `Cut Candidates`), `## Go/No-Go Assessment` (`NOT ASSESSED | GO | CONDITIONAL GO | NO-GO`), and `## Action Items`.

**`PR-MILESTONE` gate (Phase 3b)**:
- `solo` / `lean`: Skip with note (`"PR-MILESTONE skipped — Solo/Lean mode."`) and state Go/No-Go from observed metrics without producer verdict.
- `full`: Spawn `producer` pointing to `.ags/gates/pr-milestone.md` (parent does not read the gate file), passing milestone name/target date, completion `%`, blocked count, sprint velocity, and cut candidates:
  - `OFF TRACK`: Prompt (`[A] Accept NO-GO` / `[B] Override to CONDITIONAL GO with user-documented risks` / `[C] Stop to resolve blockers`). Never issue `GO` over `OFF TRACK` unless user explicitly picks `[B]`.
  - `AT RISK`: Prompt (`[A] CONDITIONAL GO` / `[B] NO-GO` / `[C] GO accepting risk`).
  - `ON TRACK`: Proceed to `GO` (unless inputs forced `NOT ASSESSED`).

---

## Phase 4: Save & Next Steps

Present the review, confirm write to `production/milestones/[milestone-name]-review.md` (`COMPLETE` on save, `BLOCKED` on decline), and recommend `ags-gate` (if milestone closes a phase) or `ags-plan sprint update`.
