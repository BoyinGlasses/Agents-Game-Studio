# Gate Procedure, Quality Checks, CoVe & Stage Update (`ags-gate`)

## 1. Tier Reductions, Smoke Floor & `system_overrides`

- **Reduction semantics**: Each `references/gate-*.md` file states the `full` baseline then `standard` / `minimal` relaxations (`drop` = omitted; `recommended` = `CONCERNS` if absent, never `FAIL`). Reductions only ever relax requirements — only `workflow_overrides` adds requirements.
- **`qa.level: minimal`**: Relaxes per-story unit/evidence items at every workflow tier, **excluding the smoke check** (build-health floor stays required wherever the gate file lists it).
- **`performance.enforce` independence**: Runs at every workflow tier (`warn` default -> `CONCERNS`, `block` -> `FAIL` from Polish onward regardless of tier, `off` -> informational). Unrecognized values warn and fall back to `warn`.
- **Zero-artifact guard**: If after applying `workflow` and `qa.level` reductions, 0 required artifacts remain, report `NOT ASSESSED` naming both reducers and the gate.
- **`workflow_overrides.system_overrides`**:
  1. Check every key in `system_overrides` against `design/gdd/<key>.md`. Any unmatched key emits a `CONCERNS` finding listing the unmatched key and available GDD stems.
  2. Apply each system's effective tier (`system_overrides.<stem>` else project `workflow`) at Systems Design and Pre-Production GDD checks. A system pinned `minimal` has zero GDD section requirement.
  3. Apply additive flags: `art_bible_strict: true` (forces 9-section art bible at Technical Setup and Pre-Production gates), `edge_cases: true` and `tuning_knobs: true` (force those GDD sections blocking on top of tier).

## 2. Deterministic Artifact & Quality Checks

1. **Artifacts**: Run `python .ags/cli.py check artifacts --phase <source-phase>` (`PRESENT`, `ABSENT`, `SHORT`, `PATTERN_MISS`, `NO_CHECK`). Surface all `NO_CHECK` items as `MANUAL CHECK NEEDED` — never treat `NO_CHECK` as `PRESENT`. Spot-read artifacts the verdict depends on for real non-placeholder content.
2. **Smoke report spot-check (mandatory)**: Cross-check claims against the repository:
   - Claims passing automated suite -> `tests/` must contain tests and a runner must be configured.
   - Claims critical path PASS -> matching implementation must exist under the resolved code root.
   - Missing date or predating latest code-root commit -> flag stale report.
   Contradictions fail at the smoke report's required level (`FAIL` when required, `CONCERNS` when recommended).
3. **Cross-GDD review** (Systems Design -> Technical Setup): Look up `design/gdd/gdd-cross-review-*.md` (`full`: missing = `FAIL`; `standard`: missing = `CONCERNS`; `minimal`: N/A). Read verdict line; `FAIL` blocks.
4. **Tests**: Run configured test runner. Resolve `testing.strict.logic` and `testing.strict.integration` from `preflight` (`true` -> `FAIL`, `false` -> `CONCERNS`; defaults `true`). When tests are required by `qa.level` and no runner is configured or starts, emit `NOT ASSESSED`.
5. **GDD structure**: Run `python .ags/cli.py check gdd` (`PRESENT:` / `ABSENT:` per GDD) and check against each GDD's effective tier (`full`: 8 sections; `standard`: 5 sections + conditional Formulas). Spot-read sections the verdict turns on.
6. **ADR circular dependencies**: Run `python .ags/cli.py check adr-graph` (`Technical Setup -> Pre-Production`). Any `CYCLE:` line -> `FAIL`; many `NO_DEPS_SECTION` -> `CONCERNS`.
7. **Performance**: Compare `performance.*` budgets (`project.yaml`, else technical preferences) against measured data in `tests/performance/` or `ags-diagnose` output. Placeholder `[16.67ms]` without actual measurement = `NOT ASSESSED`, not met.
8. **Localization**: Scan for hardcoded player-facing strings in resolved code root (`NOT ASSESSED — code root unresolved` if unresolved).

