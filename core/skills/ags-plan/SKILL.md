---
name: ags-plan
description: "Use when decomposing GDDs/ADRs or game briefs into epics and stories, estimating task effort, planning or updating sprints, checking sprint status, or running milestone reviews and retrospectives. Do NOT use when authoring architecture/ADRs (-> ags-architect), checking story readiness or coding (-> ags-dev), or running formal phase gates (-> ags-gate)."
---

# Studio Production Planning

Breaks approved design and architecture (or `minimal` game briefs) into layer-ordered epics and implementable stories, produces 3-point effort estimates, manages sprint plans and status snapshots, and executes milestone reviews and retrospectives.

## Contract

- **Inputs**: `project.yaml`, `project.local.yaml`, `design/gdd/*.md` (`systems-index.md`) or `design/game-brief.md` (`minimal`), `docs/architecture/{architecture.md,adr-*.md,control-manifest.md,tr-registry.yaml}`, `docs/engine-reference/<engine>/VERSION.md`, `production/epics/**/EPIC.md`, `production/epics/**/story-*.md`, `production/sprints/sprint-*.md`, `production/sprint-status.yaml`, `production/milestones/*.md`, `production/risk-register/*.md`, `production/qa/qa-plan-*.md`, `production/retrospectives/*.md`, resolved code root (`src/`, `Assets/`, `Source/`)
- **Roles**: `producer` (gates PR-EPIC, PR-SPRINT, PR-MILESTONE), `qa-lead` (read-only gate QL-STORY-READY), `technical-director` (read-only dependency consultation), `creative-director` (milestone scope escalations), `scout` (optional read-only scan)
- **Outputs**: `production/epics/[epic-slug]/EPIC.md`, `production/epics/index.md`, `production/epics/[epic-slug]/story-NNN-[slug].md`, `production/sprints/sprint-[N].md`, `production/sprint-status.yaml`, `production/milestones/[name]-review.md`, `production/retrospectives/retro-*.md`, `production/session-logs/decision-log.md` (`autonomous`), read-only outputs (`estimate`, `status`)
- **Verification**: `python .ags/cli.py preflight ags-plan [target]`, tier-appropriate GDD/ADR/TR checks, `VERSION.md` risk lookup, `PR-EPIC`/`QL-STORY-READY`/`PR-SPRINT`/`PR-MILESTONE` gates per `modes.review_mode`, and stale-story/insufficient-input guards
- **Next Skill**: `ags-dev` (`readiness` / `implement`), `ags-qa` (`plan`), `ags-arch-review` (`scope`), `ags-architect` (missing/Proposed ADRs), `ags-ideate` (`prototype` spike), or `ags-gate`

## Preflight

Run once at startup and hold the resolved configuration for the session:

```bash
python .ags/cli.py preflight ags-plan [target]
```

Capture `review_mode`, `automation`, `workflow`, `docs.density`, `story_granularity`, `qa.level`, `engine.*` (including resolved `code_root`), and `system_overrides`. An inline `--review [full|lean|solo]` overrides `modes.review_mode`. Follow `modes.automation` (`collaborative` prompts always; `guided` major choices & new files; `autonomous` logs to `production/session-logs/decision-log.md` except `automation_always_ask` categories).

## Phases

### Phase 1: Route Mode

Select sub-mode from arguments or user intent (load ONLY the active reference file, plus [CONTRACT.md](CONTRACT.md) for `epics`/`stories`):

| Argument / Trigger | Mode | Reference |
|---|---|---|
| `epics` (`all` \| `layer:<layer>` \| `<system>`) | **Epic Decomposition** | [references/create-epics.md](references/create-epics.md) + [CONTRACT.md](CONTRACT.md) |
| `stories` (`<epic-slug>` \| `<epic-path>` \| `minimal` brief) | **Story Breakdown** | [references/create-stories.md](references/create-stories.md) + [CONTRACT.md](CONTRACT.md) |
| `estimate <task>` | **Task Effort Estimate** (read-only) | [references/estimate.md](references/estimate.md) |
| `sprint` (`new` \| `update` \| `status`) | **Sprint Planning** | [references/sprint-plan.md](references/sprint-plan.md) |
| `status` (`[sprint-N]`) | **Sprint Status Snapshot** (read-only) | [references/sprint-status.md](references/sprint-status.md) |
| `milestone` (`current` \| `<name>`) | **Milestone Review** | [references/milestone-review.md](references/milestone-review.md) |
| `retro` (`sprint-N` \| `<milestone-name>`) | **Retrospective** | [references/retrospective.md](references/retrospective.md) |

