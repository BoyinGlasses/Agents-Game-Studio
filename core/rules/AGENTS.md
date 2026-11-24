# Agents Game Studio — Operating Instructions

Multi-harness workspace rules for Codex, Antigravity, OpenCode, Claude Code, and universal Markdown agents.

## Session, Config & Verification
- Read `project.yaml` (overridden by `project.local.yaml`) and `production/session-state/active.md` at session start and after compaction or context resets; `active.md` is the cross-harness durable checkpoint.
- Before executing any workflow skill in `.agents/skills/ags-*/SKILL.md`, run `python .ags/cli.py preflight <skill>`.
- Before citing engine APIs, read `docs/engine-reference/<engine>/VERSION.md`; resolve code root strictly from `project.yaml` (`src/`, `Assets/`, or `Source/`).
- Roles live in `.ags/roles/*.md`; director gates live in `.ags/gates/*.md` (`.ags/gates/INDEX.md`). Never claim a role, check, or test ran when it did not — report `NOT VERIFIED` or `NOT ASSESSED`.

## Story Checkpoint Harness
1. **Checkpoint 1 (Pre-Implementation)**: Present goal, scope, acceptance criteria, story type, and verification method; wait for approval before coding.
2. **In-Scope Execution**: Routine code, test, and evidence edits proceed without per-file permission. Stop and surface `STATUS: BLOCKED_ON_DECISION` only when scope, criteria, governing ADRs, or engine choice change.
3. **Checkpoint 2 (Acceptance)**: Run `python .ags/cli.py verify` (writes `.ags/state/receipt.json`), present evidence matching story type (playable run for Player-facing/Mixed; build/tests for Technical), and wait for game-maker acceptance before marking `Status: Complete`.

## Intent -> Skill -> Primary/Review Roles Routing Table

| Intent | Skill | Primary Role(s) | Review Role(s) |
|---|---|---|---|
| Create or scaffold a new game repo | `ags-new-game` | `producer` | `technical-director` |
| Start, orient, check stage, onboard | `ags-start` | `producer` | `scout` |
| Configure engine, modes, rigor, overrides | `ags-settings` | `technical-director` | `producer` |
| Audit or reverse-doc an existing codebase | `ags-adopt` | `scout`, `technical-director` | `game-designer` |
| Brainstorm pillars, prototype, vertical slice | `ags-ideate` | `creative-director`, `prototyper` | `art-ux-director` |
| Map systems, author GDDs or quick specs | `ags-gdd` | `game-designer` | `creative-director`, `technical-director` |
| Author/audit Art Bible, asset specs, UX, a11y | `ags-art-ux` | `art-ux-director`, `tech-artist` | `creative-director` |
| Review GDDs, consistency, balance, change impact | `ags-design-review` | `game-designer`, `creative-director` | `technical-director` |
| Create architecture, ADRs, control manifest | `ags-architect` | `technical-director` | `code-reviewer` |
| Review architecture, tech debt, or scope | `ags-arch-review` | `technical-director`, `code-reviewer` | `producer` |
| Plan epics, stories, estimates, sprints, retros | `ags-plan` | `producer` | `qa-lead` |
| Validate readiness & implement approved story | `ags-dev` | `gameplay-coder`, `tech-artist` | `qa-lead` |
| Code review, test evidence audit, story done | `ags-verify` | `code-reviewer`, `test-engineer` | `qa-lead` |
| Setup tests/helpers, QA plan, smoke, soak, playtest | `ags-qa` | `qa-lead`, `test-engineer` | `gameplay-coder` |
| Report or triage bugs with severity and owner | `ags-bugs` | `qa-lead`, `test-engineer` | `gameplay-coder` |
| Profile performance or run security audit | `ags-diagnose` | `test-engineer`, `code-reviewer` | `technical-director` |
| Run multi-discipline feature/domain team workflow | `ags-team` | `producer`, `gameplay-coder` | `qa-lead` |
| Evaluate phase-transition readiness gates | `ags-gate` | `producer`, `creative-director` | `technical-director`, `art-ux-director` |
| Extract strings, validate i18n, prep locales | `ags-localize` | `producer`, `gameplay-coder` | `qa-lead` |
| Release/launch checklists, notes, day-one, hotfix | `ags-release` | `producer`, `qa-lead` | `code-reviewer` |
| Test or improve studio skills and gates | `ags-skill-ops` | `technical-director` | `code-reviewer` |

## Path Rules (`.ags/rules/`)
Load the matching rule before reading/writing files in these scopes:
- `.ags/rules/agent-memory.md` -> `.ags/state/**`, `.ags/memory/**`
- `.ags/rules/ai-code.md` -> `src/ai/**`, `Assets/Scripts/AI/**`, `Source/*/AI/**`
- `.ags/rules/data-files.md` -> `assets/data/**`, `Assets/Data/**`, `Content/Data/**`
- `.ags/rules/design-docs.md` -> `design/gdd/**`
- `.ags/rules/engine-code.md` -> `src/core/**`, `Assets/Scripts/Core/**`, `Source/*/Core/**`
- `.ags/rules/gameplay-code.md` -> `src/gameplay/**`, `Assets/Scripts/Gameplay/**`, `Source/*/Gameplay/**`
- `.ags/rules/narrative.md` -> `design/narrative/**`
- `.ags/rules/network-code.md` -> `src/networking/**`, `Assets/Scripts/Networking/**`, `Source/*/Networking/**`
- `.ags/rules/prototype-code.md` -> `prototypes/**`
- `.ags/rules/shader-code.md` -> `assets/shaders/**`, `Assets/Shaders/**`, `Shaders/**`
- `.ags/rules/skill-authoring.md` -> `.agents/skills/**`, `.ags/roles/**`, `.ags/gates/**`
- `.ags/rules/test-standards.md` -> `tests/**`, `Assets/Tests/**`, `Source/*/Tests/**`
- `.ags/rules/ui-code.md` -> `src/ui/**`, `Assets/Scripts/UI/**`, `Source/*/UI/**`
