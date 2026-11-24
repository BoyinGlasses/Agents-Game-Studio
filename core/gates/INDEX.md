# Director Gates — Shared Review Pattern

Index of all director and domain-lead review gates. Skills reference gate IDs
from this index instead of embedding prompts inline — eliminating drift when
prompts need updating. Each gate's full definition (Trigger, Context to pass,
Prompt, Verdicts, and Special Handling notes) lives in its own file under
`.ags/gates/`, named after the gate ID in lowercase.

**Scope**: All 7 production stages (Concept → Release), all Tier 1 directors,
and all key domain leads/lenses. Any skill, orchestrator, or workflow may invoke
these gates.

**When a skill dispatches a director role for a gate, it must NOT read the gate
definition file itself. Include the gate definition file path in the dispatch
prompt and instruct the role to read it first, then pass only the context fields
that gate requires. Gate definitions are read by the dispatched role, in its own
context window.**

---

## Gate Index

Role dispatch by prefix (`.ags/roles/`):

| Prefix | Core Studio Agent | Domain / Lens Role | Model Effort |
|--------|-------------------|--------------------|--------------|
| `CD-` | `creative-director` | — | `high` |
| `TD-` | `technical-director` | — | `high` |
| `PR-` | `producer` | — | `medium` |
| `AD-` | `art-ux-director` | `art-director` | `medium` |
| `LP-` | `technical-director` (`LP-FEASIBILITY`) / `code-reviewer` (`LP-CODE-REVIEW`) | `lead-programmer` | `high` |
| `QL-` | `qa-lead` | — | `high` |
| `ND-` | `game-designer` | `narrative-director` | `high` |

Definition files below live in `.ags/gates/`.

| Gate ID | Purpose | Definition file |
|---------|---------|-----------------|
| CD-PILLARS | Pillar stress test after pillars are defined | cd-pillars.md |
| CD-GDD-ALIGN | GDD pillar alignment after a system GDD is authored | cd-gdd-align.md |
| CD-SYSTEMS | Systems decomposition vision check after `ags-gdd` (`map-systems`) | cd-systems.md |
| CD-NARRATIVE | Narrative consistency of story/lore documents | cd-narrative.md |
| CD-PLAYTEST | Player experience validation of playtest reports | cd-playtest.md |
| CD-PHASE-GATE | Creative readiness at phase transition | cd-phase-gate.md |
| TD-SYSTEM-BOUNDARY | System boundary review before GDD authoring | td-system-boundary.md |
| TD-FEASIBILITY | Technical feasibility of early concept risks | td-feasibility.md |
| TD-ARCHITECTURE | Master architecture document sign-off | td-architecture.md |
| TD-ADR | Individual ADR review before Accepted | td-adr.md |
| TD-ENGINE-RISK | Engine version risk for post-cutoff APIs | td-engine-risk.md |
| TD-PHASE-GATE | Technical readiness at phase transition | td-phase-gate.md |
| TD-MANIFEST | Control manifest review before it is written | td-manifest.md |
| TD-CHANGE-IMPACT | Design-change impact assessment review | td-change-impact.md |
| PR-SCOPE | Scope and timeline validation | pr-scope.md |
| PR-SPRINT | Sprint plan feasibility review | pr-sprint.md |
| PR-MILESTONE | Milestone risk assessment | pr-milestone.md |
| PR-EPIC | Epic structure feasibility before story breakdown | pr-epic.md |
| PR-PHASE-GATE | Production readiness at phase transition | pr-phase-gate.md |
| AD-CONCEPT-VISUAL | Visual identity anchor after pillars lock | ad-concept-visual.md |
| AD-ART-BIBLE | Art bible sign-off before asset production | ad-art-bible.md |
| AD-PHASE-GATE | Visual readiness at phase transition | ad-phase-gate.md |
| LP-FEASIBILITY | Implementation feasibility of the architecture | lp-feasibility.md |
| LP-CODE-REVIEW | Code review of an implemented story | lp-code-review.md |
| QL-STORY-READY | Acceptance-criteria testability before sprint | ql-story-ready.md |
| QL-TEST-COVERAGE | Test coverage review before epic done / advance | ql-test-coverage.md |
| ND-CONSISTENCY | Narrative consistency of writer deliverables | nd-consistency.md |
| AD-VISUAL | Visual consistency of art/tech-art decisions | ad-visual.md |

---

## Review Modes

Review intensity controls whether gates run.

**Global config**: `modes.review_mode` in `project.yaml` — one word: `full`,
`lean`, or `solo`. Legacy fallback: `production/review-mode.txt` (single line,
same values); `project.yaml` wins when both are present. Set once during
`ags-start`, or change it any time with `ags-settings` (`modes.review_mode=<value>`).

**Per-run override**: any gate-using skill accepts `--review [full|lean|solo]`,
overriding the global config for that run only.

| Mode | What runs |
|------|-----------|
| `full` | All gates active — every workflow step reviewed |
| `lean` | PHASE-GATEs only (`ags-gate`) — per-skill gates skipped. **Default** |
| `solo` | No director gates anywhere (game jams, prototypes, max speed) |

---

## Invocation Pattern (copy into any skill)

**MANDATORY: apply the review mode before every gate dispatch.**

Run `python .ags/cli.py preflight ags-gate` (or `python .ags/cli.py preflight <skill>`)
and read `review_mode` from the emitted resolved config block. Do **not**
re-derive it manually. The resolution chain (`project.local.yaml` → `project.yaml`
→ `production/review-mode.txt` → `modes.rigor` expansion, `standard` → `lean`)
and defaults are enforced centrally by `.ags/cli.py`.

