"""Pure-Python YAML parser, config resolver, and preflight JSON builder."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

RIGOR_ALIASES: dict[str, str] = {
    "jam": "minimal",
    "indie": "standard",
    "studio": "full",
}

RIGOR_EXPANSION: dict[str, dict[str, str]] = {
    "minimal": {
        "modes.workflow": "minimal",
        "docs.density": "terse",
        "qa.level": "minimal",
        "modes.story_granularity": "coarse",
        "modes.review_mode": "solo",
        "team.size": "individual",
    },
    "standard": {
        "modes.workflow": "standard",
        "docs.density": "balanced",
        "qa.level": "standard",
        "modes.story_granularity": "balanced",
        "modes.review_mode": "lean",
        "team.size": "individual",
    },
    "full": {
        "modes.workflow": "full",
        "docs.density": "thorough",
        "qa.level": "full",
        "modes.story_granularity": "fine",
        "modes.review_mode": "full",
        "team.size": "studio",
    },
}

TERMINAL_DEFAULTS: dict[str, str] = {
    "modes.automation": "collaborative",
    "modes.rigor": "minimal",
    "performance.enforce": "warn",
}

ALWAYS_ASK_DEFAULT: list[str] = [
    "scope_changes",
    "file_deletions",
    "schema_changes",
]

LOCALLY_OVERRIDABLE: frozenset[str] = frozenset(
    {
        "modes.review_mode",
        "modes.automation",
        "modes.automation_always_ask",
        "team.size",
        "testing.strict.logic",
        "testing.strict.integration",
        "testing.strict.visual",
        "testing.strict.ui",
        "testing.strict.config",
        "performance.enforce",
        "features.session_state",
        "features.token_budget_warn_at",
    }
)

LEGACY_FILES: dict[str, str] = {
    "modes.review_mode": "production/review-mode.txt",
    "project.stage": "production/stage.txt",
}

ENUMS: dict[str, tuple[str, ...]] = {
    "modes.review_mode": ("full", "lean", "solo"),
    "modes.rigor": ("minimal", "standard", "full", "jam", "indie", "studio"),
    "modes.workflow": ("minimal", "standard", "full"),
    "modes.automation": ("collaborative", "guided", "autonomous"),
    "modes.story_granularity": ("coarse", "balanced", "fine"),
    "docs.density": ("terse", "balanced", "thorough"),
    "qa.level": ("minimal", "standard", "full"),
    "team.size": ("individual", "small", "studio"),
    "performance.enforce": ("warn", "block", "off"),
    "platform.cert_tier": ("none", "itch", "steam", "console"),
    "accessibility.target": ("none", "standard", "aaa"),
    "engine.name": ("Godot", "Unity", "Unreal", "godot", "unity", "unreal", "none"),
    "project.stage": (
        "Concept",
        "Systems Design",
        "Technical Setup",
        "Pre-Production",
        "Production",
        "Polish",
        "Release",
    ),
    "testing.strict.logic": ("true", "false"),
    "testing.strict.integration": ("true", "false"),
    "testing.strict.visual": ("true", "false"),
    "testing.strict.ui": ("true", "false"),
    "testing.strict.config": ("true", "false"),
    "features.session_state": ("on", "off"),
    "platform.online": ("true", "false"),
    "workflow_overrides.edge_cases": ("true", "false"),
    "workflow_overrides.tuning_knobs": ("true", "false"),
    "workflow_overrides.art_bible_strict": ("true", "false"),
}

_LOCAL_SCOPE_EXEMPT_EXACT = frozenset({"schema_version"})
_LOCAL_SCOPE_EXEMPT_PREFIX = ("framework.",)
_KEY_VALUE_RE = re.compile(r"^([^:#\s][^:]*?)\s*:\s*(.*)$")


def is_unset(value: Any) -> bool:
    """Return True if a YAML value represents unset (None or empty string)."""
    return value is None or value == ""


def scalar_to_str(value: Any) -> str:
    """Convert a parsed scalar value to canonical lowercase-bool string."""
    if is_unset(value) or isinstance(value, (dict, list)):
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _strip_inline_comment(text: str) -> str:
    in_quote: str | None = None
    escaped = False
    for idx, ch in enumerate(text):
        if escaped:
            escaped = False
            continue
        if in_quote == '"' and ch == "\\":
            escaped = True
            continue
        if in_quote is not None:
            if ch == in_quote:
                in_quote = None
            continue
        if ch in ('"', "'"):
            in_quote = ch
        elif ch == "#" and (idx == 0 or text[idx - 1].isspace()):
            return text[:idx].rstrip()
    return text.rstrip()


def _unquote(token: str) -> tuple[str, bool]:
    """Return (text, was_quoted)."""
    s = token.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        inner = s[1:-1]
        out: list[str] = []
        i = 0
        while i < len(inner):
            if inner[i] == "\\" and i + 1 < len(inner):
                nxt = inner[i + 1]
                escapes = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", '"': '"', "/": "/"}
                out.append(escapes.get(nxt, nxt))
                i += 2
            else:
                out.append(inner[i])
                i += 1
        return "".join(out), True
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1].replace("''", "'"), True
    return s, False


def _parse_scalar(raw: str) -> Any:
    cleaned = _strip_inline_comment(raw).strip()
    if not cleaned:
        return None
    if cleaned[0] == "[" and cleaned.endswith("]"):
        return _parse_inline_list(cleaned)
    if cleaned[0] == "{" and cleaned.endswith("}"):
        return _parse_inline_map(cleaned)

    text, quoted = _unquote(cleaned)
    if quoted:
        return None if text == "" else text
    low = text.lower()
    if low in ("null", "~"):
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    if re.fullmatch(r"-?[0-9]+", text):
        try:
            return int(text)
        except ValueError:
            return text
    if re.fullmatch(r"-?[0-9]+\.[0-9]+", text):
        # Keep trailing-zero decimals (e.g. engine.version: 4.10 or 6.0) as exact strings.
        if text.endswith("0"):
            return text
        try:
            return float(text)
        except ValueError:
            return text
    return text


def _split_top_level(inner: str, sep: str = ",") -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    escaped = False
    depth = 0
    for ch in inner:
        if escaped:
            buf.append(ch)
            escaped = False
            continue
        if quote == '"' and ch == "\\":
            buf.append(ch)
            escaped = True
            continue
        if quote is not None:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ('"', "'"):
            quote = ch
            buf.append(ch)
        elif ch in ("[", "{"):
            depth += 1
            buf.append(ch)
        elif ch in ("]", "}"):
            if depth > 0:
                depth -= 1
            buf.append(ch)
        elif ch == sep and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _parse_inline_list(raw: str) -> list[Any]:
    inner = raw.strip()[1:-1].strip()
    if not inner:
        return []
    return [_parse_scalar(part) for part in _split_top_level(inner) if part != ""]


def _parse_inline_map(raw: str) -> dict[str, Any]:
    inner = raw.strip()[1:-1].strip()
    if not inner:
        return {}
    result: dict[str, Any] = {}
    for part in _split_top_level(inner):
        if ":" not in part:
            continue
        k, _, v = part.partition(":")
        key, _ = _unquote(k.strip())
        if key:
            result[key] = _parse_scalar(v)
    return result


@dataclass
class YamlDiagnostics:
    data: dict[str, Any] = field(default_factory=dict)
    tab_lines: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _preprocess_lines(text: str) -> tuple[list[tuple[int, int, str]], list[int]]:
    clean_text = text.lstrip("\ufeff")
    lines: list[tuple[int, int, str]] = []
    tab_lines: list[int] = []
    for lineno, raw in enumerate(clean_text.splitlines(), 1):
        stripped_end = raw.rstrip("\r")
        no_ws = stripped_end.strip()
        if not no_ws or no_ws.startswith("#"):
            continue
        lead_len = len(stripped_end) - len(stripped_end.lstrip(" \t"))
        lead = stripped_end[:lead_len]
        if "\t" in lead:
            tab_lines.append(lineno)
            continue
        lines.append((lineno, lead_len, stripped_end[lead_len:]))
    return lines, tab_lines


def _parse_block(
    lines: list[tuple[int, int, str]],
    start: int,
    min_indent: int,
    raw_lines: list[str] | None = None,
) -> tuple[Any, int]:
    if start >= len(lines):
        return {}, start
    _, first_indent, first_text = lines[start]
    if first_text == "-" or first_text.startswith("- "):
        return _parse_sequence(lines, start, first_indent, raw_lines)
    return _parse_mapping(lines, start, min_indent, raw_lines)


def _parse_sequence(
    lines: list[tuple[int, int, str]],
    start: int,
    seq_indent: int,
    raw_lines: list[str] | None = None,
) -> tuple[list[Any], int]:
    items: list[Any] = []
    idx = start
    n = len(lines)
    while idx < n:
        _, ind, text = lines[idx]
        if ind < seq_indent:
            break
        if not (text == "-" or text.startswith("- ")):
            if ind == seq_indent:
                break
            idx += 1
            continue
        after_dash = text[1:].strip() if text == "-" else text[2:].strip()
        after_dash_nc = _strip_inline_comment(after_dash).strip()
        if not after_dash_nc:
            if idx + 1 < n and lines[idx + 1][1] > ind:
                child, idx = _parse_block(lines, idx + 1, lines[idx + 1][1], raw_lines)
                items.append(child)
            else:
                items.append(None)
                idx += 1
            continue

        kv = _KEY_VALUE_RE.match(after_dash)
        if kv and not (after_dash_nc.startswith('"') or after_dash_nc.startswith("'")):
            key = _unquote(kv.group(1).strip())[0]
            val_raw = kv.group(2).strip()
            item_map: dict[str, Any] = {}
            val_nc = _strip_inline_comment(val_raw).strip()
            if val_nc == "":
                if idx + 1 < n and lines[idx + 1][1] > ind + 1:
                    child, idx = _parse_block(lines, idx + 1, lines[idx + 1][1], raw_lines)
                    item_map[key] = child
                else:
                    item_map[key] = None
                    idx += 1
            else:
                item_map[key] = _parse_scalar(val_raw)
                idx += 1
            if idx < n and lines[idx][1] > ind and not (lines[idx][2] == "-" or lines[idx][2].startswith("- ")):
                extra, idx = _parse_mapping(lines, idx, lines[idx][1], raw_lines)
                item_map.update(extra)
            items.append(item_map)
        else:
            items.append(_parse_scalar(after_dash))
            idx += 1
    return items, idx


def _consume_block_scalar(
    raw_lines: list[str],
    header_lineno: int,
    parent_indent: int,
    style: str,
) -> tuple[str | None, int]:
    """Read a YAML literal (|) or folded (>) scalar preserving blank lines and '#' lines."""
    collected: list[tuple[int, str]] = []
    block_indent: int | None = None
    last_consumed = header_lineno
    for r_idx in range(header_lineno, len(raw_lines)):
        raw = raw_lines[r_idx].rstrip("\r")
        if not raw.strip():
            collected.append((-1, ""))
            last_consumed = r_idx + 1
            continue
        lead_len = len(raw) - len(raw.lstrip(" "))
        if lead_len <= parent_indent:
            break
        if block_indent is None:
            block_indent = lead_len
        collected.append((lead_len, raw))
        last_consumed = r_idx + 1

    while collected and collected[-1][0] == -1:
        collected.pop()
    if not collected or block_indent is None:
        return None, last_consumed

    norm_lines = ["" if ind == -1 else raw[min(block_indent, len(raw)) :] for ind, raw in collected]
    if style.startswith("|"):
        return "\n".join(norm_lines), last_consumed
    # Folded scalar (> / >-): join adjacent non-empty lines with a space, preserve blank lines as paragraphs.
    parts: list[str] = []
    para: list[str] = []
    for ln in norm_lines:
        if ln == "":
            if para:
                parts.append(" ".join(para))
                para = []
            parts.append("")
        else:
            para.append(ln)
    if para:
        parts.append(" ".join(para))
    return "\n".join(parts), last_consumed


def _parse_mapping(
    lines: list[tuple[int, int, str]],
    start: int,
    map_indent: int,
    raw_lines: list[str] | None = None,
) -> tuple[dict[str, Any], int]:
    mapping: dict[str, Any] = {}
    idx = start
    n = len(lines)
    while idx < n:
        lineno, ind, text = lines[idx]
        if ind < map_indent:
            break
        if text == "-" or text.startswith("- "):
            break
        kv = _KEY_VALUE_RE.match(text)
        if not kv:
            idx += 1
            continue
        key = _unquote(kv.group(1).strip())[0]
        val_raw = kv.group(2).strip()
        val_nc = _strip_inline_comment(val_raw).strip()
        if val_nc in ("|", ">", "|-", ">-"):
            if raw_lines is not None:
                scalar_val, last_lineno = _consume_block_scalar(raw_lines, lineno, ind, val_nc)
                mapping[key] = scalar_val
                idx += 1
                while idx < n and lines[idx][0] <= last_lineno:
                    idx += 1
            else:
                block_lines: list[str] = []
                idx += 1
                block_indent = None
                while idx < n and lines[idx][1] > ind:
                    if block_indent is None:
                        block_indent = lines[idx][1]
                    pad = " " * max(0, lines[idx][1] - block_indent)
                    block_lines.append(pad + lines[idx][2])
                    idx += 1
                joiner = "\n" if val_nc.startswith("|") else " "
                mapping[key] = joiner.join(block_lines) if block_lines else None
            continue
        if val_nc == "":
            if idx + 1 < n and lines[idx + 1][1] > ind:
                child, idx = _parse_block(lines, idx + 1, lines[idx + 1][1], raw_lines)
                mapping[key] = child
            else:
                mapping[key] = None
                idx += 1
        else:
            mapping[key] = _parse_scalar(val_raw)
            idx += 1
    return mapping, idx


def parse_yaml_with_diagnostics(text: str) -> YamlDiagnostics:
    """Parse a YAML string into a dictionary while capturing tab diagnostics."""
    diag = YamlDiagnostics()
    clean_text = text.lstrip("\ufeff")
    raw_lines = clean_text.splitlines()
    lines, tab_lines = _preprocess_lines(clean_text)
    diag.tab_lines = tab_lines
    if tab_lines:
        shown = ", ".join(str(n) for n in tab_lines[:5])
        if len(tab_lines) > 5:
            shown += f" (and {len(tab_lines) - 5} more)"
        diag.errors.append(
            f"line {shown}: indented with a TAB. YAML forbids tabs for indentation; "
            "replace leading tabs with spaces."
        )
    if not lines:
        return diag
    first_indent = lines[0][1]
    parsed, _ = _parse_block(lines, 0, first_indent, raw_lines)
    if isinstance(parsed, dict):
        diag.data = parsed
    return diag


def parse_yaml(text: str) -> dict[str, Any]:
    """Parse a YAML document into a nested Python dictionary."""
    return parse_yaml_with_diagnostics(text).data


def load_yaml(path: Path) -> YamlDiagnostics:
    """Read a UTF-8 YAML file and return parsed data with diagnostics."""
    try:
        content = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return YamlDiagnostics()
    return parse_yaml_with_diagnostics(content)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from a markdown document, returning (meta, body)."""
    clean = text.lstrip("\ufeff")
    lines = clean.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, clean
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}, clean
    fm_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1 :]).lstrip("\r\n")
    return parse_yaml(fm_text), body


