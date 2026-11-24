# Configuration Management Reference (`ags-settings`)

Manages `project.yaml` (committed team-wide config) and `project.local.yaml` (gitignored personal overrides).

> Writing to `project.yaml` is a `schema_changes` decision (a default `modes.automation_always_ask` category), so team config writes confirm with the user even in `autonomous` mode unless `schema_changes` was removed from `modes.automation_always_ask`.

## Argument Validation

| Form | Mode |
|---|---|
| no args | View-all |
| `<key>` (single token, no `=`) | View-one |
| `<key>=<value>` | Set-yaml (`project.yaml`) |
| `--local <key>=<value>` | Set-local (`project.local.yaml`) |

Strip `--local` first, then split on `=`. If either `<key>` or `<value>` is empty (e.g., `=foo`, `key=`, `--local =foo`, `--local key=`), stop and print usage without writing.

## Reserved-Setting Detection

Some schema-validated keys are parsed and stored without yet altering downstream skill behavior. Query reserved keys dynamically from `python .ags/cli.py preflight ags-settings` or schema annotations (`> ### RESERVED` headings if a schema doc is present); **never hardcode reserved key names in skill prose**.

Never refuse a write to a reserved key — store it normally, and mark `, reserved` visibly across **all four paths**: `view-all`, `view-one` (notice printed *above* the value block), `set-yaml` (notice before approval), and `set-local` (notice before approval).

## Mode 1: View-All (no arguments)

1. Confirm `project.yaml` exists; if absent, stop and direct the user to `ags-start`.
2. Check whether `project.local.yaml` exists and run schema/enum validation across both files (tag each error with `[project.yaml]` or `[project.local.yaml]`).
3. Collect all non-empty leaf keys (`key: value`, preserving insertion order from `project.yaml`, then appending additional leaves from `project.local.yaml`).
4. **Always append the seven `modes.rigor`-family keys** if absent from file leaves: `modes.rigor`, `modes.workflow`, `docs.density`, `qa.level`, `modes.story_granularity`, `modes.review_mode`, `team.size`. Because rigor-derived keys are absent from files by default, omitting this step hides settings the user relies on.
5. For each key, resolve effective value, provenance (`<source>`), team YAML value, and local-override eligibility:

| Provenance `<source>` | Display Annotation |
|---|---|
| `project.local.yaml` (team `project.yaml` also set) | `(LOCAL OVERRIDE — yaml has: <yamlvalue>)` |
| `project.local.yaml` (team `project.yaml` unset) | `(project.local.yaml)` |
| `project.yaml` | `(project.yaml)` |
| Legacy file (`production/*.txt`) | `(<path>, legacy)` |
| `rigor:<level>` | `(derived from rigor: <level>)` |
| `default` | `(default)` |
| `unset` | Skip printing |

- Append `, locked` when a key is not locally overridable (locked to `project.yaml`).
- Append `, reserved` when the key is in the reserved set.

6. Print grouped by top-level section (`framework`, `project`, `modes`, `docs`, `qa`, `engine`, `specialists`, `naming`, `platform`, `performance`, `testing`, `commands`).
7. Print legends whenever applicable:
   - If any key carries `, locked`: explain that `locked` means non-overridable in `project.local.yaml` (project-wide), NOT immutable — explicit `ags-settings <key>=<value>` overrides rigor-derived values.
   - If any key carries `, reserved`: explain that `reserved` means stored and validated, with no runtime consumer active yet.

## Mode 2: View-One (`<key>`)

1. If `<key>` is reserved, print **above** the block:
   `> <key> is RESERVED — stored and validated, no active consumer today.`
2. Resolve effective value + provenance, `project.yaml` value, `project.local.yaml` value, and whitelist status (`can be locally overridden` | `locked — project-wide`).
3. Print effective value (or `(not set)`), source, locally overridden (`yes` | `no`), and whitelist status.
   - If overridden locally while also set in `project.yaml`, show both `project.yaml value:` and `project.local.yaml value:`.
   - If provenance is `rigor:<level>`, show: `Set explicitly with: ags-settings <key>=<value> (explicit wins over rigor)`.

## Mode 3: Set Team-Wide (`<key>=<value>`)

1. Validate enum/type against the schema; on error, print allowed values verbatim and stop without writing.
2. If reserved, notify the user *before* asking approval that it is stored but currently changes no behavior.
3. If `project.local.yaml` overrides `<key>`, warn *before* asking approval that the local override shadows `project.yaml` for this developer.
4. Confirm write with the user (respecting `modes.automation` + `schema_changes` always-ask).
5. Edit `project.yaml` cleanly:
   - Key exists: match parent block header + leaf line to keep edit unique and update value in place.
   - Parent block exists, leaf absent: append leaf at matching indentation inside parent block.
   - Parent block absent: append top-level block at EOF.
   - Ambiguous/commented/malformed structure: stop and ask user rather than guessing.
6. Special post-write checks:
   - If `<key>` is `modes.rigor`: re-read via `preflight` and print all 6 fronted knobs (`modes.workflow`, `docs.density`, `qa.level`, `modes.story_granularity`, `modes.review_mode`, `team.size`) showing which are now derived vs explicitly preserved.
   - If `<key>` is `modes.workflow`: emit: `"Workflow changed from [old] to [new]. Run ags-design-review content-audit to see what is now required or extra. Existing files remain untouched."`

## Mode 4: Set Personal Override (`--local <key>=<value>`)

1. Check local-override whitelist. If locked, refuse and instruct: `<key> cannot be locally overridden — use ags-settings <key>=<value> for the whole team.`
2. Validate enum/type; stop on error.
3. If reserved, display the same reserved notice as Mode 3 before approval.
4. Confirm `project.yaml` exists (`project.local.yaml` requires a base file; otherwise direct to `ags-start`).
5. Confirm write with the user, then create `project.local.yaml` (if absent) or edit in place using Mode 3's block/leaf strategy.

## Usage Summary

```text
ags-settings                         — view all effective configuration
ags-settings <key>                   — view one setting and provenance
ags-settings <key>=<value>           — set project-wide in project.yaml
ags-settings --local <key>=<value>   — set personal override in project.local.yaml
```
