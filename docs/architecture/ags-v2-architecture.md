# Agents Game Studio (AGS v2) — Architecture

Agents Game Studio v2 is a cross-harness, engine-aware studio architecture for building games with AI coding agents. It unifies one canonical studio core (`core/`) and a zero-dependency Python 3.10+ runtime (`ags/`) across **Codex**, **Antigravity**, **OpenCode**, **Claude Code**, and **Universal (`AGENTS.md` + `.agents/skills/`)** workspaces.

---

## 1. Closed-Loop Harness

Every game session operates as a five-stage deterministic loop that keeps memory in files, keeps routing thin, and gates completion on verifiable evidence:

```text
  [1. Hooks (ags/hooks.py)]
      session_start  -> O(1) Dynamic Compass (project.yaml + active.md CHECKPOINT)
      pre_command    -> blocks receipt tampering & forced generated-dir commits
      post_edit      -> validates JSON/YAML/naming & triggers story_gate on edits
      story_gate     -> blocks Status: Complete without valid receipt hash or NOT VERIFIED rationale
      checkpoint_sync-> preserves active.md checkpoint across compaction & turn stops
           │
           ▼
  [2. Thin Router (AGENTS.md + .ags/rules/*.md)]
      Intent -> Skill -> Primary/Review Roles table + scoped Path Rules
           │
           ▼
  [3. Canonical Skills (.agents/skills/ags-*/SKILL.md)]
      21 skills (<=220 lines each): ## Contract -> ## Preflight -> ## Phases -> ## Gate & Verdict
      Lazy-loads sub-mode references (references/*.md) only for the active mode
           │
           ▼
  [4. Core + Engine + Lens Roles (.ags/roles/*.md)]
      12 core roles (5 strictly read-only reviewers, 7 workspace-write executors)
      + 5 active engine specialists (Godot / Unity / Unreal) + 25 domain lenses
      Flat 1-hop worker contract: STATUS: BLOCKED_ON_DECISION when product choices change
           │
           ▼
  [5. Deterministic Checks & Verification Receipts (ags/checks.py)]
      python .ags/cli.py verify -> .ags/state/receipt.json (tree_hash + engine static checks)
      Closes loop back into story_gate and checkpoint_sync
```

### Why Closed-Loop Replaces Prose-Only Guardrails

1. **O(1) Session Compass (`hook_session_start`)**: Instead of dumping large markdown docs into session context, `session_start` reads `project.yaml` and the bounded `<!-- STATUS -->` / `<!-- CHECKPOINT -->` region of `production/session-state/active.md` (<= 12 lines), gracefully becoming a no-op outside a game project (`project.yaml` absent).
2. **Deterministic Preflight (`python .ags/cli.py preflight <skill>`)**: Replaces Bash `yaml-helper.sh` preprocessing with pure Python (`ags/config.py`) emitting resolved JSON + key provenance (`project.local.yaml` -> `project.yaml` -> legacy mirrors -> `modes.rigor` expansion -> `workflow_overrides.system_overrides` -> terminal defaults).
3. **Anti-Hallucination Story Gate (`hook_story_gate`)**: Story files cannot be transitioned to `Status: Complete` unless `.ags/state/receipt.json` carries a passing verification receipt matching the current workspace tree hash (`compute_tree_hash`), OR the story records an explicit `NOT VERIFIED: <rationale>` explanation.

---

## 2. Architecture: 1 Core + 4 Harness Adapters + Universal Standard

### Canonical Source (`core/`)

`core/` is the single source of truth in the framework repository:

| Directory | Contents | Destination in Game Project |
|---|---|---|
| `core/skills/` | 21 consolidated `ags-*` skills (`SKILL.md` <=220 lines + `references/*.md` + `CONTRACT.md`) | `.agents/skills/ags-*/` (compiled to root `skills/` via `ags build`) |
| `core/agents/core/` | 12 core studio roles (5 `read-only` + 7 `workspace-write`) | `.ags/roles/*.md` |
| `core/agents/engines/<engine>/` | 3 engine packs x 5 specialists (`godot`, `unity`, `unreal`) | `.ags/roles/*.md` (only selected `--engine` pack!) |
| `core/agents/lenses/` | 25 domain lenses preserving specialized studio checklists | `.ags/roles/*.md` |
| `core/gates/` | 28 director/lead gate definitions + `INDEX.md` | `.ags/gates/*.md` |
| `core/templates/` | 46 Markdown document templates (`guidance/` included) + `project.yaml` | `.ags/templates/` (`project.yaml` at root) |
| `core/rules/` | `AGENTS.md` master routing table + 13 path-scoped Game-Native rules | `AGENTS.md` (root) + `.ags/rules/*.md` |
| `core/engine-reference/<engine>/` | Version-pinned API references (`VERSION.md`, `breaking-changes.md`, `deprecated-apis.md`, `modules/`, `plugins/`) | `docs/engine-reference/<engine>/` (only selected `--engine`!) |
| `core/workflow-catalog.yaml` | Deterministic phase/step/artifact catalog across all 7 stages | `.ags/workflow-catalog.yaml` |

> **Repo-only eval suite (`tests/eval/`)**: Behavioral specs, `catalog.yaml`, and `quality-rubric.md` live under `tests/eval/` in the framework repo and are **never copied** into user game projects during `ags init`.

### Pure-Python Stdlib Runtime (`ags/` -> `.ags/cli.py`)

