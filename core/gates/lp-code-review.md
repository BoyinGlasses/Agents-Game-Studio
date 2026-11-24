> Gate definition. The spawning skill passes this file's path to the director role; that role reads it — the parent session should not.

# LP-CODE-REVIEW — Lead Programmer Code Review

Core role: `code-reviewer` | Lens role: `lead-programmer` | Model effort: `high` | Domain: Implementation feasibility, coding standards, testability (domain lens invoked when code-level sign-off is needed)

**Trigger**: After a dev story is implemented (`ags-dev`, `ags-verify`), or
as part of `ags-verify`

**Context to pass**:
- Implementation file paths
- Story file path (for acceptance criteria)
- Relevant GDD section
- ADR that governs this system

**Prompt**:
> "Review this implementation against the story acceptance criteria and governing
> ADR. Does the code match the architecture boundary definitions? Are there
> violations of the coding standards or forbidden patterns? Is the public API
> testable and documented? Are there any correctness issues against the GDD rules?
> Return APPROVE, CONCERNS [specific issues], or REJECT [must be revised before merge]."

**Verdicts**: APPROVE / CONCERNS / REJECT
