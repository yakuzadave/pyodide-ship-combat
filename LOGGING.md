# Battle Logging and Visualization Guide

This document describes the enhanced logging, visualization, and analytics features added to the Pyodide Ship Combat Simulator.

## Features

### 1. Structured Logging System

The battle simulator now includes a comprehensive logging system with configurable log levels and detailed event tracking.

#### Log Levels

- **DEBUG**: Detailed information including movement, repairs, shield regeneration, weapon cooling
- **INFO**: Standard battle events (default) - shots, hits, order selection, critical hits
- **WARNING**: Important events only - ship destruction, hazards, weapon overheating
- **ERROR**: Critical errors only

#### Usage

```python
from ship_combat.battle_sim import battle
from ship_combat.fleet_setup import demo_fleets
import logging

fleet_a, fleet_b = demo_fleets()

# Run battle with INFO logging (default)
battle(fleet_a, fleet_b, rounds=3, log_level=logging.INFO)

# Run with detailed DEBUG logging
battle(fleet_a, fleet_b, rounds=3, log_level=logging.DEBUG)
```

#### CLI Usage

```bash
# Standard logging
python -m ship_combat.battle_sim --rounds 3

# Debug logging
python -m ship_combat.battle_sim --rounds 3 --log-level DEBUG

# Minimal logging
python -m ship_combat.battle_sim --rounds 3 --log-level WARNING
```

### 2. Text-Based Battle Map Visualization

ASCII-art tactical display showing ship positions, headings, and elevation.

#### Features

- **Top-down view** (XY plane) with heading arrows
- **Side view** (XZ plane) showing elevation
- **Range rings** showing point/short/standard range bands
- **Ship markers**: Fleet A uses arrows/letters (A, B, C...), Fleet B uses numbers (1, 2, 3...)
- **Legend** with ship status, position, and heading

#### Heading Arrows

- `→` East (0°)
- `↗` Northeast (45°)
- `↑` North (90°)
- `↖` Northwest (135°)
- `←` West (180°)
- `↙` Southwest (225°)
- `↓` South (270°)
- `↘` Southeast (315°)

#### Usage

```python
from ship_combat.battle_sim import battle
from ship_combat.fleet_setup import demo_fleets

fleet_a, fleet_b = demo_fleets()

# Run battle with tactical map each round
battle(fleet_a, fleet_b, rounds=3, show_map=True)
```

#### CLI Usage

```bash
# Show tactical map each round
python -m ship_combat.battle_sim --rounds 3 --show-map
```

#### Example Map Output

```
================================================================================
ROUND 1 - TACTICAL DISPLAY
================================================================================

TOP-DOWN VIEW (XY Plane):
┌────────────────────────────────────────────────────────────┐
│                          ↑                                 │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                                            │
│                                  1                         │
│                                                            │
└────────────────────────────────────────────────────────────┘

================================================================================
FLEET A:
  [A] Aurora Huntress      Hull:80/145          Pos:( -10.0,  25.8,   0.0) Hdg:↑ Elv:=

FLEET B:
  [1] Celestial Warden     Hull:100/180         Pos:(  10.0, -18.5,   0.0) Hdg:↓ Elv:=
================================================================================
```

### 3. Battle Statistics and Analytics

Comprehensive tracking of combat performance and outcomes.

#### Statistics Tracked

**Per Fleet:**
- Ships destroyed
- Total damage dealt/taken
- Shots fired/hit
- Accuracy percentage
- Critical hits
- Critical hit rate
- Missiles fired

**Combat Events:**
- Boarding attempts/successes
- Environmental hazards encountered
- Systems repaired
- Weapons overheated

**Per Ship:**
- Damage dealt by each ship
- Damage taken by each ship
- Kills (ships destroyed)

#### Battle Report Example

```
================================================================================
BATTLE REPORT
================================================================================

Rounds Fought: 3
Duration: 2025-01-15T10:30:00 to 2025-01-15T10:30:15

--- FLEET A STATISTICS ---
Ships Destroyed (Fleet A): 0
Total Damage Dealt: 145
Total Damage Taken: 78
Accuracy: 62.5% (10/16)
Critical Hit Rate: 20.0%
Missiles Fired: 3

--- FLEET B STATISTICS ---
Ships Destroyed (Fleet B): 0
Total Damage Dealt: 78
Total Damage Taken: 145
Accuracy: 45.5% (5/11)
Critical Hit Rate: 0.0%
Missiles Fired: 2

--- COMBAT EVENTS ---
Boarding Attempts: 2 (Success: 1)
Hazards Encountered: 3
Systems Repaired: 5
Weapons Overheated: 2

--- TOP PERFORMERS ---
Most Damage Dealt: Aurora Huntress (145 HP)
Most Kills: Aurora Huntress (0 ships)
================================================================================
```

#### Usage

