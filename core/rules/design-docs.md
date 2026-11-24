---
paths:
  - "design/gdd/**"
---

# Design Document Rules

- The 8 GDD sections are: Overview, Player Fantasy, Detailed Rules, Formulas, Edge Cases, Dependencies, Tuning Knobs, Acceptance Criteria.
- Required count follows `modes.workflow` in `project.yaml`:
  - `full`: all 8 sections.
  - `standard`: 5 core sections + **Formulas** whenever the system defines numeric rules (rates, curves, thresholds, costs, damage, drop weights — anything a balance pass tunes).
  - `minimal`: no full GDD required (`design/game-brief.md` carries the design record).
- **Formulas test**: determined by whether the system defines numeric rules, never solely by its `Category` label (`Gameplay`, `Economy`, `Progression` are hints, not the rule).
- **Heading alias**: `## Detailed Design` and `## Detailed Rules` denote the same required section; accept either without rewriting one into the other.
- Formulas require variable definitions, units/ranges, and worked example calculations.
- Edge cases must define concrete behavior (never "handle gracefully").
- Dependencies must be bidirectional across linked GDDs (`A <-> B`).
- Tuning knobs require safe ranges, category (`Feel | Curve | Gate`), and gameplay effect.
- Acceptance criteria must be measurable pass/fail conditions (no hand-waving like "feels good").
- Balance numbers must trace to a source formula or documented rationale.
- Author multi-section GDDs skeleton-first, updating sections incrementally and syncing `production/session-state/active.md`.
