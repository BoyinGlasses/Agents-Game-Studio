# Concept Prototype & Spike Workflow (`ags-ideate`)

Fast, throwaway single-mechanic validation before full GDD/architecture investment, plus `--spike` mid-production experiments.

## Entry Routing (Phase 1)

- If `--spike` is passed -> go directly to **Spike Mode** below.
- Otherwise confirm intent:
  - `Prototype this concept` -> throwaway single-mechanic build (1-3 days) -> continue Phase 1.
  - `Skip — concept already proven` -> ask in plain text for concrete evidence, record `"Concept prototype skipped — evidence: [answer]"`, emit `SKIPPED`, hand off to `ags-gdd` (`map-systems` / `design-system`).
  - `Mid-production spike` -> jump to **Spike Mode**.

**Strategy notes**: Building 2-3 concept variants outperforms iterating a weak concept; game jams (48-72h) provide natural timeboxes and external player feedback.

**Falsifiable hypothesis (required before any build)**:
- Format: `"If the player [does X], they will feel [Y] — we will know this is true if [measurable signal Z]."`
- Ask: `"What is the riskiest assumption in this concept?"` (test the riskiest part first, not the easiest).
- Stop if the question is too vague/unfalsifiable (e.g., `"Does this feel fun?"`).

## Phase 2: Context

Read `design/gdd/game-concept.md` if present (core fantasy + core loop). Read `engine.name` and `engine.language` from `project.yaml` (fall back to legacy `technical-preferences.md`; ignore `[TO BE CONFIGURED]`).

## Phase 3: Choose Prototype Path (`--path [html|engine|paper]`)

| Genre | Recommended Path | Key Reason |
|---|---|---|
| Platformer / action / fighter | **Engine** | Feel is the hypothesis; browser latency misleads |
| Racing / sports | **Engine** | Timing and physics feedback are critical |
| Top-down / twin-stick shooter | **Engine** | Aim feel is timing-sensitive |
| Puzzle (logic) | **HTML** or **Paper** | Logic clarity matters, not timing |
| Card game | **Paper** first | Fastest rule iteration before code |
| Narrative / visual novel | **Paper** (Twine / Ink / Yarn Spinner) | Story is the mechanic; target <=3-4 exchanges to first emotional beat |
| Strategy / 4X / city builder | **Paper** (spreadsheet sim) | Validate economy and progression math first |
| Roguelike (systems-heavy) | **Paper** -> Engine | Validate ruleset interest before coding |
| Idle / clicker / incremental | **HTML** | Turn/math logic without latency sensitivity |
| Rhythm game | **Paper** first | Design levels against audio before engine work |
| RPG / open world | **Paper** -> Engine | Validate rules, then feel |
| Horror / atmospheric | **Engine** | Atmosphere requires real rendering |

Rule of thumb: *"Does this feel right?"* -> Engine; *"Are these rules interesting?"* -> Paper; *"Is this logic correct?"* -> HTML or Paper.

- **HTML**: Single double-clickable `prototypes/[name]-concept/prototype.html` (or PICO-8 / Phaser / Twine). ~85-90% one-shot; easy distribution via itch.io, Loom recordings, `r/playmygame` / `r/WebGames`, dev Discords. **Limitation**: 50-133ms browser rendering variance invalidates action/timing feel.
- **Engine**: Minimal project in `prototypes/[name]-concept/`. ~50-60% one-shot over 2-4 collaborative rounds (agent writes -> user runs -> reports observations -> iterate). **Sunk cost rule**: >2h without playable state -> stop, simplify hypothesis, or switch to Paper (or consider lighter 2D framework like Love2D if main 3D engine overhead blocks speed).
- **Paper**: `rules.md` + simulated `play-log.md` (100% reliable, cannot test feel). **5+ tester observation protocol**: brief once -> stay silent -> log hesitation/questions -> ask only `"What was confusing?"` -> fresh testers each round -> 3+ hitting same confusion = redesign rule.

State recommended path and prompt user to select `HTML` / `Engine` / `Paper`.

## Phase 4 & Phase 5: Plan & Implement

1. Plan in 3-5 bullets: hypothesis, riskiest assumption tested first, absolute minimum scope (ONE mechanic only), explicit cuts (menus, saves, error handling, polish, architecture). Confirm plan and checkpoint `production/session-state/active.md` (`Phase 5 — Implement`).
2. Confirm creating `prototypes/[concept-name]-concept/`. Prefix every code file with:
   ```
   // PROTOTYPE - NOT FOR PRODUCTION
   // Question: [Core question being tested]
   // Date: [Current date]
   ```
