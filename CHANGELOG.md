# Changelog

All notable changes to **Agents Game Studio (AGS)** are documented here.
See [docs/MIGRATION.md](docs/MIGRATION.md) for upgrading existing CCGS v1.0, v1.1, or Codex-port projects, and [docs/PARITY-LEDGER.md](docs/PARITY-LEDGER.md) for full 1-to-1 capability traceability.

---

## [2.0.0] — 2026-11-24

**Agents Game Studio v2.0**: Multi-harness Closed-Loop Harness with 1 canonical core, 4 harness adapters + universal standard, pure-Python 3.10+ stdlib runtime, consolidated 21-skill pipeline, single-engine isolation, and anti-hallucination verification receipts.

### Added

- **Pure-Python 3.10+ Stdlib Runtime (`ags/`, `ags_cli.py`, `pyproject.toml`)**:
  - `ags init` and `ags sync` assemble clean game projects from `core/` and bundle a standalone, zero-dependency `.ags/cli.py`.
  - `ags config` / `ags preflight <skill>` implements a pure-Python YAML parser and precedence resolver (`project.local.yaml` -> `project.yaml` -> legacy `.txt` -> `modes.rigor` expansion with `jam`/`indie`/`studio` aliases -> `workflow_overrides.system_overrides` -> defaults), uniformly treating `null` and `""` as unset.
  - `ags verify` performs universal JSON/YAML/TOML syntax checks plus engine-aware static validators (Godot 4 legacy Godot 3 syntax & broken `ext_resource` detection, Unity missing/orphaned `.meta` & `Update()` anti-patterns, Unreal `.generated.h` include ordering, and optional engine CLI checks) and emits `.ags/state/receipt.json` stamped with `tree_hash`.
  - `ags doctor` checks enabled harness configs, tests live hook execution, probes engine CLIs, and flags duplicate/legacy `ccgs-*` skill installs.
  - `ags build [--check]` compiles `core/skills/` -> root `skills/`, generates plugin-root `hooks.json`, and keeps `plugin.json`, `.codex-plugin/plugin.json`, and `.agents/plugins/marketplace.json` synchronized at `agents-game-studio` `2.0.0`.
- **4 Harness Adapters + Universal Standard (`ags/adapters/`)**:
  - **Codex**: `.codex/config.toml` (`multi_agent = true`), `.codex/agents/*.toml` (multiline instructions, `sandbox_mode`, `model_reasoning_effort`), and `.codex/hooks.json` (`hookSpecificOutput` snake_case protocol).
  - **Antigravity**: `.agents/hooks.json` (camelCase protojson `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`) and `.agents/rules/ags-rules.md`.
  - **OpenCode**: `opencode.json`, `.opencode/agents/*.md`, and `.opencode/plugins/ags-hooks.ts`.
  - **Claude Code**: `CLAUDE.md` (`@AGENTS.md`), `.claude/agents/*.md`, and `.claude/settings.json` (exit code `2` block protocol).
  - **Universal**: Standard `AGENTS.md` + `.agents/skills/` + `.ags/` layout.
- **5 Unified Lifecycle Hooks (`ags/hooks.py`)**: `session_start` (O(1) <=12-line Dynamic Compass), `pre_command`, `post_edit`, `story_gate` (anti-hallucination guard requiring matching receipt tree hash or explicit `NOT VERIFIED` rationale before `Status: Complete`), and `checkpoint_sync` (compaction survival + content-hash guarded session log archival).
- **New Canonical Core Roles**: Added `scout` (`read-only`, `low` effort) for fast codebase/doc reconnaissance and `code-reviewer` (`read-only`, `high` effort) for Game-Native code reviews; consolidated visual/UX/accessibility under `art-ux-director`.
- **Repo-Only Eval & Cohesion Suite (`tests/`)**: Added unit tests (`test_config.py`, `test_checks.py`, `test_hooks.py`, `test_adapters.py`, `test_cohesion.py`) and migrated behavioral specs + updated `quality-rubric.md` & `catalog.yaml` into `tests/eval/` (excluded from `ags init` game project scaffolds).
- **Architecture, Parity & Migration Documentation (`docs/`)**: Added [`docs/architecture/ags-v2-architecture.md`](docs/architecture/ags-v2-architecture.md), [`docs/PARITY-LEDGER.md`](docs/PARITY-LEDGER.md), and [`docs/MIGRATION.md`](docs/MIGRATION.md).

### Changed

- **75 -> 21 Canonical Skills (`core/skills/ags-*/`)**: Consolidated all 75 `ccgs-*` workflows into 21 intent-scoped skills (`<= 220` lines each in `SKILL.md`, with standardized `## Contract`, `## Preflight`, `## Phases`, and `## Gate & Verdict` sections and sub-mode playbooks preserved under `references/*.md`).
- **49 Roles -> 12 Core + 3x5 Engine Packs + 25 Domain Lenses (`core/agents/`)**:
  - Single-engine isolation on `ags init` installs only the selected engine's 5 specialists and `docs/engine-reference/<engine>/`.
  - Enforced `sandbox_mode: read-only` on all 5 reviewer roles (`scout`, `creative-director`, `technical-director`, `qa-lead`, `code-reviewer`) and fixed the upstream `qa-lead` gameplay-coder prompt contradiction and engine specialist `"Must NOT implement features directly"` contradiction.
- **8 Bash Scripts -> Pure-Python `ags/checks.py`**: Ported `adr-dep-graph`, `gdd-structure-check`, `artifact-check` (via `core/workflow-catalog.yaml`), `project-coherence`, `review-receipts`, `review-scope`, `rotate-session-state`, and `migrate-v1-config` into Windows/POSIX-portable Python with zero Git Bash dependency.
- **Story Checkpoint Harness & Game-Native Rubric**: Replaced per-file `"May I write"` prompts and Java-style `40-line`/`cyclomatic <= 10`/mandatory-DI rules with two-checkpoint story execution, Playtest & Game Feel Tuning Cards for Player-facing stories, and engine-idiomatic rubrics across `src/`, `Assets/`, and `Source/`.
- **Honest `NOT ASSESSED` / `NOT VERIFIED` Ranking**: Standardized `FAIL / BLOCKED > NOT ASSESSED > PASS` across skills, gates, templates, and eval rubrics so missing artifacts or skipped checks never silently report `PASS`.

### Removed

- Legacy `skills/ccgs-*` 75-directory layout, `assets/template/` monolithic bundle, `.claude/hooks/*.sh`, `.claude/scripts/*.sh`, `.codex/hooks/bridge.py`, `yaml-helper.sh`, and legacy `tests/smoke_port.py`.

---

## [0.1.0 / Upstream v1.1.0] — 2026-09-23

- **Codex Port (`codex-game-studio`)**: Initial adaptation of Donchitos' `Claude-Code-Game-Studios` v1.1.0 (`d056997`) mapping 74 workflows to `$ccgs-*`, 49 agents to `.codex/agents/*.toml`, and `.claude/hooks/*.sh` through `.codex/hooks/bridge.py`.
- **Upstream CCGS v1.1.0**: Introduced `project.yaml`, `project.local.yaml`, `modes.rigor` (`minimal`/`standard`/`full`), per-system `workflow_overrides`, `artifact-check.sh`, `adr-dep-graph.sh`, `review-receipts.sh`, `migrate-v1-config.sh`, and the Story Checkpoint Harness design spec.
