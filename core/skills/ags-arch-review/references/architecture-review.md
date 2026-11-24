# Architecture Review Workflow (`ags-arch-review review`)

Validates that architectural decisions cover all technical requirements from GDDs, remain conflict-free and acyclic, and accurately target the pinned engine version.

## Argument Modes & `workflow` Scope

- **Modes**: `full` (default, all phases), `coverage` (TR traceability only), `consistency` (cross-ADR conflicts + cycles only), `engine` (engine compatibility audit only), `single-gdd <path>` (coverage for one GDD), `rtm` (extended GDD -> ADR -> Story -> Test matrix to `docs/architecture/requirements-traceability.md`).
- **`workflow` tier**: `full` (full matrix across all GDDs/ADRs), `standard` (architecture doc + critical Foundation ADRs), `minimal` (advisory if run; no architecture required).

---

## Phase 1: Freshness Check & Targeted Loads

### Phase 1a — Receipt Freshness & L0 Summary Scan
1. Locate newest `docs/architecture/architecture-review-*.md` and run:
   ```bash
   python .ags/cli.py check receipts [latest-report] docs/architecture/adr-*.md design/gdd/*.md
   ```
   - **Any `UNRESOLVED`** (check FIRST — disqualifies skipping): One pattern matched no files. Name the unresolved pattern and stop; never treat `UNCHANGED` lines as full coverage while `UNRESOLVED` exists.
   - **All `UNCHANGED`** (zero `UNRESOLVED`): Surface prior report date/verdict and prompt `[A] Stand on prior report (Recommended)` / `[B] Re-run anyway` (`guided` selects `[A]`; `autonomous` logs and selects `[A]`).
   - **Any `CHANGED` / `NEW`**: Name changed files; recommend `ags-arch-review review single-gdd <path>` for narrow edits or full review for new/deleted ADRs.
   - **`RECEIPT: NONE`**: Proceed with full review and emit fresh hashes in Phase 7.
2. **L0 Summary scan (fail open)**: Count GDDs `N` under `design/gdd/*.md`. Pattern-search `## Summary` across `design/gdd/*.md` (+4 lines) and `docs/architecture/adr-*.md` (+3 lines). Missing `## Summary` never removes a GDD from scope — full-read unmatched GDDs when scoping.
   - `single-gdd <path>`: match target GDD summary/system name to relevant ADRs only; skip unrelated GDDs.
   - `engine`: load ADR `## Engine Compatibility` sections only.

### Phase 1b — L1/L2 Targeted Section Load (Denominator-First)
Establish denominators **`N_gdd`** (`design/gdd/*.md`) and **`N_adr`** (`docs/architecture/adr-*.md`) first, and report both.

1. **Design docs**: Read `design/gdd/systems-index.md` whole. Pattern-search GDDs for `^## (Detailed Rules|Detailed Design|Formulas|Dependencies|Tuning Knobs|Acceptance Criteria)` (+40 lines; accept both `Detailed Rules` and `Detailed Design`). Full-read a single GDD only when a section cross-references external content or matches zero sections.
2. **ADRs**: Pattern-search `^## (Status|Decision|GDD Requirements Addressed|Engine Compatibility|ADR Dependencies|Performance Implications)` (+30 lines). Interpret against `N_adr`:
   - `N_adr` matches -> proceed on scanned sections.
   - Partial matches -> record missing sections per ADR as a **structural gap** in Phase 7.
   - **`0` matches with `N_adr > 0`** -> **malformed ADRs** (not "no architecture"): stop and direct to `ags-architect adr retrofit <file>`. Never report zero coverage on malformed ADRs.
   - Full-read an individual ADR only when judging a Phase 4 conflict requires its reasoning.
3. **Architecture doc**: Read `docs/architecture/architecture.md` if present.
4. **Engine reference**: Read `VERSION.md`, `breaking-changes.md`, `deprecated-apis.md`, and ONLY `modules/` files named in ADRs' `References Consulted` / `Post-Cutoff APIs Used` fields (if none named, read none and note Phase 5 cannot verify unstated module claims).
5. **Standards & Reflexion Log**: Read `naming.*` / `performance.*` from `project.yaml`, forbidden patterns/allowed libraries from `.ags/rules/`, and `docs/consistency-failures.md` (if present — surface matching domain lessons as `"Known conflict-prone areas"` in Phase 4).

