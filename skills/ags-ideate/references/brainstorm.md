# Brainstorm & Lean Brief Workflow (`ags-ideate`)

Covers both the `minimal` Lean Brief flow and the full `standard`/`full` ideation pipeline.

## Mode & Density Controls

- **Automation**: Apply `.ags/rules/` / `modes.automation` (`collaborative` prompts everywhere, `guided` major-only, `autonomous` logs to `production/session-state/` / `production/session-logs/decision-log.md` and proceeds) EXCEPT where explicitly marked **unconditional** below.
- **`docs.density`**:
  - `terse`: pillar bullets + concept bullets.
  - `balanced`: pillars + concept with brief rationale (default).
  - `thorough`: pillars + concept + extensive rationale + alternatives.
- **`modes.review_mode`**: `solo` skips all gates (announce `[GATE-ID] skipped — Solo mode`); `lean` skips non-PHASE-GATEs (announce `[GATE-ID] skipped — Lean mode`); `full` spawns all gates below. `--review` overrides for the current run.

---

## Tier Branch: Lean Brief (`workflow: minimal` ONLY)

When `modes.workflow` resolves to `minimal`, run this 4-step flow and **STOP**. Do NOT run Phases 1-6, spawn director gates, or write `design/gdd/game-concept.md`.

Author from `.ags/templates/game-brief.md` (6 required fields + 2 optional one-liners). If `design/game-brief.md` already exists, read and refine it rather than restarting. Keep prompting light.

1. **Concept**: From the user's hint (or one open question), propose **2-3 one-line concepts** (verb-first or mashup). Prompt the user once to pick or combine.
2. **Fill brief fields conversationally**:
   - **One-sentence pitch**: Single excited sentence.
   - **Core loop**: 2-4 step cycle the player repeats.
   - **Player goal & fail state**: What winning / completing a session looks like and how a run ends.
   - **MVP**: Ruthlessly short feature list (if past ~7 items, push back on scope; each becomes a story downstream).
   - **Out of scope**: Specific exclusions saving the project.
   - **Build order**: Sequence building the risky / core-fun feature first.
   - **Who it's for / what they feel** and **Art & audio direction**: Offer one line each (optional).
   Present the filled brief in full for a single confirmation.
3. **Confirm write**: Present options `[A] Write to design/game-brief.md` / `[B] Revise a field first`. On `[B]`, revise, show before/after, and re-confirm (`modes.automation` applies). Write `design/game-brief.md`, creating parent directories as needed.
4. **Next steps**: Check `engine.name` in `project.yaml` first — list step 1 **only** if `engine.name` is absent or empty:
   1. *(only when `engine.name` is absent/empty)* `ags-settings` — configure the engine (required before code).
   2. `ags-plan` (`create-stories`) — turn MVP features into implementable stories (the epic is implicit at `minimal`; build order is the plan).
   3. `ags-dev` — write the first line of game code.
   Emit a one-line summary (pitch + MVP feature count + `design/game-brief.md`). Verdict: **`COMPLETE`**.

---

## Full Brainstorm Flow (`workflow: standard` or `full`)

Check for existing `design/gdd/game-concept.md` and `design/gdd/game-pillars.md` (resume if found). Follow studio brainstorming principles: withhold judgment, encourage unusual ideas, build with "yes, and...", treat constraints as creative fuel, time-box each phase.

### Phase 1: Creative Discovery
Ask conversationally:
- **Emotional anchors**: A game moment that moved/thrilled you and why; an unfulfilled fantasy or power trip.
- **Taste profile**: Top 3 games spent the most time with (ask in **plain text** for free-form game titles); genres loved/avoided; constrained preference prompt (`Challenge / Relax / Story / Express`).
- **Practical constraints** (single multi-tab prompt with exact tab labels):
  - `Experience`: "What kind of experience do you most want players to have?" (`Challenge & Mastery` / `Story & Discovery` / `Expression & Creativity` / `Relaxation & Flow`)
  - `Timeline`: "What's your realistic development timeline?" (`Weeks` / `Months` / `1-2 years` / `Multi-year`)
  - `Dev level`: "Where are you in your dev journey?" (`First game` / `Shipped before` / `Professional background`)
- **Synthesize**: Write a 3-5 sentence **Creative Brief** and confirm intent.

### Phase 2: Concept Generation
Generate **3 distinct concepts** using:
1. **Verb-First Design**: Start from core player verb (`build`, `fight`, `explore`, `solve`, `survive`, `create`, `manage`, `discover`).
2. **Mashup Method**: `[Genre A] + [Theme B]` creative tension.
3. **Experience-First (MDA Backward)**: Desired aesthetic (`sensation`, `fantasy`, `narrative`, `challenge`, `fellowship`, `discovery`, `expression`, `submission`) -> dynamics -> mechanics.

Present each concept with: Working Title, Elevator Pitch (1-2 sentences, 10-second test), Core Verb, Core Fantasy, Unique Hook (`Like X, AND ALSO Y`), Primary MDA Aesthetic, Estimated Scope (`small` / `medium` / `large`), Why It Could Work, Biggest Risk.

**UNCONDITIONAL PROMPT (exempt from `autonomous` auto-pick):** Present a plain option list (no tabs) for concept selection:
- Options: `Concept 1 — [Title]`, `Concept 2 — [Title]`, `Concept 3 — [Title]`, `Combine elements across concepts`, `Generate fresh directions`.

