# Smoke Check (`ags-qa smoke-check`)

Critical-path build health gate between implementation completion and QA hand-off. A build that fails a blocking smoke check does not proceed to QA.

**Output:** `production/qa/smoke-[date].md`

---

## Policy Axes & Arguments

- **`qa.level`**: `minimal` makes smoke check optional and FAIL advisory (never blocks hand-off); `standard` requires it before phase transitions; `full` requires it before every commit.
- **`testing.strict.config`** (resolved by `preflight` when `qa.level` is `standard` or `full`):
  1. Check `testing.strict.config` (`true` -> blocking, `false` -> advisory; any value other than `true`/`false` is treated as unset and surfaced to the user).
  2. Else check plain boolean `testing.strict`.
  3. Else default to **blocking** (build-health gate strict default).
  - Note: `NOT ASSESSED` is **never** governed by `testing.strict.config` — an unrun check cannot become advisory-fine.
- **Arguments**: `sprint` (default) or `quick` (skip Phase 3 coverage scan and Phase 4 Batch 3), optionally paired with `--platform pc | console | mobile | all`.

---

## Phase 1: Detect Test Setup & Config Coherence

1. **Config coherence (run first)**:
   ```bash
   python .ags/cli.py check coherence
   ```
   Include all `[DIFFERS]` lines in the report's Environment section so mismatched `engine.version`, rendering, or `commands.*` presets are surfaced immediately.
2. **Verify actual game test files exist**:
   Search `tests/unit/`, `tests/integration/`, and `tests/smoke/` for real test files (do **not** gate on `tests/` directory existence alone, because `ags-qa test-setup` creates placeholder files).
   If zero game test files exist, **deliver verdict `NOT ASSESSED — no game tests found`** under `tests/{unit,integration,smoke}` and stop, routing to `ags-qa test-setup`.
3. **Inspect CI, engine, smoke checklist, and QA plan**:
   - Check `.github/workflows/` for test workflows.
   - Read `engine.name` from `preflight` (`project.yaml` plus legacy technical-preferences fallback if present).
   - Locate `production/qa/smoke-tests.md` or `tests/smoke/`.
   - Locate most recent `production/qa/qa-plan-*.md`.
   - Report: `"Environment: [engine]. Game tests: [N]. CI configured: [yes / no]. QA plan: [path / not found]."`

---

## Phase 2: Run Automated Tests

Run headless tests according to the resolved engine:

- **Godot 4**:
  `godot --headless --script tests/gdunit4_runner.gd` (fallback `godot --headless -s addons/gdunit4/GdUnitRunner.gd`).
- **Unity**:
  First verify `com.unity.test-framework` exists in `Packages/manifest.json` (projects missing it hang rather than failing cleanly). If absent, report **`NOT ASSESSED — Unity Test Framework not installed`** with fix (`add com.unity.test-framework to Packages/manifest.json`) and stop without reading stale `test-results/` XML.
  If present, execute with explicit timeout:
  `timeout 900 "<Unity.exe>" -batchmode -runTests -projectPath . -testPlatform EditMode -testResults test-results/results.xml`
  Parse `<test-run>` `passed` and `failed` attributes. **Exit code 124 (timeout) is a gate `FAIL`.**
- **Unreal Engine**:
  Check `Saved/Logs/` for recent automation test logs (`test` / `automation`). If none found, record `NOT RUN` and prompt manual confirmation from Session Frontend or CI.
- **Unconfigured engine**: Stop and direct to `ags-settings`.
- **Missing runner / binary**: Record `NOT RUN — [reason]`. Never treat `NOT RUN` as automatic `FAIL` or as a pass — it resolves to `NOT ASSESSED` until the developer confirms IDE/CI test results in Phase 4.

Extract total run, passing count, failing count, failing test names (up to 10 plus overflow count), and runner errors/crashes.

---

## Phase 3: Check Test Coverage (skip in `quick` mode)

