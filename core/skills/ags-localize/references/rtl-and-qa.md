# Localization: Engine L10n Workflows, RTL Check & Localization QA

Detailed guides for engine-specific localization checks, `rtl-check` (plus CJK/BiDi layout verification), and `qa` localization sign-off.

---

## Engine Localization Workflows

Determine the engine from `engine.name` in `project.yaml`. If `engine.name` is unset or `null`, skip engine-specific checks and record `Engine localization check: NOT ASSESSED — no engine configured (engine.name unset in project.yaml)`.

Consult `.ags/roles/<engine>-specialist.md` grounded in `docs/engine-reference/<engine>/` for version-pinned behavior (never assert unverified engine APIs from memory; flag uncovered details as `NOT SOURCEABLE — <api> not covered by docs/engine-reference/<engine>/`):

- **Godot** (`docs/engine-reference/godot/breaking-changes.md`, `current-best-practices.md`):
  - Use built-in CSV plural form support and Context columns rather than legacy workarounds where Godot 4.6+ supports them.
  - Check `tr()` / `Tr()` localization calls (including Godot 4.6 C# automatic string extraction where applicable).
  - Inspect `Control.layout_direction` on UI scenes and `HBoxContainer` container mirroring.
  - Leverage editor live translation preview during UI text-fit verification.
- **Unity** (`docs/engine-reference/unity/` + `.ags/roles/unity-ui-specialist.md`):
  - Delegate Unity Localization / StringTable / RTL TextMeshPro verification to `unity-ui-specialist` / `unity-specialist`, checking font asset fallbacks and `RTL Support` setup against `docs/engine-reference/unity/`.
- **Unreal** (`docs/engine-reference/unreal/` + `.ags/roles/ue-umg-specialist.md`):
  - Delegate `LOCTEXT` / String Table / ICU pluralization / UMG text direction flag checks to `ue-umg-specialist` / `unreal-specialist` against `docs/engine-reference/unreal/`.

---

## Sub-Mode: `rtl-check`

Validates right-to-left languages (Arabic, Hebrew, Persian, Urdu) across layout, typography, BiDi string assembly, and directional assets:

1. **Layout Mirroring**:
   - Check engine RTL flags in scene/UI files (`Control.layout_direction`, Unity `RTL Support`, Unreal text direction flags).
   - Inspect horizontal layout containers (`HBoxContainer`, `LinearLayout`, `HorizontalBox`) and anchored HUD bounds for hardcoded left/right coordinates that fail to mirror.
   - Verify progress bars, health bars, sliders, and directional navigation flow mirror appropriately.
2. **Text Rendering & BiDi**:
   - Verify loaded fonts contain full Arabic/Hebrew glyph ranges and fallback chains.
   - Verify connected Arabic shaping/ligatures render intact (not disconnected/reversed glyphs).
   - Verify Eastern Arabic numeral requirements where specified by locale conventions.
   - Check mixed LTR/RTL embedded strings (e.g., English brand names or numbers inside Arabic sentences) use proper Unicode BiDi isolation so punctuation/numbers do not invert.
3. **String Assembly**:
   - Search resolved code root for `+` string concatenation near UI or dialogue logic (report denominator `scanned [N] files`, or `NOT ASSESSED — code root unresolved`).
   - Verify `{placeholder}` ordering can freely reverse across translated grammar.
4. **Directional Assets**:
   - Flag asymmetric icons, arrows, or chevrons needing mirrored RTL variants.
   - Flag text-baked textures requiring locale variants.

Classify findings as `BLOCKING` (unreadable or unusable UI) vs `ADVISORY` (cosmetic polish). Request user confirmation before writing `production/localization/rtl-check-[date].md`.

---

## Sub-Mode: `qa` (Localization QA Cycle)

Playthrough-based pre-ship quality check distinct from automated string completeness (`validate`).

1. **Inputs**: target shipping locale(s), screen/flow inventory (`design/gdd/` or `ags-design-review content-audit`), latest `ags-localize validate` report, and `production/localization/cultural-review-*.md` (if present).
2. **Delegate to `.ags/roles/localization-lead.md`** (`producer` core role, supported by `test-engineer` and `art-ux-director`) to execute and verify:
   - **Functional string display**: zero truncation, missing keys, unrendered `{tokens}`, or encoding corruption in-game.
   - **UI overflow & text fitting**: check translated buttons, headers, tooltips, and CJK/expanded text bounds on all target resolutions.
   - **Contextual accuracy**: sample >= 10% of strings in-game for natural phrasing, speaker tone, and grammar.
   - **Cultural compliance**: confirm all `BLOCKING` items from cultural review are resolved (if cultural review never ran for a commercial release, record `Cultural review: NOT ASSESSED`).
   - **VO & subtitle sync**: if dubbed VO exists, verify timing/lip-sync and subtitle durations.
   - **Platform certification text**: verify regional age-rating strings and legal notices (ESRB / PEGI / CERO / etc.) when `platform.cert_tier` requires them.
3. **Per-Locale Verdict Format**:

```markdown
## Localization QA Verdict — [Locale]
**Status**: NOT ASSESSED / PASS / PASS WITH CONDITIONS / FAIL
**Reviewed by**: localization-lead
**Date**: [date]

### Findings
| ID | Area | Description | Severity | Status |
|---|---|---|---|---|
| LOC-001 | UI Overflow | [Example finding] | BLOCKING | Open |

### Conditions (if PASS WITH CONDITIONS)
- [Condition required before ship]

### Sign-Off
- [ ] All BLOCKING findings resolved
- [ ] Producer approves shipping [Locale]
```

**Strict Verdict Preconditions**:
- If playthrough evidence, string tables, or runtime build verification is missing for a locale, verdict is **`NOT ASSESSED`** — never report `PASS`.
- **`FAIL`** blocks release **for that failing locale only**; other passing locales may ship independently.
- **`PASS` or `PASS WITH CONDITIONS`** is required for every shipping locale before `ags-gate` (Polish -> Release).

4. Request user confirmation before writing `production/localization/loc-qa-[locale]-[date].md`. Include QA report paths when invoking `ags-gate`.
