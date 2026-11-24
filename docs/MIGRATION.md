# Migrating to Agents Game Studio (AGS v2)

This guide covers migrating **existing CCGS v1.0, CCGS v1.1, and Codex-port game projects** to **AGS v2**.
Your game design documents (`design/`), architecture (`docs/architecture/`), epics/stories (`production/`), and source code (`src/`, `Assets/`, `Source/`) stay intact throughout migration.

---

## Scenario A: Legacy CCGS v1.0 Config -> `project.yaml`

If your repo has **no `project.yaml` yet**, and contains any of:
- `production/stage.txt`
- `production/review-mode.txt`
- `.claude/docs/technical-preferences.md` (with configured values instead of `[TO BE CONFIGURED]`)

Run the deterministic converter (ported from `migrate-v1-config.sh` into pure Python — no Git Bash needed):

```bash
# 1. Preview changes without writing files
python .ags/cli.py check migrate-v1 --dry-run
# (Or if `ags` is installed globally / invoked from the framework repo:)
ags check migrate-v1 --dry-run

# 2. Perform non-destructive migration (writes project.yaml + production/migration-report.md)
ags check migrate-v1

# 3. Inspect the migration report (warnings, raw custom values, manual review items)
cat production/migration-report.md

# 4. Finalize (deletes stage.txt and review-mode.txt ONLY after proving preservation in project.yaml)
ags check migrate-v1 --finalize
```

### Important Behavior Notes

1. **`none` -> `solo` rename**: Legacy `production/review-mode.txt` containing `none` maps cleanly to `modes.review_mode: solo`.
2. **`modes.review_mode` vs `modes.rigor`**: If `review-mode.txt` existed, `modes.review_mode` is pinned explicitly in `project.yaml` (which outranks `modes.rigor`). To let `modes.rigor` control review depth later, delete `modes.review_mode` from `project.yaml`.
3. **Preserving v1.0 process depth**: v1.0 behaved like `modes.rigor: standard`. Set `modes.rigor: standard` in `project.yaml` if you want the exact v1.0 depth instead of the lighter `minimal` default.
4. **Never deleted on `--finalize`**: `.claude/docs/technical-preferences.md` is kept because `Forbidden Patterns` and `Allowed Libraries` have no `project.yaml` field yet. Move custom project notes into `AGENTS.md` or `.ags/rules/` when ready.
5. **Split-brain safety**: If both `project.yaml` and differing legacy files exist, `migrate-v1` exits with code `3` (`REFUSED`) until you resolve which is authoritative.

---

## Scenario B: CCGS v1.1 / Codex Port -> AGS v2 Structure

If you already use `project.yaml` with `.claude/`, `.codex/hooks/bridge.py`, and the 74 `.agents/skills/ccgs-*` directories:

### 1. Check for Local Customizations Before Updating

```bash
git status
git log --oneline -- .claude .codex AGENTS.md CLAUDE.md
```

Back up or note any project-specific edits you made to `.claude/agents/*.md`, `.claude/rules/*.md`, or `.claude/docs/director-gates/*.md`.

### 2. Install AGS v2 Core & Selected Harness Adapters

From your game repository root, run `ags init` (or `ags sync` on an already-initialized AGS v2 repo) choosing **only your engine** and **desired harnesses**:

```bash
ags init --engine godot --harness codex,antigravity
# Options:
#   --engine   godot | unity | unreal | none
#   --harness  codex,antigravity,opencode,claude,universal
```

What changes on disk:
- **Standalone CLI added**: `.ags/cli.py` replaces `.claude/scripts/*.sh`, `.claude/hooks/*.sh`, `yaml-helper.sh`, and `.codex/hooks/bridge.py`.
- **Single-engine isolation**: Only `docs/engine-reference/<engine>/` and the 5 matching engine specialists in `.ags/roles/` are installed (the other two engines are omitted).
- **Consolidated skills**: `.agents/skills/` moves from 74 `ccgs-*` directories to the 21 canonical `ags-*` skills (see [PARITY-LEDGER.md](./PARITY-LEDGER.md)).
- **Harness configs regenerated**: `.codex/{config.toml,agents/*.toml,hooks.json}`, `.agents/{hooks.json,rules/ags-rules.md}`, `opencode.json` + `.opencode/`, and/or `CLAUDE.md` + `.claude/{agents/*.md,settings.json}`.
- **No eval bloat in game repos**: `tests/eval/` stays in the AGS v2 framework repository and is never copied into your game repo.

### 3. Clean Up Removed v1 / Codex-Port Artifacts

