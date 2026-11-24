# Read-Only Code Review & Game-Native Rubric (`ags-verify`)

Evaluates implemented code using `code-reviewer` (`sandbox_mode: read-only`) and bounded engine/test specialists against engine-idiomatic game architecture rather than dogmatic Java-style rules. Strictly read-only — never edits files.

## 1. Insufficient Input Guard

Before reviewing, check target files, engine config, and optional story/ADR inputs (`FOUND` / `ABSENT`).
- If all target files are absent/unreadable, stop with `NOT ASSESSED — NO DATA`.
- If `engine.name` is unset (`project.yaml` and technical preferences), skip engine specialist consultation and explicitly output: `Engine validation: NOT ASSESSED — no engine configured`.

## 2. Specialist Identification & Claim Verification

Read `specialists.*` from `project.yaml` (treat `"null"` / empty / missing as UNSET and fall back to `<engine>-specialist` from `engine.name` or technical preferences):
- `.gd` / `.cs` / `.cpp` -> `specialists.code`
- `.gdshader` / `.hlsl` / shader graphs -> `specialists.shader`
- UI widgets / screens -> `specialists.ui`
- Architecture / scene lifecycle -> `<engine>-specialist`
- Testability seams (`Logic`/`Integration` or manual state reachability for `Visual/Feel`/`UI`) -> `test-engineer` / `qa-lead`

Spawn independent bounded consultations in parallel and wait for all before reporting. Name skipped specialists explicitly (`Specialist consultation: SKIPPED — no bounded question`).

**Mandatory Specialist Claim Verification**:
Never pass specialist findings through unchecked. For every specialist finding reported, record:
- **File and line** (`path:line`)
- **Evidence** (quoted code or concrete triggering input/state)
- **Confidence**: `VERIFIED` (independently confirmed in source) or `UNVERIFIED — specialist claim` (not directly confirmed; never promote to a defect without verification)

## 3. Bounded ADR Compliance Check

Identify governing ADRs from: (1) story argument, (2) file header comments, or (3) recent git commit messages (`git log --oneline -- [file]`). If none exist, record `"No ADR references found — ADR compliance check skipped."`

For each referenced ADR:
1. Read `## Status` first. `Proposed` -> `CHANGES REQUIRED` (`ARCHITECTURE RISK`) and pause active story for game-maker decision. Unreadable status -> `NOT ASSESSED`.
2. Map headings (`^## ` with line numbers) and bounded-read ONLY `## Decision` and `## Consequences` (full read only if headingless legacy file; search for decision/consequence content if over cap).
3. Classify deviations: **ARCHITECTURAL VIOLATION** (BLOCKING — uses rejected pattern), **ADR DRIFT** (WARNING), **MINOR DEVIATION** (INFO).

## 4. Game-Native Engine-Idiomatic Rubric

Evaluate against real game engine engineering rather than arbitrary line-count or Java constructor-DI dogma:

1. **Engine-Idiomatic Composition & Layer Boundaries**:
   - Uses native engine decoupling (`Node`/signals/`Resource` in Godot; `ScriptableObject`/events/Burst/Jobs/subsystems in Unity; `UActorComponent`/`UGameInstanceSubsystem`/GAS/delegates in Unreal).
   - Strict dependency direction (`engine <- gameplay`), no circular dependencies, UI never owns simulation state, no raw unguarded global mutable state across systems.
2. **Data-Driven Tuning**:
   - Gameplay parameters, curves, cooldowns, and damage/economy formulas live in config/data assets (`.tres`/`.res`, `ScriptableObject`, `DataTable`/`DataAsset`, JSON/YAML) rather than hardcoded magic literals in logic paths.
3. **Cohesive, Readable Units**:
   - Functions and components maintain clear single responsibilities and shallow control flow; state machines use explicit state definitions/tables rather than fragile flag webs — without forcing artificial 40-line method splitting or pointless single-impl interfaces.
4. **Hot-Path & Resource Hygiene**:
   - Frame-rate independence (`delta`/`DeltaTime`), zero per-frame allocations or expensive scene-tree lookups (`get_nodes_in_group`, `FindObjectOfType`, `GetComponent`, `GetAllActorsOfClass`) inside `_process`/`_physics_process`/`Update`/`Tick`.
   - Deterministic cleanup (`queue_free`, object pooling, `Dispose`, unsubscribed signals/delegates), thread safety where multi-threaded, null/empty guards.
5. **Testability & Direct Scene Reachability**:
   - Pure logic/formulas separated from rendering/scene nodes for deterministic headless unit tests; player-facing features expose direct scene/map launch or debug state args for `run-and-observe` capture.
6. **Public API Clarity & Standards**:
   - Concise doc comments on public classes, signals, exported knobs, and shared utilities; complies with `AGENTS.md` and `.ags/rules/`.

## 5. Review Output & Handoff

Emit sections: `Engine Specialist Findings`, `Testability`, `ADR Compliance`, `Game-Native Rubric Compliance`, `Architecture & Boundaries`, `Game-Specific Concerns`, `Positive Observations`, `Required Changes`, `Suggestions`, and `Verdict: [NOT ASSESSED | APPROVED | APPROVED WITH SUGGESTIONS | CHANGES REQUIRED]`.

- **Within active approved story**: Return findings directly to primary agent (`ags-verify` Phase 3/4) — do NOT open a routine user menu on `APPROVED` / `APPROVED WITH SUGGESTIONS`. For `CHANGES REQUIRED`, primary agent resolves in-scope fixes and reruns `python .ags/cli.py verify` + review checks before Checkpoint #2.
- **Unresolved ADR / Scope / Engine conflict**: Pause related work immediately and ask the game maker in every automation mode. Never silently revise an ADR; use `ags-architect` after decision approval.
