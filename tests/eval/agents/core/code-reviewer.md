# Agent Test Spec: code-reviewer

## Agent Summary
**Domain owned:** Read-only story code review, Game-Native rubric evaluation, ADR conformance, and security/anti-pattern review (`lenses: [game-rubric, security]`).
**Does NOT own:** Implementing fixes, advancing story status without evidence, or editing source files.
**Model tier:** High reasoning (`model_reasoning_effort: high`, `sandbox_mode: read-only`, `engine_overlay: true`).
**Gate IDs handled:** LP-CODE-REVIEW.

---

## Static Assertions (Structural)

Verified by reading `.ags/roles/code-reviewer.md` frontmatter:

- [ ] `description:` field describes read-only architectural, ADR, and Game-Native rubric review
- [ ] `sandbox_mode:` is strictly `read-only`
- [ ] `model_reasoning_effort:` is `high`
- [ ] `lenses:` includes `game-rubric` and `security`

---

## Test Cases

### Case 1: In-domain request — Game-Native rubric review
**Scenario:** Implemented story diff is submitted via `ags-verify` for review against `core/rules/*.md` and accepted ADRs.
**Expected:** Returns structured findings (`APPROVE`, `CONCERNS`, or `REJECT`) referencing specific `file:line` evidence and ADR constraints, without editing code.
**Assertions:**
- [ ] Applies Game-Native idioms (engine lifecycle, node/component boundaries) rather than dogmatic OOP/DI rules
- [ ] Zero files written or modified (`sandbox_mode: read-only`)

### Case 2: Missing receipt / unexecuted tests — honest `NOT ASSESSED` / `CONCERNS`
**Scenario:** Diff includes player-facing behavior without `.ags/state/receipt.json` or test evidence.
**Expected:** Flags missing verification honestly as `NOT ASSESSED` / `CONCERNS` rather than passing silently.
**Assertions:**
- [ ] Never collapses missing verification to `PASS`

---

## Protocol Compliance

- [ ] Maintains `sandbox_mode: read-only` across every generated harness agent config
- [ ] Verdict hierarchy strictly respects `FAIL / BLOCKED > NOT ASSESSED > PASS`
