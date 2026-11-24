---
name: ags-arch-review
description: "Use when auditing GDD-to-ADR traceability, detecting cross-ADR conflicts and cycles, auditing engine compatibility, managing technical debt, or checking scope creep. Do NOT use when authoring or accepting ADRs or control manifests (-> ags-architect), or reviewing individual code stories (-> ags-verify)."
---

# Architecture Review, Tech Debt & Scope Check

Audits GDD-to-ADR traceability, cross-ADR conflicts and dependency cycles, engine compatibility, technical debt registers, and baseline-vs-current scope creep.

## Contract

- **Inputs**: `project.yaml`, `project.local.yaml`, `design/gdd/*.md`, `design/gdd/systems-index.md`, `docs/architecture/{architecture.md,adr-*.md,tr-registry.yaml,architecture-review-*.md}`, `docs/engine-reference/<engine>/{VERSION,breaking-changes,deprecated-apis}.md`, referenced `docs/engine-reference/<engine>/modules/*.md`, `docs/consistency-failures.md`, `docs/tech-debt-register.md`, `production/epics/**/*.md`, `production/sprints/sprint-*.md`, `production/milestones/*.md`, `tests/{unit,integration}/**/*_test.*`, resolved code root (`src/`, `Assets/`, `Source/`)
- **Roles**: `technical-director` (read-only conflict/engine audit), `code-reviewer` (read-only review lens), `producer` (scope/milestone tracking), `scout` (optional codebase/doc scan), `godot-specialist`, `unity-specialist`, `unreal-specialist`
- **Outputs**: `docs/architecture/architecture-review-[date].md`, `docs/architecture/architecture-traceability.md`, `docs/architecture/requirements-traceability.md` (`rtm`), `docs/architecture/tr-registry.yaml` (append/update without renumbering), `docs/consistency-failures.md` (append `CONFLICT` entries if file exists), `docs/tech-debt-register.md` (`tech-debt` write modes), `production/session-state/active.md` (`review`), read-only reports (`scope` and `tech-debt report`)
- **Verification**: `python .ags/cli.py preflight ags-arch-review [target]`, `python .ags/cli.py check receipts ...`, `python .ags/cli.py check adr-graph`, engine specialist consultation, and code-root/baseline denominator checks
- **Next Skill**: `ags-architect` (missing/Proposed ADRs or manifest), `ags-plan` (re-planning or scheduling debt), `ags-qa` (`setup`), `ags-art-ux` (`ux-design`), or `ags-gate` (when pre-gate items pass)

## Preflight

Run once at startup and hold the resolved configuration for the run:

```bash
python .ags/cli.py preflight ags-arch-review [target]
```

Capture `automation`, `workflow`, `engine.*` (including resolved `code_root`), and `review_mode`. Follow `modes.automation` (`collaborative` prompts at decisions and writes; `guided` prompts on major choices and new files; `autonomous` logs to `production/session-logs/decision-log.md` except `automation_always_ask` categories).

## Phases

### Phase 1: Route Mode

Select sub-mode from arguments or user intent (load ONLY the active reference file):

| Argument / Trigger | Mode | Reference |
|---|---|---|
| `review` (`full` \| `coverage` \| `consistency` \| `engine` \| `single-gdd <path>` \| `rtm`) or default | **Architecture Review** | [references/architecture-review.md](references/architecture-review.md) |
| `tech-debt` (`scan` \| `add` \| `prioritize` \| `report`) | **Technical Debt Register** | [references/tech-debt.md](references/tech-debt.md) |
| `scope` (`<feature \| sprint-N \| milestone>`) | **Scope Creep Check** (read-only) | [references/scope-check.md](references/scope-check.md) |

### Phase 2: Execute Mode Workflow

1. **Architecture Review (`review`)**: Follow [references/architecture-review.md](references/architecture-review.md).
   - Check freshness first via `python .ags/cli.py check receipts [latest-report] docs/architecture/adr-*.md design/gdd/*.md`. Any `UNRESOLVED` disqualifies skipping.
   - Perform L0 Summary scan (fail open if absent) and L1/L2 bounded section loads with explicit `N_gdd` / `N_adr` denominators (`0` section matches on `N_adr > 0` = malformed ADRs -> stop and route to `ags-architect adr retrofit`).
   - Pre-load `docs/architecture/tr-registry.yaml` (never renumber IDs; skip `deprecated`). Grade `Proposed` ADRs as `🟡 Covered (Proposed)` capping overall verdict at `CONCERNS` (never `PASS`).
   - Run `python .ags/cli.py check adr-graph` for deterministic cycle detection and `NO_DEPS_SECTION` structural gaps. Consult `<engine>-specialist` (or record `NOT ASSESSED` if unconfigured). Flag GDD revisions with exact status `Needs Revision`. Audit `architecture.md` (or emit `NOT ASSESSED` line item if absent). Emit content hashes via `check receipts hash`.

2. **Technical Debt (`tech-debt`)**: Follow [references/tech-debt.md](references/tech-debt.md).
   - In `scan`: resolve code root (`src/` / `Assets/` / `Source/`) from preflight. If code root is unresolved or 0 source files exist, emit `NOT ASSESSED — no source files to scan` and stop without writing `docs/tech-debt-register.md` or emitting `COMPLETE`. Always report the scanned file denominator.
   - Support `add` (categorize + effort), `prioritize` (`(impact x frequency) / effort`), and read-only `report` (trends + items older than 3 sprints).

3. **Scope Check (`scope`)**: Follow [references/scope-check.md](references/scope-check.md).
   - Strictly read-only. Locate baseline (`design/gdd/`, `production/sprints/`, or `production/milestones/`), compare against current implementation/commits/TODOs, and compute Bloat Score (`<=10%` `PASS`, `10–25%` `CONCERNS`, `>25%` `FAIL`).
   - If baseline enumerates zero items, current state is unreadable, or denominator is zero, replace the numeric counts/Bloat Score with `Baseline unusable — see verdict` and emit `NOT ASSESSED`.

### Phase 3: Handoff & Integrity

- Never run `ags-arch-review review` in the same session that authored ADRs (`ags-architect`).
- Do not offer `ags-gate` in handoff while any pre-gate item (`tests/`, CI tests workflow, `design/accessibility-requirements.md`, `design/ux/interaction-patterns.md`) is missing.

## Gate & Verdict

- **`PASS` / `COMPLETE`**: All in-scope requirements traced to `Accepted` ADRs with zero blocking conflicts/cycles and consistent engine compatibility (`review`); debt action completed with non-zero scanned file denominator (`tech-debt`); or net scope change `<=10%` over non-empty baseline (`scope`).
- **`NOT ASSESSED`** *(ranks above `PASS`/`COMPLETE` and below `CONCERNS`/`FAIL`/`BLOCKED`)*: Review could not evaluate stated scope (no ADRs, missing requirement source, unreadable/statusless ADR, or missing `architecture.md` when Phase 6 is the scope), `tech-debt scan` has unresolved code root or zero source files, or `scope` has empty baseline / unreadable current state / zero denominator. Name the exact gap and fix; never report an unrun check as clean.
- **`CONCERNS`**: Non-blocking gaps, partial coverage, coverage resting on `Proposed` ADRs (always caps verdict at `CONCERNS`), `NO_DEPS_SECTION` gaps, or `10–25%` scope creep.
- **`FAIL` / `BLOCKED`**: Uncovered Foundation/Core critical requirements, blocking cross-ADR conflicts or `CYCLE` edges, missing required `tech-debt` subcommand or missing baseline file, `>25%` scope creep, or user declined write.