After verifying `ags doctor` passes, remove obsolete legacy skill/hook directories if unused:
- Remove old `.agents/skills/ccgs-*` folders so `ags doctor` does not report duplicate/legacy skill names.
- Remove old `.codex/hooks/bridge.py` and `.claude/hooks/*.sh` / `.claude/scripts/*.sh` (replaced by `.ags/cli.py hook` and `.ags/cli.py check`).
- Keep `design/`, `docs/architecture/`, `production/`, `prototypes/`, and your game code untouched.

### 4. Brownfield Repos Without Docs (`ags-adopt`)

If you are adopting an **existing game codebase that has no GDDs, ADRs, or `project.yaml`**:

1. Initialize the workspace (`ags init --engine <engine> --harness <harnesses>`).
2. Run the **`ags-adopt`** skill (or `ags-adopt` `reverse-document` mode) to inventory existing code, detect stage gaps, and generate `game-concept.md`, system GDDs, and ADRs from implementation.

---

## Scenario C: Habit & Command Cheat Sheet

| Legacy `/cmd` or `$ccgs-*` | AGS v2 Skill / CLI | Notes |
|---|---|---|
| `/start`, `/help`, `/onboard`, `/project-stage-detect` | `ags-start` | Onboarding, stage check, next-step guide |
| `/settings`, `/setup-engine` | `ags-settings` | Config + engine setup + docs pin |
| `/adopt`, `/reverse-document` | `ags-adopt` | Brownfield adoption & reverse-doc |
| `/brainstorm`, `/prototype`, `/vertical-slice` | `ags-ideate` | Concept, prototype, vertical slice |
| `/map-systems`, `/design-system`, `/quick-design` | `ags-gdd` | Systems index, full GDD, quick spec |
| `/art-bible`, `/asset-spec`, `/asset-audit`, `/ux-design`, `/ux-review` | `ags-art-ux` | Art, assets, UX, accessibility |
| `/design-review`, `/review-all-gdds`, `/consistency-check`, `/balance-check`, `/content-audit`, `/propagate-design-change` | `ags-design-review` | All GDD & balance reviews |
| `/create-architecture`, `/architecture-decision`, `/create-control-manifest` | `ags-architect` | Master arch, ADRs, control manifest |
| `/architecture-review`, `/tech-debt`, `/scope-check` | `ags-arch-review` | Arch review, tech debt, scope check |
| `/create-epics`, `/create-stories`, `/estimate`, `/sprint-plan`, `/sprint-status`, `/milestone-review`, `/retrospective` | `ags-plan` | Epics, stories, sprint & milestone ops |
| `/story-readiness`, `/dev-story` | `ags-dev` | Story Checkpoint #1 + implementation |
| `/code-review`, `/story-done`, `/test-evidence-review` | `ags-verify` | Read-only review + receipt + Checkpoint #2 |
| `/test-setup`, `/test-helpers`, `/qa-plan`, `/smoke-check`, `/regression-suite`, `/soak-test`, `/test-flakiness`, `/playtest-report` | `ags-qa` | Test setup, QA plans, smoke/soak, playtests |
| `/bug-report`, `/bug-triage` | `ags-bugs` | Structured bug logging & triage |
| `/perf-profile`, `/security-audit` | `ags-diagnose` | Performance profiling & security audit |
| `/team-*` (all 9 domain teams) | `ags-team` | Multi-role domain playbooks (`team.size` aware) |
| `/gate-check` | `ags-gate` | Phase transition checks & director panel |
| `/localize` | `ags-localize` | Localization tables, pseudoloc, RTL/CJK |
| `/release-checklist`, `/launch-checklist`, `/changelog`, `/patch-notes`, `/day-one-patch`, `/hotfix` | `ags-release` | Release checklists, notes, hotfixes |
| `/skill-test`, `/skill-improve` | `ags-skill-ops` | Skill/role validation & eval rubric |
| `bash .claude/scripts/<script>.sh` | `python .ags/cli.py check <subcommand>` | `adr-graph`, `gdd`, `artifacts`, `coherence`, `receipts`, `review-scope`, `rotate-state`, `migrate-v1` |
| *New verification receipt* | `python .ags/cli.py verify` | Writes `.ags/state/receipt.json` checked by `story_gate` |

---

## 5. Post-Migration Health Check

Run these four deterministic commands after migrating:

```bash
python .ags/cli.py doctor
python .ags/cli.py check coherence
python .ags/cli.py check artifacts
python .ags/cli.py verify
```

Confirm:
1. `doctor` reports zero broken JSON/TOML hook configs and zero duplicate `ccgs-*` skills.
2. `coherence` reconciles `project.yaml` against `docs/engine-reference/<engine>/VERSION.md` and engine project files.
3. `artifacts` scans `.ags/workflow-catalog.yaml` cleanly across all 7 phases.
4. `verify` emits a valid `.ags/state/receipt.json` matching your workspace tree hash.
