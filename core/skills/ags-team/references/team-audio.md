# Team Playbook: Audio (`ags-team audio`)

Orchestrates audio direction, SFX/accessibility specification, engine audio architecture, and gameplay audio integration for a target feature or area.

## Argument & Context

- **Argument check**: Requires `[feature or area]` (e.g., `combat`, `main menu`, `forest biome`, `boss encounter`). If omitted, print usage (`ags-team audio <feature or area>`) and exit without spawning roles.
- **Gather context**:
  - Relevant design docs in `design/gdd/`
  - Sound bible at `design/gdd/sound-bible.md` (template reference: `.ags/templates/sound-bible.md`)
  - Existing audio asset lists in `assets/audio/`
  - Existing sound design docs for this area

## Active-Set & Role Mapping (`team.size`)

- **`individual`** (default): `tech-artist` (carrying `sound-designer` lens) only. Other roles consulted via `tech-artist`, not spawned separately.
- **`small`**: `tech-artist` + `audio-director` (`.ags/roles/audio-director.md`) + `sound-designer` (`.ags/roles/sound-designer.md`).
- **`studio`**: + `localization-lead` (`.ags/roles/localization-lead.md`) + per-system audio reviewers.
- Directors (`creative-director`, `technical-director`, `producer`) spawn only at phases ending in a user decision point when `modes.review_mode` allows (`full` or `PHASE-GATE` in `lean`).
- **Role map**:
  - `audio-director` lens -> `tech-artist` (`.ags/roles/audio-director.md`)
  - `sound-designer` lens -> `tech-artist` (`.ags/roles/sound-designer.md`)
  - `accessibility-specialist` lens -> `art-ux-director` (`.ags/roles/accessibility-specialist.md`)
  - `gameplay-coder` -> `.ags/roles/gameplay-coder.md`
  - Engine specialist -> `.ags/roles/<engine>-specialist.md`

Announce the active roster, unspawned roles routed through `tech-artist`, and engine validation status before Step 1.

## Pipeline

### Step 1: Audio Direction (`audio-director`)

Delegate to `audio-director` (or `tech-artist` at `individual`) to:
- Define the sonic identity for the feature or area.
- Specify emotional tone and audio palette.
- Set music direction (adaptive layers, stems, transitions).
- Define audio priorities and mix targets.
- Establish adaptive audio rules (combat intensity, exploration, tension).

### Step 2: Sound Design and Audio Accessibility (Parallel)

Issue both delegations simultaneously when active:

1. **`sound-designer`**:
   - Create detailed SFX specifications for every audio event.
   - Define sound categories (`ambient`, `UI`, `gameplay`, `music`, `dialogue`).
   - Specify per-sound parameters (volume range, pitch variation, attenuation).
   - Plan the audio event list with trigger conditions.
   - Define mixing groups and ducking rules.

2. **`accessibility-specialist`**:
   - Identify audio events carrying critical gameplay information (damage received, enemy nearby, objective complete) that require visual alternatives for hearing-impaired players.
   - Specify subtitle/caption requirements (which events need captions, text format, on-screen duration).
   - Verify no gameplay state is communicated by audio alone (visual fallback required for all).
   - Review the event list for auditory sensitivity risks (high-frequency alerts, sudden loud transients).
   - Output: audio accessibility requirements list integrated into the audio event spec.

### Step 3: Technical Implementation (Parallel)

Issue both delegations simultaneously when engine is configured:

1. **`tech-artist`**:
   - Design audio middleware integration (Wwise / FMOD / native).
   - Define audio bus structure and routing.
   - Specify memory budgets for audio assets per platform.
   - Plan streaming vs preloaded asset strategy.
   - Design any audio-reactive visual effects.

2. **`<engine>-specialist`** (derived from `engine.name` in `project.yaml`: Godot -> `godot-specialist`, Unity -> `unity-specialist`, Unreal -> `unreal-specialist`):
   - Validate whether proposed audio middleware integration is idiomatic (e.g., Godot `AudioStreamPlayer` vs FMOD, Unity Audio Mixer vs Wwise, Unreal MetaSounds vs FMOD) against `docs/engine-reference/<engine>/`.
   - Recommend idiomatic engine audio nodes/components.
   - Check `docs/engine-reference/<engine>/` for pinned engine-version audio breaking changes.
   - If `engine.name` is unset or `null`, skip this spawn and record:
     `Engine validation: NOT ASSESSED — no engine configured (engine.name unset in project.yaml)`

### Step 4: Code Integration (`gameplay-coder`)

Delegate to `gameplay-coder` to:
- Implement or review the audio manager system.
- Wire audio events to gameplay triggers.
- Implement adaptive music transitions if specified.
- Set up audio occlusion and reverb zones.
- Write unit/integration tests for audio event triggers.

### Step 5: Compile, Confirm, and Summarize

1. Working artifacts produced by delegated roles stay under `production/`.
2. Compile the unified audio design document from all outputs.
3. Because `design/` is outside the worker bounded-write zone, present the compiled document and obtain explicit user confirmation before writing `design/audio/audio-[feature].md` (creating `design/audio/` if absent).
4. Output summary: audio event count, estimated asset count, implementation tasks, open cross-role questions, active/skipped roster, and engine validation status.

## Verdicts & Next Steps

- **COMPLETE**: Audio design document compiled, approved, and saved (`Engine validation` assessed or explicitly recorded as `NOT ASSESSED` if no engine is configured).
- **NOT ASSESSED** (partial check): Engine validation or sound bible input absent — record explicitly in the summary.
- **BLOCKED**: Unresolved dependency (missing GDD, unaddressed critical accessibility gap, or unconfirmed ADR).
- **Common blockers & redirects**:
  - Missing GDD -> `ags-gdd`
  - Proposed ADR -> `ags-architect architecture-decision`
  - Oversized scope -> `ags-plan create-stories`
- **Next Skills**:
  - Review audio design with `audio-director` before implementation.
  - `ags-dev` to implement audio manager and trigger stories.
  - `ags-art-ux asset-audit` after audio asset creation to verify naming and format compliance.
