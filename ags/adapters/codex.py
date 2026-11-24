"""Codex harness adapter (.codex/config.toml, .codex/agents/*.toml, .codex/hooks.json)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ags.adapters.common import RoleSpec


def _toml_escape_basic(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")


def _toml_escape_multiline(value: str) -> str:
    # Escape backslashes first, then triple double quotes inside multiline TOML strings.
    escaped = value.replace("\\", "\\\\").replace('"""', '\\"""')
    return escaped


def _codex_hook_cmd(python_bin: str, event: str) -> str:
    return (
        f'{python_bin} -c "import runpy,sys;from pathlib import Path;'
        f"p=next(d/'.ags/cli.py' for d in (Path.cwd(),*Path.cwd().parents) if (d/'.ags/cli.py').is_file());"
        f"sys.argv=[str(p),'hook','--harness','codex','{event}'];"
        f"runpy.run_path(str(p),run_name='__main__')\""
    )


def apply_codex(target_dir: Path, roles: list[RoleSpec]) -> list[Path]:
    """Write Codex multi-agent config, agent TOMLs, and hooks.json."""
    written: list[Path] = []
    codex_dir = target_dir / ".codex"
    agents_dir = codex_dir / "agents"
    if agents_dir.is_dir():
        shutil.rmtree(agents_dir)
    agents_dir.mkdir(parents=True, exist_ok=True)

    config_lines = [
        "# Agents Game Studio (AGS v2) — Codex multi-agent configuration",
        "",
        "[features]",
        "multi_agent = true",
        "",
    ]

    for role in roles:
        agent_path = agents_dir / f"{role.name}.toml"
        header = (
            f"Follow AGENTS.md, project.yaml, and .ags/rules/. "
            f"Use python .ags/cli.py preflight/verify as needed.\n\n"
        )
        instructions = header + role.body
        toml_text = (
            f'name = "{_toml_escape_basic(role.name)}"\n'
            f'description = "{_toml_escape_basic(role.description)}"\n'
            f'sandbox_mode = "{_toml_escape_basic(role.sandbox_mode)}"\n'
            f'model_reasoning_effort = "{_toml_escape_basic(role.model_reasoning_effort)}"\n'
            f'developer_instructions = """\n'
            f"{_toml_escape_multiline(instructions)}\n"
            f'"""\n'
        )
        agent_path.write_text(toml_text, encoding="utf-8")
        written.append(agent_path)

        config_lines.extend(
            [
                f"[agents.{role.name}]",
                f'description = "{_toml_escape_basic(role.description)}"',
                f'config_file = "agents/{role.name}.toml"',
                "",
            ]
        )

    config_path = codex_dir / "config.toml"
    config_path.write_text("\n".join(config_lines), encoding="utf-8")
    written.append(config_path)

    def _entry(matcher: str, event: str, timeout: int = 15) -> dict:
        return {
            "matcher": matcher,
            "hooks": [
                {
                    "type": "command",
                    "command": _codex_hook_cmd("python3", event),
                    "commandWindows": _codex_hook_cmd("python", event),
                    "timeout": timeout,
                }
            ],
        }

    hooks_payload = {
        "description": "Agents Game Studio v2 hooks for Codex",
        "hooks": {
            "SessionStart": [_entry("startup|resume|clear|compact", "SessionStart", timeout=10)],
            "PreToolUse": [
                _entry("Bash|exec_command|shell|local_shell", "PreToolUse", timeout=15),
                _entry("Edit|Write|apply_patch", "PreToolUse", timeout=15),
            ],
            "PostToolUse": [_entry("Edit|Write|apply_patch", "PostToolUse", timeout=10)],
            "PreCompact": [_entry("manual|auto", "PreCompact", timeout=10)],
            "PostCompact": [_entry("manual|auto", "PostCompact", timeout=10)],
            "Stop": [_entry("", "Stop", timeout=10)],
        },
    }
    hooks_path = codex_dir / "hooks.json"
    hooks_path.write_text(json.dumps(hooks_payload, indent=2) + "\n", encoding="utf-8")
    written.append(hooks_path)

    return written
