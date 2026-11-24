# Sub-Mode: Changelog (`ags-release changelog`)

Generates both an internal engineering changelog and a player-facing changelog from verified game git history, sprint data, and design documents.

## Provenance Check (Mandatory Before Gathering History)

Do not assume the current git log belongs to the game:

1. Inspect recent commits and tags from the game project root:
   ```bash
   git log --oneline -30
   git tag --list --sort=-v:refname
   ```
   Read the latest five tags.
2. **Classify every commit subject individually** into:
   - **Game**: mechanics, content, balance, art, audio, UI, or bugs in those systems.
   - **Framework / maintenance**: commits touching skills, hooks, roles, rules, CI, test harnesses, or framework documentation. **Exclude from release copy; do not stop merely because maintenance commits exist.**
   - **Unclear**: treat as Framework / maintenance (never generate player-facing copy from an ambiguous commit).
3. **Corroborate**: Verify Game commit subjects describe systems actually present in `design/` or the resolved code root (`src/` / `Assets/` / `Source/`). If commits describe an unrelated product not in `design/` or game code, stop.
4. **Decide**:
   - `>= 1` Game commit belonging to this game -> proceed using ONLY Game commits, and state the ratio explicitly (`used [X] of [Y] commits`).
   - `0` Game commits (or wrong-product commits) -> **Hard Stop (`BLOCKED`)**: inform the user what the git history actually describes and request the right repository range or an explicit change list.

## Phase 1: Parse Arguments

- Target version (git tag) or sprint number (date range).
- Verify git working tree: `git rev-parse --is-inside-work-tree`. If not a git repo, inform the user and abort cleanly.

## Phase 2: Gather Change Data

- If tags exist: `git log --oneline [last-tag]..HEAD`.
- If no tags exist: bound explicitly with `git log --oneline -n 100` (never run an unbounded full log; if 100 commits do not reach far enough back, stop and ask for a start ref).
- Read relevant sprint reports in `production/sprints/` and completed GDDs in `design/gdd/`.

## Phase 3: Categorize Changes & Audit Task Traceability

Classify each Game commit into:
- **New Features**: new gameplay systems, modes, or content
- **Improvements**: enhancements, UX polish, noticeable performance gains
- **Bug Fixes**: corrections to broken behavior
- **Balance Changes**: tuning of gameplay values, difficulty, economy
- **Known Issues**: acknowledged unresolved issues
- **Miscellaneous**: other valid game changes or ambiguous game commits

Check each commit message for a task/story/bug ID (`[STORY-123]`, `TR-...`, `#NNN`, `BUG-NNN`). Count commits lacking a task ID and report `Commits without task reference: [N]` under Metrics.

## Phase 4: Generate Internal Changelog

Use `.ags/templates/changelog-template.md` structure:
- Header: Version, Date, Sprint(s), Commit count & range (`[first-hash]..[last-hash]`).
- Sections: `New Features` (system, commits, owner, GDD link), `Improvements`, `Bug Fixes` (`BUG-ID`, root cause, fix, commits, owner), `Balance Changes` (`old -> new`, design intent, owner), `Technical Debt / Refactoring`, `Miscellaneous`, `Known Issues` (severity, ETA), `Metrics` (total commits, files changed, lines added/removed, commits without task reference).

## Phase 5: Generate Player-Facing Changelog

Translate into player language (zero internal file paths, code identifiers, developer names, or ticket IDs):
- `New Features`: player experience focus
- `Improvements`: concrete player benefit without jargon
- `Bug Fixes`: describe player-visible symptom fixed
- `Balance Changes`: clear before/after values plus design rationale
- `Known Issues`: honest player-terms summary + workaround if any

## Phase 6: Output & Save

1. Present both changelogs (internal primary + player-facing draft) and commit provenance count (`used [X] of [Y]`).
2. Check whether `docs/CHANGELOG.md` already exists. Ask the user before writing:
   - `[A]` Append new entry at top (newest first — recommended when `docs/CHANGELOG.md` already exists)
   - `[B]` Overwrite `docs/CHANGELOG.md`
   - `[C]` Do not write file (user will copy manually)
3. Archive a versioned internal copy at `production/releases/[version]-changelog.md` if confirmed so `ags-release patch-notes` can consume it directly.

## Verdicts & Next Steps

- **CHANGELOG WRITTEN / COMPLETE**: Generated (and saved if approved).
- **BLOCKED**: Non-git directory or zero verified Game commits in provenance check.
- **Next Skills**: `ags-release patch-notes [version]` for styled public notes; `ags-release release-checklist` before publishing externally.
