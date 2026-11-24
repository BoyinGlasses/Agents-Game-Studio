# Security Audit (`ags-diagnose security`)

Audits save files/serialization, multiplayer networking, input validation, data exposure, anti-tamper surfaces, and third-party dependencies with strict engine-reference provenance and anti-silent-skip rules.

**Output:** `production/security/security-audit-[date].md`

---

## Phase 1: Parse Arguments, Engine, Code Root & Multiplayer Scope

**Modes:** `full` (default before release), `network`, `save`, `input`, `quick` (high-severity checks only).

Resolve from `python .ags/cli.py preflight ags-diagnose security` (`project.yaml` plus any legacy technical-preferences fallback):
1. **`engine.name` and `engine.language`**: Load-bearing for Phase 3. If absent or empty, state it in the report and mark every grep-based category **`NOT ASSESSED`** — never fall back to Godot pattern lists.
2. **Code root**: Resolve `src/` (Godot), `Assets/` (Unity), or `Source/<Module>/` (Unreal). If unresolved, emit **`NOT ASSESSED — code root unresolved`** and do not run zero-hit scans against `src/`.
3. **`platform.targets`**: Scopes attack surfaces.
4. **`platform.multiplayer` and `platform.online` — ABSENT DOES NOT MEAN `false`**:
   - Setup skills do not automatically populate a `platform:` block, so both keys are commonly absent.
   - **Never assume single-player or skip Category 2 when absent/empty.** Ask the user whether the game has multiplayer or online features (they can persist it via `ags-settings platform.multiplayer=true|false`).
   - If you cannot ask or multiplayer scope remains unconfirmed, **run Category 2 anyway** and mark it **`NOT ASSESSED — multiplayer scope unconfirmed (platform.multiplayer unset)`**, making `CLEAR TO SHIP` unreachable.

---

## Phase 2: Delegate to `code-reviewer` (`security-engineer` Lens)

Delegate to `code-reviewer` applying `.ags/roles/security-engineer.md` (or perform directly using `.ags/roles/security-engineer.md` if delegation is unavailable), passing audit mode, resolved `engine.name`/`engine.language`, and manifest of resolved code root, `assets/data/`, and config files.

---

## Phase 3: Audit Categories & Pinned Engine Reference Matrix

**Verify every API list below against `docs/engine-reference/<engine>/` before scanning and extend it with any version-pinned APIs documented there.** Do not invent engine APIs from memory.

| Category | Godot | Unity | Unreal |
|---|---|---|---|
| **1 — Save / Serialization** | Floor list below (verify `FileAccess` vs 3.x `File.open` against `docs/engine-reference/godot/`) | **`NOT SOURCEABLE`** | **`NOT SOURCEABLE`** |
| **2 — Network / Multiplayer** | Floor list below (`docs/engine-reference/godot/modules/networking.md`) | `ServerRpc`, `ClientRpc`, `NetworkVariable`, `NetworkObject`, `NetworkManager`, `NetworkBehaviour`, `IsServer`, `IsOwner` | `UFUNCTION`, `Server`, `Client`, `NetMulticast`, `Replicated`, `DOREPLIFETIME`, `GetLifetimeReplicatedProps`, `HasAuthority` |
| **3 — Input Validation** | Floor list below (`docs/engine-reference/godot/modules/input.md`) | `InputSystem`, `PlayerInput`, `ReadValue`, `InputValue` | `EnhancedInput`, `UInputAction`, `InputMappingContext`, `BindAction`, `FInputActionValue` |
| **4 — Data Exposure** | Engine-agnostic (applies to all engines) | Engine-agnostic | Engine-agnostic |
| **5, 6 — Anti-Tamper & Supply Chain** | Manifest & architecture inspection | Manifest & architecture inspection | Manifest & architecture inspection |

> **`NOT SOURCEABLE` forces `NOT ASSESSED`:** `docs/engine-reference/unity/` and `docs/engine-reference/unreal/` do not include a save/serialization module. Never write Unity/Unreal serialization patterns from training data. Record **`NOT ASSESSED — Category 1 Save/Serialization has no sourced pattern set for <engine>`**; `CLEAR TO SHIP` is unreachable until a sourced module exists in `docs/engine-reference/<engine>/`.

