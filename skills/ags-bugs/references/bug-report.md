# Bug Report Lifecycle (`ags-bugs report|analyze|verify|close`)

Handles structured bug filing, proactive static defect scanning, fix verification, and audited bug closure under `production/qa/bugs/`.

**Output:** `production/qa/bugs/BUG-[NNNN].md`

---

## 1. Parse Sub-Mode

- **`report [description]`** (default when description provided): draft a structured report from a bug description (prompt user if blank).
- **`analyze [path]`**: scan target file(s) for potential defects and produce a report per finding.
- **`verify [BUG-ID]`**: confirm a reported fix actually resolves the bug before closure.
- **`close [BUG-ID]`**: record closure after `Verified Fixed` confirmation.

---

## 2. Mode Workflows

### A. Description Mode (`report`)
1. Extract what broke, when it occurs, reproduction steps, and expected vs. actual behavior.
2. Search the resolved code root (`src/` Godot, `Assets/` Unity, `Source/<Module>/` Unreal) to locate likely affected files and related systems. (If code root is unresolved, record `Likely affected files: NOT ASSESSED — code root unresolved`.)
3. Draft `BUG-[NNNN]` using the schema below.

> **Priority Ladder Parity:** `Priority` labels MUST match `references/bug-triage.md` exactly (`P1-Fix this sprint`, `P2-Fix soon`, `P3-Backlog`, `P4-Won't fix`). Never write `P4-Wishlist` — `P4` means accepted risk / deferred (`Won't fix`), not a feature wishlist.

```markdown
# Bug Report

## Summary
**Title**: [Concise, descriptive title]
**ID**: BUG-[NNNN]
**Severity**: [S1-Critical / S2-Major / S3-Minor / S4-Trivial]
**Priority**: [P1-Fix this sprint / P2-Fix soon / P3-Backlog / P4-Won't fix]
**Status**: Open
**Reported**: [Date]
**Reporter**: [Name]

## Classification
- **Category**: [Gameplay / UI / Audio / Visual / Performance / Crash / Network]
- **System**: [Affected game system]
- **Frequency**: [Always / Often (>50%) / Sometimes (10-50%) / Rare (<10%)]
- **Regression**: [Yes / No / Unknown — was this working before?]

## Environment
- **Build**: [Version or commit hash]
- **Platform**: [OS, hardware if relevant]
- **Scene/Level**: [Where in the game]
- **Game State**: [Relevant state — inventory, quest progress, etc.]

## Reproduction Steps
**Preconditions**: [Required state before starting]

1. [Exact step 1]
2. [Exact step 2]
3. [Exact step 3]

**Expected Result**: [What should happen]
**Actual Result**: [What actually happens]

## Technical Context
- **Likely affected files**: [List of files from codebase search]
- **Related systems**: [Involved systems]
- **Possible root cause**: [If identifiable]

## Evidence
- **Logs**: [Relevant log output]
- **Visual**: [Description or link to screenshot/capture]

## Related Issues
- [Related bugs or design documents]

## Notes
[Additional context]
```

### B. Analyze Mode (`analyze [path]`)
1. Read target file(s) at `[path]`.
2. Check for null/uninitialized references, off-by-one bounds, race conditions / async ordering issues, unhandled edge cases, resource leaks, and invalid state transitions.
3. Generate one structured bug report per potential bug with its likely trigger scenario and recommended fix.

### C. Verify Mode (`verify [BUG-ID]`)
Read `production/qa/bugs/[BUG-ID].md` and extract reproduction steps and expected result:
1. **Inspect root-cause path**: search the resolved code root to verify whether the defective code path was fixed or changed.
2. **Run system tests**: if the bug's system has tests under `tests/`, run them via shell and record pass/fail.
3. **Regression scan**: search the codebase for other occurrences of the same bug pattern.

Assign verification verdict:
- **`VERIFIED FIXED`**: reproduction path resolved and related tests pass.
- **`STILL PRESENT`**: defect reproduces or fix incomplete.
- **`CANNOT VERIFY`** (`NOT ASSESSED` equivalent): automated checks inconclusive or runner/code-root unavailable; manual playtest required.

Prompt per `modes.automation` to update `Status:` in `production/qa/bugs/[BUG-ID].md` (`Verified Fixed` / `Still Present` / `Cannot Verify`).
- If `STILL PRESENT`: reopen `Status: Open` and suggest `ags-release hotfix [BUG-ID]`.

### D. Close Mode (`close [BUG-ID]`)
Read `production/qa/bugs/[BUG-ID].md`. **Verify `Status` is `Verified Fixed`.**
If status is anything else, STOP:
`"Bug [BUG-ID] must be Verified Fixed before closing. Run ags-bugs verify [BUG-ID] first."`

Append closure record and update top-level `**Status**: Open` to `**Status**: Closed`:

```markdown
## Closure Record
**Closed**: [date]
**Resolution**: Fixed — [one-line summary of change]
**Fix commit / PR**: [if known]
**Verified by**: test-engineer
**Closed by**: [user]
**Regression test**: [test file path, or "Manual verification"]
**Status**: Closed
```

Confirm update per `modes.automation`. Check `production/qa/bug-triage-*.md` — if `[BUG-ID]` appears in an open triage report, remind user to run `ags-bugs triage` to refresh open counts.

---

## 3. Write & Next Steps

Confirm writing `production/qa/bugs/BUG-[NNNN].md` per `modes.automation` (verdict **`COMPLETE`** on write, **`BLOCKED`** if declined).
- **After filing**: run `ags-bugs triage`; if `S1` or `S2`, run `ags-release hotfix [BUG-ID]`.
- **After developer fixes**: run `ags-bugs verify [BUG-ID]` (never mark closed without verification).
- **After `VERIFIED FIXED`**: run `ags-bugs close [BUG-ID]`, then `ags-bugs triage` and `ags-qa regression-suite update` if a regression test was added.
