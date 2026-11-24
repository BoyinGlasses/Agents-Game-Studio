# Per-System GDD Authoring & Retrofit (`ags-gdd`)

Authors or retrofits one system GDD (`design/gdd/<system>.md`) section by section with skeleton-first writes, specialist input, and cross-system registry checks.

## 1. Arguments, Retrofit Detection & Effective Tier

- **`docs.density`**: `terse` (2-5 line bullets, skip preamble — mandated Formulas variable table and Given-When-Then AC format still required), `balanced` (paragraphs + light rationale), `thorough` (full prose + examples + alternatives).
- **Missing argument**: Read `design/gdd/systems-index.md`, propose highest-priority `"Not Started"` system (`[A] Yes` / `[B] Pick different` / `[C] Stop`); if no index exists (outside minimal brief), fail and point to `ags-gdd map-systems`.
- **Retrofit mode** (arg starts with `retrofit` or points to an existing `design/gdd/<file>.md`):
  1. Scan existing `##` headings across the 8 sections: Overview, Player Fantasy, Detailed Rules / Detailed Design, Formulas, Edge Cases, Dependencies, Tuning Knobs, Acceptance Criteria.
  2. Classify missing vs placeholder (`[To be designed]` / blank / single stub line) vs complete against the **resolved effective tier** — report absent sections as gaps **only** when required at that tier (e.g., at `standard`, list absent Player Fantasy / Tuning Knobs as available-to-add, never as missing gaps).
  3. Present status summary and confirm filling ONLY `[N]` missing/incomplete sections. **NEVER overwrite existing section content.** Skip Phase 3 skeleton creation and run Phase 4 only on gaps.
- **Normalize filename**: Kebab-case (`combat system` -> `design/gdd/combat-system.md`).
- **Required sections by resolved tier** (`## Summary` is REQUIRED at **every** tier):
  - `full`: all 8 sections.
  - `standard`: 5 required (`Overview`, `Detailed Design` / `Detailed Rules`, `Edge Cases`, `Dependencies`, `Acceptance Criteria`) + **conditional `Formulas`** (required whenever the system **defines numeric rules**: rates, curves, thresholds, costs, damage, drop weights, or any balance-tunable value; `Category` in `systems-index.md` is a hint — `Gameplay`/`Economy`/`Progression` almost always qualify, and `Core`/`UI`/`Persistence` qualify if numeric rules exist — never gate solely on a category token). `Player Fantasy` & `Tuning Knobs` skipped unless `workflow_overrides.tuning_knobs: true`.
  - `minimal`: GDD optional. If authored voluntarily, author `## Summary` + the 5 standard sections ONLY — the conditional `Formulas` rule does **NOT** re-apply at `minimal`.

## 2. Gather Context (Before Any User Questions)

### 2a. Required Reads (Check **Project** Tier First!)
- **When the PROJECT tier is `minimal`** (even if `workflow_overrides.system_overrides.<stem>` bumps THIS system to `standard`/`full`): read `design/game-brief.md` instead of `game-concept.md`, **skip `systems-index.md`** (never create a stub index), and derive `Category` (one of the 9 categories in `.ags/templates/systems-index.md`), `Layer` (`Foundation` if depended on, else `Feature`), and `Priority` (`MVP` if in build order, else `Post-MVP`) from the brief. Carry all three forward and mark them `(inferred from the brief — no systems index at this tier)` in `## Summary`. Downstream authoring still uses this system's **effective** tier.
- **At `standard` / `full` projects**: Read `design/gdd/game-concept.md` and `design/gdd/systems-index.md` (fail if missing; warn if target system is off-index).
- **Entity registry (`design/registry/entities.yaml`)**: If present, extract live entries under `entities:`/`items:`/`formulas:`/`constants:` (`referenced_by` / `source` matching this system). **Ignore commented example blocks** in the template stub. Hold matched entries as locked cross-system facts.
- **Reflexion log (`docs/consistency-failures.md`)**: If present, extract entries matching this system's domain for `"Past failure patterns"`.

