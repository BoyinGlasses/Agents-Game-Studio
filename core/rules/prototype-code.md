---
paths:
  - "prototypes/**"
---

# Prototype Code Rules (Relaxed)

Prototypes are throwaway builds for validating mechanics or technical feasibility quickly. Standards are intentionally relaxed to maximize learning speed.

## Allowed in `prototypes/`
- Hardcoded tuning values and inline data
- Minimal or omitted doc comments
- Simple, direct architecture (no forced abstractions, interfaces, or DI)
- Singletons and quick global state for fast wiring
- Copy-pasted logic, debug prints, and placeholder art/audio

## Required in `prototypes/`
- Isolate every prototype in its own directory: `prototypes/[name]-concept/`, `prototypes/[name]-vertical-slice/`, or `prototypes/[name]-spike-[date]/`.
- Maintain a `README.md` (and `REPORT.md` / `SPIKE-NOTE.md` on completion) documenting: hypothesis tested, how to run, status (`in-progress` / `concluded`), and evidence findings.
- Start prototype source files with `// PROTOTYPE - NOT FOR PRODUCTION` (or `// VERTICAL SLICE - NOT FOR PRODUCTION`).
- Never import `prototypes/` from production code (`src/`, `Assets/`, `Source/`) and never modify production files from a prototype.

## Graduation & Cleanup
- When a prototype succeeds, rewrite the production system cleanly from scratch under production standards (`ags-gdd` / `ags-architect` / `ags-dev`) — never graduate throwaway code directly into production.
- Preserve `README.md` / `REPORT.md` learnings and archive or delete stale prototype code once findings are captured.
