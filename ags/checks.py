"""Ported CCGS studio checks, tree hashing, and engine-aware static validators."""

from __future__ import annotations

import datetime as _dt
import glob as _glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ags.config import (
    find_project_root,
    get_yaml_key,
    load_yaml,
    parse_yaml_with_diagnostics,
)

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None  # type: ignore[assignment]


@dataclass
class CheckResult:
    """Result of running an observation or validation check."""

    returncode: int = 0
    stdout: str = ""
    stderr: str = ""


NOT_A_SYSTEM_GDD_EXACT = frozenset(
    {
        "game-concept.md",
        "systems-index.md",
        "game-pillars.md",
        "gameplay-tags.md",
        "fixture-swap-ledger.md",
        "entity-registry.md",
    }
)

IGNORED_DIRS = frozenset(
    {
        ".git",
        ".godot",
        "Library",
        "Temp",
        "Obj",
        "Binaries",
        "DerivedDataCache",
        "Intermediate",
        "Saved",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        ".mypy_cache",
        ".pytest_cache",
    }
)

_GDD_SECTIONS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Overview", re.compile(r"^##+\s+(?:[0-9]+[.)]?\s*)?Overview", re.I | re.M)),
    ("Player Fantasy", re.compile(r"^##+\s+(?:[0-9]+[.)]?\s*)?Player Fantasy", re.I | re.M)),
    ("Detailed Rules", re.compile(r"^##+\s+(?:[0-9]+[.)]?\s*)?Detailed (?:Rules|Design)", re.I | re.M)),
    ("Formulas", re.compile(r"^##+\s+(?:[0-9]+[.)]?\s*)?Formulas", re.I | re.M)),
    ("Edge Cases", re.compile(r"^##+\s+(?:[0-9]+[.)]?\s*)?Edge Cases", re.I | re.M)),
    ("Dependencies", re.compile(r"^##+\s+(?:[0-9]+[.)]?\s*)?Dependencies", re.I | re.M)),
    ("Tuning Knobs", re.compile(r"^##+\s+(?:[0-9]+[.)]?\s*)?Tuning Knobs", re.I | re.M)),
    ("Acceptance Criteria", re.compile(r"^##+\s+(?:[0-9]+[.)]?\s*)?Acceptance Criteria", re.I | re.M)),
)

_POSIX_CLASSES: dict[str, str] = {
    "[:space:]": r" \t\n\r\f\v",
    "[:blank:]": r" \t",
    "[:digit:]": r"0-9",
    "[:alpha:]": r"A-Za-z",
    "[:alnum:]": r"A-Za-z0-9",
    "[:upper:]": r"A-Z",
    "[:lower:]": r"a-z",
    "[:word:]": r"A-Za-z0-9_",
    "[:punct:]": r"!\"#$%&'()*+,\-./:;<=>?@\[\]^_`{|}~\\",
}


def _posix_ere_to_python(pattern: str) -> re.Pattern[str]:
    converted = pattern
    for posix_cls, chars in _POSIX_CLASSES.items():
        converted = converted.replace(posix_cls, chars)
    return re.compile(converted)


def _is_system_gdd(path: Path) -> bool:
    name = path.name
    if name in NOT_A_SYSTEM_GDD_EXACT or name.startswith("gdd-cross-review-"):
        return False
    return True


def _norm_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _run_cmd(args: list[str], cwd: Path, stdin_bytes: bytes | None = None, timeout: int = 15) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        input=stdin_bytes,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def _git_blob_hash_file(path: Path) -> str:
    """Hash a file via `git hash-object`, falling back to pure-Python git blob SHA-1."""
    git_bin = shutil.which("git")
    if git_bin:
        try:
            proc = subprocess.run(
                [git_bin, "hash-object", "--", str(path)],
                capture_output=True,
                timeout=10,
                check=False,
            )
            if proc.returncode == 0:
                out = proc.stdout.decode("utf-8", errors="replace").strip()
                if out:
                    return out
        except OSError:
            pass
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _git_blob_hash_bytes(data: bytes) -> str:
    """Hash raw bytes via `git hash-object --stdin`, falling back to git blob SHA-1."""
    git_bin = shutil.which("git")
    if git_bin:
        try:
            proc = subprocess.run(
                [git_bin, "hash-object", "--stdin"],
                input=data,
                capture_output=True,
                timeout=10,
                check=False,
            )
            if proc.returncode == 0:
                out = proc.stdout.decode("utf-8", errors="replace").strip()
                if out:
                    return out
        except OSError:
            pass
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


# ---------------------------------------------------------------------------
# 1. adr-dep-graph
# ---------------------------------------------------------------------------

def adr_dep_graph(adr_dir: Path | str | None = None, root: Path | None = None) -> CheckResult:
    """Build ADR dependency graph and detect cycles using Kahn's algorithm."""
    proj_root = find_project_root(root)
    target_dir = Path(adr_dir) if adr_dir is not None else (proj_root / "docs" / "architecture")

    if not target_dir.is_dir():
        adr_files: list[Path] = []
    else:
        adr_files = sorted(
            p for p in target_dir.iterdir()
            if p.is_file() and p.name.startswith("adr-") and p.name.endswith(".md")
        )

    if not adr_files:
        lines = [
            "ADRS: 0",
            "EDGES:",
            f"  (none — no ADRs in {_norm_path(target_dir)})",
        ]
        return CheckResult(0, "\n".join(lines) + "\n")

    edges: list[tuple[str, str]] = []
    no_deps: list[str] = []

    for fpath in adr_files:
        m_id = re.search(r"adr-[0-9]+", fpath.name, re.I)
        from_id = m_id.group(0).lower() if m_id else fpath.stem.lower()
        try:
            text = fpath.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            no_deps.append(from_id)
            continue

        in_sec = False
        deps_rows: list[str] = []
        for line in text.splitlines():
            if line.startswith("## "):
                in_sec = "## ADR Dependencies" in line
            elif in_sec and "**Depends On**" in line:
                deps_rows.append(line)

        if not deps_rows:
            no_deps.append(from_id)
            continue

        targets = sorted(
            {m.lower() for row in deps_rows for m in re.findall(r"adr-[0-9]+", row, re.I)}
        )
        for t in targets:
            if t != from_id:
                edges.append((from_id, t))

    out: list[str] = [f"ADRS: {len(adr_files)}", "EDGES:"]
    if not edges:
        out.append("  (none)")
    else:
        for a, b in edges:
            out.append(f"  {a} -> {b}")

    if no_deps:
        out.append("NO_DEPS_SECTION: " + ", ".join(no_deps))

    if edges:
        nodes: set[str] = set()
        out_deg: dict[str, int] = {}
        rev_adj: dict[str, list[str]] = {}
        fwd_adj: dict[str, list[str]] = {}
        for a, b in edges:
            nodes.add(a)
            nodes.add(b)
            out_deg[a] = out_deg.get(a, 0) + 1
            out_deg.setdefault(b, 0)
            rev_adj.setdefault(b, []).append(a)
            fwd_adj.setdefault(a, []).append(b)

        queue = sorted(n for n in nodes if out_deg.get(n, 0) == 0)
        removed: set[str] = set()
        while queue:
            cur = queue.pop(0)
            if cur in removed:
                continue
            removed.add(cur)
            for parent in rev_adj.get(cur, ()):
                out_deg[parent] -= 1
                if out_deg[parent] == 0:
                    queue.append(parent)

        remaining = sorted(n for n in nodes if n not in removed)
        for node in remaining:
            outs = "".join(f" -> {dst}" for dst in fwd_adj.get(node, ()))
            out.append(f"CYCLE: {node}{outs}")

    return CheckResult(0, "\n".join(out) + "\n")


# ---------------------------------------------------------------------------
# 2. gdd-structure-check
# ---------------------------------------------------------------------------

def _check_single_gdd(fpath: Path) -> list[str]:
    try:
        content = fpath.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        content = ""
    present: list[str] = []
    absent: list[str] = []
    for label, pattern in _GDD_SECTIONS:
        if pattern.search(content):
            present.append(label)
        else:
            absent.append(label)
    lines = [f"{fpath.name} PRESENT: {','.join(present)}"]
    if absent:
        lines.append(f"{fpath.name} ABSENT:  {','.join(absent)}")
    return lines


