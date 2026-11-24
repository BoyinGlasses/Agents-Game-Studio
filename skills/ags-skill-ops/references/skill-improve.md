# Skill Improvement Loop (`ags-skill-ops` Improve Mode)

Executes a disciplined `baseline -> diagnose -> targeted fix -> retest -> keep or revert` loop on a single skill.

## 1. Validate Target & Establish Baseline

1. Require skill argument (`ags-*`, e.g., `ags-dev`). If omitted, show usage and stop.
2. Confirm `core/skills/[name]/SKILL.md` (or `.agents/skills/[name]/SKILL.md`) exists; if absent, stop with `"Skill '[name]' not found."`
3. Run `static [name]` from [skill-test.md](skill-test.md) and record baseline `FAIL`, `WARN`, and `NOT ASSESSED` counts plus specific failing invariants (`S1`–`S6`, Checks 1–7).
4. Look up `category:` in `tests/eval/catalog.yaml` (if `tests/eval/` is present). If found, run `category [name]` and record category baseline `FAIL` / `WARN` / `NOT ASSESSED` counts; if `tests/eval/` or `category:` is absent, announce `"Category baseline: skipped — [reason]"` and continue with static baseline.
5. If static (and category, if run) baselines show `0` failures, `0` warnings, and `0` unassessed items, stop cleanly: `"Skill passes all static and category checks. No improvements needed."`

## 2. Diagnose & Propose Targeted Fix

1. Read `SKILL.md` (and any referenced `references/*.md` / `CONTRACT.md`) completely.
2. Map every failing or warning check to its exact textual gap:
   - Missing or non-canonical frontmatter key -> fix `name` / `description` (`Use when ... Do NOT use when ...`).
   - Line count `> 220` -> extract detailed tables/sub-modes into `references/*.md` while keeping routing concise.
   - Missing `## Contract`, `## Preflight`, `## Phases`, or `## Gate & Verdict` -> restore required structure and `python .ags/cli.py preflight <skill>`.
   - Missing `NOT ASSESSED` precedence or silent skip -> add explicit `NOT ASSESSED` trigger and announcement rule.
   - Missing write/checkpoint authorization -> add Story Checkpoint Harness or `modes.automation` rule without per-file write spam.
   - Broken role/template/gate/skill reference or forbidden token -> replace with canonical AGS v2 path/name.
   - Category rubric gap (e.g., `G2`, `SH4`, `T1`) -> patch only the missing clause.
3. Present full diagnosis and marked **before/after** patches. Only edit what failed — preserve passing sections unchanged.
4. Wait for explicit user approval before modifying `SKILL.md` (or `references/*.md`). If declined, stop without edits.

## 3. Apply, Retest & Keep or Revert

1. Snapshot current file content before editing (for safe rollback).
2. Apply targeted fix to `core/skills/[name]/SKILL.md` (or `.agents/skills/[name]/SKILL.md`).
3. Re-run `static [name]` and (when applicable) `category [name]`. In the framework repo, also run:
   - `python -m unittest tests.test_cohesion -v`
   - `python -m ags.build --check` (or `python -m ags.build` if compiling `skills/` after approval)
4. Display before/after delta:
   - `Static: Before [N] FAIL, [M] WARN -> After [N'] FAIL, [M'] WARN`
   - `Category: Before [N] FAIL, [M] WARN -> After [N'] FAIL, [M'] WARN`
5. **Verdict**:
   - **Combined issue count decreased (`FAIL + WARN + NOT ASSESSED` lower than baseline)** and zero new regressions: report `"Score improved. Changes kept."` and summarize fixed dimensions.
   - **Same or worse**: report `"Combined score did not improve."`, explain why, and ask user confirmation to revert (`git checkout -- <path>`).
6. Recommend running `ags-skill-ops` (`static all`, `audit`, or `improve [next-name]`).
