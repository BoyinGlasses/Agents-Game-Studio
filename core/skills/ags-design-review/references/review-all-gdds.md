# Cross-GDD Holistic Review Workflow (`ags-design-review`)

Simultaneously evaluates all system GDDs for cross-system contradictions (Phase 2), design-theory holism (Phase 3), and multi-system interaction walkthroughs (Phase 4).

## Modes & Tier Resolution

- **`full`** (blank): Consistency + Design Theory + Scenarios.
- **`consistency`**: Cross-GDD consistency only.
- **`design-theory`**: Design-theory holism only.
- **`since-last-review`**: Scope narrowed deterministically via `python .ags/cli.py check review-scope`.
- **Per-GDD `workflow`**: Apply each GDD's effective tier (`system_overrides.<stem>` -> `modes.workflow` -> `modes.rigor`). At `minimal`, not applicable (no GDDs).

## Phase 1: L0 Discovery, Registry Pre-Load & Bounded Section Load

1. **Phase 1a — L0 Summary Scan**:
   - Count total system GDD files **N** under `design/gdd/` (excluding `game-concept.md`, `systems-index.md`, `game-pillars.md`, `gdd-cross-review-*.md`, `reviews/`).
   - Search `## Summary` (`-A 5`). **Fail open on missing summaries**: if fewer than N match, those GDDs predate `## Summary` and stay in scope (never shrink review set).
   - For `since-last-review`, run:
     ```bash
     python .ags/cli.py check review-scope
     ```
     If `PRIOR_REVIEW: NONE`, fall back to `full`. Otherwise scope strictly to `CHANGED` + `DEPS` files listed by the script.
2. **Phase 1b — Registry Pre-Load**: Read `design/registry/entities.yaml`. If populated, use as baseline for Phase 2; if empty/absent, note recommendation to run `ags-design-review consistency`.
3. **Phase 1c — L1/L2 Section Load**:
   - Read `design/gdd/game-concept.md`, `design/gdd/game-pillars.md` (if present), and `design/gdd/systems-index.md`.
   - From each in-scope system GDD, extract ONLY the sections consumed downstream (`## (Dependencies|Detailed Rules|Detailed Design|Formulas|Tuning Knobs|Acceptance Criteria|Player Fantasy)` — accept either `Detailed Rules` or `Detailed Design`). Escalate to full read for a GDD ONLY if a section cross-references outside material or matches zero template sections.
   - If `<2` readable GDDs exist, emit **`NOT ASSESSED`** (cross-review requires >=2 GDDs).

## Parallel Execution (Phase 2 & Phase 3)

When running both passes, spawn two `game-designer` subagents **in parallel** — pasting the extracted GDD content slices directly into each prompt (NEVER passing just file paths, and passing only Phase 2's slice `[Dependencies, Detailed Design/Rules, Formulas, Tuning Knobs, Acceptance Criteria]` to Phase 2 and Phase 3's slice `[Player Fantasy, progression/reward structure, game pillars]` to Phase 3), plus `design/registry/entities.yaml` contents, `engine.name`/`engine.version`, and `docs/engine-reference/<engine>/VERSION.md`.

### Phase 2: Cross-GDD Consistency (2a-2f)
- **2a Dependency Bidirectionality**: Flag asymmetric `Depends On` vs `Depended on by` declarations.
- **2b Rule Contradictions**: Compare floor/ceiling rules, resource ownership, death/state transitions, sync/async timing, stacking rules.
- **2c Stale References**: Start from each GDD's `## Cross-References` table (`Target GDD`, `Specific Element Referenced`, `Nature` — report absent/template-only tables explicitly rather than treating them as zero dependencies), THEN scan prose across all GDDs for references to removed/changed mechanics.
- **2d Data & Tuning Knob Ownership**: Flag duplicate ownership of the same multiplier or resource.
- **2e Formula Compatibility**: Verify upstream formula output ranges fall within downstream formula input expectations (`CONCERNS` on mismatch).
- **2f Acceptance Criteria Cross-Check**: Flag mutually unsatisfiable ACs across GDDs.

### Phase 3: Game Design Holism (3a-3g)
- **3a Progression Loop Competition**: Detect multiple systems competing equally as primary XP/unlock driver.
- **3b Player Attention Budget**: Count simultaneously active decision systems during core loop; flag if `>3-4`.
- **3c Dominant Strategy Detection**: Flag resource monopolies, risk-free power, zero-tradeoff options, or non-choices.
- **3d Economic Loop Analysis**: Map sources vs sinks per currency/resource; flag infinite source/no sink, sink>>source, runaway positive feedback, no catch-up.
- **3e Difficulty Curve Consistency**: Compare scaling curves (linear vs exponential vs stepped) across enemy health, player power, costs.
- **3f Pillar Alignment & Anti-Pillar Violations**: Flag GDDs serving no pillar (`Pillar Drift`) or violating an anti-pillar (`Anti-Pillar Violation`).
- **3g Player Fantasy Coherence**: Flag incompatible player identities across systems.

## Phase 4: Cross-System Scenario Walkthrough

1. **4a**: Identify 3-5 peak multi-system player moments (Combat+Economy, Progression+Difficulty, Narrative+Gameplay, 3+ system chains).
2. **4b**: Trace Trigger -> Activation order -> Data flow -> Player experience -> Check 7 failure modes (race conditions, uncapped feedback loops, broken state transitions, contradictory messaging, compounding difficulty spikes, reward double-dipping, undefined combined states).
3. **4c**: Classify findings `BLOCKER` / `WARNING` / `INFO` citing scenario, systems, step, and failure mode.

## Phase 5 & Phase 6: Report, ISO Date & `NOT ASSESSED` Rules

- **Verdict precedence**: `FAIL` > `CONCERNS` > `NOT ASSESSED` > `PASS`.
- **`NOT ASSESSED` triggers** (must also report `GDDs reviewed: [N] of [M] present`):
  - `<2` readable GDDs.
  - Any parallel review phase returned empty/no artifact (check artifact on disk before reading transcript; resume unmet contract before marking `BLOCKED`/`NOT ASSESSED` per error recovery protocol).
  - Design pillars undefined (pillar-drift uncheckable).
  - In-scope GDD is headings-only / all `[To be designed]` placeholders.
- **Confirm write to `design/gdd/gdd-cross-review-[YYYY-MM-DD].md`**: MUST use **ISO 8601 `YYYY-MM-DD`** filename so `python .ags/cli.py check review-scope` chronological sorting works reliably.
- **Confirm systems-index update**: Set flagged GDDs' `Status` to exact string **`Needs Revision`** (no parentheticals).
- **Append `production/session-state/active.md`** (`## Session Extract — ags-design-review review-all [date]`) + dynamic closing prompt (`ags-design-review` quick fixes / flagged GDDs, next `ags-gdd`, `ags-architect`, or `ags-gate`).
