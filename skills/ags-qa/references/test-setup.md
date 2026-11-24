# Test Setup (`ags-qa test-setup`)

Scaffolds the automated testing framework, directory layout, smoke seed, and CI workflow once during Technical Setup before sprint implementation begins.

**Output:** `tests/` directory tree, `production/qa/evidence/`, and `.github/workflows/tests.yml`

---

## Phase 1: Detect Engine and Existing State

1. **Read engine config** (from `python .ags/cli.py preflight ags-qa test-setup`):
   - Use `engine.name` from `project.yaml` (or legacy technical-preferences fallback reported by preflight) if absent or empty.
   - If neither source configures an engine (missing or `[TO BE CONFIGURED]`), stop:
     `"Engine not configured. Run ags-settings first, then re-run ags-qa test-setup."`
2. **Inspect existing test infrastructure**:
   - Check whether `tests/`, `tests/unit/`, `tests/integration/`, `.github/workflows/`, and engine test artifacts (`tests/gdunit4_runner.gd` for Godot, `tests/EditMode/` for Unity, `Source/Tests/` for Unreal) exist.
3. **Report findings**:
   - `"Engine: [engine]. Test directory: [found / not found]. CI workflow: [found / not found]."`
   - If all expected files exist and `force` was not passed:
     `"Test infrastructure appears to be in place. Re-run with 'ags-qa test-setup force' to create any missing files. Existing test files will not be overwritten."`
   - With `force`, skip the early exit and create missing files only — never overwrite existing files at any path.

---

## Phase 2: Present Plan & Approval

Present the planned files before writing:

```text
## Test Setup Plan — [Engine]

Create the following (skipping any paths that already exist):

tests/
  unit/           — Isolated unit tests for formulas, state, and logic
  integration/    — Cross-system tests and save/load round-trips
  smoke/          — Critical path test list (15-minute manual gate)
  README.md       — Test framework documentation

production/qa/
  evidence/       — Screenshot and manual test sign-off records

[Engine-specific files]
.github/workflows/tests.yml  — CI: run tests on every push to main
```

Prompt: `"Approve creating these missing test setup files? Existing test files will not be overwritten."`
- `collaborative` / `guided`: Wait for explicit approval (new files require confirmation in both modes).
- `autonomous`: Create files and log the decision to `production/session-logs/decision-log.md`.

---

## Phase 3: Create Directory Structure

### `tests/README.md`

Manual evidence lives under `production/qa/evidence/`, never `tests/evidence/`, matching `ags-qa`, `ags-verify`, and `.ags/rules/test-standards.md`.

```markdown
# Test Infrastructure

**Engine**: [engine name + version]
**Test Framework**: [GdUnit4 | Unity Test Framework | UE Automation]
**CI**: `.github/workflows/tests.yml`
**Setup date**: [date]

## Directory Layout

tests/
  unit/           # Isolated unit tests (formulas, state machines, logic)
  integration/    # Cross-system and save/load tests
  smoke/          # Critical path test list for ags-qa smoke-check gate

production/qa/
  evidence/       # Screenshot logs and manual test sign-off records

## Running Tests

[Engine-specific command]

## Test Naming

- **Files**: `[system]_[feature]_test.[ext]`
- **Functions**: `test_[scenario]_[expected]`
- **Example**: `combat_damage_test.gd` -> `test_base_attack_returns_expected_damage()`

## Story Type -> Test Evidence

| Story Type | Required Evidence | Location |
|---|---|---|
| Logic | Automated unit test — must pass | `tests/unit/[system]/` |
| Integration | Integration test OR playtest doc | `tests/integration/[system]/` |
| Visual/Feel | Screenshot + lead sign-off | `production/qa/evidence/` |
| UI | Manual walkthrough OR interaction test | `production/qa/evidence/` |
| Config/Data | Smoke check pass | `production/qa/smoke-*.md` |

## CI

Tests run automatically on every push to `main` and on every pull request. A failed test suite blocks merging.
```

### Engine-Specific Files