### Phase 2: Execute Mode Workflow

1. **Epics (`epics`)**: Follow [references/create-epics.md](references/create-epics.md).
   - At `minimal`, epics are optional (`stories` synthesizes an implicit epic from `design/game-brief.md`); at `standard`/`full`, resolve per-system workflow tiers via GDD stem, run fail-open Summary scan, bounded-read in-scope ADRs (`GDD Requirements Addressed`, `Decision`, `Engine Compatibility`), check TR coverage, pass `PR-EPIC` (`review_mode`), and write `EPIC.md` + `index.md`.
2. **Stories (`stories`)**: Follow [references/create-stories.md](references/create-stories.md).
   - At `minimal`, synthesize implicit `EPIC.md` from `design/game-brief.md` (Option A) and look up `VERSION.md` Risk (`NOT ASSESSED` treated as `HIGH` downstream). At `standard`/`full`, require existing epic(s) (stop on zero epics), bounded-read ADRs (`Summary`, `Decision` + `Implementation Guidelines`, `Engine Compatibility`, `Last Verified` -> `ADR Version` stamp), size by `story_granularity`, classify `Type`, `Handoff Class` (`Player-facing|Technical|Mixed`), and `Verification Method` (always required even when `qa.level: minimal` waives automated test evidence), set `Proposed`-ADR stories `Status: Blocked`, run single `qa-lead` `QL-STORY-READY` spawn (or reuse `production/qa/qa-plan-*.md`), and update `EPIC.md` + `index.md`.
3. **Estimate (`estimate`)**: Follow [references/estimate.md](references/estimate.md). Read-only 3-point (`Optimistic / Expected / Pessimistic`) half-day estimates with confidence and risk drivers.
4. **Sprint Plan (`sprint`)**: Follow [references/sprint-plan.md](references/sprint-plan.md). Hold any unconfigured `review_mode` prompt choice until Phase 1 confirms story backlog exists under `production/epics/**/story-*.md`; handle optional `milestones/` and `risk-register/` gracefully; pass `PR-SPRINT`; write `sprint-[N].md` + `production/sprint-status.yaml` together; enforce Phase 5 QA plan check.
5. **Sprint Status (`status`)**: Follow [references/sprint-status.md](references/sprint-status.md). Read-only `<50`-line snapshot reading `sprint-status.yaml` first, single pattern search `Last Updated` for `>4d` `STALE` escalation (`At Risk`), and top escalation flags.
6. **Milestone Review (`milestone`)**: Follow [references/milestone-review.md](references/milestone-review.md). Skip `-review.md` when selecting `current`, scan sprint reports with exact `sprint-plan` headings, apply `PR-MILESTONE`, emit `GO | CONDITIONAL GO | NO-GO | NOT ASSESSED`.
7. **Retrospective (`retro`)**: Follow [references/retrospective.md](references/retrospective.md). Check existing retrospective (`Update` vs `Start fresh` archive), combine `sprint-status.yaml` + `git log` + code-health trends, confirm save, and offer pre-loaded handoff to `ags-plan sprint new`.

## Gate & Verdict

- **`COMPLETE` / `PASS` / `GO`**: Epics/stories/sprint/review/retrospective written or read-only estimate/status generated with all required inputs present and director gates resolved (`REALISTIC`, `ADEQUATE`, `ON TRACK`).
- **`CONCERNS` / `CONDITIONAL GO`**: Non-blocking producer/QA concerns accepted by user, `Proposed`-ADR stories marked `Blocked`, `AT RISK` burndown (including `>4d` `STALE` stories), or missing optional QA plan warning accepted.
- **`NOT ASSESSED`** *(ranks above `COMPLETE`/`PASS`/`GO` and below `CONCERNS`/`FAIL`/`BLOCKED`/`NO-GO`)*: Required planning inputs absent/empty (`milestone`/`retro` insufficient-input guard), unresolved code root during code-health scan, or missing `VERSION.md` risk rating on story creation (carried into story `Risk:` field rather than guessed). Name missing inputs and producing skill.
- **`BLOCKED` / `FAIL` / `NO-GO`**: Missing required epic/story/ADR inputs for resolved tier, zero stories in `production/epics/` during `sprint`, director `UNREALISTIC`/`INADEQUATE`/`OFF TRACK` unresolved, or user declined write.
