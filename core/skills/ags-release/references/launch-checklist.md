# Sub-Mode: Launch Checklist (`ags-release launch-checklist`)

Explicit-invocation-only multi-department launch readiness audit across code, content, QA, certification, store, legal, infrastructure, community, and launch operations.

## Scoping & Config Rules

Apply the same scoping rules as `release-checklist`:
- **`project.stage`**: Out-of-scope future-stage items noted as skipped rather than listed unchecked.
- **`modes.rigor`**: At `minimal`, drop heavy process-weight items.
- **`platform.cert_tier`** (`none` | `itch` | `steam` | `console`):
  - **Unset is NOT `none`**: Ask which platforms/tier apply; if unknown, emit `NOT ASSESSED — cert tier unknown`.
  - Branch certification rows strictly on `platform.cert_tier` (emit ONLY the matching block).
- Missing config fields force `NOT ASSESSED — platform/stage unknown` rather than guessing multi-platform rows.

## Phase 1: Parse Arguments

Accept target launch date or `dry-run` mode (`dry-run` builds the checklist without creating sign-off records or writing files).

## Phase 2: Gather Project Context

- Read `AGENTS.md` and `project.yaml` for tech stack, target platforms, and studio roles.
- Read latest milestone in `production/milestones/`.
- Read existing release checklist in `production/releases/` if present.
- Read `design/live-ops/content-calendar.md` if present.

## Phase 3: Scan Codebase & Asset Health

Resolve code root from `engine.name` (`Godot` -> `src/`, `Unity` -> `Assets/`, `Unreal` -> `Source/<Module>/`, or unambiguous single directory).

**Mandatory denominator discipline**: Every scan checks for negative conditions, so an empty/missing root produces zero hits identically to a clean repo unless gated. Report every scan line as `scanned [N] files, [M] hits` OR `NOT ASSESSED — [code root unresolved | no assets/ | directory empty]`:
1. Count `TODO`, `FIXME`, `HACK` comments and locations in resolved code root.
2. Scan for leftover debug output (`console.log`, `print()`, `Debug.Log`, `UE_LOG` debug prints) in production code.
3. Scan `assets/` (and code root) for placeholder files (`placeholder`, `temp_`, `WIP_`).
4. Scan for hardcoded test/dev values (`localhost`, test credentials, debug flags).

**Checklist box mapping**: Any item whose underlying scan returned `NOT ASSESSED` MUST be written as `- [?]` (never `- [ ]` or `- [x]`), accompanied by the legend:
`[?] = not assessed — the input to this check was absent`

## Phase 4: Generate Launch Checklist

Sections to emit:
1. **Code Readiness**:
   - Build Health: clean build on all targets, zero warnings, unit/integration tests passing, performance benchmarks met, no leaks (extended soak), build size within limits, tagged version.
   - Code Quality: `TODO` / `FIXME` (`0` required) / `HACK` (justified) counts, no debug output, no hardcoded dev/test values, production feature flags, critical-path error handling, crash reporting verified.
   - Security: no exposed API keys/credentials, encrypted save data, TLS/DTLS networking, anti-cheat (if multiplayer), server input validation (if multiplayer), privacy policy compliance.
2. **Content Readiness**:
   - Assets: placeholder art/audio replaced, audio mix approved by `audio-director` (`tech-artist`), VFX performance-verified, zero broken asset refs, naming conventions enforced.
   - Text & Localization: text proofread, zero hardcoded strings, supported locales translated/verified, UI text-fit pass complete, font glyph coverage verified, credits complete.
   - Game Content: all levels playable end-to-end, tutorial tested with new players, achievements/trophies tested, save/load across all states, difficulty balanced, end-game/credits complete.
3. **Quality Assurance**:
   - Testing: full regression passed, zero S1, zero S2 (or documented exceptions), 8+ hour soak test, multiplayer stress test (if applicable), critical paths per platform, edge cases (full storage, no network, suspend/resume).
   - Platform Certification *(ONLY the block matching `platform.cert_tier`)*:
     - `none`: `Platform Certification: omitted — cert_tier is 'none' (internal/jam release).`
     - `itch`: upload size limits, complete itch.io page, honest age/content tags, downloadable vs browser build tested.
     - `steam`: Steamworks SDK, store page/capsule/trailer/specs, fresh-account depot install, achievements, Steam common content rules.
     - `console`: TRC/TCR/Lotcheck submission, save-data compliance, controller mapping & button prompts, suspend/resume, regional age ratings (ESRB/PEGI/etc.).
     - Every tier: minimum accessibility standards met (remapping, text scaling, colorblind support).
   - Performance: min-spec target FPS, load times, memory budget, multiplayer bandwidth, zero critical-gameplay hitches.
4. **Store and Distribution**:
   - Store Pages: copy proofread, resolution-compliant screenshots, trailers, final key art/capsules, PC system specs, regional pricing, wishlist/pre-purchase active.
   - Legal: EULA finalized, privacy policy published/linked, third-party attributions, music/audio licensing, trademark/IP clearance, GDPR/CCPA consent/deletion compliance.
5. **Infrastructure**:
   - Servers *(if multiplayer/online)*: provisioned & load-tested, auto-scaling, DB backups, CDN, DDoS protection, monitoring/alerting.
   - Analytics & Monitoring: pipeline live, crash dashboard live, server dashboards live, DAU/session/retention/crash metrics tracked, critical-threshold alerts set.
6. **Community and Marketing**:
   - Community: guidelines published, moderation briefed, Discord/forum/social ready, FAQ & known issues ready, support ticketing active.
   - Marketing: launch trailer live, press/influencer keys distributed, launch social posts scheduled, launch dev update drafted, patch notes ready.
7. **Operations**:
   - Team Readiness: 72-hour post-launch on-call schedule, incident response playbook reviewed (`.ags/templates/incident-response.md`), rollback plan tested, hotfix pipeline tested (<4h emergency turnaround), comms escalation plan.
   - Day-One Plan: day-one patch status, server unlock/go-live runbook, dashboards bookmarked, launch war room active.
8. **Go / No-Go Decision**:
   - Overall Status: `[READY / NOT READY / CONDITIONAL / NOT ASSESSED]`
   - Blocking items, Conditional items, Sign-offs (`creative-director`, `technical-director`, `qa-lead`, `producer`, `release-manager`).

## Phase 5: Save & Next Steps

- Summarize total items, blocking count, conditional count, incomplete departments, and any `[?]` unassessed items.
- Unless in `dry-run` mode, request explicit user confirmation before writing `production/releases/launch-checklist-[date].md`.
- **Next Skills**: Run `ags-gate` for formal `PASS`/`CONCERNS`/`FAIL`/`NOT ASSESSED` gate verdict; coordinate sign-offs with `ags-team release`.
