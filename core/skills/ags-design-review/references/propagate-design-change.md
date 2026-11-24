# Design Change Propagation Workflow (`ags-design-review`)

Finds every ADR and downstream GDD affected by a GDD modification, classifies validity, runs `TD-CHANGE-IMPACT`, and updates traceability.

## Step 1-3: Validate, Git Diff Hunks & Change Summary

1. **Validate required `<gdd-path>`**: Verify file exists; otherwise fail clearly with usage. Resolve **system workflow tier** (`system_overrides.<stem>` -> `modes.workflow` -> `modes.rigor`): `full` checks all ADRs, `standard` checks critical Foundation ADRs + referencing ADRs, `minimal` reports N/A (no ADRs) and stops.
2. **Diff via git (never compare whole documents by eye)**:
   - Run `git diff HEAD -- <gdd-path>`; if empty, run `git diff HEAD~1 HEAD -- <gdd-path>`.
   - Distinguish **no git history** (new file — nothing to propagate), **empty diff with history** (ask which commit/revision to propagate), and **non-empty hunks**.
   - Use `@@` hunk headers to identify changed sections; read surrounding section ONLY when a tiny numeric diff needs rule context. Unchanged sections need no read.
3. **Change Summary & Registry Downstream GDDs**: List Changed vs Unchanged sections and architecture-relevant changes. If `design/registry/entities.yaml` lists entries with `source: <gdd-path>`, collect their `referenced_by:` paths under `"Downstream GDDs to re-check"`.

## Step 4 & Step 5: ADR Scan & Bounded Impact Analysis

1. **Establish ADR denominator `N`**: Count in-scope `docs/architecture/adr-*.md` files per resolved tier. If `N = 0`, stop cleanly.
2. **Two-scan union `M`**:
   - Scan A: Search `## GDD Requirements Addressed` (`-A 15`) across `docs/architecture/adr-*.md`.
   - Scan B (prose recall net): Search files matching `[changed-gdd-basename]` in `docs/architecture/adr-*.md`.
   - Take union **M** (`N - M` non-matching ADRs are out of scope, not `"verified unaffected"`).
   - **If `M = 0` and `N > 0`**: Search for `## GDD Requirements Addressed` presence across `adr-*.md`. If absent everywhere -> emit **`NOT ASSESSED`** (*"ADRs lack `GDD Requirements Addressed` tables — traceability cannot be computed; run `ags-architect` ADR retrofit"*). If tables exist everywhere and none match -> `"No ADR references [gdd] — no architecture impact."`
3. Read `docs/architecture/requirements-traceability.md` if present.
4. **Bounded ADR reads (only on set `M`)**: Check byte size first (`wc -c`):
   - **Under 50KB**: Full read of the ADR.
   - **50KB or larger**: Map `^## ` headings with line numbers first, then bounded line-range read ONLY `## Context`, `## Decision`, and `## Consequences`.
5. Classify each affected ADR (`Still Valid` / `Needs Review` / `Likely Superseded`) quoting prior assumption vs new GDD rule and recommended action.

## Step 6-10: Report, Technical Director Gate, Resolution & Traceability

1. Present full **Design Change Impact Report** (`Not Affected`, `Needs Review`, `Likely Superseded`).
2. **Director Gate `TD-CHANGE-IMPACT`**: Apply `modes.review_mode` (`solo`/`lean` skip with note; `full` spawns `technical-director` reading `.ags/gates/td-change-impact.md` with the full impact report). On `CONCERNS`, prompt (`Revise impact assessment` / `Accept with concerns` / `Discuss`); on `REJECT`, re-analyze before resolution.
3. **Per-ADR Resolution**: Walk each `Needs Review` / `Likely Superseded` ADR individually (`Mark Superseded` -> confirm status update `Superseded by ADR-[next] (pending — see change-impact-[YYYY-MM-DD]-[system].md)` / `Update in place` / `Keep as-is` / `Skip`). Respect `modes.automation_always_ask` (`schema_changes` / `architecture_decisions`). Never delete ADR content.
4. **Confirm updates**:
   - Append changed requirements to `## Superseded Requirements` in `docs/architecture/requirements-traceability.md` if present.
   - Write `docs/architecture/change-impact-[YYYY-MM-DD]-[system-slug].md` (`COMPLETE`, or `BLOCKED` if write declined).
5. **Follow-ups**: Direct superseded ADRs to `ags-architect` (`adr [title]`), then re-run `ags-design-review propagate` or `ags-arch-review`.
