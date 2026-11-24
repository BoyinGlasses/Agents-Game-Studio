# Test Helpers (`ags-qa test-helpers`)

Generates engine-specific test assertion, factory, and scene helpers under `tests/helpers/` matched to the project's existing test conventions and GDD bounds.

**Output:** `tests/helpers/` library files

---

## Mandatory Framework & Safety Rules

1. **Always assert through the configured test framework API, never bare `assert()`**:
   - Bare `assert()` aborts execution on the first failure (hiding subsequent test results in the suite).
   - Bare `assert()` is stripped in release builds, silently making tests pass when assertions stop executing.
   - Verify the exact assertion call for `testing.framework` against project test files or `docs/engine-reference/` before generating code. **If the framework assertion call cannot be confirmed, state the gap (`NOT ASSESSED`) and generate no helper rather than guessing.**
2. **Helpers must never extend the test-suite base class**:
   - Files in `tests/helpers/` that extend the suite runner base class (e.g., `GdUnitTestSuite`) are discovered as empty test suites containing zero tests. Keep helpers as plain utility classes (`RefCounted`, static C# class, C++ namespace/macros).

---

## 1. Parse Arguments & Engine

**Modes:**
- `[system-name]`: generate `tests/helpers/[system]_factory.[ext]` for one system
- `all`: generate helpers for all systems with test files
- `scaffold`: generate base helper library only (default if no helpers exist yet)
- Blank: run `scaffold` if `tests/helpers/` has no files, else `all`

Resolve `engine.name`, `engine.language`, and `testing.framework` from `python .ags/cli.py preflight ags-qa test-helpers` (`project.yaml` plus legacy technical-preferences fallback if present). Stop and direct to `ags-settings` if unconfigured.

---

## 2. Sample Existing Conventions & Design Inputs

- Scan up to 5 existing test files matching `tests/**/*_test.*` to extract setup (`before_each`/`setUp`), assertion style, scene/object instantiation, and mock/stub conventions.
- Read `design/gdd/systems-index.md` and `docs/architecture/tr-registry.yaml` to map systems and requirements.

---

## 3. Generate Engine-Specific Base Helpers

### Godot 4 (GDScript)

> **`FAIL_IF(...)` below is a placeholder, not a real API.** Resolve `testing.framework`'s failure call that registers a failure with the runner without halting the suite before writing disk files, and replace `FAIL_IF`. If the framework API is not confirmed in project files or `docs/engine-reference/` (note `docs/engine-reference/godot/` does not cover GdUnit4), generate **no helper**. Never write unresolved `FAIL_IF` or bare `assert()` to disk.

- **Base assertions (`tests/helpers/game_assertions.gd`)**: `class_name GameAssertions extends RefCounted` with static helpers:
  - `assert_in_range(value: float, min_val: float, max_val: float, label: String = "value")`
  - `assert_signal_emitted(obj: Object, signal_name: String, action: Callable)`
  - `assert_signal_not_emitted(obj: Object, signal_name: String, action: Callable)`
  - `assert_node_exists(parent: Node, path: NodePath)`
- **Factory (`tests/helpers/game_factory.gd`)**: `class_name GameFactory extends RefCounted` with `make_player(health: int = 100) -> Node` setting minimal metadata without requiring a scene tree.
- **Scene helper (`tests/helpers/scene_runner_helper.gd`)**: `class_name SceneRunnerHelper extends RefCounted` accepting a host `parent: Node` (`load_scene_and_wait(parent: Node, scene_path: String) -> Node`, calling `parent.add_child(scene)` and `await parent.get_tree().process_frame`) so it does not extend `GdUnitTestSuite`.

### Unity (NUnit / C#)

- **`tests/helpers/GameAssertions.cs`**: static class using `NUnit.Framework` (`Assert.That(value, Is.InRange(min, max))`, `AssertEventRaised(ref bool wasCalled, System.Action action, string eventName)`, `AssertHasComponent<T>(GameObject obj)`).
- **`tests/helpers/GameFactory.cs`**: `MakeGameObject(string name)` and `MakeScriptableObject<T>()` (caller disposes via `Object.DestroyImmediate`).

### Unreal Engine (C++)

- **`tests/helpers/GameTestHelpers.h`**: includes `"CoreMinimal.h"` and `"Misc/AutomationTest.h"`; defines macros `GAME_TEST_ASSERT_IN_RANGE`, `GAME_TEST_ASSERT_VALID` (`IsValid`), `GAME_TEST_ASSERT_SPAWNED` (`TestNotNull`), plus `GameTestHelpers::CreateTestWorld` (reminder to call `World->DestroyWorld(false)` in teardown).

---

## 4. Generate System-Specific Helpers (`[system-name]` or `all`)

Read only the targeted GDD sections (`## Formulas`, `## Edge Cases`, `## Detailed Rules` / `## Detailed Design`) in `design/gdd/[system].md` rather than full-reading multi-hundred-line GDDs across every system.

Extract entity types, formula bounds/constants, and edge scenarios into `tests/helpers/[system]_factory.[ext]` (e.g., `CombatTestFactory` with `DAMAGE_MIN`, `DAMAGE_MAX` traced to the GDD, `make_attacker`, `make_target`, `assert_damage_in_bounds`).

---

## 5. Write & Verify Output

1. Present the file list (`tests/helpers/...`) and ask approval per `modes.automation`.
2. **Never overwrite existing helpers** — report `"Skipping [path] — already exists. Remove manually to regenerate."`
3. Explain usage per engine (`class_name` auto-imported in Godot; `using` / assembly reference in Unity; `#include "tests/helpers/GameTestHelpers.h"` in Unreal).
4. Next steps: `ags-qa test-setup` (if test directory missing), `ags-dev` (use helpers in story tests), `ags-skill-ops` (skill validation).
