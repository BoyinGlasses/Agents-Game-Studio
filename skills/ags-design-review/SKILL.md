---
name: ags-design-review
description: "Use when reviewing one GDD for quality, running holistic cross-GDD review, checking GDD consistency against the entity registry, auditing balance or content counts, or propagating a GDD change to ADRs. Do NOT use when authoring a GDD (-> ags-gdd), reviewing UX specs (-> ags-art-ux), or reviewing architecture/ADRs (-> ags-arch-review)."
---

# Design Review, Consistency & Change Propagation

Validates single GDDs (`design-review`), holistic cross-system coherence (`review-all`), entity-registry conflicts (`consistency`), numerical balance (`balance`), implemented vs planned content (`content-audit`), and ADR cascade impact (`propagate`).

## Contract

- **Inputs**: Target `design/gdd/<system>.md` or `design/gdd/*.md`, `design/gdd/{game-concept,game-pillars,systems-index}.md`, `design/gdd/reviews/<doc>-review-log.md`, `design/gdd/gdd-cross-review-<YYYY-MM-DD>.md`, `design/registry/entities.yaml`, `docs/consistency-failures.md`, `assets/data/`, `design/balance/`, `docs/architecture/{adr-*.md,requirements-traceability.md}`, resolved code root (`src/`, `Assets/`, `Source/`), `project.yaml`.
- **Roles**: `creative-director` (senior synthesis), `technical-director` (TD-CHANGE-IMPACT), `game-designer` (lenses: `systems-designer`, `economy-designer`, `narrative-director`, `level-designer`), `qa-lead`, `art-ux-director` (lens: `ux-designer`), `tech-artist` (lens: `audio-director`), `gameplay-coder` (lenses: `ai-programmer`, `network-programmer`, `ui-programmer`), `test-engineer` (lens: `performance-analyst`), `godot-specialist`, `unity-specialist`, `unreal-specialist`, `scout`.
- **Outputs**: Read-only reports (`design-review`, `balance`, `content-audit --summary`); confirmed writes to `design/gdd/reviews/<doc>-review-log.md`, `design/gdd/gdd-cross-review-<YYYY-MM-DD>.md`, `design/gdd/systems-index.md`, `design/registry/entities.yaml`, `docs/consistency-failures.md`, `design/balance/balance-check-<system>-<YYYY-MM-DD>.md`, `docs/content-audit-<YYYY-MM-DD>.md`, `docs/architecture/change-impact-<YYYY-MM-DD>-<system>.md`, `docs/architecture/adr-*.md` status, `docs/architecture/requirements-traceability.md`, `production/session-state/active.md`.
- **Verification**: Run `python .ags/cli.py check receipts check|hash`, `python .ags/cli.py check gdd [path]`, and `python .ags/cli.py check review-scope`; resolve code root before content scans; apply `<50KB` full vs `>=50KB` bounded-section ADR reads.
- **Next Skill**: `ags-gdd` (revise flagged GDDs or design next system), `ags-architect` (start architecture or replace superseded ADRs), `ags-arch-review` (rebuild traceability), `ags-plan`, or `ags-gate`.

## Preflight

Run once at startup and hold resolved settings:

```bash
python .ags/cli.py preflight ags-design-review [mode-or-target]
```

- Resolve `modes.workflow` (`workflow_overrides.system_overrides.<stem>` where `<stem>` is the GDD filename stem -> `modes.workflow` -> `modes.rigor`), `workflow_overrides.tuning_knobs`, `modes.automation`, `modes.automation_always_ask` (`schema_changes` / `architecture_decisions`), `modes.review_mode` (`--review [full|lean|solo]` overrides), `engine.name`, and `engine.version`.

| Mode | Trigger | Reference |
|---|---|---|
| `design-review` | Path to one GDD (must run in a fresh session separate from authoring) | [references/design-review.md](references/design-review.md) |
| `review-all` | `all`, `full`, `consistency`, `design-theory`, or `since-last-review` | [references/review-all-gdds.md](references/review-all-gdds.md) |
| `consistency` | `consistency`, `entity:<name>`, `item:<name>` | [references/consistency-check.md](references/consistency-check.md) |
| `balance` | `balance [combat\|economy\|progression\|loot\|<path>]` | [references/balance-check.md](references/balance-check.md) |
| `content-audit` | `content-audit [system\|--summary]` | [references/content-audit.md](references/content-audit.md) |
| `propagate` | `propagate <gdd-path>` (ADR & traceability impact cascade) | [references/propagate-design-change.md](references/propagate-design-change.md) |

## Phases

