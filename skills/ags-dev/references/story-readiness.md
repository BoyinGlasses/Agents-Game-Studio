# Story Readiness Workflow (`ags-dev` Read-Only Mode)

Validates that a story file contains everything needed for implementation without mid-sprint design interruptions, guessing, or ambiguous acceptance criteria. **Strictly read-only**: never modify files; offer draft corrections in conversation only.

## 1. Verdict Precedence & `NOT ASSESSED`

Evaluate in strict order (first matching rule wins): **BLOCKED** > **NEEDS WORK** > **NOT ASSESSED** > **READY**.

- **BLOCKED**: Real, listable obstacle preventing work (missing or `Draft` dependency story, missing or `Proposed` governing ADR per tier, or unowned `UNRESOLVED` design question marker).
- **NEEDS WORK**: Story can be fixed by the author before assignment (failing testable criteria, invalid `Handoff Class:` or vague `Verification Method:`, stale `Manifest Version:`, missing referenced asset, or below-minimum criterion count).
- **NOT ASSESSED**: Story could not be evaluated at all — empty scope (`NOT ASSESSED — no stories in scope`), unreadable/unparseable story file, or unreadable ADR `## Status`. Distinct from `BLOCKED`; `READY` is unreachable without evaluation.
- **READY**: All applicable checklist items pass, are explicitly N/A with reason, or are advisory-only (`testing.strict.<type>: false`).

## 2. Scope Resolution

- **Specific path**: Validate that single story file.
- **`sprint`**: Read the most recent sprint file in `production/sprints/` and extract every referenced story path.
- **`all`**: Scan `production/epics/**/*.md` excluding `EPIC.md` index files.
- **No argument**: Prompt the user for scope (`specific story`, `current sprint`, `all stories in production/epics/`, or `specific epic`).

Report `"Validating [N] story files."` before checking.

**Zero-scope guard**:
- If the scope resolves to zero story files, STOP immediately and report `NOT ASSESSED — no stories in scope`.
- Name the exact searched path/glob and route: `ags-plan` (create epics -> create stories).
- Distinguish `"no sprint file found in production/sprints/"` (missing plan) from `"sprint plan lists zero stories"` (empty list). Never render `Ready: 0 / Needs Work: 0 / Blocked: 0` over an empty set.

## 3. Single-Pass Supporting Context Load

Load shared references once before evaluating stories (never re-scan per story):
1. `design/gdd/systems-index.md` — check approved GDDs.
2. `docs/architecture/control-manifest.md` — extract only the header `Manifest Version:` date (do not read full rule bodies). Note once if missing.
3. `docs/architecture/tr-registry.yaml` — index entries by `id`. Note once if missing (TR-ID checks auto-pass if registry predates stories).
4. **ADR statuses in one scan**: Count `docs/architecture/adr-*.md` (`N`) first, then scan `^## Status` lines across all ADRs. If `N > 0` and 0 status matches appear, report malformed ADRs (`ags-architect` retrofit) rather than failing every story's ADR check. Cache the map.
5. Current sprint file (if `sprint` scope) — extract `Must Have` / `Should Have` priority tiers for sprint escalation.

Resolve `workflow` **per story** using the GDD filename stem of its `GDD:` path (`TR-[system]-NNN` `[system]` is fallback alias only) against `workflow_overrides.system_overrides.<stem>`, else project `workflow`, else `modes.rigor`.

## 4. Story Readiness Checklist

Apply workflow tier adjustment (`full` baseline; `standard` keeps Design Completeness + Scope Clarity blocking, only missing/`Proposed` critical Foundation ADRs block in Architecture Completeness, non-critical ADR/TR/manifest become advisory; `minimal` runs Design Completeness + Scope Clarity + Handoff/Type checks only and marks Architecture Completeness N/A).

### Design Completeness
- [ ] **GDD requirement referenced**: Story cites a `design/gdd/` path and quotes/links a specific requirement or rule (filename alone fails).
- [ ] **Requirement is self-contained**: Acceptance criteria specify DONE without needing to open the GDD.
- [ ] **Acceptance criteria are testable**: Specific observable conditions (not "implement X" or "works correctly").
- [ ] **No judgment-call criteria** *(auto-pass for `Type: Visual/Feel`)*: Logic/Integration/UI/Config criteria must use measurable benchmarks; for `Visual/Feel`, verify each subjective criterion pairs with an explicit evidence doc path (`production/qa/evidence/[slug]-evidence.md`).

