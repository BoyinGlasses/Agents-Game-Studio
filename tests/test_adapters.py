"""Integration tests for ags init adapters across godot, unity, unreal and all 4 harnesses."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

from ags.config import parse_frontmatter


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "ags_cli.py"

ENGINE_PREFIXES = {
    "godot": ("godot-",),
    "unity": ("unity-",),
    "unreal": ("unreal-", "ue-"),
}


class TestAdaptersInit(unittest.TestCase):
    """Test `ags init` engine isolation, harness configs, and standalone `.ags/cli.py`."""

    def _run_init(self, target: Path, engine: str, harness: str) -> dict:
        proc = subprocess.run(
            [
                sys.executable,
                "-B",
                str(CLI_PATH),
                "init",
                str(target),
                "--engine",
                engine,
                "--harness",
                harness,
                "--rigor",
                "standard",
                "--name",
                f"Test-{engine}",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, f"init failed:\n{proc.stdout}\n{proc.stderr}")
        return json.loads(proc.stdout)

    def test_init_all_engines_isolated_and_standalone_cli_works(self) -> None:
        all_harnesses = "codex,antigravity,opencode,claude"
        with tempfile.TemporaryDirectory() as tmp:
            for engine in ("godot", "unity", "unreal"):
                proj = Path(tmp) / f"proj_{engine}"
                with self.subTest(engine=engine):
                    res = self._run_init(proj, engine=engine, harness=all_harnesses)
                    self.assertEqual(res["engine"], engine)

                    # Core common files present
                    self.assertTrue((proj / "AGENTS.md").is_file())
                    self.assertTrue((proj / "project.yaml").is_file())
                    self.assertTrue((proj / ".ags" / "cli.py").is_file())
                    self.assertTrue((proj / ".ags" / "workflow-catalog.yaml").is_file())
                    self.assertEqual(len(list((proj / ".agents" / "skills").glob("*/SKILL.md"))), 21)

                    # tests/eval/ MUST NOT be copied into user game projects
                    self.assertFalse((proj / "tests" / "eval").exists())
                    self.assertFalse((proj / ".ags" / "eval").exists())

                    # ONLY selected engine reference installed
                    ref_root = proj / "docs" / "engine-reference"
                    self.assertTrue((ref_root / engine).is_dir())
                    for other in ("godot", "unity", "unreal"):
                        if other != engine:
                            self.assertFalse(
                                (ref_root / other).exists(),
                                f"{other} engine-reference leaked into {engine} project",
                            )

                    # ONLY selected engine roles installed in .ags/roles and harness agent dirs
                    role_stems = {p.stem for p in (proj / ".ags" / "roles").glob("*.md")}
                    for own_pref in ENGINE_PREFIXES[engine]:
                        self.assertTrue(
                            any(s.startswith(own_pref) for s in role_stems),
                            f"Missing {own_pref}* roles for {engine}",
                        )
                    for other, other_prefs in ENGINE_PREFIXES.items():
                        if other == engine:
                            continue
                        for op in other_prefs:
                            leaked = [s for s in role_stems if s.startswith(op)]
                            self.assertEqual(leaked, [], f"{other} roles leaked into {engine}: {leaked}")

                    # Codex adapter validation (.codex/config.toml, .codex/agents/*.toml, .codex/hooks.json)
                    cfg_toml = tomllib.loads((proj / ".codex" / "config.toml").read_text(encoding="utf-8"))
                    self.assertTrue(cfg_toml["features"]["multi_agent"])
                    codex_agents = list((proj / ".codex" / "agents").glob("*.toml"))
                    self.assertEqual(len(codex_agents), len(role_stems))
                    for agent_toml in codex_agents:
                        raw_toml = agent_toml.read_text(encoding="utf-8")
                        self.assertIn('developer_instructions = """', raw_toml)
                        parsed = tomllib.loads(raw_toml)
                        self.assertIn("sandbox_mode", parsed)
                        self.assertIn("model_reasoning_effort", parsed)
                        self.assertIn(parsed["sandbox_mode"], ("read-only", "workspace-write"))
                    codex_hooks = json.loads((proj / ".codex" / "hooks.json").read_text(encoding="utf-8"))
                    self.assertIn("SessionStart", codex_hooks["hooks"])
                    self.assertIn("PreToolUse", codex_hooks["hooks"])

                    # Antigravity adapter validation (.agents/hooks.json camelCase + rules)
                    ag_hooks_raw = json.loads((proj / ".agents" / "hooks.json").read_text(encoding="utf-8"))
                    ag_hooks = ag_hooks_raw["ags-hooks"]
                    self.assertIsInstance(ag_hooks["SessionStart"], list)
                    self.assertIsInstance(ag_hooks["Stop"], list)
                    self.assertEqual(ag_hooks["PreToolUse"][0]["matcher"], "run_command|edit_file|write_file")
                    self.assertEqual(ag_hooks["PostToolUse"][0]["matcher"], "edit_file|write_file")
                    self.assertTrue((proj / ".agents" / "rules" / "ags-rules.md").is_file())

                    # OpenCode adapter validation
                    oc_cfg = json.loads((proj / "opencode.json").read_text(encoding="utf-8"))
                    self.assertIn("AGENTS.md", oc_cfg["instructions"])
                    self.assertEqual(len(oc_cfg["agent"]), len(role_stems))
                    oc_agents = list((proj / ".opencode" / "agents").glob("*.md"))
                    self.assertEqual(len(oc_agents), len(role_stems))
                    for oc_md in oc_agents:
                        meta, body = parse_frontmatter(oc_md.read_text(encoding="utf-8"))
                        self.assertEqual(meta["mode"], "subagent")
                        self.assertTrue(body.strip())
                    ts_plugin = (proj / ".opencode" / "plugins" / "ags-hooks.ts").read_text(encoding="utf-8")
                    self.assertIn(".ags/cli.py", ts_plugin)
                    self.assertIn("findAgsCli", ts_plugin)
                    self.assertIn("tool.execute.before", ts_plugin)

                    # Claude adapter validation
                    self.assertIn("@AGENTS.md", (proj / "CLAUDE.md").read_text(encoding="utf-8"))
                    claude_settings = json.loads((proj / ".claude" / "settings.json").read_text(encoding="utf-8"))
                    self.assertIn("SessionStart", claude_settings["hooks"])
                    self.assertEqual(len(list((proj / ".claude" / "agents").glob("*.md"))), len(role_stems))

                    # Standalone `.ags/cli.py` works inside isolated temp project with no PYTHONPATH
                    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
                    doc_proc = subprocess.run(
                        [sys.executable, "-B", ".ags/cli.py", "doctor", "--json"],
                        cwd=proj,
                        env=env,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        timeout=30,
                    )
                    self.assertEqual(doc_proc.returncode, 0, f"standalone doctor failed:\n{doc_proc.stdout}\n{doc_proc.stderr}")
                    doc_data = json.loads(doc_proc.stdout)
                    self.assertTrue(doc_data["ok"])

                    ver_proc = subprocess.run(
                        [sys.executable, "-B", ".ags/cli.py", "verify", "--json"],
                        cwd=proj,
                        env=env,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        timeout=30,
                    )
                    self.assertEqual(ver_proc.returncode, 0, f"standalone verify failed:\n{ver_proc.stdout}\n{ver_proc.stderr}")
                    ver_data = json.loads(ver_proc.stdout)
                    self.assertEqual(ver_data["verdict"], "PASS")
                    self.assertEqual(ver_data["engine"], engine)
                    self.assertTrue((proj / ".ags" / "state" / "receipt.json").is_file())

                    # Verify emitted Codex & Antigravity hook commands execute cleanly inside proj
                    codex_cmd_entry = codex_hooks["hooks"]["SessionStart"][0]["hooks"][0]
                    codex_cmd = codex_cmd_entry.get("commandWindows" if os.name == "nt" else "command")
                    c_hook = subprocess.run(
                        codex_cmd,
                        cwd=proj,
                        env=env,
                        shell=True,
                        input="{}",
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        timeout=30,
                    )
                    self.assertEqual(c_hook.returncode, 0, f"codex hook cmd failed:\n{c_hook.stderr}")
                    self.assertIn("[AGS Compass]", json.loads(c_hook.stdout)["hookSpecificOutput"]["additionalContext"])

                    agy_cmd = ag_hooks["SessionStart"][0]["command"]
                    a_hook = subprocess.run(
                        agy_cmd,
                        cwd=proj,
                        env=env,
                        shell=True,
                        input="{}",
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        timeout=30,
                    )
                    self.assertEqual(a_hook.returncode, 0, f"antigravity hook cmd failed:\n{a_hook.stderr}")
                    self.assertIn(
                        "[AGS Compass]",
                        json.loads(a_hook.stdout)["injectSteps"][0]["systemMessage"]["systemMessage"],
                    )


if __name__ == "__main__":
    unittest.main()
