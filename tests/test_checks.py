"""Unit tests for ags.checks (8 ported studio checks + engine-aware validators + receipts)."""

from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from ags.checks import (
    adr_dep_graph,
    artifact_check,
    compute_tree_hash,
    gdd_structure_check,
    migrate_v1_config,
    project_coherence,
    review_receipts,
    review_scope,
    rotate_session_state,
    verify_project,
)


class TestPortedChecks(unittest.TestCase):
    """Test all 8 bash script ports in ags.checks."""

    def test_adr_dep_graph_acyclic_missing_section_and_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp) / "docs" / "architecture"
            adr_dir.mkdir(parents=True)
            (adr_dir / "adr-0001-core.md").write_text(
                "# ADR-0001\n\n## ADR Dependencies\n| **Depends On** | None |\n",
                encoding="utf-8",
            )
            (adr_dir / "adr-0002-combat.md").write_text(
                "# ADR-0002\n\n## ADR Dependencies\n| **Depends On** | ADR-0001, ADR-0003 |\n",
                encoding="utf-8",
            )
            (adr_dir / "adr-0003-damage.md").write_text(
                "# ADR-0003\n\n## ADR Dependencies\n| **Depends On** | ADR-0002 |\n",
                encoding="utf-8",
            )
            (adr_dir / "adr-0004-audio.md").write_text(
                "# ADR-0004\n\n## Context\nNo deps section.\n",
                encoding="utf-8",
            )

            res = adr_dep_graph(adr_dir=adr_dir)
            self.assertEqual(res.returncode, 0)
            self.assertIn("ADRS: 4", res.stdout)
            self.assertIn("adr-0002 -> adr-0001", res.stdout)
            self.assertIn("adr-0002 -> adr-0003", res.stdout)
            self.assertIn("adr-0003 -> adr-0002", res.stdout)
            self.assertIn("NO_DEPS_SECTION: adr-0004", res.stdout)
            self.assertIn("CYCLE: adr-0002", res.stdout)
            self.assertIn("CYCLE: adr-0003", res.stdout)
            self.assertNotIn("CYCLE: adr-0001", res.stdout)

    def test_gdd_structure_check_alias_and_non_system_exclusion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gdd_dir = root / "design" / "gdd"
            gdd_dir.mkdir(parents=True)
            # Excluded governance file
            (gdd_dir / "systems-index.md").write_text("# Index\n", encoding="utf-8")
            # System GDD using "Detailed Design" alias
            (gdd_dir / "combat.md").write_text(
                "## Overview\nok\n"
                "## 2. Detailed Design\nok\n"
                "## Edge Cases\nok\n"
                "## Dependencies\n- loot.md\n"
                "## Acceptance Criteria\nok\n",
                encoding="utf-8",
            )

            res = gdd_structure_check(root=root)
            self.assertEqual(res.returncode, 0)
            self.assertNotIn("systems-index.md", res.stdout)
            self.assertIn("combat.md PRESENT: Overview,Detailed Rules,Edge Cases,Dependencies,Acceptance Criteria", res.stdout)
            self.assertIn("combat.md ABSENT:  Player Fantasy,Formulas,Tuning Knobs", res.stdout)

    def test_artifact_check_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".ags").mkdir()
            (root / ".ags" / "workflow-catalog.yaml").write_text(
                "phases:\n"
                "  concept:\n"
                "    steps:\n"
                "      - id: present-step\n"
                "        required: true\n"
                "        artifact:\n"
                "          glob: \"design/*.md\"\n"
                "          pattern: \"Engine:[[:space:]]*Godot\"\n"
                "      - id: miss-pattern\n"
                "        required: true\n"
                "        artifact:\n"
                "          glob: \"docs/*.md\"\n"
                "          pattern: \"MUST_EXIST\"\n"
                "      - id: short-step\n"
                "        required: false\n"
                "        artifact:\n"
                "          glob: \"items/*.txt\"\n"
                "          min_count: 2\n"
                "      - id: absent-step\n"
                "        required: true\n"
                "        artifact:\n"
                "          glob: \"missing/*.md\"\n"
                "      - id: anyof-step\n"
                "        required: true\n"
                "        artifact:\n"
                "          any_of:\n"
                "            - glob: \"nope.yaml\"\n"
                "            - glob: \"project.yaml\"\n"
                "              pattern: \"Godot\"\n"
                "      - id: nocheck-step\n"
                "        required: false\n"
                "        artifact:\n"
                "          note: \"Manual check\"\n",
                encoding="utf-8",
            )
            (root / "design").mkdir()
            (root / "design" / "ok.md").write_text("Engine: Godot\n", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "other.md").write_text("nothing here\n", encoding="utf-8")
            (root / "items").mkdir()
            (root / "items" / "one.txt").write_text("1\n", encoding="utf-8")
            (root / "project.yaml").write_text("engine:\n  name: Godot\n", encoding="utf-8")

            res = artifact_check(phase="concept", root=root)
            self.assertEqual(res.returncode, 0)
            self.assertIn("PHASES: 1", res.stdout)
            self.assertIn("STEPS: 6", res.stdout)
            self.assertIn("NO_CHECK: 1", res.stdout)
            self.assertIn("STEP: present-step required=true repeatable=false check=glob status=PRESENT", res.stdout)
            self.assertIn("STEP: miss-pattern required=true repeatable=false check=glob status=PATTERN_MISS", res.stdout)
            self.assertIn("STEP: short-step required=false repeatable=false check=glob status=SHORT", res.stdout)
            self.assertIn("STEP: absent-step required=true repeatable=false check=glob status=ABSENT", res.stdout)
            self.assertIn("STEP: anyof-step required=true repeatable=false check=any_of status=PRESENT", res.stdout)
            self.assertIn("STEP: nocheck-step required=false repeatable=false check=none status=NO_CHECK", res.stdout)

    def test_project_coherence_godot_matches_and_diffs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "engine-reference" / "godot").mkdir(parents=True)
            (root / "docs" / "engine-reference" / "godot" / "VERSION.md").write_text(
                "| **Engine Version** | 4.3 |\n"
                "| **Installed at pin time** | 4.3.stable |\n",
                encoding="utf-8",
            )
            (root / "project.yaml").write_text(
                "engine:\n"
                "  name: Godot\n"
                "  version: '4.3'\n"
                "  rendering: Forward+\n"
                "  physics: Jolt\n"
                "commands:\n"
                "  build: godot --headless --export-debug Windows\n",
                encoding="utf-8",
            )
            (root / "project.godot").write_text(
                'config_version=5\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n',
                encoding="utf-8",
            )
            (root / "src").mkdir()
            (root / "src" / "player.gd").write_text("extends CharacterBody2D\n", encoding="utf-8")

            with mock.patch("ags.checks.shutil.which", return_value=None):
                res = project_coherence(root=root)

            self.assertEqual(res.returncode, 0)
            self.assertIn("[MATCH]", res.stdout)
            self.assertIn("[DIFFERS]", res.stdout)
            self.assertIn("gl_compatibility", res.stdout)
            self.assertIn("2D nodes were found under src/", res.stdout)
            self.assertIn("no export_presets.cfg", res.stdout)

    def test_review_receipts_content_and_section_delta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gdd = root / "combat.md"
            gdd.write_text(
                "Intro line\n"
                "## Overview\n"
                "Original overview\n"
                "## Edge Cases\n"
                "Original edges\n",
                encoding="utf-8",
            )
            receipt = root / "receipt.log"

            h_res = review_receipts(["hash", "combat.md"], root=root)
            sh_res = review_receipts(["sections-hash", "combat.md"], root=root)
            self.assertEqual(h_res.returncode, 0)
            self.assertEqual(sh_res.returncode, 0)
            receipt.write_text(h_res.stdout + sh_res.stdout, encoding="utf-8")

            # Unchanged before edit + unexpanded glob detection + missing optional literal silent.
            c1 = review_receipts(["check", "receipt.log", "combat.md", "optional.yaml", "missing/*.md"], root=root)
            self.assertEqual(c1.returncode, 0)
            self.assertIn("UNCHANGED: combat.md", c1.stdout)
            self.assertNotIn("optional.yaml", c1.stdout)
            self.assertIn("UNRESOLVED: missing/*.md", c1.stdout)

            # Edit only Edge Cases and add Formulas
            gdd.write_text(
                "Intro line\n"
                "## Overview\n"
                "Original overview\n"
                "## Edge Cases\n"
                "Modified edges\n"
                "## Formulas\n"
                "dmg = 10\n",
                encoding="utf-8",
            )

            c2 = review_receipts(["check", "receipt.log", "combat.md"], root=root)
            self.assertIn("CHANGED: combat.md", c2.stdout)

            sc = review_receipts(["sections-check", "receipt.log", "combat.md"], root=root)
            self.assertEqual(sc.returncode, 0)
            self.assertIn("SECTION-UNCHANGED: __preamble__", sc.stdout)
            self.assertIn("SECTION-UNCHANGED: Overview", sc.stdout)
            self.assertIn("SECTION-CHANGED: Edge Cases", sc.stdout)
            self.assertIn("SECTION-NEW: Formulas", sc.stdout)

    def test_review_scope_mtime_fallback_and_deps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gdd_dir = root / "design" / "gdd"
            gdd_dir.mkdir(parents=True)
            prior = gdd_dir / "gdd-cross-review-2026-10-01.md"
            prior.write_text("# Review\n", encoding="utf-8")
            old_ts = time.time() - 100
            os.utime(prior, (old_ts, old_ts))

            old_gdd = gdd_dir / "inventory.md"
            old_gdd.write_text("## Overview\nUnchanged\n", encoding="utf-8")
            os.utime(old_gdd, (old_ts - 10, old_ts - 10))

            new_gdd = gdd_dir / "combat.md"
            new_gdd.write_text("## Overview\nNew\n## Dependencies\n- inventory.md\n", encoding="utf-8")
            new_ts = time.time()
            os.utime(new_gdd, (new_ts, new_ts))

            res = review_scope(root=root)
            self.assertEqual(res.returncode, 0)
            self.assertIn("PRIOR_REVIEW: design/gdd/gdd-cross-review-2026-10-01.md", res.stdout)
            self.assertIn("design/gdd/combat.md", res.stdout)
            self.assertNotIn("design/gdd/inventory.md\n", res.stdout)
            self.assertIn("combat.md -> inventory.md", res.stdout)

    def test_rotate_session_state_dry_run_and_execute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_dir = root / "production" / "session-state"
            state_dir.mkdir(parents=True)
            active = state_dir / "active.md"

            # Refused without marker
            active.write_text("# Active\nline1\nline2\n", encoding="utf-8")
            refused = rotate_session_state(root=root)
            self.assertEqual(refused.returncode, 3)
            self.assertIn("REFUSED:", refused.stdout)

            # Valid checkpoint + 8 lines narrative
            narrative = "\n".join(f"Note {i}" for i in range(1, 9))
            active.write_text(
                "<!-- CHECKPOINT -->\n"
                "Phase: Production\n"
                "<!-- /CHECKPOINT -->\n"
                + narrative
                + "\n",
                encoding="utf-8",
            )
            dry = rotate_session_state(dry_run=True, root=root)
            self.assertEqual(dry.returncode, 0)
            self.assertIn("DRY RUN", dry.stdout)
            self.assertFalse((root / "production" / "session-logs").exists())

            real = rotate_session_state(dry_run=False, root=root)
            self.assertEqual(real.returncode, 0)
            self.assertIn("rotated 8 lines", real.stdout)
            new_text = active.read_text(encoding="utf-8")
            self.assertIn("Phase: Production", new_text)
            self.assertNotIn("Note 8", new_text)
            logs = list((root / "production" / "session-logs").glob("session-state-*.md"))
            self.assertEqual(len(logs), 1)
            self.assertIn("Note 8", logs[0].read_text(encoding="utf-8"))

    def test_migrate_v1_config_dry_run_migrate_and_finalize(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "production").mkdir(parents=True)
            (root / ".claude" / "docs").mkdir(parents=True)
            (root / "production" / "stage.txt").write_text("Systems Design\n", encoding="utf-8")
            (root / "production" / "review-mode.txt").write_text("none\n", encoding="utf-8")
            (root / ".claude" / "docs" / "technical-preferences.md").write_text(
                "## Engine & Language\n"
                "- **Engine**: Godot 4.3\n"
                "- **Language**: GDScript\n\n"
                "## Performance Budgets\n"
                "- **Target Framerate**: 60fps\n"
                "- **Frame Budget**: 16.67ms\n\n"
                "## Engine Specialists\n"
                "- **Language/Code Specialist**: godot-gdscript-specialist (gameplay scripts)\n",
                encoding="utf-8",
            )

            dry = migrate_v1_config(dry_run=True, root=root)
            self.assertEqual(dry.returncode, 0)
            self.assertIn("DRY RUN", dry.stdout)
            self.assertFalse((root / "project.yaml").exists())

            mig = migrate_v1_config(root=root)
            self.assertEqual(mig.returncode, 0)
            py_text = (root / "project.yaml").read_text(encoding="utf-8")
            self.assertIn('stage: "Systems Design"', py_text)
            self.assertIn("review_mode: solo", py_text)
            self.assertIn('name: "Godot"', py_text)
            self.assertIn('version: "4.3"', py_text)
            self.assertIn("target_framerate: 60", py_text)
            self.assertIn('code: "godot-gdscript-specialist"', py_text)
            self.assertTrue((root / "production" / "migration-report.md").is_file())

            # Second migrate refuses while legacy leftovers + migration-report exist
            second = migrate_v1_config(root=root)
            self.assertEqual(second.returncode, 3)

            # Finalize deletes stage.txt & review-mode.txt, preserves technical-preferences.md
            fin = migrate_v1_config(finalize=True, root=root)
            self.assertEqual(fin.returncode, 0)
            self.assertFalse((root / "production" / "stage.txt").exists())
            self.assertFalse((root / "production" / "review-mode.txt").exists())
            self.assertTrue((root / ".claude" / "docs" / "technical-preferences.md").exists())


