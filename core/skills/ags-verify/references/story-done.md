# Story Acceptance & Closure Workflow (`ags-verify` Checkpoint #2)

Completes an approved `In Progress` story, verifies receipts and criteria, enforces Checkpoint #2 human acceptance, and writes `Status: Complete`.

## 1. Story Resolution & Approval Integrity Guard

1. Resolve story (argument -> `active.md` -> in-progress stories in `production/sprints/`). If already `Status: Complete` with `Accepted By Game Maker`, report and stop.
2. Extract `Type:`, `Handoff Class:`, `Verification Method:`, `**Story Approval**`, `Manifest Version:`, `TR-ID`, `ADR`, acceptance criteria, scope, and `## Test Evidence`.
3. **Approval drift check**: Read the latest approval extract in `production/session-state/active.md`. Missing `**Story Approval**`, missing `Handoff Class:`, missing extract, or any drift in scope, criteria, `Handoff Class`, or `Verification Method` MUST return `NOT ASSESSED — story approval drift` and return to `ags-dev` for revised Checkpoint #1 approval. Never silently default a missing `Handoff Class` to `Technical`.
4. Read targeted `tr-registry.yaml` `id: <TR-ID>` entries, GDD rules, `control-manifest.md` header version, and bounded ADR `## Decision` + `## Consequences` spans.

## 2. Verification Receipt & Criteria Traceability

1. **Run `python .ags/cli.py verify`** before presenting Checkpoint #2 so `.ags/state/receipt.json` holds current static/engine checks and matches the working tree hash (`NOT VERIFIED — <reason>` if engine binary unavailable; never promote file existence or unrun tests to `PASS`).
2. **Verify every acceptance criterion**:
   - Automatic checks: file existence, executed test output, hardcoded numeric literals, hardcoded player-facing strings in resolved code root (`NOT ASSESSED — code root unresolved` if code root unknown), dependency existence.
   - Performance criteria: require actual measured timing + retained command/report (`NOT VERIFIED — no timing measurement` if absent).
   - Manual/feel criteria: fold into the single Checkpoint #2 report (`awaiting game-maker play`, `OBSERVED + path`, or `NOT VERIFIED — reason`); never ask separate per-criterion prompts beforehand.
   - **Traceability table**: Map each `AC-N` to unit test, integration test, retained screenshot (`production/qa/evidence/[story-slug]/`), or game-maker play confirmation (`PENDING` until confirmed). Unless `qa.level: minimal`, **`>50% UNTESTED` escalates to BLOCKING**; `<=50% UNTESTED` is ADVISORY.
3. **Handoff & `testing.strict` evidence rules**:
   - Resolve `testing.strict.<key>` (`logic`, `integration`, `visual`, `ui`, `config`) from `preflight` output (`true` -> BLOCKING, `false` -> ADVISORY; fallback plain boolean; defaults: `Logic`/`Integration`/`Visual/Feel`/`UI` BLOCKING, `Config/Data` ADVISORY in `story-done`). At `qa.level: minimal`, waive type-specific automated test files (still require executed technical evidence for `Technical`/`Mixed` technical criteria, and NEVER waive `Run result:` observation or game-maker play!).
   - Visual/Feel & UI require evidence doc (`.ags/templates/test-evidence.md` schema) + retained image file + checked sign-off rows (`[x] Approved`).
   - Other story types require a valid `Run result:` (`OBSERVED` with path, valid `N/A — <reason>`, or flagged `NOT VERIFIED`).

## 3. Deviation Checks & Optional Tier Gates

Resolve per-story `workflow` tier (`full` = GDD + ADR checks; `standard` = 5 GDD sections + critical ADRs; `minimal` = skip GDD/ADR traceability, keep manifest/hardcoded/scope checks):
1. GDD rules against current `tr-registry.yaml` text
2. Manifest version staleness (`ADVISORY` if story predates current manifest)
3. ADR constraints (`## Decision` + `control-manifest.md`)
4. Hardcoded gameplay tuning values in logic code
5. Scope check (extra files outside stated scope)

