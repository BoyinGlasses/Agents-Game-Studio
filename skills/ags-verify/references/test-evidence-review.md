# Test & Evidence Quality Audit (`ags-verify` Evidence Mode)

Audits whether automated tests and manual visual/playtest evidence documents genuinely verify story behavior rather than passing vacuously. Strictly read-only on source, tests, and evidence docs; optional persistent report write only with user approval.

## 1. Scope & Zero-Scope Guard

Accept one of: `[story-path]`, `sprint` (most recent file in `production/sprints/`), `[system-name]` (`production/epics/[system-name]/story-*.md`), or ask user if omitted.

**Zero-scope guard**: If resolved scope contains zero stories, STOP and emit `NOT ASSESSED — no stories in scope`, naming the exact searched path/glob and remediation (`ags-plan`). Distinguish absent sprint file from empty story list. Never render `BLOCKING items: 0 / ADVISORY items: 0` over an empty set.

Collect `## Test Evidence` and `## Acceptance Criteria` via targeted section scans first; read whole story files only if those sections are missing or ambiguous.

## 2. Locate Evidence & Evaluate Quality

Locate per story type:
- **Logic**: `tests/unit/[system]/[story-slug]_test.*` (fallback search for slug in `tests/unit/[system]/`)
- **Integration**: `tests/integration/[system]/[story-slug]_test.*` + `production/session-logs/` playtest records
- **Visual/Feel & UI**: `production/qa/evidence/[story-slug]-evidence.*` + retained images (`*.png`, `*.jpg`, `*.gif`)
- **Config/Data**: `production/qa/smoke-*.md`

### Automated Test Quality (`Logic` / `Integration`)
- **Assertion coverage**: Count distinct assertions (`assert`, `expect`, `check`, `verify`, engine assertions).
  - `3+` per test function -> adequate
  - `1–2` per test function -> thin (ADVISORY)
  - `0` assertions -> **BLOCKING** (vacuous pass)
- **Edge case coverage**: Check that numeric bounds, thresholds, and conditional `"when X"` criteria map to boundary checks (`zero`, `min`, `max`, `null`, `empty`, `invalid`, `boundary`, `edge`, formula min/max).
- **Naming quality**: Require `test_[scenario]_[expected_outcome]`; flag generic names (`test_1`, `test_run`, `testBasic`).
- **Formula traceability**: If GDD has `## Formulas`, verify tests reference the formula name or value.

### Manual Evidence Quality (`Visual/Feel` / `UI`)
- **Criterion linkage**: Every story AC must appear in the evidence doc (`.ags/templates/test-evidence.md`).
- **Sign-off completeness**: Check Developer, Designer/Art-Lead/UX-Lead, and QA Lead sign-off rows (`[x] Approved`). Unchecked rows -> `INCOMPLETE`.
- **Screenshot / walkthrough completeness**: Retained image file (`*.png`/`*.jpg`/`*.gif`) must exist on disk beside the doc or in `production/qa/evidence/[story-slug]/`; UI stories also require a step-by-step interaction walkthrough. Missing image -> `INCOMPLETE` (BLOCKING by default).
- **Freshness**: Evidence date predating last major story/sprint update -> flag `POTENTIALLY STALE`.

## 3. Verdict Precedence & Report

**Per-story and aggregate verdict precedence**: `MISSING` / `INCOMPLETE` > `NOT ASSESSED` > `ADEQUATE`.
- **ADEQUATE**: Required tests/evidence exist, pass quality checks, cover criteria, and have complete sign-offs.
- **INCOMPLETE**: Evidence exists with thin assertions, missing sign-offs, or missing retained image.
- **MISSING**: No test or evidence found for a required type.
- **NOT ASSESSED**: Story type cannot be determined, named evidence path is unreadable/outside scope, or story file cannot be parsed. Always state the exact reason per story; never collapse unknowns into `MISSING` or `ADEQUATE`.

Present the story-by-story report and summary table (`Story | Type | Verdict | Issues`, plus `BLOCKING` / `ADVISORY` / `NOT ASSESSED` counts). Offer to save to `production/qa/evidence-review-[date].md` only if the user wants a persistent record (respecting `modes.automation`), and route thin assertions to `ags-qa` (`test-helpers`) or resolved items to `ags-verify` closure.
