---
name: ags-start
description: "Use when onboarding a fresh game project, checking current development stage, asking what to do next, or generating a contributor onboarding guide. Do NOT use when auditing brownfield format compliance or reverse-documenting code -> ags-adopt."
---

# Studio Start & Orientation

Entry point for project onboarding (`start`), quick next-step orientation (`help`), full project stage detection (`stage`), and contributor onboarding (`contributor`).

## Contract

- **Inputs**: `project.yaml`, `project.local.yaml`, `.ags/workflow-catalog.yaml`, `.ags/templates/project-stage-report.md`, `production/session-state/active.md`, `production/sprint-status.yaml`, role definitions under `.ags/roles/`, and project trees (`design/`, `docs/`, resolved code root, `prototypes/`, `tests/`).
- **Roles**: Direct orchestrator execution; reads `scout`, `creative-director`, `technical-director`, `qa-lead`, `code-reviewer`, `producer`, `game-designer`, `art-ux-director`, `prototyper`, `gameplay-coder`, `tech-artist`, or `test-engineer` role files during contributor onboarding.
- **Outputs**: `project.yaml` (`project.stage`, `modes.rigor`, `modes.automation`) + `production/stage.txt` (`start`, never writes `modes.review_mode` or `production/review-mode.txt`); read-only status (`help`); `production/project-stage-report.md` (`stage`); `production/onboarding/onboard-[role]-[date].md` (`contributor`).
- **Verification**: Run `python .ags/cli.py preflight ags-start` and `python .ags/cli.py check artifacts` (`--phase <phase>` for `help`, full catalog for `stage`); resolve code root (`src/`, `Assets/`, `Source/`) before claiming source counts.
- **Next Skill**: `ags-settings`, `ags-ideate`, `ags-adopt`, `ags-plan`, or `ags-gate`

## Preflight

Run:

```bash
python .ags/cli.py preflight ags-start
```

Capture `project.stage`, `modes.rigor`, `modes.workflow`, `modes.automation`, `modes.review_mode`, `engine.name`, and resolved code root. If `project.yaml` is absent on a fresh template, proceed in `start` mode interactively (`collaborative`).

For `help` and `stage` modes, also run deterministic artifact evaluation:

```bash
python .ags/cli.py check artifacts [--phase <current-phase>]
```

## Phases

### Phase 1: Route Sub-Mode

Load ONLY the reference file for the active mode:

| Trigger / Argument | Mode | Workflow Reference |
|---|---|---|
| Fresh project, unconfigured setup, or `start` | **Guided Onboarding** | [references/onboard-flow.md](references/onboard-flow.md) |
| `"what next?"`, stuck, or `help` | **Quick Next-Step Help** (read-only) | [references/help-flow.md](references/help-flow.md) |
| `"where are we?"`, gap scan, or `stage [role]` | **Project Stage Detection** | [references/stage-detect.md](references/stage-detect.md) |
| New contributor/agent, or `contributor <role>` | **Contributor Onboarding Doc** | [references/contributor-onboard.md](references/contributor-onboard.md) |

### Phase 2: Execute Active Mode

- **Guided Onboarding (`start`)**: Silently inspect engine, concept/brief, resolved code root, prototypes, design docs, and production artifacts. Prompt starting state (`A` No idea / `B` Vague idea / `C` Clear concept / `D` Existing work). Write `project.stage` + `production/stage.txt` (omit `modes.review_mode` and `modes.rigor` from initial template). Prompt `modes.rigor` seeded from concept signals, then `modes.automation`. Present the tier-matched path (`minimal` 4-step floor vs `standard` vs `full`) and hand off to one next skill without auto-running.
- **Quick Help (`help`)**: Read `.ags/workflow-catalog.yaml`, run `check artifacts --phase <phase>`, inspect latest `## (Session Extract|STATUS)` block in `production/session-state/active.md` (and `production/sprint-status.yaml` in `production`), list up to 10 uncataloged skills from `.agents/skills/*/SKILL.md`, and surface one required blocker plus tier-appropriate optional steps.
- **Stage Detection (`stage`)**: Run full `check artifacts` plus qualitative scans across resolved code root, `design/`, `docs/`, `production/`, `prototypes/`, and `tests/`. Always run stage heuristics even when `project.stage` is configured and report any disagreement. Ask clarifying questions only for gaps required by `modes.workflow`, then confirm and write `production/project-stage-report.md`.
- **Contributor Onboarding (`contributor`)**: Verify input availability (`FOUND` / `ABSENT`), read `AGENTS.md`, target `.ags/roles/` file, area artifacts, and recent git log, then confirm and write `production/onboarding/onboard-[role]-[date].md`.

### Phase 3: Mode & Recovery Discipline

- Respect `modes.automation` (`collaborative` asks always; `guided` major-only; `autonomous` logs to `production/session-logs/decision-log.md` and proceeds except `automation_always_ask`). Core onboarding choices (starting point, rigor, automation) always prompt on fresh projects.
- Never auto-run the recommended next skill after handoff; output the exact `ags-*` skill name.

## Gate & Verdict

- **`COMPLETE`**: Requested onboarding, orientation, stage report, or contributor guide finished cleanly with explicit artifact and config state.
- **`NOT ASSESSED`** *(ranks above `COMPLETE` and below `BLOCKED` / `CONCERNS` / `FAIL`)*: Required inputs are missing (`contributor` mode with empty project), code root is unresolved when reporting code counts, or `check artifacts` reports `NO_CHECK` / `UNKNOWN` for target scope. Name missing inputs and producing skills.
- **`CONCERNS`**: Configured `project.stage` disagrees with observed artifacts (`stage`), or chosen `modes.rigor` contradicts the stated project scope (`start`).
- **`BLOCKED`**: User declined a requested report write (`stage` / `contributor`) or critical prerequisite input is missing with no fallback.
