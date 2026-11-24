# Engine Setup, Refresh & Upgrade Reference (`ags-settings engine`)

Configures the game engine, installed version pin, `AGENTS.md` Technology Stack, `project.yaml` (`engine`, `specialists`, `naming`, `commands`), and `docs/engine-reference/<engine>/`.

> Engine setup is a project-wide irreversible commitment and always runs interactively/collaboratively regardless of `modes.automation`.

## 1. Subcommands

- `ags-settings engine <godot|unity|unreal> <version>` — explicit engine + version
- `ags-settings engine <godot|unity|unreal>` — engine provided, look up latest stable version
- `ags-settings engine` — guided recommendation flow
- `ags-settings engine refresh` — update existing `docs/engine-reference/<engine>/` from official docs (Section 9)
- `ags-settings engine upgrade [old] [new]` — audit code root for deprecated APIs and migrate pinned version (Section 10)

## 2. Guided Selection (No Engine Specified)

1. Read existing design artifact for resolved `modes.workflow`:
   - `standard`/`full`: `design/gdd/game-concept.md` (genre, scope, platforms, art style, engine preference).
   - `minimal`: `design/game-brief.md` if present (absence is normal at `minimal` when running engine setup first).
2. Ask **Q1 Prior Experience** (`Godot` | `Unity` | `Unreal Engine 5` | `Multiple` | `None`). If user picks a single familiar engine, recommend it and skip matrix.
3. Ask **Q2 Target Platform** (`PC` | `Mobile` | `Console` | `Web` | `Multiple`) and **Q3–Q7** (2D vs 3D, primary input, team size/experience, language preference, licensing budget).
4. Evaluate honest tradeoffs (never a blind scoring elimination):
   - **Godot 4**: Best-in-class 2D, strong stylized/contained 3D, MIT open-source free forever, fast iteration; thinner 3D open-world ecosystem; console export requires third-party middleware/publishers.
   - **Unity**: Standard for mobile & mid-scope 3D, strong indie console cert & Asset Store ecosystem; C# steeper than GDScript; free below $200K revenue and 200K installs.
   - **Unreal Engine 5**: AAA 3D visuals (Lumen/Nanite/Chaos) & large open worlds, C++ + Blueprint; heaviest editor & compile times, poor web/lightweight mobile fit, 5% royalty after $1M gross.
5. Present comparison table, primary recommendation, best alternative, and offer an optional `"Explore further"` deep-dive before locking the choice.

## 3. Version Lookup & Installed Binary Probe

1. Use provided version, or search web for official `"<engine> latest stable version"` and confirm with user. Never guess an engine version.
2. Probe the local binary (treat probe failure as unknown, never as absent):
   - Godot: `godot --version` (or inspect `Godot_v*` on PATH / default install dir)
   - Unity: `Unity -version` (or Unity Hub editor directory)
   - Unreal: `UnrealEditor-Cmd -version` (or Epic launcher directory)
3. Handle result:
   - **Match**: note match in one line.
   - **Mismatch**: display both versions and let user pick (pin installed / pin newer & upgrade later / pin newer deliberately).
   - **Probe failed / not found**: record `installed version NOT DETERMINED` (never report "no engine installed").
4. Record result in `docs/engine-reference/<engine>/VERSION.md` under `Installed at pin time`. Record `engine.path` in `project.yaml` when the binary is not on `PATH` (critical on Windows).

## 4. Update `AGENTS.md` Technology Stack & Engine Reference Import

