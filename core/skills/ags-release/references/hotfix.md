# Sub-Mode: Hotfix (`ags-release hotfix`)

Explicit-invocation-only emergency fix workflow bypassing normal sprint cadence for S1/S2 incidents, enforcing upfront severity gating, rollback readiness, parallel sign-offs, QA re-entry, unconditional merge/deploy approval, and dual-branch backport verification.

**Automation override**: Always operates in `collaborative` confirmation mode regardless of `modes.automation`.

## Phase 1: Assess Severity

Evaluate the reported defect:
- **S1 (Critical)**: Game unplayable, data loss, or security vulnerability.
- **S2 (Major)**: Significant feature broken with a workaround.
- **S3 or lower**: Normal bug workflow applies.

Confirm severity with the user (`[A] S1` / `[B] S2` / `[C] S3 or lower`). If `[C]`, stop immediately with Verdict **`REDIRECTED`** to `ags-bugs`.

## Phase 2: Create Hotfix Record

Draft hotfix record (Date, Severity, Reporter, `Status: IN PROGRESS`, Problem, Root Cause, Fix, Testing, Approvals for `lead-programmer` / `test-engineer` / `producer`, Rollback Plan; cross-reference `.ags/templates/incident-response.md` when needed). Request user confirmation before writing `production/hotfixes/hotfix-[date]-[short-name].md`.

## Phase 3: Create Hotfix Branch

Verify git repo (`git rev-parse --is-inside-work-tree`):
- If non-git, note manual branch creation required and proceed to Phase 4.
- If git repo, confirm branch name and base ref (`[A] Create hotfix/[short-name] from [base-ref]` / `[B] Specify different base ref` / `[C] Skip`) before running `git checkout -b`.

## Phase 4: Investigate, Propose & Implement

1. Identify root cause and propose the **minimum viable fix** (files touched, exact change, what stays untouched — zero refactoring or feature additions). Escalate to `technical-director` if fix effort exceeds 4 hours.
2. **Pre-edit approval**: Present root cause and proposed fix and obtain explicit user confirmation **before** modifying source files.
3. Implement approved minimal fix, run targeted tests + `python .ags/cli.py verify`, check adjacent systems for regressions, and update the Phase 2 hotfix record.

## Phase 5: Parallel Approvals & QA Re-Entry Gate

1. **Parallel sign-offs** (all three must return `APPROVE`; any `CONCERNS`/`REJECT` halts deployment):
   - `.ags/roles/lead-programmer.md` (`code-reviewer` lens): Fix correctness and side effects
   - `.ags/roles/test-engineer.md`: Targeted regression tests
   - `.ags/roles/producer.md`: Deployment timing and player communication plan
2. **QA Re-Entry Gate (`qa-lead`)**: Provide hotfix summary, Phase 5 test results, and all caller systems discovered via code search. `qa-lead` decides required gate:
   - `ags-qa smoke-check` (`PASS`)
   - Scoped `ags-team qa [affected-system]` (`APPROVED` / `APPROVED WITH CONDITIONS`)
   - Full `ags-team qa sprint` (for S1 fixes touching core systems)
   - **`NOT ASSESSED` rule**: If QA returns `NOT ASSESSED` (tests never executed or no evidence), treat the gate as **unmet** — either run the suite to get real evidence or escalate explicitly to `producer` as a documented unverified emergency deployment decision.

## Phase 6: Unconditional Deploy Gate & Backport Verification

1. **Unconditional confirmation**: Before any merge, tag, or deploy, prompt the user regardless of `modes.automation`:
   - `[A] Yes — merge and deploy`
   - `[B] Merge to development only — hold release`
   - `[C] Stop here`
2. **Mandatory dual-branch backport verification**: After merging, check git history/diff explicitly to verify the fix commit/patch is present on **both** the release branch AND the development branch. Report either `Backport: verified present on release AND development` or `Backport: NOT VERIFIED — [missing branch / unverified check]` (never claim verified backport without checking both branches).
3. Update associated bug file if present (`Fixed in`, `Fixed date`, `Status: Fixed — Pending Verification`) and output deployment summary (`Severity`, `Root cause`, `Fix`, `QA gate`, `Approvals`, `Backport`, `Rollback plan`).

## Phase 7: Post-Deploy Verification & Post-Mortem

- Run `ags-bugs` (`verify` then `close`) after deploy; if defect persists, re-open immediately, assess rollback, and escalate.
- Schedule a post-incident review within 48 hours via `ags-plan retrospective` (using `.ags/templates/post-mortem.md` / `.ags/templates/incident-response.md`).
- Offer user next step: `ags-qa smoke-check`, `ags-release patch-notes`, or stop.
