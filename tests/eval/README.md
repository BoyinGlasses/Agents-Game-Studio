# AGS v2 Skill & Agent Eval Framework

Quality assurance suite for the **Agents Game Studio (AGS v2)** framework.
Tests the studio skills and role definitions themselves — **not** any game built with AGS v2.

> **Framework-only test suite:** Unlike CCGS v1, `tests/eval/` stays in the AGS v2 framework
> repository and is **NOT copied into user game projects** during `ags init`.
> Driven by `ags-skill-ops` (`static`, `spec`, `category`, `audit`, `improve`) and `tests/test_cohesion.py`.

---

## Layout

```text
tests/eval/
├── README.md              <- this overview
├── AGENTS.md              <- eval execution guide for agents
├── catalog.yaml           <- registry mapping 21 ags-* skills + 49 legacy/core/engine roles
├── quality-rubric.md      <- AGS v2 structural, harness, and category pass/fail rubric
├── skills/                <- behavioral spec files (migrated & modernized from CCGS v1)
├── agents/                <- role behavioral specs (core, directors, leads, specialists, engine, operations, qa)
├── templates/             <- spec templates (skill-test-spec.md, agent-test-spec.md)
└── results/               <- optional run outputs (gitignored)
```

---

## Key AGS v2 Evaluation Standards

1. **<= 220-line `SKILL.md` budget:** Every `core/skills/ags-*/SKILL.md` stays at or below 220 lines; detailed sub-mode workflows live in `references/*.md` and `CONTRACT.md`.
2. **Closed-loop structural headings:** Every `SKILL.md` defines `## Contract`, `## Preflight` (`python .ags/cli.py preflight <skill>`), `## Phases`, and `## Gate & Verdict`.
3. **Story Checkpoint Harness:** `ags-dev` and `ags-verify` enforce two human checkpoints (story approval before coding; evidence/play acceptance before `Status: Complete`) instead of per-file write-approval prompts.
4. **Honest `NOT ASSESSED` ranking:** Verdict precedence is `FAIL / BLOCKED > NOT ASSESSED > PASS`. Missing artifacts, skipped modes, or unexecuted verification never collapse silently into `PASS`.
5. **Read-only reviewer sandboxes:** `scout`, `creative-director`, `technical-director`, `qa-lead`, and `code-reviewer` enforce `sandbox_mode: read-only`.
6. **Zero harness leakage:** Zero legacy tool names or host-specific tokens (no host-only file/search tool names, legacy prompt tools, legacy shell config helpers, legacy agent directory paths, legacy skill prefixes, or per-file write-approval prompts).
