---
name: ags-team
description: "Use when orchestrating multi-discipline game development teams across audio, combat, level, live-ops, narrative, polish, qa, release, or ui domains. Do NOT use when executing single-story implementation -> ags-dev, verifying a single story or PR -> ags-verify, running standalone release checklists/notes/hotfixes -> ags-release, or rendering formal stage gate verdicts -> ags-gate."
---

# Team Orchestrator

Routes multi-discipline feature, content, QA, polish, UI, and release pipelines across studio roles while preventing silent team collapses or skipped checks.

## Contract
- **Inputs**: Domain sub-mode (`audio`, `combat`, `level`, `live-ops`, `narrative`, `polish`, `qa`, `release`, `ui`), target feature/area/sprint/version, `project.yaml`, and relevant `design/` or `production/` artifacts.
- **Roles**: `producer`, `creative-director`, `technical-director`, `qa-lead`, `code-reviewer`, `game-designer`, `art-ux-director`, `gameplay-coder`, `tech-artist`, `test-engineer`, `godot-specialist`, `unity-specialist`, `unreal-specialist`
- **Outputs**: Domain artifacts under `design/`, `docs/architecture/`, `production/`, or `docs/patch-notes/`, plus active-roster disclosure and final pipeline verdict.
- **Verification**: Every phase naming a concrete output file checks disk existence before advancing; run `python .ags/cli.py verify` and `python .ags/cli.py check artifacts` after code or deliverable writes.
- **Next Skill**: `ags-design-review`, `ags-dev`, `ags-verify`, `ags-gate`, `ags-localize`, or `ags-release` per domain playbook.

## Preflight

Run config resolution once before Phase 1:

```bash
python .ags/cli.py preflight ags-team
```

Inspect `team.size` (`individual` | `small` | `studio`), `modes.review_mode` (`full` | `lean` | `solo`), `modes.automation` (`collaborative` | `guided` | `autonomous`), `engine.name`, `specialists.*`, and `project.stage`. Treat `null` or `""` values (including `specialists.ui: null`) as unset — never spawn `"null"` as a role. Inline `--review <mode>` overrides `modes.review_mode` for the current run.

## Phases

### Phase 0: Sub-Mode Routing & Active-Set Announcement

1. Parse the domain sub-mode and target argument. If the domain or required target argument is missing (except `qa` inferring active sprint or `release` inferring target version from `production/session-state/active.md` and `production/milestones/`), output usage guidance for the 9 sub-modes and stop without spawning roles.
2. Read the matching domain playbook completely before orchestrating:

| Sub-mode | Playbook Reference | Core Lead Anchor |
|---|---|---|
| `audio` | `references/team-audio.md` | `tech-artist` |
| `combat` | `references/team-combat.md` | `gameplay-coder` |
| `level` | `references/team-level.md` | `game-designer` |
| `live-ops` | `references/team-live-ops.md` | `producer` |
| `narrative` | `references/team-narrative.md` | `game-designer` |
| `polish` | `references/team-polish.md` | `test-engineer` |
| `qa` | `references/team-qa.md` | `test-engineer` / `qa-lead` |
| `release` | `references/team-release.md` | `producer` |
| `ui` | `references/team-ui.md` | `gameplay-coder` / `art-ux-director` |

3. **Active-Set Announcement (mandatory before Phase 1)**: Compute the active roster from the playbook's `team.size` matrix (`individual` | `small` | `studio`) and `modes.review_mode` (`full` | `lean` | `solo`), plus `engine.name` availability. Emit this block verbatim in the run output before spawning any worker:

```markdown
Active set (team.size: <resolved>, review_mode: <resolved>): <roles/lenses spawned this run>.
Not spawned this run (skipped by team.size): <every unspawned role/lens named in the playbook> — routed through <nearest active core role>. Raise team.size or modes.rigor to widen.
Skipped checks / engine status: <list missing engine specialist or absent input as NOT ASSESSED, or "none">.
```

