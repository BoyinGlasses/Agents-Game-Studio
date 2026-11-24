# AGS v2 Skill & Agent Eval Framework — Agent Instructions

This directory (`tests/eval/`) is the behavioral and rubric evaluation suite for the
Agents Game Studio (AGS v2) framework repository. It is NOT copied into generated game projects.

## Key files

| File | Purpose |
|---|---|
| `catalog.yaml` | Registry mapping the 21 `ags-*` skills, their consolidated legacy behavioral specs, and all core/engine/lens role specs. |
| `quality-rubric.md` | AGS v2 pass/fail metrics (`core-structural`, `story-harness`, `gate`, `review`, `authoring`, `pipeline`, `analysis`, `team`, `sprint`, `utility`, and agent roles). |
| `skills/<category>/<name>.md` | Behavioral test specs + protocol assertions. |
| `agents/<tier>/<name>.md` | Behavioral test specs for core, engine, and lens roles. |
| `templates/skill-test-spec.md` | Template for authoring new skill test specs. |
| `templates/agent-test-spec.md` | Template for authoring new role test specs. |

## Running Evaluations

1. Static structural and parity checks run deterministically via `python -m unittest discover -s tests -v` (notably `tests/test_cohesion.py`) and `python -m ags.build --check`.
2. Behavioral / rubric checks run via `ags-skill-ops` (`static`, `spec`, `category`, `audit`, `improve`):
   - Inspect `catalog.yaml` to locate the target skill (`core/skills/ags-<name>/SKILL.md`) and its mapped specs.
   - Read the matching `###` section in `quality-rubric.md`.
   - Score every case independently using `FAIL / BLOCKED > NOT ASSESSED > PASS` — never mark an unverified case `PASS`.
