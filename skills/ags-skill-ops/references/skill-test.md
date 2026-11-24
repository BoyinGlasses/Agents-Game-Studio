# Skill Test Workflows (`ags-skill-ops` Test Modes)

Evaluates AGS v2 skills and role definitions across four modes: `static`, `spec`, `category`, and `audit`.

## 1. Static Mode (`static [name|all]`)

Target `core/skills/*/SKILL.md` (framework repo) or `.agents/skills/*/SKILL.md` (game project). Run all checks per skill:

1. **Frontmatter (`S2`)**: Valid YAML fence containing strictly `name` (matching directory name `ags-*`) and `description` (`"Use when ... Do NOT use when ..."`). **FAIL** if missing, empty, or extra obsolete keys appear.
2. **Length & Modularity (`S1`)**: `SKILL.md` is `<= 220` lines; deep workflows belong in `references/*.md` or `CONTRACT.md`. **FAIL** if `> 220` lines.
3. **Closed-Loop Headings & Preflight (`S3`, `S4`)**: Exact `## Contract` (with `Inputs`, `Roles`, `Outputs`, `Verification`, `Next Skill`), `## Preflight` (invoking `python .ags/cli.py preflight <skill>`), `## Phases` (`>=2` sub-phases), and `## Gate & Verdict`. **FAIL** if any required heading or preflight command is absent.
4. **Verdict Keywords & Honest `NOT ASSESSED` (`S5`)**: Skill states explicit verdict outcomes (`PASS`, `FAIL`, `CONCERNS`, `APPROVED`, `BLOCKED`, `COMPLETE`, `READY`, `COMPLIANT`, `PROCEED`/`PIVOT`/`KILL`, or `CRITICAL`/`HIGH`/`MEDIUM`/`LOW`) AND includes `NOT ASSESSED` (outranking pass, below fail) for assessment skills. Artifact/config-only skills without a judgement emit **WARN** rather than FAIL if no verdict keyword applies.
5. **Write Authorization & Checkpoint Discipline**: Mutating skills declare story-checkpoint approval (`ags-dev`/`ags-verify`), mode-aware confirmation (`modes.automation`), or explicit user confirmation before writing/advancing stages — without per-file write-permission boilerplate. **FAIL** for mutating skills lacking authorization rules; **PASS** for read-only skills.
6. **Zero Harness Leakage (`S6`)**: Zero occurrences of Claude-only tools, legacy shell helpers, legacy paths, legacy skill prefixes, or per-file write-permission phrases; all `Roles`, `Next Skill`, `references/*.md`, `.ags/templates/*.md`, `.ags/gates/*.md`, and `.ags/roles/*.md` links resolve to real files. **FAIL** on any broken reference or forbidden token.
7. **Next-Step Handoff**: `## Contract` -> `Next Skill` and closing phase route cleanly to canonical `ags-*` skills (**WARN** if absent).

**Static output & `NOT ASSESSED`**:
- Per-skill result: `COMPLIANT`, `WARNINGS`, `NON-COMPLIANT`, or `NOT ASSESSED` (if unreadable/unparseable; ranked above `COMPLIANT`, below `WARNINGS`/`NON-COMPLIANT`).
- Always print `[N] of [M] skills checked` in the summary header so skipped/unreadable entries never hide behind the total count.

## 2. Spec Mode (`spec [name]`)

Requires `tests/eval/catalog.yaml` and the matching spec file under `tests/eval/skills/`. If `tests/eval/` is missing (e.g., inside an initialized game project) or spec path is missing, emit `NOT ASSESSED — <exact missing path>`.

1. Read both `SKILL.md` (plus referenced `references/*.md` / `CONTRACT.md`) and the spec file completely.
2. Evaluate each test case (**Fixture**, **Expected behavior**, **Assertions**) and **Protocol Compliance** (checkpoint/mode authorization before writes, findings before approval, next-step handoff, no unapproved auto-creation).
3. Grade each assertion: `PASS`, `PARTIAL`, `FAIL`, or `NOT ASSESSED` (undefined fixture state, missing referenced file/section, or runtime-only check static reading cannot settle — ranked above `PASS`, below `PARTIAL` and `FAIL`).
4. Report per-case verdicts and overall verdict (`FAIL` > `PARTIAL` > `NOT ASSESSED` > `PASS`).
5. Ask user confirmation before saving `tests/eval/results/skill-test-spec-[name]-[date].md` and updating `last_spec` / `last_spec_result` in `tests/eval/catalog.yaml`.

## 3. Category Mode (`category [name|all]`)

Requires `tests/eval/catalog.yaml` and `tests/eval/quality-rubric.md`. If absent, emit `NOT ASSESSED`.

1. Look up `category:` for the target skill (or iterate all categorized skills for `all`). Note missing `category:` explicitly.
2. Read the matching rubric table in `tests/eval/quality-rubric.md` (`gate`, `review`, `authoring`, `readiness`, `pipeline`, `analysis`, `team`, `sprint`, `utility`) plus `S1`–`S6` Global Skill Invariants.
3. Evaluate each metric as `PASS`, `FAIL`, `WARN`, or `NOT ASSESSED` with exact section quotes for any gap.
4. Ask user confirmation before updating `last_category` / `last_category_result` in `tests/eval/catalog.yaml`.

## 4. Audit Mode (`audit`)

Strictly **read-only** (zero file writes). Requires `tests/eval/catalog.yaml`.

1. Enumerate actual skills (`core/skills/ags-*/SKILL.md` or `.agents/skills/*/SKILL.md`) and roles (`core/agents/{core,engines/*,lenses}/*.md` or `.ags/roles/*.md`).
2. Cross-reference against `tests/eval/catalog.yaml` (`spec:` existence, `last_static*`, `last_spec*`, `last_category*`, `priority:`). Flag skills or roles present on disk yet absent from `catalog.yaml` — never silently drop them.
3. Output skill and role coverage tables showing exact examined denominators (`[examined] of [total]`), top critical/high priority gaps, and suggest next commands (`static all`, `category all`, `spec [name]`, or new spec authoring from `tests/eval/templates/skill-test-spec.md`).
