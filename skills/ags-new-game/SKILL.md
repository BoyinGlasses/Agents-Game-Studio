---
name: ags-new-game
description: "Use when initializing a brand-new Agents Game Studio project directory outside an existing game project or adding multi-harness scaffolding. Do NOT use when already inside an initialized project -> ags-start."
---

# New Game Project

Scaffolds a fresh, harness-neutral Agents Game Studio (AGS v2) game project directory using `ags_cli.py init` (or `ags init`), installing `AGENTS.md`, `project.yaml`, `.agents/skills/`, `.ags/`, selected engine pack, and harness adapters.

## Contract

- **Inputs**: Non-existent target directory path, `--engine` (`godot|unity|unreal|none`), `--harness` (`codex,antigravity,opencode,claude,universal`), and AGS framework repo path containing `ags_cli.py`.
- **Roles**: `none` (direct orchestrator CLI initialization).
- **Outputs**: Initialized game project at target containing `AGENTS.md`, `project.yaml`, `.gitignore`, `.agents/skills/`, `.ags/` (`cli.py`, `roles/`, `gates/`, `templates/`, `rules/`, `workflow-catalog.yaml`), `docs/engine-reference/<engine>/`, and harness adapter configs.
- **Verification**: Confirm target directory did not pre-exist (use `sync` for upgrades), verify core and harness files exist, and run `python .ags/cli.py doctor` inside target.
- **Next Skill**: `ags-start` (inside the newly created project directory)

## Preflight

1. Check whether the current working directory already contains `project.yaml`:
   - If `project.yaml` exists and the user wants to configure or inspect the current project, run `python .ags/cli.py preflight ags-new-game` and hand off to `ags-start` or `ags-settings` instead of creating a nested project.
   - If refreshing runtime files in an existing project, run `ags sync` per [references/multi-harness-setup.md](references/multi-harness-setup.md).
2. Verify the AGS launcher (`python <repo>/ags_cli.py --help` or `ags --help`). Stop and report `BLOCKED` if unreachable.
3. Confirm target path, `--engine`, and `--harness` choices before running initialization.

## Phases

### Phase 1: Confirm Target & Harness Choices

1. Verify target does not exist on disk. Do not overwrite an existing non-AGS repository without explicit `sync` intent and confirmation.
2. Confirm `--engine` (`godot`, `unity`, `unreal`, or `none`) and `--harness` (`codex`, `antigravity`, `opencode`, `claude`, `universal`). See [references/multi-harness-setup.md](references/multi-harness-setup.md) for per-harness file layouts.

### Phase 2: Run Initializer

Execute the standalone initializer:

```bash
python <repo>/ags_cli.py init <target> --engine <engine> --harness <harness-list>
```

If `ags` is installed on PATH, `ags init <target> --engine <engine> --harness <harness-list>` is equivalent.

### Phase 3: Verify Scaffold & Doctor Health

1. Inspect target to confirm expected layout:
   - `AGENTS.md`, `project.yaml`, `.gitignore`
   - `.ags/cli.py`, `.ags/workflow-catalog.yaml`, `.ags/roles/`, `.ags/gates/`, `.ags/templates/`, `.ags/rules/`
   - `.agents/skills/ags-start/SKILL.md`
   - `docs/engine-reference/<engine>/` (when `--engine` is not `none`)
   - Harness files per [references/multi-harness-setup.md](references/multi-harness-setup.md)
2. Run inside target:

```bash
python .ags/cli.py doctor
```

### Phase 4: Hand Off

Instruct the user to open target in their coding agent harness and invoke `ags-start` to complete onboarding, set `modes.rigor` and `modes.automation`, and configure engine details. Remind Codex users to approve/trust project hooks on first open.

## Gate & Verdict

- **`COMPLETE`**: Project initialized cleanly at target, all core and harness files verified, and `python .ags/cli.py doctor` passed with zero critical errors.
- **`NOT ASSESSED`** *(ranks above `COMPLETE` and below `BLOCKED`)*: Project files were written, but `python .ags/cli.py doctor` or harness verification could not run — list unverified items explicitly; never report verified health without running `doctor`.
- **`BLOCKED`**: Target directory already exists (when `init` requested), invalid flags, or `ags_cli.py` / `ags` CLI unreachable.