- If **Godot**, ask language preference FIRST (`GDScript` | `C#` | `Both`), then read [references/godot-language-config.md](references/godot-language-config.md) ONCE (`A1`, `A2`, `A3`). Never load that file for Unity or Unreal. Pure GDScript uses `"GDScript"` only — never append `"C++ via GDExtension"`.
- Show proposed changes to `AGENTS.md`, confirm with user, then update:
  - Technology Stack bullets (Godot from `A1`; Unity = C# / Unity Build Pipeline / Addressables; Unreal = C++ primary + Blueprint / UBT / Unreal Content Pipeline).
  - Locate the `ENGINE-REFERENCE-IMPORT` marker in `AGENTS.md` and point it to `docs/engine-reference/<engine>/VERSION.md`.
- If a legacy technical-preferences file exists in the repo, keep it synced (do NOT pre-populate Forbidden Patterns or speculative Allowed Libraries).

## 5. Populate `project.yaml` (Primary Store)

Confirm and write four blocks (`engine`, `specialists`, `naming`, `commands`) while preserving all existing blocks (`schema_version`, `framework`, `project`, `modes`). Omit `modes.review_mode` when creating a new file.

### `engine` Block & Godot 2D/3D/Web Matrix

| Engine | Project Shape | `rendering` | `physics` |
|---|---|---|---|
| Godot 4.x | 2D · web (or multi incl. web) | `Compatibility` | `Godot Physics 2D` |
| Godot 4.x | 2D · non-web | `Forward+` | `Godot Physics 2D` |
| Godot 4.x | 3D · web (or multi incl. web) | `Compatibility` | `Jolt` |
| Godot 4.x | 3D · non-web | `Forward+` | `Jolt` |
| Unity | any | `URP` | `PhysX` |
| Unreal | any | `Lumen + Nanite (deferred)` | `Chaos` |

For Godot, if 2D/3D or web target was not gathered in Section 2 or found in the concept/brief, **ask** (`2D · non-web` / `2D · web` / `3D · non-web` / `3D · web` / `[TO BE CONFIGURED]`) — never guess `Jolt` for 2D or `Forward+` for Web. For Godot `Both`, write `language: "GDScript"` (primary gameplay); for Unreal, `"C++"` unless Blueprint-primary.

### `specialists` Block

| Engine / Language | `code` | `shader` | `ui` | `additional` |
|---|---|---|---|---|
| Godot — GDScript | `godot-gdscript-specialist` | `godot-shader-specialist` | `godot-specialist` | `["godot-gdextension-specialist"]` |
| Godot — C# | `godot-csharp-specialist` | `godot-shader-specialist` | `godot-specialist` | `["godot-gdextension-specialist"]` |
| Godot — Both | `godot-gdscript-specialist` | `godot-shader-specialist` | `godot-specialist` | `["godot-csharp-specialist", "godot-gdextension-specialist"]` |
| Unity | `unity-specialist` | `unity-shader-specialist` | `unity-ui-specialist` | `["unity-dots-specialist", "unity-addressables-specialist"]` |
| Unreal | `unreal-specialist` | `unreal-specialist` | `ue-umg-specialist` | `["ue-gas-specialist", "ue-blueprint-specialist", "ue-replication-specialist"]` |

### `naming` Block

| Field | Godot GDScript | Godot C# | Unity | Unreal |
|---|---|---|---|---|
| `classes` | `PascalCase` | `PascalCase` | `PascalCase` | `PascalCase` |
| `variables` | `snake_case` | `camelCase` | `camelCase` | `PascalCase` |
| `constants` | `SCREAMING_SNAKE` | `PascalCase` | `SCREAMING_SNAKE` *(# UNVERIFIED)* | `SCREAMING_SNAKE` *(# UNVERIFIED)* |
| `signals` | `past_tense` | `on_event_name` | `On<Event>` | `On<Event>` |
| `files` | `snake_case` | `PascalCase` | `PascalCase` | `PascalCase` |
| `scenes` | `snake_case` | `PascalCase` | `PascalCase` | `PascalCase` |

*(For Unreal, note mandatory `U`/`A`/`F`/`E`/`I`/`T` type prefixes in coding standards; `scenes` maps to Levels/Maps. For Godot `Both`, use GDScript row in `project.yaml` and apply per-file rules from `A2`.)*

### `commands` Block & YAML Quoting Rule

| Engine | `build` *(ASK — never guess)* | `test` | `run` *(windowed game, never editor/headless)* | `smoke` |
|---|---|---|---|---|
| Godot | `godot --headless --export-debug '<PRESET>'` | `godot --headless --script tests/gdunit4_runner.gd` | `godot --path . --windowed --resolution 1280x720` | `godot --headless --quit-after 5` |
| Unity | `Unity -batchmode -quit -projectPath . -buildTarget <TARGET>` | `Unity -runTests -projectPath . -testPlatform PlayMode` | `Builds/<Target>/<Game>.exe -screen-width 1280 -screen-height 720 -screen-fullscreen 0` | `Unity -batchmode -quit -projectPath . -executeMethod SmokeCheck.Run` |
| Unreal | `'RunUAT.bat BuildCookRun -project=<project>.uproject -platform=Win64 -build -cook'` | `'UnrealEditor-Cmd.exe <project>.uproject -ExecCmds="Automation RunTests <project>; Quit" -unattended -nullrhi'` | `'UnrealEditor.exe <project>.uproject -game -windowed -ResX=1280 -ResY=720'` | `'UnrealEditor-Cmd.exe <project>.uproject -game -nullrhi -unattended -ExecCmds="Quit"'` |

- Ask operator for `<PRESET>` / `<TARGET>`; if no presets exist yet, write `[TO BE CONFIGURED]`.
- Keep `-game` on Unreal `smoke` and `; Quit` inside Unreal `test` so headless runs exit.
- **YAML quoting rule**: Never use escaped quotes (`\"` or `''`) inside `project.yaml` scalars. Wrap strings containing `'` in double quotes (`"..."`), and strings containing `"` in single quotes (`'...'`). Never mix both quote styles in one value.

## 6. Knowledge Gap & Reference Docs

Check the pinned version against the reference cutoff table in `docs/engine-reference/<engine>/VERSION.md` (or treat any cutoff >6 months unverified as `HIGH RISK`).

- **Existing directory pins older version**: Update in place (preserve older version spans under `## <old> -> <new>` headings in `breaking-changes.md`, `deprecated-apis.md`, `current-best-practices.md`; update `VERSION.md` fields and `Installed at pin time`).
- **Existing directory pins newer version**: Stop and ask before downgrading.
- **Sourcing rule**: Every claim must come from fetched official docs with URL recorded; never fill gaps from training data — write `NOT SOURCEABLE — <what>, not stated at <url>`.

## 7. Scaffold Project Files & Coherence Check

- **Godot**: If `project.godot` is absent, confirm creation (`config_version=5`, `[application]` name + `PackedStringArray("<major.minor>", "<renderer feature>")`, `[rendering]` method, leave `run/main_scene` unset). Run `godot --headless --path . --import` if binary matches, else record `project.godot NOT VERIFIED — <reason>`. Never overwrite an existing `project.godot`.
- **Unity / Unreal**: Instruct operator to initialize the editor-generated project (`Unity Hub` / `UnrealEditor`) rather than fabricating `.uproject` or `ProjectSettings/`.
- Run `python .ags/cli.py check coherence` after writes. Resolve every `[DIFFERS]` line and report every `[NOT CHECKED]` line explicitly (`[NOT CHECKED]` is not agreement).

## 8. Tiered Handoff

- **`minimal` (`modes.workflow`)**: 1. `ags-ideate` (`design/game-brief.md`) -> 2. `ags-plan` (stories) -> 3. `ags-dev` (first game code).
- **`standard` / `full`**: `ags-ideate` (if no concept) -> `ags-art-ux` -> `ags-gdd` -> `ags-design-review` -> `ags-architect`.

## 9. Refresh Subcommand (`ags-settings engine refresh`)

1. Read `docs/engine-reference/<engine>/VERSION.md`.
2. Search official docs for new patch/minor releases, migration guides, and newly deprecated APIs.
3. Append verified updates, update `Last Docs Verified` dates on modified files only, and summarize changes.

## 10. Upgrade Subcommand (`ags-settings engine upgrade [old] [new]`)

1. Read `VERSION.md` (default `old` to pinned version), fetch official migration guide & breaking changes between `old` and `new`.
2. Resolve code root (`src/` Godot, `Assets/` Unity, `Source/` Unreal; report `NOT ASSESSED` if unresolved) and search source files for deprecated/removed APIs extracted from the guide.
3. Present Pre-Upgrade Audit table (File | Deprecated API | Effort), breaking changes, and dependency-sorted migration order.
4. Confirm with user before updating `VERSION.md`, appending `breaking-changes.md` / `deprecated-apis.md`, and syncing `engine.version` in `project.yaml` (source files are migrated separately via stories).
5. Recommend: migrate listed usages -> `ags-settings engine refresh` -> `ags-arch-review` -> `ags-design-review propagate` if ADRs change.
