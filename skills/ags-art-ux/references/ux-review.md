# UX, HUD & Pattern Library Review (`ags-art-ux`) — Read-Only

Validates UX design artifacts before implementation (`ags-team ui`) or `ags-gate pre-production`. Strictly read-only — reports findings without modifying files.

## Verdict Hierarchy & Arguments

- **Verdict precedence**: `MAJOR REVISION NEEDED` / `NEEDS REVISION` > `NOT ASSESSED` > `APPROVED`.
  - **`APPROVED`**: Complete, consistent, implementation-ready across all checked dimensions.
  - **`NOT ASSESSED`**: Target unreadable/missing, checklist dimension lacks a source of truth, or `design/accessibility-requirements.md` is absent (uncommitted tier — NEVER report `COMPLIANT` over an absent standard; if spec header states a tier, mark it an **assumption** and recommend `ags-art-ux ux-design accessibility`).
  - **`NEEDS REVISION`**: Specific blocking gaps found; targeted fixes needed.
  - **`MAJOR REVISION NEEDED`**: Fundamental scope, player-need, or completeness flaws requiring rework.
- **Arguments**: `<file-path>` | `all` (summary table `file | verdict | primary issue` then full details) | `hud` (`design/ux/hud.md`) | `patterns` (`design/ux/interaction-patterns.md`) | blank (ask user).

## Phase 2: Load Cross-Reference Context

1. **Input & Platform config (authoritative over spec header)**: Read `platform.*` from `project.yaml` (`targets`, `primary_input`, `gamepad_support`, `touch_support`; derive keyboard/mouse if `PC`/`Web` in targets, gamepad/touch if Full/Partial, plus `primary_input`), else legacy `technical-preferences.md`, else spec header.
2. `design/accessibility-requirements.md` (committed tier; if absent, Accessibility dimension MUST emit `NOT ASSESSED`).
3. `design/ux/interaction-patterns.md`.
4. Referenced GDDs' `UI Requirements` sections.
5. `design/player-journey.md` (context-arrival check).

## Phase 3A: UX Spec Checklist

- **Completeness (14 required sections)**: Document header (`Status`, `Author`, `Platform Target`), Purpose & Player Need (player-perspective), Player Context on Arrival, Navigation Position, Entry & Exit Points, Layout Specification (zones + component table), States & Variants (loading, empty/populated, error), Interaction Map (all target input methods), Data Requirements (source system + owner), Events Fired (event or explicit null), Transitions & Animations (enter/exit min), Accessibility Requirements, Localization Considerations (max char counts), Acceptance Criteria (>=5 testable criteria).
- **Quality Checks (9 categories)**:
  - *Player Need Clarity*: player perspective, `"The player arrives wanting to ___"`, specific prior activity.
  - *Completeness of States*: error, empty, async loading, timer/auto-dismiss durations.
  - *Input Method Coverage*: keyboard-only on PC, D-pad/face buttons on console/gamepad, no mouse-precision traps on gamepad, Tab/D-pad focus order.
  - *Data Architecture*: no data owned by `"UI"`, real-time update triggers defined, null handling defined.
  - *Accessibility*: matches/exceeds committed tier (`Basic`: no color-only cues; `Standard+`: focus order + contrast ratios; `Comprehensive+`: screen-reader announcements), colorblind alternatives.
  - *GDD Alignment*: every header-referenced GDD UI Requirement covered, no unsourced UI state modification.
  - *Pattern Library Consistency*: patterns referenced by name (no duplicate re-specs), new patterns flagged.
  - *Localization*: character-limit warnings, 40% text-expansion accommodation flagged on layout-critical text.
  - *Acceptance Criteria Quality*: self-contained for QA (performance open time ms, resolution check, zero external doc dependencies).

## Phase 3B: HUD Validation Checklist

- **Completeness (8 items)**: HUD Philosophy, Information Architecture covering ALL GDDs with UI Requirements, Layout Zones with platform safe margins, full HUD element specs (zone/trigger/source/priority), HUD states (`exploration`, `combat`, `dialogue/cutscene`, `paused`), Visual Budget (max simultaneous elements & screen %), Platform Adaptation, player-adjustable Tuning Knobs.
- **Quality & GDD Alignment (6 items)**: No permanent center-play occlusion without visibility rule, every GDD info item assigned or explicitly `hidden`/`on-demand`, colorblind variants on color-coded elements, queue/priority behavior for notifications/feedback, Visual Budget compliance, every UI-category system in `systems-index.md` represented or justified.

## Phase 3C: Pattern Library Validation Checklist

- Pattern catalog index matches document patterns; all standard control patterns specified (`button variants`, `toggle`, `slider`, `dropdown`, `list`, `grid`, `modal`, `dialog`, `toast`, `tooltip`, `progress bar`, `input field`, `tab bar`, `scroll`); game-specific patterns needed by specs present; every pattern includes `When to Use`, `When NOT to Use`, full states, accessibility spec, implementation notes; Animation Standards and Sound Standards tables present; zero conflicting navigation behaviors (e.g., consistent `Back`).

## Phase 4 & Phase 5: Report & Advisory Follow-Ups

- Output structured report (`Completeness: X/Y`, `Quality Issues [BLOCKING / ADVISORY]`, `GDD Alignment`, `Accessibility: COMPLIANT / GAPS / NON-COMPLIANT / NOT ASSESSED`, `Pattern Library`, `Verdict`, `Blocking issues`, `Advisory issues`, `Dimensions not assessed`).
- **Next steps**: `APPROVED` -> `ags-team ui`; `NOT ASSESSED` -> produce named missing input (`ags-art-ux ux-design accessibility` or missing GDD) — never re-run unchanged missing inputs expecting a different verdict; `NEEDS REVISION` -> offer targeted drafting only on user instruction; `MAJOR REVISION NEEDED` -> return to `ags-art-ux ux-design`. Verdicts are advisory — surface risks cleanly and let user decide.