Load stories from the latest `qa-plan-*.md` (else latest `production/sprints/` file). For each story, match `tests/{unit,integration}/[system]/` and story `Test file:` / `## Test Evidence`:
- `COVERED`: matching automated test file found
- `MANUAL`: `Visual/Feel` or `UI` story with evidence doc in `production/qa/evidence/`
- `MISSING`: `Logic` or `Integration` story lacking a test file (advisory gap; blocks `ags-verify` closure)
- `EXPECTED`: `Config/Data` story
- `UNKNOWN`: story file missing or unreadable (forces `NOT ASSESSED` verdict)

---

## Phase 4: Manual Smoke Batches

Select checklist source in priority order and **print `Checklist source: <path or standard fallback>` in the report**:
1. QA plan `## Smoke Test Scope`
2. `production/qa/smoke-tests.md`
3. `tests/smoke/` contents
4. Standard fallback list below

Prompt the user in at most 3 batched checks (plus `--platform` batches if requested) tailored to the sprint's mechanics, collecting failure descriptions for any failed item:
- **Batch 1 — Core stability (always)**: launch to main menu without crash, new game/session starts, main menu responds to inputs, no crash/hang in basic navigation.
- **Batch 2 — Sprint changes & regression (always)**: primary sprint mechanic(s), prior sprint features, unexpected breakage.
- **Batch 3 — Data integrity & performance (skip in `quick`)**: save/load integrity (or N/A if unimplemented), frame rate stability, or `"Performance not checked this session"`.
- **Platform batches (`--platform pc|console|mobile|all`)**:
  - **PC**: keyboard controls, mouse/cursor visibility, windowed/fullscreen toggle, resolution change.
  - **Console**: gamepad input, TV safe zone / text clipping, no KB/M fallback shown to gamepad user, cold start (no prior save).
  - **Mobile**: touch controls, portrait/landscape orientation change, background/foreground resume, thermal/performance throttling.

---

## Phase 5: Report & Verdict Rules

Generate the report with `Environment` (including `[DIFFERS]`), `Checklist source`, `Automated Tests`, `Test Coverage`, `Manual Smoke Checks`, `Missing Test Evidence`, `Platform-Specific Results` (when `--platform` used), and Verdict:

**First matching verdict wins:**
1. **`FAIL`**: Automated tests failed or timed out (exit 124), OR any Batch 1/Batch 2 check failed, OR any `--platform` check failed.
2. **`NOT ASSESSED`**: Automated suite is unconfirmed `NOT RUN`, OR any Batch 1/2 check could not execute (no build, unconfigured engine, unavailable platform), OR any Phase 3 coverage row is `UNKNOWN`, OR Batch 3 was offered and skipped (`"Performance not checked this session"`).
3. **`PASS WITH WARNINGS`**: Automated tests pass (or `NOT RUN` explicitly confirmed passing in IDE/CI), all Batch 1/2 checks pass, and >=1 story has `MISSING` test evidence.
4. **`PASS`**: Automated tests pass, all smoke batches pass or N/A, and zero `MISSING` entries.

---

## Phase 6: Write & Gate

Present the report and confirm writing `production/qa/smoke-[date].md` per `modes.automation`. Deliver the gate decision:
- **`FAIL` (blocking)**: Do not hand off to QA; list failures and re-run `ags-qa smoke-check`.
- **`FAIL` (advisory via `qa.level: minimal` or `testing.strict.config: false`)**: Log failures and proceed to manual QA (`ags-qa qa-plan` hand-off), resolving before release.
- **`NOT ASSESSED`**: Do not hand off to QA; list each unexecuted check, why it did not run, and the exact action required to make it runnable (`confirm IDE/CI result`, `run ags-settings`, `produce build`).
- **`PASS` / `PASS WITH WARNINGS`**: Ready for manual QA; surface any `MISSING` items to resolve before `ags-verify`. Never edit game source or test files inside `smoke-check`.
