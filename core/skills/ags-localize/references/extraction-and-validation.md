# Localization: Scan, Extract, Validate, Pseudolocalization, Status & Freeze

Detailed execution guides for `scan`, `extract`, `validate`, `status`, and `freeze` sub-modes, including key-naming schemas, pseudolocalization, CJK/pluralization checks, and anti-silent-skip rules.

---

## Sub-Mode: `scan` (Read-Only)

Resolve the code root from `engine.name` (`Godot` -> `src/`, `Unity` -> `Assets/`, `Unreal` -> `Source/<Module>/`, or unambiguous single directory). **If the code root is unresolved, report `NOT ASSESSED — code root unresolved` and stop — never default to `src/` or report zero hits.**

Report denominator (`scanned [N] files`) and search for:
- Unwrapped string literals in UI/gameplay code not routed through localization calls (`tr()`, `Tr()`, `NSLocalizedString`, `LOCTEXT`, `GetText`, etc.).
- String concatenation instead of parameterized templates.
- Positional format placeholders (`%s`, `%d`) instead of named tokens (`{playerName}`).
- Locale-sensitive formatting (dates, times, numbers `1,000` vs `1.000`, currencies) lacking locale-aware formatters.
- Text embedded inside textures/images under `assets/`.
- Left-to-right assumptions in layout positioning or multi-fragment string assembly.
- Baked-in gender or singular/plural branching instead of proper pluralization rules or gender tokens.
- Hardcoded punctuation (`"You won!"`) where punctuation rules differ across locales.

Report all hits with `file:line`. Write no files.

---

## Sub-Mode: `extract`

1. Scan resolved code root for localized string keys and compare against `assets/data/strings/strings-en.json`.
2. Enforce the **Key-Naming Schema**:
   - Pattern: `[category].[subcategory].[description]` (lowercase `snake_case` segments).
   - Standard top-level categories: `ui.*`, `menu.*`, `hud.*`, `dialogue.*`, `item.*`, `quest.*`, `system.*`, `error.*`, `tutorial.*`.
   - Examples: `ui.hud.health_label`, `dialogue.npc.merchant.greeting`, `menu.main.play_button`.
3. Require a structured `context` object/field on every new entry:
   - Screen/scene where string appears
   - Hard character limit (or UI box constraint)
   - Meaning and type of each `{placeholder}` (e.g., `{playerName}` = player display name)
   - Gender / plurality / speaker context if applicable
4. **Freeze integration**: Check `production/localization/freeze-status.md`. If `Status: ACTIVE`, append all newly added or modified keys under `## Post-Freeze Changes` and emit:
   `String freeze is active. [N] new/modified strings detected (freeze violations) — notify your localization vendor before shipping.`
5. Present only the diff (new/changed entries), request user confirmation, and write incremental updates to `assets/data/strings/strings-en.json` without overwriting existing entries.

---

## Sub-Mode: `validate` (Read-Only)

Inspect all locale files in `assets/data/strings/`. If `assets/data/strings/` or `strings-en.json` is missing, emit `NOT ASSESSED — no string table found` and stop.

### Core Validation Checks
- **Completeness**: Key present in `en` source but missing or empty in target locale.
- **Placeholder integrity**: Source `{name}` tokens omitted, misspelled, duplicated, or extra tokens added in translation.
- **Character limit compliance**: Translated length exceeds the limit in source `context` (flag tight UI fields; account for +30–40% expansion headroom in German/Finnish/Romance locales).
- **Orphaned keys**: Translation exists in string tables with zero references in the resolved code root (report only when code root is resolved; mark orphan check `NOT ASSESSED` if code root unresolved).
- **Stale translations**: Source string modified since translation timestamp/hash.