4. **Role-to-Core & Lens Mapping**: Dispatch core and engine roles from `.ags/roles/<role>.md`. When a playbook invokes a domain lens (`.ags/roles/<lens>.md`), route it according to `team.size` using its core parent:
   - `game-designer` lenses: `systems-designer`, `economy-designer`, `narrative-director`, `level-designer`, `world-builder`, `writer`
   - `art-ux-director` lenses: `art-director`, `ux-designer`, `accessibility-specialist`
   - `tech-artist` lenses: `audio-director`, `sound-designer`
   - `gameplay-coder` lenses: `ai-programmer`, `network-programmer`, `engine-programmer`, `tools-programmer`, `ui-programmer`, `analytics-engineer`
   - `code-reviewer` lenses: `lead-programmer`, `security-engineer`
   - `test-engineer` lenses: `performance-analyst`
   - `producer` lenses: `live-ops-designer`, `community-manager`, `localization-lead`, `release-manager`, `devops-engineer`

### Phase 1-N: Execute Domain Playbook

Follow the phases, parallel steps, decision gates, and exact output paths defined in the loaded `references/team-<domain>.md` playbook.

**Shared Orchestration Rules (apply to every playbook):**
- **Distilled briefing**: Read shared inputs once and pass only the distilled lines each worker needs; pass file paths only for unread role-specific files.
- **Return contract**: Every delegated worker writes its full output to the concrete path named in the playbook and returns `(1) path written`, `(2) <=5 decision bullets`, and `(3) one-line BLOCKED/CONCERNS items`.
- **Bounded write scope**: Delegated workers may write directly only to newly named artifacts under `production/`, `docs/`, or `tests/` within a phase gated by a user decision point. Orchestrators compile and request explicit user confirmation before writing files under `design/` (e.g., `design/audio/`, `design/levels/`, `design/live-ops/`). Outward or irreversible actions (tags, deploys, storefront updates) always require explicit user confirmation regardless of `modes.automation`.
- **Review-mode gate depth**: At `solo`, skip director/lead gates outside explicit user approvals. At `lean`, run `PHASE-GATE` checks (`cd-phase-gate.md`, `td-phase-gate.md`, `pr-phase-gate.md`, `ad-phase-gate.md` under `.ags/gates/`) and skip per-step director gates. At `full`, run all gates. A "phase gate" applies only to phases that end in a user decision point before advancing.
- **Engine specialist validation**: Derive `<engine>-specialist` from `engine.name` in `project.yaml` (or `specialists.ui` for UI). If `engine.name` is unset or `null`, skip the spawn and record `Engine validation: NOT ASSESSED — no engine configured (engine.name unset in project.yaml)`.
- **Trigger 0 & Error Recovery**: Before advancing past any phase with a named output path, verify that file exists on disk; an absent artifact is a failed phase regardless of response prose—resume the worker citing the unmet contract. If any worker reports `BLOCKED` or errors, surface it immediately, halt dependent phases, offer retry/narrow/stop options, and emit a partial report.

## Gate & Verdict

Rank final outcomes strictly from highest severity to lowest:

| Verdict | Rank | Meaning & Required Disclosure |
|---|---|---|
| **BLOCKED / FAIL / NOT APPROVED** | 1 (Highest) | Unresolved dependency, failed smoke check, ethics violation, NO-GO call, or S1/S2 blocker halted the pipeline. Partial report emitted. |
| **CONCERNS / APPROVED WITH CONDITIONS** | 2 | Pipeline completed with non-blocking warnings, S3/S4 bugs, or accepted deviations documented for follow-up. |
| **NOT ASSESSED** | 3 | One or more required inputs or checks could not be evaluated (missing engine config, absent `design/accessibility-requirements.md`, absent `design/live-ops/ethics-policy.md`, missing `production/qa/smoke-*.md`, or unexecuted story evidence). Never downgrade to PASS/COMPLETE. |
| **COMPLETE / APPROVED / PASS** | 4 (Lowest) | All in-scope phases executed, disk artifacts verified, active/skipped roster disclosed, and zero unassessed mandatory preconditions remain. |
