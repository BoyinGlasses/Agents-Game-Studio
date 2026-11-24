> Gate definition, loaded by `ags-gate` for Systems Design -> Technical Setup ONLY.

# Gate: Systems Design -> Technical Setup

**Required Artifacts:**
- [ ] Systems index exists at `design/gdd/systems-index.md` with MVP systems enumerated
- [ ] All MVP-tier GDDs exist in `design/gdd/` and individually pass `ags-design-review`
- [ ] Cross-GDD review report exists in `design/gdd/gdd-cross-review-*.md` (`ags-design-review` review-all mode)

**Quality Checks:**
- [ ] All MVP GDDs pass individual design review (8 required sections at `full`, no `MAJOR REVISION NEEDED` verdict)
- [ ] Cross-GDD review verdict is not `FAIL`
- [ ] All cross-GDD consistency issues flagged by `ags-design-review` are resolved or explicitly accepted
- [ ] System dependencies in `systems-index.md` are bidirectionally consistent
- [ ] MVP priority tier is defined
- [ ] No stale GDD references flagged across later GDD revisions

## Workflow Tier Reductions

Baseline above is **`full`** (apply `workflow_overrides.system_overrides.<stem>` per MVP GDD):
- **`full`** — `systems-index.md` + all MVP GDDs at 8 sections + cross-GDD review report all required
- **`standard`** — MVP GDDs validated at the **5 standard sections** (`Overview`, `Player Fantasy`, `Detailed Rules`, `Edge Cases`, `Acceptance Criteria` + conditional `Formulas` when numeric rules exist); cross-GDD review report -> recommended (`CONCERNS` if absent)
- **`minimal`** — **gate not applicable**: auto-`PASS` with note: *"No design gate at minimal workflow — minimal skips the Systems Design phase; advancing brief -> code."* Do NOT flag absent GDDs as blockers; still confirm user before updating stage.
