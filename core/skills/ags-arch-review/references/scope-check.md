# Scope Creep Check (`ags-arch-review scope`)

Strictly **read-only** comparison between an original baseline plan and current implementation state to detect, quantify, and triage scope creep. Never modifies files.

## Phase 1: Locate Baseline Plan

Accept `<feature-name | sprint-N | milestone-name>`:
- **Feature name** -> `design/gdd/[feature].md` or matching file in `design/`.
- **Sprint number** (e.g., `sprint-3`) -> `production/sprints/sprint-03.md` (or `sprint-3.md`).
- **Milestone** -> `production/milestones/[name].md`.

If the baseline document does not exist on disk, report the missing file path and stop (`BLOCKED` / `NOT ASSESSED`).

---

## Phase 2: Inspect Current State

1. Resolve code root (`src/`, `Assets/`, `Source/`) via preflight (`NOT ASSESSED` if code root unresolved when evaluating code).
2. Scan code root files related to the feature or sprint.
3. Inspect recent commits (`git log --oneline --since=[start-date]`), `TODO`/`FIXME` additions, and active sprint plan (`production/sprint-status.yaml` / `production/sprints/`).

---

## Phase 3: Compare Baseline vs Current & Bloat Score

Check whether the comparison denominator is usable BEFORE rendering any numeric counts or percentages:
- **Unusable baseline / unreadable current state**: If the baseline document contains zero concrete scope items (only headings/placeholders), current state has no readable code/commits/work-in-progress, or the denominator is zero, **DO NOT render the numeric counts or Bloat Score block (`Original items: 0 / Net scope change: 0%`)**. Replace that block with:
  `Baseline unusable — see verdict` + specific reason, so `0%` never renders above a `NOT ASSESSED` verdict.

When measurable, output:
- **Original Scope** and **Current Scope** lists
- **Scope Additions** table (`Addition | Source | When | Justified? | Effort`)
- **Scope Removals** table (`Removed Item | Reason | Impact`)
- **Bloat Score**: Original items, Current items, Items added (`+X%`), Items removed, Net scope change (`+/-N`, `X%`)
- **Risk Assessment**: Schedule, Quality, and Integration risk (`Low | Medium | High`)
- **Recommendations**: `Cut`, `Defer`, `Keep`, and `Flag` (for `producer` / `creative-director`)

---

## Phase 4: Verdict

Emit **`NOT ASSESSED`** (never `0%` PASS) whenever:
1. Baseline file exists but enumerates zero scope items (placeholders/headings only).
2. Current state cannot be determined (no related source files, no commits in window, nothing in progress).
3. Denominator is zero for any reason.

Otherwise score net scope change:

| Net Change | Verdict | Meaning |
|---|---|---|
| `<= 10%` | **PASS** | On Track — within acceptable variance |
| `10–25%` | **CONCERNS** | Minor Creep — manageable with targeted cuts |
| `25–50%` | **FAIL** | Significant Creep — must cut or extend timeline |
| `> 50%` | **FAIL** | Out of Control — stop, re-plan, escalate to `producer` |

**Ordering**: `NOT ASSESSED` ranks above `PASS` and below `CONCERNS` and `FAIL`. Format:
`Scope Verdict: [PASS | CONCERNS | NOT ASSESSED | FAIL]` with exact net change % or `[NOT ASSESSED — <which side unreadable and why>]`.

---

## Phase 5: Follow-Up Routing

- **PASS**: Suggest re-running before next milestone.
- **NOT ASSESSED**: Name which side was unreadable and how to populate/locate it; do NOT suggest re-running identical inputs.
- **CONCERNS**: Identify top 2–3 cut candidates with best cut ratio; route to `ags-plan sprint update`.
- **FAIL**: Escalate to `producer`; route to `ags-plan sprint update` or `ags-plan estimate` to re-baseline. Remind user to re-run `ags-arch-review scope [name]` after cuts.
