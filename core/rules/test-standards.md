---
paths:
  - "tests/**"
  - "Assets/Tests/**"
  - "Source/*/Tests/**"
---

# Test Standards

- File naming: `[system]_[feature]_test.[ext]` (or engine test suite convention like `[System]Tests.cs` / `[System]Test.cpp`).
- Function naming: `test_[system]_[scenario]_[expected_result]`.
- Structure every unit/integration test cleanly as **Arrange / Act / Assert**.
- Keep unit tests deterministic and fast: no network, random unseeded values, wall-clock flakiness, or external state; clean up integration test temp files/scenes.
- Performance tests must declare explicit numeric thresholds and fail if exceeded.
- **Watch regression tests fail first**: run any new bug-fix regression test against the unfixed code to confirm it catches the bug before applying the fix and trusting the pass (see `.ags/rules/skill-authoring.md`).

## Multi-Engine Examples

```gdscript
# Godot (GdUnit4)
func test_health_system_take_damage_reduces_health() -> void:
    var health := HealthComponent.new()
    health.max_health = 100
    health.current_health = 100
    health.take_damage(25)
    assert_eq(health.current_health, 75)
```

```csharp
// Unity (NUnit)
[Test]
public void HealthSystem_TakeDamage_ReducesHealth()
{
    var health = new HealthModel(maxHealth: 100);
    health.TakeDamage(25);
    Assert.AreEqual(75, health.CurrentHealth);
}
```

```cpp
// Unreal Automation
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHealthDamageTest, "Game.Combat.HealthReducesOnDamage", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FHealthDamageTest::RunTest(const FString& Parameters)
{
    FHealthState Health(100);
    Health.ApplyDamage(25);
    TestEqual(TEXT("Health reduced"), Health.Current, 75);
    return true;
}
```