```python
from ship_combat.battle_sim import battle
from ship_combat.fleet_setup import demo_fleets

fleet_a, fleet_b = demo_fleets()

# Run battle and get statistics
logger = battle(fleet_a, fleet_b, rounds=3, show_stats=True)

# Access statistics programmatically
print(f"Fleet A Accuracy: {logger.stats.get_accuracy('a'):.1f}%")
print(f"Fleet B Accuracy: {logger.stats.get_accuracy('b'):.1f}%")
```

### 4. Quick Status Display

Compact fleet status summary with visual health bars.

```
================================================================================
FLEET STATUS
================================================================================
Fleet A: 1/1 ships operational, Total Hull: 80
  Aurora Huntress      H:[░░░░░░░░  ] S:[██████    ] (80HP/65SP)

Fleet B: 1/1 ships operational, Total Hull: 100
  Celestial Warden     H:[░░░░░░░░░░] S:[████████  ] (100HP/80SP)
================================================================================
```

## Advanced Features

### BattleLogger API

The `BattleLogger` class provides comprehensive event tracking:

```python
from ship_combat.battle_logger import BattleLogger
import logging

# Create logger
logger = BattleLogger(
    log_level=logging.INFO,
    log_to_file=True,  # Also log to file
    filename="battle_20250115.log"  # Optional custom filename
)

# Logger methods (called automatically by battle simulator)
logger.start_battle(fleet_a, fleet_b)
logger.log_round_start(1)
logger.log_phase("Shooting")
logger.log_shot(attacker, target, "Lance Battery", hit=True, damage=15, critical=False)
logger.log_ship_destroyed(ship, killer)
logger.end_battle()

# Generate report
report = logger.generate_report()
print(report)

# Access raw events
for event in logger.events:
    print(f"{event.timestamp} - {event.event_type}: {event.message}")

# Query events
shooting_events = logger.get_events_by_phase("Shooting")
ship_events = logger.get_events_by_ship("Aurora Huntress")
```

### BattleMap API

The `BattleMap` class provides tactical visualization:

```python
from ship_combat.battle_map import BattleMap, render_quick_status

# Create map
battle_map = BattleMap(
    width=80,      # Character width
    height=30,     # Character height
    grid_size=50.0 # Game units represented
)

# Render views
top_down = battle_map.render_top_down(
    fleet_a, fleet_b,
    show_heading=True,
    show_range_rings=True
)
print(top_down)

side_view = battle_map.render_side_view(fleet_a, fleet_b)
print(side_view)

legend = battle_map.render_legend(fleet_a, fleet_b)
print(legend)

# Complete visualization
complete = battle_map.render_complete(
    fleet_a, fleet_b,
    round_num=1,
    show_range_rings=False
)
print(complete)

# Quick status (standalone function)
status = render_quick_status(fleet_a, fleet_b)
print(status)
```

## Pyodide/PyScript Integration

All logging and visualization features are fully compatible with Pyodide and can be used in browser-based PyScript applications.

### HTML Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>Fleet Battle</title>
  <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
  <script defer src="https://pyscript.net/latest/pyscript.js"></script>
</head>
<body>
  <h1>Fleet Battle Simulator</h1>
  <button id="run">Run Battle</button>
  <pre id="output"></pre>

  <script type="py" output="output">
import micropip
await micropip.install("py-rolldice")
import logging
from fleet_setup import demo_fleets
import BATTLE_SIM

fleet_a, fleet_b = demo_fleets()

# Run with enhanced logging
BATTLE_SIM.battle(
    fleet_a, fleet_b,
    rounds=3,
    log_level=logging.INFO,
    show_map=True,
    show_stats=True
)
  </script>
</body>
</html>
```

See `battle.html` for a full interactive demo with configurable options.

## Performance Considerations

- **Logging overhead**: DEBUG level has ~10-15% performance impact
- **Map rendering**: ~5% performance impact per round when enabled
- **Statistics tracking**: Negligible performance impact
- **Memory**: Event history grows linearly with battle length

For long battles (>100 rounds), consider:
- Using WARNING or ERROR log level
- Disabling map visualization
- Clearing event history periodically

## Tips and Best Practices

1. **Development**: Use `--log-level DEBUG --show-map` to see everything
2. **Production**: Use `--log-level INFO` for balanced output
3. **Analysis**: Enable `show_stats=True` to get post-battle analytics
4. **Debugging**: Access `logger.events` for detailed event inspection
5. **Performance**: Use `logging.WARNING` for fastest execution

## File Structure

```
ship_combat/
├── battle_logger.py   # Structured logging and statistics
├── battle_map.py      # ASCII tactical map visualization
└── battle_sim.py      # Updated with logging integration

Root-level re-exports (for Pyodide):
├── battle_logger.py   # Re-exports ship_combat.battle_logger
└── battle_map.py      # Re-exports ship_combat.battle_map
```

## Future Enhancements

Potential additions:
- JSON/CSV export of battle statistics
- HTML report generation
- Real-time event streaming
- WebSocket integration for live updates
- 3D visualization (browser-based)
- Replay system from event log
- Heatmap of damage concentration
- Movement trails showing ship paths
