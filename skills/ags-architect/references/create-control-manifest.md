# Control Manifest (`ags-architect manifest`)

Extracts a flat, layer-organized, actionable programmer rules sheet (`docs/architecture/control-manifest.md`) from Accepted ADRs, project config, and engine reference docs.

## Phase 1: Load All Inputs (Denominator-First)

### ADRs
1. Establish denominator **N** by listing top-level `docs/architecture/adr-*.md`. If `N == 0`, stop and route to `ags-architect adr`.
2. Scan `^## Status` (+3 lines) across all ADRs BEFORE opening any ADR body, and interpret against **N**:

| Scan Result | Meaning | Action |
|---|---|---|
| `N` matches, some `Accepted` | Valid Accepted set **A** | Proceed with Accepted set **A** only |
| `N` matches, `0` `Accepted` | No Accepted ADRs yet | Warn (`"[N] ADRs found, none Accepted"`). Prompt user to proceed with `Proposed` or stop; never silently emit an empty manifest |
| `0` matches, `N > 0` | **Malformed ADRs** (not an empty Accepted set) | **STOP**: `"[N] ADRs found, none carries ## Status — run ags-architect adr retrofit on each."` Do not emit a manifest |

### Project Config & Engine Reference
- Naming (`naming.*`) and performance budgets (`performance.*`) from preflight (`project.yaml`), plus approved libraries/addons and forbidden patterns from `.ags/rules/` or project technical preferences.
- `docs/engine-reference/<engine>/VERSION.md`, `deprecated-apis.md`, and `current-best-practices.md` (if present).

Report: `"Loaded [|A|] Accepted ADRs (of [N] total), engine: [name + version]."`

## Phase 2: Bounded 4-Section Extraction

For Accepted ADRs **A**, pattern-search ONLY these four headings (never full-read all ADRs; never scan `### Implementation Guidelines` alone):

`^## (Decision|Alternatives Considered|Performance Implications|Engine Compatibility)`

- Filter matches to Accepted set **A**. If a section is absent on one ADR, note it and continue; if absent across ALL of **A**, explicitly warn `"No Accepted ADR contains [section] — manifest [category] rules will be empty."` Escalate to full read of one ADR only when its scanned sections explicitly cross-reference external sections.
- Extract:
  - **Required Patterns** (from `## Decision` body AND any `### Implementation Guidelines` subsection): every `"must"`, `"should"`, `"required to"`, `"always"` mandate.
  - **Forbidden Approaches** (from `## Alternatives Considered`): rejected alternatives (`"never use X because Y"`) and explicit anti-patterns.
  - **Performance Guardrails** (from `## Performance Implications`): frame time, memory, and draw/network budgets.
  - **Engine API Constraints** (from `## Engine Compatibility`): post-cutoff APIs needing verification and version-specific behaviors.
- Classify into `Foundation`, `Core`, `Feature`, and `Presentation` layers (duplicating multi-layer rules into each applicable layer).

## Phase 3: Merge Global Rules

- **Naming Conventions** & **Performance Budgets**: from `project.yaml` (via preflight) / technical preferences.
- **Forbidden APIs (`deprecated-apis.md`)**: **Filter strictly for relevance to this project.** Never copy the deprecation table wholesale across unused dimensions/subsystems (e.g., do not emit 3D-only physics rules into a 2D project). When applicability is uncertain, scope explicitly (`"When using 3D physics: ..."`) or omit and note as unresolved.
- **Engine-Recommended Patterns**: from `current-best-practices.md`.
- **Approved Libraries & Forbidden Patterns**: from project technical preferences / `.ags/rules/`.

## Phase 4: Preview & `TD-MANIFEST` Gate

1. Present rule counts per layer (`Foundation`, `Core`, `Feature`, `Presentation`, `Global`) and confirm completeness (`[A] Proceed to review & write` / `[B] Add rules` / `[C] Remove rules` / `[D] Stop`).
2. **Review mode check**:
   - `solo` -> skip (`TD-MANIFEST skipped — Solo mode.`)
   - `lean` -> skip (`TD-MANIFEST skipped — Lean mode.`)
   - `full` -> spawn `technical-director` pointing to `.ags/gates/td-manifest.md` (pass preview, ADRs covered, engine version, preference/engine-doc rules; parent does not read the gate file).
   - Apply verdict (`APPROVE` -> Phase 5; `CONCERNS` -> prompt `Revise` / `Accept and proceed` / `Discuss`; `REJECT` -> fix and re-preview before writing).

## Phase 5: Write Control Manifest

Confirm write of `docs/architecture/control-manifest.md` (`[A] Write` / `[B] Show full draft first` / `[C] Not yet`). Emit:

```markdown
# Control Manifest

> **Engine**: [name + version]
> **Last Updated**: [YYYY-MM-DD]
> **Manifest Version**: [YYYY-MM-DD — must match Last Updated]
> **ADRs Covered**: [ADR-NNNN, ...]
> **Status**: Active — regenerate with `ags-architect manifest update` when ADRs change
```

Include `Foundation Layer Rules`, `Core Layer Rules`, `Feature Layer Rules`, `Presentation Layer Rules` (each with `Required Patterns`, `Forbidden Approaches`, `Performance Guardrails`), and `Global Rules (All Layers)` (`Naming Conventions`, `Performance Budgets`, `Approved Libraries / Addons`, `Forbidden APIs ([engine version])`, `Cross-Cutting Constraints`). Every rule must cite its source (`ADR-NNNN`, `project.yaml`, or engine doc).

## Phase 6: Next Steps

- New pipeline: recommend `ags-plan epics layer: foundation` -> `ags-plan stories [epic-slug]`.
- Regeneration: warn team of changed rules, especially new Forbidden entries.
