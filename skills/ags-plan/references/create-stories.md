# Story Breakdown (`ags-plan stories`)

Decomposes one epic (or `design/game-brief.md` at `minimal`) into atomic, traceable `production/epics/[epic-slug]/story-NNN-[slug].md` files ready for `ags-dev`. See [../CONTRACT.md](../CONTRACT.md).

## Argument Resolution & Zero-Epic Guard

- Accept `<epic-slug>` or `production/epics/<slug>/EPIC.md`.
- **No argument**:
  - At **`minimal`**: Proceed to Option A (`minimal` brief synthesis) below.
  - At **`standard` / `full`**: Search `production/epics/*/EPIC.md`. **If zero epics exist, STOP immediately** and report: `"No epics found under production/epics/. Run ags-plan epics layer: foundation first — an epic is what this skill decomposes."` (Never prompt with an empty epic list.)
- Resolve system `workflow` tier via `workflow_overrides.system_overrides.<stem>` -> `modes.workflow` -> `modes.rigor`.

---

## Phase 1: Context Load

### Option A: `minimal` Tier (Brief Synthesis)
1. Read `design/game-brief.md` in full.
2. Synthesize an implicit lightweight `production/epics/<slug>/EPIC.md` (`<slug>` = slugified working title or `mvp`; goal = one-sentence pitch; scope = MVP feature list; ordering = **Build order**).
3. Generate **one coarse story per MVP feature** in Build-order sequence. Skip GDD/ADR/TR/manifest reads and apply this deterministic field mapping:
   - `GDD` -> `design/game-brief.md`
   - `Requirement` -> `Brief MVP feature N`
   - `ADR Governing Implementation` / `ADR Decision Summary` / `ADR Version` -> `N/A (minimal — no ADRs)`
   - `Manifest Version` / `Control Manifest Rules` -> `N/A (minimal — no control manifest)`
   - **`Engine` & `Risk`**: Read `docs/engine-reference/<engine>/VERSION.md` (`engine.name` + `engine.version`; `Risk` = pinned version risk row). **If `VERSION.md` is missing or assigns no rating, write `NOT ASSESSED (no VERSION.md risk rating)` — never guess a rating** (`ags-dev` treats `NOT ASSESSED` as `HIGH` for specialist spawn).
   - `Engine Notes` -> `none (no ADR engine-compatibility analysis at minimal)`
   - Acceptance-criteria source line -> `"From design/game-brief.md (Player goal & fail state + MVP feature), scoped to this story"`
   - `## QA Test Cases` -> `*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above*`
   - `## Test Evidence`: `Handoff Class:` and `Verification Method:` remain **required** even when `qa.level: minimal` waives automated test evidence as advisory.

### Option B: `standard` / `full` Tier (Existing Epic)
1. Read `production/epics/[epic-slug]/EPIC.md` and the epic's GDD (`design/gdd/[filename].md`, prioritizing Acceptance Criteria, Formulas, Edge Cases).
2. Read `docs/engine-reference/<engine>/VERSION.md`.
3. Extract ONLY this epic's layer section (`^## <Layer> Layer Rules` + header `Manifest Version:`) from `docs/architecture/control-manifest.md`.
4. Extract ONLY this system's entries (`system: <slug>` or `TR-<slug>-`) from `docs/architecture/tr-registry.yaml`.
5. **Bounded ADR reads** (never unbounded full reads of large ADRs):
   - Pattern-search heading map `^## |^### Implementation Guidelines` for line numbers.
   - Bounded-read ONLY `## Summary`, `## Decision` (including `### Implementation Guidelines`), and `## Engine Compatibility`.
   - Pattern-search `^## (Last Verified|Date)` (+1 line) -> `ADR Version` (`Last Verified`, else `Date`, else `unversioned`).
   - Skip `Context`, `Alternatives`, `Consequences`, `Risks`, and `Amendments Log` unless explicitly cross-referenced. If the heading map is empty (legacy ADR), perform a single bounded/capped read and flag for `ags-architect adr retrofit`.
6. **ADR existence validation (tier-gated)**:
   - `full`: STOP if any referenced ADR file is missing.
   - `standard`: STOP only if a critical (Foundation-layer) ADR is missing; warn and set `Status: Blocked` on non-critical missing ADRs.
   - `minimal`: Never stop on missing ADRs.

Report actual loaded counts and manifest/ADR status accurately (never claim "all present" if any ADR was missing).