class TestEngineValidatorsAndReceipts(unittest.TestCase):
    """Test Godot, Unity, Unreal static validators and receipt.json generation."""

    def test_godot_legacy_syntax_and_broken_ext_resource(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.yaml").write_text("engine:\n  name: Godot\n", encoding="utf-8")
            (root / "project.godot").write_text("config_version=5\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "bad.gd").write_text(
                "extends Node\n"
                "export var hp = 10\n"
                "onready var label = $Label\n"
                "func _ready():\n"
                "    var s = preload('res://x.tscn').instance()\n"
                "    connect(\"pressed\", self, \"_on_press\")\n"
                "    yield(get_tree(), \"idle_frame\")\n",
                encoding="utf-8",
            )
            (root / "src" / "main.tscn").write_text(
                '[gd_scene format=3]\n[ext_resource type="Script" path="res://src/missing.gd" id="1"]\n',
                encoding="utf-8",
            )

            with mock.patch("ags.checks.shutil.which", return_value=None):
                receipt = verify_project(root=root, write_receipt=True)

            self.assertEqual(receipt["engine"], "godot")
            self.assertEqual(receipt["verdict"], "FAIL")
            checks = {c["name"]: c for c in receipt["checks"]}
            self.assertEqual(checks["godot_gdscript_syntax"]["status"], "FAIL")
            errs = "\n".join(checks["godot_gdscript_syntax"]["errors"])
            for needle in ("yield()", "export var", "onready var", ".instance()", "connect()"):
                self.assertIn(needle, errs)
            self.assertEqual(checks["godot_ext_resource_paths"]["status"], "FAIL")
            self.assertIn("res://src/missing.gd", "\n".join(checks["godot_ext_resource_paths"]["errors"]))

            receipt_file = root / ".ags" / "state" / "receipt.json"
            self.assertTrue(receipt_file.is_file())
            loaded = json.loads(receipt_file.read_text(encoding="utf-8"))
            self.assertEqual(loaded["tree_hash"], compute_tree_hash(root))

    def test_unity_meta_pairs_and_update_antipatterns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.yaml").write_text("engine:\n  name: Unity\n", encoding="utf-8")
            assets = root / "Assets"
            scripts = assets / "Scripts"
            scripts.mkdir(parents=True)
            # Missing directory .meta for Scripts, missing file .meta for Player.cs, orphaned Ghost.cs.meta
            (scripts / "Player.cs").write_text(
                "public class Player {\n"
                "  void Update() {\n"
                "    var rb = GetComponent<Rigidbody>();\n"
                "    var mgr = FindObjectOfType<GameManager>();\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )
            (scripts / "Ghost.cs.meta").write_text("guid: 123\n", encoding="utf-8")

            with mock.patch("ags.checks.shutil.which", return_value=None):
                receipt = verify_project(root=root, write_receipt=True)

            self.assertEqual(receipt["engine"], "unity")
            self.assertEqual(receipt["verdict"], "FAIL")
            checks = {c["name"]: c for c in receipt["checks"]}
            self.assertEqual(checks["unity_meta_pairs"]["status"], "FAIL")
            meta_txt = "\n".join(checks["unity_meta_pairs"]["errors"])
            self.assertIn("missing .meta for directory Assets/Scripts", meta_txt)
            self.assertIn("missing .meta for file Assets/Scripts/Player.cs", meta_txt)
            self.assertIn("orphaned .meta file Assets/Scripts/Ghost.cs.meta", meta_txt)
            self.assertEqual(checks["unity_update_antipatterns"]["status"], "WARN")
            self.assertEqual(len(checks["unity_update_antipatterns"]["warnings"]), 2)

    def test_unreal_generated_h_order_pass_and_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.yaml").write_text("engine:\n  name: Unreal\n", encoding="utf-8")
            src = root / "Source" / "MyGame"
            src.mkdir(parents=True)
            bad_h = src / "Hero.h"
            bad_h.write_text(
                "#pragma once\n"
                '#include "CoreMinimal.h"\n'
                '#include "Hero.generated.h"\n'
                '#include "OtherHeader.h"\n'
                "UCLASS()\n"
                "class AHero : public AActor {};\n",
                encoding="utf-8",
            )

            fail_receipt = verify_project(root=root, write_receipt=True)
            self.assertEqual(fail_receipt["verdict"], "FAIL")
            self.assertIn(".generated.h must be the last #include", "\n".join(fail_receipt["errors"]))

            # Fix include order and verify PASS receipt + stable tree hash.
            bad_h.write_text(
                "#pragma once\n"
                '#include "CoreMinimal.h"\n'
                '#include "OtherHeader.h"\n'
                '#include "Hero.generated.h"\n'
                "UCLASS()\n"
                "class AHero : public AActor {};\n",
                encoding="utf-8",
            )
            pass_receipt = verify_project(root=root, write_receipt=True)
            self.assertEqual(pass_receipt["verdict"], "PASS")
            self.assertEqual(pass_receipt["errors"], [])
            # Tree hash excludes .ags/state/receipt.json itself
            self.assertEqual(pass_receipt["tree_hash"], compute_tree_hash(root))


if __name__ == "__main__":
    unittest.main()
