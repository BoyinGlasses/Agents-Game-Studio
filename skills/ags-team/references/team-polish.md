# Team Playbook: Polish (`ags-team polish`)

Orchestrates profiling, optimization, visual/audio juice, and soak/stress QA hardening for a feature or area.

## Argument, Paths & Role Mapping

- **Argument check**: Requires `[feature or area]` (e.g., `combat`, `main menu`, `inventory system`, `level-1`). If omitted, output usage (`ags-team polish <feature or area>`) and stop without spawning roles.
- **Active-set (`team.size`)**:
  - **`individual`** (default): `performance-analyst` (via `test-engineer`) + `tech-artist`. Other roles consulted through these two.
  - **`small`**: + `sound-designer` + `test-engineer`.
  - **`studio`**: Full pipeline + engine sub-specialists + adversarial review (`code-reviewer`).
- **Director gate skip rule**: Before spawning any director or lead review outside `PHASE-GATE` triggers, skip at `solo` and skip non-`PHASE-GATE` reviews at `lean`.
- **Role map**:
  - `performance-analyst` lens -> `test-engineer` (`.ags/roles/performance-analyst.md`)
  - `engine-programmer` lens -> `gameplay-coder` (`.ags/roles/engine-programmer.md`, invoked on low-level bottlenecks)
  - `tech-artist` -> `.ags/roles/tech-artist.md`
  - `sound-designer` lens -> `tech-artist` (`.ags/roles/sound-designer.md`)
  - `tools-programmer` lens -> `gameplay-coder` (`.ags/roles/tools-programmer.md`, invoked if content pipeline tools are in scope)
  - `test-engineer` -> `.ags/roles/test-engineer.md`

Announce the active roster and unspawned roles before Phase 1.

### Concrete Output Paths (`production/polish/`)

Date-stamped polish measurements write to `production/polish/` so runs remain comparable over time (inform the user that `production/polish/` records are point-in-time reports and not inputs to downstream gates):

| Role | Destination Path |
|---|---|
| `performance-analyst` | `production/polish/[area]-report-[date].md` |
| `tech-artist` | `production/polish/[area]-render-notes-[date].md` |
| `engine-programmer` | `production/polish/[area]-engine-fixes-[date].md` |
| `sound-designer` | `production/polish/[area]-audio-notes-[date].md` |
| `test-engineer` | `production/polish/[area]-verification-[date].md` |

## Pipeline

### Phase 1: Assessment (`performance-analyst`)

- Profile the target feature/area using `ags-diagnose perf-profile`.
- Identify performance bottlenecks and frame budget violations.
- Measure memory usage and check for leaks.
- Benchmark against target hardware specifications.
- Output: prioritized optimization list (`production/polish/[area]-report-[date].md`).

### Phase 2: Optimization (`performance-analyst` + programmers)

- Optimize hotspots identified in Phase 1 (draw calls, overdraw, memory leaks, allocation pressure).
- Verify optimizations preserve identical gameplay behavior.
- If Phase 1 found engine-level root causes (rendering pipeline, resource loading, allocator), delegate engine hot-path fixes to `engine-programmer` in parallel.
- Output: optimized code with measured before/after metrics.

### Phase 3: Visual Polish (`tech-artist`, parallel with Phase 2)

- Review VFX quality and alignment with `design/art/art-bible.md`.
- Optimize particle systems and shaders.
- Add screen shake, camera feedback, and visual juice where appropriate.
- Verify effects degrade gracefully on lower quality settings.

### Phase 4: Audio Polish (`sound-designer`, parallel with Phase 2)

- Audit audio events for completeness (ensure no player actions lack feedback).
- Check mix levels so no cue dominates or disappears.
- Layer ambient audio for atmosphere and verify spatial positioning.

### Phase 5: Hardening (`test-engineer`)

- Test boundary conditions, rapid inputs, and unusual action sequences.
- Run extended soak testing to detect degradation or leaks over time.
- Run stress tests (maximum entities, worst-case load).
- Run regression tests to verify polish changes broke nothing.
- Validate on minimum-spec hardware if available (if unavailable, report `Min-spec hardware check: NOT ASSESSED — hardware unavailable`).

### Phase 6: Sign-Off

Collect results across all roles, compare measured metrics against project budgets, and report:
- `READY FOR RELEASE` / `NEEDS MORE WORK` / `NOT ASSESSED` (if profiling or test suites could not run)
- Remaining issues with severity, owners, and active/skipped roster disclosure.

## Verdicts & Next Steps

- **COMPLETE (READY FOR RELEASE)**: Performance budgets met, polish verified, zero regressions.
- **CONCERNS (NEEDS MORE WORK)**: Non-blocking polish items or S3/S4 issues deferred to sprint planning.
- **NOT ASSESSED**: Profiler, soak runner, or target hardware unavailable — report explicitly instead of passing.
- **BLOCKED**: Unresolved regression, missing GDD/architecture prerequisite, or `Proposed` ADR.
- **Next Skills**:
  - `ags-release release-checklist` if `READY FOR RELEASE`.
  - `ags-plan sprint-plan` to schedule remaining polish items if `NEEDS MORE WORK`.
  - `ags-gate` for a formal phase-gate verdict before release.
