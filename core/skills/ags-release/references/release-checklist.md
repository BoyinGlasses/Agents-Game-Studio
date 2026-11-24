# Sub-Mode: Release Checklist (`ags-release release-checklist`)

Explicit-invocation-only pre-release verification checklist covering codebase health, build verification, quality gates, content completeness, hardware targets, certification tier, store metadata, and launch readiness.

## Scoping & Config Rules

Scope the emitted checklist strictly to the project:
- **`project.stage`**: Items belonging to stages not yet reached are out of scope — state that explicitly instead of listing them unchecked.
- **`modes.rigor`**: At `minimal`, drop heavy process-weight items the project opted out of.
- **`platform.cert_tier`** (`none` | `itch` | `steam` | `console`):
  - **Unset is NOT `none`**: If `platform.cert_tier` is unset, ask which platform/tier is in scope. If still undeterminable, emit `### Certification: NOT ASSESSED — cert tier unknown` and explain why.
  - **`none`**: Emit NO certification checklist block — emit exactly:
    `Certification: omitted — cert_tier is 'none' (internal build, alpha or jam release).`
  - **`itch`**: Emit itch.io items only (build size, page setup, age tags, browser vs downloadable, butler channels). Zero console or Steamworks rows.
  - **`steam`**: Emit Steamworks items only (SDK, depot install, achievements, cloud saves, Steam Deck, common content rules). Zero console rows.
  - **`console`**: Emit full platform certification (TRC / XR / Lotcheck, first-party submission, trophies/achievements, parental controls, save-data corruption/full-storage/user-switching, regional age ratings).
- **Unresolved config**: If platform or stage is unknown, mark affected sections `NOT ASSESSED — platform/stage unknown` rather than emitting an unassessable multi-platform checklist.

## Phase 1: Parse Arguments

Parse target hardware platform argument: `pc` | `console` | `mobile` | `all` (default: `all`).
- **Two independent axes**: The command argument selects **hardware/device** blocks (`pc`, `console`, `mobile`); `platform.cert_tier` selects the **certification** track (`none`, `itch`, `steam`, `console`). Never emit certification blocks from the hardware argument (`all` does NOT authorize emitting all certification tracks; `console` as hardware arg does not override `cert_tier`).

## Phase 2: Load Project Context

- Read `AGENTS.md`, `project.yaml`, and `.ags/templates/release-checklist-template.md` for project context, version targets, and platform config.
- Read the latest milestone under `production/milestones/` for expected release scope.

## Phase 3: Scan Codebase Health

Resolve code root from `engine.name` (`Godot` -> `src/`, `Unity` -> `Assets/`, `Unreal` -> `Source/<Module>/`, or unambiguous single directory among `src/`, `Assets/`, `Source/`).

Always state the denominator with every count:
- Report `scanned [N] source files: [M] TODO, [M] FIXME, [M] HACK` (note locations and severity).
- If code root is unresolved, absent, or holds zero files, report `NOT ASSESSED — no source files found to scan` (never a bare `0`).
- Check test outputs or CI logs if available; if none exist, report `Test results: NOT ASSESSED — no test output or CI logs found`.

## Phase 4: Generate Release Checklist

```markdown
## Release Checklist: [Version] -- [Platform]
Generated: [Date]

### Codebase Health
- Source scan: [scanned N files: M TODO, M FIXME, M HACK | NOT ASSESSED — reason]
- Test results: [summary | NOT ASSESSED — no test output or CI logs found]

### Build Verification
- [ ] Clean build succeeds on all target platforms
- [ ] Zero compiler warnings
- [ ] All assets included and loading correctly
- [ ] Build size within budget ([target size])
- [ ] Build version number set ([version])
- [ ] Build reproducible from tagged commit

### Quality Gates
- [ ] Zero S1 (Critical) bugs
- [ ] Zero S2 (Major) bugs — or documented exceptions with producer approval
- [ ] All critical path features tested and signed off by QA
- [ ] Performance within budgets (target FPS on min spec, memory, load times, no leaks)
- [ ] No regression from previous build
- [ ] Soak test passed (4+ hours continuous play)

### Content Complete
- [ ] All placeholder assets replaced with final versions
- [ ] All TODO/FIXME in content files resolved or documented
- [ ] All player-facing text proofread
- [ ] All text localization-ready (no hardcoded strings)
- [ ] Audio mix finalized and approved
- [ ] Credits complete and accurate
```

**Hardware Device Blocks (from argument; omit certification SDK rows here):**

- **For `pc`**: Minimum/recommended specs documented; KB+M controls; controller support (Xbox, PlayStation, generic); resolution scaling (1080p, 1440p, 4K, ultrawide); windowed/borderless/fullscreen; graphics settings persistence.
- **For `console`**: Platform controller prompts; suspend/resume; user switching; graceful network loss handling; storage-full handling.
- **For `mobile`** *(storefront compliance items live here because `platform.cert_tier` models `none|itch|steam|console`)*: App store guidelines; device permissions justified; privacy policy linked; data safety/nutrition labels; touch controls across screen sizes; battery usage; background pause/resume/terminate; push permissions; IAP flow (if applicable); app size within limits.

**Certification Block (ONLY the block matching `platform.cert_tier`):**
- `none`: `Certification: omitted — cert_tier is 'none' (internal build, alpha or jam release).`
- `itch`: Build size within itch.io limits; page complete (cover art, screenshots, description); honest age/content tags; downloadable vs browser build tested; butler channel names verified.
- `steam`: Steamworks SDK integrated/tested; depot installs cleanly from fresh account; achievements; cloud saves; Steam Deck compatibility (if targeting); Steam common content rules.
- `console`: TRC/TCR/Lotcheck checklist complete; first-party submission prepared; platform trophies/achievements; parental controls; save-data rules (corruption, full storage, user switching); age ratings (ESRB, PEGI, regional).
- Unset: Ask user or emit `### Certification: NOT ASSESSED — cert tier unknown`.

**Store / Distribution & Launch Readiness (all tiers unless `none` or internal build excludes store):**
- Store metadata (short/long descriptions, feature list, PC system specs), per-platform screenshots, trailers, key art/capsules, regional age ratings (ESRB/PEGI/other), EULA & privacy policy, third-party licenses, regional pricing.
- Analytics/telemetry live, crash reporting dashboard, day-one patch status, 72h on-call schedule, community launch announcements, press/influencer keys, support FAQ, rollback plan documented.

**Go / No-Go & Sign-Offs**:
- Status: `[READY / NOT READY / NOT ASSESSED]` with rationale.
- Required sign-offs: `qa-lead`, `technical-director`, `producer`, `creative-director`.
- Mark any item backed by an absent input with `- [?]` and legend: `[?] = not assessed — the input to this check was absent`.

## Phase 5: Save & Next Steps

1. Present total items, blocker count (`FIXME`/`HACK`, open S1/S2), and unassessed `[?]` items.
2. Obtain explicit user confirmation before writing `production/releases/release-checklist-[version].md` (respecting `modes.automation`).
3. **Next Skills**: Run `ags-gate` for formal phase-gate verdict; coordinate full release execution via `ags-team release`.
