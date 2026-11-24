"""Common project assembly and standalone .ags/cli.py bundler."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ags.config import parse_frontmatter

_ENGINE_DISPLAY = {
    "godot": "Godot",
    "unity": "Unity",
    "unreal": "Unreal",
}

_ENGINE_CODE_ROOT = {
    "godot": "src",
    "unity": "Assets",
    "unreal": "Source",
}

_DEFAULT_PROJECT_YAML = """\
# Agents Game Studio (AGS v2) project configuration — single source of truth.
# Local personal overrides belong in `project.local.yaml` (gitignored).
# Run `python .ags/cli.py preflight ags-start` or `ags-settings` to inspect resolved config.

schema_version: 1

framework:
  version: 2.0.0
"""

_DEFAULT_GITIGNORE = """\
# === AGS Local & Ephemeral State ===
project.local.yaml
.ags/state/
production/session-logs/
production/session-state/
.scratch/
__pycache__/
*.pyc
.DS_Store
Thumbs.db
"""

_BUNDLE_TEMPLATE = '''#!/usr/bin/env python3
"""Standalone self-contained Agents Game Studio (AGS) v2 CLI."""

from __future__ import annotations

import importlib.abc
import importlib.util
import json
import sys
from types import ModuleType

_BUNDLED_MODULES: dict[str, str] = __MODULES_JSON__


class _BundledLoader(importlib.abc.Loader):
    def __init__(self, fullname: str, source: str, is_pkg: bool) -> None:
        self.fullname = fullname
        self.source = source
        self.is_pkg = is_pkg

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType | None:
        return None

    def exec_module(self, module: ModuleType) -> None:
        module.__file__ = f"<ags-bundle:{self.fullname}>"
        if self.is_pkg:
            module.__path__ = [f"<ags-bundle:{self.fullname}>"]
            module.__package__ = self.fullname
        else:
            module.__package__ = self.fullname.rpartition(".")[0]
        exec(compile(self.source, module.__file__, "exec"), module.__dict__)


class _BundledFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path: object = None, target: object = None):
        if fullname != "ags" and not fullname.startswith("ags."):
            return None
        mod_rel = fullname.replace(".", "/")
        pkg_key = f"{mod_rel}/__init__.py"
        file_key = f"{mod_rel}.py"
        if pkg_key in _BUNDLED_MODULES:
            return importlib.util.spec_from_loader(
                fullname,
                _BundledLoader(fullname, _BUNDLED_MODULES[pkg_key], is_pkg=True),
                is_package=True,
            )
        if file_key in _BUNDLED_MODULES:
            return importlib.util.spec_from_loader(
                fullname,
                _BundledLoader(fullname, _BUNDLED_MODULES[file_key], is_pkg=False),
                is_package=False,
            )
        return None


def main() -> int:
    if not any(isinstance(f, _BundledFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _BundledFinder())
    import ags

    ags._EMBEDDED_MODULES = _BUNDLED_MODULES  # type: ignore[attr-defined]
    from ags.__main__ import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
'''


@dataclass
class RoleSpec:
    """Normalized agent/lens definition loaded from core/agents/."""

    name: str
    description: str
    sandbox_mode: str
    model_reasoning_effort: str
    body: str
    category: str  # "core" | "engine" | "lens"
    meta: dict[str, Any]


def collect_ags_sources() -> dict[str, str]:
    """Collect all Python source modules under `ags/` for standalone bundling."""
    import ags as ags_pkg

    embedded = getattr(ags_pkg, "_EMBEDDED_MODULES", None)
    if isinstance(embedded, dict) and embedded:
        return dict(embedded)

    ags_dir = Path(__file__).resolve().parents[1]
    sources: dict[str, str] = {}
    for py_file in sorted(ags_dir.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue
        rel = "ags/" + str(py_file.relative_to(ags_dir)).replace("\\", "/")
        sources[rel] = py_file.read_text(encoding="utf-8")
    return sources


def bundle_standalone_cli(dest_cli: Path) -> None:
    """Write a self-contained `.ags/cli.py` runnable with zero external repo deps."""
    sources = collect_ags_sources()
    dest_cli.parent.mkdir(parents=True, exist_ok=True)
    rendered = _BUNDLE_TEMPLATE.replace("__MODULES_JSON__", json.dumps(sources, ensure_ascii=False))
    dest_cli.write_text(rendered, encoding="utf-8")


def load_roles(core_dir: Path, engine: str) -> list[RoleSpec]:
    """Load core agents, selected engine pack agents, and domain lenses."""
    agents_dir = core_dir / "agents"
    sources: list[tuple[str, Path]] = []

    core_agents = agents_dir / "core"
    if core_agents.is_dir():
        sources.extend(("core", p) for p in sorted(core_agents.glob("*.md")))

    if engine and engine != "none":
        eng_agents = agents_dir / "engines" / engine
        if eng_agents.is_dir():
            sources.extend(("engine", p) for p in sorted(eng_agents.glob("*.md")))

    lens_agents = agents_dir / "lenses"
    if lens_agents.is_dir():
        sources.extend(("lens", p) for p in sorted(lens_agents.glob("*.md")))

    roles: list[RoleSpec] = []
    for category, md_path in sources:
        text = md_path.read_text(encoding="utf-8-sig", errors="replace")
        meta, body = parse_frontmatter(text)
        name = str(meta.get("name") or md_path.stem)
        desc = str(meta.get("description") or f"{name} specialist role")
        sandbox = str(meta.get("sandbox_mode") or "workspace-write")
        effort = str(meta.get("model_reasoning_effort") or "medium")
        roles.append(
            RoleSpec(
                name=name,
                description=desc,
                sandbox_mode=sandbox,
                model_reasoning_effort=effort,
                body=body.strip(),
                category=category,
                meta=meta,
            )
        )
    return roles


def _copy_tree_clean(src: Path, dst: Path) -> None:
    if not src.is_dir():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "Thumbs.db"),
    )


def _render_project_yaml(
    core_dir: Path,
    engine: str,
    rigor: str | None = None,
    project_name: str | None = None,
) -> str:
    template_candidates = [
        core_dir / "project.yaml",
        core_dir / "templates" / "project.yaml",
    ]
    base_text = _DEFAULT_PROJECT_YAML
    for cand in template_candidates:
        if cand.is_file():
            base_text = cand.read_text(encoding="utf-8-sig", errors="replace")
            break

    lines = [base_text.rstrip()]
    if project_name:
        lines.extend(["", "project:", f'  name: "{project_name}"'])
    if engine and engine != "none":
        eng_disp = _ENGINE_DISPLAY.get(engine, engine.capitalize())
        lines.extend(["", "engine:", f"  name: {eng_disp}"])
    if rigor:
        lines.extend(["", "modes:", f"  rigor: {rigor}"])
    return "\n".join(lines) + "\n"


def _sync_project_yaml_engine(py_path: Path, engine: str) -> None:
    if not engine or engine == "none" or not py_path.is_file():
        return
    eng_disp = _ENGINE_DISPLAY.get(engine, engine.capitalize())
    text = py_path.read_text(encoding="utf-8-sig", errors="replace")
    if re.search(r"^engine:\s*$", text, re.M):
        updated = re.sub(r"(^engine:\s*\n(?:\s+[^\n]+\n)*?\s+name:\s*).*$", rf"\1{eng_disp}", text, flags=re.M)
        if updated != text:
            py_path.write_text(updated, encoding="utf-8")
            return
    if "engine:" not in text:
        py_path.write_text(text.rstrip() + f"\n\nengine:\n  name: {eng_disp}\n", encoding="utf-8")


def assemble_common(
    core_dir: Path,
    target_dir: Path,
    engine: str,
    rigor: str | None = None,
    project_name: str | None = None,
    sync_only: bool = False,
) -> list[RoleSpec]:
    """Assemble engine-filtered common AGS files into `target_dir` and return loaded roles."""
    target_dir.mkdir(parents=True, exist_ok=True)

    # Root AGENTS.md
    agents_md_src = core_dir / "rules" / "AGENTS.md"
    if agents_md_src.is_file():
        shutil.copy2(agents_md_src, target_dir / "AGENTS.md")

    # project.yaml
    py_dest = target_dir / "project.yaml"
    if not sync_only or not py_dest.is_file():
        py_dest.write_text(
            _render_project_yaml(core_dir, engine, rigor=rigor, project_name=project_name),
            encoding="utf-8",
        )
    else:
        _sync_project_yaml_engine(py_dest, engine)

    # .gitignore
    gi_dest = target_dir / ".gitignore"
    if not gi_dest.is_file():
        gi_dest.write_text(_DEFAULT_GITIGNORE, encoding="utf-8")

    # Skills: core/skills/ -> .agents/skills/
    _copy_tree_clean(core_dir / "skills", target_dir / ".agents" / "skills")

    # Selected engine reference ONLY: core/engine-reference/<engine>/ -> docs/engine-reference/<engine>/
    ref_dst_root = target_dir / "docs" / "engine-reference"
    if engine and engine != "none":
        ref_src = core_dir / "engine-reference" / engine
        if ref_dst_root.is_dir():
            for other in ("godot", "unity", "unreal"):
                if other != engine and (ref_dst_root / other).is_dir():
                    shutil.rmtree(ref_dst_root / other)
        ref_dst_root.mkdir(parents=True, exist_ok=True)
        readme_src = core_dir / "engine-reference" / "README.md"
        if readme_src.is_file():
            shutil.copy2(readme_src, ref_dst_root / "README.md")
        if ref_src.is_dir():
            _copy_tree_clean(ref_src, ref_dst_root / engine)
    elif ref_dst_root.is_dir() and sync_only:
        for other in ("godot", "unity", "unreal"):
            if (ref_dst_root / other).is_dir():
                shutil.rmtree(ref_dst_root / other)

    # Roles: core + selected engine + lenses -> .ags/roles/
    roles = load_roles(core_dir, engine)
    roles_dst = target_dir / ".ags" / "roles"
    if roles_dst.is_dir():
        shutil.rmtree(roles_dst)
    roles_dst.mkdir(parents=True, exist_ok=True)

    # Copy raw source role files into flat .ags/roles/
    agents_src = core_dir / "agents"
    for src_dir in [agents_src / "core", agents_src / "lenses"] + (
        [agents_src / "engines" / engine] if engine and engine != "none" else []
    ):
        if src_dir.is_dir():
            for md_file in sorted(src_dir.glob("*.md")):
                shutil.copy2(md_file, roles_dst / md_file.name)

    # Gates, templates, rules, workflow catalog -> .ags/
    _copy_tree_clean(core_dir / "gates", target_dir / ".ags" / "gates")
    _copy_tree_clean(core_dir / "templates", target_dir / ".ags" / "templates")

    rules_dst = target_dir / ".ags" / "rules"
    if rules_dst.is_dir():
        shutil.rmtree(rules_dst)
    rules_dst.mkdir(parents=True, exist_ok=True)
    rules_src = core_dir / "rules"
    if rules_src.is_dir():
        for rule_file in sorted(rules_src.glob("*.md")):
            if rule_file.name == "AGENTS.md":
                continue
            shutil.copy2(rule_file, rules_dst / rule_file.name)

    catalog_src = core_dir / "workflow-catalog.yaml"
    if catalog_src.is_file():
        shutil.copy2(catalog_src, target_dir / ".ags" / "workflow-catalog.yaml")

    # Standalone .ags/cli.py
    bundle_standalone_cli(target_dir / ".ags" / "cli.py")

    # Scaffold basic workspace directories if fresh init
    if not sync_only:
        (target_dir / "design" / "gdd").mkdir(parents=True, exist_ok=True)
        (target_dir / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
        (target_dir / "production" / "session-state").mkdir(parents=True, exist_ok=True)
        code_root = _ENGINE_CODE_ROOT.get(engine)
        if code_root:
            (target_dir / code_root).mkdir(parents=True, exist_ok=True)
        # Skip assets/data on Unity to avoid colliding with Assets/ on case-insensitive filesystems.
        if engine == "unreal":
            (target_dir / "Content" / "Data").mkdir(parents=True, exist_ok=True)
        elif engine != "unity":
            (target_dir / "assets" / "data").mkdir(parents=True, exist_ok=True)

    return roles
