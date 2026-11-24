# Numeric & Economy Balance Check (`ags-design-review`)

Identifies balance outliers, dominant strategies, broken curves, and economic imbalances across GDD formulas and `assets/data/` files.

## Insufficient-Input Gate (Run Before Reporting)

1. List inputs (`assets/data/`, `design/balance/`, `design/registry/entities.yaml`, target GDD in `design/gdd/`).
2. Record `FOUND` or `ABSENT` per input.
3. Any section missing its required inputs MUST be reported **`NOT ASSESSED — NO DATA`** (never guess or fabricate numbers). If ALL inputs are `ABSENT`, emit overall **`NOT ASSESSED — NO DATA`** naming missing artifacts and producing skills (`ags-gdd design-system`, `assets/data/`).

## Phase 1-4: Domain, Data, Design Baseline & Checks

1. **Domain**: `Combat` | `Economy` | `Progression` | `Loot` | `<file-path>` (prompt user if omitted).
2. **Read Data**: Load relevant `assets/data/` and `design/balance/` files (list all in `Data Sources Analyzed`).
3. **Read Design Targets (Registry First)**: Read `design/registry/entities.yaml` (`constants:` and `formulas:` sections) if populated for authoritative targets, then read target GDD in `design/gdd/` for tuning knobs and missing details.
4. **Domain Checks**:
   - **Combat**: Weapon/ability DPS per power tier, time-to-kill per tier, strictly dominant options, unkillable defensive loops, damage-type/resistance balance.
   - **Economy**: Resource faucets/sinks & flow rates, accumulation curves over time, infinite resource loops, gold sink scaling vs income, dead/never-worth items.
   - **Progression**: XP & power curves, dead zones, sudden power spikes, content gate vs expected power alignment, skip/grind exploit resistance.
   - **Loot**: Expected acquisition time per rarity tier, pity-timer math, strictly obsolete loot, inventory pressure vs drop rate.

## Phase 5 & Phase 6: Report & Fix-Verify Cycle

1. Output structured analysis (`Data Sources Analyzed`, `Health Summary: NOT ASSESSED / HEALTHY / CONCERNS / CRITICAL ISSUES`, `Outliers Detected`, `Degenerate Strategies Found`, `Progression Analysis`, `Recommendations`, `Values That Need Attention`).
2. Prompt next action:
   - `[A]` Fix highest-priority issue in `assets/data/` or `design/balance/` and re-verify (if fix modifies a GDD/ADR tuning knob, remind user to run `ags-design-review propagate [gdd-path]`).
   - `[B]` Save report to `design/balance/balance-check-[system]-[YYYY-MM-DD].md`.
   - `[C]` Stop for manual review.
