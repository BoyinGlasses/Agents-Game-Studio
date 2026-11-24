> Gate definition, loaded by `ags-gate` for Production -> Polish ONLY.

# Gate: Production -> Polish

**Required Artifacts:**
- [ ] Resolved code root has active code organized into subsystems
- [ ] All core mechanics from GDD are implemented (cross-reference `design/gdd/` with code root)
- [ ] Main gameplay path is playable end-to-end
- [ ] Test files exist in `tests/unit/` and `tests/integration/` covering Logic and Integration stories
- [ ] All Logic stories from sprint have corresponding unit test files in `tests/unit/`
- [ ] Smoke check run with `PASS` or `PASS WITH WARNINGS` report in `production/qa/smoke-*.md` *(build-health floor — NOT waived by `qa.level: minimal`)*
- [ ] At least one QA plan in `production/qa/` (`ags-qa`) — advisory (`CONCERNS` if missing)
- [ ] QA sign-off report in `production/qa/` (`ags-team` `qa` playbook) with `APPROVED` or `APPROVED WITH CONDITIONS`
- [ ] At least 3 distinct playtest sessions in `production/qa/playtests/` covering new player experience, mid-game systems, and difficulty curve
- [ ] Fun hypothesis from Game Concept explicitly validated or revised

**Quality Checks:**
- [ ] Automated test suite passes (`testing.strict.logic`/`.integration` control Blocker vs Concern; unconfigured runner when tier requires tests = `NOT ASSESSED`)
- [ ] Zero critical/blocker bugs open
- [ ] Core loop matches GDD acceptance criteria
- [ ] Performance within budget (`performance.enforce`: `warn` -> `CONCERNS`, `block` -> `FAIL`, `off` -> informational; runs at EVERY workflow tier)
- [ ] Critical fun issues from playtests addressed; zero >50%-tester confusion loops
- [ ] Difficulty curve matches `design/difficulty-curve.md` (if present; note hand-authored from `.ags/templates/difficulty-curve.md` if absent)
- [ ] All implemented screens have UX specs, updated `design/ux/interaction-patterns.md`, and verified `design/accessibility-requirements.md` tier compliance

## Workflow Tier Reductions

Baseline above is **`full`**:
- **`full`** — core mechanics + Logic/Integration tests + smoke check + QA sign-off + 3+ playtests all required
- **`standard`** — QA sign-off + per-story test coverage -> recommended; **core mechanics + smoke check + playable end-to-end + 1+ documented playtest + zero critical/blocker bugs** required
- **`minimal`** — **smoke check + playable end-to-end + zero critical/blocker bugs** required; core-mechanics cross-check -> recommended; everything else **drops** (excluding `performance.enforce`, which stays active at every tier, and the smoke check, which is never waived by `qa.level: minimal`)
