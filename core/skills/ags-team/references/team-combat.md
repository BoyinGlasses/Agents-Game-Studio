# Team Playbook: Combat (`ags-team combat`)

Orchestrates design, engine-validated architecture, parallel implementation, integration, QA validation, and sign-off for a combat feature.

## Argument & Role Mapping

- **Argument check**: Requires `[combat feature description]` (e.g., `melee parry system`, `ranged weapon spread`). If omitted, output usage (`ags-team combat <combat feature description>`) and stop immediately without reading project files or spawning roles.
- **Decision Points**: Follow `modes.automation` (`collaborative` asks at every gate; `guided` advances unless BLOCKED; `autonomous` records each skipped gate to `production/session-logs/decision-log.md`, still prompting for `modes.automation_always_ask` categories).

### Active-Set (`team.size`) & Role Mapping

- **`individual`** (default): `gameplay-coder` runs the pipeline; escalate `ai-programmer` lens only if the feature requires enemy/NPC AI behavior. All other roles consulted through `gameplay-coder`.
- **`small`**: Full Team Composition pipeline below.
- **`studio`**: Full pipeline + engine sub-specialists + adversarial review pass (`code-reviewer`).
- **Role map**:
  - `game-designer` -> `.ags/roles/game-designer.md`
  - `gameplay-coder` -> `.ags/roles/gameplay-coder.md`
  - `ai-programmer` lens -> `gameplay-coder` (`.ags/roles/ai-programmer.md`)
  - `tech-artist` -> `.ags/roles/tech-artist.md`
  - `sound-designer` lens -> `tech-artist` (`.ags/roles/sound-designer.md`)
  - Engine specialist -> `.ags/roles/<engine>-specialist.md`
  - `test-engineer` -> `.ags/roles/test-engineer.md`

Announce the active roster, unspawned roles routed through `gameplay-coder`, and engine status before Phase 1.

## Concrete Artifact Paths

| Phase / Role | Writes To | Notes |
|---|---|---|
| Phase 1 `game-designer` | `design/gdd/[feature].md` | GDD convention |
| Phase 2 `gameplay-coder` | `docs/architecture/[feature]-sketch.md` | Pre-ADR working sketch (inform user no downstream gate consumes sketches directly) |
| Phase 2 `<engine>-specialist` | `docs/architecture/[feature]-engine-notes.md` | Working sketch notes |
| Phase 5 `test-engineer` (cases) | `production/qa/test-cases/[feature]-cases.md` | Consumed by `ags-team qa` |
| Phase 5 `test-engineer` (bugs) | `production/qa/bugs/BUG-[NNN]-[slug].md` | Consumed by `ags-bugs` / `ags-team qa` |

Phase 6 outputs a summary report directly (no separate artifact path).

## Pipeline

### Phase 1: Design (`game-designer`)

Delegate to `game-designer` to author or update `design/gdd/[feature].md` covering:
- Mechanic overview and player fantasy
- Detailed rules
- Formulas with variable definitions
- Edge cases and dependencies
- Tuning knobs with safe ranges
- Acceptance criteria

### Phase 2: Architecture (`gameplay-coder` + `<engine>-specialist`)

1. Delegate to `gameplay-coder` (with `ai-programmer` if NPC/enemy AI is involved) to review the design doc, design class/node/component structures, interfaces, data flow, and system integration points, writing `docs/architecture/[feature]-sketch.md`.
2. Delegate to `<engine>-specialist` (from `engine.name` in `project.yaml`, referencing `docs/engine-reference/<engine>/`):
   - Validate whether class/node/component structure is idiomatic (Godot node hierarchy, Unity MonoBehaviour vs DOTS, Unreal Actor/Component/GAS).
   - Identify engine-native systems to prefer over custom code.
   - Check deprecated/changed APIs in the pinned engine version.
   - Write `docs/architecture/[feature]-engine-notes.md` and incorporate notes before Phase 3.
   - If `engine.name` is unset or `null`, skip specialist spawn and record `Engine validation: NOT ASSESSED — no engine configured (engine.name unset in project.yaml)`.
3. **Architecture Gate**: Present architecture sketch + engine notes to the user:
   - `[A] Proceed — run parallel implementation`
   - `[B] Revise the architecture first`
   - `[C] Stop here`
   In `guided` / `autonomous` modes, proceed unless Phase 2 returned `BLOCKED` (log decision in `autonomous`).

### Phase 3: Implementation (Parallel)

Issue parallel delegations:
- **`gameplay-coder`**: Implement core combat mechanic code.
- **`ai-programmer`**: Implement AI behaviors (if the feature involves NPC reactions).
- **`tech-artist`**: Create VFX and shader effects.
- **`sound-designer`**: Define audio event list and mixing notes.

### Phase 4: Integration

- Wire together gameplay code, AI, VFX, and audio.
- Ensure all tuning knobs are exposed and data-driven (external config/data files, zero magic numbers).
- Verify compatibility with existing combat systems.

### Phase 5: Validation (`test-engineer`)

Delegate to `test-engineer` to:
- Write test cases derived from GDD acceptance criteria to `production/qa/test-cases/[feature]-cases.md`.
- Test all documented edge cases.
- Verify performance impact remains within frame/memory budgets.
- File bug reports under `production/qa/bugs/BUG-[NNN]-[slug].md` for any defects found.

### Phase 6: Sign-off

Collect results across all roles and report feature status (`COMPLETE` / `NEEDS WORK` / `BLOCKED`) with open issues, owners, active/skipped roster, and engine validation status.

## Verdicts & Next Steps

- **COMPLETE**: Combat feature designed, implemented, integrated, and validated (with active/skipped roster and engine status stated).
- **NEEDS WORK / CONCERNS**: Implemented with non-blocking open defects or unverified optional polish.
- **NOT ASSESSED**: Engine validation skipped (`engine.name` unset) or validation tests could not execute.
- **BLOCKED**: Missing prerequisite GDD, `Proposed` ADR (`ags-architect architecture-decision`), oversized scope (`ags-plan create-stories`), or unresolved ADR conflict.
- **Next Skills**:
  - `ags-verify` for code review and story closure.
  - `ags-design-review balance-check` to validate combat formulas and tuning knobs.
  - `ags-team polish` for VFX, audio, or performance hardening.
