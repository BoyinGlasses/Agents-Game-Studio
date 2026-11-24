> Gate definition, loaded by `ags-gate` for Polish -> Release ONLY.

# Gate: Polish -> Release

**Required Artifacts:**
- [ ] All milestone features implemented
- [ ] Content complete (all referenced levels, assets, dialogue exist)
- [ ] Player-facing strings externalized (zero hardcoded player-facing text in code root; `NOT ASSESSED` if code root unresolved)
- [ ] QA test plan exists (`production/qa/`)
- [ ] QA sign-off report exists (`ags-team` `qa` — `APPROVED` or `APPROVED WITH CONDITIONS`)
- [ ] All `Must Have` story test evidence present (`tests/` passes; `production/qa/evidence/` docs + retained screenshots signed off)
- [ ] Smoke check passes cleanly (`PASS`) on release candidate build *(build-health floor — NOT waived by `qa.level: minimal`)*
- [ ] Full regression suite passes with zero regressions (`ags-qa`)
- [ ] Balance data reviewed (`ags-design-review` balance-check mode)
- [ ] Release & launch readiness checked (`ags-release`)
- [ ] Store metadata prepared (if applicable) and changelog / patch notes drafted (`ags-release`)

**Quality Checks:**
- [ ] Full QA pass signed off by `qa-lead`
- [ ] All automated tests pass
- [ ] Performance targets met across all target platforms (`performance.enforce: block` -> `FAIL` regardless of workflow tier)
- [ ] Zero known critical, high, or medium-severity bugs
- [ ] Accessibility basics verified (remapping, text scaling where applicable)
- [ ] Localization verified for all target locales (`ags-localize`)
- [ ] Legal requirements met (EULA, privacy policy, age ratings if applicable)
- [ ] Release build compiles and packages cleanly

## Workflow Tier Reductions

Baseline above is **`full`**:
- **`full`** — all features + content complete + localization + QA sign-off + smoke (`PASS`) + zero critical bugs all required
- **`standard`** — content-complete audit + QA sign-off + localization -> recommended; **all features + smoke (`PASS`) + zero critical bugs** required
- **`minimal`** — only **smoke check + zero critical bugs** required; everything else **drops** (excluding `performance.enforce`, which remains active at every tier)
