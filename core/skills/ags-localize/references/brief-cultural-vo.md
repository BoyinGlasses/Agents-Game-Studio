# Localization: Translator Brief, Cultural Review & VO Pipeline

Detailed guides for `brief`, `cultural-review`, and `vo-pipeline` sub-modes.

---

## Sub-Mode: `brief`

Generate an external translator / vendor briefing package alongside exported string tables.

1. **Read inputs**:
   - `design/gdd/` (genre, tone, setting, character names)
   - `assets/data/strings/strings-en.json` (source string table)
   - Narrative and lore docs under `design/narrative/`
2. **Draft `production/localization/translator-brief-[locale]-[date].md`**:
   - **Game Overview**: 2-3 paragraphs on genre, tone, and audience.
   - **Tone and Voice**: overall voice, player address formality (`tu` vs `vous` guidance, honorifics), profanity intensity policy, humor/wordplay localization strategy.
   - **Character Glossary**: `Name | Role | Personality | Translation/Transliteration Notes`.
   - **World Glossary**: `Term | Meaning | Keep Verbatim / Translate Notes`.
   - **Do Not Translate List**: game title, matching in-engine brand labels, trademarks.
   - **Placeholder Reference**: table mapping every `{token}` to meaning and example (`{playerName}`, `{count}`).
   - **Character Limits & Expansion**: enforce `context` hard limits; default ±30% guideline when unspecified.
   - **Contact & Delivery Schema**: team contact placeholder and JSON delivery schema matching `strings-en.json`.
3. Request user confirmation before writing `production/localization/translator-brief-[locale]-[date].md`.

---

## Sub-Mode: `cultural-review`

Delegate to `.ags/roles/localization-lead.md` (`producer` core role) to audit target locale strings (`assets/data/strings/`) and visual/audio assets (`assets/`) across six cultural risk areas:

1. **Symbols & Gestures**: thumbs-up, OK sign, peace sign, religious/spiritual iconography, flags, maps, disputed borders.
2. **Colors**: mourning/luck/danger/political color associations (white, green, red) in alerts and UI states.
3. **Numbers**: culturally sensitive numbers in UI/prices/rooms (`4`, `13`, `666`, etc.).
4. **Humor & Idioms**: idioms degrading across locales, region-sensitive toilet/bodily humor (Japan, Germany, Middle East), sensitive dark humor.
5. **Violence & Content Ratings**: DE, AU, CN, AE rating triggers (blood color, gore, substance references requiring regional asset variants).
6. **Names & Representation**: character/place names carrying profane or negative meanings in target languages; national/religious/ethnic stereotypes.

Present findings table (`Finding | Locale(s) Affected | Severity (BLOCKING / ADVISORY / NOTE) | Recommended Action`). `BLOCKING` items must resolve before shipping the affected locale. Request user confirmation before writing `production/localization/cultural-review-[date].md`.

---

## Sub-Mode: `vo-pipeline`

Dispatch on sub-task argument (`scan` | `script` | `validate` | `integrate`):

### `vo-pipeline scan` (Read-Only)
Cross-reference `dialogue.*` keys in `assets/data/strings/` and `design/narrative/` against audio files in `assets/audio/vo/` to emit the **VO Recording Manifest** (`Key | Character | Source Line | Status [Recorded / Needs recording]`). If `assets/data/strings/` is absent, emit `NOT ASSESSED — no string table found`.

### `vo-pipeline script`
Build per-character recording scripts grouped by scene containing:
- Character name and personality note
- Full dialogue line plus pronunciation guides for proper nouns/invented terms
- Emotion/acting direction tag (`[Warm, welcoming]`, `[Annoyed, clipped]`)
- Conversational response context (`"Player just said X"`)

Request user confirmation before writing `production/localization/vo-scripts-[locale]-[date].md`.

### `vo-pipeline validate` (Read-Only)
List `.wav`/`.ogg` files under `assets/audio/vo/[locale]/` and cross-reference the VO manifest:
- Missing files (scripted key lacks audio file)
- Extra unmapped files (audio file lacks string key)
- Naming convention mismatches
- If `assets/audio/vo/[locale]/` is absent or empty while VO keys exist, report `NOT ASSESSED — no VO audio directory found for [locale]`.

### `vo-pipeline integrate` (Read-Only)
Search resolved code root (`src/` / `Assets/` / `Source/`) for VO audio path references and verify each path resolves inside `assets/audio/vo/[locale]/`. Report denominator (`scanned [N] source files`) and all broken references (or `NOT ASSESSED — code root unresolved`).
