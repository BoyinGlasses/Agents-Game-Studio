# Vertical Slice Workflow (`ags-ideate`)

Pre-production end-to-end validation answering: *"Can we build this full game loop at representative production quality, on schedule?"*

## Phase 1: Context & Mode Resolution

Apply `modes.review_mode` (`--review [full|lean|solo]` override) and `modes.automation`. Read:
- `AGENTS.md` / `project.yaml` (tech stack, engine, `naming.*`)
- `design/gdd/game-concept.md` (core fantasy, pillars)
- `design/gdd/systems-index.md` (MVP systems & priorities)
- `docs/architecture/architecture.md` & `docs/architecture/control-manifest.md`
- Key GDDs for sliced systems + any prior `prototypes/*/PIVOT-NOTE.md`

## Phase 2 & Phase 3: Scope, Validation Question & Plan

1. Define the **falsifiable validation question**:
   `"Does a player, starting from nothing, experience [core fantasy] within [N] minutes without developer guidance — and can we build one such [start -> challenge -> resolution] loop in [X] days at representative quality?"`
2. **Scope discipline**:
   - Include ALL core-loop systems needed for one `[start -> challenge -> resolution]` cycle.
   - **Target length: 3-5 minutes** of continuous polished gameplay.
   - **Cut scope before cutting quality** (low-quality slices prove nothing).
   - **Cap total effort at 1-3 weeks**; if longer, cut content rather than extending. Resist mid-slice feature creep.
3. Plan in bullets: systems/GDD sections exercised, exact `[start -> challenge -> resolution]` loop, art/audio quality level, measurable success criteria, hard time limit `[X]` days.
4. Confirm plan with user and write checkpoint to `production/session-state/active.md` (`Phase 4 — Implement`). Update `active.md` at the end of every build day.

## Phase 4: Implement

Confirm creating `prototypes/[concept-name]-vertical-slice/`. Prefix every code file with:
```
// VERTICAL SLICE - NOT FOR PRODUCTION
// Validation Question: [What this build is proving]
// Date: [Current date]
```

- **Quality standards** (higher than concept prototype): follow `docs/architecture/control-manifest.md` layer rules, `naming.*` from `project.yaml` (else legacy `technical-preferences.md`), no hardcoded gameplay constants (use external config/constants), basic error handling on critical paths, representative or clean placeholder art.
- **Day 3 Sunk-Cost Checkpoint**: If the full `[start -> challenge -> resolution]` loop is not demonstrable by Day 3, STOP and surface whether scope is too large or an architectural assumption failed before continuing.
- **Playtest**: Conduct >=1 playtest once loop runs (naive external testers silent observation, team rotation, solo silent walkthrough, think-aloud UX capture, async Loom/OBS recording, or Wizard-of-Oz for incomplete AI/economy).

## Phase 5: Playtest Debrief

Instruct user to play the full `[start -> challenge -> resolution]` cycle cold without dev shortcuts. Ask **one at a time**:
1. Completed full cycle unguided?
2. Time to first meaningful action?
3. Did it deliver `[core fantasy]` specifically?
4. Blockers, confusion points, or breaks?
5. Developer pipeline check: is this quality achievable for the full game? What took unexpectedly long?
6. Verdict (`PROCEED`, `PIVOT`, or `KILL` + specific reason).
Follow up on vague answers until concrete moments are captured.

## Phase 6 & Phase 7: Report, Velocity Log & Director Gate

1. Populate `prototypes/[concept-name]-vertical-slice/REPORT.md` from `.ags/templates/vertical-slice-report.md` (fallback headings: `Executive Summary`, `Core Loop Validation`, `Feel Assessment`, `Technical Findings`, **`Velocity Log` (actual day-by-day progress, never estimates)**, `Recommended Next Steps`, `Lessons Learned`). Confirm write.
2. Update `prototypes/index.md` (append name, date, verdict, `REPORT.md` link, and whether first run or post-`PIVOT` re-run).
3. **Director review (`CD-PLAYTEST`)**: Apply `modes.review_mode`; in `full`, spawn `creative-director` reading `.ags/gates/cd-playtest.md` with `REPORT.md`, validation question, pillars, and core fantasy. Update `REPORT.md` if verdict changes.

## Phase 8: Branching & Next Steps

- **`PROCEED`**: Production code is written from scratch using the slice as design reference only (never refactor slice code into production; never import from `prototypes/`). Route to `ags-plan` (`create-epics` for `layer:foundation` & `layer:core` -> `create-stories` -> `sprint-plan` using slice velocity data) and `ags-gate` (`pre-production`; minimum 1 documented `PROCEED` `REPORT.md` required, 3+ sessions recommended).
- **`PIVOT`**: Ask sequentially: (1) what worked at slice quality, (2) what failed (loop / architecture / pipeline / fun). Write `prototypes/[concept-name]-vertical-slice/PIVOT-NOTE.md` on confirmation, route to `ags-gdd` / `ags-architect` revisions, then re-run `ags-ideate vertical-slice`.
- **`KILL`**: Run 5-box confirmation checklist (>5 min loop, zero emotional high points, 50%+ testers stuck across 2+ attempts, >50% architecture rebuild needed, 3rd vertical slice attempt). >=2 checked confirms `KILL` -> append to `prototypes/GRAVEYARD.md`, route to `ags-ideate` (`brainstorm` or `prototype`).

## Constraints

- Never import from `prototypes/` into production source.
- Networked games: local 0ms slices validate loop completeness only, not 80ms+ real-network feel.