### 2b-2d. Dependency Reads & Context Summary
- Search existing dependency GDDs for ONLY the 4 contract sections (`## (Dependencies|Formulas|Edge Cases|Tuning Knobs)`, bounded slice) — rely on `entities.yaml` first; never search-read all `design/gdd/*.md` for "thematically related" docs.
- Read `design/gdd/game-pillars.md` and existing `design/gdd/<system>.md` if present.
- Present **Designing: [System Name]** summary (Priority, Layer, Upstream/Downstream deps, Constraints, Pillar alignment, Known cross-system facts, Past failure patterns; warn on undesigned upstream deps).

### 2e. Technical Feasibility Pre-Check
1. Map `Category` -> Engine Domain (`Gameplay` -> Physics / Navigation / Scripting; `Core` -> Core / Input; `UI` -> UI; `Audio` -> Audio; `Narrative`/`Progression`/`Economy` -> Scripting; `Persistence`/`Meta` -> Core; note Animation/Rendering/Networking explicitly when applicable).
2. Read `docs/engine-reference/<engine>/VERSION.md` and `modules/<domain>.md` + `breaking-changes.md`. **If `modules/<domain>.md` does not exist (e.g., `scripting.md`, `core.md`), announce explicitly by name** (*"no engine reference for `<domain>` under `docs/engine-reference/<engine>/modules/`; feasibility not checked against pinned engine"*) and carry into Phase 5-pre.
3. Search `docs/architecture/adr-*.md` for `**Domain**` first, then read only `## Decision` and `## Engine Compatibility` of matching ADRs.
4. Present **Technical Feasibility Brief** (or short engine-unconfigured note pointing to `ags-settings`) and confirm constraints before scaffolding.

## 3. Create File Skeleton

Prompt user to create `design/gdd/<system>.md`. If declined -> **`BLOCKED`** (stop immediately). Otherwise write skeleton using the **exact section set and order** of `.ags/templates/game-design-document.md`, omitting **only** sections skipped by the resolved tier (`Player Fantasy`, `Tuning Knobs`, and non-numeric `Formulas` at `standard`/`minimal`):

```markdown
# [System Name]
> **Status**: In Design | **Author**: [user + agents] | **Last Updated**: [YYYY-MM-DD] | **Last Verified**: [YYYY-MM-DD] | **Implements Pillar**: [pillar]
## Summary
[To be designed]
> **Quick reference** — Layer: `[Foundation | Core | Feature | Presentation]` · Priority: `[MVP | Vertical Slice | Alpha | Full Vision]` · Key deps: `[System names or "None"]`
## Overview ... ## Player Fantasy ... ## Detailed Design (### Core Rules, ### States and Transitions, ### Interactions with Other Systems) ... ## Formulas ... ## Edge Cases ... ## Dependencies ... ## Tuning Knobs ... ## Visual/Audio Requirements ... ## Game Feel ... ## UI Requirements ... ## Cross-References ... ## Acceptance Criteria ... ## Open Questions
```

Update `production/session-state/active.md` (`Current section: Starting (skeleton created)`).

## 4. Section-by-Section Design Cycle

Walk each required section in order via: `Context -> Questions -> Options -> Decision -> Draft -> Approval -> Write -> Registry Conflict Check`.
- **Approval rule**: In `collaborative`, present draft + `[A] Approve — write to file` / `[B] Make changes` / `[C] Start over` in the **same** response. In `guided`, write immediately after draft with a 1-line summary. In `autonomous`, write directly and log via decision log.
- **Unique write target**: Always include `## [Section Name]\n\n[To be designed]` so replacement never collides across sections. Update `active.md` after each section.
- **Registry conflict check (Sections C & D)**: Compare any entity, item, formula, or constant against `entities.yaml`. Surface mismatches immediately before moving on; flag new items for Step 5b.

