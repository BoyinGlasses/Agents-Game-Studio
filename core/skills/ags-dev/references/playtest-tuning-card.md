# Playtest & Game Feel Tuning Card

Required deliverable during `ags-dev` for every **`Player-facing`** and **`Mixed`** story (and optional for `Technical` stories with developer-facing tooling feel). Provides the game maker with a direct launch path, exposed data-driven knobs, and clear feel questions for Checkpoint #2 in `ags-verify`.

## Card Template

Include this block in the `ags-dev` summary and save alongside visual evidence (`production/qa/evidence/[story-slug]-tuning.md` when persistent record is useful, or inline in the handoff report):

```markdown
## Playtest & Game Feel Tuning Card: [Story Title]
- **Story**: `[story-path]`
- **Handoff Class**: [Player-facing | Mixed]
- **Direct Launch Target**: `[commands.run / --scene / MapURL command to land straight on the feature]`
- **Debug Setup Args / State**: `[e.g., --gold=500 or spawn room / dev hotkey; None if default]`

### Exposed Tuning Knobs (Data-Driven — No Magic Numbers)
| Parameter | Data File / Asset | Current Value | Suggested Tuning Range | Feel Effect |
|---|---|---|---|---|
| [e.g. jump_buffer_ms] | `[data/player_movement.tres]` | `120 ms` | `80–160 ms` | Forgiveness on early jump press before landing |
| [e.g. hitstop_frames] | `[data/combat_feel.tres]` | `4 frames` | `2–6 frames` | Impact weight on heavy hit |

### Feel & Feedback Targets
- **Input / Responsiveness**: [Expected input delay, buffering, coyote time, cancel windows]
- **Telegraph & Clarity**: [Wind-up frames/duration, anticipation SFX/VFX, readable UI contrast]
- **Impact / Juice**: [Hitstop, knockback, camera impulse, particle/audio cues]
- **Appearance Observed (Screenshot)**: `production/qa/evidence/[story-slug]/[NN]-[what].png` — [what the still confirms: layout, clipping, visibility]
- **Feel Remaining for Play**: [timing, weight, rhythm, camera comfort — cannot be verified by a screenshot]

### Playtest Steps for Game Maker (`ags-verify` Checkpoint #2)
1. Launch `[direct command]`
2. Perform `[exact input sequence / scenario]`
3. Confirm:
   - [ ] Does `[core action]` feel crisp and predictable within `[target timing]`?
   - [ ] Are feedback cues (animation, SFX, VFX, HUD) clear without obscuring play?
   - [ ] Any tuning knob above that needs adjustment before acceptance?
```

## Rules
- **Reachable surface**: A feature hidden behind multiple menus must expose a direct scene/map launch or debug state argument so both screenshot capture and game-maker playtest take seconds.
- **Appearance vs Feel separation**: Never claim a retained screenshot verified responsiveness, timing, weight, or audio sync; list those explicitly under **Feel Remaining for Play**.
- **In-scope tuning tweaks**: If the game maker requests knob adjustments during Checkpoint #2 without changing acceptance criteria or scope, update the data asset within the same story and return updated evidence to `ags-verify`.
