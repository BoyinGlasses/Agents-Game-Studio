# Art Bible Authoring & Retrofit (`ags-art-ux`)

Establishes visual identity (`design/art/art-bible.md`), gating downstream asset specs and technical rendering architecture.

## Phase 0: Context & Pattern-Search Retrofit Check

- **`docs.density`**: `terse` (bulleted constraints + references), `balanced` (paragraphs per visual choice), `thorough` (full prose, style explorations, references, rationale).
- **`workflow` & override**: `full` or `workflow_overrides.art_bible_strict: true` requires all 9 sections; `standard` requires sections 1-4 only if visual asset stories exist; `minimal` is optional.
- **Required concept read**: Read `design/gdd/game-concept.md` (fail and point to `ags-ideate brainstorm` if missing). Extract working title, core fantasy, elevator pitch, all pillars, Visual Identity Anchor, and target platform. Read `performance.*` and `engine.name` from `project.yaml` (else legacy `technical-preferences.md`).
- **Non-destructive Retrofit detection**: If `design/art/art-bible.md` exists, inspect WITHOUT reading the whole file:
  1. Pattern-search `^## ` with line numbers to measure section spans.
  2. Pattern-search `\[To be designed\]|\[TBD\]|\[To be written\]|^_?TODO` for placeholders.
  3. Classify each of the 9 sections (`Complete` / `Empty` / `Placeholder`); use a bounded line-range read on an individual section ONLY if ambiguous.
  4. Present the 9-row status table and confirm authoring **only** `Empty`/`Placeholder` sections without modifying existing content.

## Phase 1: Framing

Prompt with two tabs:
- **`Scope`**: `Full bible — all 9 sections` / `Visual identity core (sections 1–4 only)` / `Asset standards only (section 8)` / `Resume — fill in missing sections`. Mark `(Recommended)` directly from the resolved `workflow` / `art_bible_strict` rule (`full` or `art_bible_strict: true` -> Full bible; `standard` -> Sections 1-4 core; `minimal` -> note optional and offer 1-4 rather than defaulting to 9).
- **`References`**: Free-text prompt for reference games, films, or artists (no preset options).

## Phase 2: Visual Identity Foundation (Sections 1-4)

Every section draft comes from `art-ux-director` (lens: `art-director`), is approved one section at a time, and is written immediately to `design/art/art-bible.md` before starting the next section.

- **Section 1 — Visual Identity Statement**: Spawn `art-ux-director` (`art-director`) solo with concept, pillars, platform, references, and any Visual Identity Anchor (ask whether to build on/revise/restart existing anchor). Produce a one-line visual rule + 2-3 supporting principles with design tests anchored to pillars. Prompt `[A] Lock in` / `[B] Revise one-liner` / `[C] Revise principle` / `[D] Custom direction`, then write.
- **Sections 2-4 — Single Batched Delegation -> Sequential Approval**: Spawn `art-ux-director` (`art-director`) **once** with the locked Section 1 + pillars requesting three mutually consistent, separately labeled blocks:
  1. **Section 2 (Mood & Atmosphere)**: Emotional target, lighting character (temperature/contrast/time of day), 3-5 atmospheric descriptors, energy level, and concrete carrying element per major game state.
  2. **Section 3 (Shape Language)**: Character silhouette readability at thumbnail distance, environment geometry, UI shape grammar, hero vs supporting shape hierarchy tied to Section 1 & pillars.
  3. **Section 4 (Color System)**: Primary 5-7 color roles with world meaning, semantic color vocabulary, per-biome temperature shifts, UI vs world divergence, and colorblind-safe backup cues (shape/icon/sound).
  Present, approve, and write **Section 2** first, then **Section 3**, then **Section 4** (batching applies only to the delegation call, never the user review/write).

## Phase 3: Production Guides (Sections 5-8)

- **Sections 5-6 — Single Batched Delegation -> Sequential Approval**: Spawn `art-ux-director` (`art-director`) **once** with Sections 1-4 requiring character/environment legibility contrast and returning two separately labeled blocks:
  1. **Section 5 (Character Design Direction)**: Player visual archetype, silhouette/feature differentiation across enemies/NPCs/allies, pose/expression style, camera-distance LOD philosophy.
  2. **Section 6 (Environment Design Language)**: World architectural culture/history, texture philosophy (painted/PBR/stylized), prop density rules per area, environmental storytelling without text.
  Approve and write **Section 5**, then **Section 6**.
- **Section 7 — UI/HUD Visual Direction**: Spawn `art-ux-director` (`art-director`: diegetic vs screen-space HUD, typography, iconography, UI motion) and `art-ux-director` (`ux-designer`: interaction pattern alignment & readability/accessibility check) in **parallel**. Surface any conflict explicitly via user prompt — never resolve silently. Write approved section.
- **Section 8 — Asset Standards**: Spawn `art-ux-director` (`art-director`: formats, naming, texture res tiers, LODs, export prefs) and `tech-artist` (poly budgets, texture memory limits, material slots, importer constraints, `performance.*` budgets) in **parallel**. Surface and resolve ideal-vs-budget tradeoffs explicitly. Write approved section.

## Phase 4: Reference Direction (Section 9)

Spawn `art-ux-director` (`art-director`) with Sections 1-8 for 3-5 additive references: per source, name exact visual technique/palette/composition rule to borrow AND what to explicitly avoid. Approve and write.

## Phase 5 & Phase 6: Sign-Off (`AD-ART-BIBLE`) & Close

1. Apply `modes.review_mode`: skip with announcement in `solo`/`lean`; in `full`, spawn `art-ux-director` (`art-director`) reading `.ags/gates/ad-art-bible.md` (pass art bible path, pillars, visual identity anchor). Record header line:
   `> **Art Director Sign-Off (AD-ART-BIBLE)**: APPROVED [date] / CONCERNS (accepted) [date] / REVISED [date]`.
2. Check project state (`systems-index.md`, configured `engine.name`, `design/gdd/*.md`, `gdd-cross-review-*.md`) and build dynamic next-step prompt showing only uncompleted steps plus always `ags-architect` (`create-architecture`) and `Stop here`.
