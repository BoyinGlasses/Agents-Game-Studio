> Gate definition. The spawning skill passes this file's path to the director role; that role reads it — the parent session should not.

# QL-TEST-COVERAGE — QA Lead Test Coverage Review

Core role: `qa-lead` | Model effort: `high` | Domain: Test coverage completeness, QA sign-off

**Trigger**: After implementation stories are complete, before marking an epic
done, or at `ags-gate` Production → Polish

**Context to pass**:
- List of implemented stories with story types (Logic / Integration / Visual / UI / Config)
- Test file paths in `tests/`
- GDD acceptance criteria for the system

**Prompt**:
> "Review the test coverage for these implementation stories. Are all Logic stories
> covered by passing unit tests? Are Integration stories covered by integration
> tests or documented playtests? Are the GDD acceptance criteria each mapped to at
> least one test? Are there untested edge cases from the GDD Edge Cases section?
> Return ADEQUATE (coverage meets standards), GAPS [specific missing tests], or
> INADEQUATE [critical logic is untested — do not advance]."

**Verdicts**: ADEQUATE / GAPS / INADEQUATE
