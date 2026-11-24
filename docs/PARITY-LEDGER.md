# AGS v2 Capability Parity Ledger

Complete 1-to-1 traceability matrix verifying **zero capability loss** from CCGS v1 / Codex Port (`skills/ccgs-*` and `assets/template/`) to **Agents Game Studio v2 (`core/`, `ags/`, `tests/eval/`)**.

---

## Summary Counts

| Asset Class | CCGS v1 / Codex Port | AGS v2 Location | Verified Parity |
|---|---|---|---|
| **Skills** | 75 (`skills/ccgs-*`) | 21 canonical `ags-*` skills + sub-mode `references/*.md` (`core/skills/`) | **75 / 75 (100%)** |
| **Agents / Roles** | 49 (`assets/template/.claude/agents/*.md`) | 52 files: 12 `core/` (9 direct + `scout`, `code-reviewer`, `art-ux-director`) + 15 `engines/` + 25 `lenses/` (`core/agents/`) | **49 / 49 legacy roles + 3 canonical roles (100%)** |
| **Director Gates** | 28 (`assets/template/.claude/docs/director-gates/*.md`) | 28 gate specs + `INDEX.md` (`core/gates/`) | **28 / 28 (100%)** |
| **Deterministic Scripts** | 8 (`assets/template/.claude/scripts/*.sh`) | 8 ported checks + engine static `verify` (`ags/checks.py`) | **8 / 8 + engine verify (100%)** |
| **Path Rules & Routing** | 13 rules + `CLAUDE.md` / `AGENTS.md` | 13 Game-Native rules + `<110`-line `AGENTS.md` (`core/rules/`) | **13 / 13 + unified router (100%)** |
| **Hooks & Bridge** | 14 `.claude/hooks/*.sh` + `.codex/hooks/bridge.py` | 5 unified cross-harness hooks (`ags/hooks.py`) + config (`ags/config.py`) | **100% functional parity across 4 harnesses** |
| **Templates** | 46 `.md` + `project.yaml` (`assets/template/.claude/docs/templates/`) | 46 `.md` (`core/templates/`, incl. `guidance/`) + `core/templates/project.yaml` | **46 / 46 + `project.yaml` (100%)** |
| **Engine Reference Docs** | 46 `.md` (`assets/template/docs/engine-reference/`) | 46 `.md` (`core/engine-reference/`: `README.md` + 12 Godot + 16 Unity + 17 Unreal) | **46 / 46 (100%)** |
| **Eval & Testing Suite** | `assets/template/CCGS Skill Testing Framework/` | `tests/eval/` (repo-only; excluded from `ags init`) + `tests/test_*.py` | **100% migrated + updated** |

---

## 1. Skills Parity Matrix (75 Original `ccgs-*` -> 21 `ags-*`)

