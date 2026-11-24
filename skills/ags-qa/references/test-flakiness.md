# Test Flakiness Detection (`ags-qa test-flakiness`)

Identifies tests that pass and fail intermittently without code changes across CI or local test runs, diagnoses root causes, recommends quarantine vs. immediate fix, and updates `tests/regression-suite.md`.

**Output:** Updated `tests/regression-suite.md` quarantine section + optional `production/qa/flakiness-report-[date].md`

---

## 1. Parse Modes

- `[ci-log-path]`: analyze one specified log or XML artifact
- `scan`: scan `.github/`, `test-results/`, or `Saved/Logs/` for result history
- `registry`: review already-quarantined tests in `tests/regression-suite.md` and propose fixes
- Blank: run `scan` if log history exists, else `registry`

---

## 2. Locate & Parse Test History

Check engine/CI artifacts:
- **Godot 4 / Unity**: JUnit / NUnit `.xml` files in `test-results/` (extract `<testcase classname=... name=...>` and `<failure>` / `<error>`).
- **Unreal Engine**: `Saved/Logs/` matching `Result: Success` / `Result: Fail`.
- **Plain text logs**: Godot `PASSED` / `FAILED`, Unity `Test passed` / `Test failed`.

Build a per-test matrix: `test_id -> [run1_result, run2_result, run3_result, ...]`.

If **no log data** is available (and mode is not `registry`), stop with **`NOT ASSESSED — no CI log history found`** and prompt the user to choose:
1. Run the test suite at least 3 times and save logs
2. Save CI output into `test-results/`
3. Switch to `ags-qa test-flakiness registry`

---

## 3. Identify & Classify Flaky Tests

A test is **flaky** when it records both PASS and FAIL across runs with no intervening code change.

- **High flakiness (`>25%` fail rate)**: Quarantine immediately (`@pytest.mark.skip`, `[Ignore]`, `GdUnitSkip`) and log in `tests/regression-suite.md`.
- **Moderate flakiness (`5–25%` fail rate)**: Investigate and fix directly; do not quarantine yet.
- **Low / suspected flakiness (`1–5%` fail rate, or `< 3` runs)**: Mark **`suspected`** (`NOT ASSESSED` for confirmed flakiness until >= 3–5 runs accumulate).

### Cause Classification
Inspect matching test files for timing/async calls, RNG, global state, or exact float comparisons:

| Cause | Symptoms | Fix Direction |
|---|---|---|
| **Timing / async** | Fails awaiting signals/timers under load | Explicit await/sync; eliminate fixed sleeps |
| **Order dependency** | Passes alone, fails after specific tests | Enforce setup/teardown isolation |
| **Random seed** | Intermittent with no pattern | Inject deterministic seed; ban `randf()` in tests |
| **Resource leak** | Fails later in long runs | Dispose objects / free Godot orphan nodes in teardown |
| **External state** | Sensitive to leftover files/globals | Isolate with in-memory fakes or temp dirs |
| **Floating point** | Exact equality like `== 0.5` fails | Use epsilon compare (`is_equal_approx`, `Assert.AreApproximately`) |
| **Scene/prefab load race** | Node/component missing right after spawn | Wait one frame (`await get_tree().process_frame`) |

---

## 4. Report, Quarantine & Follow-Up

1. Present in-conversation summary: Runs analyzed (flag `< 5` runs under `Data Limitations`), Tests tracked, Flaky Tests table (`Test | System | Fail Rate | Likely Cause | Recommendation`), Clean Tests count.
2. Ask per `modes.automation` before updating the `## Quarantined Tests` table in `tests/regression-suite.md` (append-only; **never delete test files** and never remove existing quarantine rows silently).
3. Separately ask per `modes.automation` before writing `production/qa/flakiness-report-[date].md` with per-test root cause and engine-specific fix snippets.
4. Verdict: **`COMPLETE`** once updates/report approved (`BLOCKED` if write declined; **`NOT ASSESSED`** if `< 3` runs or zero logs found). Remind the team to schedule fixes for quarantined tests before `ags-gate` release readiness.
