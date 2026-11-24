"""Unified multi-harness hooks for AGS v2 (codex, antigravity, opencode, claude)."""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ags.checks import compute_tree_hash
from ags.config import (
    find_project_root,
    load_yaml,
    resolve_config,
    session_state_enabled,
)

HARNESSES = ("codex", "antigravity", "opencode", "claude")

_EDIT_TOOL_NAMES = frozenset(
    {
        "edit",
        "write",
        "apply_patch",
        "edit_file",
        "write_file",
        "replace_file_content",
        "multi_replace_file_content",
    }
)

_GENERATED_COMMIT_PREFIXES = (
    ".ags/state/",
    "production/session-logs/",
    "production/session-state/",
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

_STORY_PATH_RE = re.compile(r"(?:^|/)(?:production/(?:epics|stories)/.*\.md|story-[^/]*\.md)$", re.I)
_STATUS_COMPLETE_RE = re.compile(
    r"(?:^|\n)\s*(?:[-*]\s*)?(?:\*\*)?Status(?:\*\*)?\s*:\s*(?:\*\*)?Complete(?:\*\*)?\b",
    re.I,
)
_NOT_VERIFIED_RATIONALE_RE = re.compile(
    r"NOT VERIFIED(?:\*\*)?\s*(?:[:\-—(]|because|due to)\s*\S{2,}",
    re.I,
)
_RECEIPT_TAMPER_RE = re.compile(
    r"(?:>|>>|\btee\b|\brm\b|\bmv\b|\bcp\b|\bsed\s+-i\b|\btouch\b|\btruncate\b)[^\n]*\.ags/state/(?:receipt\.json)?",
    re.I,
)
_FORCE_GENERATED_ADD_RE = re.compile(
    r"\bgit\s+add\b[^\n]*(?:-f|--force)[^\n]*(?:\.godot/|Library/|Temp/|Binaries/|Intermediate/|Saved/|\.ags/state/)",
    re.I,
)


@dataclass
class HookOutcome:
    """Internal result of evaluating a unified hook."""

    blocked: bool = False
    error_feedback: bool = False
    message: str = ""
    noop: bool = False


def _norm_path(path: str) -> str:
    return path.replace("\\\\", "/").replace("\\", "/")


def _extract_tool_and_input(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    tool_call = payload.get("toolCall")
    if isinstance(tool_call, dict):
        tname = str(tool_call.get("name") or "")
        args = tool_call.get("args")
        return tname, (args if isinstance(args, dict) else {})
    tname = str(
        payload.get("tool_name")
        or payload.get("toolName")
        or payload.get("tool")
        or ""
    )
    tinput = (
        payload.get("tool_input")
        or payload.get("toolInput")
        or payload.get("input")
        or {}
    )
    if not isinstance(tinput, dict):
        tinput = {}
    return tname, tinput


def _extract_cwd(payload: dict[str, Any]) -> str | None:
    for key in ("cwd", "directory", "workspacePath"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    ws = payload.get("workspacePaths")
    if isinstance(ws, list) and ws and isinstance(ws[0], str) and ws[0].strip():
        return ws[0].strip()
    return None


def _extract_command(tool_input: dict[str, Any]) -> str:
    for key in ("command", "cmd", "commandLine", "CommandLine"):
        val = tool_input.get(key)
        if isinstance(val, str):
            return val
    return ""


def _parse_apply_patch(patch_text: str) -> list[tuple[str, str]]:
    """Extract (file_path, added_text) pairs from Codex apply_patch format."""
    edits: list[tuple[str, list[str]]] = []
    cur_path: str | None = None
    cur_lines: list[str] = []
    for line in patch_text.splitlines():
        m_file = re.match(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", line)
        if m_file:
            if cur_path is not None:
                edits.append((cur_path, cur_lines))
            cur_path = _norm_path(m_file.group(1).strip())
            cur_lines = []
        elif cur_path is not None:
            if line.startswith("+") and not line.startswith("+++"):
                cur_lines.append(line[1:])
            elif line.startswith(" "):
                cur_lines.append(line[1:])
    if cur_path is not None:
        edits.append((cur_path, cur_lines))
    return [(p, "\n".join(lines)) for p, lines in edits]


def _extract_edits(tool_input: dict[str, Any]) -> list[tuple[str, str]]:
    """Extract [(normalized_path, proposed_or_added_text)] from any harness tool payload."""
    patch_str = ""
    for k in ("command", "patch", "input"):
        v = tool_input.get(k)
        if isinstance(v, str) and "*** " in v and ("Add File:" in v or "Update File:" in v):
            patch_str = v
            break
    if patch_str:
        parsed = _parse_apply_patch(patch_str)
        if parsed:
            return parsed

    path_val = ""
    for k in ("file_path", "filePath", "path", "TargetFile", "targetFile", "target_file"):
        v = tool_input.get(k)
        if isinstance(v, str) and v.strip():
            path_val = _norm_path(v.strip())
            break

    content_val = ""
    for k in (
        "content",
        "CodeContent",
        "codeContent",
        "new_string",
        "newString",
        "Replacement",
        "ReplacementContent",
        "replacementContent",
        "replacement",
    ):
        v = tool_input.get(k)
        if isinstance(v, str) and v:
            content_val = v
            break

    if not content_val and isinstance(tool_input.get("ReplacementChunks"), list):
        chunks = [
            str(c.get("ReplacementContent", ""))
            for c in tool_input["ReplacementChunks"]
            if isinstance(c, dict)
        ]
        content_val = "\n".join(chunks)

    if path_val:
        return [(path_val, content_val)]
    return []


def _extract_checkpoint_lines(active_path: Path) -> tuple[list[str], list[str], int]:
    """Return (status_lines, checkpoint_lines, total_lines) from active.md."""
    text = active_path.read_text(encoding="utf-8-sig", errors="replace")
    all_lines = text.splitlines()
    status_lines: list[str] = []
    cp_lines: list[str] = []
    in_status = False
    in_cp = False
    for line in all_lines:
        s = line.strip()
        if "<!-- STATUS -->" in s:
            in_status = True
            continue
        if "<!-- /STATUS -->" in s:
            in_status = False
            continue
        if "<!-- CHECKPOINT -->" in s:
            in_cp = True
            continue
        if "<!-- /CHECKPOINT -->" in s:
            in_cp = False
            continue
        if in_status and re.match(r"^(?:Epic|Feature|Task):\s*\S", s):
            status_lines.append(s)
        if in_cp and s:
            cp_lines.append(s)
    return status_lines, cp_lines, len(all_lines)


def _git_branch(root: Path) -> str:
    git_bin = shutil.which("git")
    if not git_bin or not (root / ".git").exists():
        return "n/a"
    try:
        proc = subprocess.run(
            [git_bin, "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return proc.stdout.strip() or "n/a"
    except (OSError, subprocess.TimeoutExpired):
        return "n/a"


# ---------------------------------------------------------------------------
# 5 Unified Hooks
# ---------------------------------------------------------------------------

def hook_session_start(root: Path) -> HookOutcome:
    """O(1) <=12-line Dynamic Compass reading project.yaml + active.md."""
    cfg = resolve_config(root)
    vals = cfg["values"]
    eng = cfg["engine"]

    base_data = load_yaml(root / "project.yaml").data
    proj_name = None
    if isinstance(base_data.get("project"), dict):
        proj_name = base_data["project"].get("name")
    proj_label = str(proj_name) if proj_name else root.name

    eng_name = eng.get("name") or "none"
    eng_ver = f" {eng['version']}" if eng.get("version") else ""
    stage = vals.get("project.stage") or "unset"

    receipt_status = "NONE"
    receipt_path = root / ".ags" / "state" / "receipt.json"
    if receipt_path.is_file():
        try:
            rdata = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt_status = f"{rdata.get('verdict', 'UNKNOWN')} ({str(rdata.get('tree_hash', ''))[:8]})"
        except (OSError, ValueError):
            receipt_status = "INVALID"

    lines: list[str] = [
        f"[AGS Compass] {proj_label} | Engine: {eng_name}{eng_ver} | Stage: {stage}",
        (
            f"Modes: rigor={vals.get('rigor')} workflow={vals.get('workflow')} "
            f"review={vals.get('review_mode')} auto={vals.get('automation')}"
        ),
        f"Branch: {_git_branch(root)} | Verify Receipt: {receipt_status}",
    ]

    if cfg["notes"]:
        lines.append(f"Config Note: {'; '.join(cfg['notes'][:2])}")

    active_path = root / "production" / "session-state" / "active.md"
    if session_state_enabled(root) and active_path.is_file():
        status_lines, cp_lines, total_lines = _extract_checkpoint_lines(active_path)
        lines.append(f"Session State: production/session-state/active.md ({total_lines} lines)")
        for sl in status_lines[:2]:
            lines.append(f"  {sl}")
        for cl in cp_lines[:4]:
            lines.append(f"  {cl}")
        if total_lines > 200:
            lines.append("  Note: >200 lines — run `python .ags/cli.py check rotate-state`")

    if len(lines) > 12:
        lines = lines[:11] + ["... (read production/session-state/active.md for full checkpoint)"]
    return HookOutcome(message="\n".join(lines))


def hook_pre_command(root: Path, command: str) -> HookOutcome:
    """Block direct receipt/generated-dir tampering and invalid commit JSON."""
    cmd = command.strip()
    if not cmd:
        return HookOutcome()

    if _RECEIPT_TAMPER_RE.search(cmd):
        return HookOutcome(
            blocked=True,
            message=(
                "BLOCKED: Direct modification of .ags/state/receipt.json is prohibited. "
                "Run 'python .ags/cli.py verify' to generate a verified receipt."
            ),
        )

    if _FORCE_GENERATED_ADD_RE.search(cmd):
        return HookOutcome(
            blocked=True,
            message="BLOCKED: Force-staging generated engine/cache directories is prohibited.",
        )

    if re.match(r"^git\s+commit\b", cmd):
        git_bin = shutil.which("git")
        if not git_bin:
            return HookOutcome()
        proc = subprocess.run(
            [git_bin, "diff", "--cached", "--name-only", "-z"],
            cwd=str(root),
            capture_output=True,
            timeout=10,
            check=False,
        )
        staged = [
            _norm_path(p)
            for p in proc.stdout.decode("utf-8", errors="replace").split("\0")
            if p
        ]
        if not staged:
            return HookOutcome()

        blockers: list[str] = []
        for rel in staged:
            if any(rel.startswith(pref) or f"/{pref}" in rel for pref in _GENERATED_COMMIT_PREFIXES):
                blockers.append(f"BLOCKED: {rel} is in a generated/ephemeral directory and cannot be committed.")
            if rel.startswith(".godot/") and rel != ".godot/global_script_class_cache.cfg":
                blockers.append(f"BLOCKED: {rel} is generated .godot cache (only global_script_class_cache.cfg is tracked).")
            if re.match(r"^assets/data/.*\.json$", rel):
                fpath = root / rel
                if fpath.is_file():
                    try:
                        json.loads(fpath.read_text(encoding="utf-8-sig"))
                    except Exception:
                        blockers.append(f"BLOCKED: {rel} is not valid JSON.")
        if blockers:
            return HookOutcome(blocked=True, message="\n".join(blockers))

        # Advisory commit checks
        cfg = resolve_config(root)
        workflow = cfg["values"].get("workflow") or "standard"
        code_root = cfg["engine"].get("code_root")
        warnings: list[str] = []

        if workflow != "minimal":
            req_sections = (
                ["Overview", "Player Fantasy", "Detailed", "Formulas", "Edge Cases", "Dependencies", "Tuning Knobs", "Acceptance Criteria"]
                if workflow == "full"
                else ["Overview", "Detailed", "Edge Cases", "Dependencies", "Acceptance Criteria"]
            )
            for rel in staged:
                if rel.startswith("design/gdd/") and rel.endswith(".md"):
                    gpath = root / rel
                    if gpath.is_file():
                        body = gpath.read_text(encoding="utf-8-sig", errors="replace").lower()
                        for sec in req_sections:
                            if sec.lower() not in body:
                                warnings.append(f"DESIGN: {rel} missing section required at workflow={workflow}: {sec}")

        if code_root:
            hc_re = re.compile(r"\b(?:damage|health|speed|rate|chance|cost|duration)\s*[:=]\s*[0-9]+")
            todo_re = re.compile(r"(?:TODO|FIXME|HACK)[^(]")
            code_exts = (".gd", ".cs", ".cpp", ".cc", ".hpp", ".h", ".c", ".py", ".js", ".ts", ".rs")
            for rel in staged:
                if rel.startswith(f"{code_root}/"):
                    fpath = root / rel
                    if fpath.is_file():
                        txt = fpath.read_text(encoding="utf-8-sig", errors="replace")
                        if rel.endswith(code_exts) and hc_re.search(txt):
                            warnings.append(f"CODE: {rel} may contain hardcoded gameplay values. Use data files.")
                        if todo_re.search(txt):
                            warnings.append(f"STYLE: {rel} has TODO/FIXME without owner tag. Use TODO(name).")

        if warnings:
            return HookOutcome(message="\n".join(warnings))
        return HookOutcome()

    if re.match(r"^git\s+push\b", cmd):
        branch = _git_branch(root)
        for protected in ("main", "master", "develop"):
            if branch == protected or re.search(rf"\s{protected}(?:\s|$)", cmd):
                return HookOutcome(
                    message=(
                        f"Push to protected branch '{protected}' detected. "
                        "Ensure `python .ags/cli.py verify` and tests pass."
                    )
                )

    return HookOutcome()


def _rel_path_for_root(root: Path, raw_path: str) -> str:
    norm = _norm_path(raw_path)
    p = Path(norm)
    if p.is_absolute():
        try:
            return _norm_path(str(p.resolve().relative_to(root.resolve())))
        except ValueError:
            return norm
    return norm


def hook_post_edit(root: Path, edits: list[tuple[str, str]]) -> HookOutcome:
    """Validate edited asset names/JSON and warn on skill modifications."""
    warnings: list[str] = []
    errors: list[str] = []

    for raw_path, _ in edits:
        rel = _rel_path_for_root(root, raw_path)
        if re.search(r"(^|/)assets/", rel):
            fname = Path(rel).name
            if re.search(r"[A-Z\s-]", fname):
                warnings.append(
                    f"NAMING: {rel} must be lowercase with underscores (got: {fname})"
                )
            if re.match(r"(?:^|.*/)?assets/data/.*\.json$", rel):
                fpath = Path(raw_path) if Path(raw_path).is_absolute() else (root / rel)
                if fpath.is_file():
                    try:
                        json.loads(fpath.read_text(encoding="utf-8-sig"))
                    except Exception:
                        errors.append(
                            f"FORMAT: {rel} is not valid JSON — fix syntax errors before continuing"
                        )
        if re.search(r"(^|/)\.agents/skills/", rel):
            m = re.search(r"\.agents/skills/([^/]+)", rel)
            sname = m.group(1) if m else rel
            warnings.append(
                f"Skill modified ({sname}): run `python .ags/cli.py doctor` and ags-skill-ops checks."
            )

    if errors:
        combined = "\n".join(errors + warnings)
        return HookOutcome(blocked=True, error_feedback=True, message=combined)
    if warnings:
        return HookOutcome(message="\n".join(warnings))
    return HookOutcome()


def hook_story_gate(root: Path, edits: list[tuple[str, str]]) -> HookOutcome:
    """Block setting Status: Complete on story files without fresh PASS receipt or NOT VERIFIED rationale."""
    for raw_path, proposed_text in edits:
        rel = _rel_path_for_root(root, raw_path)
        if not _STORY_PATH_RE.search(rel):
            continue

        disk_path = Path(raw_path) if Path(raw_path).is_absolute() else (root / rel)
        disk_text = ""
        if disk_path.is_file():
            try:
                disk_text = disk_path.read_text(encoding="utf-8-sig", errors="replace")
            except OSError:
                disk_text = ""

        effective_text = proposed_text or disk_text
        combined_text = f"{disk_text}\n{proposed_text}" if (disk_text and proposed_text) else effective_text
        if not _STATUS_COMPLETE_RE.search(effective_text):
            continue

        receipt_path = root / ".ags" / "state" / "receipt.json"
        if receipt_path.is_file():
            try:
                rdata = json.loads(receipt_path.read_text(encoding="utf-8"))
                cur_hash = compute_tree_hash(root)
                if rdata.get("verdict") == "PASS" and rdata.get("tree_hash") == cur_hash:
                    return HookOutcome()
                reason_detail = (
                    f"receipt verdict is {rdata.get('verdict')}"
                    if rdata.get("verdict") != "PASS"
                    else "receipt tree_hash is stale (files modified since last verify)"
                )
            except (OSError, ValueError):
                reason_detail = "receipt.json is unreadable or invalid JSON"
        else:
            reason_detail = ".ags/state/receipt.json does not exist"

        if _NOT_VERIFIED_RATIONALE_RE.search(combined_text):
            return HookOutcome(
                message=(
                    f"Story gate: allowing Status: Complete on {rel} via explicit NOT VERIFIED rationale "
                    f"({reason_detail})."
                )
            )

        return HookOutcome(
            blocked=True,
            error_feedback=True,
            message=(
                f"BLOCKED by story_gate: cannot mark {rel} as Status: Complete ({reason_detail}). "
                "Run `python .ags/cli.py verify` to generate a matching PASS receipt, or include an "
                "explicit `NOT VERIFIED: <reason>` rationale in the story."
            ),
        )

    return HookOutcome()


def _archive_active_state(log_dir: Path, state_path: Path) -> None:
    """Append active.md to session-log.md only when its content hash changed."""
    if not state_path.is_file():
        return
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    data = state_path.read_bytes()
    state_hash = hashlib.sha256(data).hexdigest()
    hash_file = log_dir / ".active-state.hash"
    prev_hash = hash_file.read_text(encoding="utf-8").strip() if hash_file.is_file() else ""
    if state_hash != prev_hash:
        with (log_dir / "session-log.md").open("a", encoding="utf-8") as fh:
            fh.write(f"## Archived Session State: {stamp}\n")
            fh.write(data.decode("utf-8-sig", errors="replace"))
            fh.write("\n---\n\n")
        hash_file.write_text(state_hash + "\n", encoding="utf-8")


def _render_compact_summary(state_path: Path) -> str:
    lines = ["=== SESSION STATE BEFORE COMPACTION ==="]
    if state_path.is_file():
        status_lines, cp_lines, _ = _extract_checkpoint_lines(state_path)
        lines.append("## Active Session State — checkpoint from production/session-state/active.md")
        lines.extend(status_lines)
        if cp_lines:
            lines.extend(cp_lines)
        else:
            lines.append("(no CHECKPOINT block — read production/session-state/active.md)")
    else:
        lines.append("No active session state at production/session-state/active.md")
    return "\n".join(lines)


def hook_checkpoint_sync(root: Path, event_name: str, payload: dict[str, Any]) -> HookOutcome:
    """Handle PreCompact, PostCompact, Stop, and checkpoint_sync."""
    if not session_state_enabled(root):
        return HookOutcome()

    log_dir = root / "production" / "session-logs"
    state_path = root / "production" / "session-state" / "active.md"
    ev = event_name.lower()
    if ev == "checkpoint_sync":
        inner = str(payload.get("hook_event_name") or payload.get("hookEventName") or "").lower()
        if inner in ("precompact", "pre_compact", "postcompact", "post_compact", "stop"):
            ev = inner

    if ev in ("precompact", "pre_compact"):
        summary = _render_compact_summary(state_path)
        log_dir.mkdir(parents=True, exist_ok=True)
        stamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with (log_dir / "compaction-log.txt").open("a", encoding="utf-8") as fh:
            fh.write(f"Context compaction occurred at {stamp}.\n")
        return HookOutcome(message=summary)

    if ev in ("postcompact", "post_compact"):
        if state_path.is_file():
            total = len(state_path.read_text(encoding="utf-8-sig", errors="replace").splitlines())
            return HookOutcome(
                message=f"Context restored. Read production/session-state/active.md ({total} lines) to resume."
            )
        return HookOutcome()

    _archive_active_state(log_dir, state_path)
    if ev == "checkpoint_sync":
        return HookOutcome(message=_render_compact_summary(state_path))
    return HookOutcome()


# ---------------------------------------------------------------------------
# Dispatcher & Harness Formatter
# ---------------------------------------------------------------------------

def _canonical_event_name(event: str) -> str:
    mapping = {
        "session_start": "SessionStart",
        "sessionstart": "SessionStart",
        "pre_command": "PreToolUse",
        "pretooluse": "PreToolUse",
        "post_edit": "PostToolUse",
        "posttooluse": "PostToolUse",
        "story_gate": "story_gate",
        "checkpoint_sync": "Stop",
        "precompact": "PreCompact",
        "postcompact": "PostCompact",
        "stop": "Stop",
    }
    return mapping.get(event.lower(), event)


def evaluate_hook(harness: str, event: str, payload: dict[str, Any], root: Path | None = None) -> tuple[HookOutcome, str]:
    """Run the unified hook logic for `(harness, event)` and return `(HookOutcome, canonical_event)`."""
    cwd_hint = _extract_cwd(payload)
    proj_root = find_project_root(cwd_hint if root is None and cwd_hint else root)
    canon_event = _canonical_event_name(event)

    # Graceful no-op outside a game project
    if not (proj_root / "project.yaml").is_file():
        return HookOutcome(noop=True), canon_event

    ev_low = event.lower()
    tool_name, tool_input = _extract_tool_and_input(payload)
    t_low = tool_name.lower()

    if ev_low in ("session_start", "sessionstart"):
        return hook_session_start(proj_root), canon_event

    if ev_low == "story_gate":
        edits = _extract_edits(tool_input)
        return hook_story_gate(proj_root, edits), canon_event

    if ev_low in ("pre_command", "pretooluse"):
        edits = _extract_edits(tool_input)
        if t_low in _EDIT_TOOL_NAMES or (edits and not _extract_command(tool_input)):
            return hook_story_gate(proj_root, edits), canon_event
        cmd = _extract_command(tool_input)
        return hook_pre_command(proj_root, cmd), canon_event

    if ev_low in ("post_edit", "posttooluse"):
        edits = _extract_edits(tool_input)
        edit_out = hook_post_edit(proj_root, edits)
        gate_out = hook_story_gate(proj_root, edits)
        if gate_out.blocked:
            msgs = [m for m in (gate_out.message, edit_out.message) if m]
            return HookOutcome(blocked=True, error_feedback=True, message="\n".join(msgs)), canon_event
        if edit_out.blocked:
            return edit_out, canon_event
        msgs = [m for m in (edit_out.message, gate_out.message) if m]
        return HookOutcome(message="\n".join(msgs)), canon_event

    if ev_low in ("checkpoint_sync", "precompact", "postcompact", "stop"):
        return hook_checkpoint_sync(proj_root, event, payload), canon_event

    return HookOutcome(noop=True), canon_event


def format_hook_response(harness: str, event: str, outcome: HookOutcome) -> tuple[int, str, str]:
    """Translate HookOutcome into `(exit_code, stdout, stderr)` for a specific harness."""
    h = harness.lower()
    canon_event = _canonical_event_name(event)

    if outcome.noop:
        if h == "antigravity":
            return 0, json.dumps({}), ""
        if h == "opencode":
            return 0, json.dumps({"allow": True, "noop": True}), ""
        return 0, "", ""

    if h == "claude":
        if outcome.blocked or outcome.error_feedback:
            return 2, "", (outcome.message + "\n" if outcome.message else "")
        if outcome.message:
            return 0, outcome.message + "\n", ""
        return 0, "", ""

    if h == "codex":
        if outcome.blocked:
            if canon_event == "PreToolUse":
                body = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": outcome.message or "AGS hook blocked this tool call.",
                    }
                }
            else:
                body = {
                    "decision": "block",
                    "reason": outcome.message or "AGS hook blocked this action.",
                    "hookSpecificOutput": {
                        "hookEventName": canon_event,
                        "additionalContext": outcome.message or "AGS hook blocked this action.",
                    },
                }
            return 0, json.dumps(body), ""
        if outcome.message:
            body = {
                "hookSpecificOutput": {
                    "hookEventName": canon_event,
                    "additionalContext": outcome.message,
                }
            }
            return 0, json.dumps(body), ""
        return 0, "", ""

    if h == "antigravity":
        if canon_event == "SessionStart":
            if outcome.message:
                body = {"injectSteps": [{"systemMessage": {"systemMessage": outcome.message}}]}
                return 0, json.dumps(body), ""
            return 0, json.dumps({}), ""
        if canon_event == "PreToolUse":
            if outcome.blocked:
                return 0, json.dumps({"decision": "deny", "reason": outcome.message}), ""
            if outcome.message:
                return 0, json.dumps({"decision": "allow", "reason": outcome.message}), ""
            return 0, json.dumps({"decision": "allow"}), ""
        if canon_event == "Stop":
            if outcome.blocked:
                return 0, json.dumps({"decision": "continue", "reason": outcome.message}), ""
            if outcome.message:
                return 0, json.dumps({"systemMessage": outcome.message}), ""
            return 0, json.dumps({}), ""
        # PostToolUse / PreCompact / PostCompact / story_gate
        if outcome.blocked:
            return 0, json.dumps({"decision": "deny", "reason": outcome.message}), ""
        if outcome.message:
            return 0, json.dumps({"systemMessage": outcome.message}), ""
        return 0, json.dumps({}), ""

    if h == "opencode":
        body = {
            "allow": not outcome.blocked,
            "blocked": outcome.blocked,
            "reason": outcome.message if outcome.blocked else "",
            "additionalContext": outcome.message if not outcome.blocked else "",
        }
        return 0, json.dumps(body), ""

    return 0, outcome.message + "\n" if outcome.message else "", ""


def run_hook_cli(harness: str, event: str, stdin_text: str | None = None, root: Path | None = None) -> tuple[int, str, str]:
    """Read JSON from stdin (or provided string), run hook, and return (rc, stdout, stderr)."""
    raw = stdin_text
    if raw is None:
        if sys.stdin is not None and not sys.stdin.isatty():
            raw = sys.stdin.read()
        else:
            raw = ""
    payload: dict[str, Any] = {}
    if raw.strip():
        try:
            loaded = json.loads(raw)
            if isinstance(loaded, dict):
                payload = loaded
        except ValueError:
            payload = {}

    outcome, _ = evaluate_hook(harness, event, payload, root=root)
    return format_hook_response(harness, event, outcome)
