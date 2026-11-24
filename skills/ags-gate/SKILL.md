---
name: ags-gate
description: "Use when evaluating readiness to advance between the 7 game development stages (Concept through Release) with artifact checks, quality gates, and director panel review. Do NOT use when detecting current project stage only (-> ags-start) or closing an individual story (-> ags-verify)."
---

# Phase Gate Validation

Validates whether the project is ready to advance to the next development stage (Concept -> Systems Design -> Technical Setup -> Pre-Production -> Production -> Polish -> Release). Distinct from `ags-start` stage detection (diagnostic) — `ags-gate` issues an advisory `PASS` / `CONCERNS` / `NOT ASSESSED` / `FAIL` verdict and updates `project.stage` only on explicit user confirmation.

## Contract
- **Inputs**: `project.yaml` (`project.stage`, `modes.workflow`, `modes.qa.level`, `modes.review_mode`, `modes.team.size`, `workflow_overrides.*`, `performance.*`, `testing.strict.*`), `project.local.yaml`, `production/stage.txt` (legacy fallback), `docs/consistency-failures.md`, `docs/engine-reference/<engine>/VERSION.md`, `docs/engine-reference/<engine>/deprecated-apis.md`, stage-specific artifacts in `design/`, `docs/architecture/`, `prototypes/`, `production/`, `tests/`, and code root
- **Roles**: `producer`, `technical-director`, `creative-director`, `art-ux-director` (with `art-director` lens), `qa-lead`
- **Outputs**: Gate report (optional `production/gate-checks/gate-[phase]-[date].md` with user approval), updated `project.stage` in `project.yaml` + `production/stage.txt` (ONLY on confirmed `PASS` + explicit user confirmation)
- **Verification**: `python .ags/cli.py check artifacts --phase <source-phase>`, `python .ags/cli.py check gdd`, `python .ags/cli.py check adr-graph`, test runner execution, smoke-report repo cross-check, 5-question Chain-of-Verification (`>=2` tool actions)
- **Next Skill**: `ags-gdd` (after Concept), `ags-architect` / `ags-settings` (after Systems Design), `ags-ideate` / `ags-plan` (after Technical Setup), `ags-dev` / `ags-plan` (after Pre-Production), `ags-diagnose` / `ags-qa` (after Production), `ags-release` (after Polish)

## Preflight

Run once at startup and hold resolved settings:

```bash
python .ags/cli.py preflight ags-gate [target-phase]
```

- **Target phase**: `systems-design`, `technical-setup`, `pre-production`, `production`, `polish`, or `release`. If omitted, detect current stage and ask the user to confirm `[Current] -> [Next]` (or choose another gate) before running — never skip confirmation when unargumented.
- **Mode rules**: `ags-gate` honors `workflow`, `qa.level`, `testing.strict`, `performance.enforce`, `team.size`, and `review_mode`, and is **exempt from `modes.automation`** — phase gates are deliberate human checkpoints and never auto-run or auto-advance. `--review [full|lean|solo]` overrides `review_mode`.

## Phases

### Phase 1: Load Target Gate & Check Overrides
1. Load **ONLY** the target transition's checklist from `references/`:
   - Concept -> Systems Design: [references/gate-systems-design.md](references/gate-systems-design.md)
   - Systems Design -> Technical Setup: [references/gate-technical-setup.md](references/gate-technical-setup.md)
   - Technical Setup -> Pre-Production: [references/gate-pre-production.md](references/gate-pre-production.md)
   - Pre-Production -> Production: [references/gate-production.md](references/gate-production.md)
   - Production -> Polish: [references/gate-polish.md](references/gate-polish.md)
   - Polish -> Release: [references/gate-release.md](references/gate-release.md)
2. Read `docs/consistency-failures.md` (if present) for domain-matched scrutiny context.
3. Apply `workflow` tier reductions and `qa.level` relaxation (`minimal` drops per-story unit/evidence checks, **NEVER** drops the smoke-check floor or `performance.enforce`).
4. **Zero-required-artifact guard**: Count remaining required artifacts after reductions. If **0** remain (e.g., Production -> Polish if a configuration left no required floor), emit `NOT ASSESSED` naming both reducers and the gate — never `PASS` by emptiness.
5. **Per-system overrides check** (Systems Design & Pre-Production GDD checks): Verify every key in `workflow_overrides.system_overrides` matches `design/gdd/<key>.md`. Any unmatched key is a `CONCERNS` finding listing available stems. Apply higher/lower tier per system (`minimal` = no GDD section floor) plus additive overrides (`art_bible_strict`, `edge_cases`, `tuning_knobs`).

