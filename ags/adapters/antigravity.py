"""Antigravity harness adapter (.agents/hooks.json and .agents/rules/ags-rules.md)."""

from __future__ import annotations

import json
from pathlib import Path

from ags.adapters.common import RoleSpec

_AGS_RULES_MD = """\
# Agents Game Studio — Antigravity Workspace Rules

Read `AGENTS.md` at the repository root and `project.yaml` before starting work.

## Core Execution Contract
- **Preflight**: Run `python .ags/cli.py preflight <skill>` before running any skill in `.agents/skills/ags-*/SKILL.md`.
- **Roles & Gates**: Role definitions live in `.ags/roles/*.md`; director gates live in `.ags/gates/*.md` (`.ags/gates/INDEX.md`).
- **Engine Reference**: Read `docs/engine-reference/<engine>/VERSION.md` before citing engine APIs.
- **Verification**: Run `python .ags/cli.py verify` to refresh `.ags/state/receipt.json` before marking a story `Status: Complete`.
- **Session Recovery**: Keep `production/session-state/active.md` updated as the durable checkpoint.
"""


def _agy_hook_cmd(event: str) -> str:
    return (
        'python -c "import runpy,sys;from pathlib import Path;'
        "p=next(d/'.ags/cli.py' for d in (Path.cwd(),*Path.cwd().parents) if (d/'.ags/cli.py').is_file());"
        f"sys.argv=[str(p),'hook','--harness','antigravity','{event}'];"
        'runpy.run_path(str(p),run_name=\'__main__\')"'
    )


def apply_antigravity(target_dir: Path, roles: list[RoleSpec]) -> list[Path]:
    """Write Antigravity camelCase hooks.json and workspace rules."""
    del roles  # Antigravity reads roles dynamically from .ags/roles/ via AGENTS.md
    written: list[Path] = []
    agents_dir = target_dir / ".agents"
    rules_dir = agents_dir / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    hooks_payload = {
        "ags-hooks": {
            "SessionStart": [
                {
                    "type": "command",
                    "command": _agy_hook_cmd("SessionStart"),
                    "timeout": 10,
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "run_command",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _agy_hook_cmd("PreToolUse"),
                            "timeout": 15,
                        }
                    ],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "edit_file|write_file",
                    "hooks": [
                        {
                            "type": "command",
                            "command": _agy_hook_cmd("PostToolUse"),
                            "timeout": 10,
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "type": "command",
                    "command": _agy_hook_cmd("Stop"),
                    "timeout": 10,
                }
            ],
        }
    }

    hooks_path = agents_dir / "hooks.json"
    hooks_path.write_text(json.dumps(hooks_payload, indent=2) + "\n", encoding="utf-8")
    written.append(hooks_path)

    rules_path = rules_dir / "ags-rules.md"
    rules_path.write_text(_AGS_RULES_MD, encoding="utf-8")
    written.append(rules_path)

    return written
