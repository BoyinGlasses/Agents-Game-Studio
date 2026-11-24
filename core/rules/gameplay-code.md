---
paths:
  - "src/gameplay/**"
  - "Assets/Scripts/Gameplay/**"
  - "Source/*/Gameplay/**"
---

# Gameplay Code Rules (Game-Native Rubric)

- **Data-driven tuning**: Load combat, movement, economy, and cooldown numbers from external data (`assets/data/`, Godot `Resource`/`.tres`, Unity `ScriptableObject`, Unreal `UDataAsset`/`UDataTable`) — never hardcode balance constants.
- **Frame-rate independence**: Multiply continuous motion, timers, and decay by `delta` / `Time.deltaTime` / `DeltaTime` (or execute deterministically in fixed physics steps).
- **Decoupled UI**: Gameplay systems never own or directly call UI widgets — emit signals, C# events, or Unreal delegates so presentation reacts cleanly.
- **Engine-idiomatic composition over Java-style dogma**:
  - Do NOT force artificial `IXyzService` interfaces, DI containers, or arbitrary 40-line / cyclomatic-10 method splits when engine idioms are cleaner.
  - **Godot**: Compose behaviors via child `Node` components, typed `signal`s, and `Resource` definitions; reserve Autoloads strictly for narrow global services (EventBus, Audio, Save), never global mutable gameplay dumps.
  - **Unity**: Compose via `MonoBehaviour` components, `ScriptableObject` event/data assets, or DOTS/Burst jobs; avoid `FindObjectOfType`/`GetComponent` in `Update()`.
  - **Unreal**: Compose via `UActorComponent`, `UGameInstanceSubsystem`/`UWorldSubsystem`, or GAS (`UAbilitySystemComponent`, `UGameplayAbility`, `UAttributeSet`); keep `.generated.h` as the final `#include`.
- **Explicit state machines & testability**: Define explicit transition rules/tables and keep pure gameplay math/rules separable from rendering so automated unit tests run headlessly.
- **Traceability**: Note the governing GDD or ADR (`ADR-NNN`) at the top of system entrypoints.

## Multi-Engine Examples

```gdscript
# Godot: Resource-backed tuning + signal decoupling + delta independence
@export var stats: CombatStats
signal damage_applied(amount: float)

func apply_cooldown(delta: float) -> void:
    _cooldown_remaining = maxf(0.0, _cooldown_remaining - delta)
```

```csharp
// Unity: ScriptableObject config + event decoupling
[SerializeField] private CombatConfig _config;
public event Action<float> DamageApplied;
```

```cpp
// Unreal: UDataAsset config + Subsystem/Component delegation (never raw global state)
UPROPERTY(EditDefaultsOnly, Category = "Combat")
TObjectPtr<UCombatConfigData> CombatConfig;
```
