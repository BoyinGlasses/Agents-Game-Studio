# Skill Spec: ags-<name>

> **Category**: [gate | review | authoring | readiness | pipeline | analysis | team | sprint | utility]
> **Priority**: [critical | high | medium | low]
> **Spec written**: [YYYY-MM-DD]

## Skill Summary

[Describe what `ags-<name>` does, sub-modes it consolidates, inputs consumed, and outputs produced.]

---

## Static Assertions (AGS v2 Structural)

- [ ] `core/skills/ags-<name>/SKILL.md` is `<= 220` lines
- [ ] Frontmatter has strictly `name: ags-<name>` and `description: "Use when ... Do NOT use when ..."`
- [ ] Exact `##` headings present: `## Contract`, `## Preflight`, `## Phases`, `## Gate & Verdict`
- [ ] `## Preflight` runs `python .ags/cli.py preflight ags-<name>`
- [ ] `## Gate & Verdict` enforces `FAIL / BLOCKED > NOT ASSESSED > PASS`
- [ ] Zero host-specific leakage or per-file write-approval prompts (no legacy tool names, legacy host config filenames, legacy directories, or legacy skill prefixes)

---

## Director Gate & Mode Checks

- **Full mode**: [gates triggered via `.ags/gates/*.md`, e.g. `CD-PHASE-GATE`, `TD-PHASE-GATE`, `PR-PHASE-GATE`, `AD-PHASE-GATE`]
- **Lean mode**: [phase gates only per `modes.workflow` width, or skipped]
- **Solo mode**: [all director gates skipped with explicit `[GATE-ID] skipped — Solo mode` note]
- **N/A**: [if this skill never triggers director gates, explain why]

---

## Test Cases

### Case 1: Happy Path — [brief name]

**Fixture** (assumed project state):
- [file/condition 1]
- [file/condition 2]

**Expected behavior**:
1. Runs `python .ags/cli.py preflight ags-<name>`
2. [Step 2]
3. [Step 3]

**Assertions**:
- [ ] [Assertion 1]
- [ ] [Assertion 2]
- [ ] [Assertion 3]

**Case Verdict**: PASS / FAIL / NOT ASSESSED

---

### Case 2: Failure / Blocked — [brief name]

**Fixture**:
- [missing or invalid condition]

**Expected behavior**:
1. Skill detects the problem deterministically
2. Skill reports `FAIL` / `BLOCKED` (or `NOT ASSESSED` if input class could not be checked)
3. Skill does NOT proceed or fabricate a `PASS`

**Assertions**:
- [ ] Skill stops early or escalates cleanly without silent skips
- [ ] Correct blocker / `NOT ASSESSED` reason displayed

**Case Verdict**: PASS / FAIL / NOT ASSESSED

---

### Case 3: Mode Variant / Rigor Scaling — [brief name]

**Fixture**:
- [standard project state]
- [`modes.rigor`, `modes.workflow`, or `workflow_overrides.system_overrides` setting]

**Expected behavior**:
1. [Behavior adapts cleanly to resolved preflight config]

**Assertions**:
- [ ] [Mode-specific assertion]
- [ ] [Skipped checks reported honestly, never collapsed to `PASS`]

**Case Verdict**: PASS / FAIL / NOT ASSESSED

---

### Case 4: Edge Case / Story Checkpoint — [brief name]

**Fixture**:
- [boundary condition, scope change, or Player-facing vs Technical story class]

**Expected behavior**:
1. [Handles gracefully; if story workflow, pauses only at Checkpoint #1, Checkpoint #2, or scope/design/engine change]

**Assertions**:
- [ ] [Edge case handled without crash or per-file write-approval prompts]
- [ ] [For Player-facing stories: Playtest & Game Feel Tuning Card required before acceptance]

**Case Verdict**: PASS / FAIL / NOT ASSESSED

---

## Protocol Compliance

- [ ] Does not ask per-file write-approval prompts during routine approved work
- [ ] Escalates missing product decisions cleanly and preserves explicit `NOT ASSESSED` / `NOT VERIFIED` honesty
- [ ] Ends with valid AGS v2 `Next Skill:` handoff (`ags-*`)
