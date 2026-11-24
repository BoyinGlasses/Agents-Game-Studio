# Brownfield Format Audit & Migration Reference (`ags-adopt`)

Audits existing project artifacts for format compatibility with AGS v2 skills, detects legacy v1 config needing migration, and writes a prioritized remediation plan (`docs/adoption-plan-[date].md`).

## Audit Scopes

- No arg / `full`: audit all artifact types
- `gdds`: GDD format compliance only
- `adrs`: ADR format compliance only
- `stories`: story format compliance only
- `infra`: infrastructure artifacts + legacy v1 config check

Audit depth follows resolved `modes.workflow`:
- `full`: audit all artifact types and all sections.
- `standard`: audit required docs/sections only (optional sections are informational).
- `minimal`: audit `design/game-brief.md` format only (do not flag absent GDDs, ADRs, or UX specs).

## Phase 1: Existence Scan

Emit one status line (`"Scanning project artifacts..."`), then silently check:
- `project.stage` in `project.yaml` (fallback `production/stage.txt`); if absent, infer stage using heuristics (10+ files in resolved code root -> `Production`, stories -> `Pre-Production`, ADRs -> `Technical Setup`, `systems-index.md` -> `Systems Design`, `game-concept.md` / `game-brief.md` -> `Concept`, none -> **Fresh**).
- Concept (`design/gdd/game-concept.md` or `design/game-brief.md`), `design/gdd/systems-index.md`, system GDD count (`design/gdd/*.md` excl. non-system docs), ADR count (`docs/architecture/adr-*.md`), story count (`production/epics/**/story-*.md`), engine configuration, `docs/engine-reference/`, and most recent `docs/adoption-plan-*.md`.

If the project is **Fresh** (zero artifacts), offer: `ags-start` / locate non-standard artifact paths / cancel — then stop without running an audit.

## Phase 2: Format Audits

### 2a: GDD Format Audit
Run deterministic section presence checking **one GDD path at a time** (including non-standard brownfield paths found in Phase 1):

```bash
python .ags/cli.py check gdd <path-to-gdd>
```

- If `check gdd` fails to find a path, record `"could not audit <path>"` (discovery error, not missing sections).
- `check gdd` accepts `## Detailed Design` as satisfying `Detailed Rules`.
- Apply resolved `modes.workflow` (plus `workflow_overrides.system_overrides` per GDD) to `PRESENT:` / `ABSENT:` output: `full` requires all 8; `standard` requires Overview, Detailed Rules, Edge Cases, Dependencies, Acceptance Criteria + conditional Formulas (when defining numeric rules); `minimal` checks `design/game-brief.md` and treats voluntary GDDs advisorily at `standard`.
- Check for `[To be designed]` placeholders and valid header status matching `^>?\s*\*\*Status\*\*:` (`Draft | In Design | Designed | In Review | Approved | Implemented | Needs Revision`).

### 2b: ADR Format Audit
Check each ADR for:
- `## Status` (**BLOCKING** if missing — readiness checks silently pass without it)
- `## ADR Dependencies` (**HIGH** if missing)
- `## Engine Compatibility` (**HIGH** if missing)
- `## GDD Requirements Addressed` (**MEDIUM** if missing)
- `## Performance Implications` (**LOW** if missing)

### 2c: `systems-index.md` Format Audit
- **Parenthetical status values** (e.g., `Needs Revision (...)`, `In Progress (...)`): **BLOCKING** — breaks exact-string matching in `ags-gate`, `ags-plan`, and `ags-arch-review`.
- **Invalid status enum**: must be in `{Not Started, In Progress, In Review, Designed, Approved, Needs Revision}`.
- **Missing minimum columns**: System name, Layer, Priority, Status.

### 2d: Story Format Audit
Check each story (`production/epics/**/story-*.md`): `Manifest Version:` (LOW — existing stories auto-pass), `TR-[a-z]+-[0-9]+` (MEDIUM), `ADR-` reference (MEDIUM), readable `Status:`, and `- [ ]` acceptance criteria checkboxes. **Never regenerate stories already in progress or done.**

### 2e & 2f: Infrastructure & Project Config Audit
Check presence of: `docs/architecture/tr-registry.yaml` (HIGH), `docs/architecture/control-manifest.md` + `Manifest Version:` (HIGH/MEDIUM), `production/sprint-status.yaml` (MEDIUM), `project.stage` / `production/stage.txt` (MEDIUM), `docs/engine-reference/<engine>/VERSION.md` (HIGH), `docs/architecture/requirements-traceability.md` (MEDIUM), plus `project.yaml` / legacy engine, naming, and performance fields (`[TO BE CONFIGURED]` = unset).

### 2g: Legacy v1 Configuration Check
When `project.yaml` is absent and legacy v1 config files exist (`production/stage.txt`, `production/review-mode.txt`, or legacy technical preferences with real configured values), classify as **BLOCKING** and run the deterministic converter:

```bash
python .ags/cli.py check migrate-v1 --dry-run
```

On user confirmation:
1. Run `python .ags/cli.py check migrate-v1` (non-destructive: writes `project.yaml` + `production/migration-report.md` and leaves legacy files intact; note legacy `review_mode: none` maps to `solo`, and an explicit `modes.review_mode` shadows `modes.rigor`).
2. Instruct user to review `production/migration-report.md`, then run `python .ags/cli.py check migrate-v1 --finalize` to safely remove verified redundant `.txt` mirrors.
3. If `migrate-v1` exits with code 3 (values disagree / split-brain OR `production/migration-report.md` already exists), surface the conflict/state and stop — never bypass it.

## Phase 3 & 4: Prioritize & Build Migration Plan

Group gaps into `BLOCKING` -> `HIGH` (infra before GDD/ADR content) -> `MEDIUM` (GDD -> ADR -> story) -> `LOW`. Include for each gap: problem statement, exact remediation command (`ags-gdd retrofit <path>`, `ags-architect retrofit <path>`, etc.) or manual edit, rough estimate, and `- [ ]` checkbox. Preserve the exact bootstrap sequence:
1. Fix ADR formats -> 2. `ags-arch-review` (bootstraps `tr-registry.yaml`) -> 3. `ags-architect manifest` -> 4. `ags-plan sprint update` -> 5. `ags-gate`.

## Phase 5–7: Confirm, Write, Review Mode & First Action

1. Show summary counts (`BLOCKING`, `HIGH`, `MEDIUM`, `LOW`), list every `BLOCKING` gap as a one-line bullet, note any prior `docs/adoption-plan-*.md` (current run reflects state on disk, not a diff), and confirm writing `docs/adoption-plan-[date].md` (or show full draft first).
2. If `modes.review_mode` is unset in both `project.yaml` and `production/review-mode.txt`, offer `full` / `lean` / `solo` and save choice (noting that explicit `modes.review_mode` overrides `modes.rigor` expansion).
3. Offer the single highest-priority immediate action (`systems-index.md` parenthetical cleanup -> ADR `## Status` retrofits -> GDD missing Acceptance Criteria -> medium improvements / `ags-start stage`).
