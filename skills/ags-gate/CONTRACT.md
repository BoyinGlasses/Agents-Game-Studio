# ags-gate — Phase Gate Contract

## Role in Pipeline
Validates phase-transition readiness across the 7 game development stages (`Concept` -> `Systems Design` -> `Technical Setup` -> `Pre-Production` -> `Production` -> `Polish` -> `Release`), returning an advisory `PASS` / `CONCERNS` / `NOT ASSESSED` / `FAIL` verdict and updating `project.stage` + `production/stage.txt` only upon `PASS` and explicit user confirmation.

## Inputs
- `project.yaml` (`project.stage`, `modes.workflow`, `modes.qa.level`, `modes.review_mode`, `modes.team.size`, `workflow_overrides.*`, `performance.*`, `testing.strict.*`) + `project.local.yaml` + legacy `production/stage.txt`
- `docs/consistency-failures.md` (optional domain scrutiny context)
- `docs/engine-reference/<engine>/VERSION.md` and `deprecated-apis.md`
- Stage artifacts checked deterministically via `python .ags/cli.py check artifacts --phase <source-phase>`, `python .ags/cli.py check gdd`, and `python .ags/cli.py check adr-graph`

## Preconditions
- Target phase is one of `systems-design`, `technical-setup`, `pre-production`, `production`, `polish`, `release` (or detected and user-confirmed).
- `ags-gate` honors `workflow`, `qa.level`, `testing.strict`, `performance.enforce`, `team.size`, and `review_mode`, and is **exempt from `modes.automation`** (never auto-run or auto-advanced).
- **Smoke-check floor & performance independence**: `qa.level: minimal` never waives the build-health smoke report, and `workflow: minimal` never suppresses `performance.enforce`.
- **Zero-artifact `NOT ASSESSED` guard**: If reductions leave 0 required artifacts, return `NOT ASSESSED` — never `PASS`.
- **Unmatched `system_overrides` check**: Every key in `workflow_overrides.system_overrides` must resolve to `design/gdd/<key>.md`; unmatched keys emit `CONCERNS`.
- **Vertical Slice rule**: A skipped Vertical Slice downgrades to `CONCERNS`; a built Vertical Slice with any `NO` validation item is an automatic `FAIL` regardless of workflow tier.

## Outputs & Immutability
- **Read-only on project docs/code**: Never creates missing GDDs, ADRs, tests, or source files to manufacture a `PASS`.
- **Optional report write**: `production/gate-checks/gate-[phase]-[date].md` (written only after user confirmation), containing artifact checklist, quality checks, Blockers, Recommendations, Director Panel summary, Verdict, and Chain-of-Verification note.
- **Stage advance write**: Updates `project.stage` in `project.yaml` AND `production/stage.txt` (dual-write, verified matching) ONLY when verdict is `PASS` and user explicitly confirms advancement. Never writes stage on `FAIL`, `CONCERNS`, or `NOT ASSESSED` unless user explicitly overrides with documented risk.

## Downstream
- `systems-design` PASS -> `ags-architect` (blueprint before ADRs), `ags-settings`
- `technical-setup` PASS -> `ags-architect` (control manifest), `ags-ideate` (vertical slice), `ags-plan`
- `pre-production` PASS -> `ags-dev`, `ags-plan`
- `production` PASS -> `ags-diagnose`, `ags-qa`
- `polish` PASS -> `ags-release`
