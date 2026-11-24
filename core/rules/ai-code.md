---
paths:
  - "src/ai/**"
  - "Assets/Scripts/AI/**"
  - "Source/*/AI/**"
---

# AI Code Rules

- Keep AI decision/tick updates within frame budget (default <=2 ms per frame unless `project.yaml` sets another budget) — profile to verify.
- Store tunable AI parameters (perception ranges, weights, reaction timers, cooldowns) in external data files (`assets/data/`, `.tres`, `ScriptableObject`, `DataTable`), never hardcoded.
- Build debug visualization hooks for AI state (paths, perception cones, active behavior/utility scores, target selection).
- Telegraph enemy intentions clearly before commitment frames so players can read and react.
- Prefer behavior trees, utility scorers, hierarchical state machines, or Unreal EQS/StateTree over sprawling nested `if/else` chains.
- Support group AI coordination (formations, flanking, token/slot assignment) from data.
- Log AI state transitions behind a debug toggle for diagnosis without spamming release logs.
- Never trust AI-related state or action triggers sent by clients in multiplayer — validate server-side.
