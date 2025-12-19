# Examples

This directory contains example scripts demonstrating various features of the Pyodide Ship Combat system.

## Available Examples

### demo_ship_building.py

Comprehensive demonstration of the ship building and fleet generation system.

**Features demonstrated:**
- Fluent ShipBuilder API
- Quick ship creation functions
- Randomized ships with variance
- Fleet generation with various compositions
- Symmetric fleet generation for battles
- Variance comparison and effects

**Run the demo:**
```bash
# From repository root
PYTHONPATH=. python examples/demo_ship_building.py
```

**Output:**
The script demonstrates:
1. Creating ships with the ShipBuilder fluent API
2. Generating fleets with different compositions
3. Creating symmetric fleets for balanced battles
4. Using quick convenience functions
5. Comparing variance effects on fleet diversity

## Creating Your Own Examples

When creating new examples, remember to:

1. **Import from ship_combat package:**
   ```python
   from ship_combat.ship_builder import ShipBuilder
   from ship_combat.fleet_generator import FleetGenerator
   ```

2. **Run with PYTHONPATH set** (if not installed):
   ```bash
   PYTHONPATH=. python examples/your_example.py
   ```

3. **Or install the package** in development mode:
   ```bash
   pip install -e .
   python examples/your_example.py
   ```

## Example Template

```python
#!/usr/bin/env python3
"""Your example description."""

from ship_combat.ship_builder import ShipBuilder
from ship_combat.fleet_generator import quick_fleet

def main():
    # Create a custom ship
    ship = (ShipBuilder("MyShip")
            .with_class("Cruiser")
            .with_hull(90)
            .build())
    
    # Generate a fleet
    fleet = quick_fleet(size=5, composition="balanced")
    
    # Display results
    print(f"Ship: {ship.name}")
    print(f"Fleet: {len(fleet)} ships")

if __name__ == "__main__":
    main()
```

## More Information

- See [SHIP_BUILDING.md](../SHIP_BUILDING.md) for comprehensive documentation
- See [README.md](../README.md) for project overview
- See [tests/](../tests/) for more usage examples
