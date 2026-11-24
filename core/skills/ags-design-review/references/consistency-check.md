# GDD Entity-Registry Consistency Check (`ags-design-review`)

Pattern-search-first cross-document conflict check comparing GDDs against `design/registry/entities.yaml` and maintaining the `docs/consistency-failures.md` reflexion log.

## Tier Applicability & Modes

- **`workflow`**: `full` checks all GDD sections; `standard` checks required sections; `minimal` is N/A (no GDDs).
- **Modes**: `full` (blank) | `since-last-review` | `entity:<name>` | `item:<name>`.

## Phase 1 & Phase 2: Load Registry & Locate Scope

1. Read `design/registry/entities.yaml`. If absent or zero live entries (ignore commented examples), emit **`NOT ASSESSED`** (*"Entity registry is empty — run `ags-gdd design-system` to populate it"*), and stop.
2. Build 4 maps: `entity_map` (`source`, `attributes`, `referenced_by`), `item_map`, `formula_map`, `constant_map`.
3. Locate system GDDs under `design/gdd/*.md` (excluding `game-concept.md`, `systems-index.md`, `game-pillars.md`, `gdd-cross-review-*.md`). For `since-last-review`, use `git log` / `python .ags/cli.py check review-scope` since the latest `gdd-cross-review-*.md`.

## Phase 3 & Phase 4: Targeted Conflict Scan & Investigation

1. **Targeted search (`-C 3`)**: For each registered entry in scope, search `design/gdd/*.md` by name (no full-document reads unless a conflict triggers Phase 4):
   - **3a Entities**: numeric/categorical/derived attributes -> mismatch = `CONFLICT`, mention without attribute = `NOTE (unverifiable)`.
   - **3b Items**: sell/gold value, weight, stack rules, category.
   - **3c Formulas**: variable names, output ranges/caps.
   - **3d Constants**: numeric values near constant name.
2. **Deep investigation (conflicts only)**: Read conflicting sections in full; verify authoritative `source:` GDD; check `git log` to distinguish:
   - **`CONFLICT`**: Different values across GDDs (blocking before architecture).
   - **`STALE REGISTRY`**: `source:` GDD updated more recently than `entities.yaml`.
   - **`UNVERIFIABLE`**: Entity mentioned without comparable values.

## Phase 5-7: Report, Registry Updates, Reflexion Log & Breadcrumb

1. Present report (`Conflicts Found`, `Stale Registry Entries`, `Unverifiable References`, `Clean Entries`, Verdict: `PASS | CONFLICTS FOUND | BLOCKED | NOT ASSESSED`).
2. **Registry updates (on confirmation)**:
   - Update stale entries with `revised: YYYY-MM-DD` and `# was: [old_value] before [date]`.
   - Offer adding newly discovered cross-system entities (appearing in >1 GDD).
   - **NEVER delete registry entries** — set `status: deprecated` if removed from all GDDs.
   - Unresolved conflicts -> **`BLOCKED`**.
3. **Reflexion log (`docs/consistency-failures.md`)**: Whenever any `CONFLICT` is found (resolved or not), unconditionally append an entry (creating `docs/consistency-failures.md` with `# Consistency Failure Log` header table if absent) recording Date, GDDs involved, differing values, Resolution, and generalized Pattern.
4. **Session breadcrumb & closing**: Append `<!-- CONSISTENCY-CHECK: [date] | GDDs checked: [N] | Conflicts found: [N] | Log: docs/consistency-failures.md -->` to `production/session-state/active.md` (always naming `docs/consistency-failures.md`) and close with action prompt (`[A] Fix highest-priority conflict` / `[B] Save & stop` / `[C] Run ags-design-review on most conflicted GDD` / `[D] Stop`).