### Pluralization, CJK & Encoding Checklists
- **CLDR Plural Form Coverage**: Verify every pluralized key supplies all required CLDR categories for the target locale (not just `one`/`other`):
  - CJK/Vietnamese/Thai (`ja`, `ko`, `zh`, `vi`, `th`): `other` (or `one`/`other` checks without forced English `-s` logic).
  - English/German/Spanish/Italian (`en`, `de`, `es`, `it`): `one`, `other`.
  - French/Portuguese (`fr`, `pt`): `one`, `many` (large numbers), `other`.
  - Slavic (`ru`, `uk`, `pl`): `one`, `few`, `many`, `other`.
  - Arabic (`ar`): all six (`zero`, `one`, `two`, `few`, `many`, `other`).
  Flag any locale missing required plural forms as `BLOCKING`.
- **CJK Line-Breaking, Wrapping & Font Coverage**:
  - Verify non-ASCII glyphs (CJK ideographs, Hangul, Kana, accents, diacritics) exist in the project's font atlas / fallback font chain (never rely on OS fallback without verifying font export).
  - Check CJK line wrapping does not depend on ASCII spaces; verify forbidden line-start/line-end punctuation rules (kinsoku shori) and full-width vs half-width punctuation consistency.
  - Check vertical line-height/leading accommodates tall glyphs (Thai, Arabic, Vietnamese stacked diacritics, CJK ruby/furigana).
- **Pseudolocalization Readiness Pass**:
  - Generate or test a pseudolocalized (`qps-ploc` / `en-XA`) pass over `strings-en.json` before paying external translators:
    - Expand English text length by +35% (`[!! ... !!]` bracket delimiters) to surface UI truncation/clipping early.
    - Replace ASCII letters with accented/wide Unicode lookalikes (`Á, ß, Č, 汉`) while leaving `{placeholders}` untouched to expose hardcoded unextracted strings, broken placeholder concatenation, and font glyph gaps.

Report findings grouped by locale and severity (`BLOCKING` / `ADVISORY`). Write no files.

---

## Sub-Mode: `status` (Read-Only)

If `assets/data/strings/` or the source table is absent, output **`NOT ASSESSED — no string table found`** instead of a zero-filled table or a pre-filled `100%` source row.

Count every cell directly from the string table files (including `en` source):

```markdown
## Localization Status
Generated: [Date]
String freeze: [Active / Not yet called / Lifted]

| Locale | Total | Translated | Missing | Stale | Coverage |
|---|---|---|---|---|---|
| en (source) | [N] | [N] | [N] | [N] | [N]% |
| [locale] | [N] | [N] | [N] | [N] | [X]% |

### Issues
- Hardcoded strings in code root: [N | NOT ASSESSED — code root unresolved] (ags-localize scan)
- Character-limit violations: [N]
- Placeholder / plural mismatches: [N]
- Orphaned keys: [N | NOT ASSESSED]
- Post-freeze additions/edits: [N]
```

---

## Sub-Mode: `freeze`

### `freeze call`
1. Check `production/localization/freeze-status.md`. If `Status: ACTIVE`, report call date and count of post-freeze violations.
2. Otherwise, verify the Pre-Freeze Checklist:
   - `[ ]` Planned UI screens implemented
   - `[ ]` Dialogue lines final
   - `[ ]` System strings (errors, tutorials) complete
   - `[ ]` `ags-localize scan` reports zero hardcoded strings (verified denominator > 0)
   - `[ ]` `ags-localize validate` shows zero placeholder/plural errors in source (`en`)
   - `[ ]` Marketing/storefront strings final
3. Prompt user to confirm locking the source string table (`[A] Call string freeze now` / `[B] Hold — more strings pending`).
4. On `[A]`, confirm and write `production/localization/freeze-status.md` (`Status: ACTIVE`, `Called`, `Called by`, `Total strings at freeze`, `## Post-Freeze Changes`).

### `freeze lift`
Update `production/localization/freeze-status.md` to `Status: LIFTED` with date and reason, and warn that all modified strings require re-translation and vendor notification.
