> Gate definition, loaded by `ags-gate` for Technical Setup -> Pre-Production ONLY.

# Gate: Technical Setup -> Pre-Production

**Required Artifacts:**
- [ ] Engine chosen (`engine.name` set in `project.yaml`, `AGENTS.md` Technology Stack not `[CHOOSE]`)
- [ ] Project config populated (`project.yaml` has engine, naming, and performance targets set)
- [ ] Art bible exists at `design/art/art-bible.md` with at least Sections 1–4 (Visual Identity Foundation)
- [ ] At least 3 Architecture Decision Records in `docs/architecture/adr-*.md` covering Foundation-layer systems (scene management, event architecture, save/load)
- [ ] Engine reference docs exist in `docs/engine-reference/<engine>/`
- [ ] Test framework initialized (`tests/unit/` and `tests/integration/` directories exist)
- [ ] CI/CD test workflow exists at `.github/workflows/tests.yml` (or configured equivalent)
- [ ] At least one example test file confirms test runner works
- [ ] Master architecture doc exists at `docs/architecture/architecture.md`
- [ ] Architecture traceability index exists at `docs/architecture/requirements-traceability.md`
- [ ] `ags-arch-review` has been run (review report exists in `docs/architecture/`)
- [ ] `design/accessibility-requirements.md` exists with accessibility tier committed
- [ ] `design/ux/interaction-patterns.md` exists (pattern library initialized)

**Quality Checks:**
- [ ] Architecture decisions cover core systems (rendering, input, state management)
- [ ] Naming conventions and performance budgets are configured
- [ ] Accessibility tier is defined and documented
- [ ] At least one screen UX spec started (main menu or core HUD)
- [ ] All ADRs have `Engine Compatibility` stamped with pinned engine version
- [ ] All ADRs have `GDD Requirements Addressed` linking GDD items
- [ ] No ADR uses APIs from `docs/engine-reference/<engine>/deprecated-apis.md`
- [ ] All `HIGH RISK` engine domains (per `VERSION.md`) addressed or tracked as open questions
- [ ] Zero Foundation-layer traceability gaps

**ADR Circular Dependency Check**:
Run `python .ags/cli.py check adr-graph`:
- Any `CYCLE:` line -> **FAIL** (break dependency cycle before ADRs can reach `Accepted`).
- Many `NO_DEPS_SECTION` ADRs -> **CONCERNS** note.

**Engine Validation** (`docs/engine-reference/<engine>/VERSION.md`):
- [ ] Post-cutoff ADRs flagged `Knowledge Risk: HIGH/MEDIUM`
- [ ] `ags-arch-review` audit shows no deprecated API usage
- [ ] All ADRs agree on same pinned engine version

## Workflow Tier Reductions

Baseline above is **`full`**:
- **`full`** — engine + art bible §1–4+ + 3+ ADRs + architecture + UX started + accessibility doc + traceability index all required
- **`standard`** — art bible required **only if visual-asset stories exist** (unless `workflow_overrides.art_bible_strict: true`); ADRs reduced to **critical (Foundation-layer) only**; UX started, accessibility doc, interaction patterns, traceability index -> recommended (`CONCERNS` if absent)
- **`minimal`** — only **engine configured** required (minimal floor); everything else **drops** (except `performance.enforce` remains active when configured)
