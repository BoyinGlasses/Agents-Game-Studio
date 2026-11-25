# Guided Onboarding Flow (`ags-start`)

Entry workflow for new projects or unconfigured repositories. Configures `project.yaml` (`project.stage`, `modes.rigor`, `modes.automation`) and `production/stage.txt`, then routes to the next skill.

> **Never write `modes.review_mode` or `production/review-mode.txt` during onboarding.** `modes.rigor` supplies review depth via expansion; writing an explicit `modes.review_mode` shadows the rigor expansion permanently. Likewise, omit `modes.rigor` from the initial template so Phase 3d always prompts unless already configured.

## Phase 1: Silent Context Detection

Gather context before asking anything (do not display raw scan output unprompted):

- **Engine configured?** Read `engine.name` from `project.yaml`; if absent or empty, fall back to legacy technical preferences (if present, `[TO BE CONFIGURED]` means unset).
- **Game concept exists?** Check `design/gdd/game-concept.md` (or `design/game-brief.md` at `minimal`).
- **Source code exists?** Resolve code root from `engine.name` (`src/` Godot, `Assets/` Unity, `Source/` Unreal; if unambiguous single directory exists, use it; otherwise **unresolved**). Count source files (`*.gd`, `*.cs`, `*.cpp`, `*.h`, `*.rs`, `*.py`, `*.js`, `*.ts`) under the resolved root only. If code root is unresolved, note that source status could not be checked rather than assuming zero code.
- **Prototypes / Design / Production**: Check subdirectories in `prototypes/`, markdown files in `design/gdd/`, and files in `production/sprints/` or `production/milestones/`.

**Returning user fast path**: If engine is configured AND a concept (`design/gdd/game-concept.md` or `design/game-brief.md`) exists, skip onboarding and report configured engine, concept path, and effective `modes.review_mode` (explicit or derived from `modes.rigor`: `minimal`->`solo`, `standard`->`lean`, `full`->`full`), suggesting `ags-plan` or asking what they want to work on.

## Phase 2: Ask Starting Point

Prompt the user with these exact choices:

- **Prompt**: "Welcome to Agents Game Studio! Before I suggest anything, where are you starting from with your game idea?"
- **Options**:
  - `A) No idea yet` — No concept yet; want to explore what to make.
  - `B) Vague idea` — Rough theme, feeling, or genre, nothing concrete.
  - `C) Clear concept` — Know genre and core loop, not formalized into docs yet.
  - `D) Existing work` — Already have design docs, prototypes, code, or planning.

Wait for response.

## Phase 3: Route Based on Answer

- **If A (No idea yet)**: Reassure them; explain `ags-ideate` neutrally without assuming process tier (at `minimal` it writes a one-page `design/game-brief.md`; at `standard`/`full` it runs full MDA/pillar ideation). Name `ags-ideate brainstorm open` as the immediate step and hold the full pipeline until Phase 3d sets rigor.
- **If B (Vague idea)**: Ask for their short hint, validate it, and name `ags-ideate brainstorm <hint>` as the immediate step; hold the full pipeline until Phase 3d.
- **If C (Clear concept)**: Ask for a one-sentence description (plain text), acknowledge it, then prompt:
  - `Formalize it first` -> `ags-ideate brainstorm <concept>`
  - `Jump straight in` -> `ags-settings engine` now and author design docs afterward.
  Name their selected immediate next step only; hold the full pipeline until Phase 3d.
- **If D (Existing work)**: Share Phase 1 findings (`[X] source files / [Y] design docs / [Z] prototypes`, engine status).
  - **D1 (Early stage — engine unset or only concept)**: Recommend `ags-settings engine`, then `ags-start stage`.
  - **D2 (GDDs, ADRs, or stories exist)**: Explain that file existence does not guarantee format compatibility and present the retrofit path:
    1. `ags-start stage` — phase detection + existence gaps
    2. `ags-adopt` — format compliance audit + migration plan
    3. `ags-settings engine` — if engine unconfigured
    4. `ags-gdd retrofit <path>` — fill missing GDD sections
    5. `ags-architect retrofit <path>` — add missing ADR sections
    6. `ags-arch-review` — bootstrap TR registry
    7. `ags-gate` — validate readiness for next phase

**Edge-case checks**: If user picks D on an empty project, suggest A or B. If user picks A when code exists under resolved code root, confirm whether they meant D.

## Phase 3c: Write Initial Stage Anchor

Write the initial stage to BOTH `project.yaml` and `production/stage.txt` (no trailing newline in `stage.txt`, creating `production/` if needed):

