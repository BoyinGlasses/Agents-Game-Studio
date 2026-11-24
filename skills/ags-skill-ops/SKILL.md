---
name: ags-skill-ops
description: "Use when auditing, linting, behavior-testing, rubric-checking, or iteratively improving AGS v2 skills and agent specs. Do NOT use when testing game source code (-> ags-qa) or verifying game story completion (-> ags-verify)."
---

# Skill Testing & Iterative Improvement

Validates AGS v2 skills (`core/skills/ags-*/SKILL.md` in framework repo or `.agents/skills/ags-*/SKILL.md` in a game project) and role definitions, and executes the `baseline -> diagnose -> targeted fix -> retest -> keep or revert` improvement loop.

## Contract
- **Inputs**: `core/skills/*/SKILL.md` or `.agents/skills/*/SKILL.md`, `core/agents/` or `.ags/roles/`, `tests/eval/{catalog.yaml,quality-rubric.md,skills/**,agents/**,templates/skill-test-spec.md}`, `tests/test_cohesion.py`
- **Roles**: Primary agent runs checks; `scout` (optional read-only spec/skill scan), `qa-lead` (optional rubric review)
- **Outputs**: Compliance/spec/category/audit reports in conversation, optional `tests/eval/results/skill-test-spec-[name]-[date].md` and `tests/eval/catalog.yaml` updates, or targeted edits to a failing `SKILL.md` in `improve` mode after user confirmation
- **Verification**: `python -m unittest tests.test_cohesion -v` and `python -m ags.build --check` (when run in framework repo), plus before/after static + category scores
- **Next Skill**: `ags-skill-ops` (`static all` / `audit` / `improve [next]`), `ags-verify` (when changes are part of a framework story)

## Preflight

Run once at startup (no-op defaults outside a game project):

```bash
python .ags/cli.py preflight ags-skill-ops [mode-and-target]
```

- **Sub-modes**:
  - `static [name|all]` — structural & invariant checks (`S1`–`S6` + legacy checks) on one or all skills.
  - `spec [name]` — behavioral assertion verifier against `tests/eval/skills/**`.
  - `category [name|all]` — category rubric evaluation against `tests/eval/quality-rubric.md`.
  - `audit` *(default if omitted)* — full coverage report across skills and roles.
  - `improve [name]` — test-fix-retest loop on one skill ([references/skill-improve.md](references/skill-improve.md)).

## Phases

### Phase 1: Parse Sub-Mode & Locate Corpus
1. Parse mode (`static`, `spec`, `category`, `audit`, `improve`) and optional skill name (`ags-*`). Unrecognized sub-mode prints usage and stops.
2. Locate skill root: prefer `core/skills/` in framework repo (followed by `.agents/skills/` in a game project). Verify `tests/eval/` availability:
   - `static` runs even if `tests/eval/` is absent.
   - `spec`, `category`, and `audit` require `tests/eval/` (present in framework repo, intentionally omitted in game projects); if absent, stop and report `NOT ASSESSED — tests/eval/ not present in this workspace` rather than emitting partial passes.

### Phase 2: Execute Mode Checks
- **If `static` / `spec` / `category` / `audit`**: Follow [references/skill-test.md](references/skill-test.md).
  - Check all Global Skill Invariants (`<=220` lines, exact 2-key frontmatter, required 4 `##` sections, `preflight` CLI invocation, explicit `NOT ASSESSED` ranking, zero legacy/Claude leakage, valid role & `Next Skill` references).
  - Always state the exact denominator (`[N] of [M] skills checked`) so unexamined files never masquerade as covered.
- **If `improve [name]`**: Follow [references/skill-improve.md](references/skill-improve.md).
  - Verify target `SKILL.md` exists. Run `static [name]` and `category [name]` baselines (stop if already `0 FAIL, 0 WARN, 0 NOT ASSESSED`).
  - Diagnose each failing or warning check and show targeted before/after patches. Wait for explicit user confirmation before writing `SKILL.md`.
  - Re-run `static [name]` and `category [name]` (plus `python -m unittest tests.test_cohesion -v` and `python -m ags.build --check` in framework repo). Keep only if combined issues decreased; otherwise propose `git checkout -- <path>`.

### Phase 3: Persistence & Next Steps
1. For `spec` or `category`, ask confirmation before writing `tests/eval/results/` or updating `last_spec*` / `last_category*` in `tests/eval/catalog.yaml`. Never auto-write in `audit` mode.
2. Route to `ags-skill-ops` (`spec [name]`, `improve [failing]`, or `audit`) or `tests/eval/templates/skill-test-spec.md` for uncovered gaps.

## Gate & Verdict

- **Static Mode Precedence**: `NON-COMPLIANT` > `WARNINGS` > `NOT ASSESSED` > `COMPLIANT`.
- **Spec Mode Precedence**: `FAIL` > `PARTIAL` > `NOT ASSESSED` > `PASS`.
- **Category Mode Precedence**: `FAIL` > `WARN` > `NOT ASSESSED` > `PASS`.
- **`NOT ASSESSED` Semantics**: Used whenever a skill file is unreadable, `tests/eval/` (or `catalog.yaml` / `spec:`) is absent, or an assertion depends on undefined fixture/runtime state. Always outranks `PASS`/`COMPLIANT` and ranks below `FAIL`/`PARTIAL`/`NON-COMPLIANT`. Never mark an unrun or unevaluable check `PASS`.
- Full check rules in [references/skill-test.md](references/skill-test.md) and [references/skill-improve.md](references/skill-improve.md).
