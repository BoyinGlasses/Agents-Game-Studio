# Team Playbook: Live-Ops (`ags-team live-ops`)

Orchestrates season/event scoping, narrative framing, live economy design, analytics, content writing, player communications, and ethics review.

## Argument & Role Mapping

- **Argument check**: Requires `[season name or event description]`. If omitted, output usage (`ags-team live-ops <season name or event description>`) and stop immediately.
- **Active-set (`team.size`)**:
  - **`individual`** (default): `live-ops-designer` (via `producer`) + `economy-designer` (via `game-designer`). Other roles routed through these two.
  - **`small`**: + `analytics-engineer` + `community-manager`.
  - **`studio`**: + `writer` + `narrative-director` + per-season reviews.
- **Role map**:
  - `live-ops-designer` lens -> `producer` (`.ags/roles/live-ops-designer.md`)
  - `economy-designer` lens -> `game-designer` (`.ags/roles/economy-designer.md`, template `.ags/templates/economy-model.md`)
  - `narrative-director` lens -> `game-designer` (`.ags/roles/narrative-director.md`)
  - `writer` lens -> `game-designer` (`.ags/roles/writer.md`)
  - `analytics-engineer` lens -> `gameplay-coder` (`.ags/roles/analytics-engineer.md`)
  - `community-manager` lens -> `producer` (`.ags/roles/community-manager.md`)

Announce the active roster and unspawned roles before Phase 1.

## Pipeline

### Phase 1: Season/Event Scoping (`live-ops-designer`)

Define season/event type (seasonal, limited-time event, challenge), duration, theme direction, content list (new modes, items, challenges, story beats), daily/weekly retention hook, and new vs reused resource budget. Output: season brief (`production/live-ops/S[N]_[name]-brief.md`).

### Phase 2: Narrative Theme (`narrative-director`)

Read Phase 1 season brief; define how the event connects to the world, the central story hook players discover, and existing lore threads to advance. Output: narrative framing (`production/live-ops/S[N]_[name]-narrative.md`).

### Phase 3: Economy Design (`economy-designer`, parallel with Phase 2 if theme is clear)

Read season brief and `design/live-ops/economy-rules.md`; design free/premium progression tracks, seasonal currency, store rotation, pricing, pity timers / bad-luck protection, and verify zero pay-to-win items in the premium track. Output: economy design (`production/live-ops/S[N]_[name]-economy.md`).

### Phase 4: Analytics and Success Metrics (`analytics-engineer`, parallel with Phase 3)

Define participation rate target, retention lift target, battle-pass completion rate, A/B test plans (e.g., reward cadences), and new telemetry instrumentation specs. Output: analytics working plan (`production/live-ops/S[N]_[name]-analytics-draft.md`).

### Phase 5: Content Writing (Parallel)

- **`narrative-director`** (if needed): In-game cutscene scripts, NPC dialogue, world event text.
- **`writer`**: Player-facing event names, reward descriptions, challenge objective copy, seasonal flavor text (using Phase 2 framing).

### Phase 6: Player Communication Plan (`community-manager`)

Read season brief, economy design, and narrative framing; draft launch announcement (tone, highlights, platform variants), comms cadence (pre-launch teaser, launch post, mid-season reminder, final-week push), and day-1 patch notes known-issues placeholder.

### Phase 7: Review, Ethics Gate & Sign-Off

Present consolidated season summary:
- Content scope
- Economy health check (fair and non-predatory)
- Analytics readiness
- **Ethics review** against `design/live-ops/ethics-policy.md`:
  - **If `design/live-ops/ethics-policy.md` is absent**: Record `ETHICS REVIEW SKIPPED: design/live-ops/ethics-policy.md not found. Economy design was not reviewed against an ethics policy. Recommend creating one before production begins.` Include this notice in the output document and add creating the policy to Next Steps. Verdict must reflect `NOT ASSESSED` for ethics compliance (never clean `COMPLETE` without surfacing the skip).
  - **If `design/live-ops/ethics-policy.md` exists and a violation is found**: Emit `ETHICS FLAG: [element] in Phase 3 economy design violates [policy rule]. Approval is blocked until resolved.` Do NOT issue `COMPLETE` or write `design/live-ops/` files. Prompt the user to: revise economy design (re-run Phase 3 and return to Phase 7) / override with documented rationale / cancel (`BLOCKED — unresolved ethics violation`).
- Open questions needing decisions before production.

### Output Documents

Working role artifacts stay under `production/live-ops/`. Because `design/` requires explicit user approval before writing, compile the final documents and obtain user confirmation before writing:
- `design/live-ops/seasons/S[N]_[name].md` (season design, Phases 1-3)
- `design/live-ops/seasons/S[N]_[name]_analytics.md` (analytics plan, Phase 4)
- `design/live-ops/seasons/S[N]_[name]_comms.md` (comms calendar, Phase 6)

## Verdicts & Next Steps

- **COMPLETE**: User approved season plan, zero unresolved ethics violations, and `ethics-policy.md` passed.
- **NOT ASSESSED**: Ethics policy file absent (`ETHICS REVIEW SKIPPED`) — surfaced explicitly in the season doc and summary.
- **BLOCKED**: Unresolved ethics violation, missing prerequisite, or worker error.
- **Next Skills**: `ags-design-review` on season docs, `ags-plan sprint-plan` to schedule content production, `ags-team release` when seasonal content deploys.
