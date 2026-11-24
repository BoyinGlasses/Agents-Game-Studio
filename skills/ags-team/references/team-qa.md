# Team Playbook: QA (`ags-team qa`)

Orchestrates sprint/feature scoping, smoke gating, QA strategy, test-plan creation, manual test cases, execution/evidence capture, and QA sign-off.

## Active-Set & Role Mapping (`team.size`)

- **`individual`** (default): `test-engineer` (`.ags/roles/test-engineer.md`) only; `qa-lead` (`.ags/roles/qa-lead.md`) invoked at phases ending in a user decision point only.
- **`small`**: `qa-lead` + `test-engineer` full pipeline.
- **`studio`**: `qa-lead` + per-story `test-engineer` spawns + formal sign-off.
- Directors (`creative-director`, `technical-director`, `producer`) spawn at decision-gated phases per `modes.review_mode`.

Announce the active roster and unspawned roles before Phase 1.

## Pipeline

### Phase 1: Load Context

1. Resolve sprint or feature scope from the argument:
   - Sprint ID (e.g., `sprint-03`): search `production/sprints/` for matching `*[sprint-identifier]*.md` (use most recently modified if multiple).
   - Feature scope (`feature: [system-name]`): search story files under `production/epics/` tagged for that system.
   - No argument: read `production/session-state/active.md` and `production/sprint-status.yaml` (if present) to infer the active sprint.
2. Read `project.stage` from `project.yaml` (fallback `production/stage.txt`).
3. Report story count and current stage to the user before starting QA strategy.

### Phase 2: QA Strategy (`qa-lead`)

Delegate to `qa-lead` to review all in-scope stories:
- Classify each story: `Logic` | `Integration` | `Visual/Feel` | `UI` | `Config/Data`.
- Determine which stories require automated test evidence vs manual QA walkthroughs.
- Flag missing acceptance criteria or missing test evidence that block QA.
- Estimate manual QA session effort.
- **Smoke check lookup**: Search `production/qa/smoke-*.md` and read the most recently modified report.
  - If present, adopt its verdict (`PASS` | `PASS WITH WARNINGS` | `FAIL` | `NOT ASSESSED`) directly without re-interviewing.
  - If absent, recommend running `ags-qa smoke-check sprint` and record smoke status as `UNKNOWN (no report found)` (allows planning to continue with caution, NOT clean `APPROVED`).
- **Hard stop on smoke FAIL**: If smoke check is `FAIL`, list failures prominently and stop — fix failures, re-run `ags-qa smoke-check`, then re-run `ags-team qa`.
- Present strategy table (`Story | Type | Automated Required | Manual Required | Blocker?`) + `Smoke Check` line and capture user decision:
  - Proceed to test plan / Adjust story types / Skip blocked stories / Cancel to resolve blockers.

### Phase 3: Test Plan Generation

Compile the test plan using `.ags/templates/test-plan.md`:
- **Scope**, **Story Classification Table**, **Automated Test Requirements** (expected paths under `tests/`), **Manual QA Scope**, **Out of Scope**.
- **Entry Criteria**: always include (1) smoke check `PASS` or `PASS WITH WARNINGS` report at `production/qa/smoke-*.md`, (2) stable build without launch crashes, (3) all Must Have stories marked in-progress or done in `production/sprint-status.yaml`.
- **Exit Criteria**: all in-scope stories `PASS` or `FAIL` with formal bug reports filed.
- Request user confirmation before writing `production/qa/qa-plan-[sprint]-[date].md`.

### Phase 4: Test Case Writing (`test-engineer`)

Runs only if Phase 2 smoke status was `PASS`, `PASS WITH WARNINGS`, or `UNKNOWN`. For each manual-QA story (`Visual/Feel`, `UI`, `Integration` without automated tests), spawn `test-engineer` in parallel batches writing directly to concrete paths:
- **Explicit return path**: `production/qa/test-cases/[story-slug]-cases.md` (one file per story; never leave destination unspecified across parallel spawns).
- Each test case includes: **Preconditions**, numbered **Steps**, **Expected Result**, blank **Actual Result**, blank **Pass/Fail**.
- Present grouped test cases (batches of 3-4 stories) for user review before execution (`Approved` / `Revise` / `Skip manual QA`).

### Phase 5: Manual QA Execution

Walk through approved manual stories in batches of 3-4, recording per-story outcome:
- `PASS` — all acceptance criteria verified
- `PASS WITH NOTES` — minor issues found (capture notes)
- `FAIL` — acceptance criteria unmet; collect failure details and delegate to `test-engineer` to write `production/qa/bugs/BUG-[NNN]-[short-slug].md` (increment `NNN` sequentially).
- `BLOCKED` — cannot test yet (record reason).

**Visual/Feel & UI Evidence Requirement**:
- After any `PASS` or `PASS WITH NOTES` on a `Visual/Feel` or `UI` story, write the evidence record to `production/qa/evidence/[story-slug]-evidence.md` using `.ags/templates/test-evidence.md` with the sign-off table intact and the captured screenshot saved in `production/qa/evidence/` and linked from the doc.
- Leave sign-off rows **unchecked** unless sign-off genuinely occurred during this session. (`ags-verify` and `ags-gate` gate on `production/qa/evidence/`.)

Summarize counts: `PASS`, `PASS WITH NOTES`, `FAIL` (with `BUG-NNN` IDs), `BLOCKED`.

### Phase 6: QA Sign-Off Report (`qa-lead`)

Delegate to `qa-lead` to compile the sign-off report covering test coverage summary, bugs found, verdict, conditions, and next steps.

**Mandatory Precondition (checked first)**:
- Every story in scope must have executed evidence (an automated test run or a walked manual test case).
- If ANY in-scope story is `BLOCKED`, unexecuted, missing test cases, or lacks evidence (or if smoke check was `FAIL`/`UNKNOWN` with unverified risk), the verdict MUST be **`NOT ASSESSED — NO EVIDENCE`** — do NOT evaluate the passing rules below (zero executed tests must never vacuously satisfy "no S1/S2 bugs open").

**Verdict evaluation (only when precondition holds)**:
- **NOT ASSESSED — NO EVIDENCE**: Missing execution evidence for one or more stories (list exact stories and missing evidence). Do not advance build.
- **NOT APPROVED**: Any open S1/S2 bugs, or story `FAIL` without an accepted workaround.
- **APPROVED WITH CONDITIONS**: S3/S4 bugs or `PASS WITH NOTES` documented; zero S1/S2 bugs.
- **APPROVED**: All stories `PASS` or `PASS WITH NOTES` and zero open S1/S2 bugs.

Request user confirmation before writing `production/qa/qa-signoff-[sprint]-[date].md`.

### Session State Checkpoint

After writing the sign-off report (or reaching `BLOCKED`), append one summary comment to `production/session-state/active.md`:

```markdown
<!-- QA RUN: [date] | Sprint: [sprint identifier or "ad-hoc"] | Verdict: [NOT ASSESSED/APPROVED/APPROVED WITH CONDITIONS/NOT APPROVED] | Report: production/qa/qa-signoff-[sprint]-[date].md -->
```

## Next Steps

- `NOT ASSESSED`: Produce missing automated tests, manual walkthrough evidence, or `ags-qa smoke-check`, then re-run `ags-team qa`.
- `APPROVED` / `APPROVED WITH CONDITIONS`: Proceed to `ags-gate` (or resolve S3/S4 conditions before release).
- `NOT APPROVED`: Fix S1/S2 bugs via `ags-dev` / `ags-bugs` and re-run QA.
