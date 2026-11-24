# Skill & Role Quality Rubric (AGS v2)

Used by `ags-skill-ops` (`category` and `static` modes) and `tests/test_cohesion.py` to evaluate
AGS v2 skills and agent roles. Every metric is binary `PASS`, `FAIL`, or `NOT ASSESSED` (with `WARN`
only when partially satisfied).

**Verdict Ranking (Mandatory):** `FAIL / BLOCKED > NOT ASSESSED > PASS`.
An unexecuted check, absent input class, or skipped mode MUST be reported as `NOT ASSESSED`
(or `NOT VERIFIED` for build/play evidence) — never silently collapsed into `PASS`.

---

## Global Skill Invariants (All 21 `ags-*` Skills)

| Metric | PASS criteria |
|---|---|
| **S1 — Length budget** | `core/skills/<name>/SKILL.md` is `<= 220` lines; deep sub-mode workflows live in `references/*.md` |
| **S2 — Canonical frontmatter** | YAML frontmatter has strictly `name: ags-...` and `description: "Use when ... Do NOT use when ..."` |
| **S3 — Closed-loop sections** | Contains `## Contract`, `## Preflight`, `## Phases`, and `## Gate & Verdict` |
| **S4 — Deterministic preflight** | `## Preflight` invokes `python .ags/cli.py preflight <skill>` (never legacy shell helpers) |
| **S5 — Honest `NOT ASSESSED`** | `## Gate & Verdict` enforces `FAIL / BLOCKED > NOT ASSESSED > PASS` and forbids silent skips |
| **S6 — Zero harness leakage** | Zero occurrences of per-file write-approval prompts, legacy host tool names, legacy host config filenames, legacy directories, or legacy slash/skill prefixes |

---

## Skill Categories

### `gate` (`ags-gate`)

| Metric | PASS criteria |
|---|---|
| **G1 — Review mode read** | Reads `modes.review_mode` and `modes.workflow` via `preflight ags-gate` before spawning directors |
| **G2 — Full mode panel** | In `full` mode, invokes applicable `*-PHASE-GATE` definitions from `.ags/gates/` in parallel |
| **G3 — Lean mode: PHASE-GATE only** | In `lean` mode, runs `*-PHASE-GATE` only per `modes.workflow` panel width; skips inline gates |
| **G4 — Solo mode skip notice** | In `solo` mode, skips director gates and emits explicit `[GATE-ID] skipped — Solo mode` (`NOT ASSESSED` for director sign-off) |
| **G5 — No auto-advance** | Runs `python .ags/cli.py check artifacts` and never advances `project.yaml` `project.stage` without explicit game-maker confirmation |

### `review` (`ags-design-review`, `ags-arch-review`, `ags-art-ux` review mode)

| Metric | PASS criteria |
|---|---|
| **R1 — Read-only reviewer sandbox** | Delegates review checks to `sandbox_mode: read-only` roles (`creative-director`, `technical-director`, `code-reviewer`, `scout`); never mutates reviewed docs unrequested |
| **R2 — Complete section/dimension check** | Uses `python .ags/cli.py check gdd` / `adr-graph` / `receipts` / `review-scope` deterministically and evaluates all required sections for the active `modes.workflow` tier |
| **R3 — Canonical verdict vocabulary** | Emits exact verdict vocabulary (`APPROVED` / `NEEDS REVISION` / `MAJOR REVISION NEEDED` for design; `PASS` / `CONCERNS` / `FAIL` for architecture) plus `NOT ASSESSED` when inputs are absent |
| **R4 — Separation of analysis and post-analysis gates** | Completes deterministic + analytical findings before spawning post-analysis director gates |
| **R5 — Structured findings table** | Presents per-section / per-check status table with `file:line` or receipt citations before the verdict |

### `authoring` (`ags-ideate`, `ags-gdd`, `ags-art-ux`, `ags-architect`)

