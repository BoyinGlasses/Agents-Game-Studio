# Team Playbook: UI (`ags-team ui`)

Orchestrates context gathering, UX spec authoring (`ags-art-ux`), UX review, visual design, engine-validated UI implementation, multi-stream review, and polish.

## Active-Set & Role Mapping (`team.size`)

- **`individual`** (default): `ui-programmer` (via `gameplay-coder`) + `ux-designer` (via `art-ux-director`). Other roles consulted through these two.
- **`small`**: + `accessibility-specialist` + `art-director`.
- **`studio`**: + engine UI specialist + adversarial review (`code-reviewer`).
- **Director gate skip rule**: Skip non-`PHASE-GATE` director reviews at `lean`; skip all director gates at `solo`.
- **Role map**:
  - `ux-designer` lens -> `art-ux-director` (`.ags/roles/ux-designer.md`)
  - `art-director` lens -> `art-ux-director` (`.ags/roles/art-director.md`)
  - `accessibility-specialist` lens -> `art-ux-director` (`.ags/roles/accessibility-specialist.md`)
  - `ui-programmer` lens -> `gameplay-coder` (`.ags/roles/ui-programmer.md`)
  - Engine UI specialist -> `specialists.ui` in `project.yaml` (`.ags/roles/unity-ui-specialist.md`, `.ags/roles/ue-umg-specialist.md`, `.ags/roles/godot-specialist.md`)

**`specialists.ui: null` rule**: Treat `null` or `""` as UNSET — skip engine UI specialist and never pass `"null"` as a role name.

Announce the active roster, unspawned roles, and engine UI status before Phase 1a.

## Templates

- `.ags/templates/ux-spec.md` — Standard screen/flow UX specification
- `.ags/templates/hud-design.md` — HUD-specific UX specification
- `.ags/templates/interaction-pattern-library.md` — Reusable interaction patterns
- `.ags/templates/accessibility-requirements.md` — Committed accessibility tier and requirements

## Pipeline

### Phase 1a: Context Gathering

Read and **explicitly report status (`present` or `ABSENT`) for every one of these five documents** before designing anything:
1. `design/gdd/game-concept.md` — platform targets and audience
2. `design/player-journey.md` — player state/context reaching this screen
3. Relevant GDD UI Requirements sections
4. `design/ux/interaction-patterns.md` — existing patterns to reuse
5. `design/accessibility-requirements.md` — committed accessibility tier (e.g., Basic, Enhanced, Full)

**Mandatory Accessibility Tier Guard**:
- If `design/accessibility-requirements.md` is `ABSENT`:
  - Surface immediately: there is no committed accessibility tier, so Phase 4 cannot silently pass an absent standard.
  - Record for Phase 4: `Accessibility: NOT ASSESSED — no committed tier (design/accessibility-requirements.md absent)` and forbid marking the accessibility gate as passed.
  - Require `ux-designer` to declare the **assumed** tier used while drafting.
  - Recommend `ags-art-ux ux-design accessibility` to establish the committed tier.
- If `game-concept.md`, `player-journey.md`, or `design/ux/hud.md` is `ABSENT`: non-blocking, but name each missing doc in the `ux-designer` brief so missing context is explicit rather than inferred.
- **If `design/ux/interaction-patterns.md` is `ABSENT`**: surface immediately (`interaction-patterns.md does not exist — no existing patterns to reuse`) and ask the user:
  - `(a)` Run `ags-art-ux ux-design patterns` first, then resume.
  - `(b)` Proceed without pattern library — instruct `ui-programmer` in Phase 3 to treat all new patterns as novel and document them in a new `design/ux/interaction-patterns.md` upon completion.

### Phase 1b: UX Spec Authoring

Invoke `ags-art-ux ux-design [feature name]` (or delegate directly to `ux-designer`) using `.ags/templates/ux-spec.md` (or `.ags/templates/hud-design.md` when argument is `hud`). Output: `design/ux/[feature-name].md`. Note `ags-art-ux ux-design patterns` establishes the reusable pattern library.

