# Godot Language Configuration Reference

Lookup tables for Godot setups in `ags-settings engine`. Read ONLY when the selected engine is Godot, and apply the block matching the chosen language (`GDScript`, `C#`, or `Both`).

## A1. `AGENTS.md` Technology Stack Templates

**GDScript:**
```markdown
- **Engine**: Godot [version]
- **Language**: GDScript
- **Build System**: SCons (engine), Godot Export Templates
- **Asset Pipeline**: Godot Import System + custom resource pipeline
```
*(Write Language as exactly `GDScript` — never append `"C++ via GDExtension"` here.)*

**C#:**
```markdown
- **Engine**: Godot [version]
- **Language**: C# (.NET 8+, primary), C++ via GDExtension (native plugins only)
- **Build System**: .NET SDK + Godot Export Templates
- **Asset Pipeline**: Godot Import System + custom resource pipeline
```

**Both — GDScript + C#:**
```markdown
- **Engine**: Godot [version]
- **Language**: GDScript (gameplay/UI scripting), C# (performance-critical systems), C++ via GDExtension (native only)
- **Build System**: .NET SDK + Godot Export Templates
- **Asset Pipeline**: Godot Import System + custom resource pipeline
```

## A2. Naming Conventions

*(Must match the `naming` block written to `project.yaml` value-for-value so `check coherence` and downstream checks agree.)*

**GDScript:**
- Classes: `PascalCase` (`PlayerController`)
- Variables / functions: `snake_case` (`move_speed`)
- Signals: `snake_case` past tense (`health_changed`)
- Files: `snake_case` matching class (`player_controller.gd`)
- Scenes: `snake_case` matching file (`player_controller.tscn`)
- Constants: `SCREAMING_SNAKE` (`MAX_HEALTH`)

**C#:**
- Classes: `PascalCase` (`PlayerController`), marked `partial` for Godot nodes
- Public properties/fields: `PascalCase` (`MoveSpeed`); private fields: `_camelCase` (`_currentHealth`)
- Methods: `PascalCase` (`TakeDamage()`)
- Signal delegates: `PascalCase` + `EventHandler` suffix (`HealthChangedEventHandler`)
- Files & Scenes: `PascalCase` matching root class (`PlayerController.cs`, `PlayerController.tscn`)
- Constants: `PascalCase` (`MaxHealth`)

**Both — GDScript + C#:**
Apply GDScript rules to `.gd` files and C# rules to `.cs` files (per-file boundary; never mix inside one file). In `project.yaml`, `naming` uses the GDScript column.

## A3. Engine Specialists Routing

**GDScript:**
- `code`: `godot-gdscript-specialist` (`.gd`)
- `shader`: `godot-shader-specialist` (`.gdshader`, `VisualShader`)
- `ui`: `godot-specialist` (Control nodes, CanvasLayer, `.tscn`, `.tres`, architecture)
- `additional`: `["godot-gdextension-specialist"]` (native C++/Rust extensions)

**C#:**
- `code`: `godot-csharp-specialist` (`.cs`, `.csproj`, NuGet, `[Signal]`, `[Export]`)
- `shader`: `godot-shader-specialist` (`.gdshader`, `VisualShader`)
- `ui`: `godot-specialist` (Control nodes, CanvasLayer, `.tscn`, `.tres`, architecture)
- `additional`: `["godot-gdextension-specialist"]`

**Both — GDScript + C#:**
- `code`: `godot-gdscript-specialist` (`.gd`), with `godot-csharp-specialist` in `additional` (`.cs`, `.csproj`)
- `shader`: `godot-shader-specialist`
- `ui`: `godot-specialist` (also mediates cross-language boundary — prefer signals over direct cross-language method calls)
- `additional`: `["godot-csharp-specialist", "godot-gdextension-specialist"]`
