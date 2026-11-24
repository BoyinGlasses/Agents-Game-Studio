---
paths:
  - "assets/shaders/**"
  - "Assets/Shaders/**"
  - "Shaders/**"
---

# Shader Code Rules

## Naming & Organization
- Follow `[type]_[category]_[name].[ext]`:
  - Godot: `spatial_env_water.gdshader`, `canvas_ui_flash.gdshader`
  - Unity: `SG_Env_Water` (Shader Graph), `HLSL` custom passes under `Assets/Shaders/`
  - Unreal: `M_Env_Water` / `MI_Env_Water` / custom `.usf`/`.ush` under `Shaders/`
- Prefix shader purpose clearly: `spatial_`, `canvas_`, `particles_`, `post_`.
- Include an authorship/purpose header, target render pipeline (Godot Forward+/Mobile/Compatibility, Unity URP/HDRP, Unreal SM5/SM6), and do not mix incompatible render pipelines in one directory.

## Quality, Performance & Variants
- Use descriptive uniform/parameter names with inspector hints and grouping (`group_uniforms`, `[Header]`, Unreal `Category`).
- Replace magic numbers with named constants or uniforms; comment non-obvious math.
- Document target platform complexity budgets; use `half`/`mediump` precision where full float32 precision is unnecessary.
- Minimize fragment texture samples; avoid dynamic branching where `step()`, `mix()`, and `smoothstep()` suffice; never sample textures inside dynamic loops; use two-pass separable blurs.
- Test on minimum-spec hardware with simplified quality-tier fallbacks and actively track/strip shader variants.