### Category Details
1. **Save File & Serialization Security**:
   - Check blind deserialization, path traversal from user strings, checksum/HMAC integrity, numeric bounds validation on load, and `eval`/dynamic code calls near loads.
   - Godot floor patterns: `FileAccess`, `File.open`, `open(`, `load`, `deserialize`, `parse`, `parse_string`, `from_json`, `read_file`, `get_var`, `bytes_to_var`. Confirm version-appropriate names against `docs/engine-reference/godot/` — a zero-hit scan using only deprecated 3.x names on Godot 4 is invalid; if pinned version APIs cannot be confirmed, record `NOT ASSESSED`.
2. **Network & Multiplayer Security** *(skip ONLY when `platform.multiplayer` is explicitly confirmed `false`)*:
   - Check server authority, packet size/type/range checks, server-side position/state validation, rate limiting, token encryption, and debug endpoints in release builds.
   - Godot floor patterns: `recv`, `receive`, `PacketPeer`, `socket`, `MultiplayerPeer` (matches both 3.x `NetworkedMultiplayerPeer` and 4.x `ENetMultiplayerPeer`), `ENetMultiplayerPeer`, `NetworkedMultiplayerPeer`, `rpc`, `rpc_id`, `@rpc`.
3. **Input Validation**:
   - Check player strings in file paths, log injection, numeric/stat bounds, and backend stat/achievement validation.
   - Godot floor patterns: `get_input`, `Input.get_`, `input_map`, user-facing text fields.
4. **Data Exposure** *(all engines)*:
   - Search for `api_key`, `secret`, `password`, `token`, `private_key`, `DEBUG`, `print(` in release-facing code; verify no embedded secrets, verbose error leaks, sensitive logs, or internal paths.
5. **Cheat & Anti-Tamper Vectors**:
   - Check plain editable progression/economy files, client-trusted DLC/entitlement checks, memory-edit exposure in competitive multiplayer, and server-side leaderboard validation.
6. **Dependency & Supply Chain**:
   - Scan `addons/`, `plugins/`, `third_party/`, `vendor/` and inventory plugin name, version, verified source, and known CVEs.

---

## Phase 4 & 5: Severity Classification & Report

| Severity | Definition |
|---|---|
| **CRITICAL** | RCE, data breach, or trivial multiplayer-breaking cheat *(any `HIGH` finding in multiplayer scope escalates to `CRITICAL`)* |
| **HIGH** | Save tampering bypassing progression, credential leak, or server-authority bypass |
| **MEDIUM** | Client-side cheat enablement, info disclosure, or bounded input-validation gap |
| **LOW** | Defense-in-depth hardening with no direct exploit |

Status per finding: `Open` / `Accepted Risk` / `Out of Scope`.

Generate `production/security/security-audit-[date].md` (`Executive Summary`, `Release recommendation`, `CRITICAL`/`HIGH`/`MEDIUM`/`LOW` findings with `SEC-NNN`, `Accepted Risk`, `Dependency Inventory`, `Remediation Priority Order`, `Re-Audit Trigger`).

**Release Recommendation Precedence:**
1. **`DO NOT SHIP` / `FIX CRITICALS FIRST`**: Any open `CRITICAL` or `HIGH` finding.
2. **`NOT ASSESSED`** *(strictly outranks `CLEAR TO SHIP`)*: Insufficient implemented surface (e.g., trivial/empty source tree), missing `engine.name`, unresolved code root, unconfirmed version-pinned APIs, any `NOT SOURCEABLE` category for `<engine>`, or unconfirmed `platform.multiplayer`. Name every missing input/category and the skill that supplies it.
3. **`CLEAR TO SHIP`**: All applicable categories assessed with zero open `CRITICAL`/`HIGH` items and zero `NOT ASSESSED` categories.

---

## Phase 6 & 7: Write & Gate Integration

Present executive summary + `CRITICAL`/`HIGH` findings in conversation, then confirm writing `production/security/security-audit-[date].md` per `modes.automation`.
- This report is required for `ags-gate` (`release` stage).
- Never treat an accepted risk on `LOW` findings without explicit documentation; never present this static audit as a substitute for a professional human penetration test on competitive or monetized multiplayer launches.
- Re-run `ags-diagnose security quick` after remediating `CRITICAL`/`HIGH` items before `ags-gate release` and `ags-release launch-checklist`.
