---
name: ags-verify
description: "Use when reviewing implemented code, auditing test/evidence quality, or running final Checkpoint #2 verification and closure on an approved story. Do NOT use when starting or implementing a story (-> ags-dev), running sprint QA suites (-> ags-qa), or advancing a project phase (-> ags-gate)."
---

# Code Review, Test Evidence Audit & Story Acceptance

Closes the Story Checkpoint Harness loop via read-only `code-reviewer` review (Game-Native Rubric), `python .ags/cli.py verify` static/engine verification receipts, deep test-evidence quality audit, and Checkpoint #2 game-maker acceptance. Only `ags-verify` may write `Status: Complete`.

## Contract
- **Inputs**: `production/epics/**/*.md` story (`Status: In Progress`, `**Story Approval**`, `Handoff Class:`, `Verification Method:`), `production/session-state/active.md`, changed source files under code root, `tests/`, `production/qa/evidence/`, `docs/architecture/{tr-registry.yaml,control-manifest.md,adr-*.md}`, `design/gdd/`, `project.yaml` / `project.local.yaml`
- **Roles**: Primary agent coordinates verification; `code-reviewer` (with `lead-programmer` and `security-engineer` lenses), `qa-lead`, `test-engineer`, `scout`, and configured engine specialists (`godot-specialist`, `godot-gdscript-specialist`, `godot-csharp-specialist`, `godot-shader-specialist`, `godot-gdextension-specialist`, `unity-specialist`, `unity-dots-specialist`, `unity-ui-specialist`, `unity-shader-specialist`, `unity-addressables-specialist`, `unreal-specialist`, `ue-blueprint-specialist`, `ue-gas-specialist`, `ue-replication-specialist`, `ue-umg-specialist`)
- **Outputs**: Read-only review report, `.ags/state/receipt.json` via `python .ags/cli.py verify`, Checkpoint #2 Story Handoff report, updated story (`Status: Complete`, `## Completion Notes` — ONLY after explicit game-maker acceptance), `production/sprint-status.yaml` (`done`), `production/session-state/active.md`, optional `production/qa/evidence-review-[date].md` and `docs/tech-debt-register.md`
- **Verification**: `python .ags/cli.py verify` receipt matching current tree hash + executed test/build output + retained screenshot inspection + game-maker play confirmation for `Player-facing`/`Mixed` stories
- **Next Skill**: `ags-dev` (for next ready story or revised scope approval), `ags-qa` (sprint smoke/QA close-out), `ags-gate` (phase advance after `ags-qa` sign-off), `ags-arch-review` (if tech debt logged)

## Preflight

Run once at startup and hold the resolved config:

```bash
python .ags/cli.py preflight ags-verify [story-path-or-scope]
```

- **Modes**:
  - `story` / default (`[story-path]`): runs internal `code-review` + `verify` receipt + `story-done` Checkpoint #2 closure in one flow.
  - `code-review [files] [story-path]`: strictly read-only Game-Native code review (`code-reviewer` + bounded specialists). Returns verdict to primary agent without routine user menu.
  - `evidence [story-path|sprint|system-name]`: deep test-file and manual-evidence quality review ([references/test-evidence-review.md](references/test-evidence-review.md)).
- **Overrides**: `--review [full|lean|solo]` overrides `modes.review_mode`. Resolve `workflow` per story via GDD filename stem (`workflow_overrides.system_overrides.<stem>`). Checkpoint #2 acceptance applies in **every** automation mode (`collaborative`, `guided`, `autonomous`).

## Phases

### Phase 1: Input & Approval-Drift Guard
1. Resolve target story (argument, else `production/session-state/active.md`, else `In Progress` stories in `production/sprints/`). If already `Status: Complete` with `Accepted By Game Maker`, report acceptance and stop.
2. Check **insufficient input**: list required inputs (`FOUND` / `ABSENT`). An absent input yields `NOT ASSESSED — NO DATA`; zero stories in `evidence` scope stops with `NOT ASSESSED — no stories in scope`.
3. **Approval integrity**: Verify `**Story Approval**`, `Handoff Class:`, `Verification Method:`, and the latest `active.md` approval extract. If missing or if scope, criteria, class, or method drifted, emit `NOT ASSESSED — story approval drift` and return to `ags-dev` before closure.
4. Load targeted `tr-registry.yaml` `id: <TR-ID>` entries, GDD rules/criteria, `control-manifest.md` header version, and bounded ADR `## Status` + `## Decision` / `## Consequences` sections.

