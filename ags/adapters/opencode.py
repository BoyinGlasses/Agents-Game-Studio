"""OpenCode harness adapter (opencode.json, .opencode/agents/*.md, .opencode/plugins/ags-hooks.ts)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ags.adapters.common import RoleSpec

_OPENCODE_PLUGIN_TS = """\
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

function findAgsCli(startDir: string): string | null {
  let dir = resolve(startDir);
  while (true) {
    const candidate = join(dir, ".ags", "cli.py");
    if (existsSync(candidate)) return candidate;
    const parent = dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

function runAgsHook(event: string, payload: Record<string, any>): Record<string, any> {
  const startDir = typeof payload?.directory === "string" && payload.directory ? payload.directory : process.cwd();
  const cliPath = findAgsCli(startDir);
  if (!cliPath) return { allow: true, noop: true };
  const rootDir = dirname(dirname(cliPath));
  try {
    const out = execFileSync("python", [".ags/cli.py", "hook", "--harness", "opencode", event], {
      cwd: rootDir,
      input: JSON.stringify(payload ?? {}),
      encoding: "utf-8",
    }).trim();
    return out ? JSON.parse(out) : { allow: true };
  } catch {
    return { allow: true, noop: true };
  }
}

export const AgsHooksPlugin = async ({ directory }: { directory: string }) => ({
  "session.created": async () => runAgsHook("SessionStart", { directory }),
  "tool.execute.before": async (input: any, output: any) => {
    const res = runAgsHook("PreToolUse", { directory, tool: input?.tool, input: output?.args ?? input });
    if (res.blocked) throw new Error(res.reason || "Blocked by AGS pre-tool hook");
  },
  "tool.execute.after": async (input: any) => {
    runAgsHook("PostToolUse", { directory, tool: input?.tool, input: input?.args ?? input });
  },
  "experimental.session.compacting": async (_input: any, output: any) => {
    const res = runAgsHook("PreCompact", { directory });
    if (res.additionalContext && Array.isArray(output?.context)) output.context.push(res.additionalContext);
  },
  "session.idle": async () => runAgsHook("Stop", { directory }),
});

export default AgsHooksPlugin;
"""


def _yaml_quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def apply_opencode(target_dir: Path, roles: list[RoleSpec]) -> list[Path]:
    """Write opencode.json, .opencode/agents/*.md, and .opencode/plugins/ags-hooks.ts."""
    written: list[Path] = []
    opencode_dir = target_dir / ".opencode"
    agents_dir = opencode_dir / "agents"
    plugins_dir = opencode_dir / "plugins"

    if agents_dir.is_dir():
        shutil.rmtree(agents_dir)
    agents_dir.mkdir(parents=True, exist_ok=True)
    plugins_dir.mkdir(parents=True, exist_ok=True)

    agent_entries: dict[str, dict] = {}
    for role in roles:
        is_ro = role.sandbox_mode == "read-only"
        agent_entries[role.name] = {
            "description": role.description,
            "mode": "subagent",
            "permission": {
                "edit": "deny" if is_ro else "allow",
                "bash": "ask" if is_ro else "allow",
            },
        }
        md_text = (
            "---\n"
            f"description: {_yaml_quote(role.description)}\n"
            "mode: subagent\n"
            "tools:\n"
            f"  write: {'false' if is_ro else 'true'}\n"
            f"  edit: {'false' if is_ro else 'true'}\n"
            "---\n\n"
            f"{role.body}\n"
        )
        agent_path = agents_dir / f"{role.name}.md"
        agent_path.write_text(md_text, encoding="utf-8")
        written.append(agent_path)

    opencode_cfg = {
        "$schema": "https://opencode.ai/config.json",
        "instructions": ["AGENTS.md"],
        "permission": {
            "bash": {
                "*": "allow",
                "rm -rf *": "deny",
                "git push --force*": "deny",
                "git reset --hard*": "deny",
            },
            "edit": "allow",
            "read": {
                "*": "allow",
                "**/.env*": "deny",
            },
        },
        "agent": agent_entries,
    }
    cfg_path = target_dir / "opencode.json"
    cfg_path.write_text(json.dumps(opencode_cfg, indent=2) + "\n", encoding="utf-8")
    written.append(cfg_path)

    plugin_path = plugins_dir / "ags-hooks.ts"
    plugin_path.write_text(_OPENCODE_PLUGIN_TS, encoding="utf-8")
    written.append(plugin_path)

    return written
