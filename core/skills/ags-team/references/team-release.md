# Team Playbook: Release (`ags-team release`)

Orchestrates release planning, release candidate cut, parallel quality/security/netcode/l10n/perf/analytics gates, Go/No-Go decision, deployment, and post-release monitoring.

## Argument & Role Mapping

- **Version resolution**:
  1. If no `[version]` argument is supplied, inspect `production/session-state/active.md` and the latest file in `production/milestones/`.
  2. If a version is discovered, state it and confirm with the user (`Releasing [version]. Is this correct?`).
  3. If no version is discoverable, ask the user for the version (e.g., `v1.0.0`) before proceeding — never invent a hardcoded default.
- **Active-set (`team.size`)**:
  - **`individual`** (default): `release-manager` (via `producer`) only; other roles routed through `producer`.
  - **`small`**: + `producer` + `devops-engineer` + `qa-lead`.
  - **`studio`**: + `security-engineer` + `analytics-engineer` + `localization-lead` (+ `network-programmer` when multiplayer).
- **Role map**:
  - `release-manager` lens -> `producer` (`.ags/roles/release-manager.md`)
  - `producer` -> `.ags/roles/producer.md`
  - `qa-lead` -> `.ags/roles/qa-lead.md`
  - `devops-engineer` lens -> `producer` (`.ags/roles/devops-engineer.md`)
  - `security-engineer` lens -> `code-reviewer` (`.ags/roles/security-engineer.md`)
  - `network-programmer` lens -> `gameplay-coder` (`.ags/roles/network-programmer.md`)
  - `localization-lead` lens -> `producer` (`.ags/roles/localization-lead.md`)
  - `performance-analyst` lens -> `test-engineer` (`.ags/roles/performance-analyst.md`)
  - `analytics-engineer` lens -> `gameplay-coder` (`.ags/roles/analytics-engineer.md`)
  - `community-manager` lens -> `producer` (`.ags/roles/community-manager.md`)

Announce the active roster, skipped roles, and feature-conditional exclusions (e.g., non-multiplayer projects skipping `network-programmer` / `security-engineer`) before Phase 1.

## Concrete Output Paths

Each phase writes its own file so parallel Phases 3 and 4 never race on a shared file:

| Phase / Role | Writes To | Shared By |
|---|---|---|
| 1 `producer` | `production/releases/release-plan-[version].md` | `ags-team release` |
| 2 `release-manager` | `production/releases/release-checklist-[version].md` | `ags-release release-checklist` |
| 3 `qa-lead` | `production/releases/qa-gate-[version].md` | `ags-team release` |
| 4 specialists | `production/releases/signoff-[version].md` | `ags-team release` |
| 5 `producer` | `production/releases/go-no-go-[version].md` | `ags-team release` |
| 6 `community-manager` | `docs/patch-notes/[version].md` | `ags-release patch-notes` |
| 7 `release-manager` | `production/releases/release-report-[version].md` | `ags-team release` |

Note: Sub-skills (`ags-release`) follow normal confirmation rules rather than worker auto-writes; outward actions (tags, pushes, builds, storefront updates) always require explicit user confirmation.

## Pipeline

### Phase 1: Release Planning (`producer`)

Confirm all milestone acceptance criteria are met, list any deferred scope items, set target release date, and issue release authorization (`production/releases/release-plan-[version].md`).

### Phase 2: Release Candidate (`release-manager`)

Cut the release branch from the agreed commit, bump version identifiers across project files, execute `ags-release release-checklist` (`production/releases/release-checklist-[version].md`), and freeze the branch (bug fixes only, zero feature changes).

### Phase 3: Quality Gate (Parallel)

Delegate concurrently when active:
- **`qa-lead`**: Execute full regression suite (`ags-qa regression-suite`), test all critical paths, verify zero open S1/S2 bugs, write `production/releases/qa-gate-[version].md`.
- **`devops-engineer`**: Build reproducible release artifacts for all target platforms and run CI tests.
- **`security-engineer`** *(if game has online features, multiplayer, or player data)*: Audit auth, anti-cheat, data privacy compliance (`ags-diagnose security-audit`).
- **`network-programmer`** *(if game has multiplayer)*: Sign off on netcode stability, lag compensation, reconnect handling, and bandwidth under load.

### Phase 4: Localization, Performance, and Analytics (can run parallel with Phase 3)

- **`localization-lead`**: Verify all shipping locales passed `ags-localize qa` (`PASS` or `PASS WITH CONDITIONS`).
- **`performance-analyst`**: Verify frame/memory/load benchmarks against targets (`ags-diagnose perf-profile`).
- **`analytics-engineer`**: Confirm telemetry events fire on the release build and onboarding/progression/monetization funnels reach live dashboards.
- Write combined results to `production/releases/signoff-[version].md`. If any check cannot run due to missing build, runner, or locale data, record `NOT ASSESSED` explicitly with reason.

### Phase 5: Go / No-Go (`producer`)

Collect sign-offs from `qa-lead`, `release-manager`, `devops-engineer`, `security-engineer` (if active), `network-programmer` (if active), and `technical-director`. Evaluate open defects and issue `GO` or `NO-GO` in `production/releases/go-no-go-[version].md`.

**If `producer` declares `NO-GO`:**
1. Surface immediately: `PRODUCER: NO-GO — [rationale]`.
2. Prompt the user with options:
   - Fix blocker and re-run affected phase.
   - Defer release to a later date.
   - Override `NO-GO` with documented written rationale (user provides plain-text justification; embed `Override Justification: [user text]` into `go-no-go-[version].md` before Phase 6).
3. Unless overridden with written justification, **skip Phase 6 entirely** (no tag, staging deploy, prod deploy, or `community-manager` launch copy), emit a partial report summarizing Phases 1-5 and skipped Phase 6, and stop with Verdict: **BLOCKED**.

### Phase 6: Deployment (if `GO`)

**Unconditional confirmation gate**: Production deployment is irreversible and ALWAYS requires explicit user confirmation regardless of `modes.automation` (including `autonomous`):
- Options: `[A] Yes — tag and deploy` / `[B] Staging only — hold production` / `[C] Stop here`.

After approval:
- **`release-manager` + `devops-engineer`**: Tag release in git, generate changelog via `ags-release changelog`, deploy to staging for final smoke check (`ags-qa smoke-check`), deploy to production only if `[A]` selected. Schedule 48-hour live dashboard monitoring and a 48-hour post-release `ags-plan retrospective`.
- **`community-manager`** (parallel): Finalize player-facing notes via `ags-release patch-notes [version]` (`docs/patch-notes/[version].md`), prepare store/social/community launch announcements, and draft known-issues communication if any S3+ issues shipped.

### Phase 7: Post-Release

- **`release-manager`**: Write `production/releases/release-report-[version].md` (what shipped, deferred items, metrics).
- **`producer`**: Update milestone tracking and notify stakeholders.
- **`qa-lead`**: Monitor incoming bug reports for regressions.
- **`community-manager`**: Publish approved player comms and monitor sentiment.
- **`analytics-engineer`**: Verify live dashboards and alert on missing critical events.
- Update `project.stage` in `project.yaml` to `Release` (and mirror `Release` to `production/stage.txt` if present). `Release` is the terminal `project.stage` enum; record post-launch status in the release report.

## Verdicts

- **COMPLETE**: Release verified, approved, tagged, and deployed; release report written.
- **NOT ASSESSED**: One or more Phase 3/4 checks lacked build/telemetry/QA inputs and was explicitly surfaced (must be resolved or explicitly accepted before GO).
- **BLOCKED**: Producer declared `NO-GO` without override, or critical gate failed.