### Phase 2: Read-Only Code Review & Verification Receipt
1. **Run `code-reviewer`** (`sandbox_mode: read-only`) against [references/code-review.md](references/code-review.md) using the **Game-Native Engine-Idiomatic Rubric** (engine composition/signals/subsystems, data-driven tuning, cohesive units, zero hot-path allocations/`delta` discipline, testability seams, ADR/manifest compliance).
2. Consult `specialists.*` (`null` = UNSET) or `test-engineer` only for bounded questions; record skipped checks by name (`Engine validation: NOT ASSESSED — no engine configured` when unset). Independently verify every specialist claim (`VERIFIED` vs `UNVERIFIED — specialist claim`).
3. Fix in-scope `CHANGES REQUIRED` issues via `ags-dev` and rerun checks. Pause immediately if an unresolved ADR/scope/engine decision arises.
4. **Verification Receipt**: Run `python .ags/cli.py verify` so `.ags/state/receipt.json` captures syntax/engine static checks and current tree hash (or document explicit `NOT VERIFIED — <reason>` when an engine binary is absent).

### Phase 3: Criteria, Deviations & Evidence Evaluation
1. Verify each acceptance criterion (`COVERED` via executed test output, retained `production/qa/evidence/[story-slug]/` screenshot, or pending game-maker play confirmation; >50% `UNTESTED` blocks unless `qa.level: minimal`). Unrun checks are `NOT VERIFIED — <reason>`, never `PASS`.
2. Enforce `qa.level` + `testing.strict.<key>` (`Logic`/`Integration`/`Visual/Feel`/`UI` default BLOCKING; `Config/Data` default ADVISORY in `story-done`).
3. Run workflow-adjusted deviation checks (GDD rules, manifest staleness, ADR constraints, hardcoded values, scope boundaries).
4. In `full` review mode only: spawn `qa-lead` for `QL-TEST-COVERAGE` (`.ags/gates/ql-test-coverage.md`, skipped at `qa.level: minimal`) and `code-reviewer` with `lead-programmer` lens for `LP-CODE-REVIEW` (`.ags/gates/lp-code-review.md`). In `lean` mode, fold the `code-review` verdict into Checkpoint #2. Full details in [references/story-done.md](references/story-done.md).

### Phase 4: Checkpoint #2 — Game-Maker Acceptance & Closure
1. Present the single **Story Handoff & Completion Report** mapping every criterion to executed evidence or a named gap, plus `Play steps` and Playtest & Game Feel Tuning Card for `Player-facing`/`Mixed` stories (`N/A — Technical` for Technical).
2. Wait for the single Checkpoint #2 decision (`Accept` / `Request fixes` / `Wait for play or missing evidence` / `Explicitly accept named gap`). A screenshot proves appearance, never play; `Player-facing` and `Mixed` stories stay `In Progress` until the game maker confirms playing.
3. On fixes/wait: keep `Status: In Progress`, record `Pending acceptance:` in `active.md`. On acceptance (or explicit named-gap override): write `Status: Complete`, `Last Updated`, `## Completion Notes` (preserving original `NOT VERIFIED`/gap records), `production/sprint-status.yaml`, `active.md`, and surface next ready story or sprint close-out sequence.

## Gate & Verdict

- **Verdict Precedence (Story Closure)**: `BLOCKED` > `NOT ASSESSED` > `COMPLETE WITH NOTES` > `COMPLETE` (`NOT ASSESSED` outranks `COMPLETE` and `COMPLETE WITH NOTES`, ranks below `BLOCKED`).
  - `BLOCKED`: failing criteria, missing BLOCKING test/visual evidence, `>50% UNTESTED` (when `qa.level` != `minimal`), `CHANGES REQUIRED` / `REJECT`, or `Proposed` ADR.
  - `NOT ASSESSED`: approval extract drift, unevaluable criterion, unreadable/corrupt evidence, missing governing GDD/ADR for deviation check, `NOT ASSESSED` from `evidence` sub-mode, or `NOT VERIFIED` required execution (cannot reach `COMPLETE` without explicit named-gap acceptance).
  - Pending game-maker play keeps `Player-facing`/`Mixed` stories `In Progress` (never `COMPLETE`).
- **Verdict Precedence (`code-review` sub-mode)**: `CHANGES REQUIRED` > `NOT ASSESSED` > `APPROVED WITH SUGGESTIONS` > `APPROVED`.
- **Verdict Precedence (`evidence` sub-mode)**: `MISSING` / `INCOMPLETE` > `NOT ASSESSED` > `ADEQUATE`. Full contract in [CONTRACT.md](CONTRACT.md).
