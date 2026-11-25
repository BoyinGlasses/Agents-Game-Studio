# Agents Game Studio (AGS v2.0)

**Multi-harness, engine-aware AI game studio framework.**

Plan, design, architect, build, verify, and ship games across **Codex**, **Antigravity**, **OpenCode**, **Claude Code**, and **Universal `AGENTS.md` harnesses** from a single canonical studio core and a zero-dependency Python runtime.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![21 Skills](https://img.shields.io/badge/skills-21-green.svg)](core/skills/) [![52 Roles](https://img.shields.io/badge/studio_roles-12_core_%2B_15_engine_%2B_25_lenses-blueviolet.svg)](core/agents/) [![28 Gates](https://img.shields.io/badge/director_gates-28-orange.svg)](core/gates/)

*Evolved from [BoyinGlasses/Codex-Game-Studio](https://github.com/BoyinGlasses/Codex-Game-Studio) and [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios).*

---

## Why AGS v2.0?

Building a game with AI assistants breaks down when design decisions vanish into chat history, skills prompt before every routine file edit, reviewers modify code they were supposed to audit, or engine versions drift past model training cutoffs.

**Agents Game Studio v2.0** solves this with a **Closed-Loop Harness**:

```text
Hooks (ags/hooks.py) ──> Thin AGENTS.md Routing ──> 21 Skills (ags-*)
        ▲                                                   │
        │                                                   ▼
Receipts (.ags/state/receipt.json) ◄── Core + Engine + Lens Roles (.ags/roles/)
```

- **1 Core, 4 Harness Adapters + Universal Standard**: One `core/` repository compiles cleanly into Codex, Antigravity, OpenCode, Claude Code, and universal `AGENTS.md` + `.agents/skills/` layouts.
- **Zero-Dependency Python 3.10+ Runtime**: Replaces fragile Bash/Git-Bash scripts with pure-Python stdlib tooling (`ags/`), bundled directly into every initialized game project as a standalone `.ags/cli.py`.
- **Single-Engine Isolation**: Choose `--engine godot | unity | unreal | none` at init time; only your engine's 5 specialists and `docs/engine-reference/<engine>/` snapshot are installed.
- **Story Checkpoint Harness**: Replaces per-file write interruptions with two clean checkpoints — **Checkpoint 1** (goal, scope, acceptance criteria, `Handoff Class`, verification method) and **Checkpoint 2** (receipt + evidence + play confirmation before `Status: Complete`).
- **Honest `NOT ASSESSED` & Anti-Hallucination Receipts**: `story_gate` blocks `Status: Complete` unless `.ags/state/receipt.json` matches the workspace tree hash or carries an explicit `NOT VERIFIED` rationale.

---

## What's Included

| Component | Count | Location | Purpose |
|---|---:|---|---|
| Unified workflow skills | 21 | [`core/skills/`](core/skills/) -> [`skills/`](skills/) | Consolidates all 75 legacy `ccgs-*` workflows (`SKILL.md` <=220 lines + lazy-loaded `references/*.md`) |
| Core studio roles | 12 | [`core/agents/core/`](core/agents/core/) | 5 strictly `read-only` reviewers (`scout`, `creative-director`, `technical-director`, `qa-lead`, `code-reviewer`) + 7 `workspace-write` executors |
| Engine specialist packs | 15 | [`core/agents/engines/`](core/agents/engines/) | 5 Godot + 5 Unity + 5 Unreal specialists (only active engine installed per project) |
| Domain lenses | 25 | [`core/agents/lenses/`](core/agents/lenses/) | Preserves 100% of specialized checklists (AI, networking, audio, narrative, economy, security, l10n, etc.) |
| Director & lead gates | 28 | [`core/gates/`](core/gates/) | Structured gate prompts indexed in [`core/gates/INDEX.md`](core/gates/INDEX.md) |
| Path-scoped rules & router | 14 | [`core/rules/`](core/rules/) | `<110`-line `AGENTS.md` routing table + 13 Game-Native rules across `src/`, `Assets/`, `Source/` |
| Document templates | 46 + `project.yaml` | [`core/templates/`](core/templates/) | GDDs, ADRs, art/audio bibles, UX guides, epics/stories, test plans, session state |
| Version-pinned engine docs | 46 | [`core/engine-reference/`](core/engine-reference/) | Godot 4.6, Unity 6.3 LTS, Unreal Engine 5.7 post-cutoff API references |
| Pure-Python CLI & hooks | 1 runtime | [`ags/`](ags/) | `init`, `sync`, `doctor`, `verify`, `preflight`, `check`, `hook`, `build` |

---

## Quick Start

### Requirements

- **Python 3.10+** (pure stdlib — no third-party packages required)
- **Git** (optional, recommended for tree-hash receipts and scope checks)
- Your chosen game engine (**Godot 4**, **Unity 6**, or **Unreal Engine 5**) to build and playtest

### 1. Install or Run the CLI

Run directly from a clone, or install the `ags` console script locally:

```bash
git clone https://github.com/BoyinGlasses/Agents-Game-Studio.git
cd Agents-Game-Studio

# Option A: install editable CLI (`ags` command)
pip install -e .

# Option B: invoke directly without installing
python ags_cli.py --help
```

For Codex plugin marketplace installation:

```bash
codex plugin marketplace add BoyinGlasses/Agents-Game-Studio
codex plugin add agents-game-studio@agents-game-studio
```

### 2. Initialize a Game Project (`ags init`)

Target your game repository and select your **engine** and **harness adapter(s)**:

```bash
# Godot + Codex & Antigravity
ags init /path/to/MyGame --engine godot --harness codex,antigravity

# Unity + OpenCode & Claude Code
ags init /path/to/MyGame --engine unity --harness opencode,claude

# Unreal + all harnesses (or universal AGENTS.md standard only)
ags init /path/to/MyGame --engine unreal --harness all
ags init /path/to/MyGame --engine godot --harness universal
```

> Every initialized game project receives a standalone, zero-dependency `.ags/cli.py`, so hooks and checks run inside the game repo with no runtime dependency on this framework repository. `tests/eval/` stays in the framework repo and is never copied into game projects.

### 3. Harness Setup Notes

| Harness | Generated Adapter Files | First-Run Notes |
|---|---|---|
| **Codex** (`codex`) | `.codex/config.toml`, `.codex/agents/*.toml`, `.codex/hooks.json` | Multi-agent roles with native `sandbox_mode` (`read-only` enforced for reviewers) and `model_reasoning_effort`. Review/trust hooks via `/hooks` on first open. Invoke workflows with `$ags-start` or `ags-start`. |
| **Antigravity** (`antigravity`) | `.agents/hooks.json`, `.agents/rules/ags-rules.md`, `.agents/skills/ags-*/` | Uses camelCase protojson hook schema (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`) and workspace rules. |
| **OpenCode** (`opencode`) | `opencode.json`, `.opencode/agents/*.md`, `.opencode/plugins/ags-hooks.ts` | Configures tool permissions, agent modes, and a thin TypeScript hook plugin calling `python .ags/cli.py hook --harness opencode`. |
| **Claude Code** (`claude`) | `CLAUDE.md` (`@AGENTS.md`), `.claude/agents/*.md`, `.claude/settings.json` | Routes hooks through `.ags/cli.py hook --harness claude` (exit code `2` on policy block). |
| **Universal** (`universal`) | `AGENTS.md`, `project.yaml`, `.agents/skills/ags-*/`, `.ags/` | Compatible with any coding agent reading `AGENTS.md` and the Agent Skills layout. |

### 4. Start Building

Open your initialized game directory in your AI harness and invoke **`ags-start`**. Choose your `modes.rigor` level (`minimal` / `jam`, `standard` / `indie`, or `full` / `studio`), configure your engine with `ags-settings`, and follow the guided loop:

```text
ags-ideate -> ags-gdd -> ags-architect -> ags-plan -> ags-dev -> ags-verify -> ags-qa -> ags-release
```

---

## CLI Reference

Inside an initialized game project, replace `ags` with `python .ags/cli.py`:

| Command | Purpose |
|---|---|
| `ags init [dir] --engine <e> --harness <h>` | Assemble a new game project from `core/` for selected engine and harnesses |
| `ags sync [dir]` | Refresh `.ags/cli.py`, core skills/roles/templates, and harness configs in an existing AGS v2 repo |
| `ags doctor [dir] [--json]` | Verify harness JSON/TOML schemas, test hook execution, check engine CLIs, flag duplicate `ccgs-*` skills |
| `ags verify [dir] [--engine <e>] [--json]` | Run universal JSON/YAML/TOML checks + engine-aware validators (Godot 4, Unity, Unreal) and write `.ags/state/receipt.json` |
| `ags preflight <skill> [target]` | Emit resolved config (`project.local.yaml` -> `project.yaml` -> rigor -> overrides -> defaults) + session/receipt context as JSON |
| `ags check adr-graph [adr-dir]` | Build ADR dependency graph and detect cycles deterministically |
| `ags check gdd [target]` | Report section presence across system GDDs |
| `ags check artifacts [--phase <id>]` | Evaluate `.ags/workflow-catalog.yaml` artifact specs against files on disk |
| `ags check coherence` | Reconcile `project.yaml` declarations against `docs/engine-reference/` and engine files |
| `ags check receipts <hash\|check\|sections-hash\|sections-check> ...` | Compute content hashes and section-level diffs for review receipts |
| `ags check review-scope` | Compute incremental cross-GDD review scope from git history and dependencies |
| `ags check rotate-state [--dry-run]` | Archive narrative notes in `production/session-state/active.md` while keeping the bounded checkpoint |
| `ags check migrate-v1 [--dry-run \| --finalize]` | Safely convert CCGS v1.0 legacy `.txt`/markdown config files into `project.yaml` |
| `ags hook --harness <h> <event>` | Execute one of the 5 unified lifecycle hooks (`session_start`, `pre_command`, `post_edit`, `story_gate`, `checkpoint_sync`) |
| `ags build [--check]` | Compile `core/skills/` -> root `skills/`, root `hooks.json`, and sync plugin manifests (`--check` exits 0 only when clean) |

---

## 21 Cohesive Skills (`core/skills/`)

| Stage / Domain | Skills |
|---|---|
| **Setup & Discovery** | `ags-new-game`, `ags-start`, `ags-settings`, `ags-adopt` |
| **Design & Art/UX** | `ags-ideate`, `ags-gdd`, `ags-art-ux`, `ags-design-review` |
| **Architecture & Planning** | `ags-architect`, `ags-arch-review`, `ags-plan` |
| **Implementation & Verification** | `ags-dev`, `ags-verify`, `ags-qa`, `ags-bugs`, `ags-diagnose` |
| **Orchestration, Gates & Release** | `ags-team`, `ags-gate`, `ags-localize`, `ags-release`, `ags-skill-ops` |

See the complete 75 -> 21 mapping in [`docs/PARITY-LEDGER.md`](docs/PARITY-LEDGER.md).

---

## Documentation & Testing

- **Architecture Deep Dive**: [`docs/architecture/ags-v2-architecture.md`](docs/architecture/ags-v2-architecture.md)
- **Zero-Loss Parity Matrix**: [`docs/PARITY-LEDGER.md`](docs/PARITY-LEDGER.md)
- **Upgrading from v1 / Codex Port**: [`docs/MIGRATION.md`](docs/MIGRATION.md)
- **Eval Rubric & Behavioral Specs**: [`tests/eval/README.md`](tests/eval/README.md)

Run the full framework test suite and build sync verification:

```bash
python -m unittest discover -s tests -v
python -m ags.build --check
python ags_cli.py doctor --json
```

---

## Credits and License

**Agents Game Studio v2.0** builds upon **[Codex-Game-Studio](https://github.com/BoyinGlasses/Codex-Game-Studio)** and adapts **[Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)** by Donchitos.

Licensed under **MIT**. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
