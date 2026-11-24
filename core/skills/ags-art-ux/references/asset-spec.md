# Entity Inventory & Per-Asset Spec Workflow (`ags-art-ux`)

Produces `design/assets/entity-inventory.md` (`Phase 0b`) and per-asset `ASSET-NNN` visual specs + generation prompts (`design/assets/specs/[target]-assets.md`, `design/assets/asset-manifest.md`).

## Entry Routing & External-Call Guard

- **No argument**: Check `design/assets/entity-inventory.md` -> else `design/assets/asset-manifest.md` -> locate first `"Needed"` item with no spec file and offer `[A] Yes — spec [name]` / `[B] Pick different` / `[C] Stop`. If neither file exists -> start **Phase 0b** rather than failing.
- **With argument**: Parse `<system|level|character>:<name>` (kebab-case) and optional `--review [full|lean|solo]` (overrides preflight `modes.review_mode`, whose default is `lean`).
- **Unconditional external-call guard**: Prompting/generating prompt *text* proceeds normally, but actually invoking any external image-generator API MUST unconditionally prompt the user regardless of `modes.automation`.

---

## Phase 0b: Entity & Screen Inventory (No Args & No Inventory/Manifest)

1. **Gather from docs**: Read `design/gdd/systems-index.md`; pattern-search `design/gdd/*.md` for `## (Visual/Audio Requirements|UI Requirements)` (full-read a GDD only if that section is absent or `[To be designed]`); read `design/registry/entities.yaml` (`entities`/`items`) if populated; read `design/art/art-bible.md` and scan `design/narrative/`.
2. **Categorize** with source-doc citations: Characters/Protagonists, Enemies/Creatures, Buildings/Structures, Environment/Terrain, Items/Props, VFX/Particles, UI Screens, HUD Elements, Audio (SFX/Music descriptions only — no generation prompts), Other.
3. **Collaborate**: Present inventory and prompt (`[A] Save` / `[B] Add` / `[C] Remove` / `[D] Both`).
4. **Confirm & write `design/assets/entity-inventory.md`** with tables for `## Entities` (`# | Name | Type | Description | Source | Status`), `## UI Screens`, `## HUD Elements`, and `## Audio` (`Needed` initial status). Hand off to `ags-art-ux ux-design [screen]` or `ags-art-ux asset-spec entity:[name]`.

---

## Phases 0-6: Per-Asset Spec Generation

### Phase 1: Gather Context
- **Required**: `design/art/art-bible.md` (fail and point to `ags-art-ux art-bible` if missing); extract Visual Identity Statement, Color System, Shape Language, Asset Standards (§8). Read `performance.*` and `naming.*` from `project.yaml` (else legacy `technical-preferences.md`).
- **Source doc by target type**:
  - `system`: `design/gdd/[target].md` (`Visual/Audio Requirements`; if empty/`[To be designed]`, ask `[A] Describe needs manually` / `[B] Stop`).
  - `level`: `design/levels/[target].md`.
  - `character` / `entity`: `design/narrative/characters/[target].md` or `entity-inventory.md`; if absent, do NOT fail — ask `[A] Describe it now` / `[B] Skip` / `[C] Stop`.
- **Optional**: `design/assets/asset-manifest.md` (prevent duplicates + find highest `ASSET-NNN`) and `design/assets/specs/*.md` (shared assets).

### Phase 2: Asset Identification
Group extracted assets into `Sprite / 2D Art`, `VFX / Particles`, `Environment`, `UI`, `Audio` (sonic character descriptions only, no image prompts), `3D Assets`. Confirm grouped list before Phase 3.

**Shared Asset Protocol**: Before creating a duplicate, check existing `design/assets/specs/*.md`; if matched, reuse the existing `ASSET-NNN` ID and append this target to `referenced-by` in the manifest.
**Asset ID Assignment**: Scan `design/assets/asset-manifest.md` for `ASSET-` and start new assets at `ASSET-[highest + 1]` (or `ASSET-001` if absent).

### Phase 3: Spec Generation
- `full`: Spawn `art-ux-director` (`art-director`: 2-3 sentence visual description anchored to Shape Language & Color System, AI image generation prompt with keywords/composition/palette/negative prompts or sonic character for audio, cite art bible sections) AND `tech-artist` (exact dimensions/polycount matching §8 tiers, file format/export settings, `naming.*` convention, engine constraints, LODs) in **parallel**. Surface conflicts explicitly.
- `lean`: Spawn `art-ux-director` (`art-director`) only.
- `solo`: Derive directly from art bible rules; flag technical constraints unvalidated.

### Phase 4-6: Compile, Write & Error Recovery
1. Present specs in `ASSET-NNN` format (`Category | Dimensions | Format | Naming | Polycount | Texture Res`, Visual Description, Art Bible Anchors, Generation Prompt, `Status: Needed`). Prompt `[A] Approve` / `[B] Revise inline` / `[C] Regenerate`.
2. Confirm & write `design/assets/specs/[target-name]-assets.md`; create or update `design/assets/asset-manifest.md` (Progress Summary counts + Assets by Context table).
3. Close with options for next system/level/character, `ags-art-ux asset-audit`, or stop.
4. **Error Recovery**: If `tech-artist` blocks -> proceed with `art-director` noting technical constraints unvalidated; if `art-director` blocks -> derive from art bible noting verification needed; always preserve partial output.
