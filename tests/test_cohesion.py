"""Repository-wide cohesion, structural compliance, and parity tests for AGS v2."""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "core"
SKILLS_DIR = CORE / "skills"
AGENTS_DIR = CORE / "agents"
GATES_DIR = CORE / "gates"
RULES_DIR = CORE / "rules"
TEMPLATES_DIR = CORE / "templates"
ENGINE_REF_DIR = CORE / "engine-reference"

EXPECTED_SKILLS = (
    "ags-new-game",
    "ags-start",
    "ags-settings",
    "ags-adopt",
    "ags-ideate",
    "ags-gdd",
    "ags-art-ux",
    "ags-design-review",
    "ags-architect",
    "ags-arch-review",
    "ags-plan",
    "ags-dev",
    "ags-verify",
    "ags-qa",
    "ags-bugs",
    "ags-diagnose",
    "ags-team",
    "ags-gate",
    "ags-localize",
    "ags-release",
    "ags-skill-ops",
)

LEGACY_75_SKILLS = (
    "ccgs-adopt", "ccgs-architecture-decision", "ccgs-architecture-review",
    "ccgs-art-bible", "ccgs-asset-audit", "ccgs-asset-spec",
    "ccgs-balance-check", "ccgs-brainstorm", "ccgs-bug-report",
    "ccgs-bug-triage", "ccgs-changelog", "ccgs-code-review",
    "ccgs-consistency-check", "ccgs-content-audit", "ccgs-create-architecture",
    "ccgs-create-control-manifest", "ccgs-create-epics", "ccgs-create-stories",
    "ccgs-day-one-patch", "ccgs-design-review", "ccgs-design-system",
    "ccgs-dev-story", "ccgs-estimate", "ccgs-gate-check", "ccgs-help",
    "ccgs-hotfix", "ccgs-launch-checklist", "ccgs-localize",
    "ccgs-map-systems", "ccgs-milestone-review", "ccgs-new-game",
    "ccgs-onboard", "ccgs-patch-notes", "ccgs-perf-profile",
    "ccgs-playtest-report", "ccgs-project-stage-detect",
    "ccgs-propagate-design-change", "ccgs-prototype", "ccgs-qa-plan",
    "ccgs-quick-design", "ccgs-regression-suite", "ccgs-release-checklist",
    "ccgs-retrospective", "ccgs-reverse-document", "ccgs-review-all-gdds",
    "ccgs-scope-check", "ccgs-security-audit", "ccgs-settings",
    "ccgs-setup-engine", "ccgs-skill-improve", "ccgs-skill-test",
    "ccgs-smoke-check", "ccgs-soak-test", "ccgs-sprint-plan",
    "ccgs-sprint-status", "ccgs-start", "ccgs-story-done",
    "ccgs-story-readiness", "ccgs-team-audio", "ccgs-team-combat",
    "ccgs-team-level", "ccgs-team-live-ops", "ccgs-team-narrative",
    "ccgs-team-polish", "ccgs-team-qa", "ccgs-team-release",
    "ccgs-team-ui", "ccgs-tech-debt", "ccgs-test-evidence-review",
    "ccgs-test-flakiness", "ccgs-test-helpers", "ccgs-test-setup",
    "ccgs-ux-design", "ccgs-ux-review", "ccgs-vertical-slice",
)

LEGACY_49_AGENTS = (
    "accessibility-specialist", "ai-programmer", "analytics-engineer",
    "art-director", "audio-director", "community-manager", "creative-director",
    "devops-engineer", "economy-designer", "engine-programmer", "game-designer",
    "gameplay-programmer", "godot-csharp-specialist",
    "godot-gdextension-specialist", "godot-gdscript-specialist",
    "godot-shader-specialist", "godot-specialist", "lead-programmer",
    "level-designer", "live-ops-designer", "localization-lead",
    "narrative-director", "network-programmer", "performance-analyst",
    "producer", "prototyper", "qa-lead", "qa-tester", "release-manager",
    "security-engineer", "sound-designer", "systems-designer",
    "technical-artist", "technical-director", "tools-programmer",
    "ue-blueprint-specialist", "ue-gas-specialist", "ue-replication-specialist",
    "ue-umg-specialist", "ui-programmer", "unity-addressables-specialist",
    "unity-dots-specialist", "unity-shader-specialist", "unity-specialist",
    "unity-ui-specialist", "unreal-specialist", "ux-designer",
    "world-builder", "writer",
)

