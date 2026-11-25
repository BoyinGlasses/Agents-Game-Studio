"""Unit tests for ags.hooks across all 5 unified hooks and 4 harness schemas."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ags.checks import verify_project
from ags.hooks import run_hook_cli


def _setup_game_project(root: Path) -> None:
    (root / "project.yaml").write_text(
        "schema_version: 1\n"
        "project:\n"
        "  name: Starlight\n"
        "  stage: Production\n"
        "engine:\n"
        "  name: Godot\n"
        "  version: '4.3'\n"
        "modes:\n"
        "  rigor: standard\n",
        encoding="utf-8",
    )
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "main.gd").write_text("extends Node\n", encoding="utf-8")


class TestHooksUnified(unittest.TestCase):
    """Test all 5 hooks across codex, antigravity, opencode, and claude schemas."""

    def test_noop_outside_game_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for harness in ("codex", "antigravity", "opencode", "claude"):
                for event in ("session_start", "pre_command", "post_edit", "story_gate", "checkpoint_sync"):
                    rc, out, err = run_hook_cli(harness, event, "{}", root=root)
                    self.assertEqual(rc, 0, (harness, event, err))
                    self.assertEqual(err, "")
                    if harness == "antigravity":
                        if event == "pre_command":
                            self.assertEqual(json.loads(out), {"decision": "allow"})
                        elif event == "checkpoint_sync":
                            self.assertEqual(json.loads(out), {"decision": ""})
                        else:
                            self.assertEqual(json.loads(out), {})
                    elif harness == "opencode":
                        data = json.loads(out)
                        self.assertTrue(data["allow"])
                        self.assertTrue(data["noop"])
                    else:
                        self.assertEqual(out, "")

    def test_session_start_compass_under_12_lines_all_harnesses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup_game_project(root)
            state_dir = root / "production" / "session-state"
            state_dir.mkdir(parents=True)
            (state_dir / "active.md").write_text(
                "<!-- STATUS -->\n"
                "Epic: Combat\n"
                "Task: S-01\n"
                "<!-- /STATUS -->\n"
                "<!-- CHECKPOINT -->\n"
                "Next: Run verify\n"
                "<!-- /CHECKPOINT -->\n"
                + ("History line\n" * 210),
                encoding="utf-8",
            )

            # Codex (snake_case)
            rc, out, err = run_hook_cli("codex", "session_start", json.dumps({"cwd": str(root)}))
            self.assertEqual(rc, 0, err)
            codex_msg = json.loads(out)["hookSpecificOutput"]["additionalContext"]
            self.assertLessEqual(len(codex_msg.splitlines()), 12)
            self.assertIn("[AGS Compass] Starlight", codex_msg)
            self.assertIn("Godot 4.3", codex_msg)

            # Antigravity (camelCase)
            rc, out, _ = run_hook_cli("antigravity", "SessionStart", json.dumps({"workspacePath": str(root)}))
            self.assertEqual(rc, 0)
            ag_msg = json.loads(out)["injectSteps"][0]["systemMessage"]["systemMessage"]
            self.assertLessEqual(len(ag_msg.splitlines()), 12)
            self.assertIn("[AGS Compass] Starlight", ag_msg)

            # OpenCode
            rc, out, _ = run_hook_cli("opencode", "session_start", json.dumps({"directory": str(root)}))
            self.assertEqual(rc, 0)
            oc_data = json.loads(out)
            self.assertTrue(oc_data["allow"])
            self.assertIn("[AGS Compass] Starlight", oc_data["additionalContext"])

            # Claude
            rc, out, _ = run_hook_cli("claude", "session_start", "{}", root=root)
            self.assertEqual(rc, 0)
            self.assertLessEqual(len(out.strip().splitlines()), 12)
            self.assertIn("[AGS Compass] Starlight", out)

    def test_post_edit_asset_json_and_naming_across_harnesses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup_game_project(root)
            data_dir = root / "assets" / "data"
            data_dir.mkdir(parents=True)
            bad_json = data_dir / "BadData.json"
            bad_json.write_text("{broken", encoding="utf-8")

            # Codex apply_patch
            codex_in = json.dumps({
                "tool_name": "apply_patch",
                "tool_input": {"command": "*** Begin Patch\n*** Add File: assets/data/BadData.json\n+{broken\n*** End Patch"},
            })
            rc, out, _ = run_hook_cli("codex", "post_edit", codex_in, root=root)
            self.assertEqual(rc, 0)
            codex_json = json.loads(out)
            self.assertEqual(codex_json["decision"], "block")
            self.assertIn("not valid JSON", codex_json["reason"])
            self.assertNotIn("NAMING:", codex_json["reason"])

            # Antigravity PreToolUse catches invalid JSON BEFORE write (PostToolUse returns {})
            ag_in = json.dumps({
                "toolCall": {
                    "name": "write_file",
                    "args": {"TargetFile": str(bad_json), "CodeContent": "{broken"},
                }
            })
            rc, out, _ = run_hook_cli("antigravity", "PreToolUse", ag_in, root=root)
            self.assertEqual(rc, 0)
            ag_pre = json.loads(out)
            self.assertEqual(ag_pre["decision"], "deny")
            self.assertIn("not valid JSON", ag_pre["reason"])

            rc, out, _ = run_hook_cli("antigravity", "PostToolUse", ag_in, root=root)
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out), {})

            # Engine-aware Godot 3 syntax check fires on post_edit AND PreToolUse write_file
            legacy_gd = root / "src" / "legacy.gd"
            legacy_gd.write_text("extends Node\nexport var speed = 5\n", encoding="utf-8")
            gd_in = json.dumps({
                "toolCall": {
                    "name": "write_file",
                    "args": {"TargetFile": str(legacy_gd), "CodeContent": "extends Node\nexport var speed = 5\n"},
                }
            })
            rc, out, _ = run_hook_cli("antigravity", "PreToolUse", gd_in, root=root)
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out)["decision"], "deny")
            self.assertIn("legacy Godot 3", json.loads(out)["reason"])

            rc, _, err = run_hook_cli("claude", "post_edit", json.dumps({"tool_name": "Write", "tool_input": {"file_path": "src/legacy.gd"}}), root=root)
            self.assertEqual(rc, 2)
            self.assertIn("legacy Godot 3", err)

            # OpenCode
            oc_in = json.dumps({
                "tool": "edit",
                "input": {"filePath": "assets/data/BadData.json"},
            })
            rc, out, _ = run_hook_cli("opencode", "post_edit", oc_in, root=root)
            self.assertEqual(rc, 0)
            oc_json = json.loads(out)
            self.assertFalse(oc_json["allow"])
            self.assertTrue(oc_json["blocked"])

            # Claude exit code 2
            cl_in = json.dumps({
                "tool_name": "Write",
                "tool_input": {"file_path": "assets\\data\\BadData.json"},
            })
            rc, _, err = run_hook_cli("claude", "post_edit", cl_in, root=root)
            self.assertEqual(rc, 2)
            self.assertIn("not valid JSON", err)

    def test_pre_command_block_and_allow_across_harnesses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup_game_project(root)

            # Tampering with receipt.json blocked
            tamper_cmd = "echo '{}' > .ags/state/receipt.json"
            payloads = {
                "codex": {"tool_name": "exec_command", "tool_input": {"cmd": tamper_cmd}},
                "antigravity": {"toolCall": {"name": "run_command", "args": {"CommandLine": tamper_cmd}}},
                "opencode": {"tool": "bash", "input": {"command": tamper_cmd}},
                "claude": {"tool_name": "Bash", "tool_input": {"command": tamper_cmd}},
            }
            for harness, payload in payloads.items():
                rc, out, err = run_hook_cli(harness, "pre_command", json.dumps(payload), root=root)
                if harness == "claude":
                    self.assertEqual(rc, 2)
                    self.assertIn("BLOCKED:", err)
                elif harness == "codex":
                    self.assertEqual(rc, 0)
                    self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "deny")
                elif harness == "antigravity":
                    self.assertEqual(rc, 0)
                    self.assertEqual(json.loads(out)["decision"], "deny")
                elif harness == "opencode":
                    self.assertEqual(rc, 0)
                    self.assertFalse(json.loads(out)["allow"])

            # Safe command allowed
            safe_payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}})
            rc, out, err = run_hook_cli("claude", "pre_command", safe_payload, root=root)
            self.assertEqual((rc, out, err), (0, "", ""))

            rc, out, _ = run_hook_cli("antigravity", "PreToolUse", safe_payload, root=root)
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out)["decision"], "allow")

            # Git commit with staged invalid JSON in assets/data/
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / "assets" / "data").mkdir(parents=True)
            (root / "assets" / "data" / "loot.json").write_text("{bad", encoding="utf-8")
            subprocess.run(["git", "add", "assets/data/loot.json"], cwd=root, check=True, capture_output=True)

            commit_in = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit -m test"}})
            rc, _, err = run_hook_cli("claude", "pre_command", commit_in, root=root)
            self.assertEqual(rc, 2)
            self.assertIn("not valid JSON", err)

            # Chained `git add <file> && git commit` also blocked even before git add runs
            (root / "assets" / "data" / "chained.json").write_text("{still_bad", encoding="utf-8")
            subprocess.run(["git", "reset", "HEAD", "assets/data/loot.json"], cwd=root, check=False, capture_output=True)
            chained_in = json.dumps({
                "tool_name": "Bash",
                "tool_input": {"command": "git add assets/data/chained.json && git commit -m chained"},
            })
            rc, _, err = run_hook_cli("claude", "pre_command", chained_in, root=root)
            self.assertEqual(rc, 2)
            self.assertIn("chained.json", err)
            self.assertIn("not valid JSON", err)

    def test_story_gate_receipt_enforcement_and_not_verified_rationale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup_game_project(root)
            story = root / "production" / "stories" / "S-01.md"
            story.parent.mkdir(parents=True)
            story.write_text("# Story S-01\nStatus: In Progress\n", encoding="utf-8")

            # 1) Block Status: Complete with NO receipt across all 4 harnesses
            harness_payloads = {
                "codex": {
                    "tool_name": "apply_patch",
                    "tool_input": {
                        "command": "*** Begin Patch\n*** Update File: production/stories/S-01.md\n+Status: Complete\n*** End Patch"
                    },
                },
                "antigravity": {
                    "toolCall": {
                        "name": "edit_file",
                        "args": {
                            "TargetFile": str(story),
                            "ReplacementContent": "Status: Complete",
                        },
                    }
                },
                "opencode": {
                    "tool": "edit",
                    "input": {
                        "filePath": "production/stories/S-01.md",
                        "newString": "Status: Complete",
                    },
                },
                "claude": {
                    "tool_name": "Edit",
                    "tool_input": {
                        "file_path": "production/stories/S-01.md",
                        "new_string": "Status: Complete",
                    },
                },
            }
            for harness, payload in harness_payloads.items():
                rc, out, err = run_hook_cli(harness, "pre_command", json.dumps(payload), root=root)
                if harness == "claude":
                    self.assertEqual(rc, 2, harness)
                    self.assertIn("BLOCKED by story_gate", err)
                elif harness == "codex":
                    self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "deny")
                elif harness == "antigravity":
                    self.assertEqual(json.loads(out)["decision"], "deny")
                elif harness == "opencode":
                    self.assertFalse(json.loads(out)["allow"])

            # 2) Generate valid PASS receipt -> allow Status: Complete
            with mock.patch("ags.checks.shutil.which", return_value=None):
                receipt = verify_project(root=root, write_receipt=True)
            self.assertEqual(receipt["verdict"], "PASS")

            for harness, payload in harness_payloads.items():
                rc, out, err = run_hook_cli(harness, "pre_command", json.dumps(payload), root=root)
                if harness == "claude":
                    self.assertEqual((rc, err), (0, ""))
                elif harness == "antigravity":
                    self.assertEqual(json.loads(out)["decision"], "allow")
                elif harness == "opencode":
                    self.assertTrue(json.loads(out)["allow"])
                elif harness == "codex":
                    self.assertEqual(out, "")

            # 3) Modify source file -> receipt becomes stale -> blocked again
            (root / "src" / "main.gd").write_text("extends Node2D\n", encoding="utf-8")
            rc, _, err = run_hook_cli("claude", "story_gate", json.dumps(harness_payloads["claude"]), root=root)
            self.assertEqual(rc, 2)
            self.assertIn("stale", err)

            # 4) Pre-existing template/placeholder NOT VERIFIED in disk text MUST NOT bypass story_gate
            story.write_text(
                "# Story S-01\nStatus: In Progress\nNote: if blocked, mark NOT VERIFIED: reason here.\n",
                encoding="utf-8",
            )
            bypass_attempt = json.dumps({
                "toolCall": {
                    "name": "edit_file",
                    "args": {"Path": str(story), "Replacement": "Status: Complete"},
                }
            })
            rc, out, _ = run_hook_cli("antigravity", "PreToolUse", bypass_attempt, root=root)
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out)["decision"], "deny")

            # 5) Explicit non-placeholder NOT VERIFIED rationale -> allowed with notice
            rationale_payload = json.dumps({
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "production/stories/S-01.md",
                    "content": "# Story S-01\nStatus: Complete\nVerification: NOT VERIFIED: Godot binary unavailable in CI\n",
                },
            })
            rc, out, err = run_hook_cli("claude", "story_gate", rationale_payload, root=root)
            self.assertEqual(rc, 0, err)
            self.assertIn("NOT VERIFIED", out)

    def test_checkpoint_sync_precompact_stop_dedup_and_off(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _setup_game_project(root)
            state_dir = root / "production" / "session-state"
            state_dir.mkdir(parents=True)
            active = state_dir / "active.md"
            active.write_text(
                "<!-- CHECKPOINT -->\nCurrent: S-02\n<!-- /CHECKPOINT -->\n",
                encoding="utf-8",
            )

            # PreCompact emits checkpoint and logs compaction
            rc, out, _ = run_hook_cli("codex", "PreCompact", "{}", root=root)
            self.assertEqual(rc, 0)
            ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("Current: S-02", ctx)
            self.assertTrue((root / "production" / "session-logs" / "compaction-log.txt").is_file())

            # Stop archives once, then deduplicates repeated firing with unchanged active.md
            run_hook_cli("claude", "checkpoint_sync", "{}", root=root)
            log_file = root / "production" / "session-logs" / "session-log.md"
            first_content = log_file.read_text(encoding="utf-8")
            self.assertIn("Current: S-02", first_content)
            run_hook_cli("claude", "checkpoint_sync", "{}", root=root)
            self.assertEqual(log_file.read_text(encoding="utf-8"), first_content)

            # features.session_state: off -> no-op
            (root / "project.local.yaml").write_text("features:\n  session_state: off\n", encoding="utf-8")
            rc, out, _ = run_hook_cli("claude", "PreCompact", "{}", root=root)
            self.assertEqual((rc, out), (0, ""))


if __name__ == "__main__":
    unittest.main()
