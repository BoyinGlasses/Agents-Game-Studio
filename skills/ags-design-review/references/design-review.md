# Single-GDD Review Workflow (`ags-design-review`)

Reviews one GDD (`design/gdd/<system>.md`) for completeness, internal consistency, implementability, cross-system conflicts, and design rigor. Always run in a **fresh session** independent from the authoring session.

## Mode & Tier Controls

- **Per-system `workflow`**: Resolve `workflow_overrides.system_overrides.<stem>` -> `modes.workflow` -> `modes.rigor`.
  - `full`: All 8 sections required; missing any blocks approval.
  - `standard`: 5 required (`Overview`, `Detailed Design`/`Detailed Rules`, `Edge Cases`, `Dependencies`, `Acceptance Criteria`) + conditional `Formulas` (required whenever system **defines numeric rules** — rates, curves, thresholds, costs, damage, drop weights; `Category` is a hint only, never the sole test). `Player Fantasy` & `Tuning Knobs` are advisory unless `workflow_overrides` require them.
  - `minimal`: GDD optional; validate any authored GDD advisorily against the 5 standard sections.
- **Review mode (`modes.review_mode` / `--review`)**:
  - `full`: All phases + parallel adversarial specialist delegation (Phase 3b).
  - `lean`: Phases 1-5 without specialist delegation.
  - `solo`: Phases 1-4 only (no delegation, no Phase 5 closing prompt).

## Phase 1: Receipt Check & Context Load

1. **Freshness check first**:
   ```bash
   python .ags/cli.py check receipts check "design/gdd/reviews/[doc-name]-review-log.md" "[target-doc-path]" "design/registry/entities.yaml"
   ```
   - **All `UNCHANGED`** and log carries latest verdict: If `APPROVED`, prompt `[A] Use prior verdict (Recommended)` / `[B] Re-review anyway` (`guided` uses `[A]`; `autonomous` logs and uses `[A]`). If prior verdict was `NEEDS REVISION` or `MAJOR REVISION NEEDED`, state plainly that the document has not changed since failing review and direct user to revise it (offer to print prior findings).
   - **Only registry `CHANGED`** (doc `UNCHANGED`): Re-verify registry-sourced values in the doc; escalate to full review only if a conflict appears.
   - **Target `CHANGED`/`NEW` or `RECEIPT: NONE`**: Run the **full** review below. NEVER perform a partial/delta re-review skipping unchanged sections.
2. Read target GDD in full and check `AGENTS.md` / `project.yaml`.
3. **Cross-document facts (registry first)**: If `design/registry/entities.yaml` exists and lists entries for this system, search `source: design/gdd/[system].md` (`-A 6`) for owned entries and `design/gdd/[system].md` (`-B 8`) for referenced entries (because `referenced_by:` is a multi-line YAML sequence). If registry is absent or empty for this system, read ONLY the GDDs named in `Dependencies` (never search-read all `design/gdd/*.md`).
4. Check whether every named dependency GDD exists on disk (flag missing files as broken references). Read `design/gdd/game-concept.md` and `design/narrative/` if present for tone/pillar conflicts. Check `design/gdd/reviews/[doc-name]-review-log.md` for prior blockers.

## Phase 2: Deterministic Completeness Check

1. Run:
   ```bash
   python .ags/cli.py check gdd "[target-doc-path]"
   ```
   (`check gdd` reports `PRESENT:` / `ABSENT:` and accepts both `## Detailed Design` and `## Detailed Rules`.)
2. Evaluate checklist against the resolved tier (mark each missing section **REQUIRED** or **ADVISORY**; spot-read any present heading that looks empty):
   - Overview (REQUIRED all tiers)
   - Player Fantasy (REQUIRED `full`; ADVISORY `standard`)
   - Detailed Rules / Detailed Design (REQUIRED `full`/`standard`)
   - Formulas (REQUIRED `full`; conditional REQUIRED `standard` on numeric rules, else ADVISORY)
   - Edge Cases (REQUIRED `full`/`standard`)
   - Dependencies (REQUIRED `full`/`standard`)
   - Tuning Knobs (REQUIRED `full`; ADVISORY `standard` unless `workflow_overrides.tuning_knobs: true`)
   - Acceptance Criteria (REQUIRED `full`/`standard`)

## Phase 3 & Phase 3b: Consistency, Implementability & Parallel Adversarial Review

- **Phase 3**: Check internal consistency (formulas vs behavior, edge cases vs rules, bidirectional dependencies), implementability (no hand-waving, perf considered), and cross-system alignment (pillars, tone, mechanics).
- **Phase 3b (`full` mode only; skip in `lean`/`solo`)**: Print 8-15 min timing notice (`--review lean` hint). Identify ALL touched domains from the already-loaded GDD and spawn **real parallel subagents simultaneously** (never simulate domain reviews inline):