**Director gates** (per resolved `review_mode`):
- **`QL-TEST-COVERAGE`** (`.ags/gates/ql-test-coverage.md` via `qa-lead`): skipped if `qa.level: minimal`, `Config/Data`, `solo`, or `lean`. In `full`, `ADEQUATE` passes, `GAPS` = ADVISORY, `INADEQUATE` = BLOCKING.
- **`LP-CODE-REVIEW`** (`.ags/gates/lp-code-review.md` via `code-reviewer` with `lead-programmer` lens): skipped in `solo`; in `lean`, report `LP-CODE-REVIEW skipped — Lean mode` and fold the Phase 2 `code-review` verdict into Checkpoint #2 (`CHANGES REQUIRED`/`REJECT` -> `BLOCKED`).

## 4. Verdict Precedence & Checkpoint #2 Report

**Precedence (first match wins)**: `BLOCKED` > `NOT ASSESSED` > `COMPLETE WITH NOTES` > `COMPLETE`.
- Emit `NOT ASSESSED` when approval extract drifted, a criterion lacks any observable outcome, evidence is corrupt/unreadable, `evidence` sub-mode returned `NOT ASSESSED`, governing GDD/ADR for a deviation check is missing, or required verification was `NOT VERIFIED`.
- Pending game-maker play on `Player-facing`/`Mixed` prevents `COMPLETE` and `COMPLETE WITH NOTES` — keep `Status: In Progress`.

Present ONE Checkpoint #2 report before any completion write:

```markdown
## Story Done: [Story Name]
**Story**: [file path] | **Date**: [YYYY-MM-DD] | **Verdict**: [COMPLETE | COMPLETE WITH NOTES | NOT ASSESSED | BLOCKED]

### Acceptance Criteria & Traceability
[X/Y passing + | Criterion | Test/Evidence | Status (COVERED/UNTESTED/PENDING) |]

### Verification & Deviations
- **Verify Receipt**: [.ags/state/receipt.json tree hash + engine check result | NOT VERIFIED — reason]
- **Test Evidence**: [Story Type, required vs found]
- **Deviations & Scope**: [NONE | BLOCKING / ADVISORY / OUT OF SCOPE list]

### Story Handoff (Checkpoint #2)
- **Changes**: [files changed and player-visible effect]
- **Handoff Class**: [Player-facing | Technical | Mixed]
- | Acceptance criterion | Evidence path or command and result | Status |
- **Play steps**: [direct launch + steps + Tuning Card for Player-facing/Mixed | N/A — Technical]
- **Game-maker play**: [Confirmed after playing | Pending | N/A — Technical]
- **Review**: [code-reviewer verdict + unresolved items; in full mode include `Gate: LP-CODE-REVIEW — [result]`]
- **Limitations**: [specific gaps or None]
```

**Single Checkpoint #2 decision** (mandatory in every automation mode):
- `Accept this story — I have played it if required`
- `Request fixes — keep this story In Progress`
- `Wait for play or missing evidence — keep this story In Progress`
- `Explicitly accept the named verification gap or deviation`

## 5. Closure Updates & Next-Story Routing

- **On fixes/wait**: Leave `Status: In Progress`, append `Pending acceptance: [item]` to `active.md`, fix in-scope issues via `ags-dev` and return to Checkpoint #2.
- **On acceptance** (requiring play confirmation for `Player-facing`/`Mixed`; named-gap acceptance preserves original `NOT VERIFIED`/failure in notes):
  1. Write `Status: Complete`, `Last Updated: YYYY-MM-DD`, and `## Completion Notes` (Completed, Criteria, Deviations, Blocking Deviations Explicitly Accepted, Test Evidence, Code Review, Accepted By Game Maker, Game-maker Play, Verification Gaps Accepted).
  2. Append to `docs/tech-debt-register.md` ONLY if user explicitly requested logging advisory deviations.
  3. Update `production/sprint-status.yaml` (`status: done`, `completed: YYYY-MM-DD`, `updated: YYYY-MM-DD`) if present.
  4. Suggest a Conventional Commit (`feat: [story title] ([TR-ID])`) and update `production/session-state/active.md`.
  5. Surface up to 3 next `READY`/`NOT STARTED` unblocked stories in sprint (`ags-dev`), OR if all `Must Have` stories are done, emit the **Sprint Close-Out Sequence**: `ags-qa` (`smoke-check` -> `team-qa`) -> `ags-plan` (`retrospective`) -> `ags-gate` -> `ags-plan` (`sprint-plan`).
