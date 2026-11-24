# Sprint / Milestone Retrospective (`ags-plan retro`)

Analyzes planned vs actual delivery, velocity trends, estimation accuracy, carryover, technical debt trends, and action items for the next iteration.

## Insufficient Input Guard (Always Check First)

Inventory required inputs (`sprint plan / milestone definition`, `production/sprint-status.yaml`, `git log`, `resolved code root`, `previous retrospectives`) and mark each `FOUND` or `ABSENT`:
- Missing section inputs -> mark section **`NOT ASSESSED — NO DATA`** (never guess).
- All required inputs missing and user declines manual entry -> stop with **`NOT ASSESSED — NO DATA`**.

---

## Phase 1: Parse Target & Check Existing Retrospective

1. Determine target: `sprint-N` or `<milestone-name>`.
2. Search for existing retrospectives BEFORE loading sprint data:
   - Sprint: `production/retrospectives/retro-[sprint-slug]-*.md` or `production/sprints/sprint-[N]-retrospective.md`
   - Milestone: `production/retrospectives/retro-[milestone-name]-*.md`
3. If a matching file exists, prompt the user:
   - `[A] Update existing — revise sections with new data`
   - `[B] Start fresh — generate a new retrospective (archive old file with -archived-[date] suffix before writing)`

---

## Phase 2: Load Data & Git History

1. Read sprint plan (`production/sprints/`) or milestone definition (`production/milestones/`) alongside `production/sprint-status.yaml` (authoritative completion status, dates, blockers; note any discrepancies against markdown).
2. If sprint/milestone data is absent or empty, route hint to `ags-plan status` and prompt: `[A] Provide sprint data manually` or `[B] Stop (BLOCKED)`.
3. Run `git log --oneline --since="<period>"` (fallback `git log --oneline -20`) to verify actual commit activity.

---

## Phase 3: Analyze Completion, Debt & Previous Actions

- Classify tasks: completed as planned, completed modified, carried over, added unplanned mid-sprint, removed/descoped.
- Resolve code root (`src/`, `Assets/`, `Source/`) via preflight (`NOT ASSESSED` if unresolved), count `TODO` / `FIXME` / `HACK` comments, and compare against previous retrospectives in `production/retrospectives/` for debt direction (`Growing | Stable | Shrinking`).
- Audit previous retrospective action items (`Done | In Progress | Not Started`) to surface recurring systemic blockers without blaming individuals.

---

## Phase 4: Generate Retrospective Report

Emit structured sections:
- `### Metrics` (Tasks, Completion Rate, Effort Days, Bugs Found/Fixed, Unplanned Added, Commits)
- `### Velocity Trend` (last 3 sprints + `Increasing | Stable | Decreasing`)
- `### What Went Well` & `### What Went Poorly`
- `### Blockers Encountered` (`Blocker | Duration | Resolution | Prevention`)
- `### Estimation Accuracy` (`Estimated | Actual | Variance | Likely Cause`, `% within +/- 20%`)
- `### Carryover Analysis` (`Task | Original Sprint | Times Carried | Reason | Action`)
- `### Technical Debt Status` (`TODO / FIXME / HACK` counts + trend)
- `### Previous Action Items Follow-Up`
- `### Action Items for Next Iteration` (limit 3–5 concrete items, each with Owner, Priority, Deadline)
- `### Process Improvements` (2–3 actionable changes) & `### Summary`

---

## Phase 5: Save & Next-Sprint Handoff

1. Summarize completion rate, velocity trend, top blocker, and top action item, then confirm write to `production/retrospectives/retro-sprint-[N]-[date].md` (or `retro-[milestone-name]-[date].md`). Archive old file with `-archived-[date]` first if `[B] Start fresh` was selected.
2. Prompt to start `ags-plan sprint new` pre-loaded with retrospective action items and velocity delta (and recommend `ags-gate` for milestone retrospectives).
