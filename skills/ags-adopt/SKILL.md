---
name: ags-adopt
description: "Use when auditing an existing brownfield game project for AGS format compliance, migrating legacy v1 config files, or reverse-documenting existing code/prototypes into GDDs, ADRs, or concepts. Do NOT use when onboarding a fresh empty project -> ags-start."
---

# Brownfield Adoption & Reverse Documentation

Audits existing project artifacts for format compliance (`full`, `gdds`, `adrs`, `stories`, `infra`), drives deterministic legacy v1 config migration, and reverse-documents implemented systems or prototypes into design or architecture docs.

## Contract

- **Inputs**: `project.yaml`, legacy v1 files (`production/stage.txt`, `production/review-mode.txt`), design docs (`design/`), ADRs (`docs/architecture/adr-*.md`), stories (`production/epics/**/story-*.md`), infra artifacts, `docs/engine-reference/`, templates under `.ags/templates/`, and resolved code root or `prototypes/` (`reverse` mode).
- **Roles**: `scout`, `game-designer`, `technical-director` (optional assistance when tracing complex legacy code or clarifying intent).
- **Outputs**: `docs/adoption-plan-[date].md` (`audit`), migrated `project.yaml` + `production/migration-report.md` (`migrate-v1`), optional `modes.review_mode` + `production/review-mode.txt`, or provenance-stamped reverse-documented GDD / game brief / ADR / concept doc (`reverse`).
- **Verification**: Run `python .ags/cli.py preflight ags-adopt`, `python .ags/cli.py check gdd <path>` one file at a time (audit), and `python .ags/cli.py check migrate-v1 --dry-run` before v1 migration (`--finalize` only after inspecting `production/migration-report.md`); enforce the Sufficiency Check before drafting in `reverse` mode.
- **Next Skill**: `ags-gdd`, `ags-architect`, `ags-arch-review`, `ags-design-review`, or `ags-start`

## Preflight

Run:

```bash
python .ags/cli.py preflight ags-adopt [target-path]
```

Resolve `modes.automation`, `modes.automation_always_ask`, `modes.workflow`, `workflow_overrides.system_overrides`, `engine.name`, and code root before auditing or scanning code.

## Phases

### Phase 1: Route Mode

| Argument | Mode | Reference |
|---|---|---|
| No args, `full`, `gdds`, `adrs`, `stories`, `infra`, or `migrate` | **Brownfield Format Audit & v1 Migration** | [references/brownfield-audit.md](references/brownfield-audit.md) |
| `reverse <design\|architecture\|concept> <path>` | **Reverse-Document Code or Prototype** | [references/reverse-document.md](references/reverse-document.md) |

### Phase 2: Execute Mode Rules

- **Audit & Migration (`audit`)**:
  - Run existence scan first; if zero artifacts exist, prompt to switch to `ags-start` and stop.
  - Audit per resolved `modes.workflow` (`minimal` checks `design/game-brief.md` only; `standard` checks required docs/sections; `full` checks all): `check gdd <path>` per GDD, ADR critical sections (`## Status` BLOCKING), `systems-index.md` parenthetical status values (BLOCKING), story fields (existing stories auto-pass missing optional stamps — never regenerate in-progress stories), infra files, and `check migrate-v1 --dry-run`.
  - Classify gaps (`BLOCKING`, `HIGH`, `MEDIUM`, `LOW`), confirm and write `docs/adoption-plan-[date].md`, set `modes.review_mode` only if unset, and offer the single highest-priority fix immediately.
- **Reverse Documentation (`reverse`)**:
  - Resolve code root before reading source paths; extract mechanics, formulas, tuning constants, patterns, or emergent loops.
  - Run the **Sufficiency Check** (stop if implemented mechanics, formulas, and tuning values are all zero OR code `< ~20` non-boilerplate lines).
  - Clarify **intent** with the user; mark unanswered items `INTENT UNKNOWN — inferred from implementation, not confirmed`, write `none found in the source` for empty groups, stamp provenance at the top of the artifact, and confirm write per `modes.automation`.

## Gate & Verdict

- **`COMPLETE`**: Audit plan written (`audit`), migration executed cleanly (`migrate-v1`), or reverse-documented artifact approved and saved (`reverse`).
- **`NOT ASSESSED`** *(ranks above `COMPLETE` and below `BLOCKED` / `FAIL`)*: Code root is unresolved when scanning code (`reverse`), `check gdd` fails file discovery (`Not found:`), or `reverse` fails the Sufficiency Check (insufficient implementation to reverse-document without invention).
- **`BLOCKED`**: User declined file write, `check migrate-v1` exited with split-brain conflict (exit code 3), or project is fresh with zero brownfield artifacts (`ags-start`).
