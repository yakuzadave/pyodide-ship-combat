# DESIGN_CANVAS: Data Model Overview

This project simulates simple fleet battles. The new `models.py` module defines core dataclasses used across the example code.

## Dataclasses

### `ShipSystem`
Represents an individual system on a ship (e.g. engines, shields). Each system
tracks its current status, efficiency and a critical threshold for degradation.
Systems may define an `effect` string that describes what happens when the
system goes offline (e.g. "Hull exposed").

Fields:
- `status`: textual state such as `Operational`, `Degraded`, or `Offline`.
- `efficiency`: percentage value (0-100) describing how well the system performs.
- `critical_threshold`: point below which the system is considered `Degraded`.
- `effect`: narrative effect when the system fails

### `WeaponBattery`
Represents a single turret or battery.

Fields:
- `name`: descriptive label
- `rating`: offensive strength
- `accuracy`: attack modifier
- `arc`: fire arc (fore, aft, etc.)
- `damage_dice`: damage roll expression
- `range`: effective range band
- `special`: optional special rule such as `area` or `piercing`

### `WeaponSystem`
Aggregates multiple batteries and missile stores.

Fields:
- `batteries`: list of `WeaponBattery`
- `missiles`: remaining missile count
- `rating`: property returning the total of all battery ratings

### `Ship`
Encapsulates an entire vessel with hull and shield values plus a set of
`ShipSystem` objects.

Key fields:
- `name`, `hull`, `shield`
- `weapons`: `WeaponSystem` instance
- `crew`, `leadership`, `boarding_strength`
- `class_name`: high level ship classification (frigate, cruiser, etc.)
- `speed`, `maneuver`: basic movement traits
- `systems`: mapping of system names to `ShipSystem`
- `ai`: description or personality string used for flavour text
- `order` and `range`: current tactical order and range band

`Ship` implements `__getitem__` and `__setitem__` so existing dictionary-style
sample code continues to function while using the dataclasses.

## Usage Pattern

The helper `new_ship` function in the sample interface instantiates `Ship` objects with pre-populated systems. Systems are created using `system_status_block`, which now returns a `ShipSystem` dataclass.

These dataclasses replace the previous raw dictionaries, providing clearer
structure for future expansion while remaining lightweight for Pyodide.
