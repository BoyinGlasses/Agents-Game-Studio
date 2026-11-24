"""Implementation of `ags init` and `ags sync` commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ags.adapters import ENGINE_CHOICES, HARNESS_CHOICES
from ags.adapters.antigravity import apply_antigravity
from ags.adapters.claude import apply_claude
from ags.adapters.codex import apply_codex
from ags.adapters.common import assemble_common
from ags.adapters.opencode import apply_opencode
from ags.config import get_yaml_key, load_yaml
from ags.doctor import _detect_enabled_harnesses

_ADAPTERS = {
    "codex": apply_codex,
    "antigravity": apply_antigravity,
    "opencode": apply_opencode,
    "claude": apply_claude,
}


def find_core_dir(explicit_core: Path | str | None = None) -> Path:
    """Locate the AGS `core/` template source tree."""
    if explicit_core is not None:
        cand = Path(explicit_core).resolve()
        if cand.is_dir():
            return cand
        raise FileNotFoundError(f"core directory not found: {cand}")

    repo_core = Path(__file__).resolve().parents[1] / "core"
    if repo_core.is_dir():
        return repo_core

    cwd_core = Path.cwd().resolve() / "core"
    if cwd_core.is_dir():
        return cwd_core

    raise FileNotFoundError(
        "Unable to locate AGS `core/` directory. Pass `--core <path>` when running outside the AGS repo."
    )


def parse_harnesses(raw: str | list[str] | tuple[str, ...] | None) -> list[str]:
    """Normalize `--harness` comma-separated values or list into validated harness names."""
    if raw is None:
        return ["universal"]
    tokens: list[str] = []
    items = [raw] if isinstance(raw, str) else list(raw)
    for item in items:
        for part in str(item).split(","):
            p = part.strip().lower()
            if p:
                tokens.append(p)
    if not tokens:
        return ["universal"]
    if "all" in tokens:
        return ["codex", "antigravity", "opencode", "claude"]
    seen: list[str] = []
    for tok in tokens:
        if tok not in HARNESS_CHOICES:
            raise ValueError(
                f"Unknown harness '{tok}'. Expected one of: {', '.join(HARNESS_CHOICES)}, all"
            )
        if tok not in seen:
            seen.append(tok)
    return seen


def run_init(
    target: Path | str,
    engine: str = "none",
    harnesses: str | list[str] | tuple[str, ...] | None = "universal",
    rigor: str | None = None,
    name: str | None = None,
    core_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Assemble a new AGS v2 game project into `target`."""
    eng = engine.strip().lower()
    if eng not in ENGINE_CHOICES:
        raise ValueError(f"Unknown engine '{engine}'. Expected: {', '.join(ENGINE_CHOICES)}")

    selected_harnesses = parse_harnesses(harnesses)
    core_path = find_core_dir(core_dir)
    target_path = Path(target).resolve()

    roles = assemble_common(
        core_path,
        target_path,
        engine=eng,
        rigor=rigor,
        project_name=name,
        sync_only=False,
    )

    written: list[str] = []
    for h in selected_harnesses:
        if h == "universal":
            continue
        adapter_fn = _ADAPTERS[h]
        for wpath in adapter_fn(target_path, roles):
            written.append(str(wpath.relative_to(target_path)).replace("\\", "/"))

    return {
        "target": str(target_path).replace("\\", "/"),
        "engine": eng,
        "harnesses": selected_harnesses,
        "roles_count": len(roles),
        "harness_files_written": len(written),
    }


def run_sync(
    target: Path | str = ".",
    engine: str | None = None,
    harnesses: str | list[str] | tuple[str, ...] | None = None,
    core_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Sync an existing game project's `.ags/`, `.agents/skills/`, and harness adapters."""
    target_path = Path(target).resolve()
    core_path = find_core_dir(core_dir)

    if engine:
        eng = engine.strip().lower()
    else:
        py_data = load_yaml(target_path / "project.yaml").data
        ename = (get_yaml_key(py_data, "engine.name") or "none").lower()
        eng = "unreal" if ename.startswith("unreal") else ename
    if eng not in ENGINE_CHOICES:
        raise ValueError(f"Unknown engine '{eng}'. Expected: {', '.join(ENGINE_CHOICES)}")

    if harnesses is not None:
        selected_harnesses = parse_harnesses(harnesses)
    else:
        detected = _detect_enabled_harnesses(target_path)
        selected_harnesses = detected or ["universal"]

    roles = assemble_common(
        core_path,
        target_path,
        engine=eng,
        sync_only=True,
    )

    written: list[str] = []
    for h in selected_harnesses:
        if h == "universal":
            continue
        adapter_fn = _ADAPTERS[h]
        for wpath in adapter_fn(target_path, roles):
            written.append(str(wpath.relative_to(target_path)).replace("\\", "/"))

    return {
        "target": str(target_path).replace("\\", "/"),
        "engine": eng,
        "harnesses": selected_harnesses,
        "roles_count": len(roles),
        "harness_files_written": len(written),
    }
