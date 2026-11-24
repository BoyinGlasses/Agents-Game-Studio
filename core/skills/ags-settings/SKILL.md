---
name: ags-settings
description: "Use when inspecting or changing project.yaml / project.local.yaml configuration, running guided game engine setup, or refreshing/upgrading engine reference docs. Do NOT use when onboarding a brand-new project before config exists -> ags-start."
---

# Project Settings & Engine Setup

Manages `project.yaml` (shared team config), `project.local.yaml` (gitignored personal overrides), guided/explicit engine configuration, and `docs/engine-reference/<engine>/` maintenance.

## Contract

- **Inputs**: `project.yaml`, `project.local.yaml`, `design/gdd/game-concept.md` (`standard`/`full`) or `design/game-brief.md` (`minimal`), `docs/engine-reference/<engine>/`, and installed engine binary probes.
- **Roles**: `technical-director` (optional upgrade risk review), `godot-specialist`, `unity-specialist`, `unreal-specialist`.
- **Outputs**: Updated `project.yaml` or `project.local.yaml` (config modes), plus updated `AGENTS.md` Technology Stack / `ENGINE-REFERENCE-IMPORT`, `docs/engine-reference/<engine>/*`, and `project.godot` when absent (engine modes).
- **Verification**: Validate enums and local-override whitelist via `python .ags/cli.py preflight ags-settings`; run `python .ags/cli.py check coherence` after engine writes and report every `[DIFFERS]` and `[NOT CHECKED]` line.
- **Next Skill**: `ags-ideate`, `ags-design-review` (when `modes.workflow` changed), `ags-arch-review` (after engine `upgrade`), or `ags-start`

## Preflight

Run:

```bash
python .ags/cli.py preflight ags-settings
```

Use resolved values (`modes.rigor` expansion, `modes.workflow`, `modes.automation`, `modes.automation_always_ask`, `engine.*`, schema notes, and reserved-key metadata) directly.

For engine setup, refresh, or upgrade, run coherence verification after writes:

```bash
python .ags/cli.py check coherence
```

## Phases

### Phase 1: Parse Arguments & Route Mode

| Invocation Form | Mode | Reference |
|---|---|---|
| No arguments | **Config View-All** (effective values + provenance) | [references/config-mode.md](references/config-mode.md) |
| `<key>` (no `=`) | **Config View-One** | [references/config-mode.md](references/config-mode.md) |
| `<key>=<value>` | **Config Set Team-Wide** (`project.yaml`) | [references/config-mode.md](references/config-mode.md) |
| `--local <key>=<value>` | **Config Set Personal** (`project.local.yaml`) | [references/config-mode.md](references/config-mode.md) |
| `engine [name] [version]` | **Engine Setup** (guided or explicit) | [references/engine-setup.md](references/engine-setup.md) |
| `engine refresh` | **Engine Reference Refresh** | [references/engine-setup.md](references/engine-setup.md) |
| `engine upgrade [old] [new]` | **Engine Version Upgrade & Code Audit** | [references/engine-setup.md](references/engine-setup.md) |

Malformed `key=value` operands (`=foo`, `key=`, `--local key=`) print usage instructions and stop without writing.

### Phase 2: Execute Mode Rules

- **Config Modes**:
  - Derive reserved keys dynamically from preflight/schema metadata (never hardcode them); flag `, reserved` across all four paths (`view-all`, `view-one` above the block, `set-yaml`, `set-local`) without blocking writes.
  - Append all seven `modes.rigor`-family keys in `view-all` so derived values remain visible with `(derived from rigor: <level>)`.
  - Writing `project.yaml` is a `schema_changes` decision (prompts even in `autonomous` mode unless removed from `modes.automation_always_ask`). `--local` refuses locked keys.
- **Engine Modes** (always collaborative due to irreversible project-wide scope):
  - Probe installed editor binary (`godot --version`, `Unity -version`, `UnrealEditor-Cmd -version`), recording `Installed at pin time` or `NOT DETERMINED` in `VERSION.md`.
  - For Godot, load ONLY [references/godot-language-config.md](references/godot-language-config.md) once (`A1`/`A2`/`A3`); never load for Unity or Unreal.
  - Apply the 2D/3D × web/non-web table for Godot `rendering` and `physics`, ask operator for `commands.build` `<PRESET>`/`<TARGET>` (else `[TO BE CONFIGURED]`), obey YAML quote safety, write `AGENTS.md` + `project.yaml`, and verify via `check coherence`.

## Gate & Verdict

- **`COMPLETE`**: View completed, config write validated, or engine setup/refresh/upgrade verified with zero unresolved `[DIFFERS]` errors.
- **`NOT ASSESSED`** *(ranks above `COMPLETE` and below `BLOCKED` / `CONCERNS`)*: Engine setup completed, but binary probe failed (`installed version NOT DETERMINED`), `project.godot` headless import could not run (`project.godot NOT VERIFIED`), or `check coherence` reported `[NOT CHECKED]` items. State every unverified check explicitly.
- **`CONCERNS`**: `check coherence` flagged non-fatal mismatches, `constants` remains `# UNVERIFIED` on Unity/Unreal, or `modes.workflow` changed mid-project (recommend `ags-design-review content-audit`).
- **`BLOCKED`**: Invalid enum value, locked key passed to `--local`, missing base `project.yaml` on `--local`, missing `AGENTS.md` markers, or user declined confirmation.