Report: `"Loaded [N_gdd] GDDs, [N_adr] ADRs, engine: [name + version]."`

---

## Phase 2: Technical Requirements Baseline (Registry-Pinned)

1. **Pre-load `docs/architecture/tr-registry.yaml`** if it exists; index by `id` and normalized `requirement` text (lowercase, trimmed) so IDs never renumber across runs:
   - Exact/near match for same system -> reuse `TR-[system]-NNN` unchanged (add `revised: [date]` if wording clarified).
   - No match -> assign next sequential `TR-[system]-NNN` (highest existing + 1).
   - Ambiguous -> prompt user (`Same requirement` vs `New requirement`).
   - `status: deprecated` -> skip intentionally removed requirement.
2. Extract technical requirements across all categories (Data structures, Performance constraints, Engine capability, Cross-system communication, State persistence, Threading/timing, Platform requirements) into `TR-[GDD]-NNN` rows.

---

## Phase 3: Traceability Matrix & Optional RTM

### 3a. ADR Coverage Grading
Match Phase 2 requirements against loaded ADR `## GDD Requirements Addressed` and `## Decision` text:
- `✅ Covered`: Addressed by an **`Accepted`** ADR.
- `🟡 Covered (Proposed)`: Addressed by a `Proposed` ADR — **NOT a pass state**; caps verdict at `CONCERNS` and cites `ags-architect adr accept ADR-NNNN`.
- `⚠️ Partial`: Partially or ambiguously covered.
- `❌ Gap`: No ADR addresses the requirement.
- `❓ Not assessed`: ADR unreadable or missing `## Status`.

### 3b. Story & Test Linkage (`rtm` or `full` with stories)
1. Count story files under `production/epics/**/*.md` (excluding `EPIC.md`). Collect fields via targeted pattern search on `production/epics/**/story-*.md`: `## Test Evidence` (+8 lines), `TR-`, and `^> \*\*Status\*\*`. Full-read a story only if `## Test Evidence` is missing or ambiguous.
2. Search `tests/unit/**/*_test.*` and `tests/integration/**/*_test.*` and verify existence of every stated test path.
3. Classify each `TR-ID`: `COVERED` (test exists), `MISSING` (path stated, missing on disk), `NONE` (Visual/Feel/UI without automated test), or `NO STORY`.

---

## Phase 4: Cross-ADR Conflicts & Dependency Graph

1. Check pairwise ADR contradictions across: Data ownership, Integration contract, Performance budget sum exceeding frame budget, Dependency ordering, Architecture pattern (e.g., events vs direct calls), and State authority.
2. **Deterministic dependency graph** (never trace cycles manually):
   ```bash
   python .ags/cli.py check adr-graph
   ```
   Interpret `ADRS:`, `EDGES:`, `NO_DEPS_SECTION:`, and `CYCLE:`:
   - Report every `NO_DEPS_SECTION` ADR as a structural gap (missing dependency declarations must never read as a clean acyclic graph).
   - Cross `EDGES:` against `## Status` from Phase 1b; flag any edge pointing to `Proposed` or missing ADRs.
   - Report every `CYCLE:` as `🔴 DEPENDENCY CYCLE`.
   - Emit topological implementation order (Foundation first).

---

## Phase 5: Engine Cross-Check, Specialist & GDD Revision Flags

### 5a. Engine Audit + Specialist Consultation
1. Verify version consistency across ADRs, validate `Post-Cutoff APIs Used` against module docs, search all ADRs for `deprecated-apis.md` symbols, and list ADRs missing `## Engine Compatibility`.
2. **Engine Specialist**: Resolve `<engine>-specialist` from `project.yaml` `engine.name`. If unconfigured, skip and record: `Engine validation: NOT ASSESSED — no engine configured (engine.name unset in project.yaml)`. Otherwise spawn `<engine>-specialist` with engine-touching ADRs, engine docs, and Phase 5 findings to verify idioms, hidden anti-patterns, and version mismatches. Specialist findings carry equal weight in the final verdict.