### Phase 3: Core Loop Design
- **30-Second Loop**: Derive concept-specific prompts (with free-text escape) for (1) core action feel and (2) key design variable; evaluate intrinsic satisfaction (audio, visual juice, timing, tactical depth).
- **5-Minute Loop**: Short-term cycles, "one more turn/run" hook, tactical choices.
- **Session Loop (30-120 min)**: Complete session arc, stopping points, between-session hook.
- **Progression Loop (days/weeks)**: Growth axis (power/knowledge/options/story) and completion state.
- **Self-Determination Theory (SDT) Check**: Autonomy (meaningful choice), Competence (felt mastery), Relatedness (characters/players/world).

### Phase 4: Pillars, Anti-Pillars & Parallel Visual/Pillar Gates
1. Define **3-5 pillars**, each with name, one-sentence definition, and design test (`"If debating X vs Y, choose __"`). Pillars must create productive tension.
2. Define **3+ anti-pillars** (`"We will NOT do [thing] because it would compromise [pillar]"`).
3. **Pillar confirmation**:
   - Prompt `[A] Lock these in` / `[B] Rename or reframe one` / `[C] Swap a pillar out` / `[D] Something else`.
   - `collaborative`: repeat until `[A]`. `guided`: ask once, apply revision, lock. `autonomous`: draft, log decision, lock.
4. **Director gates** (apply `modes.review_mode` first; in `full`, spawn BOTH simultaneously):
   - `creative-director` -> `CD-PILLARS` (read `.ags/gates/cd-pillars.md` first). Pass: pillars + design tests, anti-pillars, core fantasy, unique hook.
   - `art-ux-director` (lens: `art-director`) -> `AD-CONCEPT-VISUAL` (read `.ags/gates/ad-concept-visual.md` first). Pass: elevator pitch, full pillars + design tests, target platform, user touchstones.
   - Resolve any `CD-PILLARS` `CONCERNS`/`REJECT` before asking the user to pick the **Visual Identity Anchor** from the 2-3 named directions (multi-tab presentation when both proceed: `Pillars` + `Visual anchor` with combine/custom options).

### Phase 5: Player Type Validation
Validate using Bartle taxonomy and Quantic Foundry motivations: Primary player type (`Achievers`, `Explorers`, `Socializers`, `Competitors`, `Creators`, `Storytellers`), Secondary appeal, Who this is NOT for, Market validation against comparable titles.

### Phase 6: Scope, Feasibility & Document Generation
1. **Target platform**: Prompt (`PC (Steam / Epic)` / `Mobile (iOS / Android)` / `Console` / `Web / Browser` / `Multiple platforms`) + note implications.
2. **Engine experience — UNCONDITIONAL PROMPT (always prompts even in `autonomous` mode)**:
   - Options: `Godot` / `Unity` / `Unreal Engine 5` / `No preference — help me decide`.
   - If picked: record preference without second-guessing. If `No preference`: direct to `ags-settings` after this session without guessing a recommendation.
3. Define art pipeline, content scope (levels/items/hours), MVP definition, biggest risks (technical/design/market), and scope tiers (full vision vs fallback).
4. **Technical Feasibility Gate** (`TD-FEASIBILITY` -> `.ags/gates/td-feasibility.md` via `technical-director`; check `modes.review_mode`): Pass core loop, platform, engine, risk list. On `HIGH RISK`, offer scope revision.
5. **Producer Scope Gate** (`PR-SCOPE` -> `.ags/gates/pr-scope.md` via `producer`; check `modes.review_mode`): Pass full scope, MVP, timeline, team size. On `UNREALISTIC`, adjust MVP/tiers before writing.
6. **Generate `design/gdd/game-concept.md`** from `.ags/templates/game-concept.md`:
   - Include MDA analysis, SDT motivation, flow state design, and **Visual Identity Anchor** (direction name, one-line visual rule, 2-3 supporting visual principles with design tests, color philosophy summary).
   - **Scope consistency rule**: Core Identity table `Estimated Scope` must match the full-vision timeline (`"Large (X-Y months, solo/team of N)"`).
   - Confirm write (`[A] Write to design/gdd/game-concept.md` / `[B] Revise a section`): `collaborative` loops until `[A]`; `guided` applies one revision and writes; `autonomous` writes and logs.
7. **Next steps (list all steps in order)**:
   - **Path A (Design-First)**: (1) `ags-settings` -> (2) `ags-art-ux` (`art-bible` before GDDs/architecture) -> (3) `ags-design-review` on `design/gdd/game-concept.md` -> (4) `creative-director` pillar refinement -> (5) `ags-gdd` (`map-systems`) -> (6) `ags-gdd` (`design-system` per system) -> (7) `ags-architect` (`create-architecture`) -> (8) `ags-architect` (`adr` x N) -> (9) `ags-arch-review` -> (10) `ags-gate`.
   - **Path B (Prototype-First)**: (1) `ags-settings` -> (2) `ags-ideate` (`prototype [core-mechanic]`) -> (3) on `PROCEED`: `ags-art-ux` (`art-bible`) then Path A steps 5-10 -> (4) on `PIVOT`: return to `ags-ideate` (`brainstorm`) -> (5) after design/arch: `ags-ideate` (`vertical-slice`).
8. **Context Window Awareness**: At >=70% context usage, append a note confirming `design/gdd/game-concept.md` is saved and recommending a fresh session to continue.
