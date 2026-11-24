# Multi-Harness Project Setup Reference

## Generated Core Layout (All Harnesses)

Every initialized game project receives the shared AGS v2 core:

- `AGENTS.md` — master cross-harness studio routing and workflow rules
- `project.yaml` — single source of truth for project stage, rigor, engine, naming, and QA settings
- `.gitignore` — excludes `project.local.yaml`, ephemeral session logs, and cache artifacts
- `.agents/skills/<ags-*>/` — all 21 portable studio skills (`SKILL.md`, `references/`, `CONTRACT.md`)
- `.ags/cli.py` — standalone zero-dependency Python 3.10+ CLI (`preflight`, `verify`, `check`, `doctor`, `hook`, `sync`)
- `.ags/roles/*.md` — 12 core roles + selected engine pack specialists (5) + 22 domain lenses
- `.ags/gates/*.md` — 28 director & lead review gate definitions + `INDEX.md`
- `.ags/templates/*.md` — 46 studio document templates
- `.ags/rules/*.md` — 13 game-native engineering, design, and skill rules
- `.ags/workflow-catalog.yaml` — phase/step artifact catalog used by `check artifacts`
- `docs/engine-reference/<engine>/` — version-pinned reference files for the chosen engine only (`godot`, `unity`, or `unreal`)

## Harness Adapter Files

| `--harness` value | Files generated | Notes |
|---|---|---|
| `codex` | `.codex/config.toml`, `.codex/agents/*.toml`, `.codex/hooks.json` | Enables `multi_agent = true`; on first project open, approve/trust project hooks when prompted |
| `antigravity` | `.agents/hooks.json`, `.agents/rules/ags-rules.md` | Object-keyed camelCase lifecycle hooks + workspace rules |
| `opencode` | `opencode.json`, `.opencode/agents/*.md`, `.opencode/plugins/ags-hooks.ts` | Agent permission modes + TypeScript hook plugin bridging to `.ags/cli.py hook` |
| `claude` | Root instruction shim importing `@AGENTS.md` + harness agent and hook settings | Generated automatically by the `claude` adapter |
| `universal` | Core layout only (`.agents/skills/` + `AGENTS.md` + `.ags/`) | Minimal portable layout for any AGENTS.md / Agent-Skills compatible client |

## Updating an Existing Project (`sync`)

To refresh `.agents/skills/`, `.ags/`, or harness adapters inside an existing AGS v2 project without overwriting game design docs, source code, or `project.yaml`:

```bash
python <repo>/ags_cli.py sync <target> --harness <harness-list>
```

For migrating legacy v1 projects, open the project and run `ags-adopt` (which wraps `python .ags/cli.py check migrate-v1`).
