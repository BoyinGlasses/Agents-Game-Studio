---
name: ags-qa
description: "Use when scaffolding test infrastructure, generating test helpers, planning sprint QA, running smoke checks, maintaining regression suites, designing soak tests, detecting test flakiness, or authoring playtest reports. Do NOT use when reviewing/closing a single implemented story (-> ags-verify), filing or triaging bugs (-> ags-bugs), or profiling performance/security (-> ags-diagnose)."
---

# Quality Assurance & Playtest Suite

Unified QA workflow covering test setup, test helper generation, sprint QA planning, smoke gating, regression maintenance, soak protocols, CI flakiness detection, and playtest reporting.

## Contract

- **Inputs**: `project.yaml`, `project.local.yaml`, `production/sprints/`, `production/sprint-status.yaml`, `production/epics/**/story-*.md`, `design/gdd/`, `docs/architecture/{tr-registry.yaml,control-manifest.md}`, `tests/`, `test-results/`, `production/qa/`, `docs/engine-reference/<engine>/`
- **Roles**: `qa-lead` (sprint QA planning, coverage targets, regression/flakiness sign-off), `test-engineer` (test setup, helpers, headless runner execution, smoke gating, soak protocols, flakiness triage, playtest reporting), `creative-director` (`CD-PLAYTEST` gate in full review mode), `game-designer` / `art-ux-director` (Visual/Feel and UI evidence sign-off), plus configured engine specialist (`godot-specialist`, `unity-specialist`, `unreal-specialist`) for runner and framework API resolution
- **Outputs**: `tests/` scaffold & `.github/workflows/tests.yml` (`test-setup`), `tests/helpers/` (`test-helpers`), `production/qa/qa-plan-*.md` (`qa-plan`), `production/qa/smoke-*.md` (`smoke-check`), `tests/regression-suite.md` (`regression-suite`), `production/qa/soak-test-*.md` (`soak-test`), `production/qa/flakiness-report-*.md` (`test-flakiness`), `production/qa/playtests/playtest-*.md` (`playtest-report`)
- **Verification**: `python .ags/cli.py check coherence` before smoke checks, `python .ags/cli.py verify`, engine headless test execution where available, CI log parsing, and explicit `NOT ASSESSED` reporting when tests, runners, inputs, or denominators are missing
- **Next Skill**: `ags-bugs` (report/triage defects from smoke, soak, or playtest), `ags-verify` (close stories after test evidence passes), `ags-gate` (Polish/Release phase readiness), `ags-diagnose` (profile hotspots or security risks uncovered in QA)

## Preflight

Run once at startup and apply the resolved values without re-deriving them:

```bash
python .ags/cli.py preflight ags-qa [sub-mode] [args]
```

- **`modes.automation`**: `collaborative` (ask before every decision and write), `guided` (ask on major decisions and new files; proceed with summary on updates), `autonomous` (pick recommended options, write directly, log choices to `production/session-logs/decision-log.md` except `modes.automation_always_ask`).
- **`modes.review_mode`**: `full` | `lean` | `solo` (`--review <mode>` overrides for this run). Governs `.ags/gates/cd-playtest.md` in `playtest-report`.
- **`modes.workflow` & `workflow_overrides.system_overrides`**: Resolve per GDD filename stem (`design/gdd/<stem>.md`; `TR-[system]-NNN` is fallback alias only) in `qa-plan` and `regression-suite audit`.
- **`qa.level`** (`minimal` | `standard` | `full`): Independent axis from `workflow` — controls whether automated tests are required (`qa-plan`), whether smoke failures block (`smoke-check`), and whether `regression-suite` runs (`minimal` stops early).
- **`testing.strict.config`**: Controls `smoke-check` FAIL blocking when `qa.level` is `standard` or `full` (defaults to **blocking** if unset).
- **`engine.name` / `testing.framework` / `performance.*`**: Read from preflight (`project.yaml` plus any legacy technical-preferences fallback). Never guess an unconfigured engine or fall back to Godot defaults.

## Phases

Select the requested sub-mode (or ask the user to choose if omitted) and follow its dedicated playbook:

1. **`test-setup [force]`** -> [references/test-setup.md](references/test-setup.md)
   - Require configured engine (`ags-settings` if missing). Check existing `tests/` and CI; `force` creates missing files only and never overwrites existing test files.
   - Scaffold `tests/{unit,integration,smoke}/`, `tests/README.md` (manual evidence under `production/qa/evidence/`), engine runner, `tests/smoke/critical-paths.md`, and `.github/workflows/tests.yml`.