### Phase 1c: UX Review Gate

Invoke `ags-art-ux ux-review design/ux/[feature-name].md`.
- **Gate**: Do not advance to Phase 2 until verdict is `APPROVED`. If `NEEDS REVISION`, `ux-designer` revises and re-reviews. User may explicitly accept a `NEEDS REVISION` risk only after inspecting the specific concerns.

### Phase 2: Visual Design (`art-director`)

Delegate to `art-director` to:
- Review full UX spec (flows, wireframes, patterns, accessibility notes).
- Apply art-bible treatment (colors, typography, spacing, motion style).
- Verify contrast ratios and ensure color is never the sole state indicator (reinforce with shape, text, or icon).
- Specify exact asset deliverables (icon dimensions, textures, fonts, decorative elements, formats) and ensure consistency with existing UI screens.

### Phase 3: Engine Validation & Implementation

1. **Engine UI Specialist** (from `specialists.ui` or `engine.name` in `project.yaml`, referencing `docs/engine-reference/<engine>/`):
   - Recommend engine UI framework (Unity UI Toolkit vs UGUI, Godot Control/CanvasLayer, Unreal UMG vs CommonUI), widget/node structure, and layout/input gotchas.
   - If `engine.name` is unset or `specialists.ui` is `null` with no engine fallback, skip spawn and record:
     `Engine validation: NOT ASSESSED — no engine configured (engine.name unset in project.yaml)`
2. **Implementation (`ui-programmer`)**:
   - Implement from UX spec + visual spec.
   - Reuse patterns from `design/ux/interaction-patterns.md`; flag any necessary deviations for `ux-designer` review, and add newly invented patterns to `design/ux/interaction-patterns.md` before finishing.
   - Enforce separation: **UI never owns or modifies game state** — display only, emit events/signals for player actions.
   - Route all player-facing text through the localization system (zero hardcoded strings).
   - Support both keyboard/mouse and gamepad inputs; implement the committed (or declared assumed) accessibility tier.

### Phase 4: Multi-Stream Review (Parallel)

Delegate simultaneously and wait for all three:
- **`ux-designer`**: Verify implementation matches wireframes/interaction spec, keyboard-only and gamepad-only navigation, and accessibility features.
- **`art-director`**: Verify art-bible visual fidelity across minimum and maximum supported resolutions.
- **`accessibility-specialist`**: Audit against `design/accessibility-requirements.md` and flag violations as blockers. If `design/accessibility-requirements.md` is absent, report `Accessibility: NOT ASSESSED — no committed tier (design/accessibility-requirements.md absent)` and do NOT mark the gate as passed (explicitly cite the assumed tier from Phase 1a).

### Phase 5: Polish

- Address review feedback; ensure animations are skippable and respect reduced-motion preferences.
- Route UI sound triggers through the audio event system (no direct audio calls).
- Test across all supported resolutions and aspect ratios.
- Confirm `design/ux/interaction-patterns.md` includes any newly introduced patterns.
- Confirm HUD elements satisfy budgets (element count, screen region allocations, max opacity) in `design/ux/hud.md`.

## Verdicts & Next Steps

- **COMPLETE**: UX spec approved, visual spec delivered, UI implemented and verified across UX, art, accessibility, and engine checks.
- **NOT ASSESSED**: `design/accessibility-requirements.md` absent or engine validation skipped (`engine.name` unset) — surfaced explicitly; accessibility/engine gates never marked passed.
- **BLOCKED**: Unapproved UX review without risk acceptance, `BLOCKING` accessibility violation, `Proposed` ADR, or missing GDD prerequisite.
- **Next Skills**: `ags-art-ux ux-review` (if spec changed), `ags-verify` (UI story code/evidence review), `ags-team polish` (polish pass).