def get_nested(data: dict[str, Any], dotted_path: str) -> Any:
    """Walk dotted_path inside data, returning None if absent."""
    cur: Any = data
    for key in dotted_path.split("."):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def get_yaml_key(data: dict[str, Any], dotted_path: str) -> str | None:
    """Return a non-unset scalar string at dotted_path, or None."""
    val = get_nested(data, dotted_path)
    if isinstance(val, (dict, list)) or is_unset(val):
        return None
    return scalar_to_str(val)


def get_yaml_array(data: dict[str, Any], dotted_path: str) -> list[str] | None:
    """Return a list of non-empty strings at dotted_path, or None."""
    val = get_nested(data, dotted_path)
    if not isinstance(val, list):
        return None
    items = [scalar_to_str(item) for item in val if not is_unset(item)]
    return items if items else None


def find_project_root(explicit_root: Path | str | None = None) -> Path:
    """Resolve the game project root without unsafe upward traversal."""
    if explicit_root is not None:
        return Path(explicit_root).resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "project.yaml").is_file() or (cwd / "project.local.yaml").is_file():
        return cwd
    if (cwd / ".ags").is_dir() or (cwd / ".claude").is_dir():
        return cwd
    for env_key in ("AGS_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
        env_val = os.environ.get(env_key, "").strip()
        if env_val:
            cand = Path(env_val).resolve()
            if (cand / "project.yaml").is_file() or (cand / ".ags").is_dir():
                return cand
    return cwd


def validate_enum_value(dotted_path: str, value: str | None) -> str | None:
    """Return an error message if dotted_path has an enum constraint and value violates it."""
    if dotted_path not in ENUMS or is_unset(value):
        return None
    allowed = ENUMS[dotted_path]
    if value not in allowed:
        return f"{dotted_path}: '{value}' is not a valid value (expected: {'|'.join(allowed)})"
    return None


def validate_yaml_enums(diag: YamlDiagnostics) -> list[str]:
    """Return all tab and enum validation errors for a parsed YAML document."""
    errors = list(diag.errors)
    for dotted_path in ENUMS:
        val = get_yaml_key(diag.data, dotted_path)
        if val is None:
            continue
        err = validate_enum_value(dotted_path, val)
        if err:
            errors.append(err)
    return errors


def validate_local_scope(local_data: dict[str, Any]) -> list[str]:
    """Return dotted paths present in project.local.yaml that are not locally overridable."""
    disallowed: list[str] = []

    def walk(node: dict[str, Any], prefix: str) -> None:
        for key, val in node.items():
            dotted = f"{prefix}.{key}" if prefix else key
            if isinstance(val, dict) and val:
                walk(val, dotted)
            elif dotted in LOCALLY_OVERRIDABLE or dotted in _LOCAL_SCOPE_EXEMPT_EXACT:
                continue
            elif dotted.startswith(_LOCAL_SCOPE_EXEMPT_PREFIX):
                continue
            else:
                disallowed.append(dotted)

    walk(local_data, "")
    return disallowed


def _read_legacy_value(root: Path, dotted_path: str) -> tuple[str | None, str | None]:
    rel = LEGACY_FILES.get(dotted_path)
    if not rel:
        return None, None
    path = root / rel
    if not path.is_file():
        return None, None
    try:
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            trimmed = line.strip()
            if trimmed:
                return trimmed, rel
    except OSError:
        return None, None
    return None, None


def _normalize_rigor(raw: str | None) -> str | None:
    if is_unset(raw) or raw is None:
        return None
    if raw in RIGOR_EXPANSION:
        return raw
    return RIGOR_ALIASES.get(raw)


def _resolve_rigor_level(base_data: dict[str, Any]) -> str:
    raw = get_yaml_key(base_data, "modes.rigor")
    norm = _normalize_rigor(raw)
    if norm:
        return norm
    return TERMINAL_DEFAULTS["modes.rigor"]


def resolve_setting(
    dotted_path: str,
    root: Path,
    base_data: dict[str, Any],
    local_data: dict[str, Any],
) -> tuple[str | None, str]:
    """Resolve one scalar setting through local -> yaml -> legacy -> rigor -> default."""
    if dotted_path in LOCALLY_OVERRIDABLE and local_data:
        val = get_yaml_key(local_data, dotted_path)
        if val is not None and validate_enum_value(dotted_path, val) is None:
            if dotted_path == "modes.rigor":
                val = _normalize_rigor(val) or val
            return val, "project.local.yaml"

    if base_data:
        val = get_yaml_key(base_data, dotted_path)
        if val is not None and validate_enum_value(dotted_path, val) is None:
            if dotted_path == "modes.rigor":
                val = _normalize_rigor(val) or val
            return val, "project.yaml"

    legacy_val, legacy_rel = _read_legacy_value(root, dotted_path)
    if legacy_val is not None and validate_enum_value(dotted_path, legacy_val) is None:
        return legacy_val, legacy_rel or "legacy"

    if dotted_path != "modes.rigor":
        rigor_level = _resolve_rigor_level(base_data)
        derived = RIGOR_EXPANSION.get(rigor_level, {}).get(dotted_path)
        if derived is not None:
            return derived, f"rigor:{rigor_level}"

    if dotted_path in TERMINAL_DEFAULTS:
        return TERMINAL_DEFAULTS[dotted_path], "default"

    return None, "unset"


def resolve_code_root(
    root: Path,
    base_data: dict[str, Any] | None = None,
    local_data: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Determine engine-specific source root (src / Assets / Source) without guessing."""
    base = base_data if base_data is not None else load_yaml(root / "project.yaml").data
    local = local_data if local_data is not None else load_yaml(root / "project.local.yaml").data

    ename = get_yaml_key(local, "engine.name") if local else None
    src = "project.local.yaml"
    if not ename:
        ename = get_yaml_key(base, "engine.name") if base else None
        src = "engine.name"
    if not ename:
        tp = root / ".claude" / "docs" / "technical-preferences.md"
        if tp.is_file():
            try:
                for line in tp.read_text(encoding="utf-8-sig", errors="replace").splitlines():
                    m = re.match(r"^\s*[-*]?\s*\*{0,2}Engine\*{0,2}\s*:\s*(.+)$", line, re.I)
                    if m:
                        candidate = m.group(1).strip().strip("*").split()[0]
                        if not candidate.startswith("["):
                            ename = candidate
                            src = ".claude/docs/technical-preferences.md"
                        break
            except OSError:
                pass

    if ename:
        low = ename.lower()
        if low == "godot":
            return "src", src
        if low == "unity":
            return "Assets", src
        if low.startswith("unreal"):
            return "Source", src

    found = [d for d in ("src", "Assets", "Source") if (root / d).is_dir()]
    if len(found) == 1:
        return found[0], "detected"
    return "", "unset"


def session_state_enabled(root: Path) -> bool:
    """Return True unless features.session_state is explicitly set to 'off'."""
    for fname in ("project.local.yaml", "project.yaml"):
        path = root / fname
        if not path.is_file():
            continue
        diag = load_yaml(path)
        val = get_yaml_key(diag.data, "features.session_state")
        if val is not None:
            return val != "off"
    return True


def resolve_config(root: Path | None = None, system: str | None = None) -> dict[str, Any]:
    """Compute the full resolved configuration dictionary and diagnostic notes."""
    proj_root = find_project_root(root)
    base_path = proj_root / "project.yaml"
    local_path = proj_root / "project.local.yaml"

    notes: list[str] = []
    base_diag = YamlDiagnostics()
    local_diag = YamlDiagnostics()

    if not base_path.is_file():
        notes.append("project.yaml absent — defaults in use")
    else:
        try:
            raw_base = base_path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            raw_base = ""
        if not raw_base.strip():
            notes.append("project.yaml is EMPTY — defaults in use")
        else:
            base_diag = parse_yaml_with_diagnostics(raw_base)
            notes.extend(base_diag.errors)
            for err in validate_yaml_enums(base_diag):
                if err not in base_diag.errors:
                    notes.append(f"{err} — ignored, chain continued")

    if local_path.is_file():
        if not base_path.is_file():
            notes.append(
                "project.local.yaml exists but project.yaml is missing — local overrides require a base"
            )
        local_diag = load_yaml(local_path)
        notes.extend(f"local: {e}" for e in validate_yaml_enums(local_diag))
        disallowed = validate_local_scope(local_diag.data)
        if disallowed:
            notes.append(
                "local: not locally overridable, ignored — "
                + ", ".join(disallowed)
                + " (move to project.yaml or delete)"
            )

    scalar_keys = [
        ("modes.rigor", "rigor"),
        ("modes.review_mode", "review_mode"),
        ("modes.automation", "automation"),
        ("modes.workflow", "workflow"),
        ("docs.density", "docs.density"),
        ("modes.story_granularity", "story_granularity"),
        ("qa.level", "qa.level"),
        ("team.size", "team.size"),
        ("project.stage", "project.stage"),
        ("performance.enforce", "performance.enforce"),
    ]
    values: dict[str, Any] = {}
    sources: dict[str, str] = {}
    for dotted, label in scalar_keys:
        val, src = resolve_setting(dotted, proj_root, base_diag.data, local_diag.data)
        values[label] = val
        sources[label] = src

    # Stage mirror disagreement observation
    yaml_stage = get_yaml_key(base_diag.data, "project.stage") if base_diag.data else None
    txt_stage, _ = _read_legacy_value(proj_root, "project.stage")
    if yaml_stage and txt_stage and yaml_stage != txt_stage:
        notes.append(
            f"stage sources disagree: project.yaml='{yaml_stage}' vs production/stage.txt='{txt_stage}'"
        )

    # automation_always_ask
    aaa_local = get_yaml_array(local_diag.data, "modes.automation_always_ask") if local_diag.data else None
    aaa_base = get_yaml_array(base_diag.data, "modes.automation_always_ask") if base_diag.data else None
    if aaa_local is not None:
        values["automation_always_ask"] = aaa_local
        sources["automation_always_ask"] = "project.local.yaml"
    elif aaa_base is not None:
        values["automation_always_ask"] = aaa_base
        sources["automation_always_ask"] = "project.yaml"
    else:
        values["automation_always_ask"] = list(ALWAYS_ASK_DEFAULT)
        sources["automation_always_ask"] = "default"

    # cert_tier (intentionally no terminal default)
    ct_val = get_yaml_key(base_diag.data, "platform.cert_tier") if base_diag.data else None
    if ct_val and validate_enum_value("platform.cert_tier", ct_val) is None:
        values["platform.cert_tier"] = ct_val
        sources["platform.cert_tier"] = "project.yaml"
    else:
        values["platform.cert_tier"] = None
        sources["platform.cert_tier"] = "unset"

    # testing.strict.* (intentionally no central default)
    testing_strict: dict[str, str | None] = {}
    bare_strict = get_yaml_key(base_diag.data, "testing.strict") if base_diag.data else None
    if bare_strict not in ("true", "false"):
        bare_strict = None
    for kind in ("logic", "integration", "visual", "ui", "config"):
        path = f"testing.strict.{kind}"
        lv = get_yaml_key(local_diag.data, path) if local_diag.data else None
        if lv is not None and validate_enum_value(path, lv) is None:
            testing_strict[kind] = lv
            continue
        bv = get_yaml_key(base_diag.data, path) if base_diag.data else None
        if bv is not None and validate_enum_value(path, bv) is None:
            testing_strict[kind] = bv
            continue
        testing_strict[kind] = bare_strict

    # system_overrides
    raw_so = get_nested(base_diag.data, "workflow_overrides.system_overrides")
    system_overrides: dict[str, str] = {}
    if isinstance(raw_so, dict):
        for sys_name, sys_tier in raw_so.items():
            tier_str = scalar_to_str(sys_tier)
            norm_tier = _normalize_rigor(tier_str) or tier_str
            if norm_tier in ("minimal", "standard", "full"):
                system_overrides[str(sys_name)] = norm_tier

    eff_workflow = values["workflow"]
    eff_workflow_src = sources["workflow"]
    if system and system in system_overrides:
        eff_workflow = system_overrides[system]
        eff_workflow_src = "system_overrides"

    code_root, code_root_src = resolve_code_root(proj_root, base_diag.data, local_diag.data)
    engine_info = {
        "name": get_yaml_key(base_diag.data, "engine.name"),
        "version": get_yaml_key(base_diag.data, "engine.version"),
        "rendering": get_yaml_key(base_diag.data, "engine.rendering"),
        "physics": get_yaml_key(base_diag.data, "engine.physics"),
        "code_root": code_root or None,
        "code_root_source": code_root_src,
    }

    return {
        "project_root": str(proj_root).replace("\\", "/"),
        "project_configured": base_path.is_file(),
        "values": values,
        "sources": sources,
        "effective_workflow": eff_workflow,
        "effective_workflow_source": eff_workflow_src,
        "testing_strict": testing_strict,
        "system_overrides": system_overrides,
        "engine": engine_info,
        "notes": notes,
    }


def preflight(skill: str, target: str | None = None, root: Path | None = None) -> dict[str, Any]:
    """Build deterministic O(1) preflight JSON payload for a skill invocation."""
    system: str | None = None
    proj_root: Path | None = Path(root).resolve() if root is not None else None
    if target:
        cand = Path(target)
        if proj_root is None and (cand.is_dir() or "/" in target or "\\" in target):
            proj_root = cand.resolve()
        else:
            system = target
    resolved_root = find_project_root(proj_root)
    cfg = resolve_config(resolved_root, system=system)

    active_path = resolved_root / "production" / "session-state" / "active.md"
    active_lines = 0
    if active_path.is_file():
        try:
            active_lines = len(active_path.read_text(encoding="utf-8-sig", errors="replace").splitlines())
        except OSError:
            active_lines = 0

    receipt_path = resolved_root / ".ags" / "state" / "receipt.json"
    receipt_info: dict[str, Any] = {"exists": False, "verdict": None, "tree_hash": None}
    if receipt_path.is_file():
        try:
            rdata = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt_info = {
                "exists": True,
                "verdict": rdata.get("verdict"),
                "tree_hash": rdata.get("tree_hash"),
                "timestamp": rdata.get("timestamp"),
            }
        except (OSError, ValueError):
            receipt_info = {"exists": True, "verdict": "INVALID", "tree_hash": None}

    return {
        "skill": skill,
        "target": target,
        "system": system,
        **cfg,
        "session_state": {
            "enabled": session_state_enabled(resolved_root),
            "path": "production/session-state/active.md",
            "exists": active_path.is_file(),
            "lines": active_lines,
        },
        "receipt": receipt_info,
    }
