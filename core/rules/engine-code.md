---
paths:
  - "src/core/**"
  - "Assets/Scripts/Core/**"
  - "Source/*/Core/**"
---

# Engine & Core Code Rules

- **Zero allocations in hot paths** (frame ticks, `_physics_process`, `Update`/`FixedUpdate`, `Tick`, rendering/audio callbacks) — pre-allocate pools, caches, and scratch buffers.
- Document thread-safety guarantees explicitly (thread-safe vs main-thread/game-thread only).
- Record measured before/after profiler metrics whenever optimizing core systems.
- **Strict dependency direction**: `engine/core <- gameplay` (core systems must never import or depend on gameplay modules).
- Document public core APIs with concise doc comments and usage examples; deprecate breaking interface changes with migration notes.
- Use deterministic cleanup / RAII (`queue_free` + signal disconnect on `tree_exited`, `IDisposable` / `OnDestroy`, `EndPlay` / smart pointers) and degrade gracefully on missing optional assets.
- Verify engine APIs against `docs/engine-reference/<engine>/VERSION.md` and `deprecated-apis.md` before writing engine code.

## Engine-Idiomatic Hot-Path Example (Godot / Unity / Unreal)

```gdscript
# Godot: reuse pre-allocated array instead of allocating inside _physics_process
var _nearby_cache: Array[Node3D] = []

func _physics_process(_delta: float) -> void:
    _nearby_cache.clear()
    _spatial_grid.query_radius(global_position, query_radius, _nearby_cache)
```

```csharp
// Unity: reuse pre-allocated buffer (NonAlloc / Span / NativeArray), avoid Find/GetComponent in Update
private readonly Collider[] _hitCache = new Collider[32];

private void FixedUpdate()
{
    int count = Physics.OverlapSphereNonAlloc(transform.position, _radius, _hitCache, _mask);
    for (int i = 0; i < count; i++) { /* process _hitCache[i] */ }
}
```