EXPECTED_CORE_ROLES = (
    "scout",
    "creative-director",
    "technical-director",
    "qa-lead",
    "code-reviewer",
    "producer",
    "game-designer",
    "art-ux-director",
    "prototyper",
    "gameplay-coder",
    "tech-artist",
    "test-engineer",
)

REQUIRED_SKILL_SECTIONS = (
    "## Contract",
    "## Preflight",
    "## Phases",
    "## Gate & Verdict",
)

FORBIDDEN_SKILL_PATTERNS = (
    ("May I write", re.compile(r"may i write", re.IGNORECASE)),
    ("Glob", re.compile(r"\bGlob\b")),
    ("Grep", re.compile(r"\bGrep\b")),
    ("AskUserQuestion", re.compile(r"\bAskUserQuestion\b")),
    ("subagent_type", re.compile(r"\bsubagent_type\b")),
    ("CLAUDE.md", re.compile(r"CLAUDE\.md")),
    ("yaml-helper.sh", re.compile(r"yaml-helper\.sh")),
    (".claude/", re.compile(r"\.claude/")),
    ("$ccgs-", re.compile(r"\$ccgs-")),
)

STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "for", "from",
    "if", "in", "into", "is", "it", "not", "of", "on", "or", "the", "to",
    "use", "when", "with", "you", "your",
})


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Extract top-level YAML key/value pairs from markdown frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("Missing opening '---' frontmatter fence")
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        raise ValueError("Missing closing '---' frontmatter fence")

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    data: dict[str, str] = {}
    current_key: str | None = None
    for raw in fm_lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] in (" ", "\t") and current_key is not None:
            data[current_key] = (data[current_key] + " " + raw.strip()).strip()
            continue
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", raw)
        if not m:
            raise ValueError(f"Invalid frontmatter line: {raw!r}")
        key = m.group(1)
        val = m.group(2).strip()
        if val in ("|", ">", "|-", ">-"):
            val = ""
        elif len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        data[key] = val
        current_key = key
    return data, body


def _all_role_stems() -> set[str]:
    """Return every role stem across core, engines, and lenses."""
    stems: set[str] = set()
    for folder in (
        AGENTS_DIR / "core",
        AGENTS_DIR / "engines" / "godot",
        AGENTS_DIR / "engines" / "unity",
        AGENTS_DIR / "engines" / "unreal",
        AGENTS_DIR / "lenses",
    ):
        if folder.is_dir():
            stems.update(p.stem for p in folder.glob("*.md"))
    return stems


