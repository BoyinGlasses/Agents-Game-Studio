> Gate definition, loaded by `ags-gate` for Pre-Production -> Production ONLY.

# Gate: Pre-Production -> Production

**Required Artifacts:**
- [ ] Vertical slice exists in `prototypes/*-vertical-slice/REPORT.md` (`ags-ideate`) — **recommended, not blocking** (`CONCERNS` if absent)
- [ ] First sprint plan exists in `production/sprints/`
- [ ] Art bible complete (all 9 sections) with `AD-ART-BIBLE` sign-off in `design/art/art-bible.md`
- [ ] Entity inventory at `design/assets/entity-inventory.md` — recommended (`ags-art-ux`)
- [ ] All MVP-tier GDDs from `design/gdd/systems-index.md` are complete
- [ ] Master architecture doc exists at `docs/architecture/architecture.md`
- [ ] At least 3 Foundation-layer ADRs exist in `docs/architecture/`
- [ ] All Foundation and Core ADRs have `Status: Accepted` (not `Proposed`)
- [ ] Control manifest exists at `docs/architecture/control-manifest.md` (`ags-architect`)
- [ ] Epics defined in `production/epics/` (Foundation + Core layers) and broken into stories (`ags-plan`)
- [ ] Vertical slice build playable, >=1 documented playtest session, and playtest report in `production/qa/playtests/` — **recommended, not blocking** (`CONCERNS` if absent)
- [ ] UX specs exist in `design/ux/` (main menu, core gameplay HUD at `design/ux/hud.md`, pause menu) and passed `ags-art-ux` UX review (`APPROVED` or accepted `NEEDS REVISION`)

**Quality Checks:**
- [ ] **Core loop fun validated** via playtest data
- [ ] UX specs cover all UI Requirements from MVP GDDs, match `design/ux/interaction-patterns.md`, and satisfy `design/accessibility-requirements.md` tier
- [ ] Sprint plan references real story files in `production/epics/`
- [ ] **Vertical Slice is COMPLETE** (full start -> challenge -> resolution cycle) if built
- [ ] Architecture has no unresolved Foundation/Core open questions; ADRs carry `Engine Compatibility` and `ADR Dependencies`
- [ ] Cross-GDD and architecture coherence verified (`ags-design-review`, `ags-arch-review`)
- [ ] **Core fantasy delivered** (unprompted playtester feedback matches core GDD Player Fantasy)

**Vertical Slice Validation** *(run ONLY if a Vertical Slice was built)*:
- [ ] Human played core loop without developer guidance
- [ ] Game communicates objective within first 2 minutes
- [ ] Zero critical fun-blocker bugs
- [ ] Core mechanic feels good to interact with (ask user directly)

> **Vertical Slice Verdict Rule (applies at EVERY tier):**
> - Slice was built AND any validation item is `NO` -> **automatic `FAIL`**.
> - Slice was not built -> downgrade to `CONCERNS` ("Advancing without a validated Vertical Slice increases late-pivot risk").

## Workflow Tier Reductions

Baseline above is **`full`**:
- **`full`** — sprint plan + 9-section art bible + epics + 3+ playtests + UX specs + control manifest all required; Vertical Slice keeps Section 2 recommended status
- **`standard`** — **1+ playtest** required; epics + sprint plan required; complete art bible + UX specs + control manifest -> recommended (`workflow_overrides.art_bible_strict: true` forces complete art bible)
- **`minimal`** — only **sprint plan** required (minimal floor); epics, playtests, art bible, UX, control manifest **drop** (note: `game-brief.md` build order satisfies minimal planning when sprints are absent only if user confirms; built broken Vertical Slice still returns `FAIL`)
