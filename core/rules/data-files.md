---
paths:
  - "assets/data/**"
  - "Assets/Data/**"
  - "Content/Data/**"
---

# Data File Rules

- All JSON/YAML/data files must parse cleanly — broken syntax fails `python .ags/cli.py verify` and blocks the build.
- File naming: lowercase `snake_case`, following `[system]_[name].json` (or matching engine data-asset convention alongside JSON exports).
- Every data file must have a documented schema (JSON Schema or companion specification in the governing GDD).
- Document numeric meaning, units, and safe tuning ranges alongside schema docs.
- Use `snake_case` for keys within JSON data files across all engines:
  - **Unity / Unreal DTO note**: `JsonUtility` binds exact field names while C#/C++ conventions often use `camelCase`/`PascalCase`. Keep JSON keys `snake_case` as the cross-engine wire format and bind through a small private DTO or serializer naming policy (`SnakeCaseNamingStrategy`, `JsonNamingPolicy.SnakeCaseLower`, Unreal `FJsonObjectConverter` mapping) rather than changing the JSON schema.
- Avoid orphaned entries: every data record should be referenced by code, scene/level data, or another active data file.
- Version data files (`schema_version`) on breaking changes and supply sensible defaults for optional fields.

## Example (`combat_enemies.json`)

```json
{
  "goblin": {
    "base_health": 50,
    "base_damage": 8,
    "move_speed": 3.5,
    "loot_table": "loot_goblin_common"
  }
}
```
