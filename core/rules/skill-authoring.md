---
paths:
  - ".agents/skills/**"
  - ".ags/roles/**"
  - ".ags/gates/**"
---

# Skill and Gate Authoring Rules

**A check that cannot report that it did not run is not a check.**

A step that fails to run must never produce output indistinguishable from a step that ran and found nothing. Every skill, check, and gate in AGS enforces five obligations:

## The Five Obligations

1. **Include a `NOT ASSESSED` verdict above pass and below failure.**
   - A vocabulary with only pass/fail forces missing inputs into false passes.
   - Rank `NOT ASSESSED` above `PASS` / `APPROVED` (unverified scope has not passed) and below `FAIL` / `REJECT` / `BLOCKED` (never bury known failures behind access gaps). State the exact missing input or unmet precondition.

2. **Never default an absent config key to the permissive branch.**
   - Verify whether any writer sets a config key before defaulting. An absent engine, code root, or `platform.multiplayer` setting must not silently skip a check and emit clean output.

3. **Every skipped step announces itself in the output artifact.**
   - If an agent, engine specialist, lens, or check category did not run (due to `team.size`, `review_mode`, missing engine, or missing input), name what was skipped and why in the generated report.

4. **Never assert unsourced engine facts — wire gaps to the verdict.**
   - Pin engine API claims against `docs/engine-reference/**`. When missing, write `NOT SOURCEABLE — <what> is not covered by <path>` and prevent a clean pass when sourced inputs are absent.

5. **Gates derive their covered set instead of trusting stale allowlists.**
   - Derive skills, roles, gates, and templates dynamically from repo directories so new files cannot ship unguarded. Assert distinctive tokens rather than ambiguous substrings, and **verify every gate fails on a broken fixture before trusting it**.

## Self-Check

Before finalizing any skill or gate: **"If this check silently failed to execute, would its output look identical to a clean pass?"** If yes, it is unfinished.