### 5b. GDD Revision Flags (Architecture -> Design Feedback)
Check whether any GDD assumes behavior contradicted by `HIGH RISK` engine findings, known engine limits, or deprecated APIs. Present proposed `systems-index.md` row updates inline, confirm with user (`[A] Apply` / `[B] Show full diff` / `[C] Leave unchanged`), and set flagged rows to exact status **`Needs Revision`** (no parentheticals).

---

## Phase 6: Architecture Document Coverage

If `docs/architecture/architecture.md` does not exist, emit `Architecture document coverage: NOT ASSESSED — no docs/architecture/architecture.md` as a named section/line item (do not silently omit findings; emit overall `NOT ASSESSED` verdict if Phase 6 is the review's stated scope). When present, verify all `systems-index.md` systems appear in layers, cross-system data flows and API boundaries match GDDs, and flag orphaned architecture modules.

---

## Phase 7: Review Report, Hashes & Verdict

Include content hashes from:
```bash
python .ags/cli.py check receipts hash docs/architecture/adr-*.md design/gdd/*.md
```
Structure the report with: Date, Engine, GDDs/ADRs Reviewed, Receipts, Traceability Summary, Coverage Gaps (`ags-architect adr "<suggested title>"`), Cross-ADR Conflicts, ADR Dependency Order, GDD Revision Flags, Engine Compatibility Issues + Specialist Findings, Architecture Document Coverage, Blocking Issues (`FAIL` only), Required ADRs (Foundation first), and Verdict:

- **`PASS`**: All requirements covered by `Accepted` ADRs, zero conflicts/cycles, engine consistent.
- **`NOT ASSESSED`** *(ranks above `PASS` and below `CONCERNS` and `FAIL`)*: Stated scope could not be evaluated (zero ADRs or unreadable ADRs, missing GDD/TR requirement source, unreadable/statusless ADRs yielding `❓`, or missing `architecture.md` when Phase 6 is the scope). Never resolve an unexamined scope to `PASS`.
- **`CONCERNS`**: Non-blocking gaps, partial coverage, any coverage resting on `Proposed` ADRs (`🟡`), or `NO_DEPS_SECTION` gaps.
- **`FAIL`**: Uncovered critical Foundation/Core requirements, blocking cross-ADR conflicts, or dependency `CYCLE`s.

---

## Phase 8: Writes, Reflexion Log & Session State

1. Confirm writes per `modes.automation` (`[A] Review report + traceability index + TR registry`, `[B] Review report only -> docs/architecture/architecture-review-[date].md`, `[C] None yet`; or `docs/architecture/requirements-traceability.md` in `rtm` mode).
2. Confirm `docs/architecture/tr-registry.yaml` updates: append new IDs, update `requirement` + `revised` date when GDD wording changed, mark `status: deprecated` (with confirmation) for removed requirements, update top `last_updated`/`version`, and **never renumber or delete entries**.
3. If `docs/consistency-failures.md` exists, append 🔴 `CONFLICT` entries only (never `GAP` entries, and never create the file if absent):
   ```markdown
   ### [YYYY-MM-DD] — ags-arch-review — 🔴 CONFLICT
   **Domain**: Architecture / [domain]
   **Documents involved**: [ADR-NNNN] vs [ADR-MMMM]
   **What happened**: [specific conflict — what each ADR claims]
   **Resolution**: [how resolved or resolution path]
   **Pattern**: [generalized lesson for future ADR authors]
   ```
4. Update `production/session-state/active.md` (keeping `STATUS`/`CHECKPOINT` bounded) with:
   `## Session Extract — ags-arch-review [date]` (`Verdict`, `Requirements` counts, `New TR-IDs registered`, `GDD revision flags`, `Top ADR gaps`, `Report` path).

---

## Phase 9: Pre-Gate Handoff

Present top 3 needed ADRs (Foundation first) and check existence of pre-gate files:
- `tests/unit/` and `tests/integration/` (missing -> `ags-qa setup`)
- CI test workflow `.github/workflows/tests.yml` (missing -> `ags-qa setup`)
- `design/accessibility-requirements.md` and `design/ux/interaction-patterns.md` (missing -> `ags-art-ux`)

Do NOT offer `ags-gate` as a next option while any pre-gate item is missing; route to a fresh session for missing ADRs (`ags-architect adr`) or missing pre-gate setups (`ags-qa`, `ags-art-ux`).
