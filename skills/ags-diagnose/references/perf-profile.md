# Performance Profiling (`ags-diagnose perf`)

Identifies CPU, memory, rendering, and I/O hotspots, compares measurements against committed `performance.*` budgets, and outputs ranked optimization recommendations.

**Output:** `production/polish/[scope]-report-[date].md`

---

## Mandatory Insufficient-Input Gate (Run Before Any Report)

**If required inputs do not exist, the verdict is `NOT ASSESSED — NO DATA`, never a filled-in pass.**

1. Inventory every input this run reads: source files under the resolved code root (`src/`, `Assets/`, `Source/<Module>/`), profiler captures, prior polish/soak reports, test results, and committed budgets.
2. Mark each explicitly as **`FOUND`** or **`ABSENT`**.
3. If any input required for a section is `ABSENT`, mark that section **`NOT ASSESSED — NO DATA`**. Never estimate it, infer it from an adjacent artifact, or leave template cells to be treated as measured.
4. If **all** required inputs are `ABSENT` (or code root is unresolved), stop and report **`NOT ASSESSED — NO DATA`** as the whole verdict, naming missing artifacts and which skill produces them (`ags-settings`, `ags-dev`, `ags-qa`).

> Absence of evidence is never evidence of absence. Zero findings over missing or empty files has verified nothing.

---

## Phase 0: Resolve Budget Enforcement (`performance.enforce`)

`performance.enforce` (resolved via `preflight`, locally overridable via `ags-settings --local performance.enforce=block`) governs what budget breaches mean without changing what is measured:

| Value | Effect on Findings |
|---|---|
| `warn` *(default)* | Report violations as findings; informational in CI, non-blocking |
| `block` | Report violations as **blockers** — `ags-gate` fails the Polish gate on over-budget systems |
| `off` | Budgets informational only — report measured values without raising findings or fix tasks |

Only `warn`, `block`, and `off` are valid. Surface any unrecognized value to the user and fall back to `warn`.

---

## Phase 1 & 2: Scope & Committed Budgets

- **Scope**: `[system]` (focus on one system) or `full` (entire codebase).
- **Load budgets from config FIRST** (literal dotted keys resolved via `python .ags/cli.py preflight ags-diagnose perf`):
  - `performance.target_framerate`
  - `performance.frame_budget_ms`
  - `performance.draw_call_limit`
  - `performance.memory_ceiling_mb`
- Fall back to design docs or `AGENTS.md` (and any legacy technical-preferences file) only for keys unset in config (FPS, total/per-system memory, load time targets, draw calls, multiplayer bandwidth).
- **An unset budget is `NOT ASSESSED`, not a pass.** Never compare estimates against template example numbers like `[16.67ms]`.

---

## Phase 3: Analyze Codebase (`performance-analyst` lens)

Run as `test-engineer` applying `.ags/roles/performance-analyst.md` across the resolved code root:
- **CPU targets**: `_process()` / `Update()` / `Tick()` cost inventory, nested loops over large collections, string concatenation/formatting in hot paths, per-frame allocations, unindexed entity search/sort, per-frame physics raycasts or overlap queries.
- **Memory targets**: growing data structures, texture/mesh/audio footprint estimates, object pooling vs. frequent instantiate/destroy churn, leaked node/object references, unbounded caches.
- **Rendering targets**: draw call estimates, transparent overdraw, heavy shader passes, unoptimized particle emitters, missing LODs or occlusion culling.
- **I/O targets**: synchronous save/load stalls, blocking asset loads vs. async streaming, network packet frequency and payload size.

---

## Phase 4: Generate & Write Profiling Report

Write to `production/polish/[scope]-report-[date].md` (same path used by `ags-team` polish so runs compare directly), creating the directory if absent and confirming per `modes.automation`. **Keep every `NOT ASSESSED` section intact in the written file — never edit gaps out on the way to disk.**

Include:
1. `### Performance Budgets` (`Metric | Budget | Estimated Current | Status` — `OK / WARNING / OVER / NOT ASSESSED`)
2. `### Hotspots Identified` (`# | Location | Issue | Estimated Impact | Fix Effort [S/M/L]`)
3. `### Optimization Recommendations (Priority Order)` (`Location file:line`, `Expected gain`, `Risk`, `Approach`)
4. `### Quick Wins (< 1 hour each)`
5. `### Requires Investigation` (items needing runtime profiler validation on target hardware)

Present summary in conversation: top 3 hotspots, headroom vs. budget (or `NOT ASSESSED`), and recommended next action.

---

## Phase 5: Scope & Timeline Decision (if any Fix Effort is M or L)

Phase 5 makes **no source edits** (only the Phase 4 report is written upon approval). For each M/L hotspot, ask the user to choose:
- **A)** Implement the optimization now or schedule it (`ags-plan`)
- **B)** Reduce feature scope (`ags-arch-review [feature]`)
- **C)** Accept impact and defer to Polish (record under `### Deferred to Polish`)
- **D)** Escalate to `technical-director` for architectural ADR (`ags-architect`)

---

## Rules

- Never optimize without measuring first; static analysis surfaces candidates while target-hardware runtime profiling confirms actual bottlenecks.
- Every recommendation must cite `file:line` and estimated impact.
- Verdict: **`COMPLETE`** once report approved and no `NOT ASSESSED` / `block` violations remain; **`NOT ASSESSED`** when budgets or profiler/code inputs were absent; **`BLOCKED`** when `performance.enforce: block` sees an over-budget system or write approval is declined.
