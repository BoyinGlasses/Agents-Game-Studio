# Sub-Mode: Patch Notes (`ags-release patch-notes`)

Generates player-facing patch notes from internal changelogs, sprint records, balance docs, and verified game git history.

## Provenance Check (Mandatory Before Gathering History)

Confirm git commits describe THIS game before using git history:
1. Sample `git log --oneline -20`.
2. Classify every commit individually as:
   - **Game**: mechanics, content, balance, art, audio, UI, or game bug fixes.
   - **Framework / maintenance**: skills, hooks, roles, rules, CI, test harnesses, or framework docs (exclude from player copy; do not stop merely because maintenance commits exist).
   - **Unclear**: treat as Framework / maintenance.
3. Corroborate Game commits against `design/` and resolved code root (`src/` / `Assets/` / `Source/`).
4. Decide:
   - `>= 1` Game commit belonging to this game -> proceed using ONLY those commits and state `used [X] of [Y] commits`.
   - `0` Game commits (or commits describe an unrelated product) -> **Hard Stop (`BLOCKED`)**: state what git history describes and request the correct history or explicit change list.

## Phase 1: Parse Arguments

- `version`: release version (e.g., `1.2.0`). Ask the user if omitted.
- `--style`: `brief` | `detailed` (default) | `full` (adds Developer Commentary).

## Phase 2: Gather Change Data & Style

1. **Sources** (in priority order):
   - Internal changelog `production/releases/[version]-changelog.md`
   - `docs/CHANGELOG.md` entry for `[version]`
   - `git log` between previous release tag and target tag/`HEAD`
   - Sprint retrospectives in `production/sprints/`, balance docs in `design/balance/`, QA bug fix records
   - **If zero changelog/git data exists**: Stop with Verdict **`BLOCKED`** and recommend running `ags-release changelog [version]` first.
2. **Tone guide detection**:
   - Check `project.yaml`, `docs/PATCH-NOTES-STYLE.md`, and `design/community/tone-guide.md` for tone/voice/style guidance.
   - Default if absent: player-friendly, non-technical, enthusiastic without hyperbole, focused on player experience.
3. **Template detection**:
   - Check `docs/patch-notes-template.md` and `.ags/templates/release-notes.md`.
   - If custom `docs/patch-notes-template.md` exists, adopt its section structure; otherwise use `.ags/templates/release-notes.md` or the selected `--style` template (`brief`, `detailed`, `full`).

## Phase 3: Categorize and Translate

Categories: **New Content**, **Gameplay Changes** (`Balance` table + `Mechanics`), **Quality of Life**, **Bug Fixes** (grouped by Combat, UI, Networking, Audio, Platform), **Performance**, **Known Issues**.

Translation rules:
- Replace internal jargon with player-visible behavior (e.g., `"Refactored damage calculation"` -> `"Improved hit detection accuracy"`).
- Strip purely internal refactoring/CI/ticket/sprint references.
- Preserve exact before -> after numbers and brief design rationale for balance changes.

## Phase 4: Generate & Review Patch Notes

- **Brief**: New / Changes (`before -> after`) / Fixes / Known Issues.
- **Detailed**: Highlights / New Content / Balance table (`Change | Before | After | Reason`) / Mechanics / Quality of Life / Bug Fixes by system / Performance / Known Issues.
- **Full**: Detailed + `## Developer Commentary` (first-person team insight into major changes).

Review pass before presenting: zero internal jargon, zero sprint/ticket/code refs, concrete balance before/after values, player-symptom bug descriptions, matched voice/tone.

## Phase 5: Save & Next Steps

1. Present completed patch notes with category change counts, excluded internal changes list, and commit provenance count (`used [X] of [Y]`).
2. Obtain explicit user confirmation before writing `docs/patch-notes/[version].md` and archiving a copy to `production/releases/[version]-patch-notes.md`.
3. **Next Skills**: `ags-release release-checklist` before publishing externally; review copy with `.ags/roles/community-manager.md` (`producer` lens).
