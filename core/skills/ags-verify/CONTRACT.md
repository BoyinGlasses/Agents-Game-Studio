# ags-verify — Verification, Code Review & Closure Contract

## Role in Pipeline
Owns final quality verification (`code-review` via read-only `code-reviewer` + Game-Native Rubric, `python .ags/cli.py verify` static/engine receipts, deep `evidence` quality audits) and Checkpoint #2 game-maker story acceptance (`story-done`). Only `ags-verify` may write `Status: Complete` on story files.

## Inputs
- `In Progress` story file with `**Story Approval**: YYYY-MM-DD`, `Handoff Class:`, `Verification Method:`, `Type:`, acceptance criteria, scope, and `## Test Evidence`.
- `production/session-state/active.md` (must contain a matching approval extract with unchanged scope, criteria, `Handoff Class`, and `Verification Method`; drift yields `NOT ASSESSED — story approval drift` and routes back to `ags-dev`).
- Changed code under resolved code root, test files under `tests/`, retained visual evidence in `production/qa/evidence/`, `docs/architecture/{tr-registry.yaml,control-manifest.md,adr-*.md}`, `design/gdd/`.
- Game-maker play confirmation for `Player-facing` and `Mixed` stories.

## Preconditions & Anti-Hallucination
- Every verdict vocabulary includes `NOT ASSESSED` ranking strictly **above** pass (`COMPLETE`/`APPROVED`/`ADEQUATE`) and **below** failure (`BLOCKED`/`CHANGES REQUIRED`/`MISSING`/`INCOMPLETE`).
- Never mark an unrun test or missing build observation `PASS`; record `NOT VERIFIED — <reason>`.
- Never infer `NOT VERIFIED` passed from file existence alone; require executed command output or `python .ags/cli.py verify` receipt (`.ags/state/receipt.json`).
- A screenshot proves appearance only; `Player-facing` and `Mixed` stories require explicit game-maker play confirmation before closure regardless of `qa.level` or `testing.strict.visual`.
- `code-reviewer` runs with `sandbox_mode: read-only`; specialist claims require independent file:line/evidence verification (`VERIFIED` vs `UNVERIFIED — specialist claim`).

## Outputs & Immutability
| Artifact | Write Authority | Rule |
|---|---|---|
| Source & test code | **Read-only** in `ags-verify` | Return in-scope fix requests to primary agent (`ags-dev`); never modify code in `code-review` or `evidence` modes. |
| `.ags/state/receipt.json` | `python .ags/cli.py verify` | Fresh static/engine receipt matching current tree hash before Checkpoint #2 closure (or explicit `NOT VERIFIED` rationale). |
| Story file | Checkpoint #2 acceptance only | Write `Status: Complete`, `Last Updated`, `## Completion Notes` (with original gaps/overrides preserved). Never write on fix request, wait, or missing play. |
| `production/sprint-status.yaml` | Checkpoint #2 acceptance only | Set matching story `status: done`, `completed: YYYY-MM-DD`, `updated: YYYY-MM-DD` if file exists. |
| `production/session-state/active.md` | Always updated | Record review verdict, `Pending acceptance:` if unfinished, or final acceptance, play status, gaps, and next story. |
| `docs/tech-debt-register.md` / `production/qa/evidence-review-[date].md` | User-confirmed optional writes | Append advisory tech debt or persist deep evidence review only when explicitly requested/approved by user. |

## Downstream
- Accepted story -> `ags-dev` for next ready story in sprint, or `ags-qa` (`smoke-check` -> `team-qa`) -> `ags-plan` (`retrospective`) -> `ags-gate` -> `ags-plan` (`sprint-plan`) when all `Must Have` stories are done.