An inline `--review [mode]` argument, if the skill accepts one, overrides the
resolved value for that run.

Apply the resolved mode:
- `solo` → **skip all gates**. Note: `[GATE-ID] skipped — Solo mode`
- `lean` → **skip unless this is a PHASE-GATE** (`CD-PHASE-GATE`, `TD-PHASE-GATE`, `PR-PHASE-GATE`, `AD-PHASE-GATE`). Note: `[GATE-ID] skipped — Lean mode`
- `full` → dispatch as normal

> **PHASE-GATE panel width is a second, independent axis.** `review_mode` decides
> whether the four PHASE-GATEs run at all; `modes.workflow` decides how many of
> them run — `minimal` → PR only, `standard` → TD + PR, `full` → all four. The
> rule and its rationale live in `ags-gate`, the primary skill that invokes
> PHASE-GATEs. Every other gate in this index is single-director and unaffected.
> Width never softens a verdict: the escalation rule below applies unchanged to
> whoever ran.

```
# Apply mode check, then:
Dispatch `[core-role]` from `.ags/roles/` (attaching `[lens-role].md` if applicable):
- Gate: [GATE-ID] — dispatch prompt instructs the role to read
  `.ags/gates/[gate-id].md` FIRST (parent session must not read it)
- Context: [fields under that gate's **Context to pass**]
- Await the verdict before proceeding.
```

For parallel dispatching (multiple directors at one gate point): apply the mode
check per gate, then dispatch all surviving roles concurrently before waiting
for results; collect all verdicts before proceeding.

---

## Standard Verdict Format

All gates return one of three verdicts. Skills must handle all three:

| Verdict | Meaning | Default action |
|---------|---------|----------------|
| **APPROVE / READY** | No issues. Proceed. | Continue the workflow |
| **CONCERNS [list]** | Issues present but not blocking. | Surface to the user — options: `Revise flagged items` / `Accept and proceed` / `Discuss further` |
| **REJECT / NOT READY [blockers]** | Blocking issues. Do not proceed. | Surface blockers to the user. Do not write files or advance stage until resolved. |

**Escalation rule**: When multiple directors are dispatched in parallel, apply
the strictest verdict — one `NOT READY` overrides all `READY` verdicts.

---

## Recording Gate Outcomes

After a gate resolves, record the verdict in the relevant document's status header:

```markdown
> **[Director] Review ([GATE-ID])**: APPROVED [date] / CONCERNS (accepted) [date] / REVISED [date]
```

For phase gates, record in `docs/architecture/architecture.md` or
`production/session-state/active.md` as appropriate.

---

## Parallel Gate Protocol

At checkpoints needing multiple directors (most common at `ags-gate`):

```
Dispatch in parallel (launch all role dispatches before waiting for results):
creative-director → CD-PHASE-GATE,
technical-director → TD-PHASE-GATE,
producer → PR-PHASE-GATE,
art-ux-director (lens: art-director) → AD-PHASE-GATE

Collect all verdicts (per modes.workflow panel width), then apply escalation rules:
- Any NOT READY / REJECT → overall verdict minimum FAIL
- Any CONCERNS → overall verdict minimum CONCERNS
- All READY / APPROVE → eligible for PASS (still subject to artifact checks)
```

---

## Adding New Gates

1. Assign a gate ID: `[DIRECTOR-PREFIX]-[DESCRIPTIVE-SLUG]`. Prefixes: `CD-`
   `TD-` `PR-` `LP-` `QL-` `ND-` `AD-`; add new ones for new roles
   (`audio-director` → `AU-`, `ux-designer` → `UX-`, paired with their core
   agent in `.ags/roles/`)
2. Create `.ags/gates/[gate-id].md` (lowercase), starting with the standard
   `> Gate definition...` header note, the `Core role` / `Lens role` / `Model effort`
   metadata line, and all five fields: Trigger, Context to pass, Prompt,
   Verdicts, and Special Handling notes
3. Add its row to the Gate Index table above
4. Reference it in `AGENTS.md` and `ags-*` skills by ID only — never copy the
   prompt text inline

---

## Gate Coverage by Stage

| Stage | Required Gates | Optional Gates |
|-------|---------------|----------------|
| **Concept** | CD-PILLARS, AD-CONCEPT-VISUAL | TD-FEASIBILITY, PR-SCOPE |
| **Systems Design** | TD-SYSTEM-BOUNDARY, CD-SYSTEMS, PR-SCOPE, CD-GDD-ALIGN (per GDD) | ND-CONSISTENCY, AD-VISUAL, TD-CHANGE-IMPACT (on GDD revision) |
| **Technical Setup** | TD-ARCHITECTURE, TD-ADR (per ADR), TD-MANIFEST, LP-FEASIBILITY, AD-ART-BIBLE | TD-ENGINE-RISK |
| **Pre-Production** | PR-EPIC, QL-STORY-READY (per story), PR-SPRINT, all four PHASE-GATEs (via `ags-gate`) | CD-PLAYTEST |
| **Production** | LP-CODE-REVIEW (per story), QL-STORY-READY, PR-SPRINT (per sprint), QL-TEST-COVERAGE (per sprint close-out) | PR-MILESTONE, AD-VISUAL, TD-CHANGE-IMPACT (on GDD revision) |
| **Polish** | QL-TEST-COVERAGE, CD-PLAYTEST, PR-MILESTONE | AD-VISUAL |
| **Release** | All four PHASE-GATEs (via `ags-gate`) | QL-TEST-COVERAGE |
