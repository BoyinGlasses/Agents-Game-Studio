---
name: ags-dev
description: "Use when validating story readiness or approving and implementing an approved game story within the Story Checkpoint Harness. Do NOT use when reviewing/closing a completed story (-> ags-verify), planning epics/stories (-> ags-plan), or running standalone QA suites (-> ags-qa)."
---

# Story Readiness & Development

Implements one approved game story from pre-implementation readiness through Checkpoint #1, bounded implementation, local verification, and automatic handoff to `ags-verify`.

## Contract
- **Inputs**: Story file (`production/epics/**/*.md`), `production/session-state/active.md`, `design/gdd/systems-index.md`, `docs/architecture/{tr-registry.yaml,control-manifest.md,adr-*.md}`, `project.yaml` / `project.local.yaml`, `docs/engine-reference/<engine>/VERSION.md`
- **Roles**: Primary agent implements; `qa-lead` (read-only `QL-STORY-READY` in full review mode), `scout` (optional lookup); bounded consult with `gameplay-coder`, `tech-artist`, `test-engineer`, or configured engine specialist (`godot-specialist`, `godot-gdscript-specialist`, `godot-csharp-specialist`, `godot-shader-specialist`, `godot-gdextension-specialist`, `unity-specialist`, `unity-dots-specialist`, `unity-ui-specialist`, `unity-shader-specialist`, `unity-addressables-specialist`, `unreal-specialist`, `ue-blueprint-specialist`, `ue-gas-specialist`, `ue-replication-specialist`, `ue-umg-specialist`)
- **Outputs**: Readiness report (readiness-only mode), approved story header (`Handoff Class:`, `Verification Method:`, `**Story Approval**: YYYY-MM-DD`, `Status: In Progress`), `production/sprint-status.yaml` (`in_progress`), `production/session-state/active.md` extract, source files under code root, tests in `tests/`, retained screenshots in `production/qa/evidence/`, Playtest & Game Feel Tuning Card for Player-facing/Mixed stories
- **Verification**: Configured parse/import check + test runner (`commands.test`/`commands.smoke`) + windowed launch & screenshot inspection for player-observable changes; `NOT VERIFIED — <reason>` when unexecuted
- **Next Skill**: `ags-verify` (automatic continuation in same task; `ags-plan` if stories are missing or must split)

## Preflight

Run once at startup and hold the resolved config for the run:

```bash
python .ags/cli.py preflight ags-dev [story-path-or-scope]
```

