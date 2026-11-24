---
name: ags-diagnose
description: "Use when profiling code hotspots against performance budgets or auditing save files, multiplayer networking, inputs, secrets, and dependencies for security vulnerabilities. Do NOT use when running functional QA, smoke, or soak suites (-> ags-qa), filing gameplay defects (-> ags-bugs), or reviewing a single story diff (-> ags-verify)."
---

# Diagnostics — Performance Profiling & Security Audit

Static diagnostics across performance budgets and game security surfaces, with strict input-presence, code-root, and `docs/engine-reference/` provenance gates so uncheckable areas never produce false clean passes.

## Contract

- **Inputs**: `project.yaml`, `project.local.yaml`, resolved code root (`src/`, `Assets/`, `Source/<Module>/`), `assets/data/`, `addons/` / `plugins/` / `third_party/` / `vendor/`, `docs/engine-reference/<engine>/{VERSION.md,breaking-changes.md,deprecated-apis.md,modules/{networking,input}.md}`, profiler/test outputs, design docs
- **Roles**: `test-engineer` (applying `.ags/roles/performance-analyst.md` lens for CPU/memory/render/IO profiling), `code-reviewer` (applying `.ags/roles/security-engineer.md` lens for security auditing), `technical-director` (architectural escalation), `scout` (optional file/addon discovery)
- **Outputs**: `production/polish/[scope]-report-[date].md` (`perf`), `production/security/security-audit-[date].md` (`security`), preserving every `NOT ASSESSED` and `NOT SOURCEABLE` gap verbatim
- **Verification**: `python .ags/cli.py verify`, explicit `FOUND`/`ABSENT` input inventory, engine reference provenance verification before pattern scans, and mandatory `NOT ASSESSED` gating when engine, code root, budgets, or sourced patterns are missing
- **Next Skill**: `ags-architect` (structural fixes via ADR), `ags-arch-review` (scope trade-offs), `ags-plan` (schedule remediation), `ags-gate` (Polish/Release gate check), `ags-release` (launch readiness once blockers clear)

## Preflight

Run once at startup and apply resolved values without re-deriving them:

```bash
python .ags/cli.py preflight ags-diagnose [perf|security|both] [args]
```

- **`performance.enforce`** (`warn` default | `block` | `off`; locally overridable in `project.local.yaml`): governs whether budget violations in `perf` are blockers (`block` fails `ags-gate` Polish). Unrecognized values warn and fall back to `warn`.
- **Committed budgets**: Read all four literal keys from preflight/config before design docs or `AGENTS.md`:
  - `performance.target_framerate`
  - `performance.frame_budget_ms`
  - `performance.draw_call_limit`
  - `performance.memory_ceiling_mb`
- **`engine.name`, `engine.language`, and code root**: Resolve from `project.yaml` (or preflight legacy technical-preferences fallback). Unresolved engine or code root forces **`NOT ASSESSED`** — never default to `src/` or Godot patterns.
- **`platform.multiplayer` / `platform.online`**: **Absent does NOT mean `false`.** Ask the user if online/multiplayer scope applies; if unconfirmed, run multiplayer security checks anyway and mark `NOT ASSESSED — multiplayer scope unconfirmed` (preventing `CLEAR TO SHIP`).
- **`modes.automation`**: `collaborative` | `guided` | `autonomous` per `automation-modes`.

## Phases

Route to `perf`, `security`, or both in sequence:

1. **Performance Profiling (`perf [system|full]`)** -> [references/perf-profile.md](references/perf-profile.md)
   - **Insufficient-Input Gate (run first)**: Inventory all inputs as `FOUND` or `ABSENT`. Missing required inputs make that section **`NOT ASSESSED — NO DATA`**; all inputs `ABSENT` (or unresolved code root) stops the run with **`NOT ASSESSED — NO DATA`**. Never estimate against template placeholders (`[16.67ms]`); any metric lacking a committed budget is **`NOT ASSESSED`**.
   - Resolve `performance.enforce`, load the four `performance.*` config keys (fallback to design docs / `AGENTS.md`), inspect CPU, Memory, Rendering, and I/O hotspots using `test-engineer` with `.ags/roles/performance-analyst.md`.
   - Confirm and write `production/polish/[scope]-report-[date].md` keeping all `NOT ASSESSED` sections intact. If any Fix Effort is M/L, run Phase 5 scope/timeline choices (`ags-arch-review`, `ags-architect`, or `### Deferred to Polish`).
2. **Security Audit (`security [full|network|save|input|quick]`)** -> [references/security-audit.md](references/security-audit.md)
   - Verify `engine.name`, `engine.language`, code root, and `platform.multiplayer` scope. Delegate to `code-reviewer` with `.ags/roles/security-engineer.md` (or perform directly using `.ags/roles/security-engineer.md` if delegation is unavailable).
   - Consult `docs/engine-reference/<engine>/` before scanning Categories 1–6:
     - **Category 1 (Save/Serialization)**: Godot uses verified version-pinned file/serialization patterns; Unity and Unreal are **`NOT SOURCEABLE`** (neither reference tree covers save/serialization APIs -> MUST emit **`NOT ASSESSED`** and make `CLEAR TO SHIP` unreachable — never invent APIs from training data).
     - **Category 2 (Network/Multiplayer)**: Godot/Unity/Unreal pattern sets sourced from `docs/engine-reference/<engine>/modules/networking.md`; skipped only when single-player is explicitly confirmed (`platform.multiplayer: false`).
     - **Category 3 (Input)**: Godot/Unity/Unreal pattern sets sourced from `docs/engine-reference/<engine>/modules/input.md`.
     - **Categories 4–6**: Data Exposure, Cheat/Anti-Tamper, and Dependency/Supply Chain (`addons/`, `plugins/`, `third_party/`, `vendor/`).
   - Classify `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` (elevate multiplayer `HIGH` to `CRITICAL`), confirm writing `production/security/security-audit-[date].md`, and re-run `ags-diagnose security quick` after fixes before `ags-gate` release checks.

## Gate & Verdict

Verdict precedence (first match wins; **`NOT ASSESSED` strictly outranks `COMPLETE` / `CLEAR TO SHIP` and ranks below `FAIL` / `DO NOT SHIP` / `BLOCKED`**):

1. **`DO NOT SHIP` / `FIX CRITICALS FIRST` / `BLOCKED`**: Open `CRITICAL` or `HIGH` security vulnerabilities, over-budget performance metrics under `performance.enforce: block`, or declined write approval.
2. **`NOT ASSESSED`**: Missing `engine.name`, unresolved code root, insufficient implemented surface (e.g., stub repo), unconfirmed `platform.multiplayer`, any `NOT SOURCEABLE` category for the active engine (e.g., Unity/Unreal Category 1 Save/Serialization), unconfirmed version-pinned API names, missing profiler/code inputs, or unset performance budgets. **`CLEAR TO SHIP` is strictly unreachable while any category or budget is `NOT ASSESSED`.**
3. **`COMPLETE` / `CLEAR TO SHIP`**: All applicable categories and committed budgets evaluated with zero `CRITICAL`/`HIGH` security findings, zero blocking budget breaches, and reports written cleanly.
