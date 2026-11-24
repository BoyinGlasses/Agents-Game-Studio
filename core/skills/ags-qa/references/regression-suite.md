# Regression Suite (`ags-qa regression-suite`)

Maintains `tests/regression-suite.md` — a curated manifest of critical-path and bug-fix regression tests in `tests/` — and detects coverage drift as systems and bugs evolve.

**Output:** `tests/regression-suite.md`

---

## 1. Early `qa.level` Guard & Modes

**Check `qa.level` from `preflight` FIRST (before any scan):**
- If `qa.level: minimal`: emit `"Regression suite not generated at qa.level: minimal"` and **STOP immediately in every mode** (`update`, `audit`, `report`). Do not conflate this with the `workflow: minimal` critical-path source branch in Step 2c.
- `qa.level: standard`: generate at Polish-stage entry.
- `qa.level: full`: generate at Production-stage entry.

**Modes:**
- `update`: inspect completed sprint stories and closed bugs; append newly required regression tests.
- `audit`: audit all critical paths (per workflow tier) vs. test coverage and rewrite the manifest.
- `report`: read-only status report (no writes).
- Blank: auto-select `update` if an active sprint plan has in-progress stories; otherwise prompt the user to pick `update`, `audit`, or `report`.

---

## 2. Load Context

- **2a. Existing manifest**: Read `tests/regression-suite.md` if present (extract registered count, last updated date, `STALE` / `QUARANTINED` entries).
- **2b. Test inventory**: List files under `tests/unit/**/*_test.*`, `tests/integration/**/*_test.*`, and `tests/regression/**/*` (note system from path; avoid full-reading test bodies unless needed for mapping).
- **2c. Critical-path source**:
  - In `audit` mode, read `design/gdd/systems-index.md` and resolve `modes.workflow` + `workflow_overrides.system_overrides.<stem>` per GDD stem:
    - `full`: map critical paths from all 8 GDD sections.
    - `standard`: map from **Acceptance Criteria**, **Edge Cases**, and **Formulas** (where numeric rules exist). Systems overridden to `full` use all 8 sections.
    - `minimal`: **skip GDD scan**; read the latest `production/qa/smoke-*.md` report and use its exercised critical paths instead. If no smoke report exists, stop and emit **`NOT ASSESSED — no smoke report found at workflow: minimal`** (route to `ags-qa smoke-check`).
  - In `update` mode, read the active sprint plan and stories marked `Status: Complete`.
- **2d. Closed bugs**: Scan `production/qa/bugs/*.md` for `Status: Closed` or `Status: Fixed`, recording affected system and whether a regression test was noted.

---

## 3. Map Coverage & Detect Drift

1. **Critical paths (`audit` mode)**: Search `tests/{unit,integration}/[system]/` for matching test files/functions:
   - `COVERED`: targets criterion logic
   - `PARTIAL`: happy-path only
   - `MISSING`: no test found (elevate formulas and state machines to **`HIGH PRIORITY`**)
   - `EXEMPT`: `Visual/Feel` or `UI` criterion (not automatable)
2. **Fixed bugs**: Check `tests/{unit,integration}/[system]/` for tests referencing each bug ID or failure scenario -> `HAS REGRESSION TEST` or `MISSING REGRESSION TEST` (suggest `tests/unit/[system]/[bug-slug]_regression_test.[ext]`).
3. **Coverage drift**: Flag stories completed this sprint lacking test files, new systems in `systems-index.md`, GDD sections modified since manifest `Last Updated`, or manifests untouched for >2 sprints (`STALE`).

---

## 4. Denominator Check & Report Format

**Check the denominator before computing any coverage percentage:**
- If the critical-path source yields **zero critical paths**, OR test discovery finds **zero test files**, do **not** emit `0%` or `100%`. Emit:
  `Coverage: NOT ASSESSED — [no GDD critical paths found | no smoke report found | no test files found]`
  and name the skill that produces the empty side (`ags-gdd` for GDDs, `ags-qa test-setup` for tests, `ags-qa smoke-check` for smoke reports).

Write `tests/regression-suite.md` containing:
- Header (`Last Updated`, `Total registered tests`, `Coverage` percentage or `NOT ASSESSED`)
- `## How to run` (engine command)
- `## Registered Regression Tests` (grouped by system: `Test File | Test Function | Covers | Added`)
- `## Known Gaps` (`Priority | System | Suggested Path | Covers | Reason Not Yet Written`)
- `## Quarantined Tests` (`Test File | Function | Reason | Quarantined Since`)

---

## 5. Write & Follow-Up

- Ask approval per `modes.automation` before modifying `tests/regression-suite.md` (`report` mode writes nothing).
- In `update` mode, append new entries only — never delete existing registered or quarantined tests without explicit user approval.
- Route flaky/intermittent tests to `ags-qa test-flakiness` for quarantine rather than deletion, `HIGH` gaps to `ags-qa test-helpers` / sprint backlog, and drift to periodic `ags-qa regression-suite audit`.
