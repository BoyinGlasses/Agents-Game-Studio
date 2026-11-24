> Gate definition, loaded by `ags-gate` for Concept -> Systems Design ONLY.

# Gate: Concept -> Systems Design

**Required Artifacts:**
- [ ] `design/gdd/game-concept.md` exists and has non-placeholder content
- [ ] Game pillars defined (inside `design/gdd/game-concept.md` or `design/gdd/game-pillars.md`)
- [ ] Visual Identity Anchor section exists in `design/gdd/game-concept.md` (from `ags-ideate` art-ux-director output)

**Recommended (not blocking):**
- [ ] Concept prototype exists in `prototypes/` with a `REPORT.md` showing `PROCEED` verdict (`ags-ideate` prototype mode)

**Quality Checks:**
- [ ] Game concept reviewed (`ags-design-review` verdict not `MAJOR REVISION NEEDED`)
- [ ] Core loop is described and understood
- [ ] Target audience is identified
- [ ] Visual Identity Anchor contains a one-line visual rule and at least 2 supporting visual principles

## Workflow Tier Reductions

Baseline above is **`full`**:
- **`full`** — `game-concept.md` + pillars + Visual Identity Anchor all required
- **`standard`** — pillars + Visual Identity Anchor -> recommended (`CONCERNS` if absent); `game-concept.md` stays required
- **`minimal`** — gate target is **`design/game-brief.md`** (not `game-concept.md`); GDD, pillars, and Visual Identity Anchor checks **drop** (a brief with content = `PASS`). `ags-ideate` writes `design/game-brief.md` at `minimal`; `game-concept.md` remains the `standard`/`full` concept doc.