| # | Original Skill (`skills/`) | AGS v2 Skill (`core/skills/`) | Preserved Sub-Mode / Reference Location |
|---|---|---|---|
| 1 | `ccgs-new-game` | `ags-new-game` | `core/skills/ags-new-game/SKILL.md`, `references/multi-harness-setup.md` |
| 2 | `ccgs-start` | `ags-start` | `core/skills/ags-start/SKILL.md`, `references/onboard-flow.md` |
| 3 | `ccgs-help` | `ags-start` | `core/skills/ags-start/references/help-flow.md` |
| 4 | `ccgs-project-stage-detect` | `ags-start` | `core/skills/ags-start/references/stage-detect.md` |
| 5 | `ccgs-onboard` | `ags-start` | `core/skills/ags-start/references/contributor-onboard.md` |
| 6 | `ccgs-settings` | `ags-settings` | `core/skills/ags-settings/SKILL.md`, `references/config-mode.md` |
| 7 | `ccgs-setup-engine` | `ags-settings` | `core/skills/ags-settings/references/engine-setup.md`, `references/godot-language-config.md` |
| 8 | `ccgs-adopt` | `ags-adopt` | `core/skills/ags-adopt/SKILL.md`, `references/brownfield-audit.md` |
| 9 | `ccgs-reverse-document` | `ags-adopt` | `core/skills/ags-adopt/references/reverse-document.md` |
| 10 | `ccgs-brainstorm` | `ags-ideate` | `core/skills/ags-ideate/SKILL.md`, `references/brainstorm.md` |
| 11 | `ccgs-prototype` | `ags-ideate` | `core/skills/ags-ideate/references/prototype.md` |
| 12 | `ccgs-vertical-slice` | `ags-ideate` | `core/skills/ags-ideate/references/vertical-slice.md` |
| 13 | `ccgs-map-systems` | `ags-gdd` | `core/skills/ags-gdd/SKILL.md`, `references/map-systems.md` |
| 14 | `ccgs-design-system` | `ags-gdd` | `core/skills/ags-gdd/references/design-system.md` |
| 15 | `ccgs-quick-design` | `ags-gdd` | `core/skills/ags-gdd/references/quick-design.md` |
| 16 | `ccgs-art-bible` | `ags-art-ux` | `core/skills/ags-art-ux/SKILL.md`, `references/art-bible.md` |
| 17 | `ccgs-asset-spec` | `ags-art-ux` | `core/skills/ags-art-ux/references/asset-spec.md` |
| 18 | `ccgs-asset-audit` | `ags-art-ux` | `core/skills/ags-art-ux/references/asset-audit.md` |
| 19 | `ccgs-ux-design` | `ags-art-ux` | `core/skills/ags-art-ux/references/ux-design.md`, `references/sections-{hud,patterns,ux-spec}.md` |
| 20 | `ccgs-ux-review` | `ags-art-ux` | `core/skills/ags-art-ux/references/ux-review.md` |
| 21 | `ccgs-design-review` | `ags-design-review` | `core/skills/ags-design-review/SKILL.md`, `references/design-review.md` |
| 22 | `ccgs-review-all-gdds` | `ags-design-review` | `core/skills/ags-design-review/references/review-all-gdds.md` |
| 23 | `ccgs-consistency-check` | `ags-design-review` | `core/skills/ags-design-review/references/consistency-check.md` |
| 24 | `ccgs-balance-check` | `ags-design-review` | `core/skills/ags-design-review/references/balance-check.md` |
| 25 | `ccgs-content-audit` | `ags-design-review` | `core/skills/ags-design-review/references/content-audit.md` |
| 26 | `ccgs-propagate-design-change` | `ags-design-review` | `core/skills/ags-design-review/references/propagate-design-change.md` |
| 27 | `ccgs-create-architecture` | `ags-architect` | `core/skills/ags-architect/SKILL.md`, `references/create-architecture.md` |
| 28 | `ccgs-architecture-decision` | `ags-architect` | `core/skills/ags-architect/references/architecture-decision.md` |
| 29 | `ccgs-create-control-manifest` | `ags-architect` | `core/skills/ags-architect/CONTRACT.md`, `references/create-control-manifest.md` |
| 30 | `ccgs-architecture-review` | `ags-arch-review` | `core/skills/ags-arch-review/SKILL.md`, `references/architecture-review.md` |
| 31 | `ccgs-tech-debt` | `ags-arch-review` | `core/skills/ags-arch-review/references/tech-debt.md` |
| 32 | `ccgs-scope-check` | `ags-arch-review` | `core/skills/ags-arch-review/references/scope-check.md` |
| 33 | `ccgs-create-epics` | `ags-plan` | `core/skills/ags-plan/SKILL.md`, `references/create-epics.md` |
| 34 | `ccgs-create-stories` | `ags-plan` | `core/skills/ags-plan/CONTRACT.md`, `references/create-stories.md` |
| 35 | `ccgs-estimate` | `ags-plan` | `core/skills/ags-plan/references/estimate.md` |
| 36 | `ccgs-sprint-plan` | `ags-plan` | `core/skills/ags-plan/references/sprint-plan.md` |
| 37 | `ccgs-sprint-status` | `ags-plan` | `core/skills/ags-plan/references/sprint-status.md` |
| 38 | `ccgs-milestone-review` | `ags-plan` | `core/skills/ags-plan/references/milestone-review.md` |
| 39 | `ccgs-retrospective` | `ags-plan` | `core/skills/ags-plan/references/retrospective.md` |
| 40 | `ccgs-story-readiness` | `ags-dev` | `core/skills/ags-dev/SKILL.md`, `references/story-readiness.md` |
| 41 | `ccgs-dev-story` | `ags-dev` | `core/skills/ags-dev/CONTRACT.md`, `references/dev-story.md`, `references/playtest-tuning-card.md` |
| 42 | `ccgs-code-review` | `ags-verify` | `core/skills/ags-verify/SKILL.md`, `references/code-review.md` |
| 43 | `ccgs-story-done` | `ags-verify` | `core/skills/ags-verify/CONTRACT.md`, `references/story-done.md` |
| 44 | `ccgs-test-evidence-review` | `ags-verify` | `core/skills/ags-verify/references/test-evidence-review.md` |
| 45 | `ccgs-test-setup` | `ags-qa` | `core/skills/ags-qa/SKILL.md`, `references/test-setup.md` |
| 46 | `ccgs-test-helpers` | `ags-qa` | `core/skills/ags-qa/references/test-helpers.md` |
| 47 | `ccgs-qa-plan` | `ags-qa` | `core/skills/ags-qa/references/qa-plan.md` |
| 48 | `ccgs-smoke-check` | `ags-qa` | `core/skills/ags-qa/references/smoke-check.md` |
| 49 | `ccgs-regression-suite` | `ags-qa` | `core/skills/ags-qa/references/regression-suite.md` |
| 50 | `ccgs-soak-test` | `ags-qa` | `core/skills/ags-qa/references/soak-test.md` |
| 51 | `ccgs-test-flakiness` | `ags-qa` | `core/skills/ags-qa/references/test-flakiness.md` |
| 52 | `ccgs-playtest-report` | `ags-qa` | `core/skills/ags-qa/references/playtest-report.md` |
| 53 | `ccgs-bug-report` | `ags-bugs` | `core/skills/ags-bugs/SKILL.md`, `references/bug-report.md` |
| 54 | `ccgs-bug-triage` | `ags-bugs` | `core/skills/ags-bugs/references/bug-triage.md` |
| 55 | `ccgs-perf-profile` | `ags-diagnose` | `core/skills/ags-diagnose/SKILL.md`, `references/perf-profile.md` |
| 56 | `ccgs-security-audit` | `ags-diagnose` | `core/skills/ags-diagnose/references/security-audit.md` |
| 57 | `ccgs-team-audio` | `ags-team` | `core/skills/ags-team/references/team-audio.md` |
| 58 | `ccgs-team-combat` | `ags-team` | `core/skills/ags-team/references/team-combat.md` |
| 59 | `ccgs-team-level` | `ags-team` | `core/skills/ags-team/references/team-level.md` |
| 60 | `ccgs-team-live-ops` | `ags-team` | `core/skills/ags-team/references/team-live-ops.md` |
| 61 | `ccgs-team-narrative` | `ags-team` | `core/skills/ags-team/references/team-narrative.md` |
| 62 | `ccgs-team-polish` | `ags-team` | `core/skills/ags-team/references/team-polish.md` |
| 63 | `ccgs-team-qa` | `ags-team` | `core/skills/ags-team/references/team-qa.md` |
| 64 | `ccgs-team-release` | `ags-team` | `core/skills/ags-team/references/team-release.md` |
| 65 | `ccgs-team-ui` | `ags-team` | `core/skills/ags-team/references/team-ui.md` |
| 66 | `ccgs-gate-check` | `ags-gate` | `core/skills/ags-gate/SKILL.md`, `CONTRACT.md`, `references/gate-*.md` |
| 67 | `ccgs-localize` | `ags-localize` | `core/skills/ags-localize/SKILL.md`, `references/{extraction-and-validation,brief-cultural-vo,rtl-and-qa}.md` |
| 68 | `ccgs-release-checklist` | `ags-release` | `core/skills/ags-release/SKILL.md`, `references/release-checklist.md` |
| 69 | `ccgs-launch-checklist` | `ags-release` | `core/skills/ags-release/references/launch-checklist.md` |
| 70 | `ccgs-changelog` | `ags-release` | `core/skills/ags-release/references/changelog.md` |
| 71 | `ccgs-patch-notes` | `ags-release` | `core/skills/ags-release/references/patch-notes.md` |
| 72 | `ccgs-day-one-patch` | `ags-release` | `core/skills/ags-release/references/day-one-patch.md` |
| 73 | `ccgs-hotfix` | `ags-release` | `core/skills/ags-release/references/hotfix.md` |
| 74 | `ccgs-skill-test` | `ags-skill-ops` | `core/skills/ags-skill-ops/SKILL.md`, `references/skill-test.md` |
| 75 | `ccgs-skill-improve` | `ags-skill-ops` | `core/skills/ags-skill-ops/references/skill-improve.md` |

