"""Claude Code harness adapter (CLAUDE.md, .claude/agents/*.md, .claude/settings.json)."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from ags.adapters.common import RoleSpec

_CLAUDE_MD = """\
# Agents Game Studio — Claude Code Entry

@AGENTS.md

## Claude Adapter Notes
- Use `.ags/roles/*.md` definitions matching `.claude/agents/*.md`.
- Hooks in `.claude/settings.json` run via `python .ags/cli.py hook --harness claude <event>`.
"""

_EFFORT_TO_CLAUDE_MODEL = {
    "low": "haiku",
    "medium": "sonnet",
    "high": "opus",
}


def _yaml_quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def _claude_hook_cmd(event: str) -> str:
    py = "python" if os.name == "nt" else "python3"
    return (
        f'{py} -c "import os,runpy,sys;from pathlib import Path;'
        "r=os.environ.get('CLAUDE_PROJECT_DIR');"
        "cands=([Path(r)] if r else [])+[Path.cwd(),*Path.cwd().parents];"
        "p=next((d/'.ags/cli.py' for d in cands if (d/'.ags/cli.py').is_file()),None);"
        f"p and (os.chdir(p.parent.parent),setattr(sys,'argv',[str(p),'hook','--harness','claude','{event}']),"
        "runpy.run_path(str(p),run_name='__main__'))\""
    )


def apply_claude(target_dir: Path, roles: list[RoleSpec]) -> list[Path]:
    """Write CLAUDE.md, .claude/agents/*.md, and .claude/settings.json."""
    written: list[Path] = []
    claude_dir = target_dir / ".claude"
    agents_dir = claude_dir / "agents"
    if agents_dir.is_dir():
        shutil.rmtree(agents_dir)
    agents_dir.mkdir(parents=True, exist_ok=True)

    claude_md = target_dir / "CLAUDE.md"
    claude_md.write_text(_CLAUDE_MD, encoding="utf-8")
    written.append(claude_md)

    for role in roles:
        is_ro = role.sandbox_mode == "read-only"
        tools = "Read, Grep, Glob" if is_ro else "Read, Write, Edit, Bash, Grep, Glob"
        model = _EFFORT_TO_CLAUDE_MODEL.get(role.model_reasoning_effort, "sonnet")
        md_text = (
            "---\n"
            f"name: {role.name}\n"
            f"description: {_yaml_quote(role.description)}\n"
            f"tools: {tools}\n"
            f"model: {model}\n"
            "---\n\n"
            f"{role.body}\n"
        )
        agent_path = agents_dir / f"{role.name}.md"
        agent_path.write_text(md_text, encoding="utf-8")
        written.append(agent_path)

    def _entry(matcher: str, event: str, timeout: int = 15) -> dict:
        return {
            "matcher": matcher,
            "hooks": [
                {
                    "type": "command",
                    "command": _claude_hook_cmd(event),
                    "timeout": timeout,
                }
            ],
        }

    settings = {
        "$schema": "https://json.schemastore.org/claude-code-settings.json",
        "permissions": {
            "defaultMode": "default",
            "allow": [
                "Bash(git status*)",
                "Bash(git diff*)",
                "Bash(git log*)",
                "Bash(python .ags/cli.py*)",
            ],
            "deny": [
                "Bash(rm -rf *)",
                "Bash(git push --force*)",
                "Bash(git reset --hard*)",
                "Read(**/.env*)",
            ],
        },
        "hooks": {
            "SessionStart": [_entry("", "SessionStart", timeout=10)],
            "PreToolUse": [_entry("Bash|Edit|Write", "PreToolUse", timeout=15)],
            "PostToolUse": [_entry("Edit|Write", "PostToolUse", timeout=10)],
            "PreCompact": [_entry("", "PreCompact", timeout=10)],
            "PostCompact": [_entry("", "PostCompact", timeout=10)],
            "Stop": [_entry("", "Stop", timeout=10)],
        },
    }
    settings_path = claude_dir / "settings.json"
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    written.append(settings_path)

    return written
