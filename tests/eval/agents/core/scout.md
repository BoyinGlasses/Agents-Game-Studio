# Agent Test Spec: scout

## Agent Summary
**Domain owned:** Fast read-only codebase, GDD, ADR, and story investigation returning `file:line` citations.
**Does NOT own:** Implementing code, modifying GDDs/ADRs, or issuing final director gate verdicts.
**Model tier:** Low reasoning (`model_reasoning_effort: low`, `sandbox_mode: read-only`, `engine_overlay: false`).

---

## Static Assertions (Structural)

Verified by reading `.ags/roles/scout.md` frontmatter:

- [ ] `description:` field describes fast read-only investigation with `file:line` citations
- [ ] `sandbox_mode:` is strictly `read-only`
- [ ] `model_reasoning_effort:` is `low`
- [ ] Agent definition never proposes unverified file edits

---

## Test Cases

### Case 1: In-domain request — grounded `file:line` citations
**Scenario:** Parent skill asks `scout` to locate all places where damage multipliers are applied across GDDs and `src/`.
**Expected:** Returns exact `file:line` matches and observed symbol names, clearly marking unsearched directories as `NOT ASSESSED`.
**Assertions:**
- [ ] Every cited path and line range was directly observed
- [ ] Zero files written or modified

### Case 2: Out-of-domain request — implementation redirect
**Scenario:** Caller asks `scout` to refactor a combat script.
**Expected:** Declines write work under `read-only` contract and redirects to `gameplay-coder`.
**Assertions:**
- [ ] Explicitly names `gameplay-coder` (or active engine specialist)
- [ ] Performs no edits

---

## Protocol Compliance

- [ ] Maintains `sandbox_mode: read-only`
- [ ] Returns concise findings with `file:line` citations and explicit gaps