---

## 2. Agent & Role Parity Matrix (49 Original Roles -> 12 Core + 15 Engine + 25 Lenses = 52 Files)

### 2A. 12 Core Roles (`core/agents/core/`)

| AGS v2 Core Role | Sandbox Mode | Effort | Engine Overlay | Attached Lenses | Legacy Source Role(s) |
|---|---|---|---|---|---|
| `scout` | `read-only` | `low` | `false` | `[]` | New fast codebase/GDD/ADR investigator |
| `creative-director` | `read-only` | `high` | `false` | `[player-psychology]` | `creative-director` |
| `technical-director` | `read-only` | `high` | `true` | `[architecture]` | `technical-director` |
| `qa-lead` | `read-only` | `high` | `true` | `[qa-strategy]` | `qa-lead` (fixed coder prompt contradiction) |
| `code-reviewer` | `read-only` | `high` | `true` | `[game-rubric, security]` | New read-only reviewer (absorbs `lead-programmer` review) |
| `producer` | `workspace-write` | `medium` | `false` | `[scope-estimation]` | `producer` |
| `game-designer` | `workspace-write` | `high` | `false` | `[systems-design, economy, narrative, difficulty]` | `game-designer` |
| `art-ux-director` | `workspace-write` | `medium` | `false` | `[art-direction, ux-design, accessibility]` | Consolidates `art-director` + `ux-designer` + `accessibility-specialist` |
| `prototyper` | `workspace-write` | `medium` | `true` | `[]` | `prototyper` |
| `gameplay-coder` | `workspace-write` | `medium` | `true` | `[ai, networking, engine-core, ui]` | `gameplay-programmer` |
| `tech-artist` | `workspace-write` | `medium` | `true` | `[shaders, audio]` | `technical-artist` |
| `test-engineer` | `workspace-write` | `medium` | `true` | `[test-automation, performance]` | `qa-tester` |