- **Modes**: `readiness [path|sprint|all]` (strictly read-only readiness gate) or `implement [story-path]` (default: runs readiness on a new `Ready` story, pauses at Checkpoint #1, implements, and hands off to `ags-verify`; resumes directly on an approved `In Progress` story with matching session extract).
- **Per-story tier resolution**: Resolve `modes.workflow` per story from `workflow_overrides.system_overrides.<stem>` where `<stem>` is the `design/gdd/<stem>.md` filename stem (`TR-[system]-NNN` is fallback alias only), else project `workflow`, else `modes.rigor`.
- **Overrides**: `--review [full|lean|solo]` overrides `modes.review_mode` for this run. `qa.level` and `testing.strict.<type>` govern test-evidence obligations independently of `workflow`; neither waives Checkpoint #1 or player-observable run observation.

## Phases

### Phase 1: Scope, Readiness & Context Load
1. **If `readiness` mode**: Follow [references/story-readiness.md](references/story-readiness.md) strictly read-only. Zero resolved story files (`all`, `sprint`, or path) MUST emit `NOT ASSESSED — no stories in scope` with remediation (`ags-plan`). Distinguish absent sprint file from empty sprint story list.
2. **If `implement` mode**:
   - Resolve story path (argument, else active story in `production/session-state/active.md`, else list `Ready` stories in `production/epics/`).
   - Always read `production/session-state/active.md` (if present) for the latest approval extract and pending decision matching this story path.
   - For a new `Ready` story, run the readiness checklist in [references/story-readiness.md](references/story-readiness.md) first; proceed to Phase 2 only on `READY`.
   - Load context in parallel only for independent unconditional reads (`story` + targeted TR-ID lookup in `tr-registry.yaml`). Do NOT read the governing ADR unconditionally: check `## Status` (a `Proposed` ADR BLOCKS at `full`, or at `standard`/`minimal` when referenced; unreadable status is `NOT ASSESSED`) and `## Last Verified` against `**ADR Version**`; open ADR (`<50KB` whole, `>=50KB` `## Decision`, `## Engine Compatibility`, `## ADR Dependencies` only) only on date mismatch with user choice `[A]`. Read only the story's layer in `control-manifest.md` and validate dependencies. Full rules in [references/dev-story.md](references/dev-story.md).

### Phase 2: Checkpoint #1 — Story Approval
Mandatory human checkpoint in **every** automation mode (`collaborative`, `guided`, `autonomous`).
1. Check `Handoff Class:` (`Player-facing | Technical | Mixed`) and `Verification Method:`. For legacy stories missing either field, propose both from actual acceptance criteria and configured commands — NEVER infer `Technical` solely from `Type: Logic`.
2. Present one Checkpoint #1 card with Story, Scope (including `Out of Scope`), every Acceptance Criterion, `Handoff Class`, `Verification Method`, and `Decision: [Approve this story | Revise the story]`.
3. **Resume guard**: An `In Progress` story skips Checkpoint #1 ONLY when `**Story Approval**` exists, no pending decision exists for this story, and current scope, criteria, `Handoff Class`, and `Verification Method` match the latest approval extract in `active.md`. Any drift or missing approval requires Checkpoint #1 before edits.
4. **On approval**: Persist missing handoff fields, approved ADR/manifest version updates, `**Story Approval**: YYYY-MM-DD`, `Status: In Progress`, `Last Updated`, `production/sprint-status.yaml` (`in_progress`, or report `Sprint status not updated: production/sprint-status.yaml absent`), and the approval extract in `active.md`. Approval authorizes all routine in-scope source, test, and evidence file writes (including new files) without per-file permission prompts.

### Phase 3: Bounded Implementation & Specialist Consult
1. **Primary-agent ownership**: Implement within approved scope under the resolved code root (`src/` Godot, `Assets/Scripts/<System>/` Unity, `Source/<Module>/<System>/` Unreal). Stop if the code root cannot be resolved.
2. **Bounded specialist consultation**: Skip for `Config/Data`. Otherwise consult `specialists.*` (`null` = UNSET, fall back to `<engine>-specialist` from `engine.name`) or domain roles only for concrete engine/domain risks. Read `docs/engine-reference/<engine>/VERSION.md`; its risk rating overrides any improvised card `Risk:` and unknown counts as `HIGH`. Report each consult as result, `SKIPPED — <reason>`, or `NOT ASSESSED — specialist unavailable`.
3. **Scope-change pause**: Before touching an out-of-scope file, changing acceptance criteria or handoff fields, making a consequential gameplay/architecture choice, or changing the engine, STOP, append `Pending decision: [story path, change, proposed scope]` to `active.md`, preserve in-scope work, and present a revised Checkpoint #1 card.
4. **Player-facing & Mixed stories**: Complete the Playtest & Game Feel Tuning Card in [references/playtest-tuning-card.md](references/playtest-tuning-card.md) exposing tunable knobs, feel targets, direct launch path, and play steps.

### Phase 4: Local Verification & Handoff to `ags-verify`
1. Confirm implementation is complete (not partial/`INCOMPLETE`), run parse/import check (`parse NOT VERIFIED — engine binary not available` if missing), and write/run tests per `testing.strict` and `qa.level` (at `qa.level: minimal`, emit the explicit test-waiver line).
2. For every story with a player-observable surface (not waived at `qa.level: minimal`), launch windowed (`commands.run`), inspect retained screenshot(s) under `production/qa/evidence/[story-slug]/`, and emit `Run result: OBSERVED — ...`, `Run result: NOT VERIFIED — ...`, or `Run result: N/A — ...`.
3. Update `production/session-state/active.md` (per `.ags/templates/session-state.md` extract schema) and continue immediately in the same task to `ags-verify` with changed files and story path. Never set `Status: Complete` in `ags-dev`.

## Gate & Verdict

- **Readiness Verdict Precedence** (first match wins): `BLOCKED` > `NEEDS WORK` > `NOT ASSESSED` > `READY`.
  - `BLOCKED`: missing/Draft dependency story, `Proposed`/missing governing ADR (per tier), or unowned `UNRESOLVED` design marker.
  - `NEEDS WORK`: failing testable criteria, invalid `Handoff Class` or vague `Verification Method`, stale manifest, missing assets, or insufficient criterion count (`Logic`/`Integration` >= 3, `Visual/Feel`/`UI` >= 2, `Config/Data` >= 1). Missing handoff fields on legacy stories emit `ADVISORY: classify at the dev-story approval checkpoint` without downgrading `READY`.
  - `NOT ASSESSED`: zero stories in scope, unreadable/unparseable story, or unreadable ADR `## Status` (distinct from `BLOCKED`; `READY` is unreachable without evaluation).
  - `QL-STORY-READY` (`.ags/gates/ql-story-ready.md`) runs via `qa-lead` only in `full` review mode; skipped with announcement in `lean`/`solo`.
- **Implementation Handoff Gate**: Incomplete edits -> `INCOMPLETE` (fix before handoff); approved, parsed, tested/observed (or explicitly `NOT VERIFIED`) -> `READY FOR VERIFY` -> invoke `ags-verify`. Full contract in [CONTRACT.md](CONTRACT.md).
