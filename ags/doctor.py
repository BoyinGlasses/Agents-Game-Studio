"""Health checks for enabled harnesses, hooks, engine CLIs, and duplicate skills."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from ags.checks import tomllib, _validate_toml_fallback
from ags.config import find_project_root, parse_frontmatter, resolve_config
from ags.hooks import run_hook_cli


def _check_json_file(path: Path) -> str | None:
    try:
        json.loads(path.read_text(encoding="utf-8-sig"))
        return None
    except Exception as exc:
        return f"{path.name}: invalid JSON ({exc})"


def _check_toml_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8-sig")
        if tomllib is not None:
            tomllib.loads(text)
            return None
        err = _validate_toml_fallback(text)
        return f"{path.name}: invalid TOML ({err})" if err else None
    except Exception as exc:
        return f"{path.name}: invalid TOML ({exc})"


def _detect_enabled_harnesses(root: Path) -> list[str]:
    found: list[str] = []
    if (root / ".codex").is_dir():
        found.append("codex")
    if (root / ".agents" / "hooks.json").is_file() or (root / ".agents" / "rules").is_dir():
        found.append("antigravity")
    if (root / "opencode.json").is_file() or (root / ".opencode").is_dir():
        found.append("opencode")
    if (root / ".claude" / "settings.json").is_file() or (root / "CLAUDE.md").is_file():
        found.append("claude")
    return found


def _collect_skill_names(skills_dir: Path) -> dict[str, list[str]]:
    """Map frontmatter/folder skill name -> relative directory paths."""
    found: dict[str, list[str]] = {}
    if not skills_dir.is_dir():
        return found
    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.is_file():
            continue
        meta, _ = parse_frontmatter(skill_md.read_text(encoding="utf-8-sig", errors="replace"))
        name = str(meta.get("name") or entry.name)
        found.setdefault(name, []).append(entry.name)
    return found


def run_doctor(root: Path | None = None) -> dict[str, Any]:
    """Run diagnostic health checks on an AGS workspace."""
    proj_root = find_project_root(root)
    checks: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []

    cfg = resolve_config(proj_root)
    if not cfg["project_configured"]:
        warnings.append("project.yaml not found (running outside initialized game project or unconfigured)")
    for note in cfg["notes"]:
        warnings.append(note)

    checks.append(
        {
            "name": "config_resolution",
            "status": "PASS" if cfg["project_configured"] else "WARN",
            "details": cfg["notes"],
        }
    )

    harnesses = _detect_enabled_harnesses(proj_root)
    harness_issues: list[str] = []
    for h in harnesses:
        if h == "codex":
            cfg_toml = proj_root / ".codex" / "config.toml"
            hooks_json = proj_root / ".codex" / "hooks.json"
            if cfg_toml.is_file():
                err = _check_toml_file(cfg_toml)
                if err:
                    harness_issues.append(f"codex/{err}")
            else:
                harness_issues.append("codex: missing .codex/config.toml")
            if hooks_json.is_file():
                err = _check_json_file(hooks_json)
                if err:
                    harness_issues.append(f"codex/{err}")
            else:
                harness_issues.append("codex: missing .codex/hooks.json")
        elif h == "antigravity":
            hooks_json = proj_root / ".agents" / "hooks.json"
            if hooks_json.is_file():
                err = _check_json_file(hooks_json)
                if err:
                    harness_issues.append(f"antigravity/{err}")
            else:
                harness_issues.append("antigravity: missing .agents/hooks.json")
        elif h == "opencode":
            oc_json = proj_root / "opencode.json"
            plugin_ts = proj_root / ".opencode" / "plugins" / "ags-hooks.ts"
            if oc_json.is_file():
                err = _check_json_file(oc_json)
                if err:
                    harness_issues.append(f"opencode/{err}")
            else:
                harness_issues.append("opencode: missing opencode.json")
            if not plugin_ts.is_file():
                harness_issues.append("opencode: missing .opencode/plugins/ags-hooks.ts")
        elif h == "claude":
            settings_json = proj_root / ".claude" / "settings.json"
            if settings_json.is_file():
                err = _check_json_file(settings_json)
                if err:
                    harness_issues.append(f"claude/{err}")
            else:
                harness_issues.append("claude: missing .claude/settings.json")

    errors.extend(harness_issues)
    checks.append(
        {
            "name": "enabled_harnesses",
            "status": "FAIL" if harness_issues else ("PASS" if harnesses else "WARN"),
            "harnesses": harnesses,
            "errors": harness_issues,
        }
    )

    # Hook execution test
    hook_errors: list[str] = []
    tested_harnesses = harnesses or ["codex", "antigravity", "opencode", "claude"]
    for h in tested_harnesses:
        rc, out, err = run_hook_cli(h, "session_start", json.dumps({"cwd": str(proj_root)}), root=proj_root)
        if rc != 0:
            hook_errors.append(f"{h} session_start returned rc={rc}: {err.strip()}")
        elif h in ("codex", "antigravity", "opencode") and out.strip():
            try:
                json.loads(out)
            except ValueError as exc:
                hook_errors.append(f"{h} session_start emitted invalid JSON: {exc}")

    # Standalone .ags/cli.py check if present
    cli_py = proj_root / ".ags" / "cli.py"
    if cli_py.is_file():
        try:
            proc = subprocess.run(
                [sys.executable, str(cli_py), "--help"],
                cwd=str(proj_root),
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if proc.returncode != 0:
                hook_errors.append(f".ags/cli.py --help failed: {proc.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            hook_errors.append(f".ags/cli.py execution failed: {exc}")

    errors.extend(hook_errors)
    checks.append(
        {
            "name": "hook_execution",
            "status": "FAIL" if hook_errors else "PASS",
            "tested": tested_harnesses,
            "errors": hook_errors,
        }
    )

    # Engine CLI availability
    engine_name = (cfg["engine"].get("name") or "none").lower()
    cli_probes = {
        "godot": ["godot", "godot4"],
        "unity": ["Unity", "dotnet"],
        "unreal": ["UnrealEditor-Cmd", "UnrealBuildTool"],
    }
    available_clis: dict[str, str | None] = {}
    for eng, bins in cli_probes.items():
        found_bin = next((shutil.which(b) for b in bins if shutil.which(b)), None)
        available_clis[eng] = found_bin

    if engine_name in cli_probes and not available_clis.get(engine_name):
        warnings.append(f"configured engine '{engine_name}' CLI not found in PATH")

    checks.append(
        {
            "name": "engine_cli_availability",
            "status": "PASS" if (engine_name not in cli_probes or available_clis.get(engine_name)) else "WARN",
            "configured_engine": engine_name,
            "available": available_clis,
        }
    )

    # Duplicate skill detection (skills/ vs .agents/skills/)
    root_skills = _collect_skill_names(proj_root / "skills")
    agents_skills = _collect_skill_names(proj_root / ".agents" / "skills")
    duplicates: list[str] = []
    overlap = sorted(set(root_skills) & set(agents_skills))
    for name in overlap:
        duplicates.append(
            f"duplicate skill '{name}' exists in both skills/ and .agents/skills/"
        )
    for label, skill_map in (("skills/", root_skills), (".agents/skills/", agents_skills)):
        for name, dirs in sorted(skill_map.items()):
            if len(dirs) > 1:
                duplicates.append(f"duplicate skill name '{name}' in {label}: {', '.join(dirs)}")

    warnings.extend(duplicates)
    checks.append(
        {
            "name": "duplicate_skills",
            "status": "WARN" if duplicates else "PASS",
            "root_skills_count": sum(len(v) for v in root_skills.values()),
            "project_skills_count": sum(len(v) for v in agents_skills.values()),
            "duplicates": duplicates,
        }
    )

    return {
        "ok": not errors,
        "project_root": str(proj_root).replace("\\", "/"),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def format_doctor_report(report: dict[str, Any]) -> str:
    """Format doctor health report as readable text."""
    lines = [f"AGS Doctor ({report['project_root']}) — {'OK' if report['ok'] else 'ISSUES FOUND'}"]
    for chk in report["checks"]:
        lines.append(f"  [{chk['status']}] {chk['name']}")
    if report["errors"]:
        lines.append("Errors:")
        lines.extend(f"  - {e}" for e in report["errors"])
    if report["warnings"]:
        lines.append("Warnings:")
        lines.extend(f"  - {w}" for w in report["warnings"])
    return "\n".join(lines) + "\n"