3. Relaxed prototype standards: hardcode freely, colored-shape placeholders, zero error handling, no production imports/abstractions, zero polish unless UI IS the tested mechanic. Encourage silent external observation, tester rotation, 5-minute solo speedrun, think-aloud testing, or Wizard-of-Oz NPC/AI puppeteering.

## Phase 6: Playtest Debrief

Hand off build (`prototype.html`, engine run, or `rules.md` + `play-log.md`) and instruct user to approach it cold. When user returns, ask **one at a time**:
1. Hypothesis check (`CONFIRMED` / `PARTIALLY CONFIRMED` / `REFUTED` + observed evidence)
2. Best moment (specific)
3. Worst / most confusing / broken moment (specific)
4. Unexpected behavior (good or bad)
5. Verdict (`PROCEED`, `PIVOT`, or `KILL` + one-sentence reason)
Follow up on vague answers until concrete observations are recorded.

## Phase 7 & Phase 8: Report & Creative Director Gate

1. Populate `prototypes/[concept-name]-concept/REPORT.md` from `.ags/templates/prototype-report.md` using concrete debrief observations (confirm write).
2. Update `prototypes/index.md` (create if absent): append concept name, date, path, verdict, `REPORT.md` link, and any prior `PIVOT-NOTE.md` chain.
3. **Director review (`CD-PLAYTEST`)**: Apply `modes.review_mode` (`solo`/`lean` skip with announcement; `full` spawns `creative-director` reading `.ags/gates/cd-playtest.md` ONLY if `design/gdd/game-concept.md` has pillars defined, otherwise announce `CD-PLAYTEST skipped — game pillars not yet defined`). Pass full `REPORT.md`, hypothesis, pillars, and core fantasy. Update `REPORT.md` if CD overrides verdict.

## Phase 9: Branching & Next Steps

- **`PROCEED`**: Rewrite production implementation from scratch (never refactor prototype code). Recommend: `ags-design-review` (`game-concept.md`) -> `ags-gate` -> `ags-art-ux` (`art-bible`) -> `ags-gdd` (`map-systems`, `design-system`) -> `ags-design-review` (`all`). Note: if HTML path left feel untested, run a quick engine feel prototype first.
- **`PIVOT`**: Ask sequentially: (1) what worked to preserve, (2) single biggest thing to change. Write `prototypes/[concept-name]-concept/PIVOT-NOTE.md` (original hypothesis, keep, change, revised hypothesis) on confirmation. On next `ags-ideate prototype` run, inspect `prototypes/` for `PIVOT-NOTE.md` first and seed the new hypothesis from it. Route to `ags-ideate` (`prototype [revised]` or `brainstorm`).
- **`KILL`**: Run 5-box validation checklist before finalizing:
  - Core mechanic unclear after 2+ playtests?
  - Zero fun/retry moments observed?
  - **3+ PIVOT iterations** on same concept with no clear improvement? *(3 PIVOTs force a KILL evaluation.)*
  - Works only with heavy dev explanation?
  - Building feels like obligation rather than excitement?
  - >=2 checked -> `KILL` confirmed; 0-1 -> consider one focused `PIVOT`.
  - Append entry (`Kill reason`, `What worked`, `What failed`, `Next time`) to `prototypes/GRAVEYARD.md` on confirmation, then route to `ags-ideate brainstorm`.

---

## Spike Mode (`--spike`)

Lightweight ~4h experiment with no GDD prerequisites, no `CD-PLAYTEST`, no phase-gate impact, and no `PROCEED/PIVOT/KILL` verdict.

1. Ask plain-text question: `"Can we [do X] using [approach Y]?"`
2. Select path (`HTML` / `Engine` / `Paper`).
3. Bound scope to 2-3 bullets (one mechanic or technical question).
4. Build under prototype standards with a hard **4-hour cap** (if unbuildable in 4h, split the question).
5. **Performance spike (special case)**: For demanding rendering/physics/particles, ask `"Can engine render [scene X] at 60fps on [min spec]?"` using max scene load without gameplay logic; output is a measured benchmark (`NO` = immediate architecture/scope constraint).
6. Write `prototypes/[name]-spike-[YYYY-MM-DD]/SPIKE-NOTE.md` (`Question tested`, `Result: YES / NO / PARTIAL`, `Next action`) and clear spike state in `production/session-state/active.md`.

## Non-Negotiable Constraints

- Production code MUST NEVER import from `prototypes/`; prototype code MUST NEVER import from production code.
- Hard 1-day cap for concept prototypes; 4h cap for spikes; 2h iteration cap on engine builds.
- **Networked/multiplayer**: Local 0ms builds test rule interest only, never network combat/movement/prediction feel (requires real peers or latency simulation, e.g., 80ms+).
