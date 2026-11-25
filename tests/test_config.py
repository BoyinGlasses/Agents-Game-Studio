"""Unit tests for ags.config pure-Python YAML parser, resolver, and preflight."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ags.config import (
    ALWAYS_ASK_DEFAULT,
    load_yaml,
    parse_frontmatter,
    parse_yaml,
    parse_yaml_with_diagnostics,
    preflight,
    resolve_code_root,
    resolve_config,
    session_state_enabled,
    validate_local_scope,
)


class TestYamlParser(unittest.TestCase):
    """Test pure-Python YAML subset parsing and edge cases."""

    def test_nested_maps_lists_quotes_comments_and_nulls(self) -> None:
        raw = (
            "\ufeff# header comment\r\n"
            "schema_version: 1\r\n"
            "modes:\r\n"
            "  rigor: standard  # inline comment\r\n"
            "  review_mode: \"\"\r\n"
            "  workflow: null\r\n"
            "  automation: ~\r\n"
            "  automation_always_ask: [scope_changes, \"a, b\", 'x#y']\r\n"
            "engine:\r\n"
            "  name: \"Godot\"\r\n"
            "  version: '4.3'\r\n"
            "tags:\r\n"
            "  - core\r\n"
            "  - \"combat #v2\"\r\n"
        )
        data = parse_yaml(raw)
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["modes"]["rigor"], "standard")
        self.assertIsNone(data["modes"]["review_mode"])
        self.assertIsNone(data["modes"]["workflow"])
        self.assertIsNone(data["modes"]["automation"])
        self.assertEqual(
            data["modes"]["automation_always_ask"],
            ["scope_changes", "a, b", "x#y"],
        )
        self.assertEqual(data["engine"]["name"], "Godot")
        self.assertEqual(data["engine"]["version"], "4.3")
        self.assertEqual(data["tags"], ["core", "combat #v2"])

    def test_tab_indentation_captured_in_diagnostics(self) -> None:
        raw = "modes:\n\tworkflow: full\n"
        diag = parse_yaml_with_diagnostics(raw)
        self.assertEqual(diag.tab_lines, [2])
        self.assertTrue(any("TAB" in err for err in diag.errors))
        self.assertNotIn("workflow", diag.data.get("modes") or {})

    def test_frontmatter_and_multiline_block_scalars(self) -> None:
        md = (
            "---\n"
            "name: ags-dev\n"
            "description: |\n"
            "  Line one.\n"
            "  Line two.\n"
            "---\n"
            "# Body\n"
        )
        meta, body = parse_frontmatter(md)
        self.assertEqual(meta["name"], "ags-dev")
        self.assertEqual(meta["description"], "Line one.\nLine two.")
        self.assertEqual(body, "# Body")

    def test_trailing_zero_versions_and_literal_block_blank_hash_lines(self) -> None:
        raw = (
            "engine:\n"
            "  name: Godot\n"
            "  version: 4.10\n"
            "  minor: 6.0\n"
            "  budget_ms: 16.67\n"
            "notes: |\n"
            "  First line\n"
            "\n"
            "  # Heading inside block\n"
            "  Second line\n"
            "next_key: ok\n"
        )
        data = parse_yaml(raw)
        self.assertEqual(data["engine"]["version"], "4.10")
        self.assertEqual(data["engine"]["minor"], "6.0")
        self.assertEqual(data["engine"]["budget_ms"], 16.67)
        self.assertEqual(data["notes"], "First line\n\n# Heading inside block\nSecond line")
        self.assertEqual(data["next_key"], "ok")


class TestConfigResolution(unittest.TestCase):
    """Test resolution precedence, rigor expansion, overrides, and null handling."""

    def test_unconfigured_defaults_use_minimal_rigor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = resolve_config(root)
            self.assertFalse(cfg["project_configured"])
            vals = cfg["values"]
            srcs = cfg["sources"]
            self.assertEqual(vals["rigor"], "minimal")
            self.assertEqual(srcs["rigor"], "default")
            self.assertEqual(vals["automation"], "collaborative")
            self.assertEqual(srcs["automation"], "default")
            self.assertEqual(vals["performance.enforce"], "warn")
            self.assertEqual(vals["workflow"], "minimal")
            self.assertEqual(srcs["workflow"], "rigor:minimal")
            self.assertEqual(vals["docs.density"], "terse")
            self.assertEqual(vals["qa.level"], "minimal")
            self.assertEqual(vals["story_granularity"], "coarse")
            self.assertEqual(vals["review_mode"], "solo")
            self.assertEqual(vals["team.size"], "individual")
            self.assertEqual(vals["automation_always_ask"], ALWAYS_ASK_DEFAULT)
            self.assertTrue(any("project.yaml absent" in n for n in cfg["notes"]))

    def test_rigor_aliases_expand_all_six_fronted_knobs(self) -> None:
        cases = {
            "jam": ("minimal", "minimal", "terse", "minimal", "coarse", "solo", "individual"),
            "indie": ("standard", "standard", "balanced", "standard", "balanced", "lean", "individual"),
            "studio": ("full", "full", "thorough", "full", "fine", "full", "studio"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for alias, expected in cases.items():
                proj = Path(tmp) / alias
                proj.mkdir()
                (proj / "project.yaml").write_text(
                    f"modes:\n  rigor: {alias}\n",
                    encoding="utf-8",
                )
                cfg = resolve_config(proj)
                vals = cfg["values"]
                srcs = cfg["sources"]
                norm = expected[0]
                self.assertEqual(vals["rigor"], norm)
                self.assertEqual(vals["workflow"], expected[1])
                self.assertEqual(vals["docs.density"], expected[2])
                self.assertEqual(vals["qa.level"], expected[3])
                self.assertEqual(vals["story_granularity"], expected[4])
                self.assertEqual(vals["review_mode"], expected[5])
                self.assertEqual(vals["team.size"], expected[6])
                self.assertEqual(srcs["workflow"], f"rigor:{norm}")

    def test_precedence_local_over_yaml_over_rigor_and_null_fallthrough(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "production").mkdir()
            (root / "production" / "review-mode.txt").write_text("lean\n", encoding="utf-8")
            (root / "project.yaml").write_text(
                "schema_version: 1\n"
                "modes:\n"
                "  rigor: full\n"
                "  workflow: \"\"\n"
                "  review_mode: null\n"
                "docs:\n"
                "  density: terse\n"
                "testing:\n"
                "  strict:\n"
                "    logic: true\n"
                "    integration: true\n"
                "workflow_overrides:\n"
                "  system_overrides:\n"
                "    combat: minimal\n"
                "    inventory: studio\n",
                encoding="utf-8",
            )
            (root / "project.local.yaml").write_text(
                "schema_version: 1\n"
                "modes:\n"
                "  review_mode: solo\n"
                "  automation: guided\n"
                "  rigor: minimal\n"
                "testing:\n"
                "  strict:\n"
                "    logic: false\n",
                encoding="utf-8",
            )

            cfg = resolve_config(root, system="combat")
            vals = cfg["values"]
            srcs = cfg["sources"]

            # project.local.yaml wins for whitelisted settings.
            self.assertEqual(vals["review_mode"], "solo")
            self.assertEqual(srcs["review_mode"], "project.local.yaml")
            self.assertEqual(vals["automation"], "guided")
            self.assertEqual(srcs["automation"], "project.local.yaml")

            # Non-whitelisted modes.rigor in local is ignored and flagged.
            self.assertEqual(vals["rigor"], "full")
            self.assertEqual(srcs["rigor"], "project.yaml")
            self.assertIn("modes.rigor", validate_local_scope(load_yaml(root / "project.local.yaml").data))
            self.assertTrue(any("not locally overridable" in n and "modes.rigor" in n for n in cfg["notes"]))

            # Explicit docs.density in project.yaml beats rigor:full expansion.
            self.assertEqual(vals["docs.density"], "terse")
            self.assertEqual(srcs["docs.density"], "project.yaml")

            # Empty "" modes.workflow falls through to rigor:full.
            self.assertEqual(vals["workflow"], "full")
            self.assertEqual(srcs["workflow"], "rigor:full")

            # system_overrides beats project workflow for targeted system.
            self.assertEqual(cfg["system_overrides"], {"combat": "minimal", "inventory": "full"})
            self.assertEqual(cfg["effective_workflow"], "minimal")
            self.assertEqual(cfg["effective_workflow_source"], "system_overrides")

            # Deep merge on testing.strict.*
            self.assertEqual(cfg["testing_strict"]["logic"], "false")
            self.assertEqual(cfg["testing_strict"]["integration"], "true")
            self.assertIsNone(cfg["testing_strict"]["visual"])

    def test_local_null_falls_back_to_base_and_invalid_enum_falls_through(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.yaml").write_text(
                "modes:\n"
                "  automation: autonomous\n"
                "  workflow: bogus_tier\n",
                encoding="utf-8",
            )
            (root / "project.local.yaml").write_text(
                "modes:\n"
                "  automation: null\n"
                "features:\n"
                "  session_state: off\n",
                encoding="utf-8",
            )
            cfg = resolve_config(root)
            self.assertEqual(cfg["values"]["automation"], "autonomous")
            self.assertEqual(cfg["sources"]["automation"], "project.yaml")
            self.assertEqual(cfg["values"]["workflow"], "minimal")
            self.assertEqual(cfg["sources"]["workflow"], "rigor:minimal")
            self.assertTrue(any("modes.workflow" in n and "ignored" in n for n in cfg["notes"]))
            self.assertFalse(session_state_enabled(root))

    def test_code_root_resolution_and_preflight_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.yaml").write_text(
                "engine:\n"
                "  name: Unity\n"
                "  version: '6000.0'\n"
                "modes:\n"
                "  rigor: standard\n"
                "workflow_overrides:\n"
                "  system_overrides:\n"
                "    ai: full\n",
                encoding="utf-8",
            )
            (root / "production" / "session-state").mkdir(parents=True)
            (root / "production" / "session-state" / "active.md").write_text("line1\nline2\n", encoding="utf-8")
            (root / ".ags" / "state").mkdir(parents=True)
            (root / ".ags" / "state" / "receipt.json").write_text(
                '{"verdict": "PASS", "tree_hash": "abc123", "timestamp": "2026-11-24T00:00:00Z"}',
                encoding="utf-8",
            )

            self.assertEqual(resolve_code_root(root), ("Assets", "engine.name"))
            pf = preflight("ags-gdd", target="ai", root=root)
            self.assertEqual(pf["skill"], "ags-gdd")
            self.assertEqual(pf["system"], "ai")
            self.assertEqual(pf["effective_workflow"], "full")
            self.assertEqual(pf["effective_workflow_source"], "system_overrides")
            self.assertEqual(pf["engine"]["code_root"], "Assets")
            self.assertTrue(pf["session_state"]["enabled"])
            self.assertEqual(pf["session_state"]["lines"], 2)
            self.assertTrue(pf["receipt"]["exists"])
            self.assertEqual(pf["receipt"]["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
