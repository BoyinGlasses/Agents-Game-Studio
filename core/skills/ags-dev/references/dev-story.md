# Story Implementation Workflow (`ags-dev` Implement Mode)

Executes Checkpoint #1, primary-agent implementation, bounded specialist consultation, verification, and handoff to `ags-verify` in one continuous task.

## 1. Story Resolution & Resume Guard

1. **Resolve story path**: Use explicit path argument; else active story in `production/session-state/active.md`; else list `Ready` stories in `production/epics/**/*.md`.
2. **Always read `production/session-state/active.md`** (even when path was supplied). Select the latest approval extract and pending decision for this exact story path (pending decisions for other stories do not affect this story).
3. **Resume classification**:
   - `Status: Ready` (new story): Run [story-readiness.md](story-readiness.md) first; stop unless verdict is `READY`.
   - `Status: In Progress` with `**Story Approval**: YYYY-MM-DD`, matching `scope` / `Out of Scope` / `Acceptance Criteria` / `Handoff Class` / `Verification Method` in the latest `active.md` approval extract, and `Pending decision: None`: resume automatically at Phase 3 without repeating Checkpoint #1 or re-running readiness.
   - `Status: In Progress` missing `**Story Approval**`, missing extract, showing field drift, or carrying an unresolved `Pending decision:`: do NOT infer consent; run Checkpoint #1 with the revised card before any edits.

## 2. Context Loading & Bounded Reads

Resolve per-story `workflow` tier via GDD filename stem (`workflow_overrides.system_overrides.<stem>` -> `modes.workflow` -> `modes.rigor`). Enforce tier prerequisites:
- `full`: missing `docs/architecture/tr-registry.yaml` or missing/`Proposed` governing ADR -> set `BLOCKED` in `active.md` and stop (`ags-arch-review` / `ags-architect`). Missing `control-manifest.md` -> WARN and continue (`ags-architect`).
- `standard`/`minimal`: only a referenced ADR that is missing or `Proposed` blocks; absent TR registry or absent-by-design ADR does not block.

**Bounded read sequence**:
1. Read story file and extract targeted `id: <TR-ID>` entry from `docs/architecture/tr-registry.yaml` in parallel. Do NOT bundle the governing ADR into this batch.
2. **ADR status & freshness**:
   - Read `## Status` of every referenced ADR at every tier. `Proposed` -> BLOCK (`ags-architect [path]`); unreadable -> `NOT ASSESSED`, stop before Checkpoint #1.
   - Compare ADR `## Last Verified` line against story `**ADR Version**`:
     - Match -> trust story's `**ADR Decision Summary**` & `## Implementation Notes`; do NOT read full ADR.
     - Story lacks `**ADR Version**` -> trust summary; note `"Story predates ADR Version stamp; summary trusted unverified."`
     - ADR lacks `## Last Verified` and story says `unversioned` -> trust summary; recommend `ags-architect` retrofit.
     - ADR lacks `## Last Verified` but story has a date, OR dates differ -> prompt `[A] Re-read changed ADR sections (Recommended)`, `[B] Accept drift risk`, `[C] Stop for ADR diff`. On `[A]`: read whole ADR if `<50KB`, or bounded-read only `## Decision`, `## Engine Compatibility`, `## ADR Dependencies` if `>=50KB`. Hold updated `ADR Version` for post-approval write.
3. **Control manifest**: Read only `## <layer> Layer Rules` in `docs/architecture/control-manifest.md`. If story `Manifest Version:` differs from header date, ask `[A] Update and follow current rules`, `[B] Proceed on old rules (log Manifest-Note)`, or `[C] Stop`.
4. **Dependencies**: Verify each dependency story exists and is `Complete`/`Done` (otherwise prompt `[A] Accept risk`, `[B] Stop & BLOCK`, `[C] Verify dependency via ags-verify`).

## 3. Checkpoint #1 & State Transition

