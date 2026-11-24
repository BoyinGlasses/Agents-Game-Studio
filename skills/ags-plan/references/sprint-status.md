# Sprint Status Snapshot (`ags-plan status`)

Strictly **read-only**, concise (`< 50` lines) sprint progress, stale-story, burndown, and risk snapshot. Never modifies files and makes at most one concrete recommendation.

## Phase 1: Locate Sprint & Timeline

1. If a sprint number argument is provided, locate matching `production/sprints/sprint-0N.md` / `sprint-N.md`. Otherwise take the most recently modified file in `production/sprints/`. If none exist, report `"No sprint files found. Start a sprint with ags-plan sprint new."` and stop (`NOT ASSESSED`).
2. Extract sprint number, goal, start/end dates, and entries (`Must Have`, `Should Have`, `Nice to Have`).
3. Compute total days, days elapsed, days remaining, and `% time consumed`. If dates are missing, explicitly note `"Sprint dates not found — burndown assessment skipped."`
4. Account for `story_granularity` grain (`coarse` = feature chunks, `balanced` = task chunks, `fine` = AC chunks).

---

## Phase 2: Resolve Status & Stale Story Detection

1. **Primary source (`production/sprint-status.yaml`)**: Read YAML `status`, `sprint`, `goal`, `start`, and `end` directly when present.
2. **Markdown fallback**: Only if `production/sprint-status.yaml` is absent, scan linked story files (and inline sprint rows) for `DONE | COMPLETE | IN PROGRESS | BLOCKED | NOT STARTED` (unmarked -> `NOT STARTED`; missing file -> `MISSING`), and emit warning: `"⚠ No sprint-status.yaml found — status inferred from markdown. Run ags-plan sprint update to generate one."`
3. **Single-pass stale story check**: Run ONE pattern search across `production/epics/**/story-*.md` for `Last Updated` stamps:
   `\*{0,2}(Last Updated|Updated|last-updated|updated_at)\*{0,2}[[:space:]]*:`
   *(The `\*{0,2}` wrappers match markdown bold headers emitted by `ags-plan stories`.)*
   - No match -> classify as `"never stamped"` (do not compute an age).
   - Inline task -> `"inline task — cannot check staleness"`.
   - `IN PROGRESS` story stamped **> 4 days ago** -> flag **`STALE`** (4-day threshold covers weekends) and list under `### Attention Needed`.
   - **Stale escalation**: Any `STALE` `IN PROGRESS` story forces the burndown verdict to at least **`At Risk`** even when completion `%` looks on track (`"At Risk — [N] story(ies) with no progress in [N] days."`).

---

## Phase 3: Burndown & Fast Escalation Flags

Compare `completion % = (complete / total) * 100` against `time consumed %`:
- **On Track**: within 10 points of time consumed `%` or ahead (unless escalated by `STALE` stories)
- **At Risk**: 10–25 points behind time consumed `%` (or has `STALE` story)
- **Behind**: > 25 points behind time consumed `%`

Place triggered escalation flags at the **TOP** above the status table:
- **Critical Flag**: Any `Must Have` story is `BLOCKED` or `NOT STARTED` with `< 40%` time remaining -> `SPRINT AT RISK: [N] Must Have stories are not complete with [X]% of sprint time remaining. Recommend replanning with ags-plan sprint update.`
- **Completion Flag**: All `Must Have` stories `DONE` -> `All Must Haves complete. Team can pull from Should Have backlog.`
- **Missing Stories Flag**: Any referenced story file absent -> `NOTE: [N] story files referenced in the sprint plan are missing. Run ags-dev readiness sprint to validate story file coverage.`

---

## Phase 4: Concise Output (`< 50` Lines)

Render: Header (`Sprint [N] Status`, Goal, Days Remaining), Progress count & `%`, mandatory story table (`Story / Task | Priority | Status | Owner | Blocker`), conditional `### Attention Needed` (omit if none), `### Burndown`, `### Must-Haves at Risk`, `### Emerging Risks` (omit if none), and single `### Recommendation`.