### 2B. 15 Engine Specialists (`core/agents/engines/`)

| Pack | Original Roles -> AGS v2 Exact 1-to-1 Path |
|---|---|
| `godot/` (5) | `godot-specialist.md`, `godot-gdscript-specialist.md`, `godot-csharp-specialist.md`, `godot-shader-specialist.md`, `godot-gdextension-specialist.md` |
| `unity/` (5) | `unity-specialist.md`, `unity-dots-specialist.md`, `unity-ui-specialist.md`, `unity-shader-specialist.md`, `unity-addressables-specialist.md` |
| `unreal/` (5) | `unreal-specialist.md`, `ue-blueprint-specialist.md`, `ue-gas-specialist.md`, `ue-replication-specialist.md`, `ue-umg-specialist.md` |

### 2C. 25 Domain Lenses (`core/agents/lenses/`)

Every one of the remaining 25 original roles is preserved 1-to-1 under `core/agents/lenses/*.md` and copied to `.ags/roles/` during `ags init`:

| # | Original Role (`assets/template/.claude/agents/`) | AGS v2 Lens (`core/agents/lenses/`) | Core Parent |
|---|---|---|---|
| 1 | `accessibility-specialist.md` | `core/agents/lenses/accessibility-specialist.md` | `art-ux-director` |
| 2 | `ai-programmer.md` | `core/agents/lenses/ai-programmer.md` | `gameplay-coder` |
| 3 | `analytics-engineer.md` | `core/agents/lenses/analytics-engineer.md` | `gameplay-coder` |
| 4 | `art-director.md` | `core/agents/lenses/art-director.md` | `art-ux-director` |
| 5 | `audio-director.md` | `core/agents/lenses/audio-director.md` | `tech-artist` |
| 6 | `community-manager.md` | `core/agents/lenses/community-manager.md` | `producer` |
| 7 | `devops-engineer.md` | `core/agents/lenses/devops-engineer.md` | `producer` |
| 8 | `economy-designer.md` | `core/agents/lenses/economy-designer.md` | `game-designer` |
| 9 | `engine-programmer.md` | `core/agents/lenses/engine-programmer.md` | `gameplay-coder` |
| 10 | `lead-programmer.md` | `core/agents/lenses/lead-programmer.md` | `code-reviewer` |
| 11 | `level-designer.md` | `core/agents/lenses/level-designer.md` | `game-designer` |
| 12 | `live-ops-designer.md` | `core/agents/lenses/live-ops-designer.md` | `producer` |
| 13 | `localization-lead.md` | `core/agents/lenses/localization-lead.md` | `producer` |
| 14 | `narrative-director.md` | `core/agents/lenses/narrative-director.md` | `game-designer` |
| 15 | `network-programmer.md` | `core/agents/lenses/network-programmer.md` | `gameplay-coder` |
| 16 | `performance-analyst.md` | `core/agents/lenses/performance-analyst.md` | `test-engineer` |
| 17 | `release-manager.md` | `core/agents/lenses/release-manager.md` | `producer` |
| 18 | `security-engineer.md` | `core/agents/lenses/security-engineer.md` | `code-reviewer` |
| 19 | `sound-designer.md` | `core/agents/lenses/sound-designer.md` | `tech-artist` |
| 20 | `systems-designer.md` | `core/agents/lenses/systems-designer.md` | `game-designer` |
| 21 | `tools-programmer.md` | `core/agents/lenses/tools-programmer.md` | `gameplay-coder` |
| 22 | `ui-programmer.md` | `core/agents/lenses/ui-programmer.md` | `gameplay-coder` |
| 23 | `ux-designer.md` | `core/agents/lenses/ux-designer.md` | `art-ux-director` |
| 24 | `world-builder.md` | `core/agents/lenses/world-builder.md` | `game-designer` |
| 25 | `writer.md` | `core/agents/lenses/writer.md` | `game-designer` |