## 3. Director Panel Width & `NOT ASSESSED`

- `review_mode: solo` -> skip panel (`Director Panel skipped — Solo mode`).
- `review_mode: lean | full` -> run parallel directors for resolved `workflow` width (`minimal`: `producer`; `standard`: `technical-director`, `producer`; `full`: `creative-director`, `technical-director`, `producer`, `art-ux-director`).
- **Pre-read rule**: Parent session must NOT read `.ags/gates/*.md`; pass the gate path to each spawned director (`cd-phase-gate.md`, `td-phase-gate.md`, `pr-phase-gate.md`, `ad-phase-gate.md`).
- Announce panel omissions explicitly (`Panel: N of 4 (<tier>). <Omitted> not consulted. Run ags-gate --review full or set modes.workflow: full for complete panel.`).
- Strictest verdict from running directors wins (`NOT READY` -> min `FAIL`, `CONCERNS` -> min `CONCERNS`). A director expected by the tier that fails to return yields `NOT ASSESSED` (never fire this on intentional tier narrowing!).

## 4. Chain-of-Verification (5 Questions, >=2 `[TOOL ACTION]`)

Challenge the draft verdict before presenting:
- **PASS draft**: (1) Which quality checks were read vs inferred? (2) `[TOOL ACTION]` Re-scan for unresolved `[?]` / `MANUAL CHECK NEEDED` items. (3) `[TOOL ACTION]` Spot-read key artifacts for placeholder/skeleton text. (4) Could any dismissed minor blocker stop the next phase? (5) Least confident check?
- **CONCERNS draft**: (1) Could any concern escalate to blocker? (2) Does it compound next phase? (3) Was any `FAIL` softened to `CONCERNS`? (4) Unchecked artifacts that could reveal blockers? (5) Do combined concerns block together?
- **FAIL draft**: (1) Hard blockers separated from recommendations? (2) Lenient PASS items? (3) Additional missed blockers? (4) Minimal 3-step path to PASS? (5) Fixable or deeper design defect?

Revise upward if gaps appear (`PASS -> CONCERNS`, `CONCERNS -> FAIL`, or inferred/manual/placeholder check -> `NOT ASSESSED`). Never downgrade `NOT ASSESSED` to `PASS` without obtaining the missing input. Record: `Chain-of-Verification: [N] questions checked — verdict [unchanged | revised from X to Y]`.

## 5. Stage Update, Rigor-Fit & Remediation Routing

1. Ask confirmation before writing `production/gate-checks/gate-[phase]-[date].md`.
2. **Only on `PASS` + explicit user confirmation**:
   - Update `project.stage: <new-stage>` in `project.yaml` (if no `project:` block, insert before `modes:`; if no `project.yaml`, initialize minimal AGS v2 `project.yaml` without seeding `modes.review_mode` so `modes.rigor` still expands).
   - Dual-write single-line `<new-stage>` (no trailing newline) to `production/stage.txt`.
   - Re-read both files and verify they match; report immediately if they diverge.
3. **Rigor-fit check (advisory)**: When advancing into `Production` or later while resolved `workflow` is `minimal`, emit once: `"Entering [stage] on rigor: minimal — most projects this size run standard. Revisit with ags-settings modes.rigor=standard?"`
4. **Tailored next steps**:
   - `systems-design` PASS -> `ags-architect` (master architecture blueprint + ADR plan before individual ADRs).
   - `technical-setup` PASS -> ordered Pre-Production sequence: `ags-architect` (`control-manifest`), `ags-ideate` (`vertical-slice`), `ags-qa` (`playtest-report` >=1 session, 3+ recommended), `ags-art-ux` (`ux-design` key screens), `ags-plan` (`create-epics` foundation then core -> `create-stories` -> `sprint-plan`).
   - Hand-authored artifacts without generating skills (`design/difficulty-curve.md` from `.ags/templates/difficulty-curve.md`; `design/player-journey.md` from `.ags/templates/player-journey.md`): instruct the user to author them from those templates rather than pointing to a skill that cannot write them.