---

## Phase 2: Classify, Size & Derive Story Fields

1. **Story Type** (highest implementation risk wins for mixed):
   - `Logic`: Formulas, numeric thresholds, state transitions, AI, calculations -> unit test (`tests/unit/<system>/<slug>_test.<ext>`).
   - `Integration`: Cross-system interaction, boundary signals, save/load -> integration test or playtest doc.
   - `Visual/Feel`: Animation, VFX, timing, screen shake, audio sync -> evidence doc (`production/qa/evidence/<slug>-evidence.md`).
   - `UI`: Menus, HUD, buttons, screens, dialogue, tooltips -> evidence doc or interaction test.
   - `Config/Data`: Tuning values / data files only -> smoke check pass.
2. **Sizing & Density**:
   - **`story_granularity`**: `coarse` (`5–10` ACs covering a feature), `balanced` (`2–4` ACs covering one task), `fine` (`1` AC restatement). Group/split criteria to match.
   - **`docs.density`**: Scales context/implementation prose (`terse` bullets, `balanced` short paragraph + notes, `thorough` full context + ADR rationale). Never trim `TR-ID`, `ADR Version`, or Acceptance Criteria.
3. **Traceability & Governance**:
   - Lookup stable `TR-[system]-NNN` in `tr-registry.yaml` (`TR-[system]-???` + warning if unmatched).
   - Governing ADR `Accepted` -> embed; `Proposed` -> set story `Status: Blocked` (`BLOCKED: ADR-NNNN is Proposed — run ags-architect adr accept ADR-NNNN to advance it`); multiple ADRs -> primary first; none applicable -> `ADR: N/A — [reason]` (never blank).
4. **Handoff Class & Verification Method** (mandatory at every `qa.level`, including `minimal`):
   - **`Handoff Class`**: `Player-facing` (game maker must play to judge observable behavior), `Technical` (build/test evidence suffices), or `Mixed` (both play result and technical criteria). Derive from ACs, NOT from `Type:` (a Logic story with player-visible behavior is `Player-facing`).
   - **`Verification Method`**: Concrete build/test command (from `project.yaml` when configured) or manual check + expected evidence path + playable setup/steps for `Player-facing`/`Mixed`. Name missing runners rather than implying a pass.

---

## Phase 3: `QL-STORY-READY` Gate & QA Plan Reuse

- Check `review_mode`: `solo` / `lean` -> skip with note (`"QL-STORY-READY skipped — Solo/Lean mode."`).
- In `full`: spawn `qa-lead` **once** pointing to `.ags/gates/ql-story-ready.md` (parent does not read the gate file), passing story list, types, TR-IDs, and GDD ACs. Require BOTH per-story verdict (`ADEQUATE | GAPS | INADEQUATE`) and spec blocks (`Given/When/Then` for Logic/Integration; `Setup/Verify/Pass condition` for Visual/Feel/UI) in that single return. Revise any `GAPS`/`INADEQUATE` stories before proceeding.
- **Reuse existing QA plan (no extra spawn)**: Check latest `production/qa/qa-plan-*.md`. If it holds differing test specs for these stories, prompt the user to choose QA-plan specs, `qa-lead` specs, or skip.

---

## Phase 4: Present, Confirm & Write

Present the full story summary (Title, Type, ADR, TR-IDs, `Handoff Class`, `Verification Method`, required evidence) and confirm writing `production/epics/[epic-slug]/story-[NNN]-[slug].md` (check existing `NNN` numbers first so none collide). Then:
1. Write each story file using the canonical story schema (`# Story [NNN]: [title]`, header metadata including `Handoff Class`, `Manifest Version`, `Last Updated`, `## Context` with `ADR Version` and `Engine | Risk`, `## Acceptance Criteria`, `## Implementation Notes`, `## Out of Scope`, `## QA Test Cases`, `## Test Evidence` with `Verification Method`, `## Dependencies`).
2. Update `production/epics/[epic-slug]/EPIC.md`: replace `"Stories: Not yet created"` with the `## Stories` table (`# | Story | Type | Status | ADR`).
3. Update `production/epics/index.md` matching row (`Stories` -> `[N] stories`). If `production/epics/index.md` does not exist, report `"Epics index not updated: production/epics/index.md absent"` and continue.

Close with context-aware options (`ags-dev readiness [first-story]`, `ags-plan stories [next-epic]`, or `ags-plan sprint new`).
