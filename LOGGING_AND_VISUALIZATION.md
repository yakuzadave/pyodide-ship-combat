# Battle Logging and Visualization

This document describes the battle logging and text-map visualization systems added to the Pyodide Ship Combat Simulator.

## Table of Contents

1. [Battle Logger](#battle-logger)
2. [Text-Map Visualization](#text-map-visualization)
3. [Integration](#integration)
4. [Usage Examples](#usage-examples)
5. [Export Formats](#export-formats)

---

## Battle Logger

The `BattleLogger` class provides comprehensive event tracking and statistics for battles.

### Features

- **Event Tracking**: Every action is logged with structured data
- **Round Summaries**: Aggregated statistics per round
- **Export Formats**: JSON and text file export
- **Statistics**: Accuracy, damage, critical hits, and more
- **Configurable Verbosity**: Choose between verbose console output or silent logging

### Event Types

The logger tracks the following event types:

| Phase | Event Type | Details Tracked |
|-------|-----------|-----------------|
| Orders | `order_selected` | Ship name, order chosen |
| Movement | `ship_moved` | Start/end position, distance, heading |
| Shooting | `hit`, `miss`, `critical_hit` | Attacker, target, weapon, damage |
| Missiles | `missile_hit` | Attacker, target, damage |
| Boarding | `boarding_success`, `boarding_failed` | Attacker, target, damage |
| Repairs | `system_repaired` | Ship, system, efficiency change |
| Shields | `shield_regenerated` | Ship, old/new shield values |
| Heat | `weapon_heated`, `weapon_overheated` | Ship, weapon, heat level |
| Critical | `system_damaged` | Ship, system, efficiency loss |
| Combat | `ship_destroyed` | Ship name, destroyed by |
| Hazards | Various hazard types | Ship, hazard effect |

### Statistics Tracked

**Per Round:**
- Total damage dealt
- Shots fired / hits / misses
- Accuracy percentage
- Critical hits
- Ships destroyed

**Overall Battle:**
- Total rounds
- Total events
- Cumulative damage
- Overall accuracy
- All ships destroyed
- Round-by-round breakdown

### Basic Usage

```python
from ship_combat.battle_logger import BattleLogger

# Create logger
logger = BattleLogger(verbose=True)  # Set False for silent logging

# Start a round
logger.start_round(1)

# Log events
logger.log_order("Aurora", "Lock On")
logger.log_movement("Aurora", 0.0, 0.0, 20.0, 10.0, 90.0)
logger.log_shot("Aurora", "Enemy", "Laser", hit=True, damage=15, critical=False)

# End round
logger.end_round()

# Get summary
summary = logger.get_summary()
print(f"Total Damage: {summary['total_damage_dealt']}")
print(f"Accuracy: {summary['overall_accuracy']:.1f}%")
```

### Event Structure

Each event is stored as a `BattleEvent`:

```python
@dataclass
class BattleEvent:
    round: int              # Round number
    phase: str              # Battle phase
    event_type: str         # Type of event
    ship_name: str          # Ship involved
    details: Dict[str, Any] # Event-specific details
    timestamp: str          # ISO timestamp
```

### Round Summary Structure

```python
@dataclass
class RoundSummary:
    round: int
    events: List[BattleEvent]
    ships_destroyed: List[str]
    total_damage_dealt: int
    total_shots_fired: int
    total_hits: int
    total_misses: int
    critical_hits: int

    def accuracy() -> float:
        # Returns hit percentage
```

---

## Text-Map Visualization

The `BattleMap` class provides ASCII text-based battlefield visualization.

### Features

- **Top-Down View**: 2D projection of 3D battlefield
- **Ship Symbols**: Numbers/letters for each ship
- **Heading Indicators**: Arrows showing ship direction
- **Grid Lines**: Optional coordinate grid
- **Range Circles**: Optional distance reference
- **Multiple Render Modes**: Full map, compact status, tactical overview
- **Configurable Scale**: Adjust zoom level

### Render Modes

#### 1. Full Map (`render()`)

ASCII grid showing ship positions with heading indicators.

```python
battle_map = BattleMap(width=60, height=30, scale=2.0)
print(battle_map.render(fleet_a, fleet_b, show_grid=True, show_range=False))
```

**Output:**
```
----+----+----+----+----+----+----+----+----+----+----+----
    |    |    |    |    |    |    |    |    |    |    |
    |    |    |    1→   |    |    |    |    |    |    |
    |    |    |    |    |    |    |    |    |    |    |
----+----+----+----+----+----+----+----+----+----+----+----
    |    |    |    |    |    |    |    a←   |    |    |
```

**Symbols:**
- `1`, `2`, `3...`: Fleet A ships
- `a`, `b`, `c...`: Fleet B ships
- `→↗↑↖←↙↓↘`: Heading indicators
- `~`: Evading ship
- `·`: Range circle
- `+|-`: Grid lines

#### 2. Compact Status (`render_compact()`)

Tabular view with coordinates and status.

```python
print(battle_map.render_compact(fleet_a, fleet_b))
```

**Output:**
```
BATTLEFIELD STATUS
------------------------------------------------------------

Fleet A:
  [1] Aurora Huntress       (10.0, 5.0, 0.0)         90°  H:80 S:65
  [2] Victory               (-5.0, 10.0, 2.0)        45°  H:100 S:70

Fleet B:
  [a] Enemy Cruiser         (15.0, -5.0, 0.0)       270°  H:75 S:50
  [b] Enemy Frigate         [DESTROYED]
------------------------------------------------------------
```

#### 3. Tactical Overview (`render_tactical()`)

Detailed tactical information.

```python
print(battle_map.render_tactical(fleet_a, fleet_b))
```

**Output:**
```
TACTICAL OVERVIEW
================================================================================
Fleet A: 2/2 active
Fleet B: 1/2 active

ENGAGEMENT DISTANCES:
  Aurora Huntress → Enemy Cruiser: 12.5 units [SHORT]
  Victory → Enemy Cruiser: 25.0 units [LONG]

ACTIVE ORDERS:
Fleet A:
  Aurora Huntress: Lock On
  Victory: Power to Weapons (W:60% S:20% E:20%)

Fleet B:
  Enemy Cruiser: Evasive Maneuvers

WEAPON HEAT STATUS:
Fleet A:
  Aurora Huntress - Laser: 60%
  Victory - Plasma Cannon: 85%
Fleet B:
  Enemy Cruiser - Macro Cannon: 100% [OVERHEATED]
================================================================================
```

### Map Configuration

```python
battle_map = BattleMap(
    width=80,     # Map width in characters
    height=40,    # Map height in characters
    scale=2.0     # Units per character (higher = zoomed out)
)
```

**Scale Guide:**
- `1.0`: Very zoomed in, good for close combat
- `2.0`: Default, balanced view
- `3.0`: Zoomed out, see more of battlefield
- `5.0`: Very zoomed out, large fleet battles

### Coordinate System

- **Origin (0, 0)** is at screen center
- **X-axis**: Positive = East (right)
- **Y-axis**: Positive = North (up)
- **Z-axis**: Not displayed (3D→2D projection)

### Heading Directions

| Degrees | Direction | Symbol |
|---------|-----------|--------|
| 0° | East | → |
| 45° | Northeast | ↗ |
| 90° | North | ↑ |
| 135° | Northwest | ↖ |
| 180° | West | ← |
| 225° | Southwest | ↙ |
| 270° | South | ↓ |
| 315° | Southeast | ↘ |

---

## Integration

### Battle Function Integration

The `battle()` function now accepts logger and map parameters:

```python
from ship_combat.battle_sim import battle
from ship_combat.battle_logger import BattleLogger
from ship_combat.battle_map import BattleMap
from ship_combat.fleet_setup import demo_fleets

# Create logger and map
logger = BattleLogger(verbose=False)
battle_map = BattleMap(width=60, height=30, scale=3.0)

# Get fleets
fleet_a, fleet_b = demo_fleets()

# Run battle with logging and visualization
battle(fleet_a, fleet_b, rounds=5, logger=logger, battle_map=battle_map, show_map=True)

# Print summary
logger.print_summary()
```

### Phase Function Integration

All battle phase functions now accept an optional `logger` parameter:

- `select_orders(fleet, enemy_fleet, logger=None)`
- `move_fleet(fleet, logger=None)`
- `shooting_phase(attacking, defending, logger=None)`
- `missile_phase(attacking, defending, logger=None)`
- `boarding_phase(attacking, defending, logger=None)`
- `repair_phase(fleet, logger=None)`
- `shield_regeneration_phase(fleet, logger=None)`
- `weapon_cooling_phase(fleet, logger=None)`
- `resolve_hazards(fleet, logger=None)`

---

## Usage Examples

### Example 1: Basic Logging

```python
from ship_combat.battle_logger import BattleLogger
from ship_combat.fleet_setup import demo_fleets
from ship_combat.battle_sim import battle

logger = BattleLogger(verbose=True)
fleet_a, fleet_b = demo_fleets()

battle(fleet_a, fleet_b, rounds=3, logger=logger)

# Print summary
logger.print_summary()
```

### Example 2: Silent Logging with Export

```python
from ship_combat.battle_logger import BattleLogger
from ship_combat.fleet_setup import demo_fleets
from ship_combat.battle_sim import battle

# Silent logger (no console spam)
logger = BattleLogger(verbose=False)
fleet_a, fleet_b = demo_fleets()

battle(fleet_a, fleet_b, rounds=5, logger=logger)

# Export to files
logger.export_json("battle_log.json")
logger.export_text("battle_log.txt")

print("Battle logs exported!")
```

### Example 3: Map Visualization Only

```python
from ship_combat.battle_map import BattleMap
from ship_combat.fleet_setup import demo_fleets
from ship_combat.battle_sim import battle

battle_map = BattleMap(width=80, height=40, scale=2.5)
fleet_a, fleet_b = demo_fleets()

# Show map each round
battle(fleet_a, fleet_b, rounds=3, battle_map=battle_map, show_map=True)
```

### Example 4: Full Integration

```python
from ship_combat.battle_logger import BattleLogger
from ship_combat.battle_map import BattleMap
from ship_combat.fleet_setup import demo_fleets
from ship_combat.battle_sim import battle

# Create logger (silent) and map
logger = BattleLogger(verbose=False)
battle_map = BattleMap(width=60, height=30, scale=3.0)

# Get fleets
fleet_a, fleet_b = demo_fleets()

# Show initial state
print("Initial Battlefield:")
print(battle_map.render(fleet_a, fleet_b, show_grid=True))
print(battle_map.render_tactical(fleet_a, fleet_b))

# Run battle
battle(fleet_a, fleet_b, rounds=5, logger=logger, battle_map=battle_map, show_map=True)

# Export logs
logger.export_json("battle.json")
logger.export_text("battle.txt")

# Print statistics
summary = logger.get_summary()
print(f"\nTotal Rounds: {summary['total_rounds']}")
print(f"Total Damage: {summary['total_damage_dealt']}")
print(f"Accuracy: {summary['overall_accuracy']:.1f}%")
print(f"Critical Hits: {summary['critical_hits']}")
```

### Example 5: Analyzing Battle Data

```python
import json
from ship_combat.battle_logger import BattleLogger
from ship_combat.fleet_setup import demo_fleets
from ship_combat.battle_sim import battle

logger = BattleLogger(verbose=False)
fleet_a, fleet_b = demo_fleets()

battle(fleet_a, fleet_b, rounds=10, logger=logger)

# Export and analyze
logger.export_json("analysis.json")

with open("analysis.json") as f:
    data = json.load(f)

# Find best round
best_round = max(data['round_summaries'], key=lambda r: r['total_damage_dealt'])
print(f"Most damaging round: {best_round['round']}")
print(f"Damage dealt: {best_round['total_damage_dealt']}")
print(f"Accuracy: {best_round['accuracy']:.1f}%")

# Count critical hits per ship
critical_events = [e for e in logger.events if e.event_type == "critical_hit"]
for event in critical_events:
    print(f"{event.ship_name} scored critical on {event.details['target']}")
```

---

## Export Formats

### JSON Export

Structured data export suitable for analysis and visualization.

```json
{
  "start_time": "2025-11-02T10:30:00",
  "end_time": "2025-11-02T10:30:15",
  "total_rounds": 5,
  "total_events": 247,
  "total_damage_dealt": 350,
  "total_shots_fired": 45,
  "total_hits": 32,
  "total_misses": 13,
  "overall_accuracy": 71.1,
  "critical_hits": 7,
  "ships_destroyed": ["Enemy Frigate", "Patrol Boat"],
  "round_summaries": [
    {
      "round": 1,
      "events": [...],
      "ships_destroyed": [],
      "total_damage_dealt": 65,
      "total_shots_fired": 10,
      "total_hits": 7,
      "total_misses": 3,
      "critical_hits": 1,
      "accuracy": 70.0
    },
    ...
  ]
}
```

### Text Export

Human-readable battle log.

```
================================================================================
BATTLE LOG
================================================================================

[Round 1] orders - order_selected: Aurora Huntress (order=Lock On)
[Round 1] movement - ship_moved: Aurora Huntress (from_x=0.0, from_y=0.0, to_x=20.0, to_y=5.0, distance=20.6, heading=90.0)
[Round 1] shooting - hit: Aurora Huntress (target=Enemy Cruiser, weapon=Laser, damage=12)
[Round 1] shooting - critical_hit: Victory (target=Enemy Cruiser, weapon=Plasma, damage=24)
...

================================================================================
BATTLE SUMMARY
================================================================================

Total Rounds: 5
Total Events: 247
Total Damage: 350
Accuracy: 71.1%
Critical Hits: 7
Ships Destroyed: Enemy Frigate, Patrol Boat
```

---

## API Reference

### BattleLogger Methods

```python
# Round management
logger.start_round(round_num: int)
logger.end_round()

# Event logging
logger.log_order(ship_name: str, order: str)
logger.log_movement(ship_name: str, old_x: float, old_y: float, new_x: float, new_y: float, heading: float)
logger.log_shot(attacker: str, target: str, weapon: str, hit: bool, damage: int = 0, critical: bool = False)
logger.log_missile(attacker: str, target: str, damage: int)
logger.log_boarding(attacker: str, target: str, success: bool, damage: int = 0)
logger.log_repair(ship_name: str, system: str, old_efficiency: int, new_efficiency: int)
logger.log_shield_regen(ship_name: str, old_shield: int, new_shield: int)
logger.log_heat(ship_name: str, weapon: str, heat: int, overheated: bool)
logger.log_critical_system_damage(ship_name: str, system: str, efficiency: int)
logger.log_destruction(ship_name: str, killed_by: Optional[str] = None)
logger.log_hazard(ship_name: str, hazard_type: str, effect: str)

# Output
logger.print_summary()
logger.get_summary() -> Dict[str, Any]
logger.export_json(filepath: str)
logger.export_text(filepath: str)
```

### BattleMap Methods

```python
# Rendering
battle_map.render(fleet_a: List[Ship], fleet_b: List[Ship], show_grid: bool = True, show_range: bool = False) -> str
battle_map.render_compact(fleet_a: List[Ship], fleet_b: List[Ship]) -> str
battle_map.render_tactical(fleet_a: List[Ship], fleet_b: List[Ship]) -> str

# Utility
battle_map.world_to_screen(x: float, y: float) -> Tuple[int, int]
battle_map.get_heading_char(heading: float) -> str
```

---

## Performance Considerations

- **Logger**: O(1) per event, minimal overhead
- **Map Rendering**: O(n) where n = number of ships
- **Export**: O(n) where n = total events

For battles with 100+ rounds and many ships, consider:
- Setting `verbose=False` to reduce console I/O
- Exporting logs only at end of battle
- Using compact rendering instead of full map

---

## Future Enhancements

Potential additions:

- [ ] **HTML Export** - Interactive web-based battle playback
- [ ] **Animated Maps** - Frame-by-frame battle visualization
- [ ] **Heatmaps** - Damage concentration visualization
- [ ] **Ship Trails** - Show movement history
- [ ] **3D Isometric View** - Better Z-axis visualization
- [ ] **Real-time Streaming** - WebSocket-based live updates
- [ ] **Replay System** - Step through battle turn-by-turn
- [ ] **Statistics Dashboard** - Charts and graphs
- [ ] **Custom Event Filters** - Filter logs by event type
- [ ] **Diff Views** - Compare multiple battles

---

*Last updated: 2025-11-02*
