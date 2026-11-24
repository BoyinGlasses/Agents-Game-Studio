---
name: ags-localize
description: "Use when scanning hardcoded strings, extracting string tables, validating translations, tracking locale coverage, running pseudolocalization or RTL/CJK/pluralization checks, preparing translator briefs, auditing cultural sensitivity, managing localized VO, enforcing string freeze, or running localization QA. Do NOT use when drafting original dialogue/lore -> ags-team, authoring UX specs -> ags-art-ux, or verifying general story code -> ags-verify."
---

# Localization Pipeline

End-to-end localization pipeline from string extraction and freeze enforcement through pseudolocalization, cultural review, VO management, RTL/CJK/pluralization checks, and per-locale QA sign-off.

## Contract
- **Inputs**: Sub-mode (`scan` | `extract` | `validate` | `status` | `brief` | `cultural-review` | `vo-pipeline` | `rtl-check` | `freeze` | `qa`), target locale/sub-task, `project.yaml`, `assets/data/strings/`, `design/`, and resolved code root.
- **Roles**: `producer`, `gameplay-coder`, `art-ux-director`, `tech-artist`, `test-engineer`, `godot-specialist`, `unity-specialist`, `unreal-specialist`
- **Outputs**: Read-only scan/validation/coverage reports, `assets/data/strings/strings-en.json` diffs, `production/localization/` deliverables (briefs, cultural reviews, VO scripts, RTL checks, freeze status, per-locale QA verdicts).
- **Verification**: Run `python .ags/cli.py verify` after code or string-table changes; verify engine l10n workflows against `docs/engine-reference/<engine>/` and `ags-qa` / `ags-gate` requirements.
- **Next Skill**: `ags-gate`, `ags-art-ux`, `ags-team`, or `ags-release`.

## Preflight

Run config resolution once before Phase 1:

```bash
python .ags/cli.py preflight ags-localize
```

Inspect `engine.name`, `modes.automation`, `modes.rigor`, `platform.cert_tier`, and `project.stage`. Derive the code root from `engine.name` (`Godot` -> `src/`, `Unity` -> `Assets/`, `Unreal` -> `Source/<Module>/`, or unambiguous single directory among `src/`, `Assets/`, `Source/`). If unresolved, never default to `src/` — emit `NOT ASSESSED — code root unresolved`.

## Phases

### Phase 0: Sub-Mode Dispatch

Parse the sub-mode from arguments. If missing or unrecognized, print the 10 valid sub-modes and stop with Verdict **FAIL**. Read the corresponding reference guide before executing:

| Sub-mode | Reference | Write Behavior |
|---|---|---|
| `scan` | `references/extraction-and-validation.md` | Read-only |
| `extract` | `references/extraction-and-validation.md` | Confirms diff to `assets/data/strings/strings-en.json` |
| `validate` | `references/extraction-and-validation.md` | Read-only (incl. pseudolocalization, CJK, plurals) |
| `status` | `references/extraction-and-validation.md` | Read-only coverage matrix |
| `freeze` | `references/extraction-and-validation.md` | Confirms write to `production/localization/freeze-status.md` |
| `brief` | `references/brief-cultural-vo.md` | Confirms `production/localization/translator-brief-[locale]-[date].md` |
| `cultural-review` | `references/brief-cultural-vo.md` | Confirms `production/localization/cultural-review-[date].md` |
| `vo-pipeline` | `references/brief-cultural-vo.md` | Confirms `vo-scripts-[locale]-[date].md` (`script`); others read-only |
| `rtl-check` | `references/rtl-and-qa.md` | Confirms `production/localization/rtl-check-[date].md` |
| `qa` | `references/rtl-and-qa.md` | Confirms `production/localization/loc-qa-[locale]-[date].md` |

### Phase 1-N: Execute Sub-Mode & Recommended Pipeline

Standard shipping sequence: `scan` -> `extract` -> `freeze` -> `brief` -> *(external translation)* -> `validate` (with pseudolocalization) -> `cultural-review` -> `rtl-check` -> `vo-pipeline` -> `qa`.

**Core Pipeline Rules:**
- English (`en`) is the source locale; never directly edit translated locale files—produce diffs for review.
- Every source entry carries a structured `context` field (screen/scene, max char limit, placeholder meanings, gender/plurality notes) and follows `[category].[subcategory].[description]`.
- String freeze precedes external translation; `extract` checks `production/localization/freeze-status.md` and logs any post-freeze additions/edits as freeze violations.
- Delegate domain review in `cultural-review` and `qa` to `.ags/roles/localization-lead.md` (via `producer`), UI layout checks to `art-ux-director` / `gameplay-coder`, and engine-specific checks to `<engine>-specialist` (grounded in `docs/engine-reference/<engine>/`; `NOT ASSESSED` if no engine is configured).
- All user prompts and file-write confirmations follow `modes.automation`.

## Gate & Verdict

Rank final outcomes strictly from highest severity to lowest:

| Verdict | Rank | Meaning & Required Disclosure |
|---|---|---|
| **FAIL / BLOCKED** | 1 (Highest) | Missing sub-mode, `BLOCKING` cultural/RTL/overflow/encoding defects, unresolved freeze violation on release locale, or `qa` FAIL (blocks only the failing locale; other passing locales may proceed). |
| **PASS WITH CONDITIONS / ADVISORY** | 2 | Non-blocking translation polish notes or accepted workarounds logged for pre-ship resolution. |
| **NOT ASSESSED** | 3 | Unresolved code root (`NOT ASSESSED — code root unresolved`), missing `assets/data/strings/` (`NOT ASSESSED — no string table found`), missing engine config (`Engine check: NOT ASSESSED`), or unexecuted playthrough check. Never treat zero hits on an absent input as PASS. |
| **PASS / COMPLETE** | 4 (Lowest) | Scanned denominator > 0 (or verified target string tables present), zero blocking findings, all checks executed, and per-locale `qa` verdict recorded for `ags-gate`. |