If legacy story lacks `Handoff Class:` or `Verification Method:`, derive both from acceptance criteria and configured commands (never infer `Technical` solely from `Type: Logic`). Present one card in **every** automation mode:

```markdown
Story: [path and goal]
Scope: [files or boundaries, including Out of Scope]
Acceptance criteria: [every criterion]
Handoff Class: [Player-facing | Technical | Mixed]
Verification Method: [build/test command, evidence path, and play steps if required]
Decision: [Approve this story | Revise the story]
```

Wait for explicit `Approve this story`. On approval:
1. Write missing `Handoff Class:` / `Verification Method:`, held `ADR Version` / `Manifest Version` / `Manifest-Note`, `**Story Approval**: YYYY-MM-DD`, `Status: In Progress`, and `Last Updated: YYYY-MM-DD`. Never write `Complete`.
2. Update `production/sprint-status.yaml` (`status: in_progress`, `updated: YYYY-MM-DD`) if present; otherwise emit `"Sprint status not updated: production/sprint-status.yaml absent"`.
3. Write the full approval extract + `Pending decision: None` to `production/session-state/active.md`.

## 4. Implementation, Specialist Consult & Scope Pause

- **Code root resolution**: `src/` (Godot), `Assets/Scripts/<System>/` (Unity), `Source/<Module>/<System>/` (Unreal) per `project.yaml`. Stop if unresolved.
- **Specialist selection**: Skip for `Config/Data`. Read `specialists.*` directly from `project.yaml` (`specialists.code`, `specialists.shader`, `specialists.ui`; treat `null` as UNSET and fall back to `<engine>-specialist` from `engine.name`, else technical-preferences). Read `docs/engine-reference/<engine>/VERSION.md`; `VERSION.md` risk overrides story `Risk:` (unknown = `HIGH`, triggers specialist consult on the named post-cutoff API).
- **Brief discipline**: Pass targeted paths, inline `**ADR Decision Summary**` / `## Implementation Notes` (not full ADR path unless deferred), TR requirement, manifest layer rules, `naming.*` / `performance.*`, and test requirement (omit test requirement at `qa.level: minimal` and explicitly state tests are waived). Always announce dropped/absent context items to both specialist and user.
- **Scope-change pause**: Before any out-of-scope file edit, acceptance-criteria or handoff-field change, consequential gameplay/architecture choice, or engine change: STOP, append `Pending decision: [story path, affected file/decision, proposed scope]` to `active.md`, preserve completed in-scope work, and present a revised Checkpoint #1 card.
- **Player-facing & Mixed stories**: Fill [playtest-tuning-card.md](playtest-tuning-card.md) (knobs exposed, feel targets, direct launch path, play steps).

## 5. Local Verification & Session Extract

1. Confirm all edits finished cleanly (partial/broken state = `INCOMPLETE`, fix before proceeding).
2. Run cheapest engine parse/import check (`commands.test`, `commands.smoke`, or `godot --headless --path . --import`); if engine binary unavailable, write `parse NOT VERIFIED — engine binary not available`.
3. Run `testing.strict` / `qa.level` test check: at `qa.level: minimal`, emit `> *Test evidence: **waived** at qa.level: minimal — no test was required or written for this story.*`; otherwise write & execute tests (`[system]_[feature]_test.[ext]`, `test_[scenario]_[expected_outcome]`) and record command + outcome (unrun = `NOT VERIFIED — <reason>`).
4. **Run and observe** (not waived at `qa.level: minimal`): For any player-observable surface, launch windowed via `commands.run` into the target scene/map, inspect retained PNG under `production/qa/evidence/[story-slug]/`, and record `Run result: OBSERVED — <what was on screen> (<path>)`, `Run result: NOT VERIFIED — <reason>`, or `Run result: N/A — <reason>` (state explicitly what Visual/Feel *look* vs *feel* was covered).
5. Append `## Session Extract — ags-dev [date]` to `production/session-state/active.md` (`Code review: Pending`, `Next: ags-verify`) and proceed immediately to `ags-verify`.
