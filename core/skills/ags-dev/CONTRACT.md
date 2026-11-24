# ags-dev — Story Readiness & Development Contract

## Role in Pipeline
Validates story readiness (`readiness` mode, strictly read-only) and drives approved story implementation (`implement` mode) from Checkpoint #1 through bounded implementation, local parse/test/run verification, and immediate handoff to `ags-verify`. Only `ags-verify` may write `Status: Complete` after Checkpoint #2 game-maker acceptance.

## Inputs
- Story file at `production/epics/[epic-slug]/story-NNN-[slug].md` (`Status: Ready` for new work, or `Status: In Progress` with `**Story Approval**: YYYY-MM-DD` for resume).
- `production/session-state/active.md` (latest approval extract, active story, and any pending decisions per story path).
- Supporting context: `design/gdd/systems-index.md`, `docs/architecture/tr-registry.yaml`, `docs/architecture/control-manifest.md`, governing `docs/architecture/adr-*.md`, `docs/engine-reference/<engine>/VERSION.md`, `project.yaml`, `project.local.yaml`.

## Preconditions
- In `readiness` mode: scope resolves to >=1 story file; zero files yields `NOT ASSESSED — no stories in scope` (`ags-plan` remediation). Never emit `Ready: 0 / Needs Work: 0 / Blocked: 0` over an empty set.
- In `implement` mode: run readiness validation first for every new `Ready` story; only `READY` proceeds to Checkpoint #1. Skip readiness rerun only on an approved `In Progress` resume with matching extract and zero drift.
- Never infer `Handoff Class: Technical` solely from `Type: Logic`; any player-observable effect requires `Player-facing` or `Mixed`.
- At `full` workflow tier, missing TR registry or governing ADR sets `BLOCKED` in session state and stops. At `standard`/`minimal`, only a referenced ADR that is missing or `Proposed` blocks; an unreadable ADR status is `NOT ASSESSED` and stops before Checkpoint #1.
- Never trust an improvised story `Risk:` field over `docs/engine-reference/<engine>/VERSION.md`; `VERSION.md` wins and unknown counts as `HIGH`.

## Outputs & Immutability
- **`readiness` mode**: strictly read-only; offers draft fixes in conversation only; never edits files.
- **`implement` mode**:
  | Artifact | Contract |
  | --- | --- |
  | Story file | After Checkpoint #1 approval, write `Handoff Class:`/`Verification Method:` if absent, approved ADR/manifest versions, `**Story Approval**: YYYY-MM-DD`, `Status: In Progress`, `Last Updated`. Never write `Complete`. |
  | `production/sprint-status.yaml` | Set matching entry `status: in_progress` and `updated: YYYY-MM-DD` if file exists; otherwise state `Sprint status not updated: production/sprint-status.yaml absent`. |
  | `production/session-state/active.md` | Persist approval extract (story path, date, scope/Out of Scope, criteria, class, method, `Pending decision: None`), implementation summary, `Verification`, `Run result`, and pending scope decisions. |
  | Code & tests | Primary agent writes within approved scope at resolved code root and `tests/` (`qa.level: minimal` waives test file and prints waiver line). Routine in-scope new/edited files need no per-file write prompt. |
  | Visual & tuning evidence | Retained screenshot(s) in `production/qa/evidence/[story-slug]/` + Playtest & Game Feel Tuning Card for `Player-facing`/`Mixed` stories. |

## Decision Boundaries
- **Checkpoint #1**: Present Goal, Scope (`Out of Scope`), all Acceptance Criteria, `Handoff Class`, and `Verification Method` in one card; wait for explicit `Approve this story` in every automation mode.
- **Scope-change pause**: Stop before touching out-of-scope files, changing criteria/handoff fields, making consequential gameplay/architecture choices, or changing the engine. Record `Pending decision:` in `active.md` and wait for revised Checkpoint #1 approval.
- **Partial work**: Never hand off partial edits or failing parses as complete (`INCOMPLETE`); resolve or record `NOT VERIFIED — <reason>`.

## Downstream (`ags-verify`)
`ags-verify` reads the approved story, `active.md` approval extract, changed files, test/parse outputs, `Run result`, and tuning card to execute `code-reviewer` review, `python .ags/cli.py verify`, and Checkpoint #2 acceptance.