---

## 3. Director Gates Parity (28 Gates -> `core/gates/`)

All 28 gates from `assets/template/.claude/docs/director-gates/*.md` map 1-to-1 to `core/gates/*.md`, indexed in `core/gates/INDEX.md`:

- **Creative Director (`CD-`, 6)**: `cd-pillars.md`, `cd-gdd-align.md`, `cd-systems.md`, `cd-narrative.md`, `cd-playtest.md`, `cd-phase-gate.md`
- **Technical Director (`TD-`, 8)**: `td-system-boundary.md`, `td-feasibility.md`, `td-architecture.md`, `td-adr.md`, `td-engine-risk.md`, `td-phase-gate.md`, `td-manifest.md`, `td-change-impact.md`
- **Producer (`PR-`, 5)**: `pr-scope.md`, `pr-sprint.md`, `pr-milestone.md`, `pr-epic.md`, `pr-phase-gate.md`
- **Art / UX Director (`AD-`, 4)**: `ad-concept-visual.md`, `ad-art-bible.md`, `ad-phase-gate.md`, `ad-visual.md`
- **Lead Programmer / Code Reviewer (`LP-`, 2)**: `lp-feasibility.md`, `lp-code-review.md`
- **QA Lead (`QL-`, 2)**: `ql-story-ready.md`, `ql-test-coverage.md`
- **Narrative Director (`ND-`, 1)**: `nd-consistency.md`

---

## 4. Deterministic Scripts & Validators (`ags/checks.py` + `ags/config.py`)

| Original Script (`assets/template/.claude/scripts/` & `hooks/`) | AGS v2 Implementation | CLI Subcommand |
|---|---|---|
| `adr-dep-graph.sh` | `ags/checks.py:adr_dep_graph` | `ags check adr-graph` |
| `gdd-structure-check.sh` | `ags/checks.py:gdd_structure_check` | `ags check gdd` |
| `artifact-check.sh` | `ags/checks.py:artifact_check` (uses `core/workflow-catalog.yaml` / `.ags/workflow-catalog.yaml`) | `ags check artifacts` |
| `project-coherence.sh` | `ags/checks.py:project_coherence` | `ags check coherence` |
| `review-receipts.sh` | `ags/checks.py:review_receipts` | `ags check receipts` |
| `review-scope.sh` | `ags/checks.py:review_scope` | `ags check review-scope` |
| `rotate-session-state.sh` | `ags/checks.py:rotate_session_state` | `ags check rotate-state` |
| `migrate-v1-config.sh` | `ags/checks.py:migrate_v1_config` | `ags check migrate-v1` |
| `yaml-helper.sh` | `ags/config.py` (`parse_yaml`, `resolve_config`, `preflight`) | `ags preflight <skill>` |
| *New in AGS v2* | `ags/checks.py:verify_project` (`_validate_universal_syntax`, `_validate_godot`, `_validate_unity`, `_validate_unreal`) | `ags verify` |

---

## 5. Hooks & Rules Parity

### 5A. 14 Original Hooks + Codex Bridge -> 5 Unified Hooks (`ags/hooks.py`)

