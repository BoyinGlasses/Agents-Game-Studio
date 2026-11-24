---
paths:
  - "src/ui/**"
  - "Assets/Scripts/UI/**"
  - "Source/*/UI/**"
---

# UI Code Rules

- UI must **never** own or directly mutate gameplay state — display read-only state/view models and dispatch commands/signals/events to request actions.
- Route all player-facing text through the localization system (no hardcoded user-facing strings).
- Support keyboard/mouse AND gamepad focus/navigation (plus touch when configured) on every interactive screen.
- Make UI animations skippable and respect reduced-motion and accessibility preferences (`design/accessibility-requirements.md`).
- Trigger UI feedback sounds through the audio event bus/system rather than loading clips directly in view logic.
- Keep UI layout, binding, and asset loads off blocking game-thread hot paths.
- Support scalable fonts/HUD and colorblind-safe visual cues (never communicate state by color alone).
- Test every screen across minimum and maximum supported aspect ratios and resolutions (`production/qa/evidence/`).