#### Godot 4 (`Engine: Godot`)
Create `tests/gdunit4_runner.gd`:

```gdscript
# GdUnit4 test runner — invoked by CI and ags-qa smoke-check
# Usage: godot --headless --script tests/gdunit4_runner.gd
extends SceneTree

func _init() -> void:
    var runner := load("res://addons/gdunit4/GdUnitRunner.gd")
    if runner == null:
        push_error("GdUnit4 not found. Install via AssetLib or addons/.")
        quit(1)
        return
    var instance = runner.new()
    instance.run_tests()
    quit(0)
```

Create placeholder files `tests/unit/.gdignore_placeholder` and `tests/integration/.gdignore_placeholder`. Document GdUnit4 installation in `tests/README.md`:
1. Open Godot -> AssetLib -> search `GdUnit4` -> Download & Install
2. Project -> Project Settings -> Plugins -> enable `GdUnit4`
3. Restart editor and verify `res://addons/gdunit4/` exists

#### Unity (`Engine: Unity`)
- Create `tests/EditMode/README.md` (unit tests without Play Mode; requires `tests/EditMode/EditModeTests.asmdef`).
- Create `tests/PlayMode/README.md` (integration tests in a game scene; requires `tests/PlayMode/PlayModeTests.asmdef`).
- Document enabling via `Window -> General -> Test Runner`.

#### Unreal Engine (`Engine: Unreal` / `UE5`)
- Create `Source/Tests/README.md` documenting UE Automation (`Session Frontend -> Automation` or `UnrealEditor -nullrhi -ExecCmds="Automation RunTests MyGame.; Quit"`), test class `F[SystemName]Test`, and category `"MyGame.[System].[Feature]"`.

---

## Phase 4: Create CI/CD Workflow (`.github/workflows/tests.yml`)

- **Godot 4**: `actions/checkout@v4` (`lfs: true`), `MikeSchulze/gdUnit4-action@v1` (`godot-version` pinned from `docs/engine-reference/godot/VERSION.md`, `paths: tests/unit, tests/integration`, `report-name: test-results`), `actions/upload-artifact@v4` (`path: reports/`, `if: always()`).
- **Unity**: `actions/checkout@v4` (`lfs: true`), `game-ci/unity-test-runner@v4` jobs for `editmode` and `playmode` (`UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}`), `actions/upload-artifact@v4` (`path: test-results/`). Note that `UNITY_LICENSE` must be configured manually in GitHub repository secrets.
- **Unreal**: `runs-on: self-hosted`, runs `"$UE_EDITOR_PATH" "${{ github.workspace }}/[ProjectName].uproject" -nullrhi -nosound -ExecCmds="Automation RunTests MyGame.; Quit" -log -unattended`, uploads `Saved/Logs/`. Requires local runner with `UE_EDITOR_PATH` set.

---

## Phase 5: Create Smoke Test Seed (`tests/smoke/critical-paths.md`)

Seed 8 critical-path checks run by `ags-qa smoke-check` in under 15 minutes:
1. Game launches to main menu without crash
2. New game / session can be started from the main menu
3. Main menu responds to all inputs without freezing
4. `[Primary mechanic — update when first core system is implemented]`
5. Save game completes without error (once save system exists)
6. Load game restores correct state (once load system exists)
7. No visible frame rate drops on target hardware (60fps target)
8. No memory growth over 5 minutes of play (once core loop is implemented)

---

## Phase 6: Post-Setup Summary

Report created files and next steps:
1. Complete engine install step (e.g., install GdUnit4 or add `UNITY_LICENSE`).
2. Create first test at `tests/unit/[first-system]/[system]_test.[ext]` (`ags-gate` Technical Setup -> Pre-Production requires `tests/unit/`, `tests/integration/`, `.github/workflows/tests.yml`, and at least one example test file).
3. Run `ags-qa qa-plan sprint` before the first sprint and `ags-qa smoke-check` before QA hand-off.
4. Verdict: **`COMPLETE`** (or **`BLOCKED`** if engine unconfigured or approval declined).