### 1. Single-GDD Review (`design-review`)
- Follow [references/design-review.md](references/design-review.md).
- Run `python .ags/cli.py check receipts check "design/gdd/reviews/[doc]-review-log.md" "[target]" "design/registry/entities.yaml"` first: offer prior verdict reuse ONLY when all entries are `UNCHANGED` (`APPROVED` offers reuse; failed docs direct user to revise first). On `CHANGED`/`NEW`/`RECEIPT: NONE`, run a **full** review — never partial/delta re-review.
- Run `python .ags/cli.py check gdd [target]` (`## Detailed Design` == `Detailed Rules`). Apply resolved tier: `full` requires all 8; `standard` requires 5 + conditional `Formulas` (system defines numeric rules — Category is hint only) + optional `Player Fantasy` / `Tuning Knobs` unless overridden; `minimal` advisory.
- In `full` mode, spawn all matching domain specialists in **parallel** (never simulated inline) with adversarial prompts -> `creative-director` senior synthesis -> surface disagreements. Write review log with `python .ags/cli.py check receipts hash` on approval; recommend **fresh session** before re-reviewing after edits.

### 2. Cross-GDD Holistic Review (`review-all`)
- Follow [references/review-all-gdds.md](references/review-all-gdds.md).
- Run two L0 scans (`## Summary` fail-open denominator `N`; `python .ags/cli.py check review-scope` for `since-last-review`). Load `game-concept.md`, `game-pillars.md`, `systems-index.md`, `entities.yaml`, and targeted GDD sections (`Dependencies|Detailed Rules|Detailed Design|Formulas|Tuning Knobs|Acceptance Criteria|Player Fantasy`).
- Require >=2 readable GDDs; run Phase 2 (Consistency 2a-2f starting from `## Cross-References` + prose) and Phase 3 (Design Theory 3a-3g) as **parallel** `game-designer` subagents passing pasted content slices, then run Phase 4 Multi-System Scenario Walkthrough.
- Write ISO-dated `design/gdd/gdd-cross-review-YYYY-MM-DD.md` (`Needs Revision` exact string in `systems-index.md`) and append `active.md`.

### 3. Entity-Registry Consistency (`consistency`)
- Follow [references/consistency-check.md](references/consistency-check.md).
- Load `design/registry/entities.yaml`, pattern-search in-scope GDDs `-C 3` without full reads, deep-read only conflicts against authoritative `source:`. On confirmation, update stale registry (`# was:` comment, never delete -> `status: deprecated`) and unconditionally append every `CONFLICT` to `docs/consistency-failures.md` reflexion log + `active.md` breadcrumb.

### 4. Balance Check & Content Audit (`balance`, `content-audit`)
- Follow [references/balance-check.md](references/balance-check.md) and [references/content-audit.md](references/content-audit.md).
- Run **Insufficient-Input Gate** (`FOUND` vs `ABSENT` per input) before reporting. `content-audit` runs separate L0 Summary denominator + numeric content-noun patterns and resolves code root (`src/` / `Assets/` / `Source/`): unresolved code root emits `NOT ASSESSED — code root unresolved` (never defaults to `src/` or reports zero hits).

### 5. Propagate Design Change (`propagate <gdd-path>`)
- Follow [references/propagate-design-change.md](references/propagate-design-change.md).
- Inspect `git diff HEAD` / `HEAD~1 HEAD` hunks (`@@` headers) + `entities.yaml` `referenced_by:` -> scope ADRs by system tier (`minimal` N/A) -> compute union `M` of `## GDD Requirements Addressed` + prose mentions (disambiguate `M=0` against missing tables) -> bounded ADR reads (`<50KB` full, `>=50KB` heading map + `Context`/`Decision`/`Consequences`) -> `technical-director` (`TD-CHANGE-IMPACT`, `.ags/gates/td-change-impact.md`) -> resolve ADRs, update `requirements-traceability.md`, write `docs/architecture/change-impact-YYYY-MM-DD-<system>.md`.

## Gate & Verdict

- **`APPROVED` / `PASS` / `HEALTHY` / `COMPLETE`**: Checked scope conforms cleanly across all evaluated dimensions.
- **`NOT ASSESSED`** *(ranks ABOVE `APPROVED`/`PASS`/`HEALTHY`/`COMPLETE` and BELOW `NEEDS REVISION`/`MAJOR REVISION NEEDED`/`CONCERNS`/`CRITICAL ISSUES`/`FAIL`/`CONFLICTS FOUND`/`BLOCKED`)*: Target or dependency artifact missing/unreadable, `<2` GDDs for cross-review, unreturned parallel phase, undefined pillars, absent data/ADR tables, or unresolved code root — list missing items and producing skills.
- **`NEEDS REVISION` / `MAJOR REVISION NEEDED` / `CONCERNS` / `CRITICAL ISSUES` / `FAIL` / `CONFLICTS FOUND` / `BLOCKED`**: Blocking defects, conflicts, declined writes, or unresolved `REJECT` verdicts.
