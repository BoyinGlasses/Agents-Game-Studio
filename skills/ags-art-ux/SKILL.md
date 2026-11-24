---
name: ags-art-ux
description: "Use when authoring the art bible, building an entity inventory or per-asset specs, auditing delivered assets, designing UX/HUD/patterns/accessibility specs, or reviewing UX specs. Do NOT use when brainstorming visual anchors (-> ags-ideate), authoring gameplay GDDs (-> ags-gdd), or reviewing GDDs (-> ags-design-review)."
---

# Art Direction, Asset Pipeline & UX Design

Unifies visual identity authoring (`art-bible`), asset inventories and per-asset specs (`asset-spec`), measurement-backed asset audits (`asset-audit`), UX/HUD/pattern/accessibility authoring (`ux-design`), and UX validation (`ux-review`).

## Contract

- **Inputs**: `design/gdd/game-concept.md`, `design/art/art-bible.md`, `design/assets/{entity-inventory,asset-manifest}.md`, `design/assets/specs/*.md`, `assets/{art,audio,vfx,shaders,data}/**/*`, `design/player-journey.md`, `design/accessibility-requirements.md`, `design/ux/*.md`, `design/gdd/*.md`, `design/levels/*.md`, `design/narrative/**`, `design/registry/entities.yaml`, `project.yaml`.
- **Roles**: `art-ux-director` (lenses: `art-director`, `ux-designer`, `accessibility-specialist`; AD-ART-BIBLE), `tech-artist` (lens: `audio-director`), `gameplay-coder` (lens: `ui-programmer`), `game-designer` (lenses: `narrative-director`, `game-designer`), `scout` (optional asset/reference lookup).
- **Outputs**: `design/art/art-bible.md`, `design/assets/{entity-inventory,asset-manifest}.md`, `design/assets/specs/<target>-assets.md`, read-only Asset Audit Report, `design/ux/<screen-or-hud-or-interaction-patterns>.md`, `design/accessibility-requirements.md`, read-only UX Review Report, `production/session-state/active.md`.
- **Verification**: Binary file measurements (sizes, dimensions, sample rates, mtimes) verified via shell commands or marked `NOT ASSESSED`; accessibility checked against `design/accessibility-requirements.md` or marked `NOT ASSESSED`; AD-ART-BIBLE verdict recorded in `full` review mode; `ux-review` and `asset-audit` remain strictly read-only.
- **Next Skill**: `ags-gdd` (`map-systems` / `design-system`), `ags-design-review` (`review-all-gdds` / `consistency` / `content-audit`), `ags-architect`, `ags-team` (`ui` mode), or `ags-gate`.

## Preflight

Run once at startup and hold resolved settings for the run:

```bash
python .ags/cli.py preflight ags-art-ux [mode-or-target]
```

- Resolve `modes.workflow`, `workflow_overrides.art_bible_strict`, `docs.density` (`terse` / `balanced` / `thorough`), `modes.automation`, and `modes.review_mode` (`--review [full|lean|solo]` overrides).
- Read `engine.name`, `performance.*`, `naming.*`, and `platform.*` from `project.yaml` (fall back to legacy `technical-preferences.md` if present).

| Mode | Trigger | Reference |
|---|---|---|
| `art-bible` | 9-section visual identity bible or pattern-search retrofit | [references/art-bible.md](references/art-bible.md) |
| `asset-spec` | Entity/screen inventory (`Phase 0b`) or `ASSET-NNN` specs | [references/asset-spec.md](references/asset-spec.md) |
| `asset-audit` | Read-only naming, format, size-budget, orphan, missing audit | [references/asset-audit.md](references/asset-audit.md) |
| `ux-design` | Screen/flow, `hud`, `patterns`, or `accessibility` spec authoring | [references/ux-design.md](references/ux-design.md) |
| `ux-review` | Read-only UX spec, `hud`, `patterns`, or `all` validation | [references/ux-review.md](references/ux-review.md) |

## Phases

