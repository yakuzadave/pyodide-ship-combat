# pyodide-ship-combat
Playing around with the idea of running a ship-combat simulator with pyodide inspired by Battlefleet Gothic



# Battlefleet Gothic-Inspired Python Fleet Simulator

## Overview

An extensible, web-friendly, fully automated fleet battle simulator inspired by Battlefleet Gothic. Built for modern Python in the browser (Pyodide/JupyterLite) or locally, with:

* Multi-ship combat
* Order and critical system mechanics
* Environmental hazards
* Persistent repairs & system degradation
* Zero user input (everything is programmatic)

---

## Features

* Modular and extensible: Easily add ships, hazards, or custom rules
* Automated AI orders and target selection each round
* System degradation, critical hits, and repair attempts
* Fully compatible with browser/Jupyter/Pyodide (no blocking I/O)
* Example code for both procedural and OOP usage

---

## Quickstart

### In the Browser (Pyodide/JupyterLite)

No `pip install` required! All dependencies are installed at runtime via [micropip](https://pyodide.org/en/stable/usage/packages-in-pyodide.html#installing-pure-python-wheels-using-micropip).

```python
import micropip
await micropip.install("py-rolldice")
import rolldice
```

Place this at the top of your notebook or script, then run your simulator code.

---

### Local Development (Optional)

To run or test locally (for VSCode, Jupyter Desktop, etc):

```sh
pip install -r requirements.txt
# or
poetry install
```

---

## Requirements

Minimal `requirements.txt`:

```
py-rolldice
```

(You may add others as needed—keep it pure Python or Pyodide-compatible!)

Poetry example for `pyproject.toml`:

```toml
[tool.poetry]
name = "bfg-fleet-sim"
version = "0.1.0"
description = "Battlefleet Gothic-inspired fleet simulator for Pyodide"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
py-rolldice = "*"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## Example Usage

### Roll a Dice Expression

```python
import rolldice
result, explanation = rolldice.roll_dice("2d20+4")
print(f"Result: {result}")
print(f"Explanation: {explanation}")
```

### Random Automated Order

```python
import random
BATTLE_ORDERS = [
    "Brace for Impact", "Lock On", "All Power to Shields", "Reload Ordnance",
    "Boarding Party", "Fire Everything"
]
def random_order():
    order = random.choice(BATTLE_ORDERS)
    print(f"Order this round: {order}")
    return order
```

### One-Round Class-Based Battle Scaffold

```python
import rolldice, random
class Ship:
    def __init__(self, name, hull, shield):
        self.name = name
        self.hull = hull
        self.shield = shield
        self.order = None
        self.alive = True
    def choose_order(self, order_list):
        self.order = random.choice(order_list)
        print(f"{self.name} chooses order: {self.order}")
    def attack(self, target):
        atk, _ = rolldice.roll_dice("2d20+2")
        print(f"{self.name} attacks {target.name} for {atk}!")
        if atk > 28:
            shield, _ = rolldice.roll_dice("1d100")
            print(f"{target.name} shield roll: {shield}")
            if shield > target.shield:
                dmg, _ = rolldice.roll_dice("2d10")
                target.hull -= int(dmg)
                print(f"Hit! {target.name} hull now {target.hull}")
                if target.hull <= 0:
                    target.alive = False
                    print(f"{target.name} destroyed!")
            else:
                print("Shields absorb the hit!")
        else:
            print("Miss!")

BATTLE_ORDERS = [
    "Brace for Impact", "Lock On", "All Power to Shields",
    "Reload Ordnance", "Boarding Party", "Fire Everything"
]

fleet = [
    Ship("Aurora", 78, 65),
    Ship("Black Horizon", 85, 70),
    Ship("Celestial Warden", 90, 80),
]

for round_num in range(3):
    print(f"\n=== ROUND {round_num+1} ===")
    for ship in fleet:
        if ship.alive:
            ship.choose_order(BATTLE_ORDERS)
    for ship in fleet:
        if ship.alive:
            targets = [s for s in fleet if s is not ship and s.alive]
            if targets:
                target = random.choice(targets)
                ship.attack(target)

print("\nFINAL STATUS:")
for ship in fleet:
    print(f"{ship.name}: {'ALIVE' if ship.alive else 'DESTROYED'}, Hull: {ship.hull}")
```

---

## Project Structure & Design

* **No user input:** All logic is automated for browser safety and reproducibility
* **Extensible:** Modular, OOP-friendly, and ready for advanced features (system tracking, boarding, repairs)
* **Output:** Print/log, or append to a Python list for web/Jupyter integration

---

## Further Ideas

* Add support for multi-fleet, multiplayer, or commander AI
* Integrate with visualizations (mermaid, matplotlib)
* Campaign and salvage mechanics
* Pre-bundled demo fleets and scenarios

---

## Best Practices & Notes

* For Pyodide: `requirements.txt` and `pyproject.toml` are for dev/CI only
* Install all runtime dependencies using `micropip` in the browser
* Keep dependencies minimal for faster startup
* See the examples above for battle scaffolds and dice usage



## Running in the Browser (Pyodide/JupyterLite)
No pip install required! Dependencies are loaded at runtime using [micropip](https://pyodide.org/en/stable/usage/packages-in-pyodide.html#installing-pure-python-wheels-using-micropip).

Add this to your main Python cell or script:
```python
import micropip
await micropip.install("py-rolldice")
import rolldice
```