def gdd_structure_check(target: Path | str | None = None, root: Path | None = None) -> CheckResult:
    """Report which canonical GDD sections are present or absent per system GDD."""
    proj_root = find_project_root(root)
    if target is not None:
        tpath = Path(target)
        if not tpath.is_absolute():
            tpath = proj_root / tpath
        if tpath.is_file():
            return CheckResult(0, "\n".join(_check_single_gdd(tpath)) + "\n")
        if not tpath.is_dir():
            return CheckResult(1, "", f"Not found: {target}\n")
        gdd_dir = tpath
    else:
        gdd_dir = proj_root / "design" / "gdd"

    if not gdd_dir.is_dir():
        return CheckResult(0, "No system GDDs found in design/gdd/.\n")

    files = sorted(
        p for p in gdd_dir.iterdir()
        if p.is_file() and p.suffix == ".md" and _is_system_gdd(p)
    )
    if not files:
        return CheckResult(0, "No system GDDs found in design/gdd/.\n")

    lines: list[str] = []
    for fpath in files:
        lines.extend(_check_single_gdd(fpath))
    return CheckResult(0, "\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# 3. artifact-check
# ---------------------------------------------------------------------------

def _find_catalog(root: Path) -> Path | None:
    candidates = [
        root / ".ags" / "workflow-catalog.yaml",
        root / ".claude" / "docs" / "workflow-catalog.yaml",
        root / "core" / "workflow-catalog.yaml",
    ]
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


def _match_files(root: Path, pat: str | None) -> list[Path]:
    if not pat:
        return []
    full = os.path.join(str(root), pat.replace("/", os.sep))
    return sorted(Path(p) for p in _glob.glob(full, recursive=True) if os.path.isfile(p))


def _pattern_hits(files: list[Path], pattern: str | None) -> list[Path]:
    if not pattern:
        return files
    compiled = _posix_ere_to_python(pattern)
    hits: list[Path] = []
    for fpath in files:
        try:
            text = fpath.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        if compiled.search(text):
            hits.append(fpath)
    return hits


def _evaluate_artifact(root: Path, art: dict[str, Any] | None) -> tuple[str, str, dict[str, str]]:
    if not art:
        return "NO_CHECK", "none", {}

    any_of = art.get("any_of")
    if isinstance(any_of, list) and any_of:
        for idx, alt in enumerate(any_of, 1):
            if not isinstance(alt, dict):
                continue
            files = _match_files(root, alt.get("glob"))
            if not files:
                continue
            hits = _pattern_hits(files, alt.get("pattern"))
            if hits:
                return "PRESENT", "any_of", {"match": str(alt.get("glob")), "alt": str(idx)}
        return "ABSENT", "any_of", {"alts": str(len(any_of))}

    glob_pat = art.get("glob")
    if not glob_pat:
        note = art.get("note")
        return "NO_CHECK", "none", ({"note": str(note)} if note else {})

    files = _match_files(root, str(glob_pat))
    if not files:
        return "ABSENT", "glob", {"glob": str(glob_pat)}

    pat = art.get("pattern")
    hits = _pattern_hits(files, str(pat) if pat else None)
    if pat and not hits:
        return "PATTERN_MISS", "glob", {"glob": str(glob_pat), "found": str(len(files))}

    counted = hits if pat else files
    try:
        need = int(art.get("min_count") or 1)
    except (TypeError, ValueError):
        need = 1
    if len(counted) < need:
        return "SHORT", "glob", {"glob": str(glob_pat), "count": str(len(counted)), "min": str(need)}

    details: dict[str, str] = {"count": str(len(counted))}
    if need > 1:
        details["min"] = str(need)
    return "PRESENT", "glob", details


def artifact_check(phase: str | None = None, root: Path | None = None) -> CheckResult:
    """Evaluate workflow-catalog.yaml step artifacts against files on disk."""
    proj_root = find_project_root(root)
    catalog_path = _find_catalog(proj_root)
    if catalog_path is None:
        return CheckResult(1, "", f"artifact-check: catalog not found under {_norm_path(proj_root)}\n")

    parsed = load_yaml(catalog_path).data
    raw_phases = parsed.get("phases")
    if not isinstance(raw_phases, dict):
        raw_phases = {}

    phases_list: list[tuple[str, list[dict[str, Any]]]] = []
    for pid, pinfo in raw_phases.items():
        steps = pinfo.get("steps") if isinstance(pinfo, dict) else []
        if not isinstance(steps, list):
            steps = []
        phases_list.append((str(pid), [s for s in steps if isinstance(s, dict)]))

    selected = [(pid, steps) for pid, steps in phases_list if not phase or pid == phase]
    if phase and not selected:
        known = ", ".join(pid for pid, _ in phases_list) or "(none parsed)"
        return CheckResult(2, "", f"artifact-check: unknown phase '{phase}' (known: {known})\n")

    total_steps = sum(len(steps) for _, steps in selected)
    no_check = 0
    rows: list[str] = []
    for pid, steps in selected:
        rows.append(f"PHASE: {pid}")
        for st in steps:
            art = st.get("artifact")
            art_dict = art if isinstance(art, dict) else None
            status, kind, det = _evaluate_artifact(proj_root, art_dict)
            if status == "NO_CHECK":
                no_check += 1
            extra = "".join(f" {k}={v}" for k, v in sorted(det.items()) if v is not None)
            req = str(bool(st.get("required", False))).lower()
            rep = str(bool(st.get("repeatable", False))).lower()
            rows.append(f"  STEP: {st.get('id', '')} required={req} repeatable={rep} check={kind} status={status}{extra}")

    rel_cat = _norm_path(os.path.relpath(catalog_path, proj_root))
    header = [
        f"CATALOG: {rel_cat}",
        f"ROOT: {_norm_path(proj_root)}",
        f"PHASES: {len(selected)}",
        f"STEPS: {total_steps}",
        f"NO_CHECK: {no_check}",
    ]
    return CheckResult(0, "\n".join(header + rows) + "\n")


# ---------------------------------------------------------------------------
# 4. project-coherence
# ---------------------------------------------------------------------------

def project_coherence(root: Path | None = None) -> CheckResult:
    """Compare declared settings in project.yaml against engine files and binaries."""
    proj_root = find_project_root(root)
    checked = 0
    differs = 0
    skipped = 0
    out: list[str] = ["=== project coherence ==="]

    def match(msg: str) -> None:
        nonlocal checked
        checked += 1
        out.append(f"[MATCH]       {msg}")

    def diff(msg: str) -> None:
        nonlocal checked, differs
        checked += 1
        differs += 1
        out.append(f"[DIFFERS]     {msg}")

    def skip(msg: str) -> None:
        nonlocal skipped
        skipped += 1
        out.append(f"[NOT CHECKED] {msg}")

    def summarise() -> CheckResult:
        out.extend(
            [
                "",
                f"checked {checked} · differs {differs} · not checked {skipped}",
                "",
                "Observations only — no verdict. 'not checked' is not agreement:",
                "each line above names why that comparison could not be made.",
            ]
        )
        return CheckResult(0, "\n".join(out) + "\n")

    py_path = proj_root / "project.yaml"
    if not py_path.is_file():
        skip("everything — no project.yaml at the repo root. Run ags-start.")
        return summarise()

    data = load_yaml(py_path).data
    engine = get_yaml_key(data, "engine.name") or ""
    version = get_yaml_key(data, "engine.version") or ""
    rendering = get_yaml_key(data, "engine.rendering") or ""
    physics = get_yaml_key(data, "engine.physics") or ""

    if not engine or engine.lower() == "none":
        skip("every engine check — project.yaml has no engine.name. Run ags-settings.")
        return summarise()

    engine_lc = engine.lower()
    verfile = proj_root / "docs" / "engine-reference" / engine_lc / "VERSION.md"
    verfile_rel = f"docs/engine-reference/{engine_lc}/VERSION.md"

    if not verfile.is_file():
        skip(f"pinned-reference checks — {verfile_rel} does not exist")
    else:
        vtext = verfile.read_text(encoding="utf-8-sig", errors="replace")
        pinned = ""
        installed_row = ""
        for line in vtext.splitlines():
            m_pin = re.match(r"^\|\s*\*\*Engine Version\*\*\s*\|\s*(.*?)\s*\|$", line)
            if m_pin:
                pinned = m_pin.group(1).strip()
            m_inst = re.match(r"^\|\s*\*\*Installed at pin time\*\*\s*\|\s*(.*?)\s*\|$", line)
            if m_inst:
                installed_row = m_inst.group(1).strip()

        if not installed_row:
            diff(
                f"{verfile_rel} has no 'Installed at pin time' row. "
                "ags-settings is required to write one; its absence means the probe result was never recorded."
            )
        elif "NOT DETERMINED" in installed_row:
            skip(
                f"pinned-vs-installed — {verfile_rel} records '{installed_row}'. "
                "A probe that did not run has not established a match."
            )
        else:
            match(f"VERSION.md records the installed version at pin time: {installed_row}")

        if not pinned:
            skip(f"project.yaml version vs pinned reference — no Engine Version row in {verfile_rel}")
        elif not version:
            skip("project.yaml version vs pinned reference — project.yaml has no engine.version")
        elif version in pinned:
            match(f"engine.version ({version}) agrees with {verfile_rel} ({pinned})")
        else:
            diff(
                f"engine.version is '{version}' but {verfile_rel} pins '{pinned}'. "
                "Agents consult the reference file, so they will answer for a version the project does not declare."
            )

    probe = ""
    bin_map = {
        "godot": ("godot", ["--version"]),
        "unity": ("Unity", ["-version"]),
        "unreal": ("UnrealEditor-Cmd", ["-version"]),
    }
    if engine_lc in bin_map:
        bname, bargs = bin_map[engine_lc]
        exe = shutil.which(bname)
        if exe:
            try:
                res = subprocess.run([exe, *bargs], capture_output=True, text=True, timeout=10, check=False)
                first = (res.stdout or res.stderr or "").splitlines()
                probe = first[0].strip() if first else ""
            except (OSError, subprocess.TimeoutExpired):
                probe = ""

    if not probe:
        skip(f"declared version vs installed binary — no {engine} binary found on PATH.")
    elif not version:
        skip("declared version vs installed binary — project.yaml has no engine.version")
    else:
        want_m = re.match(r"^([0-9]+\.[0-9]+)", version)
        got_m = re.search(r"([0-9]+\.[0-9]+)", probe)
        want = want_m.group(1) if want_m else ""
        got = got_m.group(1) if got_m else ""
        if want and want == got:
            match(f"engine.version {version} matches the installed binary ({probe})")
        else:
            diff(
                f"engine.version is '{version}' but the binary on PATH is '{probe}'. "
                "Build, test and smoke commands target the declared version."
            )

    godot_file = proj_root / "project.godot"
    if engine_lc != "godot":
        skip(f"project-file checks — implemented for Godot only; {engine} has no single equivalent file")
    elif not godot_file.is_file():
        skip("project-file checks — no project.godot in this repo")
    else:
        gtext = godot_file.read_text(encoding="utf-8-sig", errors="replace")
        rm_match = re.search(r'^renderer/rendering_method\s*=\s*"?([a-z_]+)"?', gtext, re.M)
        method = rm_match.group(1) if rm_match else ""
        if not method:
            skip("rendering — project.godot sets no renderer/rendering_method")
        elif not rendering:
            skip("rendering — project.yaml has no engine.rendering")
        else:
            rend_map = {
                "compatibility": "gl_compatibility",
                "gl compatibility": "gl_compatibility",
                "forward+": "forward_plus",
                "forward_plus": "forward_plus",
                "forward plus": "forward_plus",
                "mobile": "mobile",
            }
            want_m_str = rend_map.get(rendering.lower(), "")
            if not want_m_str:
                skip(f"rendering — engine.rendering '{rendering}' is not mapped to a Godot rendering_method")
            elif want_m_str == method:
                match(f"engine.rendering ({rendering}) agrees with project.godot ({method})")
            else:
                diff(
                    f"engine.rendering is '{rendering}' (expects {want_m_str}) but project.godot runs '{method}'."
                )

        if not physics:
            skip("physics — project.yaml has no engine.physics")
        elif "jolt" in physics.lower():
            node2d_re = re.compile(r"\b(Node2D|CharacterBody2D|RigidBody2D|Area2D|StaticBody2D)\b")
            found_2d = False
            src_dir = proj_root / "src"
            if src_dir.is_dir():
                for p in src_dir.rglob("*"):
                    if p.is_file() and p.suffix in (".gd", ".tscn"):
                        try:
                            if node2d_re.search(p.read_text(encoding="utf-8-sig", errors="replace")):
                                found_2d = True
                                break
                        except OSError:
                            pass
            if found_2d:
                diff(
                    "engine.physics is 'Jolt', but 2D nodes were found under src/. "
                    "Jolt is Godot's 3D engine; 2D uses Godot Physics 2D."
                )
            else:
                match(f"engine.physics ({physics}) — no 2D nodes found under src/ to contradict it")
        else:
            match(f"engine.physics ({physics})")

    build_cmd = get_yaml_key(data, "commands.build") or ""
    test_cmd = get_yaml_key(data, "commands.test") or ""
    if not build_cmd and not test_cmd:
        skip("command checks — project.yaml declares no commands.build or commands.test")
    else:
        if re.search(r"export-(debug|release|pack)", build_cmd):
            if (proj_root / "export_presets.cfg").is_file():
                match("commands.build names an export preset and export_presets.cfg exists")
            else:
                diff(f"commands.build is '{build_cmd}' but there is no export_presets.cfg.")
        runner_m = re.search(r"([A-Za-z0-9_/.-]+\.(?:gd|cs|py|sh))", test_cmd)
        if runner_m:
            runner = runner_m.group(1)
            if (proj_root / runner).is_file():
                match(f"commands.test runner exists ({runner})")
            else:
                diff(f"commands.test is '{test_cmd}' but '{runner}' does not exist.")

    return summarise()


# ---------------------------------------------------------------------------
# 5. review-receipts
# ---------------------------------------------------------------------------

def _is_unexpanded_glob(arg: str) -> bool:
    return any(ch in arg for ch in ("*", "?", "["))


def _section_spans(lines: list[bytes]) -> list[tuple[int, int, str]]:
    """Return 1-based inclusive (start, end, heading) spans split on ^## lines."""
    if not lines:
        return []
    spans: list[tuple[int, int, str]] = []
    seen: dict[str, int] = {}
    pre = True
    start: int | None = None
    heading = ""

    for idx, raw in enumerate(lines, 1):
        text_line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
        if text_line.startswith("## "):
            if pre and idx > 1:
                spans.append((1, idx - 1, "__preamble__"))
            pre = False
            if start is not None:
                spans.append((start, idx - 1, heading))
            start = idx
            base = text_line[3:]
            cnt = seen.get(base, 0) + 1
            seen[base] = cnt
            heading = base if cnt == 1 else f"{base} #{cnt}"

    total = len(lines)
    if pre and total > 0:
        spans.append((1, total, "__preamble__"))
    if start is not None:
        spans.append((start, total, heading))
    return spans


def review_receipts(args: list[str], root: Path | None = None) -> CheckResult:
    """Content-hash and per-section delta change detection for review receipts."""
    proj_root = find_project_root(root)
    if not args:
        return CheckResult(
            2,
            "",
            "Usage: check receipts hash <file>... | check <receipt-file> <file>... | sections-hash <file> | sections-check <receipt-file> <file>\n",
        )

    def resolve_path(arg: str) -> Path:
        p = Path(arg)
        return p if p.is_absolute() else (proj_root / p)

    mode = args[0]
    rest = args[1:]

    if mode == "hash":
        if not rest:
            return CheckResult(2, "", "review-receipts: hash mode needs at least one file\n")
        rc = 0
        out_lines: list[str] = []
        err_lines: list[str] = []
        for farg in rest:
            fpath = resolve_path(farg)
            if not fpath.is_file():
                err_lines.append(f"review-receipts: no such file: {farg}")
                rc = 2
                continue
            h = _git_blob_hash_file(fpath)
            out_lines.append(f"Reviewed-Content-Hash: {_norm_path(farg)} {h}")
        return CheckResult(
            rc,
            ("\n".join(out_lines) + "\n") if out_lines else "",
            ("\n".join(err_lines) + "\n") if err_lines else "",
        )

    if mode == "check":
        if len(rest) < 2:
            return CheckResult(2, "", "review-receipts: check mode needs a receipt file and at least one file\n")
        receipt_arg = rest[0]
        file_args = rest[1:]
        receipt_path = resolve_path(receipt_arg)
        if not receipt_path.is_file() or receipt_path.stat().st_size == 0:
            lines = ["RECEIPT: NONE"]
            for farg in file_args:
                if not resolve_path(farg).is_file():
                    if _is_unexpanded_glob(farg):
                        lines.append(f"UNRESOLVED: {_norm_path(farg)}")
                    continue
                lines.append(f"NEW: {_norm_path(farg)}")
            return CheckResult(0, "\n".join(lines) + "\n")

        receipt_lines = receipt_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        latest_hashes: dict[str, str] = {}
        for rline in receipt_lines:
            if rline.startswith("Reviewed-Content-Hash: "):
                parts = rline[len("Reviewed-Content-Hash: ") :].rsplit(" ", 1)
                if len(parts) == 2:
                    latest_hashes[parts[0]] = parts[1].strip()

        out = [f"RECEIPT: {_norm_path(receipt_arg)}"]
        for farg in file_args:
            fpath = resolve_path(farg)
            if not fpath.is_file():
                if _is_unexpanded_glob(farg):
                    out.append(f"UNRESOLVED: {_norm_path(farg)}")
                continue
            norm = _norm_path(farg)
            stored = latest_hashes.get(norm)
            if not stored:
                out.append(f"NEW: {norm}")
                continue
            current = _git_blob_hash_file(fpath)
            out.append(f"{'UNCHANGED' if current == stored else 'CHANGED'}: {norm}")
        return CheckResult(0, "\n".join(out) + "\n")

    if mode == "sections-hash":
        if not rest or not resolve_path(rest[0]).is_file():
            return CheckResult(2, "", "review-receipts: sections-hash needs an existing file\n")
        farg = rest[0]
        fpath = resolve_path(farg)
        raw_lines = fpath.read_bytes().splitlines(keepends=True)
        norm = _norm_path(farg)
        out = []
        for s, e, heading in _section_spans(raw_lines):
            chunk = b"".join(raw_lines[s - 1 : e])
            shash = _git_blob_hash_bytes(chunk) or "NO-HASH-TOOL"
            out.append(f"Reviewed-Section-Hash: {norm}#{heading} {shash}")
        return CheckResult(0, ("\n".join(out) + "\n") if out else "")

    if mode == "sections-check":
        if len(rest) < 2 or not resolve_path(rest[1]).is_file():
            return CheckResult(2, "", "review-receipts: sections-check needs a receipt file and an existing file\n")
        receipt_path = resolve_path(rest[0])
        farg = rest[1]
        fpath = resolve_path(farg)
        norm = _norm_path(farg)
        prefix = f"Reviewed-Section-Hash: {norm}#"
        stored: dict[str, str] = {}
        if receipt_path.is_file() and receipt_path.stat().st_size > 0:
            for rline in receipt_path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
                if rline.startswith(prefix):
                    body = rline[len(prefix) :]
                    if " " in body:
                        key, hval = body.rsplit(" ", 1)
                        if key:
                            stored[key] = hval.strip()

        out: list[str] = []
        if not stored:
            out.append("SECTIONS: NONE")

        raw_lines = fpath.read_bytes().splitlines(keepends=True)
        current_headings: set[str] = set()
        for s, e, heading in _section_spans(raw_lines):
            current_headings.add(heading)
            cur_hash = _git_blob_hash_bytes(b"".join(raw_lines[s - 1 : e])) or "NO-HASH-TOOL"
            sv = stored.get(heading, "")
            if not sv:
                out.append(f"SECTION-NEW: {heading}")
            elif cur_hash == sv:
                out.append(f"SECTION-UNCHANGED: {heading}")
            else:
                out.append(f"SECTION-CHANGED: {heading}")

        for old_heading in sorted(stored):
            if old_heading not in current_headings:
                out.append(f"SECTION-REMOVED: {old_heading}")

        return CheckResult(0, ("\n".join(out) + "\n") if out else "")

    return CheckResult(
        2,
        "",
        "Usage: check receipts hash <file>... | check <receipt-file> <file>... | sections-hash <file> | sections-check <receipt-file> <file>\n",
    )


# ---------------------------------------------------------------------------
# 6. review-scope
# ---------------------------------------------------------------------------

def review_scope(root: Path | None = None) -> CheckResult:
    """Compute incremental GDD review scope and declared dependencies."""
    proj_root = find_project_root(root)
    gdd_dir = proj_root / "design" / "gdd"

    if not gdd_dir.is_dir():
        return CheckResult(
            0,
            "PRIOR_REVIEW: NONE (full review required)\nCHANGED:\n  (no system GDDs found)\n",
        )

    reviews = sorted(
        p for p in gdd_dir.iterdir()
        if p.is_file() and p.name.startswith("gdd-cross-review-") and p.suffix == ".md"
    )
    all_sys_gdds = sorted(
        p for p in gdd_dir.iterdir()
        if p.is_file() and p.suffix == ".md" and _is_system_gdd(p)
    )

    if not reviews:
        lines = ["PRIOR_REVIEW: NONE (full review required)", "CHANGED:"]
        if not all_sys_gdds:
            lines.append("  (no system GDDs found)")
        else:
            for g in all_sys_gdds:
                lines.append(f"  {_norm_path(g.relative_to(proj_root))}")
        return CheckResult(0, "\n".join(lines) + "\n")

    last_review = reviews[-1]
    last_rel = _norm_path(last_review.relative_to(proj_root))
    lines = [f"PRIOR_REVIEW: {last_rel}"]

    changed_rels: set[str] = set()
    used_git = False
    git_bin = shutil.which("git")
    if git_bin and (proj_root / ".git").exists():
        try:
            log_proc = subprocess.run(
                [git_bin, "log", "-1", "--format=%H", "--", last_rel],
                cwd=str(proj_root),
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            base_commit = log_proc.stdout.strip()
            if base_commit:
                used_git = True
                glob_spec = ":(glob)design/gdd/*.md"
                diff_proc = subprocess.run(
                    [git_bin, "diff", "--name-only", base_commit, "--", glob_spec],
                    cwd=str(proj_root),
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                for p in diff_proc.stdout.splitlines():
                    if p.strip():
                        changed_rels.add(_norm_path(p.strip()))

                stat_proc = subprocess.run(
                    [git_bin, "status", "--porcelain", "-z", "--", glob_spec],
                    cwd=str(proj_root),
                    capture_output=True,
                    timeout=10,
                    check=False,
                )
                for entry in stat_proc.stdout.decode("utf-8", errors="replace").split("\0"):
                    if len(entry) > 3:
                        changed_rels.add(_norm_path(entry[3:]))
        except (OSError, subprocess.TimeoutExpired):
            used_git = False

    if not used_git:
        base_mtime = last_review.stat().st_mtime
        for g in all_sys_gdds:
            if g.stat().st_mtime > base_mtime:
                changed_rels.add(_norm_path(g.relative_to(proj_root)))

    scope: list[Path] = []
    for rel in sorted(changed_rels):
        cand = proj_root / rel
        if cand.is_file() and _is_system_gdd(cand):
            scope.append(cand)

    lines.append("CHANGED:")
    if not scope:
        lines.append("  (none — no GDDs modified since last review)")
        return CheckResult(0, "\n".join(lines) + "\n")

    for g in scope:
        lines.append(f"  {_norm_path(g.relative_to(proj_root))}")

    lines.append("DEPS (declared in changed GDDs — include these in review scope too):")
    for g in scope:
        text = g.read_text(encoding="utf-8-sig", errors="replace")
        in_deps = False
        dep_refs: set[str] = set()
        for raw_line in text.splitlines():
            if raw_line.startswith("## "):
                h = re.sub(r"^##\s+(?:[0-9]+[.)]?\s*)?", "", raw_line).strip().lower()
                in_deps = h.startswith("dependencies")
            elif in_deps:
                dep_refs.update(re.findall(r"[A-Za-z0-9_-]+\.md", raw_line))
        for dep in sorted(dep_refs):
            lines.append(f"  {g.name} -> {dep}")

    return CheckResult(0, "\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# 7. rotate-session-state
# ---------------------------------------------------------------------------

def rotate_session_state(dry_run: bool = False, root: Path | None = None) -> CheckResult:
    """Move narrative below <!-- /CHECKPOINT --> in active.md into dated session log."""
    proj_root = find_project_root(root)
    state_path = proj_root / "production" / "session-state" / "active.md"
    log_dir = proj_root / "production" / "session-logs"

    if not state_path.is_file():
        return CheckResult(0, "no session state at production/session-state/active.md — nothing to rotate\n")

    lines = state_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    split_idx: int | None = None
    for idx, ln in enumerate(lines, 1):
        if "<!-- /CHECKPOINT -->" in ln:
            split_idx = idx
            break

    if split_idx is None:
        msg = (
            f"REFUSED: production/session-state/active.md has no <!-- /CHECKPOINT --> marker.\n"
            "  Rotation splits the file at that marker, so without it this command\n"
            "  cannot tell the checkpoint from the narrative and would move both.\n"
            "  Re-create the file from .ags/templates/session-state.md first.\n"
        )
        return CheckResult(3, msg)

    total = len(lines)
    narrative_count = total - split_idx
    if narrative_count <= 5:
        return CheckResult(0, f"narrative is {narrative_count} lines — nothing worth rotating\n")

    stamp = _dt.date.today().isoformat()
    archive_rel = f"production/session-logs/session-state-{stamp}.md"
    archive_path = log_dir / f"session-state-{stamp}.md"

    if dry_run:
        msg = (
            "DRY RUN — no changes written\n"
            f"  checkpoint kept : lines 1-{split_idx}\n"
            f"  narrative moved : lines {split_idx + 1}-{total} ({narrative_count} lines)\n"
            f"  destination     : {archive_rel}\n"
        )
        return CheckResult(0, msg)

    log_dir.mkdir(parents=True, exist_ok=True)
    narrative_block = "\n".join(lines[split_idx:])
    append_text = (
        f"\n---\n\n## Rotated from active.md on {stamp} ({narrative_count} lines)\n\n"
        f"{narrative_block}\n"
    )
    with archive_path.open("a", encoding="utf-8") as fh:
        fh.write(append_text)

    kept = "\n".join(lines[:split_idx])
    new_active = (
        f"{kept}\n\n---\n\n## Notes\n\n"
        f"_Narrative through {stamp} rotated to `{archive_rel}`._\n\n"
    )
    fd, tmp_name = tempfile.mkstemp(prefix=".ags-rotate-", dir=str(state_path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_fh:
            tmp_fh.write(new_active)
        os.replace(tmp_name, state_path)
    except OSError as exc:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        return CheckResult(1, "", f"rotate-session-state: FAILED — {exc}\n")

    new_total = len(new_active.splitlines())
    out = f"rotated {narrative_count} lines -> {archive_rel}\nproduction/session-state/active.md is now {new_total} lines\n"
    return CheckResult(0, out)


# ---------------------------------------------------------------------------
# 8. migrate-v1-config
# ---------------------------------------------------------------------------

_TP_KEYS_RE = re.compile(
    r"^\s*-\s+\*\*(Engine|Language|Rendering|Physics|Target Platforms|Primary Input|"
    r"Gamepad Support|Touch Support|Classes|Variables|Constants|Signals(?:/Events)?|"
    r"Files|Scenes(?:/Prefabs)?|Target Framerate|Frame Budget|Draw Calls|Memory Ceiling|"
    r"Framework|Minimum Coverage|Additional Specialists|Language/Code Specialist|"
    r"Shader Specialist|UI Specialist)\*\*:\s*([^\s\[].*)$"
)

_KNOWN_TP_SECTIONS = frozenset(
    {
        "Engine & Language",
        "Input & Platform",
        "Naming Conventions",
        "Performance Budgets",
        "Testing",
        "Forbidden Patterns",
        "Allowed Libraries / Addons",
        "Architecture Decisions Log",
        "Engine Specialists",
    }
)


def _trim_first_line(path: Path) -> str:
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        s = line.strip()
        if s:
            return s
    return ""


def _tp_configured(tp_path: Path) -> bool:
    if not tp_path.is_file():
        return False
    for line in tp_path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if _TP_KEYS_RE.match(line):
            return True
    return False


def _tp_get(tp_text: str, section: str, key_pat: str) -> str:
    in_sec = False
    grab = False
    val = ""
    pat = re.compile(rf"^-\s+\*\*{key_pat}\*\*:\s*(.*)$")
    for line in tp_text.splitlines():
        if line.startswith(f"## {section}"):
            in_sec = True
            continue
        if in_sec and line.startswith("## "):
            in_sec = False
        if in_sec and grab:
            if re.match(r"^\s+\S", line) and not re.match(r"^\s*-\s+\*\*", line):
                val = f"{val} {line.strip()}".strip()
                continue
            break
        if in_sec:
            m = pat.match(line)
            if m:
                val = m.group(1).strip()
                grab = True
    if val.startswith("[TO BE CONFIGURED"):
        return ""
    return val


def _strip_unit(raw: str) -> str:
    return re.sub(r"\s*(?:ms|MB|mb|fps|FPS|%)\s*$", "", raw).strip()


def _is_num(raw: str) -> bool:
    return bool(raw and re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", raw))


def _yaml_str(raw: str) -> str:
    if not raw:
        return "null"
    escaped = raw.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _yaml_num(raw: str) -> str:
    return raw if _is_num(raw) else "null"


def _split_top_commas(raw: str) -> list[str]:
    if not raw:
        return []
    parts: list[str] = []
    depth = 0
    buf: list[str] = []
    for ch in raw:
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
        if ch == "," and depth == 0:
            item = "".join(buf).strip()
            if item:
                parts.append(item)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _yaml_list(raw: str) -> str:
    items = _split_top_commas(raw)
    if not items:
        return "[]"
    formatted = ", ".join(_yaml_str(item) for item in items)
    return f"[{formatted}]"


def _agent_name(raw: str) -> str:
    m = re.search(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+", raw)
    return m.group(0) if m else raw.strip()


def _agent_names(raw: str) -> str:
    names = [_agent_name(el) for el in _split_top_commas(raw)]
    return ", ".join(n for n in names if n)


def migrate_v1_config(dry_run: bool = False, finalize: bool = False, root: Path | None = None) -> CheckResult:
    """Convert a v1.0 CCGS project configuration into project.yaml safely."""
    proj_root = find_project_root(root)
    py_path = proj_root / "project.yaml"
    stage_path = proj_root / "production" / "stage.txt"
    review_path = proj_root / "production" / "review-mode.txt"
    tp_path = proj_root / ".claude" / "docs" / "technical-preferences.md"
    report_path = proj_root / "production" / "migration-report.md"

    tp_text = tp_path.read_text(encoding="utf-8-sig", errors="replace") if tp_path.is_file() else ""
    tp_has_data = _tp_configured(tp_path)
    legacy_present = stage_path.is_file() or review_path.is_file() or tp_has_data

    def _yaml_contains_key_val(key: str, want: str) -> bool:
        if not py_path.is_file():
            return False
        txt = py_path.read_text(encoding="utf-8-sig", errors="replace")
        pat = re.compile(rf'^\s*{re.escape(key)}:\s*"?{re.escape(want)}"?\s*$', re.M)
        return bool(pat.search(txt))

    if finalize:
        if not py_path.is_file():
            return CheckResult(3, "REFUSED: project.yaml does not exist. Run migration first.\n")
        failed: list[str] = []
        if stage_path.is_file():
            want = _trim_first_line(stage_path)
            if want and not _yaml_contains_key_val("stage", want):
                failed.append("production/stage.txt")
        if review_path.is_file():
            want = _trim_first_line(review_path)
            if want == "none":
                want = "solo"
            if want and not _yaml_contains_key_val("review_mode", want):
                failed.append("production/review-mode.txt")
        if tp_has_data:
            eng_raw = _tp_get(tp_text, "Engine & Language", "Engine")
            eng_first = eng_raw.split()[0] if eng_raw.split() else ""
            if eng_first and not _yaml_contains_key_val("name", eng_first):
                failed.append(".claude/docs/technical-preferences.md")
        if failed:
            msg = (
                f"REFUSED: content not preserved in project.yaml for: {' '.join(failed)}\n"
                "  Nothing was deleted. Re-run migration or fix project.yaml by hand.\n"
            )
            return CheckResult(4, msg)
        out_lines: list[str] = []
        for lpath, lrel in ((stage_path, "production/stage.txt"), (review_path, "production/review-mode.txt")):
            if lpath.is_file():
                lpath.unlink()
                out_lines.append(f"deleted {lrel}")
        out_lines.extend(
            [
                "NOTE: .claude/docs/technical-preferences.md is NOT deleted — it still holds Forbidden Patterns and",
                "      Allowed Libraries, which have no project.yaml equivalent.",
                "finalize complete.",
            ]
        )
        return CheckResult(0, "\n".join(out_lines) + "\n")

    # Preflight conflict guard
    if py_path.is_file() and legacy_present:
        conflict = False
        if stage_path.is_file():
            sv = _trim_first_line(stage_path)
            if sv and not _yaml_contains_key_val("stage", sv):
                conflict = True
        if review_path.is_file():
            rv = _trim_first_line(review_path)
            if rv == "none":
                rv = "solo"
            if rv and not _yaml_contains_key_val("review_mode", rv):
                conflict = True
        if tp_has_data:
            ev = _tp_get(tp_text, "Engine & Language", "Engine").split()
            if ev and not _yaml_contains_key_val("name", ev[0]):
                conflict = True

        if conflict:
            return CheckResult(
                3,
                "REFUSED: both project.yaml and legacy files exist, and their values DISAGREE.\n"
                "  Resolve which is authoritative before migrating.\n"
                "  If you already migrated, the next step is: ags check migrate-v1 --finalize\n",
            )
        if report_path.is_file():
            return CheckResult(
                3,
                "REFUSED: both project.yaml and legacy files exist.\n"
                "  Resolve which is authoritative before migrating.\n"
                "  If you already migrated, the next step is: ags check migrate-v1 --finalize\n",
            )
        return CheckResult(0, "Nothing to do: project.yaml exists and the legacy files mirror it (values agree).\n")

    if py_path.is_file():
        return CheckResult(0, "Nothing to do: project.yaml exists and no legacy config was found.\n")
    if not legacy_present:
        return CheckResult(0, "Nothing to do: no legacy config files found (not a v1.0 project).\n")

    warnings: list[str] = []
    manuals: list[str] = []
    stage = _trim_first_line(stage_path) if stage_path.is_file() else ""
    if stage_path.is_file() and not stage:
        warnings.append("production/stage.txt is empty — project.stage left unset")

    review = _trim_first_line(review_path) if review_path.is_file() else ""
    if review_path.is_file():
        if not review:
            warnings.append(
                "production/review-mode.txt is empty — modes.review_mode left unset, so modes.rigor supplies it"
            )
        else:
            warnings.append(
                f"production/review-mode.txt is '{review}' — modes.review_mode is now set EXPLICITLY, which outranks modes.rigor."
            )

    valid_stages = {"", "Concept", "Systems Design", "Technical Setup", "Pre-Production", "Production", "Polish", "Release"}
    if stage not in valid_stages:
        warnings.append(f"project.stage `{stage}` is not a v1.1 stage — preserved raw, resolve by hand")
        manuals.append(f"Confirm `project.stage: {stage}` is intended")

    if review == "none":
        review = "solo"
        warnings.append("modes.review_mode `none` (v1.0 \"no reviews\") migrated to v1.1 `solo`")
    if review not in {"", "full", "lean", "solo"}:
        warnings.append(f"modes.review_mode `{review}` is not a v1.1 value — preserved raw, resolve by hand")
        manuals.append(f"Confirm `modes.review_mode: {review}` is intended")

    eng_raw = _tp_get(tp_text, "Engine & Language", "Engine")
    eng_tokens = eng_raw.split()
    eng_name = eng_tokens[0] if eng_tokens else ""
    eng_ver = (
        eng_tokens[-1]
        if len(eng_tokens) > 1 and re.fullmatch(r"[0-9]+(?:\.[0-9]+)*[A-Za-z0-9]*", eng_tokens[-1])
        else ""
    )
    lang = _tp_get(tp_text, "Engine & Language", "Language")
    render = _tp_get(tp_text, "Engine & Language", "Rendering")
    physics = _tp_get(tp_text, "Engine & Language", "Physics")

    targets = _tp_get(tp_text, "Input & Platform", "Target Platforms")
    primary_input = _tp_get(tp_text, "Input & Platform", "Primary Input")
    gamepad = _tp_get(tp_text, "Input & Platform", "Gamepad Support")
    touch = _tp_get(tp_text, "Input & Platform", "Touch Support")

    n_classes = _tp_get(tp_text, "Naming Conventions", "Classes")
    n_vars = _tp_get(tp_text, "Naming Conventions", "Variables")
    n_const = _tp_get(tp_text, "Naming Conventions", "Constants")
    n_sig = _tp_get(tp_text, "Naming Conventions", "Signals(?:/Events)?")
    n_files = _tp_get(tp_text, "Naming Conventions", "Files")
    n_scenes = _tp_get(tp_text, "Naming Conventions", "Scenes(?:/Prefabs)?")

    p_fps = _strip_unit(_tp_get(tp_text, "Performance Budgets", "Target Framerate"))
    p_budget = _strip_unit(_tp_get(tp_text, "Performance Budgets", "Frame Budget"))
    p_draw = _strip_unit(_tp_get(tp_text, "Performance Budgets", "Draw Calls"))
    p_mem = _strip_unit(_tp_get(tp_text, "Performance Budgets", "Memory Ceiling"))

    for pk, pv in (
        ("target_framerate", p_fps),
        ("frame_budget_ms", p_budget),
        ("draw_call_limit", p_draw),
        ("memory_ceiling_mb", p_mem),
    ):
        if pv and not _is_num(pv):
            warnings.append(f'performance.{pk} not migrated: "{pv}" is not a single number')
            manuals.append(f"Set `performance.{pk}` by hand — the legacy value was: {pv}")

    test_fw = _tp_get(tp_text, "Testing", "Framework")
    test_cov = _strip_unit(_tp_get(tp_text, "Testing", "Minimum Coverage"))
    if test_cov and not _is_num(test_cov):
        warnings.append(f'qa.coverage_minimum not migrated: "{test_cov}" is not a single number')
        manuals.append(f"Set `qa.coverage_minimum` by hand — the legacy value was: {test_cov}")

    s_code_raw = _tp_get(tp_text, "Engine Specialists", "Language/Code Specialist")
    s_shader_raw = _tp_get(tp_text, "Engine Specialists", "Shader Specialist")
    s_ui_raw = _tp_get(tp_text, "Engine Specialists", "UI Specialist")
    s_add_raw = _tp_get(tp_text, "Engine Specialists", "Additional Specialists")

    s_code = _agent_name(s_code_raw)
    s_shader = _agent_name(s_shader_raw)
    s_ui = _agent_name(s_ui_raw)
    s_add = _agent_names(s_add_raw)

    for dkey, raw_v, kept_v in (
        ("specialists.code", s_code_raw, s_code),
        ("specialists.shader", s_shader_raw, s_shader),
        ("specialists.ui", s_ui_raw, s_ui),
        ("specialists.additional", s_add_raw, s_add),
    ):
        if raw_v and raw_v != kept_v:
            warnings.append(f"{dkey} trimmed to `{kept_v}` — the legacy line was: {raw_v}")
            if " or " in raw_v:
                manuals.append(f'`{dkey}` had two candidates ("{raw_v}"); kept the first')

    if tp_path.is_file():
        for line in tp_text.splitlines():
            if line.startswith("## "):
                sec = line[3:].strip()
                if sec and sec not in _KNOWN_TP_SECTIONS:
                    manuals.append(f"Custom section `## {sec}` in technical-preferences.md — not migrated")
        manuals.append("Forbidden Patterns and Allowed Libraries stay in technical-preferences.md")

    warnings.append(
        "modes.rigor is not written — AGS defaults it to `minimal` (lighter than v1.0 `standard`)."
    )
    manuals.append("Decide `modes.rigor`: leave unset for minimal, or pin `standard`")

    for guard, dkey, val in (
        (eng_name, "engine.version", eng_ver),
        (eng_name, "engine.language", lang),
        (eng_name, "engine.rendering", render),
        (eng_name, "engine.physics", physics),
        (s_code + s_shader + s_ui + s_add, "specialists.code", s_code),
        (s_code + s_shader + s_ui + s_add, "specialists.shader", s_shader),
        (s_code + s_shader + s_ui + s_add, "specialists.ui", s_ui),
        (n_classes + n_vars + n_const + n_sig + n_files + n_scenes, "naming.classes", n_classes),
        (n_classes + n_vars + n_const + n_sig + n_files + n_scenes, "naming.variables", n_vars),
        (n_classes + n_vars + n_const + n_sig + n_files + n_scenes, "naming.constants", n_const),
        (n_classes + n_vars + n_const + n_sig + n_files + n_scenes, "naming.signals", n_sig),
        (n_classes + n_vars + n_const + n_sig + n_files + n_scenes, "naming.files", n_files),
        (n_classes + n_vars + n_const + n_sig + n_files + n_scenes, "naming.scenes", n_scenes),
        (targets + primary_input + gamepad + touch, "platform.primary_input", primary_input),
        (targets + primary_input + gamepad + touch, "platform.gamepad_support", gamepad),
        (targets + primary_input + gamepad + touch, "platform.touch_support", touch),
    ):
        if guard and not val:
            warnings.append(f"{dkey} written as `null` — technical-preferences.md had no value for it")

    if dry_run:
        lines = [
            "DRY RUN — nothing written.",
            "would create: project.yaml",
            "would create: production/migration-report.md",
            "",
            "detected sources:",
        ]
        if stage_path.is_file():
            lines.append(f"  production/stage.txt -> project.stage: {stage or '<empty>'}")
        if review_path.is_file():
            lines.append(f"  production/review-mode.txt -> modes.review_mode: {review or '<empty>'}")
        if not review:
            lines.append("  (no production/review-mode.txt — modes.review_mode left unset; modes.rigor will supply it)")
        else:
            lines.append(f"  (modes.review_mode will be set EXPLICITLY to '{review}')")
        if tp_has_data:
            lines.append("  .claude/docs/technical-preferences.md -> engine/platform/naming/performance/testing/specialists")
        if warnings:
            lines.append("")
            lines.append("warnings:")
            lines.extend(f"- {w}" for w in warnings)
        return CheckResult(0, "\n".join(lines) + "\n")

    yaml_lines = [
        "# AGS project configuration — migrated from v1.0 legacy files.",
        "# Review production/migration-report.md before running --finalize.",
        "",
        "schema_version: 1",
        "",
        "framework:",
        "  version: 2.0.0",
        "",
    ]
    if stage:
        yaml_lines.extend(["project:", f'  stage: "{stage}"', ""])
    if review:
        yaml_lines.extend(["modes:", f"  review_mode: {review}", ""])
    if eng_name:
        yaml_lines.extend(
            [
                "engine:",
                f"  name: {_yaml_str(eng_name)}",
                f"  version: {_yaml_str(eng_ver)}",
                f"  language: {_yaml_str(lang)}",
                f"  rendering: {_yaml_str(render)}",
                f"  physics: {_yaml_str(physics)}",
                "",
            ]
        )
    if s_code or s_shader or s_ui or s_add:
        yaml_lines.extend(
            [
                "specialists:",
                f"  code: {_yaml_str(s_code)}",
                f"  shader: {_yaml_str(s_shader)}",
                f"  ui: {_yaml_str(s_ui)}",
                f"  additional: {_yaml_list(s_add)}",
                "",
            ]
        )
    if n_classes or n_vars or n_const or n_sig or n_files or n_scenes:
        yaml_lines.extend(
            [
                "naming:",
                f"  classes: {_yaml_str(n_classes)}",
                f"  variables: {_yaml_str(n_vars)}",
                f"  constants: {_yaml_str(n_const)}",
                f"  signals: {_yaml_str(n_sig)}",
                f"  files: {_yaml_str(n_files)}",
                f"  scenes: {_yaml_str(n_scenes)}",
                "",
            ]
        )
    if p_fps or p_budget or p_draw or p_mem:
        yaml_lines.extend(
            [
                "performance:",
                f"  target_framerate: {_yaml_num(p_fps)}",
                f"  frame_budget_ms: {_yaml_num(p_budget)}",
                f"  draw_call_limit: {_yaml_num(p_draw)}",
                f"  memory_ceiling_mb: {_yaml_num(p_mem)}",
                "",
            ]
        )
    if targets or primary_input or gamepad or touch:
        yaml_lines.extend(
            [
                "platform:",
                f"  targets: {_yaml_list(targets)}",
                f"  primary_input: {_yaml_str(primary_input)}",
                f"  gamepad_support: {_yaml_str(gamepad)}",
                f"  touch_support: {_yaml_str(touch)}",
                "",
            ]
        )
    if test_fw:
        yaml_lines.extend(["testing:", f"  framework: {_yaml_str(test_fw)}", ""])
    if _is_num(test_cov):
        yaml_lines.extend(["qa:", f"  coverage_minimum: {test_cov}", ""])

    py_path.write_text("\n".join(yaml_lines), encoding="utf-8")

    (proj_root / "production").mkdir(parents=True, exist_ok=True)
    rep_lines = [
        "# Migration report — v1.0 to v2.0",
        "",
        "Legacy files were **not** deleted. Read this report, then run",
        "`python .ags/cli.py check migrate-v1 --finalize` when satisfied.",
        "",
        "## Source files detected",
        "",
    ]
    if stage_path.is_file():
        rep_lines.append("- `production/stage.txt`")
    if review_path.is_file():
        rep_lines.append("- `production/review-mode.txt`")
    if tp_has_data:
        rep_lines.append("- `.claude/docs/technical-preferences.md`")
    rep_lines.extend(["", "## Values preserved", "", "| Setting | Value | From |", "|---|---|---|"])
    preserved_rows = [
        ("project.stage", stage, "production/stage.txt"),
        ("modes.review_mode", review, "production/review-mode.txt"),
        ("engine.name", eng_name, ".claude/docs/technical-preferences.md"),
        ("engine.version", eng_ver, ".claude/docs/technical-preferences.md"),
        ("engine.language", lang, ".claude/docs/technical-preferences.md"),
        ("testing.framework", test_fw, ".claude/docs/technical-preferences.md"),
        ("qa.coverage_minimum", test_cov if _is_num(test_cov) else "", ".claude/docs/technical-preferences.md"),
        ("specialists.code", s_code, ".claude/docs/technical-preferences.md"),
        ("engine.rendering", render, ".claude/docs/technical-preferences.md"),
        ("engine.physics", physics, ".claude/docs/technical-preferences.md"),
        ("specialists.shader", s_shader, ".claude/docs/technical-preferences.md"),
        ("specialists.ui", s_ui, ".claude/docs/technical-preferences.md"),
        ("specialists.additional", s_add, ".claude/docs/technical-preferences.md"),
        ("naming.classes", n_classes, ".claude/docs/technical-preferences.md"),
        ("naming.variables", n_vars, ".claude/docs/technical-preferences.md"),
        ("naming.constants", n_const, ".claude/docs/technical-preferences.md"),
        ("naming.signals", n_sig, ".claude/docs/technical-preferences.md"),
        ("naming.files", n_files, ".claude/docs/technical-preferences.md"),
        ("naming.scenes", n_scenes, ".claude/docs/technical-preferences.md"),
        ("platform.targets", targets, ".claude/docs/technical-preferences.md"),
        ("platform.primary_input", primary_input, ".claude/docs/technical-preferences.md"),
        ("platform.gamepad_support", gamepad, ".claude/docs/technical-preferences.md"),
        ("platform.touch_support", touch, ".claude/docs/technical-preferences.md"),
        ("performance.target_framerate", p_fps if _is_num(p_fps) else "", ".claude/docs/technical-preferences.md"),
        ("performance.frame_budget_ms", p_budget if _is_num(p_budget) else "", ".claude/docs/technical-preferences.md"),
        ("performance.draw_call_limit", p_draw if _is_num(p_draw) else "", ".claude/docs/technical-preferences.md"),
        ("performance.memory_ceiling_mb", p_mem if _is_num(p_mem) else "", ".claude/docs/technical-preferences.md"),
    ]
    for skey, sval, sfrom in preserved_rows:
        if sval:
            rep_lines.append(f"| `{skey}` | {sval} | {sfrom} |")
    rep_lines.extend(["", "## Warnings", ""])
    rep_lines.extend([f"- {w}" for w in warnings] if warnings else ["None."])
    rep_lines.extend(["", "## Manual review", ""])
    rep_lines.extend([f"- {m}" for m in manuals] if manuals else ["None."])
    report_path.write_text("\n".join(rep_lines) + "\n", encoding="utf-8")

    out_lines = ["wrote project.yaml", "wrote production/migration-report.md"]
    if warnings:
        out_lines.append("")
        out_lines.append("warnings:")
        out_lines.extend(f"- {w}" for w in warnings)
    out_lines.extend(
        [
            "",
            "Legacy files left in place. Review production/migration-report.md, then:",
            "  python .ags/cli.py check migrate-v1 --finalize",
        ]
    )
    return CheckResult(0, "\n".join(out_lines) + "\n")


# ---------------------------------------------------------------------------
# 9. Tree hash + Engine-Aware Static Validators (`ags verify`)
# ---------------------------------------------------------------------------

_HASH_EXCLUDE_PREFIXES = (
    ".git/",
    ".ags/state/",
    "production/session-logs/",
    "production/session-state/",
    "production/epics/",
    "production/stories/",
    ".godot/",
    "Library/",
    "Temp/",
    "Obj/",
    "Binaries/",
    "DerivedDataCache/",
    "Intermediate/",
    "Saved/",
    "node_modules/",
    "__pycache__/",
)


def _walk_project_files(root: Path, exclude_state_and_stories: bool = False) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        rel_dir = _norm_path(Path(dirpath).relative_to(root))
        if rel_dir == ".":
            rel_dir = ""
        if exclude_state_and_stories and rel_dir:
            rel_prefix = rel_dir + "/"
            if any(rel_prefix.startswith(p) for p in _HASH_EXCLUDE_PREFIXES):
                dirnames[:] = []
                continue
        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            rel_file = f"{rel_dir}/{fname}" if rel_dir else fname
            if exclude_state_and_stories and any(rel_file.startswith(p) for p in _HASH_EXCLUDE_PREFIXES):
                continue
            files.append(fpath)
    return files


def compute_tree_hash(root: Path | None = None) -> str:
    """Compute a deterministic SHA-256 content hash of project source/asset/config files."""
    proj_root = find_project_root(root)
    hasher = hashlib.sha256()
    for fpath in _walk_project_files(proj_root, exclude_state_and_stories=True):
        rel = _norm_path(fpath.relative_to(proj_root))
        try:
            data = fpath.read_bytes()
        except OSError:
            continue
        hasher.update(rel.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(str(len(data)).encode("ascii"))
        hasher.update(b"\0")
        hasher.update(data)
        hasher.update(b"\n")
    return hasher.hexdigest()


def _validate_toml_fallback(text: str) -> str | None:
    """Lightweight TOML syntax check for Python 3.10 when tomllib is absent."""
    in_ml_quote: str | None = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if in_ml_quote:
            if in_ml_quote in line:
                in_ml_quote = None
            continue
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            if not (line.endswith("]") or re.match(r"^\[+[^\]]+\]+\s*(?:#.*)?$", line)):
                return f"line {lineno}: unclosed TOML section header"
            continue
        if "=" not in line:
            return f"line {lineno}: expected '=' in TOML assignment"
        _, _, rhs = line.partition("=")
        rhs_s = rhs.strip()
        if rhs_s.startswith('"""') and rhs_s.count('"""') == 1:
            in_ml_quote = '"""'
        elif rhs_s.startswith("'''") and rhs_s.count("'''") == 1:
            in_ml_quote = "'''"
    if in_ml_quote:
        return "unterminated multiline TOML string"
    return None


def _validate_universal_syntax(proj_root: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    checked = 0
    for fpath in _walk_project_files(proj_root):
        rel = _norm_path(fpath.relative_to(proj_root))
        ext = fpath.suffix.lower()
        if ext == ".json":
            checked += 1
            try:
                json.loads(fpath.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                errors.append(f"{rel}: invalid JSON ({exc})")
        elif ext in (".yaml", ".yml"):
            checked += 1
            try:
                diag = load_yaml(fpath)
                errors.extend(f"{rel}: {e}" for e in diag.errors)
            except Exception as exc:
                errors.append(f"{rel}: invalid YAML ({exc})")
        elif ext == ".toml":
            checked += 1
            try:
                content = fpath.read_text(encoding="utf-8-sig")
                if tomllib is not None:
                    tomllib.loads(content)
                else:
                    err = _validate_toml_fallback(content)
                    if err:
                        errors.append(f"{rel}: invalid TOML ({err})")
            except Exception as exc:
                errors.append(f"{rel}: invalid TOML ({exc})")
    return errors, checked


def _detect_engine(proj_root: Path, engine_override: str | None = None) -> str:
    if engine_override:
        return engine_override.lower()
    py_path = proj_root / "project.yaml"
    if py_path.is_file():
        ename = get_yaml_key(load_yaml(py_path).data, "engine.name")
        if ename:
            low = ename.lower()
            if low.startswith("unreal"):
                return "unreal"
            return low
    if (proj_root / "project.godot").is_file():
        return "godot"
    if (proj_root / "Assets").is_dir() and (
        (proj_root / "ProjectSettings").is_dir() or any(proj_root.glob("*.csproj")) or any(proj_root.glob("*.sln"))
    ):
        return "unity"
    if any(proj_root.glob("*.uproject")) or (proj_root / "Source").is_dir():
        return "unreal"
    return "none"


def _validate_godot(proj_root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    gd_errors: list[str] = []
    res_errors: list[str] = []

    godot_files = list(_walk_project_files(proj_root))
    godot_root = proj_root
    for fpath in godot_files:
        if fpath.name == "project.godot":
            godot_root = fpath.parent
            break

    legacy_patterns = (
        ("legacy Godot 3 yield()", re.compile(r"\byield\s*\(")),
        ("legacy Godot 3 export var (use @export)", re.compile(r"^\s*export\s*(?:\([^)]*\))?\s*var\b")),
        ("legacy Godot 3 onready var (use @onready)", re.compile(r"^\s*onready\s+var\b")),
        ("legacy Godot 3 .instance() (use .instantiate())", re.compile(r"\.instance\s*\(")),
        ("legacy Godot 3 3-arg string connect()", re.compile(r"(?:\.|\b)connect\s*\(\s*[\"'][^\"']+[\"']\s*,[^,]+,")),
    )

    gd_count = 0
    scene_count = 0
    ext_re = re.compile(r'\[ext_resource\b[^\]]*\bpath\s*=\s*"res://([^"]+)"')

    for fpath in godot_files:
        rel = _norm_path(fpath.relative_to(proj_root))
        ext = fpath.suffix.lower()
        if ext == ".gd":
            gd_count += 1
            text = fpath.read_text(encoding="utf-8-sig", errors="replace")
            for lineno, line in enumerate(text.splitlines(), 1):
                code = line.split("#", 1)[0]
                if not code.strip():
                    continue
                for msg, pat in legacy_patterns:
                    if pat.search(code):
                        gd_errors.append(f"{rel}:{lineno}: {msg}")
        elif ext in (".tscn", ".tres"):
            scene_count += 1
            text = fpath.read_text(encoding="utf-8-sig", errors="replace")
            for lineno, line in enumerate(text.splitlines(), 1):
                for m in ext_re.finditer(line):
                    res_rel = m.group(1)
                    if not (godot_root / res_rel).exists():
                        res_errors.append(f"{rel}:{lineno}: broken ext_resource path res://{res_rel}")

    checks.append(
        {
            "name": "godot_gdscript_syntax",
            "status": "FAIL" if gd_errors else "PASS",
            "files_checked": gd_count,
            "errors": gd_errors,
        }
    )
    checks.append(
        {
            "name": "godot_ext_resource_paths",
            "status": "FAIL" if res_errors else "PASS",
            "files_checked": scene_count,
            "errors": res_errors,
        }
    )

    godot_bin = shutil.which("godot") or shutil.which("godot4")
    if godot_bin:
        try:
            proc = subprocess.run(
                [godot_bin, "--headless", "--path", str(godot_root), "--check-only", "--quit"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            cli_err = [] if proc.returncode == 0 else [(proc.stderr or proc.stdout or f"exit {proc.returncode}").strip()]
            checks.append(
                {
                    "name": "godot_headless_check",
                    "status": "PASS" if proc.returncode == 0 else "FAIL",
                    "errors": cli_err,
                }
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            checks.append({"name": "godot_headless_check", "status": "FAIL", "errors": [str(exc)]})
    else:
        checks.append({"name": "godot_headless_check", "status": "SKIPPED", "reason": "godot not in PATH"})

    return checks


def _validate_unity(proj_root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    meta_errors: list[str] = []
    update_warnings: list[str] = []

    assets_dir = proj_root / "Assets"
    if assets_dir.is_dir():
        for dirpath, dirnames, filenames in os.walk(assets_dir):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and not d.endswith("~"))
            cur = Path(dirpath)
            for d in dirnames:
                dpath = cur / d
                if not (cur / f"{d}.meta").is_file():
                    meta_errors.append(f"missing .meta for directory {_norm_path(dpath.relative_to(proj_root))}")
            for fname in sorted(filenames):
                if fname.startswith(".") or fname.endswith("~"):
                    continue
                fpath = cur / fname
                rel = _norm_path(fpath.relative_to(proj_root))
                if fname.endswith(".meta"):
                    target = fpath.with_name(fname[:-5])
                    if not target.exists():
                        meta_errors.append(f"orphaned .meta file {rel}")
                else:
                    if not (cur / f"{fname}.meta").is_file():
                        meta_errors.append(f"missing .meta for file {rel}")

    update_sig_re = re.compile(r"\bvoid\s+(?:Update|FixedUpdate|LateUpdate)\s*\([^)]*\)")
    hot_call_re = re.compile(
        r"\b(?:FindObjects?OfType|FindFirstObjectByType|FindAnyObjectByType|GetComponents?(?:InChildren|InParent)?)\s*[<(]"
    )

    cs_files = [p for p in _walk_project_files(proj_root) if p.suffix.lower() == ".cs"]
    for cspath in cs_files:
        rel = _norm_path(cspath.relative_to(proj_root))
        lines = cspath.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        in_update = False
        pending_update = False
        depth = 0
        for lineno, raw in enumerate(lines, 1):
            code = raw.split("//", 1)[0]
            if not in_update:
                if update_sig_re.search(code):
                    pending_update = True
                if pending_update and "{" in code:
                    in_update = True
                    pending_update = False
                    depth = code.count("{") - code.count("}")
                    if hot_call_re.search(code):
                        update_warnings.append(f"{rel}:{lineno}: FindObjectOfType/GetComponent inside Update()")
                    if depth <= 0:
                        in_update = False
            else:
                if hot_call_re.search(code):
                    update_warnings.append(f"{rel}:{lineno}: FindObjectOfType/GetComponent inside Update()")
                depth += code.count("{") - code.count("}")
                if depth <= 0:
                    in_update = False

    checks.append(
        {
            "name": "unity_meta_pairs",
            "status": "FAIL" if meta_errors else "PASS",
            "errors": meta_errors,
        }
    )
    checks.append(
        {
            "name": "unity_update_antipatterns",
            "status": "WARN" if update_warnings else "PASS",
            "files_checked": len(cs_files),
            "warnings": update_warnings,
        }
    )

    csproj_files = sorted(proj_root.glob("*.csproj")) + sorted(proj_root.glob("*.sln"))
    dotnet_bin = shutil.which("dotnet")
    if csproj_files and dotnet_bin:
        try:
            proc = subprocess.run(
                [dotnet_bin, "build", "--nologo"],
                cwd=str(proj_root),
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            cli_err = [] if proc.returncode == 0 else [(proc.stderr or proc.stdout or f"exit {proc.returncode}").strip()]
            checks.append(
                {
                    "name": "unity_dotnet_build",
                    "status": "PASS" if proc.returncode == 0 else "FAIL",
                    "errors": cli_err,
                }
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            checks.append({"name": "unity_dotnet_build", "status": "FAIL", "errors": [str(exc)]})
    else:
        checks.append({"name": "unity_dotnet_build", "status": "SKIPPED", "reason": "no .csproj/.sln or dotnet in PATH"})

    return checks


def _validate_unreal(proj_root: Path) -> list[dict[str, Any]]:
    errors: list[str] = []
    checked = 0
    u_macro_re = re.compile(r"\bU(?:CLASS|STRUCT|INTERFACE)\s*\(")
    inc_re = re.compile(r'^\s*#\s*include\s+[<"]([^">]+)[">]')

    for fpath in _walk_project_files(proj_root):
        if fpath.suffix.lower() not in (".h", ".hpp"):
            continue
        text = fpath.read_text(encoding="utf-8-sig", errors="replace")
        if not u_macro_re.search(text):
            continue
        checked += 1
        includes: list[tuple[int, str]] = []
        in_block_comment = False
        for lineno, raw in enumerate(text.splitlines(), 1):
            line = raw
            if in_block_comment:
                if "*/" in line:
                    line = line.split("*/", 1)[1]
                    in_block_comment = False
                else:
                    continue
            while "/*" in line:
                before, after = line.split("/*", 1)
                if "*/" in after:
                    line = before + " " + after.split("*/", 1)[1]
                else:
                    line = before
                    in_block_comment = True
                    break
            code = line.split("//", 1)[0]
            m = inc_re.match(code)
            if m:
                includes.append((lineno, m.group(1)))

        gen_indices = [idx for idx, (_, inc) in enumerate(includes) if inc.endswith(".generated.h")]
        rel = _norm_path(fpath.relative_to(proj_root))
        if not gen_indices:
            errors.append(f"{rel}: UCLASS/USTRUCT header is missing .generated.h #include")
        elif gen_indices[-1] != len(includes) - 1:
            last_line, last_inc = includes[-1]
            errors.append(
                f"{rel}:{last_line}: .generated.h must be the last #include (found '{last_inc}' after it)"
            )

    return [
        {
            "name": "unreal_generated_h_order",
            "status": "FAIL" if errors else "PASS",
            "files_checked": checked,
            "errors": errors,
        }
    ]


def validate_file_content(
    rel_path: str,
    text: str,
    root: Path,
    engine: str | None = None,
) -> tuple[list[str], list[str]]:
    """Run fast O(1) single-file syntax and engine static checks; return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []
    norm_rel = _norm_path(rel_path)
    ext = Path(norm_rel).suffix.lower()
    eng = (engine or _detect_engine(root)).lower()
    clean = text.lstrip("\ufeff")

    if ext == ".json":
        try:
            json.loads(clean)
        except Exception as exc:
            errors.append(
                f"FORMAT: {norm_rel} is not valid JSON — fix syntax errors before continuing ({exc})"
            )
        return errors, warnings

    if ext in (".yaml", ".yml"):
        diag = parse_yaml_with_diagnostics(clean)
        errors.extend(f"FORMAT: {norm_rel}: {e}" for e in diag.errors)
        return errors, warnings

    if ext == ".toml":
        try:
            if tomllib is not None:
                tomllib.loads(clean)
            else:
                err = _validate_toml_fallback(clean)
                if err:
                    errors.append(f"FORMAT: {norm_rel}: invalid TOML ({err})")
        except Exception as exc:
            errors.append(f"FORMAT: {norm_rel}: invalid TOML ({exc})")
        return errors, warnings

    if ext == ".gd" and eng in ("godot", "none"):
        legacy_patterns = (
            ("legacy Godot 3 yield()", re.compile(r"\byield\s*\(")),
            ("legacy Godot 3 export var (use @export)", re.compile(r"^\s*export\s*(?:\([^)]*\))?\s*var\b")),
            ("legacy Godot 3 onready var (use @onready)", re.compile(r"^\s*onready\s+var\b")),
            ("legacy Godot 3 .instance() (use .instantiate())", re.compile(r"\.instance\s*\(")),
            ("legacy Godot 3 3-arg string connect()", re.compile(r"(?:\.|\b)connect\s*\(\s*[\"'][^\"']+[\"']\s*,[^,]+,")),
        )
        for lineno, line in enumerate(clean.splitlines(), 1):
            code = line.split("#", 1)[0]
            if not code.strip():
                continue
            for msg, pat in legacy_patterns:
                if pat.search(code):
                    errors.append(f"GODOT: {norm_rel}:{lineno}: {msg}")
        return errors, warnings

    if ext in (".tscn", ".tres") and eng in ("godot", "none"):
        ext_re = re.compile(r'\[ext_resource\b[^\]]*\bpath\s*=\s*"res://([^"]+)"')
        godot_root = root
        for lineno, line in enumerate(clean.splitlines(), 1):
            for m in ext_re.finditer(line):
                res_rel = m.group(1)
                if not (godot_root / res_rel).exists():
                    errors.append(f"GODOT: {norm_rel}:{lineno}: broken ext_resource path res://{res_rel}")
        return errors, warnings

    if ext in (".h", ".hpp") and eng in ("unreal", "none"):
        u_macro_re = re.compile(r"\bU(?:CLASS|STRUCT|INTERFACE)\s*\(")
        if u_macro_re.search(clean):
            inc_re = re.compile(r'^\s*#\s*include\s+[<"]([^">]+)[">]')
            includes: list[tuple[int, str]] = []
            in_block = False
            for lineno, raw in enumerate(clean.splitlines(), 1):
                line = raw
                if in_block:
                    if "*/" in line:
                        line = line.split("*/", 1)[1]
                        in_block = False
                    else:
                        continue
                while "/*" in line:
                    before, after = line.split("/*", 1)
                    if "*/" in after:
                        line = before + " " + after.split("*/", 1)[1]
                    else:
                        line = before
                        in_block = True
                        break
                m = inc_re.match(line.split("//", 1)[0])
                if m:
                    includes.append((lineno, m.group(1)))
            gen_indices = [idx for idx, (_, inc) in enumerate(includes) if inc.endswith(".generated.h")]
            if not gen_indices:
                errors.append(f"UNREAL: {norm_rel}: UCLASS/USTRUCT header is missing .generated.h #include")
            elif gen_indices[-1] != len(includes) - 1:
                last_line, last_inc = includes[-1]
                errors.append(
                    f"UNREAL: {norm_rel}:{last_line}: .generated.h must be the last #include (found '{last_inc}' after it)"
                )
        return errors, warnings

    return errors, warnings


def verify_project(
    root: Path | None = None,
    engine_override: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    """Run universal and engine-aware static checks and emit .ags/state/receipt.json."""
    proj_root = find_project_root(root)
    engine = _detect_engine(proj_root, engine_override)

    syntax_errors, syntax_count = _validate_universal_syntax(proj_root)
    checks: list[dict[str, Any]] = [
        {
            "name": "universal_syntax",
            "status": "FAIL" if syntax_errors else "PASS",
            "files_checked": syntax_count,
            "errors": syntax_errors,
        }
    ]

    if engine == "godot":
        checks.extend(_validate_godot(proj_root))
    elif engine == "unity":
        checks.extend(_validate_unity(proj_root))
    elif engine == "unreal":
        checks.extend(_validate_unreal(proj_root))

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for chk in checks:
        all_errors.extend(chk.get("errors", []))
        all_warnings.extend(chk.get("warnings", []))

    verdict = "FAIL" if all_errors else "PASS"
    tree_hash = compute_tree_hash(proj_root)
    timestamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    receipt: dict[str, Any] = {
        "schema_version": 1,
        "tree_hash": tree_hash,
        "timestamp": timestamp,
        "engine": engine,
        "verdict": verdict,
        "checks": checks,
        "errors": all_errors,
        "warnings": all_warnings,
    }

    if write_receipt:
        state_dir = proj_root / ".ags" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        receipt_path = state_dir / "receipt.json"
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    return receipt
