# Playtest Report (`ags-qa playtest-report`)

Generates a blank playtest report template or structures raw playtest notes into actionable findings, routes follow-ups across skills, and optionally runs `CD-PLAYTEST` review.

**Output:** `production/qa/playtests/playtest-[date]-[tester].md`

---

## Phase 1: Parse Arguments

- **`new`**: generate a blank structured playtest report template.
- **`analyze [path]`**: read raw playtest notes at `[path]`, cross-reference `design/gdd/` (or `design/game-brief.md`), fill the template, and flag observations that conflict with design intent.

---

## Phase 2: Playtest Report Structure

1. **Session Info**: Date, Build (version/commit), Duration, Tester, Platform (`PC / Console / Mobile`), Input Method (`KB+M / Gamepad / Touch`), Session Type (`First time / Returning / Targeted test`).
2. **Test Focus**: features or flows under test.
3. **First Impressions (First 5 minutes)**: understood goal? (`Yes/No/Partially`), understood controls?, emotional response (`Engaged/Confused/Bored/Frustrated/Excited`), notes.
4. **Gameplay Flow**: What worked well, Pain points (`High/Medium/Low`), Confusion points, Moments of delight.
5. **Bugs Encountered**: table (`# | Description | Severity | Reproducible`).
6. **Feature-Specific Feedback**: per feature (`Understood purpose?`, `Found engaging?`, `Suggestions`).
7. **Quantitative Data** *(if available)*: Deaths + locations, Time per area, Items used, Features discovered vs. missed.
8. **Overall Assessment**: Would play again? (`Yes/No/Maybe`), Difficulty (`Too Easy / Just Right / Too Hard`), Pacing (`Too Slow / Good / Too Fast`), Session length preference (`Shorter / Good / Longer`).
9. **Top 3 Priorities** from the session.

---

## Phase 3: Action Routing

Group all findings into four buckets and route each:
- **Design changes needed** (fun breaks, player confusion, GDD conflicts) -> `ags-design-review propagate [path]` (and re-run `ags-design-review` after GDD edits).
- **Balance adjustments** (wrong numbers, pacing spikes/flats) -> `ags-design-review balance [system]`.
- **Bug reports** (reproducible defects) -> `ags-bugs report` (and `ags-bugs triage` after fixes).
- **Polish items** (non-blocking feel/friction issues) -> `production/` polish backlog.

---

## Phase 3b: Creative Director Player Experience Review (`CD-PLAYTEST`)

Apply `modes.review_mode` (including inline `--review` override):
- `solo`: skip (`"CD-PLAYTEST skipped — Solo mode."`), proceed to Phase 4.
- `lean`: skip (`"CD-PLAYTEST skipped — Lean mode."`), proceed to Phase 4.
- `full`: delegate to `creative-director` passing gate file path `.ags/gates/cd-playtest.md` (do **not** read the gate file in the parent context — instruct `creative-director` to read it first), plus:
  - Structured playtest report content
  - Game pillars and core fantasy from `design/gdd/game-concept.md`, else `design/game-brief.md` (at `minimal`). **If neither file exists**, explicitly pass: `"No pillars available — assess against the hypothesis alone."` (never omit pillar context silently or let the reviewer invent pillars).
  - Specific hypothesis under test.

Present the `creative-director` verdict before saving:
- `APPROVE`: record approval in report.
- `CONCERNS`: add `## Creative Director Assessment` capturing verdict and concerns; prompt user (`Revise flagged items` / `Accept and proceed` / `Discuss further`).
- `REJECT`: add `## Creative Director Assessment` with blockers; treat overall gate outcome as `FAIL` / redesign needed before further playtesting.

---

## Phase 4: Save & Next Steps

Confirm writing `production/qa/playtests/playtest-[date]-[tester].md` per `modes.automation`, creating the directory if needed. Act on the highest-priority finding bucket first (`ags-design-review`, `ags-bugs`, or `ags-release`).