### Phase 2: Deterministic Checks & Spot-Reading
1. Run `python .ags/cli.py check artifacts --phase <source-phase>`. Treat `NO_CHECK` rows as `MANUAL CHECK NEEDED`, never `PRESENT`. Spot-read artifacts the verdict turns on to confirm non-placeholder content.
2. **Mandatory smoke-report audit**: Verify smoke claims against repo reality (`tests/`, code root paths, commit recency); fabricated or stale reports fail at the artifact's required level.
3. Run quality checks per [references/gate-procedure.md](references/gate-procedure.md):
   - Test suite via configured runner (`testing.strict.logic`/`.integration` control Blocker vs Concern; unconfigured or unstarted runner when tests are required by tier = `NOT ASSESSED`, never `PASS`).
   - `python .ags/cli.py check gdd` for Systems Design (`standard`: 5 sections + conditional Formulas; `full`: 8 sections) and cross-GDD report check.
   - `python .ags/cli.py check adr-graph` at Technical Setup (`CYCLE:` = `FAIL`; many `NO_DEPS_SECTION` = `CONCERNS`).
   - Performance budgets vs measured data (`performance.enforce`: `warn` default -> `CONCERNS`, `block` -> `FAIL` from Polish onward regardless of tier, `off` -> informational; placeholder numbers count as unmeasured).
   - Hardcoded player-facing strings scan in resolved code root (`NOT ASSESSED — code root unresolved` if unknown).
4. Surface all non-automatable items as `MANUAL CHECK NEEDED` and ask the user — never assume `PASS`.

### Phase 3: Director Panel & Chain-of-Verification
1. Apply `review_mode`: `solo` skips panel; `lean` and `full` run the panel scaled by `workflow`:
   - `minimal` (1): `producer` (`.ags/gates/pr-phase-gate.md`)
   - `standard` (2): `technical-director` (`.ags/gates/td-phase-gate.md`), `producer`
   - `full` (4): `creative-director` (`.ags/gates/cd-phase-gate.md`), `technical-director`, `producer`, `art-ux-director` (`.ags/gates/ad-phase-gate.md`, `art-director` lens)
   Run spawned directors in parallel without pre-reading gate files in parent session. `team.size` scales depth inside each review, not director count. Explicitly state omitted panel perspectives when width < 4 (`Panel: N of 4`). If an expected director errors or fails to return, record `NOT ASSESSED`.
2. Run the 5-question **Chain-of-Verification** (`>=2` `[TOOL ACTION]` file/command re-checks) in [references/gate-procedure.md](references/gate-procedure.md). Never downgrade `NOT ASSESSED` to `PASS` without obtaining the missing input.

### Phase 4: Verdict, Stage Write & Next-Step Routing
Present the full gate report, confirm report persistence before writing `production/gate-checks/gate-[phase]-[date].md`, and ONLY on `PASS` + explicit user confirmation dual-write `project.stage` in `project.yaml` and `production/stage.txt` (verify both match). Run the one-line `rigor: minimal` advisory when entering Production+ on `workflow: minimal`, then present tailored next steps. Never auto-create missing artifacts to manufacture a `PASS`.

## Gate & Verdict

- **Verdict Precedence (first matching rule wins)**: `FAIL` > `CONCERNS` > `NOT ASSESSED` > `PASS`.
  - **FAIL**: Missing required artifact, failing blocking test/smoke check, circular ADR dependency, built Vertical Slice failing validation, `performance.enforce: block` breach (Polish+), or any panel `NOT READY`.
  - **CONCERNS**: Missing recommended artifact, orphaned `system_overrides` key, advisory test failure, `performance.enforce: warn` breach, or panel `CONCERNS`.
  - **NOT ASSESSED** (outranks `PASS`, ranks below `CONCERNS`/`FAIL`): Zero required artifacts left after reductions, present-but-empty/placeholder required artifact, hollow/placeholder profiler data, unconfigured/unstarted required test runner, unresolved `MANUAL CHECK NEEDED` item, expected director missing verdict, or upstream `NOT ASSESSED` propagating.
  - **PASS**: All required artifacts verified, quality checks passing, panel `READY` (or `solo`), and CoVe consistent. Full procedure in [references/gate-procedure.md](references/gate-procedure.md) and [CONTRACT.md](CONTRACT.md).
