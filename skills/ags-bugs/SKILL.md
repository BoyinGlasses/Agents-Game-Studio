---
name: ags-bugs
description: "Use when filing structured bug reports, analyzing code for potential defects, verifying or closing bug fixes, or triaging the open bug backlog and trends. Do NOT use when auditing security vulnerabilities or performance budgets (-> ags-diagnose), running QA smoke or regression suites (-> ags-qa), or deploying an emergency hotfix (-> ags-release)."
---

# Bug Reporting, Verification & Triage

Manages the full defect lifecycle — drafting `BUG-[NNNN]` reports, analyzing source files for defects, verifying fixes against reproduction steps and tests, closing verified bugs, and triaging sprint backlogs and systemic trends.

## Contract

- **Inputs**: Bug description or target code path, `production/qa/bugs/*.md` (fallback `production/qa/bugs.md` or `production/qa/qa-plan-*.md`), `production/sprints/`, `production/epics/**/story-*.md`, `tests/`, `project.yaml`, `project.local.yaml`
- **Roles**: `test-engineer` (reproduction, fix verification, regression checks), `qa-lead` (severity/priority classification, sprint triage, systemic trend analysis), `gameplay-coder` (optional root-cause inspection)
- **Outputs**: `production/qa/bugs/BUG-[NNNN].md` (`report` / `analyze`), updated bug status and `## Closure Record` (`verify` / `close`), `production/qa/bug-triage-[date].md` (`triage`)
- **Verification**: Codebase root-cause search under resolved code root (`src/`, `Assets/`, `Source/<Module>/`), targeted test execution in `tests/`, regression pattern scan, strict `Verified Fixed` gate before closure, and `NOT ASSESSED` when backlog or verification inputs are missing
- **Next Skill**: `ags-release` (`hotfix` for S1/S2 blockers or failed verification), `ags-qa` (regression tests or smoke re-gate), `ags-plan` (sprint status/capacity adjustment)

## Preflight

Run once at startup and hold resolved settings for the run:

```bash
python .ags/cli.py preflight ags-bugs [sub-mode] [args]
```

- **`modes.automation`**: `collaborative` (prompt on decisions and file writes), `guided` (prompt on major choices and new files; summarize updates), `autonomous` (pick recommended choice, write directly, log to `production/session-logs/decision-log.md` except `modes.automation_always_ask`).
- **Code root**: Resolve from `engine.name` (`src/` Godot, `Assets/` Unity, `Source/<Module>/` Unreal). If unresolved during code-scanning sub-modes (`analyze`, `verify`), report **`NOT ASSESSED — code root unresolved`** rather than returning a zero-hit clean scan.

## Phases

Route to the requested sub-mode (defaulting to `report` when a description is given, or `triage` when triaging open bugs):

1. **Bug Report Lifecycle** -> [references/bug-report.md](references/bug-report.md)
   - **`report [description]`**: Parse symptoms (prompt if blank), search resolved code root for affected files, draft `BUG-[NNNN]` using the shared `S1`–`S4` / `P1`–`P4` ladder (`P4-Won't fix`, never `P4-Wishlist`), and write to `production/qa/bugs/BUG-[NNNN].md`.
   - **`analyze [path]`**: Inspect target file(s) for null references, off-by-one errors, race conditions, unhandled edge cases, resource leaks, and invalid state transitions; draft structured bug reports with trigger scenario and recommended fix.
   - **`verify [BUG-ID]`**: Read `production/qa/bugs/[BUG-ID].md`, check whether root-cause code path remains, run system tests in `tests/`, scan for pattern recurrence, and assign `VERIFIED FIXED`, `STILL PRESENT` (reopen `Open`, route to `ags-release hotfix`), or `CANNOT VERIFY`.
   - **`close [BUG-ID]`**: Enforce **`Status: Verified Fixed`** precondition (stop and route to `ags-bugs verify` if unmet), append `## Closure Record` (`Verified by: test-engineer`), set top-level `**Status**: Closed`, and check `production/qa/bug-triage-*.md` for refresh needs.
2. **Backlog Triage & Trends (`triage [sprint|full|trend]`)** -> [references/bug-triage.md](references/bug-triage.md)
   - Default to `sprint` when an active sprint exists, else `full`.
   - Discover backlog (`production/qa/bugs/*.md` -> `production/qa/bugs.md` -> `production/qa/qa-plan-*.md`); stop with `NOT ASSESSED` if zero bug records exist.
   - In `trend` mode (read-only), extract only bolded header fields (`**Severity**`, `**Priority**`, `**Status**`, `**System**`, `**Category**`, `**Reported**`) and targeted story-status matches without full-reading bug bodies.
   - Separate objective Severity (`S1`–`S4`) from team-owned Priority (`P1`–`P4`), respect sprint capacity (flag `Priority overflow` rather than over-committing), flag systemic deviation patterns (3+ bugs in one system, 2+ S1/S2 in one story, regressions on `Complete` stories), analyze volume/hot-spots/age, and confirm before writing `production/qa/bug-triage-[date].md` or marking any bug `P4 — Won't fix`.

## Gate & Verdict

Verdict precedence (first match wins; **`NOT ASSESSED` ranks above `COMPLETE`/`VERIFIED FIXED` and below `STILL PRESENT`/`BLOCKED`**):

1. **`STILL PRESENT` / `BLOCKED`**: Bug reproduces during `verify`, `close` invoked without `Status: Verified Fixed`, or user declined a required file write / status transition.
2. **`NOT ASSESSED`** (`CANNOT VERIFY`): Missing bug files in `triage`, missing `BUG-ID` file, unresolved code root in `analyze`/`verify`, or automated checks inconclusive requiring manual playtest verification. Never mark a bug `VERIFIED FIXED` or closed without positive verification.
3. **`COMPLETE` / `VERIFIED FIXED`**: Repro steps no longer trigger the defect and related tests pass (`verify`), closure record written (`close`), bug report filed (`report`/`analyze`), or triage report generated and approved (`triage`).
