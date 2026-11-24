# Asset Compliance Audit (`ags-art-ux`) — Read-Only

Audits `assets/` against art bible / `project.yaml` naming conventions, file size budgets, texture/audio format standards, orphaned assets, and missing references. Never modifies files.

## Mandatory Measurement & Insufficient-Input Gates

1. **Shell measurement requirement**: File sizes, texture dimensions (power-of-two), audio sample rates, and modification timestamps require shell execution (`stat`, binary header inspection). If any metric cannot be measured, write **`NOT ASSESSED`** in that cell — NEVER estimate or guess.
2. **Insufficient-Input Gate (check BEFORE producing report)**:
   - Record `FOUND` or `ABSENT` for standards (`design/art/art-bible.md`, `project.yaml` naming/performance), each asset directory (`assets/{art,audio,vfx,shaders,data}/`), and code root (`src/` / `Assets/` / `Source/`).
   - If any required input for a section is `ABSENT`, mark that section **`NOT ASSESSED — NO DATA`**.
   - If **every** required input is `ABSENT`, stop and emit whole verdict **`NOT ASSESSED — NO DATA`**, naming the missing inputs and producing skills (`ags-art-ux art-bible`, `ags-settings`). Never report clean `COMPLIANT` on empty or unmeasured inputs.

## Audit Workflow

1. **Read Standards**: Load `design/art/art-bible.md` (§8 Asset Standards) and `naming.*` / `performance.*` from `project.yaml` (else legacy `technical-preferences.md`).
2. **Scan Asset Directories**: List files under `assets/art/**/*`, `assets/audio/**/*`, `assets/vfx/**/*`, `assets/shaders/**/*`, `assets/data/**/*`.
3. **Run Compliance Checks**:
   - **Naming**: Art `[category]_[name]_[variant]_[size].[ext]`, Audio `[category]_[context]_[name]_[variant].[ext]`, strictly lowercase with underscores.
   - **File standards**: Textures power-of-two + expected format (PNG for UI, compressed for 3D) + within size budget; Audio sample rate + OGG (SFX) / OGG or MP3 (music) + duration limits; Data valid JSON/YAML matching schema.
   - **Orphaned assets**: Search resolved code root for references to each asset file; flag unreferenced assets with last-modified date and size. (If code root unresolved -> mark Orphaned/Missing sections `NOT ASSESSED — code root unresolved`.)
   - **Missing assets**: Search code root for asset references and verify files exist on disk.
4. **Output Read-Only Report**:
   - Header: `# Asset Audit Report -- [Category] -- [YYYY-MM-DD]`
   - Summary (`Total assets scanned`, violation/orphan/missing counts, `Overall health: NOT ASSESSED / CLEAN / MINOR ISSUES / NEEDS ATTENTION`)
   - Tables: `Naming Violations`, `Size Violations`, `Format Violations`, `Orphaned Assets`, `Missing Assets`, `Recommendations`
   - Final line: `## Verdict: [NOT ASSESSED / COMPLIANT / WARNINGS / NON-COMPLIANT]` (`NOT ASSESSED` outranks `COMPLIANT`, sits below `WARNINGS`/`NON-COMPLIANT`).
5. **Next steps**: Fix naming against `project.yaml` / art bible rules, review confirmed orphans before deletion, and run `ags-design-review content-audit`.