### Section Rules & Specialist Routing
- **Section A (Overview)**: Pre-derive recommendations before prompting (`Framing` tab: `Gameplay|UI|Audio|Narrative` -> `[C] Both`, `Core|Persistence|Meta` -> `[A] Data/infra`, `Economy|Progression` -> `[C] Both`, **Category wins tiebreak over Layer**; `ADR ref` tab: check `adr-*.md`; `Fantasy` tab: Foundation -> `[B] No`, else `[A] Yes`). In `guided`/`autonomous`, pick pre-derived recommendations inline. Keep behavior-only (implementation questions -> note `-> becomes an ADR` for `ags-architect`).
- **Section B (Player Fantasy)**: Pre-derive framing (`Gameplay|UI|Audio|Narrative` -> `[A] Direct`, `Core|Persistence|Meta` -> `[B] Indirect`, `Economy|Progression` -> `[C] Both`; Category wins tiebreak). Apply `modes.review_mode` (`solo` skips with note, `lean` skips, `full` spawns `creative-director` before drafting).
- **Section C (Detailed Design / Detailed Rules)**: `## Detailed Design` and `Detailed Rules` denote the SAME required section. Include Core Rules, States/Transitions table, Interactions. Apply `modes.review_mode` (`solo` skips, `lean` skips, `full` spawns Primary + Supporting roles in parallel from Section 6 routing below; surface disagreements).
- **Section D (Formulas)**: Required format: expression + `| Variable | Type | Range | Source | Description |` (`Source` = `data file / calculated / constant`, matching `.ags/templates/game-design-document.md`!) + `Output Range` + `Example`. Apply `modes.review_mode` (`solo` skips, `lean` runs, `full` spawns `game-designer` (lens: `systems-designer`), plus lens `economy-designer` for economy/cost systems).
- **Section E (Edge Cases)**: Required format: `- **If [condition]**: [exact outcome]. [rationale]`. Never write vague handling. Apply `modes.review_mode` (`solo`/`lean` skip, `full` spawns `game-designer` lens `systems-designer`, plus `narrative-director` for narrative).
- **Section F (Dependencies)**: Hard vs soft, bidirectional check.
- **Section G (Tuning Knobs)**: Safe ranges, extreme effects, knob interactions. Apply `modes.review_mode` (`solo` derives from Section D with note, `lean` skips unless knobs interact, `full` delegates to `game-designer` lens `systems-designer`).
- **Section H (Acceptance Criteria)**: Given-When-Then, >=1 per rule + formula + cross-system check + performance budget. If Section D was skipped at `standard`, note criteria come from Section C alone — **if Section C introduced any numeric rule at `standard`, STOP and author Formulas first** (at `minimal`, keep numbers inline in Core Rules without re-enabling Formulas). Apply `modes.review_mode` (`solo` skips, `lean` runs, `full` spawns `qa-lead`).

### Category-Driven Sections (`Visual/Audio`, `Game Feel`, `UI`, `Cross-References`, `Open Questions`)
- **At `minimal`**: Force nothing optional — offer all unauthored optional sections via prompt.
- **At `standard`/`full`**:
  - **Visual/Audio REQUIRED** for `Gameplay | UI | Narrative | Audio` (apply `modes.review_mode`: `solo` skips, `lean` runs only when player reads visual events in `Gameplay`/`UI`, `full` spawns `art-ux-director` lens `art-director`). Optional for `Core | Progression | Economy | Persistence | Meta`. Emit Asset Spec Flag (`ags-art-ux asset-spec system:[name]`) when real content written.
  - **Game Feel REQUIRED** for `Gameplay | UI`; optional for the other 7 categories.
  - **Cross-References REQUIRED** whenever `Dependencies` names another GDD; if none, write `"None — this system references no other GDD"`.
  - **UI Requirements**: If real UI content written, emit UX Flag (`ags-art-ux ux-design` before epics).
  - Offer only **outstanding** optional sections (never offer to skip mandatory ones, never quote a fixed `/8` count, mark `(Recommended)` for `autonomous` selection).

## 5. Post-Design Validation & Handoff