- **Paths A, B, C, or D (early)**: `Concept`
- **Path D with GDDs, no architecture docs**: `Systems Design`
- **Path D with architecture docs/ADRs**: `Technical Setup`

If `project.yaml` exists, update/add `project.stage` cleanly after `framework:`. If absent, create it using `.ags/templates/` or minimal structure:

```yaml
schema_version: 1

framework:
  version: "2.0.0"
  last_upgraded: "<YYYY-MM-DD>"

project:
  stage: <value>
```

Confirm: "Set `project.stage` to `<stage>` (and updated `production/stage.txt`)."

## Phase 3d: Set Rigor

If `modes.rigor` is already set in `project.yaml`, display it (`Rigor is set to <current>.`) and advance to Phase 3e.

Otherwise, seed the recommendation from Phase 2 signals:
- Concepts mentioning `open-world`, `RPG`, `sim`, `sandbox`, `faction`, `crafting`, `economy`, `MMO`, `multiplayer`, or many `"systems"` -> recommend `full`.
- Concepts mentioning `jam`, `weekend`, `prototype`, `"first game"`, `small`, `"just trying"`, `experiment`, OR no concept signal at all -> recommend `minimal` (note it can be raised anytime via `ags-settings`).
- Concepts mentioning `"release"`, `"commercial"`, `"on Steam"`, a single clear core loop, or neutral signals -> recommend `standard`.
- A Path B hint that contains scope signals seeds from the signal, not from the path.

Put the recommended option **first** with ` (Recommended)` appended:
- `Jam / prototype / first game` -> `minimal` (short brief, coarse stories, optional evidence, ~4 steps to first code; trade: no GDDs before code)
- `Several systems that affect each other` -> `standard` (balanced docs, standard QA evidence, ~8 design docs before first code)
- `Big systems-heavy or team project` -> `full` (thorough docs, fine stories, required evidence and director gates)

Write `modes.rigor` to `project.yaml` immediately (no legacy mirror). Explain that rigor drives 6 settings (`modes.workflow`, `docs.density`, `qa.level`, `modes.story_granularity`, `modes.review_mode`, `team.size`) inspectable or individually overridable via `ags-settings`.

## Phase 3e: Set Automation Mode

If `modes.automation` is already set in `project.yaml`, display it and proceed to Phase 4. Otherwise prompt:
- `Collaborative` -> `collaborative` (asks before significant steps and drafts)
- `Guided (Recommended)` -> `guided` (minor choices inline, major/always-ask prompt)
- `Autonomous` -> `autonomous` (logs minor/design calls to decision log; still stops for `modes.automation_always_ask`)

Write `modes.automation` to `project.yaml` immediately.

## Phase 4: Show Tier Path & Confirm

Present ONE pipeline matching the chosen/resolved `modes.rigor` (Paths A/B/C only; fallback `standard` if unset):

Remind first: any skill runs at any tier (`modes.rigor` controls what is *required*, not what is *allowed*; raise one system alone via `workflow_overrides.system_overrides.<system>`).

- **`minimal` (4 steps to running code)**:
  1. `ags-settings engine` — configure engine
  2. `ags-ideate` — one-page `design/game-brief.md`
  3. `ags-plan` — stories directly from the brief's MVP list (build order is the plan)
  4. `ags-dev` — first line of game code
- **`standard` (full pipeline)**:
  - Concept: `ags-settings engine` -> `ags-ideate` (brainstorm/prototype) -> `ags-art-ux` (art bible) -> `ags-gdd` (map systems + system GDDs) -> `ags-design-review` (cross-GDD) -> `ags-gate`
  - Architecture: `ags-architect` (architecture + ADRs + control manifest) -> `ags-arch-review`
  - Pre-Production: `ags-art-ux` (UX specs) -> `ags-plan` (epics -> stories -> sprint plan)
  - Production: `ags-dev`
- **`full`**: All `standard` steps plus `ags-ideate vertical-slice`, `ags-qa playtest` (`×1+`) in Pre-Production, and `ags-design-review` after each GDD.

If the user's chosen `modes.rigor` contradicts their Phase 2 concept description (e.g., `minimal` for a multi-year commercial RPG or `full` for a weekend jam), flag the mismatch once in one sentence and offer `ags-settings` — do not re-ask.

Prompt to confirm starting `[recommended first step]` vs doing something else first. Never auto-run the next skill.

## Phase 5: Hand Off

When confirmed, output one short line: `Run <chosen ags-* skill> to begin.` Verdict: **COMPLETE**.
