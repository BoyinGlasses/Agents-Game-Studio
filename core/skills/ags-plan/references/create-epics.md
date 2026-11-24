# Epic Decomposition (`ags-plan epics`)

Translates approved GDDs and architecture documents into layer-ordered `production/epics/[epic-slug]/EPIC.md` modules and `production/epics/index.md`.

## Modes, Tier Rules & Knobs

- **Modes**: `all`, `layer: foundation|core|feature|presentation`, or `<system-name>`. Prompt if no argument is passed.
- **`workflow` tier** (resolve per-system via `workflow_overrides.system_overrides.<system>` when inspecting GDDs):
  - `full`: Every in-scope GDD must be `Approved` with all 8 sections; `tr-registry.yaml` and `control-manifest.md` are required; untraced requirements warn before proceeding.
  - `standard`: GDDs need the 5 required sections (+ conditional `Formulas`) approved; only critical (Foundation-layer) ADRs are required; `control-manifest.md` is read if present. Systems pinned to `full` via `system_overrides` still meet `full`.
  - `minimal`: **Optional** (if skipped, `ags-plan stories` synthesizes an implicit epic from `design/game-brief.md` via Option A). When run at `minimal`, decompose directly from `design/game-brief.md` + `Build order` without GDD/ADR/TR/manifest prerequisites.
- **`story_granularity`**: Expected child stories per epic: `3–5` (`coarse`), `5–10` (`balanced`), `10–20` (`fine`).
- **`docs.density`**: Scales epic `## Overview` and rationale depth (`terse` bullets, `balanced` paragraph, `thorough` full rationale/risk prose). `## Governing ADRs` and `## GDD Requirements` tables remain full at every density.

---

## Phase 1: Load Inputs (Fail-Open Summary Scan + Bounded ADRs)

1. **Summary scan (`standard`/`full`)**:
   - Count `N` system GDDs in `design/gdd/*.md`, excluding non-system docs (`game-concept.md`, `systems-index.md`, `game-pillars.md`, `gameplay-tags.md`, `entity-registry.md`, `fixture-swap-ledger.md`, `gdd-cross-review-*.md`). If `N == 0`, stop and route to `ags-gdd`.
   - Pattern-search `^## Summary` (+5 lines) across `design/gdd/*.md` (`M` matches):
     - `M == N`: scope `layer:`/`<system>` from Summary Quick-reference; full-read only in-scope GDDs.
     - `0 < M < N`: scope `M` via Summary; resolve remaining `N - M` from `systems-index.md` and full-read in-scope set.
     - `M == 0`: scope all `N` via `systems-index.md` and full-read in-scope set; note once that no `## Summary` sections were found.
   - Missing `## Summary` never removes a GDD from scope.
2. **In-scope full & bounded loads**:
   - Read `design/gdd/systems-index.md`, in-scope GDDs, `docs/architecture/architecture.md`, `docs/architecture/control-manifest.md` (header `Manifest Version`), `docs/architecture/tr-registry.yaml`, and `docs/engine-reference/<engine>/VERSION.md`.
   - **Bounded ADR reads**: Load ONLY Accepted ADRs covering in-scope systems, and read ONLY `^## (GDD Requirements Addressed|Decision|Engine Compatibility)` via heading line-number map + bounded slice (full-read an ADR only if a loaded section explicitly cross-references outside content).

Report: `"Loaded [N] GDDs, [M] ADRs, engine: [name + version]."`

---

## Phase 2: Dependency-Safe Layer Order

Process layers in strict order: **Foundation -> Core -> Feature -> Presentation**.
- Within each layer, follow `design/gdd/systems-index.md` order.
- At `minimal` (where `systems-index.md` does not exist), derive ordering from the **Build order** field in `design/game-brief.md` — never route a `minimal` project to `ags-gdd map-systems`.

---

## Phase 3: Define Each Epic & Check Traceability

For each in-scope system, map to its `architecture.md` module and check `tr-registry.yaml` per resolved tier:
- `full`: Trace every `TR-ID`; warn on untraced requirements (`Stories will be Blocked until ADRs exist`).
- `standard`: Trace critical (Foundation-layer) ADRs; list untraced non-critical requirements as informational only.
- `minimal`: Skip TR/ADR checks.

Present each epic summary (`Layer`, `GDD`, `Architecture Module`, `Governing ADRs`, `Engine Risk`, `Covered / Total`, `Untraced Requirements`) and confirm (`[A] Create epic` / `[B] Skip` / `[C] Pause to write ADRs`).

---

## Phase 4: Producer Epic Structure Gate (`PR-EPIC`)

- **`review_mode: solo` / `lean`**: Skip with explicit note (`"PR-EPIC skipped — Solo/Lean mode."`).
- **`review_mode: full`**: After all epics for the layer are defined and before writing, spawn `producer` pointing to `.ags/gates/pr-epic.md` (parent does not read the gate file); pass all proposed epic summaries, layer, milestone timeline, and team capacity.
  - `UNREALISTIC`: Split/merge/reorder epics and re-run `PR-EPIC`.
  - `CONCERNS`: Prompt (`[A] Proceed accepting concerns` / `[B] Revise boundaries` / `[C] Stop — BLOCKED`).

---

## Phase 5: Write `EPIC.md` & Update `index.md`

Confirm writes per `modes.automation`, then write:
- **`production/epics/[epic-slug]/EPIC.md`**: `# Epic: [System Name]`, header (`Layer`, `GDD`, `Architecture Module`, `Status: Ready`, `Stories: Not yet created — run ags-plan stories [epic-slug]`), `## Overview`, `## Governing ADRs`, `## GDD Requirements`, `## Definition of Done` (links `ags-verify` + `tests/` + `production/qa/evidence/`), `## Next Step` (`ags-plan stories [epic-slug]`).
- **`production/epics/index.md`**: Create or append row (`Epic | Layer | System | GDD | Stories | Status`).

Close with `ags-plan stories [epic-slug]` and remind that Foundation + Core epics are required before `ags-gate production` (at `standard`/`full`).