| Metric | PASS criteria |
|---|---|
| **A1 — Mode & density scaling** | Adapts depth to `modes.workflow`, `docs.density`, and `workflow_overrides.system_overrides` from preflight |
| **A2 — Decision confirmation without per-file spam** | Asks only for missing product/creative/architecture decisions (or major section sign-off in interactive GDD authoring) rather than per-file write-approval boilerplate on every routine edit |
| **A3 — Non-destructive retrofit** | Detects existing GDD/UX/Art/ADR documents and updates targeted sections without wiping prior work |
| **A4 — Gate tier alignment** | Invokes `.ags/gates/` checks only when resolved `modes.review_mode` requires them (`full`); notes skips honestly |
| **A5 — Skeleton & traceability** | Preserves required section skeletons, `TR-ID` links, and engine reference checks (`docs/engine-reference/`) |

### `readiness` & `story-harness` (`ags-dev`, `ags-verify`)

| Metric | PASS criteria |
|---|---|
| **SH1 — Checkpoint #1 (Story approval)** | Presents story goal, scope, acceptance criteria, `Handoff Class`, and verification method and gets approval before implementation |
| **SH2 — Routine work proceeds cleanly** | Once story is approved, routine code edits and tests proceed without per-file write prompts; pauses only for scope, AC, consequential design/architecture, or engine changes |
| **SH3 — Bounded specialist consult** | Primary agent owns the story; invokes engine/domain specialists only for bounded sub-tasks |
| **SH4 — Game-Native rubric & receipt verification** | `ags-verify` delegates read-only code review (`code-reviewer`), runs `python .ags/cli.py verify`, and checks `.ags/state/receipt.json` matches current tree hash |
| **SH5 — Checkpoint #2 & Playtest Card** | Presents evidence mapped per AC; `Player-facing` / `Mixed` stories include a Playtest & Game Feel Tuning Card and require game-maker play before `Status: Complete`; missing runs are marked `NOT VERIFIED` |

### `pipeline` (`ags-plan`, `ags-gdd` map-systems, `ags-architect` manifest, `ags-design-review` propagate)

| Metric | PASS criteria |
|---|---|
| **P1 — Canonical template schema** | Outputs conform to `.ags/templates/` schemas (epics, stories with `Handoff Class`, manifests, traceability) |
| **P2 — Layer & dependency ordering** | Enforces Foundation -> Core -> Feature -> Presentation ordering and reads `python .ags/cli.py check adr-graph` |
| **P3 — Upstream grounding** | Reads authoritative GDDs, `tr-registry.yaml`, and Accepted ADRs before generating downstream artifacts |
| **P4 — Gate & decision discipline** | Triggers `PR-EPIC` / `QL-STORY-READY` / `TD-MANIFEST` according to `review_mode`, escalating unresolved blockers as `BLOCKED` |

### `analysis` (`ags-diagnose`, `ags-bugs`, `ags-design-review` consistency/balance/content, `ags-arch-review` tech-debt/scope)

| Metric | PASS criteria |
|---|---|
| **AN1 — Read-only investigation first** | Uses `scout` or `code-reviewer` (`sandbox_mode: read-only`) and deterministic CLI checks before proposing edits |
| **AN2 — Structured findings table** | Outputs ranked severity/priority findings with `file:line` citations and budget/threshold numbers |
| **AN3 — Explicit `NOT ASSESSED` coverage** | Reports unprofiled paths, missing tools, or unexpanded globs as `NOT ASSESSED`, never `PASS` |
| **AN4 — No silent mutations** | Does not auto-patch source code or auto-write registers without user scope approval |

### `team` (`ags-team`)

| Metric | PASS criteria |
|---|---|
| **T1 — Active-set announcement** | Explicitly announces resolved `team.size` (`full`, `lean`, `solo`), active roles/lenses, and any skipped roles |
| **T2 — Parallel independent fan-out** | Launches independent specialist/lens analyses in parallel; loads domain playbook from `references/team-*.md` |
| **T3 — Hard blocker surfacing** | Immediately surfaces `BLOCKED_ON_DECISION` / `REJECT` / `FAIL` and halts dependent steps |
| **T4 — Never silently collapse** | Never drops specialists silently or summarizes unrun specialists as passing |

