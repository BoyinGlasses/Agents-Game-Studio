---
paths:
  - "src/networking/**"
  - "Assets/Scripts/Networking/**"
  - "Source/*/Networking/**"
---

# Network Code Rules

- Keep the server **authoritative** for all gameplay-critical state (health, damage, inventory, currency, position, win conditions) — never trust client assertions.
- Version network message schemas and RPC payloads for forward/backward compatibility.
- Use client-side prediction where responsiveness requires it, paired with server reconciliation/rollback for mispredictions.
- Handle disconnection, reconnection, timeouts, and host migration cleanly without corrupting session state.
- Rate-limit network diagnostic logging to prevent log-flood DoS.
- Declare replication strategy explicitly for every networked property/RPC: reliable vs unreliable, update frequency, relevancy, and interpolation/extrapolation.
- Define and monitor per-message bandwidth budgets against target player counts.
- Validate all incoming packet sizes, array lengths, string lengths, and numeric bounds before applying state changes.
