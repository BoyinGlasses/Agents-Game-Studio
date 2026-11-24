# Task Effort Estimation (`ags-plan estimate`)

Strictly **read-only** 3-point effort estimation (`Optimistic / Expected / Pessimistic`) for tasks or stories based on codebase complexity, integration scope, risk, and historical sprint velocity. Never writes files.

## Phase 1: Understand Task & Project Context

1. Read task/story description from argument (ask for clarification if too vague to estimate meaningfully).
2. Read `AGENTS.md` and `project.yaml` for tech stack, coding standards, and estimation guidelines.
3. Read relevant GDDs in `design/gdd/` (or `design/game-brief.md` at `minimal`).

---

## Phase 2: Scan Codebase & Historical Velocity

1. Resolve code root (`src/` Godot, `Assets/` Unity, `Source/` Unreal) from preflight (`NOT ASSESSED` if code root unresolved when scanning source files).
2. Inspect affected files/modules: size, dependency/coupling count, integration points, existing test coverage in `tests/`.
3. Read past sprint plans/reports in `production/sprints/` for comparable task complexity and actual historical velocity.

---

## Phase 3: Analyze Complexity, Scope & Risk

- **Code Complexity**: Affected LOC, dependencies/coupling, core/engine vs leaf/feature code, existing pattern reuse vs new patterns.
- **Scope**: Systems touched, new vs modified code, automated tests required, data migration/config changes.
- **Risk**: Unfamiliar APIs/post-cutoff engine risk, ambiguous requirements, upstream blockers, cross-system coupling, performance sensitivity.

---

## Phase 4: Output 3-Point Estimate

Emit the structured read-only report (`Optimistic | Expected | Pessimistic`, rounded to **half-day increments**):

- **Task Description** (1–2 sentences)
- **Complexity Assessment** (`Systems affected`, `Files likely modified`, `New code vs modification`, `Integration points`, `Test coverage needed`, `Existing patterns available`) + key affected file paths
- **Effort Estimate**: `Optimistic | Expected | Pessimistic` with explicit assumptions (**Recommended budget = Expected**, never Optimistic)
- **Confidence**: `High | Medium | Low` + driving factors
- **Risk Factors** (`Risk | Likelihood | Impact | Mitigation`)
- **Dependencies** (`Dependency | Status | Impact if Delayed`)
- **Suggested Breakdown** (`Research/spike`, `Core implementation`, `Testing & validation`, `Total = Expected`)
- **Notes and Assumptions**

Rules: Never output a single point estimate; never silently pad estimates — make risk explicit.

---

## Phase 5: Next Steps

- Confidence `Low` -> recommend time-boxed spike via `ags-ideate prototype`.
- Estimate `> 10 days` -> recommend splitting via `ags-plan stories`.
- Ready to schedule -> route to `ags-plan sprint update`.
