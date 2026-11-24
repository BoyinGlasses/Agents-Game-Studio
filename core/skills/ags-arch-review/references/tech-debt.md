# Technical Debt Register (`ags-arch-review tech-debt`)

Tracks, categorizes, scores, and reports codebase technical debt in `docs/tech-debt-register.md`.

## Phase 1: Parse Subcommand

Require one subcommand:
- `scan`: Scan resolved source tree for debt indicators and append findings.
- `add`: Interactively record a single manual debt entry.
- `prioritize`: Re-score and sort `docs/tech-debt-register.md`.
- `report`: Read-only summary statistics and stale-item alerts.

Missing subcommand -> output usage and stop (`FAIL — missing required subcommand`).

---

## Phase 2A: Scan Mode

1. **Resolve code root from preflight (`src/` Godot, `Assets/` Unity, `Source/` Unreal)** and count scanned source files (`N_files`) BEFORE reporting findings:
   - If code root is unresolved OR `N_files == 0`, emit:
     `NOT ASSESSED — no source files to scan` (name unresolved root or empty directory) and **STOP**. Do not write `docs/tech-debt-register.md` and do not emit `COMPLETE`.
   - Always report the denominator `N_files` alongside findings (including when findings are zero over `N_files > 0`, which is a clean codebase rather than an empty scan).
2. Scan resolved code root for:
   - `TODO` comments (count & categorize)
   - `FIXME` comments (bugs disguised as debt)
   - `HACK` comments (workarounds needing proper fixes)
   - `@deprecated` markers
   - Duplicated code blocks across files
   - Files over 500 lines (potential god objects) and functions over 50 lines (complexity candidates)
3. Categorize every finding into: **Architecture Debt**, **Code Quality Debt**, **Test Debt**, **Documentation Debt**, **Dependency Debt**, or **Performance Debt**.
4. Present findings with scanned file count, confirm write to `docs/tech-debt-register.md` (append new entries without overwriting existing rows). Declined -> `BLOCKED`.

---

## Phase 2B: Add Mode

1. Collect description, affected files, and impact if unfixed.
2. Prompt for **Category** (Architecture / Code Quality / Test / Documentation / Dependency / Performance) and **Estimated Fix Effort** (`S < 1d`, `M 1–3d`, `L 3–7d`, `XL > 1w`).
3. Present complete entry (including rationale for accepting the debt) and confirm append to `docs/tech-debt-register.md`.

---

## Phase 2C: Prioritize Mode

1. Read `docs/tech-debt-register.md`. (If absent/empty, emit `NOT ASSESSED — no tech debt register found`.)
2. Score each item:
   `Priority Score = (impact_if_unfixed × frequency_of_encounter) / fix_effort`
3. Sort descending by priority score, recommend top candidates for the next sprint, present, and confirm overwrite of `docs/tech-debt-register.md`.

---

## Phase 2D: Report Mode (Read-Only)

Read `docs/tech-debt-register.md` (if absent/empty -> `NOT ASSESSED`) and output:
- Counts by category and summed estimated effort
- Items added vs resolved since previous report and trend (`growing | stable | shrinking`)
- Alert flag on any entry older than **3 sprints** without action (must either be scheduled or explicitly re-accepted with documented rationale).

---

## Debt Register Format & Rules

```markdown
## Technical Debt Register
Last updated: [Date]
Total items: [N] | Estimated total effort: [T-shirt sizes summed]

| ID | Category | Description | Files | Effort | Impact | Priority | Added | Sprint |
|---|---|---|---|---|---|---|---|---|
| TD-001 | [Cat] | [Description] | [files] | [S/M/L/XL] | [Low/Med/High/Critical] | [Score] | [Date] | [Sprint or Backlog] |
```

- Every entry must document **why** it was accepted (deadline, prototype, missing info).
- Next steps: `ags-plan sprint` to schedule priority debt; `ags-arch-review tech-debt report` at sprint start.