- **5-pre (`## Summary`)**: Write 2-3 sentence `## Summary` + `> **Quick reference**` (mark Layer/Priority inferred if minimal brief) at **every** tier, noting any missing engine domain ref from 2e.
- **5a Self-Check**: Read back completed file on disk; run `python .ags/cli.py check gdd design/gdd/<system>.md`; verify against **effective tier** section count (never hardcoded `/8`), formulas, edge cases, interfaces, testable ACs.
- **5a-bis (`CD-GDD-ALIGN`)**: Apply `modes.review_mode` (`solo`/`lean` skip with note; `full` spawns `creative-director` reading `.ags/gates/cd-gdd-align.md`) and record verdict in GDD header.
- **5b (`design/registry/entities.yaml`)**: Check existence: if absent, confirm creating it (skip with explicit note if declined, never treat skip as clean); if present-but-empty, distinguish live keys from template comment examples; if present, diff against live entries, confirm additions/`referenced_by` updates, never mutate existing values without surfacing a conflict.
- **5c Fresh-Session Review Handoff**: Output completion summary and instruct the user to open a **fresh session** and run `ags-design-review design/gdd/<system>.md`. **NEVER offer or run `ags-design-review` in the same authoring session.**
- **5d (`systems-index.md`)**: Check existence first — if absent (e.g., `minimal`), note in one line and skip (never create a stub index); if present, confirm updating row (`Designed` unless reviewed) and Progress Tracker.
- **5e-5f (`active.md` & Next Steps)**: Update `active.md` listing authored section names (never write `"All 8 written"` below `full`), check >=70% context notice, and prompt next steps (`ags-design-review consistency`, next system, or `ags-gate`).

## 6. Specialist Routing Table (Core Roles + Domain Lenses)

Two-step lookup: match `Category` -> pick specific System Type (if two apply, spawn union of Primary roles):
- `Gameplay`: Combat/damage/health | AI/pathfinding | Animation/movement | Character systems | Camera/input
- `Core`: Foundation/Infra | Camera/input
- `Persistence` / `Progression` / `Economy` / `Audio` / `Narrative`: Foundation | Progression | Economy | Audio | Dialogue/lore
- `UI`: UI systems | Visual effects (HUD VFX)
- `Meta`: Foundation (analytics/tutorial plumbing) | UI systems (accessibility options)

| System Type | Primary Role (Core + Lens) | Supporting Roles (Core + Lenses) |
|---|---|---|
| Foundation / Infra | `game-designer` (`systems-designer`) | `gameplay-coder` (`engine-programmer`) |
| Combat / Damage / Health | `game-designer` | `game-designer` (`systems-designer`), `gameplay-coder` (`ai-programmer`), `art-ux-director` (`art-director`) |
| Economy / Loot / Crafting | `game-designer` (`economy-designer`) | `game-designer` (`systems-designer`) |
| Progression / XP / Skills | `game-designer` | `game-designer` (`systems-designer`, `economy-designer`) |
| Dialogue / Quests / Lore | `game-designer` | `game-designer` (`narrative-director`, `writer`), `art-ux-director` (`art-director`) |
| UI Systems (HUD / Menus) | `game-designer` | `art-ux-director` (`ux-designer`, `art-director`), `gameplay-coder` (`ui-programmer`), `tech-artist` |
| Audio Systems | `game-designer` | `tech-artist` (`audio-director`, `sound-designer`) |
| AI / Pathfinding | `game-designer` | `gameplay-coder` (`ai-programmer`), `game-designer` (`systems-designer`) |
| Level / World Systems | `game-designer` | `game-designer` (`level-designer`, `world-builder`) |
| Camera / Input / Controls | `game-designer` | `art-ux-director` (`ux-designer`), `gameplay-coder` |
| Animation / Movement | `game-designer` | `art-ux-director` (`art-director`), `tech-artist`, `gameplay-coder` |
| VFX / Particles / Shaders | `game-designer` | `art-ux-director` (`art-director`), `tech-artist`, `game-designer` (`systems-designer`) |
| Character Systems | `game-designer` | `art-ux-director` (`art-director`), `game-designer` (`narrative-director`, `systems-designer`) |

All spawned roles return proposals to the main session; the main session confirms with the user and owns all file writes. On interruption, resume from `production/session-state/active.md` and the next `[To be designed]` heading in `design/gdd/<system>.md`.