| GDD Signal | Roles / Lenses to Spawn |
|---|---|
| Costs, drops, rewards, economy | `game-designer` (`economy-designer`) |
| Combat stats, damage, DPS, health | `game-designer` (`game-designer`, `systems-designer`) |
| AI behavior, pathfinding, targeting | `gameplay-coder` (`ai-programmer`) |
| Level layout, spawning, wave structure | `game-designer` (`level-designer`) |
| Progression, XP, unlocks | `game-designer` (`economy-designer`, `game-designer`) |
| UI, HUD, menus, displays | `art-ux-director` (`ux-designer`), `gameplay-coder` (`ui-programmer`) |
| Dialogue, quests, story, lore | `game-designer` (`narrative-director`) |
| Animation, feel, timing, juice | `gameplay-coder` |
| Multiplayer, sync, replication | `gameplay-coder` (`network-programmer`) |
| Audio cues, music triggers | `tech-artist` (`audio-director`) |
| Performance, draw calls, memory | `test-engineer` (`performance-analyst`) |
| Engine-specific patterns/APIs | `<engine>-specialist` from `project.yaml` `engine.name` (`godot`/`unity`/`unreal`) |
| Acceptance criteria, testability | `qa-lead` |
| Data schema, formulas, resource rules | `game-designer` (`systems-designer`) |
| Any gameplay system | `game-designer` (`game-designer`) always |

- **Adversarial prompts**: Instruct each role to find flaws, underspecifications, and failures rather than validate (`game-designer`: test delivery against Section B Player Fantasy; `systems-designer`: boundary-test min/max formula inputs for negatives/div-zero/infinity; `qa-lead`: reject untestable criteria and propose concrete rewrites).
- **Senior synthesis**: After all specialists return, spawn `creative-director` to synthesize findings and issue overall verdict. Surface every disagreement explicitly with `[role]` attribution — never hide conflicts.

## Phase 4: Output Review (Read-Only)

Output sections:
- `Design Review: [Title]` (`Specialists consulted`, `Re-review`)
- `Completeness: [X/N sections present]` (where **N** is the count **required at resolved tier**, NEVER hardcoded `/8`; list advisory gaps separately)
- `Dependency Graph` (`exists` vs `NOT FOUND`)
- `Required Before Implementation` (blocking, source-tagged)
- `Recommended Revisions` (advisory, source-tagged)
- `Specialist Disagreements`
- `Nice-to-Have`
- `Senior Verdict [creative-director]`
- `Scope Signal`: `S` (<3 deps, 0 formulas/ADRs) / `M` (1-2 formulas, 3-6 deps) / `L` (3+ formulas, ADR likely) / `XL` (5+ deps, multiple ADRs)
- `Verdict: [APPROVED / NEEDS REVISION / MAJOR REVISION NEEDED / NOT ASSESSED]`
  - **`NOT ASSESSED`** ranks ABOVE `APPROVED` and BELOW revision verdicts: emit when target doc is absent/unreadable/empty or a required dependency doc is missing so criteria cannot run (name missing item and producing skill).

## Phase 5: Closing Interactions & Receipt Stamp

- **If `NEEDS REVISION` / `MAJOR REVISION NEEDED`**:
  - Prompt `[A] Revise GDD now` / `[B] Stop — revise in separate session` / `[C] Accept as-is (only if advisory only)`.
  - On `[A]`: group any open design decisions into one multi-tab prompt first, apply edits, present summary table, then show post-revision prompt (`[A] Re-review in a fresh session (Recommended)` / `[B] Accept revisions and mark Approved` / `[C] Move to next system` / `[D] Stop`). Remind user above ~50% context to start a fresh session before full re-review.
  - Separate confirmations for updating `design/gdd/systems-index.md` (`In Review` / `Approved`) and appending `design/gdd/reviews/[doc-name]-review-log.md`.
- **If `APPROVED`**: Batch tracking updates with multi-select prompt (`Update systems-index.md to Approved` + `Append approval entry to review log`).
- **Review-log receipt format**: Always include hash output from:
  ```bash
  python .ags/cli.py check receipts hash "[target-doc-path]" [design/registry/entities.yaml if exists]
  ```
  (Include hashes even on failed reviews so unchanged failed docs skip redundant re-reviews.)
- **Final closing prompt**: Dynamically inspect `systems-index.md` and `design/gdd/` to offer only valid next options (`ags-design-review` other unapproved GDD, `ags-design-review consistency`, `ags-design-review review-all` if >=2 GDDs, `ags-gdd design-system [next-system]`, `Stop here`).