2. **`test-helpers [system|all|scaffold]`** -> [references/test-helpers.md](references/test-helpers.md)
   - Resolve `testing.framework` assertion API before emitting code; **never emit bare `assert()`** and **never extend the test-suite base class** in `tests/helpers/`. If the framework API cannot be confirmed against project/engine docs, generate no helper.
   - Sample existing `tests/**/*_test.*` conventions and GDD `Formulas` / `Edge Cases` to write `tests/helpers/` without overwriting existing files.
3. **`qa-plan [sprint|feature:<sys>|story:<path>|full]`** -> [references/qa-plan.md](references/qa-plan.md)
   - Enforce **N=0 guard**: zero resolved stories stops with `NOT ASSESSED — no stories in scope`.
   - Use targeted section reads per story, preserve authoritative `Type:` headers (flag missing `Type:` when inferred), mine GDD sections per system workflow tier and `qa.level`, apply `.ags/templates/test-plan.md`, write `production/qa/qa-plan-[sprint-slug]-[date].md`, optionally back-fill story `## QA Test Cases`, and record in `production/session-state/active.md`.
4. **`smoke-check [sprint|quick] [--platform pc|console|mobile|all]`** -> [references/smoke-check.md](references/smoke-check.md)
   - Run `python .ags/cli.py check coherence` first. Verify actual game test files exist under `tests/{unit,integration,smoke}/` (placeholder directories alone yield `NOT ASSESSED`).
   - Run engine tests headlessly (Unity requires `com.unity.test-framework` check + `timeout 900`), map story coverage, execute manual smoke batches naming `Checklist source:`, write `production/qa/smoke-[date].md`, and enforce `qa.level` + `testing.strict.config`.
5. **`regression-suite [update|audit|report]`** -> [references/regression-suite.md](references/regression-suite.md)
   - Early `qa.level: minimal` guard stops before any scan.
   - Map critical paths (GDDs per workflow tier, or latest smoke report at `workflow: minimal`) and closed bugs (`production/qa/bugs/*.md`), detect coverage drift, and update `tests/regression-suite.md` (empty denominator forces `NOT ASSESSED` instead of `0%`/`100%`).
6. **`soak-test [30m|1h|2h|4h] [memory|stability|balance|all]`** -> [references/soak-test.md](references/soak-test.md)
   - Generate timed observation checkpoints using unit-agnostic deltas against T+0 (plus Godot Orphan Nodes floor) — never convert or guess unverified monitor units. Human runs the session; write `production/qa/soak-test-[date]-[duration].md`.
7. **`test-flakiness [ci-log-path|scan|registry]`** -> [references/test-flakiness.md](references/test-flakiness.md)
   - Parse JUnit XML or engine logs across runs, classify failure rate (>25% quarantine, 5–25% fix soon, 1–5% monitor) and root cause, append quarantine entries to `tests/regression-suite.md` (never delete test files), and optionally write `production/qa/flakiness-report-[date].md`.
8. **`playtest-report [new|analyze <path>]`** -> [references/playtest-report.md](references/playtest-report.md)
   - Generate blank template or structure raw playtest notes, route findings (design -> `ags-design-review`, balance -> `ags-design-review`, bugs -> `ags-bugs`, polish -> `production/`), invoke `creative-director` on `.ags/gates/cd-playtest.md` in `full` review mode only, and save to `production/qa/playtests/`.

## Gate & Verdict

Verdict precedence (first matching tier wins; **`NOT ASSESSED` strictly outranks all PASS variants and ranks below FAIL/BLOCKED**):

1. **`FAIL` / `BLOCKED`**: Automated test failure, headless timeout (exit 124), Batch 1/2 or `--platform` smoke failure (blocking unless `qa.level: minimal` or `testing.strict.config: false`), confirmed soak leak/crash/severe fatigue, `CD-PLAYTEST` `REJECT`, missing required engine config, or declined write approval.
2. **`NOT ASSESSED`**: Zero stories (`qa-plan`), zero game test files or unconfirmed `NOT RUN` suite or missing Unity Test Framework or `UNKNOWN` story row or skipped Batch 3 (`smoke-check`), zero GDD/smoke critical paths or zero tests (`regression-suite`), truncated/unrun/uninstrumented soak (`soak-test`), insufficient CI run history (`test-flakiness`), or unconfirmed framework assertion API (`test-helpers`). Never substitute a pass or numeric percentage when assessment could not occur.
3. **`PASS WITH WARNINGS` / `PASS WITH CONCERNS`**: Suite passed (or `NOT RUN` explicitly confirmed via local IDE/CI), core checks passed, but advisory `MISSING` test evidence, non-blocking drift, or minor soak drift remains.
4. **`PASS` / `COMPLETE`**: All required checks ran and passed with zero blocking gaps and approved artifacts written.
