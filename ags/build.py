"""Compile core/skills -> skills/, generate root hooks.json, and sync plugin manifests."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from ags import PACKAGE_NAME, __version__

_DISPLAY_NAME = "Agents Game Studio"
_SHORT_DESC = "Build games across Codex, Antigravity, OpenCode, and Claude Code"
_LONG_DESC = (
    "Multi-harness game development framework with 21 unified workflow skills, "
    "core studio roles, engine packs, director gates, and verification hooks."
)
_DEFAULT_PROMPT = "Initialize or advance a game project with Agents Game Studio."


def _expected_root_hooks() -> dict[str, Any]:
    """Generate Antigravity plugin-root camelCase hooks.json (no-op outside game project)."""

    def cmd(event: str) -> str:
        return f"python ags_cli.py hook --harness antigravity {event}"

    return {
        PACKAGE_NAME: {
            "SessionStart": [
                {
                    "type": "command",
                    "command": cmd("SessionStart"),
                    "timeout": 10,
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "run_command",
                    "hooks": [
                        {
                            "type": "command",
                            "command": cmd("PreToolUse"),
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
                            "command": cmd("PostToolUse"),
                            "timeout": 10,
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "type": "command",
                    "command": cmd("Stop"),
                    "timeout": 10,
                }
            ],
        }
    }


def _updated_root_plugin(existing: dict[str, Any]) -> dict[str, Any]:
    data = dict(existing)
    data.setdefault("$schema", "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
    data["name"] = PACKAGE_NAME
    data["version"] = __version__
    data["description"] = (
        "Agents Game Studio (AGS v2): multi-harness game development workflows, "
        "specialist roles, engine packs, project scaffold, and validation hooks."
    )
    data.setdefault("author", {"name": "BoyinGlasses"})
    data.setdefault("repository", "https://github.com/BoyinGlasses/Codex-Game-Studio")
    data.setdefault("license", "MIT")
    data["keywords"] = [
        "agents-game-studio",
        "game-development",
        "codex",
        "antigravity",
        "opencode",
        "claude",
        "godot",
        "unity",
        "unreal",
        "skills",
    ]
    extensions = dict(data.get("extensions") or {})
    openai_ext = dict(extensions.get("com.openai") or {})
    iface = dict(openai_ext.get("interface") or {})
    iface.update(
        {
            "displayName": _DISPLAY_NAME,
            "shortDescription": _SHORT_DESC,
            "longDescription": _LONG_DESC,
            "developerName": iface.get("developerName") or "BoyinGlasses",
            "category": iface.get("category") or "Productivity",
            "capabilities": iface.get("capabilities") or ["Read", "Write"],
            "defaultPrompt": _DEFAULT_PROMPT,
        }
    )
    openai_ext["interface"] = iface
    extensions["com.openai"] = openai_ext
    data["extensions"] = extensions
    return data


def _updated_codex_plugin(existing: dict[str, Any]) -> dict[str, Any]:
    data = dict(existing)
    data["name"] = PACKAGE_NAME
    data["version"] = __version__
    data["description"] = (
        "Agents Game Studio (AGS v2): multi-harness game development workflows and project template."
    )
    data.setdefault("author", {"name": "Donchitos / BoyinGlasses"})
    data["skills"] = "./skills/"
    iface = dict(data.get("interface") or {})
    iface.update(
        {
            "displayName": _DISPLAY_NAME,
            "shortDescription": _SHORT_DESC,
            "longDescription": _LONG_DESC,
            "developerName": iface.get("developerName") or "Donchitos / BoyinGlasses",
            "category": iface.get("category") or "Productivity",
            "capabilities": iface.get("capabilities") or ["Read", "Write"],
            "defaultPrompt": _DEFAULT_PROMPT,
        }
    )
    data["interface"] = iface
    return data


def _updated_marketplace(existing: dict[str, Any]) -> dict[str, Any]:
    data = dict(existing)
    data["name"] = PACKAGE_NAME
    iface = dict(data.get("interface") or {})
    iface["displayName"] = _DISPLAY_NAME
    data["interface"] = iface
    plugins = list(data.get("plugins") or [])
    if plugins:
        first = dict(plugins[0])
        first["name"] = PACKAGE_NAME
        plugins[0] = first
    else:
        plugins = [
            {
                "name": PACKAGE_NAME,
                "source": {
                    "source": "url",
                    "url": "https://github.com/BoyinGlasses/Codex-Game-Studio.git",
                    "ref": "main",
                },
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }
        ]
    data["plugins"] = plugins
    return data


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8-sig"))
        return loaded if isinstance(loaded, dict) else {}
    except (OSError, ValueError):
        return {}


def _snapshot_tree(root: Path) -> dict[str, bytes]:
    if not root.is_dir():
        return {}
    out: dict[str, bytes] = {}
    for p in sorted(root.rglob("*")):
        if "__pycache__" in p.parts or p.name in (".DS_Store", "Thumbs.db"):
            continue
        if p.is_file():
            rel = str(p.relative_to(root)).replace("\\", "/")
            out[rel] = p.read_bytes()
    return out


def run_build(repo_root: Path | None = None, check: bool = False) -> tuple[int, str]:
    """Compile root skills/, root hooks.json, and plugin manifests; or verify sync with --check."""
    root = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    core_skills = root / "core" / "skills"
    root_skills = root / "skills"

    if not core_skills.is_dir():
        return 1, f"ERROR: core/skills directory not found at {core_skills}\n"

    manifest_specs = [
        (root / "hooks.json", _expected_root_hooks()),
        (root / "plugin.json", _updated_root_plugin(_read_json_or_empty(root / "plugin.json"))),
        (
            root / ".codex-plugin" / "plugin.json",
            _updated_codex_plugin(_read_json_or_empty(root / ".codex-plugin" / "plugin.json")),
        ),
        (
            root / ".agents" / "plugins" / "marketplace.json",
            _updated_marketplace(_read_json_or_empty(root / ".agents" / "plugins" / "marketplace.json")),
        ),
    ]

    if check:
        drifts: list[str] = []
        src_snap = _snapshot_tree(core_skills)
        dst_snap = _snapshot_tree(root_skills)
        if src_snap != dst_snap:
            missing = sorted(set(src_snap) - set(dst_snap))
            extra = sorted(set(dst_snap) - set(src_snap))
            changed = sorted(k for k in (set(src_snap) & set(dst_snap)) if src_snap[k] != dst_snap[k])
            if missing:
                drifts.append(f"skills/ missing {len(missing)} file(s): {', '.join(missing[:5])}")
            if extra:
                drifts.append(f"skills/ has {len(extra)} stale file(s): {', '.join(extra[:5])}")
            if changed:
                drifts.append(f"skills/ differs on {len(changed)} file(s): {', '.join(changed[:5])}")

        for mpath, expected_obj in manifest_specs:
            rel = str(mpath.relative_to(root)).replace("\\", "/")
            if not mpath.is_file():
                drifts.append(f"{rel}: file missing")
                continue
            actual_obj = _read_json_or_empty(mpath)
            if actual_obj != expected_obj:
                drifts.append(f"{rel}: out of sync with build spec")

        if drifts:
            return 1, "OUT OF SYNC:\n" + "\n".join(f"  - {d}" for d in drifts) + "\n"
        return 0, f"Build in sync ({len(src_snap)} skill files, 4 manifests).\n"

    # Perform build
    if root_skills.exists():
        shutil.rmtree(root_skills)
    shutil.copytree(
        core_skills,
        root_skills,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "Thumbs.db"),
    )

    for mpath, obj in manifest_specs:
        mpath.parent.mkdir(parents=True, exist_ok=True)
        mpath.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

    skill_count = sum(1 for d in root_skills.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())
    return 0, f"Built {skill_count} root skills and synced hooks.json + 3 plugin manifests (v{__version__}).\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m ags.build", description="Build root skills and plugin manifests.")
    parser.add_argument("--check", action="store_true", help="Exit 0 only if generated files are in sync.")
    parser.add_argument("--root", default=None, help="Repository root path override.")
    args = parser.parse_args(argv)
    rc, msg = run_build(Path(args.root) if args.root else None, check=args.check)
    sys.stdout.write(msg)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
