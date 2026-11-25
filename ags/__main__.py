"""Command-line entrypoint for Agents Game Studio (`ags` / `python ags_cli.py` / `python .ags/cli.py`)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ags import PACKAGE_NAME, __version__
from ags.checks import (
    CheckResult,
    adr_dep_graph,
    artifact_check,
    gdd_structure_check,
    migrate_v1_config,
    project_coherence,
    review_receipts,
    review_scope,
    rotate_session_state,
    verify_project,
)
from ags.config import find_project_root, preflight
from ags.doctor import format_doctor_report, run_doctor
from ags.hooks import HARNESSES, run_hook_cli


def _ensure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except Exception:
            pass


def _emit_check_result(res: CheckResult) -> int:
    if res.stdout:
        sys.stdout.write(res.stdout)
    if res.stderr:
        sys.stderr.write(res.stderr)
    return res.returncode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ags",
        description=f"{PACKAGE_NAME} v{__version__} — Multi-harness game studio runtime CLI.",
    )
    parser.add_argument("--version", action="version", version=f"{PACKAGE_NAME} {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = sub.add_parser("init", help="Initialize a new AGS v2 game project from core/.")
    p_init.add_argument("target", nargs="?", default=".", help="Target game project directory (default: .)")
    p_init.add_argument("--engine", default="none", choices=["godot", "unity", "unreal", "none"], help="Target game engine pack.")
    p_init.add_argument(
        "--harness",
        action="append",
        default=None,
        help="Comma-separated harnesses: codex,antigravity,opencode,claude,universal,all",
    )
    p_init.add_argument("--rigor", default=None, choices=["minimal", "standard", "full", "jam", "indie", "studio"])
    p_init.add_argument("--name", default=None, help="Game project name.")
    p_init.add_argument("--core", default=None, help="Explicit path to AGS core/ directory.")
    p_init.add_argument("--force", action="store_true", help="Allow initializing into a non-empty directory.")

    # sync
    p_sync = sub.add_parser("sync", help="Sync existing game project with core/ and rebuild .ags/cli.py.")
    p_sync.add_argument("target", nargs="?", default=".", help="Target game project directory (default: .)")
    p_sync.add_argument("--engine", default=None, choices=["godot", "unity", "unreal", "none"])
    p_sync.add_argument("--harness", action="append", default=None, help="Harnesses to regenerate.")
    p_sync.add_argument("--core", default=None, help="Explicit path to AGS core/ directory.")

    # doctor
    p_doc = sub.add_parser("doctor", help="Run health checks on harnesses, hooks, engine CLIs, and skills.")
    p_doc.add_argument("target", nargs="?", default=None, help="Project directory (default: auto-detect).")
    p_doc.add_argument("--json", action="store_true", help="Emit JSON output.")

    # verify
    p_ver = sub.add_parser("verify", help="Run universal & engine-aware static checks and write .ags/state/receipt.json.")
    p_ver.add_argument("target", nargs="?", default=None, help="Project directory (default: auto-detect).")
    p_ver.add_argument("--engine", default=None, choices=["godot", "unity", "unreal", "none"])
    p_ver.add_argument("--no-receipt", action="store_true", help="Run checks without writing .ags/state/receipt.json.")
    p_ver.add_argument("--json", action="store_true", help="Emit full JSON receipt to stdout.")

    # preflight
    p_pre = sub.add_parser("preflight", help="Emit resolved config + session/receipt context as JSON for a skill.")
    p_pre.add_argument("skill", help="Skill name (e.g. ags-dev, ags-gdd).")
    p_pre.add_argument("target", nargs="?", default=None, help="Optional system name or project root directory.")
    p_pre.add_argument("--root", default=None, help="Explicit project root directory.")
    p_pre.add_argument("--json", action="store_true", help="Emit JSON output (default).")

    # check
    p_chk = sub.add_parser("check", help="Run ported deterministic studio observation checks.")
    chk_sub = p_chk.add_subparsers(dest="check_cmd", required=True)

    p_adr = chk_sub.add_parser("adr-graph", help="Build ADR dependency graph and detect cycles.")
    p_adr.add_argument("adr_dir", nargs="?", default=None, help="ADR directory (default: docs/architecture).")

    p_gdd = chk_sub.add_parser("gdd", help="Check system GDD section presence.")
    p_gdd.add_argument("target", nargs="?", default=None, help="Optional GDD file or directory.")

    p_art = chk_sub.add_parser("artifacts", help="Evaluate workflow-catalog.yaml artifact specs on disk.")
    p_art.add_argument("--phase", default=None, help="Restrict check to a single phase ID.")
    p_art.add_argument("project_root", nargs="?", default=None, help="Optional project root directory.")

    p_coh = chk_sub.add_parser("coherence", help="Compare project.yaml declarations against real engine artifacts.")
    p_coh.add_argument("project_root", nargs="?", default=None, help="Optional project root directory.")

    p_rec = chk_sub.add_parser("receipts", help="Content-hash and per-section delta checks for review receipts.")
    p_rec.add_argument("receipt_args", nargs=argparse.REMAINDER, help="hash|check|sections-hash|sections-check args.")

    p_scp = chk_sub.add_parser("review-scope", help="Compute incremental cross-GDD review scope.")
    p_scp.add_argument("project_root", nargs="?", default=None, help="Optional project root directory.")

    p_rot = chk_sub.add_parser("rotate-state", help="Rotate active.md narrative below checkpoint to session logs.")
    p_rot.add_argument("--dry-run", action="store_true", help="Preview rotation without modifying files.")
    p_rot.add_argument("project_root", nargs="?", default=None, help="Optional project root directory.")

    p_mig = chk_sub.add_parser("migrate-v1", help="Migrate CCGS v1.0 legacy files to project.yaml.")
    p_mig.add_argument("--dry-run", action="store_true", help="Preview migration without writing.")
    p_mig.add_argument("--finalize", action="store_true", help="Delete legacy .txt mirrors after verifying preservation.")
    p_mig.add_argument("project_root", nargs="?", default=None, help="Optional project root directory.")

    # hook
    p_hook = sub.add_parser("hook", help="Execute a unified AGS lifecycle hook for a specific harness.")
    p_hook.add_argument("--harness", required=True, choices=list(HARNESSES), help="Harness schema adapter.")
    p_hook.add_argument("event", help="Hook event name (e.g. SessionStart, PreToolUse, PostToolUse, story_gate, Stop).")
    p_hook.add_argument("--root", default=None, help="Optional project root override.")

    # build (repo-only maintainer command; hidden in standalone bundled .ags/cli.py)
    import ags as _ags_pkg

    if not getattr(_ags_pkg, "_EMBEDDED_MODULES", None):
        p_bld = sub.add_parser("build", help="Compile core/skills -> skills/, root hooks.json, and plugin manifests.")
        p_bld.add_argument("--check", action="store_true", help="Exit 0 only if all build outputs match core/.")
        p_bld.add_argument("--root", default=None, help="Optional repository root override.")

    return parser


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_stdio()
    parser = _build_parser()
    args = parser.parse_args(argv)

    cmd = args.command
    if cmd == "init":
        from ags.init_cmd import run_init

        try:
            res = run_init(
                target=args.target,
                engine=args.engine,
                harnesses=args.harness,
                rigor=args.rigor,
                name=args.name,
                core_dir=args.core,
                force=args.force,
            )
        except (ValueError, FileNotFoundError) as exc:
            sys.stderr.write(f"ags init error: {exc}\n")
            return 2
        sys.stdout.write(json.dumps(res, indent=2) + "\n")
        return 0

    if cmd == "sync":
        from ags.init_cmd import run_sync

        try:
            res = run_sync(
                target=args.target,
                engine=args.engine,
                harnesses=args.harness,
                core_dir=args.core,
            )
        except (ValueError, FileNotFoundError) as exc:
            sys.stderr.write(f"ags sync error: {exc}\n")
            return 2
        sys.stdout.write(json.dumps(res, indent=2) + "\n")
        return 0

    if cmd == "doctor":
        root = Path(args.target) if args.target else None
        rep = run_doctor(root)
        if args.json:
            sys.stdout.write(json.dumps(rep, indent=2) + "\n")
        else:
            sys.stdout.write(format_doctor_report(rep))
        return 0 if rep["ok"] else 1

    if cmd == "verify":
        root = Path(args.target) if args.target else None
        receipt = verify_project(
            root=root,
            engine_override=args.engine,
            write_receipt=not args.no_receipt,
        )
        if args.json:
            sys.stdout.write(json.dumps(receipt, indent=2) + "\n")
        else:
            sys.stdout.write(
                f"AGS Verify [{receipt['engine']}] verdict={receipt['verdict']} "
                f"tree_hash={receipt['tree_hash'][:12]}\n"
            )
            for chk in receipt["checks"]:
                sys.stdout.write(f"  [{chk['status']}] {chk['name']}\n")
            for err in receipt["errors"]:
                sys.stdout.write(f"  ERROR: {err}\n")
            for warn in receipt["warnings"]:
                sys.stdout.write(f"  WARN: {warn}\n")
        return 0 if receipt["verdict"] == "PASS" else 1

    if cmd == "preflight":
        root = Path(args.root) if args.root else None
        payload = preflight(args.skill, target=args.target, root=root)
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return 0

    if cmd == "check":
        ccmd = args.check_cmd
        if ccmd == "adr-graph":
            return _emit_check_result(adr_dep_graph(args.adr_dir))
        if ccmd == "gdd":
            return _emit_check_result(gdd_structure_check(args.target))
        if ccmd == "artifacts":
            root = Path(args.project_root) if args.project_root else None
            return _emit_check_result(artifact_check(phase=args.phase, root=root))
        if ccmd == "coherence":
            root = Path(args.project_root) if args.project_root else None
            return _emit_check_result(project_coherence(root=root))
        if ccmd == "receipts":
            return _emit_check_result(review_receipts(list(args.receipt_args)))
        if ccmd == "review-scope":
            root = Path(args.project_root) if args.project_root else None
            return _emit_check_result(review_scope(root=root))
        if ccmd == "rotate-state":
            root = Path(args.project_root) if args.project_root else None
            return _emit_check_result(rotate_session_state(dry_run=args.dry_run, root=root))
        if ccmd == "migrate-v1":
            root = Path(args.project_root) if args.project_root else None
            return _emit_check_result(
                migrate_v1_config(dry_run=args.dry_run, finalize=args.finalize, root=root)
            )

    if cmd == "hook":
        root = find_project_root(args.root) if args.root else None
        rc, out, err = run_hook_cli(args.harness, args.event, root=root)
        if out:
            sys.stdout.write(out)
        if err:
            sys.stderr.write(err)
        return rc

    if cmd == "build":
        from ags.build import run_build

        rc, msg = run_build(Path(args.root) if args.root else None, check=args.check)
        sys.stdout.write(msg)
        return rc

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