`ags/` uses strictly Python 3.10+ stdlib (zero PyPI dependencies, UTF-8 enforced):

- `ags/config.py`: pure-Python YAML parser, `null`/`""` normalization, precedence resolver, and `preflight` JSON builder.
- `ags/checks.py`: ports all 8 legacy Bash scripts (`adr_dep_graph`, `gdd_structure_check`, `artifact_check`, `project_coherence`, `review_receipts`, `review_scope`, `rotate_session_state`, `migrate_v1_config`) plus engine-aware static validators (`_validate_universal_syntax`, `_validate_godot`, `_validate_unity`, `_validate_unreal`) producing `.ags/state/receipt.json`.
- `ags/hooks.py`: 5 unified hooks with bidirectional payload adapters (`evaluate_hook`, `format_hook_response`).
- `ags/doctor.py`: validates harness configs, executes hook smoke probes, checks engine CLIs, and detects duplicate skill installations.
- `ags/adapters/{common,codex,antigravity,opencode,claude}.py` + `ags/init_cmd.py`: assembles game projects cleanly and bundles a standalone self-contained `.ags/cli.py` so every game project works offline with zero dependency on the framework repo checkout.
- `ags/build.py`: compiles `core/skills/` -> root `skills/`, generates plugin-root `hooks.json`, and checks/syncs `plugin.json`, `.codex-plugin/plugin.json`, and `.agents/plugins/marketplace.json`.

### 4 Harness Adapters + Universal Standard

| Target | Files Emitted | Hook & Sandbox Translation |
|---|---|---|
| **Universal** (always) | `AGENTS.md`, `project.yaml`, `.agents/skills/ags-*/`, `.ags/{cli.py,roles/,gates/,templates/,rules/,workflow-catalog.yaml}`, `docs/engine-reference/<engine>/` | Standard `AGENTS.md` + Agent Skills layout readable by any compliant coding agent |
| **Codex** (`--harness codex`) | `.codex/config.toml` (`multi_agent = true`), `.codex/agents/*.toml` (multiline `"""..."""`, `sandbox_mode`, `model_reasoning_effort`), `.codex/hooks.json` | Snake_case payloads, `Bash\|exec_command\|shell\|local_shell` and `Edit\|Write\|apply_patch` matchers, `hookSpecificOutput` JSON responses |
| **Antigravity** (`--harness antigravity`) | `.agents/hooks.json`, `.agents/rules/ags-rules.md` | Object-keyed camelCase protojson (`SessionStart`/`Stop` flat; `PreToolUse` `run_command`; `PostToolUse` `edit_file\|write_file`), `injectSteps` / `decision` responses |
| **OpenCode** (`--harness opencode`) | `opencode.json`, `.opencode/agents/*.md`, `.opencode/plugins/ags-hooks.ts` | ~35-line TypeScript plugin invoking `python .ags/cli.py hook --harness opencode` |
| **Claude Code** (`--harness claude`) | `CLAUDE.md` (`@AGENTS.md` pointer), `.claude/agents/*.md`, `.claude/settings.json` | Hook exit code `2` + stderr on block; `settings.json` tool matchers |

---

## 3. Key Design Decisions

1. **75 -> 21 Consolidated Skills (`<= 220` Lines Core)**: Merging 75 fragmented commands into 21 intent-based skills eliminates routing confusion and keeps top-level skill prompts under 220 lines while preserving 100% of sub-mode workflows inside `references/*.md`.
2. **12 Core + 5 Engine + 25 Lenses (Engine Isolation)**: Instead of loading 49 mixed agents (including 10 irrelevant other-engine specialists) into every project, `ags init --engine <godot|unity|unreal|none>` installs only the chosen engine's 5 specialists and engine docs alongside the 12 core roles and 25 reusable lenses.
3. **Read-Only Reviewer Sandboxes**: `scout`, `creative-director`, `technical-director`, `qa-lead`, and `code-reviewer` enforce `sandbox_mode: read-only`. This fixes the upstream `qa-lead` contradiction (which previously carried coder prompts) and ensures reviewers cannot mutate files under inspection.
4. **Story Checkpoint Harness (Replacing `"May I write"` Spam)**: Routine edits inside an approved story run uninterrupted between **Checkpoint 1** (pre-implementation goal/scope/AC/verification approval) and **Checkpoint 2** (receipt + evidence + play confirmation for Player-facing/Mixed stories). Only scope, AC, governing ADR, or engine changes pause mid-story (`STATUS: BLOCKED_ON_DECISION`).
5. **Honest `NOT ASSESSED` / `NOT VERIFIED` Precedence**: Every skill and gate enforces `FAIL / BLOCKED > NOT ASSESSED > PASS`. Missing receipts, absent playtests, or unconfigured directories are explicitly surfaced rather than collapsed to `PASS`.
6. **Game-Native Engine-Idiomatic Rubric**: Replaced Java-enterprise dogma (`cyclomatic complexity <= 10`, `40-line method caps`, mandatory DI interfaces everywhere) with engine-idiomatic composition (Godot nodes/signals, Unity ScriptableObjects/Burst/events, Unreal `UActorComponent`/Subsystems/GAS), zero hot-path tick allocations, and data-driven tuning.
7. **Zero-Bash Windows-Safe Tooling**: Replacing `.claude/scripts/*.sh` + `yaml-helper.sh` + `bridge.py` with pure Python `ags/checks.py` and `ags/config.py` eliminates Git Bash path/quoting breakage and external runtime dependencies.
