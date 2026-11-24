# Quick Next-Step Help (`ags-start help`)

Read-only lightweight orientation telling the user where they are in the pipeline and what single action comes next. Writes no files. For a full gap analysis, route to `ags-start stage`.

## Step 1: Collect State Deterministically

Run both commands:

```bash
python .ags/cli.py preflight ags-start
python .ags/cli.py check artifacts --phase <current-phase>
```

Also inspect:
- `.ags/workflow-catalog.yaml` — authoritative phases, required vs optional steps, and artifact checks.
- `production/session-state/active.md` — search for the **last** `^## (Session Extract|STATUS)` block and read from there to EOF for active task/epic/open questions.
- `.agents/skills/*/SKILL.md` — read `name:` and `description:` from frontmatter and find any skills absent from `.ags/workflow-catalog.yaml` (limit footer list to the 10 most relevant for the current phase).

## Step 2: Determine Current Phase & Tier

1. Use `project.stage` from preflight (`Concept`->`concept`, `Systems Design`->`systems-design`, `Technical Setup`->`technical-setup`, `Pre-Production`->`pre-production`, `Production`->`production`, `Polish`->`polish`, `Release`->`release`).
2. If unset, infer from artifacts (most advanced wins):
   - Resolved code root has 10+ source files -> `production` (note `NOT ASSESSED` if code root unresolved)
   - `production/epics/**/story-*.md` exists -> `pre-production`
   - `docs/architecture/adr-*.md` exists -> `technical-setup`
   - `design/gdd/systems-index.md` exists -> `systems-design`
   - `design/gdd/game-concept.md` or `design/game-brief.md` exists -> `concept`
   - Otherwise -> `concept`
3. Use `modes.workflow` from preflight to filter optional items.

## Step 3: Interpret Step Completion

Map `check artifacts` statuses without re-deriving them manually:

| Status | Report as |
|---|---|
| `PRESENT` | **Complete** |
| `ABSENT` | **Incomplete** |
| `SHORT` | **Incomplete** — include `count=` vs `min=` |
| `PATTERN_MISS` | **Incomplete** — file exists, lacks marker (do not claim missing) |
| `NO_CHECK` | **MANUAL** if `note=` present, else **UNKNOWN** (`NO_CHECK` never means done!) |

**Special cases**:
- **`production` phase**: Read `production/sprint-status.yaml` first if present (`in-progress` = currently active, `ready-for-dev` = next up, `done` = complete, `blocked` = blocker). Skip artifact checks for story execution steps.
- **`repeatable: true` outside production**: Note detected progress and state that work may still be ongoing.

## Step 4: Identify One Primary Next Step

1. **Last confirmed complete step** (`✓`).
2. **First incomplete required step** (`→` — ONE primary blocker).
3. **Optional opportunities (`~`) filtered by `modes.workflow`**:
   - `full`: list all incomplete optional steps.
   - `standard`: list only optional docs required for the active system/phase.
   - `minimal`: omit optional docs once `design/game-brief.md` + engine exist (next stop is code).
4. **Coming up after that**: remaining required steps.

If the user passed context (e.g. "just finished design review"), advance past that step even if the artifact check is ambiguous.

## Step 5: Present Concise Output

Keep it short and direct:

```markdown
## Where You Are: [Phase Label]

**In progress:** [from active.md, if any]

### ✓ Done
- [completed step name]

### → Next up (REQUIRED)
**[Step name]** — [description]
Skill: `ags-...`

### ~ Also available (OPTIONAL)
- **[Step name]** — [description] -> `ags-...`

### Coming up after that
- [Next required step] (`ags-...`)

### Also installed (not in catalog)   [omit if none]
- `ags-...` — [short description]
```

Rules:
- Ask about `MANUAL` steps rather than assuming complete or incomplete.
- If all (or nearly all) required steps in the current phase are complete, add: `Approaching [Current] -> [Next] gate — run ags-gate when ready.`
- If user sounds stuck/overwhelmed, add escalation paths (`ags-start stage`, `ags-gate`, `ags-start`, and `ags-settings` ONLY when a rigor-change trigger applies — user overwhelmed above `minimal`, or project grew past `minimal` into ~9+ GDDs / Production).
- Never auto-run the recommended skill. Match the user's tone and leave them with ONE primary next action.
