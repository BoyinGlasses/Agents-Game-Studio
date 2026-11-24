---
name: ags-release
description: "Use when preparing release or launch checklists, generating internal/player changelogs or patch notes, scoping a day-one launch patch, or executing an emergency S1/S2 hotfix. Do NOT use when orchestrating the full multi-team release pipeline -> ags-team, triaging normal S3/S4 bugs -> ags-bugs, or issuing formal phase-gate verdicts -> ags-gate."
---

# Release Operations

Unified release execution and documentation skill covering pre-release verification, launch readiness, changelogs, player patch notes, day-one launch patches, and emergency S1/S2 hotfixes.

## Contract
- **Inputs**: Sub-mode (`release-checklist` | `launch-checklist` | `changelog` | `patch-notes` | `day-one-patch` | `hotfix`), target version/platform/bug ID, `project.yaml`, `production/` records, and git history.
- **Roles**: `producer`, `technical-director`, `qa-lead`, `code-reviewer`, `gameplay-coder`, `test-engineer`
- **Outputs**: Checklists/records under `production/releases/` or `production/hotfixes/`, `docs/CHANGELOG.md`, `docs/patch-notes/[version].md`, and explicit gate/readiness verdict.
- **Verification**: Run `python .ags/cli.py verify` and `python .ags/cli.py check artifacts` after code or release document changes; verify backports across both release and development branches on hotfixes.
- **Next Skill**: `ags-gate`, `ags-team`, `ags-qa`, `ags-bugs`, or `ags-plan` per sub-mode outcome.

## Preflight

Run config resolution once before Phase 1:

```bash
python .ags/cli.py preflight ags-release
```

Inspect `project.stage`, `modes.rigor`, `modes.automation`, `platform.cert_tier` (`none` | `itch` | `steam` | `console` | unset), and `engine.name`. Treat `null` or `""` as unset — never conflate unset `platform.cert_tier` with `none`.

## Phases

### Phase 0: Sub-Mode Dispatch & Safety Guards

1. Parse the sub-mode from the request. If absent or ambiguous, ask which sub-mode to run and stop.
   - **Explicit-invocation guard**: Do not auto-trigger `release-checklist`, `launch-checklist`, or `hotfix` opportunistically without explicit user selection.
   - **Always-collaborative guard**: `day-one-patch` and `hotfix` always prompt the user for confirmation at every scope, write, branch, and deployment gate regardless of `modes.automation`.
2. Read the matching reference playbook completely before executing:

| Sub-mode | Playbook Reference | Primary Outputs |
|---|---|---|
| `release-checklist` | `references/release-checklist.md` | `production/releases/release-checklist-[version].md` |
| `launch-checklist` | `references/launch-checklist.md` | `production/releases/launch-checklist-[date].md` |
| `changelog` | `references/changelog.md` | `docs/CHANGELOG.md` |
| `patch-notes` | `references/patch-notes.md` | `docs/patch-notes/[version].md`, archive copy |
| `day-one-patch` | `references/day-one-patch.md` | `production/releases/rollback-plan-[version].md`, `day-one-patch-[version].md` |
| `hotfix` | `references/hotfix.md` | `production/hotfixes/hotfix-[date]-[slug].md`, git hotfix branch |

### Phase 1-N: Execute Selected Sub-Mode

Follow the loaded reference playbook step-by-step, enforcing these shared cross-mode invariants:
- **Codebase scan denominator discipline (`release-checklist`, `launch-checklist`)**: Resolve code root from `engine.name` (`Godot` -> `src/`, `Unity` -> `Assets/`, `Unreal` -> `Source/<Module>/`, or unambiguous single directory). Always report `scanned [N] source files: [M] hits`. If code root is unresolved or empty, or `assets/` or CI test logs are absent, report `NOT ASSESSED — <missing input>` and mark affected checklist items `- [?]` with the legend `[?] = not assessed — the input to this check was absent`. Never report a bare `0` or `[ ]`/`[x]` over missing inputs.
- **Certification tier vs device axis (`release-checklist`, `launch-checklist`)**: Hardware target (`pc` | `console` | `mobile` | `all`) selects hardware blocks; `platform.cert_tier` (`none` | `itch` | `steam` | `console`) selects certification blocks. Emit ONLY the matching `cert_tier` block (at `none`, emit one explicit omission line). If `platform.cert_tier` is unset, ask the user; if undeterminable, emit `NOT ASSESSED — cert tier unknown`.
- **Git provenance verification (`changelog`, `patch-notes`)**: Sample recent commits (`git log --oneline -20`/`-30`), classify every commit as `Game` vs `Framework / maintenance` vs `Unclear` (treat `Unclear` as Framework), corroborate Game commits against `design/` and code root, and report `used [X] of [Y] commits`. If zero commits belong to this game, hard-stop (`BLOCKED`) rather than emitting framework maintenance notes as game changes.
- **Role lens mapping**: Use `.ags/roles/release-manager.md` (via `producer`), `.ags/roles/community-manager.md` (via `producer`), and `.ags/roles/lead-programmer.md` (via `code-reviewer`/`gameplay-coder`), alongside `qa-lead`, `test-engineer`, `producer`, and `technical-director`.
- **Irreversible action gate**: Merging hotfix branches, tagging, or deploying production builds always requires explicit user confirmation regardless of `modes.automation`.

## Gate & Verdict

Rank final outcomes strictly from highest severity to lowest:

| Verdict | Rank | Meaning & Required Disclosure |
|---|---|---|
| **BLOCKED / FAIL / NO-GO / NOT READY** | 1 (Highest) | Missing changelog data, zero game commits, failed/missing release gate on day-one patch, failed QA gate, unapproved rollback, or open S1/S2 blocker. |
| **CONCERNS / CONDITIONAL / REDIRECTED** | 2 | Non-blocking warnings, documented S3/S4 exceptions, or S3+ hotfix request redirected to `ags-bugs`. |
| **NOT ASSESSED** | 3 | Missing source/assets/CI logs (`[?]`), unset `platform.cert_tier`, missing `production/gate-checks/` record, unexecuted QA smoke/regression suite, or unverified hotfix backport. Never treat as PASS/READY. |
| **PASS / READY / GO / COMPLETE** | 4 (Lowest) | All required checks executed with verified denominators, required rollbacks/approvals/backports confirmed, and explicit user sign-off recorded. |