### `sprint` (`ags-plan` sprint/milestone/retro, `ags-release` changelog/patch-notes)

| Metric | PASS criteria |
|---|---|
| **SP1 — Grounded production state** | Reads `production/sprints/`, `production/epics/`, `production/milestones/`, or git history before generating plans/notes |
| **SP2 — Correct sprint/milestone gates** | Evaluates `PR-SPRINT` / `PR-MILESTONE` at `full` mode and reports `lean`/`solo` skips honestly |
| **SP3 — Structured tables & velocity math** | Emits structured tables (capacity, velocity, risks, action items) with verified file links |

### `utility` (`ags-new-game`, `ags-start`, `ags-settings`, `ags-adopt`, `ags-qa`, `ags-localize`, `ags-release`, `ags-skill-ops`)

| Metric | PASS criteria |
|---|---|
| **U1 — Global invariants** | Passes all 6 Global Skill Invariants (`S1`–`S6`) |
| **U2 — Sub-mode & harness fidelity** | Preserves all sub-mode workflows in `references/*.md` and runs `ags` CLI helpers (`preflight`, `verify`, `check`, `doctor`, `init`, `sync`) accurately |

---

## Agent Role Categories (AGS v2)

### Read-Only Core Roles (`sandbox_mode: read-only`)

**Roles**: `scout`, `creative-director`, `technical-director`, `qa-lead`, `code-reviewer`

| Metric | PASS criteria |
|---|---|
| **RC1 — Strict read-only sandbox** | Frontmatter sets `sandbox_mode: read-only`; role never edits code, GDDs, or story files directly |
| **RC2 — Grounded verdict & citations** | Returns `file:line` citations, gate verdict (`APPROVE`/`CONCERNS`/`REJECT` or `ADEQUATE`/`INADEQUATE`), and `NOT ASSESSED` for uninspected areas |
| **RC3 — Correct reasoning tier** | `scout` uses `low`; `creative-director`, `technical-director`, `qa-lead`, `code-reviewer` use `high` |

### Workspace-Write Core Roles (`sandbox_mode: workspace-write`)

**Roles**: `producer`, `game-designer`, `art-ux-director`, `prototyper`, `gameplay-coder`, `tech-artist`, `test-engineer`

| Metric | PASS criteria |
|---|---|
| **WC1 — Flat worker escalation** | Emits `STATUS: BLOCKED_ON_DECISION` when product/architecture choices exceed approved scope instead of guessing |
| **WC2 — Engine & lens composition** | Applies `engine_overlay` (`docs/engine-reference/<engine>/`) and active `.ags/roles/<lens>.md` checklists when relevant |
| **WC3 — Lean body & clean contract** | Role file is concise (`<= 2.5 KB`), free of per-file write-approval boilerplate and host-specific leakage |

### Engine Specialist Packs (`core/agents/engines/{godot,unity,unreal}/`)

**Roles**: 5 Godot + 5 Unity + 5 Unreal specialists (`sandbox_mode: workspace-write`, `model_reasoning_effort: medium`)

| Metric | PASS criteria |
|---|---|
| **E1 — Version-pin grounding** | Checks `docs/engine-reference/<engine>/VERSION.md`, `deprecated-apis.md`, and `breaking-changes.md` before suggesting engine APIs |
| **E2 — Actionable implementation** | Can implement directly within assigned scope when delegated (contradictory "Must NOT implement" restriction removed) |
| **E3 — Engine isolation** | Only the project's configured engine pack is copied into `.ags/roles/` by `ags init` |

### Domain Lenses (`core/agents/lenses/`)

**Roles**: 22+ domain lenses preserving specialized checklists across art, audio, narrative, economy, networking, security, accessibility, performance, QA, and release operations.

| Metric | PASS criteria |
|---|---|
| **LN1 — Full parity preserved** | Domain checklists, formulas, and anti-patterns from all 49 original roles are preserved across core + engines + lenses |
| **LN2 — Composable role attachment** | Loaded into `.ags/roles/` cleanly and cited by core roles and `ags-team` without duplicate hierarchy conflicts |
