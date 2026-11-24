# Agent Spec: [role-name]

> **Role Kind**: [core-readonly | core-write | engine | lens]
> **Engine Pack**: [none | godot | unity | unreal]
> **Spec written**: [YYYY-MM-DD]

## Role Summary

[Describe this role's domain, `sandbox_mode`, `model_reasoning_effort`, attached `lenses`, and what it owns vs escalates.]

**Domain**: [files/directories/decisions owned]
**Sandbox Mode**: [`read-only` | `workspace-write`]
**Escalates on**: [`STATUS: BLOCKED_ON_DECISION` triggers]

---

## Static Assertions (AGS v2)

- [ ] Role file exists under `core/agents/{core,engines/<engine>,lenses}/[role-name].md`
- [ ] Frontmatter has `name`, `description`, `sandbox_mode`, `model_reasoning_effort`
- [ ] Reviewer roles (`scout`, `creative-director`, `technical-director`, `qa-lead`, `code-reviewer`) strictly set `sandbox_mode: read-only`
- [ ] Body is concise (`<= 2.5 KB` for core roles), uses flat 1-hop escalation (`STATUS: BLOCKED_ON_DECISION`), and contains zero per-file write-approval prompts or host-specific leakage

---

## Test Cases

### Case 1: In-Domain Request — [brief name]

**Fixture**:
- [relevant project state and `docs/engine-reference/` context if `engine_overlay: true`]

**Expected behavior**:
1. Role handles task within its domain
2. Produces structured output or implementation (if `workspace-write`) / `file:line` citations & verdict (if `read-only`)

**Assertions**:
- [ ] Respects `sandbox_mode` boundary
- [ ] Cites observed `file:line` or `VERSION.md` entries when applicable

**Case Verdict**: PASS / FAIL / NOT ASSESSED

---

### Case 2: Out-of-Domain / Missing Decision — [brief name]

**Fixture**:
- [request outside domain or missing product decision]

**Expected behavior**:
1. Emits `STATUS: BLOCKED_ON_DECISION` or redirects to the owning core/engine role
2. Makes zero silent assumptions or out-of-domain edits

**Assertions**:
- [ ] Never silently guesses product/architecture decisions
- [ ] Correct target role named

**Case Verdict**: PASS / FAIL / NOT ASSESSED

---

### Case 3: Gate / Review Verdict — [brief name]

**Fixture**:
- [artifact or diff submitted for review]

**Expected behavior**:
1. Evaluates against `.ags/gates/` or `.ags/rules/`
2. Emits canonical verdict (`APPROVE` / `CONCERNS` / `REJECT` or `ADEQUATE` / `INADEQUATE`), marking missing verification `NOT ASSESSED`

**Assertions**:
- [ ] Verdict precedes any approval; missing checks stay `NOT ASSESSED`

**Case Verdict**: PASS / FAIL / NOT ASSESSED