### Architecture Completeness *(tier-adjusted)*
- [ ] **ADR referenced or N/A stated**: References >=1 ADR or states `"No ADR applies"` with reason.
- [ ] **ADR is Accepted**: Cached `## Status` must be `Accepted`. `Proposed` or missing ADR file -> **BLOCKED**; unreadable status -> **NOT ASSESSED**.
- [ ] **TR-ID is valid and active**: Registered and `status: active` (`deprecated`/`superseded` or unregistered -> NEEDS WORK; auto-pass if no TR-ID or no registry).
- [ ] **Manifest version is current**: Matches header `Manifest Version:` date (`control-manifest.md` absent -> auto-pass).
- [ ] **Engine notes present**: Post-cutoff engine APIs have notes/verification requirements (or `"N/A — no engine API involved"`).
- [ ] **Control manifest rules noted**: Relevant layer rules noted (or `"N/A — manifest not yet created"`).

### Scope Clarity
- [ ] **Estimate present**: Hours, points, or t-shirt size.
- [ ] **In-scope / Out-of-scope boundary stated**: Explicit `## Out of Scope` section or unambiguous boundary.
- [ ] **Story dependencies listed**: Story IDs listed, or `"None"` stated explicitly.

### Open Questions & Dependencies
- [ ] **No unresolved design markers**: No `UNRESOLVED`, `TBD`, `TODO`, or `?` in criteria, notes, or rules (unowned critical question -> **BLOCKED**).
- [ ] **Dependency stories not DRAFT**: Any listed dependency that is missing or `Status: Draft` -> **BLOCKED**.

### Asset References Check
- [ ] **Referenced assets exist**: Extract paths containing `assets/` or `.png`, `.jpg`, `.svg`, `.wav`, `.ogg`, `.mp3`, `.glb`, `.gltf`, `.tres`, `.tscn`, `.res` and verify existence (normalize separators across Windows/POSIX). Missing -> **NEEDS WORK**; none referenced -> note skip and auto-pass.

### Definition of Done
- [ ] **Minimum testable acceptance criteria**: `Logic`/`Integration` >= 3; `Visual/Feel`/`UI` >= 2; `Config/Data` >= 1.
- [ ] **Performance budget noted**: Budget or `"no performance impact expected — [reason]"` if touching gameplay loop/rendering/physics.
- [ ] **Story Type declared**: `Type: [Logic|Integration|Visual/Feel|UI|Config/Data]`.
- [ ] **Handoff class and verification method**:
  - `Handoff Class:` must be `Player-facing`, `Technical`, or `Mixed`. Never infer `Technical` solely from `Type: Logic`.
  - `Verification Method:` must name a concrete build/test command (configured command when `project.yaml` provides one) or manual check, an expected evidence path, and playable setup/steps for `Player-facing`/`Mixed`.
  - Present-but-invalid class or vague method ("test it") -> **NEEDS WORK**.
  - Missing on a legacy story -> emit `ADVISORY: classify at the dev-story approval checkpoint` without downgrading an otherwise `READY` story.
- [ ] **Test evidence requirement clear** *(auto-pass at `qa.level: minimal`)*: `## Test Evidence` states concrete path. Resolve gate level from `preflight` resolved `testing.strict.<key>` (`logic`, `integration`, `visual`, `ui`, `config`; valid values `true`/`false` case-insensitive; invalid value -> treat unset and surface warning; fallback plain boolean `testing.strict`; default strict for Logic/Integration/Visual/Feel/UI and advisory for Config/Data). Strict missing -> **NEEDS WORK**; advisory missing -> list gap without blocking `READY`.

## 5. Output, Sprint Escalation & Gate

- **Single-story report**: Title, File, Verdict, Passing Checks (`N/total`), Gaps (with exact Fix text), Blockers.
- **Multi-story summary**: `Ready`, `Needs Work`, `Blocked`, `NOT ASSESSED` counts + per-story details for non-ready stories.
- **Sprint escalation**: If `sprint` scope has any `Must Have` story that is `NEEDS WORK`, `BLOCKED`, or `NOT ASSESSED`, prepend a prominent `WARNING` routing to `ags-plan` (`sprint-plan update`).
- **Director gate (`QL-STORY-READY`)**:
  - `solo` -> skip (`QL-STORY-READY skipped — Solo mode`).
  - `lean` -> skip (`QL-STORY-READY skipped — Lean mode`).
  - `full` -> spawn `qa-lead` pointing to `.ags/gates/ql-story-ready.md` (do not read gate file in parent session); pass story title, acceptance criteria list, dependency status, and verdict. On `GAPS`/`INADEQUATE`, present options (`Update story`, `Accept and proceed`, `Discuss further`) per `modes.automation`.
- **Single-story next-story handoff**: Scan current sprint for up to 3 other `READY`/`NOT STARTED`, unblocked `Must Have`/`Should Have` stories. If none or no sprint file exists, explicitly state `"Next ready stories: no sprint file found"` or `"Next ready stories: none ready in [sprint]"`.
- **Redirect rules**: Missing story -> `ags-plan`; small unmapped change (<4h) -> `ags-gdd` quick-design mode; oversized story -> split via `ags-plan`.