def _extract_contract_field(text: str, label: str) -> str:
    """Extract the value of a `- Label: ...`, `**Label:** ...`, or `**Label**: ...` line."""
    m = re.search(
        rf"^(?:[-*]\s*)?(?:\*\*)?{re.escape(label)}(?::\*\*|\*\*:|:)\s*(.+)$",
        text,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else ""


class TestCohesion(unittest.TestCase):
    """Verify AGS v2 skill compliance, cross-references, parity, and build sync."""

    def test_all_21_skills_exist_and_comply(self) -> None:
        self.assertTrue(SKILLS_DIR.is_dir(), f"Missing {SKILLS_DIR}")
        actual = sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir())
        self.assertEqual(actual, sorted(EXPECTED_SKILLS))

        trigger_clauses: dict[str, str] = {}
        trigger_tokens: dict[str, set[str]] = {}

        for skill_name in EXPECTED_SKILLS:
            skill_md = SKILLS_DIR / skill_name / "SKILL.md"
            with self.subTest(skill=skill_name):
                self.assertTrue(skill_md.is_file(), f"Missing {skill_md}")
                text = skill_md.read_text(encoding="utf-8")
                lines = text.splitlines()
                self.assertLessEqual(
                    len(lines),
                    220,
                    f"{skill_name}/SKILL.md has {len(lines)} lines (>220)",
                )

                fm, _ = _parse_frontmatter(text)
                self.assertEqual(set(fm.keys()), {"name", "description"})
                self.assertEqual(fm["name"], skill_name)
                desc = fm["description"]
                self.assertTrue(desc, f"{skill_name} description is empty")
                self.assertIn("Use when", desc)

                for heading in REQUIRED_SKILL_SECTIONS:
                    self.assertRegex(
                        text,
                        rf"(?m)^{re.escape(heading)}\s*$",
                        f"{skill_name} missing section {heading!r}",
                    )

                for label, pattern in FORBIDDEN_SKILL_PATTERNS:
                    m = pattern.search(text)
                    self.assertIsNone(
                        m,
                        f"{skill_name}/SKILL.md contains forbidden token {label!r}: {m.group(0) if m else ''}",
                    )

                trigger = re.split(r"\bDo\s+NOT\s+use\b", desc, maxsplit=1)[0].strip()
                norm_trigger = re.sub(r"\s+", " ", trigger.lower())
                self.assertNotIn(
                    norm_trigger,
                    trigger_clauses.values(),
                    f"Duplicate trigger clause in {skill_name}: {trigger}",
                )
                trigger_clauses[skill_name] = norm_trigger
                words = set(re.findall(r"[a-z0-9-]+", norm_trigger)) - STOPWORDS
                trigger_tokens[skill_name] = words

        # Ensure trigger descriptions do not heavily overlap.
        names = list(EXPECTED_SKILLS)
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                ta, tb = trigger_tokens[a], trigger_tokens[b]
                if not ta or not tb:
                    continue
                jaccard = len(ta & tb) / len(ta | tb)
                self.assertLess(
                    jaccard,
                    0.75,
                    f"Trigger descriptions overlap excessively between {a} and {b} (Jaccard={jaccard:.2f})",
                )

    def test_skill_and_agents_references_resolve(self) -> None:
        role_stems = _all_role_stems()
        self.assertTrue(role_stems, "No role files found under core/agents/")
        skill_set = set(EXPECTED_SKILLS)
        agents_md = RULES_DIR / "AGENTS.md"
        self.assertTrue(agents_md.is_file(), f"Missing {agents_md}")
        agents_text = agents_md.read_text(encoding="utf-8")
        self.assertLess(
            len(agents_text.splitlines()),
            110,
            f"core/rules/AGENTS.md has {len(agents_text.splitlines())} lines (expected <110)",
        )

        # Every ags-* skill must appear in AGENTS.md routing table.
        for skill_name in EXPECTED_SKILLS:
            self.assertIn(skill_name, agents_text, f"{skill_name} missing from AGENTS.md")

        # Validate every ags-* skill name and role backtick/token in AGENTS.md routing table.
        for m in re.finditer(r"\bags-[a-z0-9-]+\b", agents_text):
            self.assertIn(m.group(0), skill_set, f"Unknown skill in AGENTS.md: {m.group(0)}")

        for row in agents_text.splitlines():
            if not row.strip().startswith("|") or "ags-" not in row:
                continue
            for token in re.findall(r"`([a-z][a-z0-9-]+)`", row):
                if token.startswith("ags-"):
                    self.assertIn(token, skill_set, f"Unknown skill {token} in AGENTS.md")
                elif token in role_stems:
                    continue
                elif token not in {"engine", "godot", "unity", "unreal"}:
                    # Any hyphenated role identifier in a routing row must resolve.
                    self.assertIn(
                        token,
                        role_stems,
                        f"Unresolved role {token!r} in AGENTS.md row: {row}",
                    )

        # Validate Contract Roles, Next Skill, and internal path references in all 21 skills.
        for skill_name in EXPECTED_SKILLS:
            skill_dir = SKILLS_DIR / skill_name
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

            roles_val = _extract_contract_field(text, "Roles")
            next_val = _extract_contract_field(text, "Next Skill")

            with self.subTest(skill=skill_name, check="next_skill"):
                for ref in re.findall(r"\bags-[a-z0-9-]+\b", next_val):
                    self.assertIn(
                        ref,
                        skill_set,
                        f"{skill_name} Next Skill references unknown skill {ref!r}",
                    )

            with self.subTest(skill=skill_name, check="roles"):
                for ref in re.findall(r"`([a-z][a-z0-9-]+)`", roles_val):
                    if ref.startswith("ags-"):
                        continue
                    if ref in {"none", "optional", "all"}:
                        continue
                    self.assertIn(
                        ref,
                        role_stems,
                        f"{skill_name} Contract Roles references unknown role {ref!r}",
                    )

            with self.subTest(skill=skill_name, check="paths"):
                for ref_path in re.findall(r"\breferences/[A-Za-z0-9_./-]+\.md\b", text):
                    self.assertTrue(
                        (skill_dir / ref_path).is_file(),
                        f"{skill_name} references missing file {ref_path}",
                    )
                for tpl in re.findall(r"\.ags/templates/([A-Za-z0-9_./-]+\.md)\b", text):
                    self.assertTrue(
                        (TEMPLATES_DIR / tpl).is_file(),
                        f"{skill_name} references missing template {tpl}",
                    )
                for gate in re.findall(r"\.ags/gates/([A-Za-z0-9_.-]+\.md)\b", text):
                    self.assertTrue(
                        (GATES_DIR / gate).is_file(),
                        f"{skill_name} references missing gate {gate}",
                    )
                for role in re.findall(r"\.ags/roles/([a-z0-9-]+)\.md\b", text):
                    self.assertIn(
                        role,
                        role_stems,
                        f"{skill_name} references missing role {role}.md",
                    )

    def test_parity_completeness(self) -> None:
        ledger = ROOT / "docs" / "PARITY-LEDGER.md"
        self.assertTrue(ledger.is_file(), f"Missing {ledger}")
        ledger_text = ledger.read_text(encoding="utf-8")

        self.assertEqual(len(LEGACY_75_SKILLS), 75)
        for name in LEGACY_75_SKILLS:
            self.assertIn(name, ledger_text, f"Legacy skill {name} missing from PARITY-LEDGER.md")

        self.assertEqual(len(LEGACY_49_AGENTS), 49)
        for agent_name in LEGACY_49_AGENTS:
            self.assertIn(
                agent_name,
                ledger_text,
                f"Legacy agent {agent_name} missing from PARITY-LEDGER.md",
            )

        # Templates: 46 .md files
        templates = list(TEMPLATES_DIR.rglob("*.md"))
        self.assertEqual(len(templates), 46, f"Expected 46 templates, got {len(templates)}")

        # Engine reference: 46 files
        engine_refs = [p for p in ENGINE_REF_DIR.rglob("*") if p.is_file()]
        self.assertEqual(
            len(engine_refs),
            46,
            f"Expected 46 engine reference files, got {len(engine_refs)}",
        )

        # Gates: 28 gates + INDEX.md
        gate_files = [p for p in GATES_DIR.glob("*.md") if p.name != "INDEX.md"]
        self.assertEqual(len(gate_files), 28, f"Expected 28 gate files, got {len(gate_files)}")
        self.assertTrue((GATES_DIR / "INDEX.md").is_file(), "Missing core/gates/INDEX.md")

        # Agents: 12 core + 15 engine (5x3) + 22+ lenses
        core_agents = sorted(p.stem for p in (AGENTS_DIR / "core").glob("*.md"))
        self.assertEqual(set(core_agents), set(EXPECTED_CORE_ROLES))
        self.assertEqual(len(core_agents), 12)

        for engine in ("godot", "unity", "unreal"):
            eng_agents = list((AGENTS_DIR / "engines" / engine).glob("*.md"))
            self.assertEqual(
                len(eng_agents),
                5,
                f"Expected 5 engine agents for {engine}, got {len(eng_agents)}",
            )

        lenses = list((AGENTS_DIR / "lenses").glob("*.md"))
        self.assertGreaterEqual(
            len(lenses),
            22,
            f"Expected >= 22 lens files, got {len(lenses)}",
        )

        # Rules: AGENTS.md + 13 rule files
        rule_files = [p for p in RULES_DIR.glob("*.md") if p.name != "AGENTS.md"]
        self.assertEqual(len(rule_files), 13, f"Expected 13 rule files, got {len(rule_files)}")

        # Workflow catalog
        self.assertTrue((CORE / "workflow-catalog.yaml").is_file())

    def test_build_check_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", "-m", "ags.build", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"`python -m ags.build --check` failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
