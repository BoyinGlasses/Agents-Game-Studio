# Sub-Mode: Day-One Patch (`ags-release day-one-patch`)

Release-critical mini-sprint for safe P1/S1-S2 fixes after gold master lock — enforces premise verification, mandatory pre-fix rollback planning, lightweight QA gating, and `NOT ASSESSED` rejection.

**Automation override**: Always operates in `collaborative` confirmation mode regardless of `modes.automation` (`autonomous` / `guided` do not waive user approvals here).

## Scope Rules

- Only P1 / S1-S2 (or platform cert-mandated) bugs that are **safe** to fix quickly.
- Zero new features; zero refactoring; minimum viable change only.
- Any fix requiring `> 4 hours` belongs in patch `1.1`, not day-one.
- Total patch effort `> 1 working day` triggers an explicit scope-risk warning requiring user confirmation.

## Phase 1: Verify Gold Master Premise & Context

Read:
- `project.stage` in `project.yaml` (fallback `production/stage.txt`) — warn if not `Release` or `Polish`.
- Most recent file in `production/gate-checks/` — verify release-gate verdict.
- `production/qa/bugs/*.md` (`Status: Open` or `Fixed — Pending Verification`).
- Latest `production/sprints/` and `production/security/security-audit-*.md` if present.

**Premise verification (do NOT infer from `project.stage: Release` alone):**
- **No file in `production/gate-checks/`** (or none recording a release gate): report `Release gate: NOT ASSESSED — no gate-check record found`, state plainly that reduced QA scope rests on an unverified gate, and ask whether to run `ags-gate` first or run a full QA pass (`ags-team qa`) instead.
- **Most recent release gate is `FAIL`, `CONCERNS`, or `NOT ASSESSED`**: name the verdict and stop (`BLOCKED`) — resolve the release gate rather than masking it under a day-one patch.

## Phase 2: Scope & Approve Patch

1. Evaluate each open bug:
   - `S1`/`S2`, `P1`, `< 4 hours`, data/config-only, or cert feedback -> **Include** (if no architecture change or risky new code paths).
   - Architecture change, new code paths, or non-trivial `S3`/`S4` -> **Defer to 1.1**.
2. Present included and deferred bug tables to the user:
   - `[A]` Approve scope / `[B]` Adjust / `[C]` No day-one patch needed (proceed to `ags-release launch-checklist` and stop).
3. Sum estimated hours; if `> 1 day`, warn and confirm scope reduction or explicit risk acceptance.

## Phase 3: Non-Negotiable Rollback Plan

Before writing any code fix, delegate to `.ags/roles/release-manager.md` (`producer` core role) to draft a rollback plan covering:
- Reversion steps back to gold master per platform
- Platform rollback constraints (e.g., consoles unable to roll back certified builds)
- Named rollback trigger owner
- Required player communication on rollback

Confirm with the user and write `production/releases/rollback-plan-[version].md` **before** Phase 4 begins.

## Phase 4: Implement & Verify Minimal Fixes

For each approved fix:
- **Code fix**: Delegate minimal fix + targeted tests to `.ags/roles/lead-programmer.md` / `gameplay-coder`, then delegate reproduction verification to `test-engineer` (`.ags/roles/test-engineer.md`).
- **Config/data-only fix**: Apply directly, confirm value changed, and re-run relevant smoke tests.

## Phase 5: Patch QA Gate

Delegate to `qa-lead` (`.ags/roles/qa-lead.md`) with changed files, fixed bug statuses, and affected systems to choose:
- **Targeted smoke check**: `ags-qa smoke-check [affected-systems]`
- **Broader regression**: targeted unit/integration tests under `tests/unit/` and `tests/integration/` (plus `python .ags/cli.py verify`)

**Strict `NOT ASSESSED` rule**:
- QA verdict MUST be `PASS` or `PASS WITH WARNINGS`.
- If `FAIL`, defer the failing fix to patch `1.1`.
- If **`NOT ASSESSED`** (no build, no runner, or unconfirmed test execution), **treat as unmet (NOT a pass and NOT `PASS WITH WARNINGS`)**: obtain a real run result or defer the fix to `1.1`.

## Phase 6: Write Patch Record & Next Steps

Compile `production/releases/day-one-patch-[version].md` (Bugs Fixed table, Deferred to 1.1 table, QA Sign-Off with explicit `Not assessed` field, Rollback Plan link & trigger condition, Approvals for `lead-programmer`, `qa-lead`, `producer`, `release-manager`, and Player-Facing Notes draft). Request user confirmation before writing.

**S1 Escalation**: If any `S1` bugs remain unpatched, warn and document them directly in the rollback trigger conditions.

**Next Skills**: `ags-release patch-notes` (mandatory player comms), `ags-bugs` (`verify` / `close` post-deploy), `ags-plan retrospective` (48-72h post-launch review).