| Legacy Hook(s) | Unified AGS v2 Hook | Purpose |
|---|---|---|
| `session-start.sh`, `detect-gaps.sh` | `hook_session_start` | O(1) <=12-line Dynamic Compass (`project.yaml` + `active.md` CHECKPOINT); graceful no-op outside game repo |
| `validate-commit.sh`, `validate-push.sh` | `hook_pre_command` | Blocks receipt tampering, forced generated-dir git commits, invalid JSON/hardcoded patterns |
| `validate-assets.sh`, `validate-skill-change.sh` | `hook_post_edit` | Checks asset naming/JSON validity and flags skill validation reminders |
| *New in AGS v2 (Story Checkpoint Harness)* | `hook_story_gate` | Blocks `Status: Complete` unless `.ags/state/receipt.json` matches current tree hash OR explicit `NOT VERIFIED` rationale exists |
| `pre-compact.sh`, `post-compact.sh`, `session-stop.sh` | `hook_checkpoint_sync` | Injects `active.md` checkpoint across compaction; content-hash guarded archiving to `production/session-logs/session-log.md` |
| `log-agent.sh`, `log-agent-stop.sh`, `notify.sh` | Subagent/notification diagnostics | Covered via native harness agent logging (`codex`/`opencode`/`claude`/`antigravity`) and `ags doctor` |

### 5B. 13 Path Rules (`core/rules/*.md`)

All 13 rules from `assets/template/.claude/rules/*.md` migrate 1-to-1 into `core/rules/`:
`agent-memory.md`, `ai-code.md`, `data-files.md`, `design-docs.md`, `engine-code.md`, `gameplay-code.md`, `narrative.md`, `network-code.md`, `prototype-code.md`, `shader-code.md`, `skill-authoring.md`, `test-standards.md`, `ui-code.md` (modernized to Game-Native engine-idiomatic rubrics across `src/`, `Assets/`, and `Source/`), routed by `core/rules/AGENTS.md`.

---

## 6. Templates (46 `.md` + `project.yaml`) & Engine Reference Docs (46 `.md`)

### 6A. 46 Templates (`core/templates/`)

All 39 root templates + 7 `guidance/` templates migrate 1-to-1 from `assets/template/.claude/docs/templates/`:
- **Root (39)**: `accessibility-requirements.md`, `architecture-decision-record.md`, `architecture-doc-from-code.md`, `architecture-traceability.md`, `art-bible.md`, `changelog-template.md`, `concept-doc-from-prototype.md`, `design-doc-from-implementation.md`, `difficulty-curve.md`, `economy-model.md`, `faction-design.md`, `game-brief.md`, `game-concept.md`, `game-design-document.md`, `game-pillars.md`, `hud-design.md`, `incident-response.md`, `interaction-pattern-library.md`, `level-design-document.md`, `milestone-definition.md`, `narrative-character-sheet.md`, `pitch-document.md`, `player-journey.md`, `post-mortem.md`, `project-stage-report.md`, `prototype-report.md`, `release-checklist-template.md`, `release-notes.md`, `risk-register-entry.md`, `session-state.md`, `SKILL-CONTRACT-TEMPLATE.md`, `sound-bible.md`, `sprint-plan.md`, `systems-index.md`, `technical-design-document.md`, `test-evidence.md`, `test-plan.md`, `ux-spec.md`, `vertical-slice-report.md`.
- **Guidance (7)**: `guidance/accessibility-requirements-guide.md`, `guidance/hud-design-guide.md`, `guidance/interaction-pattern-library-guide.md`, `guidance/interaction-pattern-library-guide-standard-controls.md`, `guidance/interaction-pattern-library-guide-game-specific.md`, `guidance/interaction-pattern-library-guide-navigation-feedback.md`, `guidance/ux-spec-guide.md`.
- **Config template**: `core/templates/project.yaml`.

### 6B. 46 Engine Reference Docs (`core/engine-reference/`)

All 46 files migrate 1-to-1 from `assets/template/docs/engine-reference/`:
- **Index (1)**: `README.md`
- **Godot (12)**: `godot/VERSION.md`, `breaking-changes.md`, `current-best-practices.md`, `deprecated-apis.md`, plus `godot/modules/{animation,audio,input,navigation,networking,physics,rendering,ui}.md` (8)
- **Unity (16)**: `unity/VERSION.md`, `PLUGINS.md`, `breaking-changes.md`, `current-best-practices.md`, `deprecated-apis.md`, plus `unity/modules/{animation,audio,input,navigation,networking,physics,rendering,ui}.md` (8) + `unity/plugins/{addressables,cinemachine,dots-entities}.md` (3)
- **Unreal (17)**: `unreal/VERSION.md`, `PLUGINS.md`, `breaking-changes.md`, `current-best-practices.md`, `deprecated-apis.md`, plus `unreal/modules/{animation,audio,input,navigation,networking,physics,rendering,ui}.md` (8) + `unreal/plugins/{common-ui,gameplay-ability-system,gameplay-camera-system,pcg}.md` (4)