### 1. Art Bible (`art-bible`)
- Follow [references/art-bible.md](references/art-bible.md).
- **Tier & retrofit**: `full` or `workflow_overrides.art_bible_strict: true` -> all 9 sections; `standard` -> sections 1-4 when visual asset stories exist (recommended option derived from tier); `minimal` -> optional. If `design/art/art-bible.md` exists, detect section status via heading + placeholder pattern search without reading complete sections (bounded line-range read only when ambiguous) and fill only `Empty`/`Placeholder` sections.
- **Delegation batching**: Section 1 spawns `art-ux-director` (`art-director`) solo -> approve & write immediately. Sections 2-4 use **one** batched `art-ux-director` call returning 3 mutually consistent blocks, approved & written one section at a time. Sections 5-6 use **one** batched `art-ux-director` call ensuring character/environment legibility, approved & written one by one. Section 7 pairs `art-director` + `ux-designer`; Section 8 pairs `art-director` + `tech-artist`; Section 9 compiles 3-5 additive references. Surface any specialist conflicts directly.
- **Sign-off (`AD-ART-BIBLE`)**: In `full` review mode (`solo`/`lean` skip with note), spawn `art-ux-director` (`art-director`) reading `.ags/gates/ad-art-bible.md` and record verdict in header.

### 2. Asset Specs & Inventory (`asset-spec`)
- Follow [references/asset-spec.md](references/asset-spec.md).
- No-arg routing: check `design/assets/entity-inventory.md` -> else `design/assets/asset-manifest.md` -> else run **Phase 0b (Entity & Screen Inventory)** to build `design/assets/entity-inventory.md` from `systems-index.md`, GDD `Visual/Audio Requirements` + `UI Requirements` searches, `entities.yaml`, `art-bible.md`, and `design/narrative/`.
- Require `design/art/art-bible.md`; run Shared Asset Protocol and global sequential `ASSET-NNN` assignment; default review mode for `asset-spec` comes from resolved `modes.review_mode` (`lean` default -> `art-director` only; `full` -> parallel `art-director` + `tech-artist`; `solo` -> art bible alone).
- **External API guard**: Any live external image-generation API call MUST unconditionally prompt the user regardless of `modes.automation`.

### 3. Asset Audit (`asset-audit`) — Read-Only
- Follow [references/asset-audit.md](references/asset-audit.md).
- Run **Insufficient Input Gate** first (`FOUND` vs `ABSENT` per input). Measure file sizes, texture dimensions, audio sample rates, and mtimes via shell tools — any unmeasurable cell or absent input MUST be reported as `NOT ASSESSED` (never estimate or emit clean `COMPLIANT` over zero data).

### 4. UX Design (`ux-design`) — Screen / `hud` / `patterns` / `accessibility`
- Follow [references/ux-design.md](references/ux-design.md) and load **ONLY the ONE active mode's section guide**: [references/sections-ux-spec.md](references/sections-ux-spec.md), [references/sections-hud.md](references/sections-hud.md), [references/sections-patterns.md](references/sections-patterns.md), or `.ags/templates/guidance/accessibility-requirements-guide.md`.
- `accessibility` writes strictly to `design/accessibility-requirements.md` (not `design/ux/`); `hud` verifies GDD denominator `N` so headless systems are confirmed before omission; retrofit mode edits placeholders in-place only; fresh specs create skeleton first.

### 5. UX Review (`ux-review`) — Read-Only
- Follow [references/ux-review.md](references/ux-review.md) using Checklists 3A (`ux-spec`), 3B (`hud`), and 3C (`patterns`), evaluating inputs against `project.yaml` `platform.*`. Missing `design/accessibility-requirements.md` (uncommitted tier) forces `Accessibility: NOT ASSESSED` and blocks `APPROVED`.

## Gate & Verdict

- **`COMPLETE` / `COMPLIANT` / `APPROVED`**: Target deliverable written or validated cleanly against all required dimensions.
- **`NOT ASSESSED`** *(ranks ABOVE `COMPLETE` / `COMPLIANT` / `APPROVED` and BELOW `NEEDS REVISION` / `MAJOR REVISION NEEDED` / `NON-COMPLIANT` / `REJECT` / `BLOCKED`)*: Required inputs (`art-bible.md`, `accessibility-requirements.md`, asset standards, binary files) are absent/unreadable, or shell measurements/checklist dimensions could not execute — list every unassessed item and its remediation.
- **`NEEDS REVISION` / `MAJOR REVISION NEEDED` / `WARNINGS` / `NON-COMPLIANT` / `BLOCKED` / `REJECT`**: Blocking gaps, standards violations, declined writes, or director rejection requiring fixes before production handoff.
