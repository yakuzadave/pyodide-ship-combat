from .models import Ship, ShipSystem, WeaponSystem, WeaponBattery
from .fleet_setup import demo_fleets, new_ship, system_block
from .battle_sim import (
    BATTLE_ORDERS,
    HAZARDS,
    distance,
    move_fleet,
    in_arc,
    in_range,
    can_fire,
)

# New ship building components
from .ship_components import (
    EngineComponent,
    ShieldComponent,
    ReactorComponent,
    ENGINE_LIBRARY,
    SHIELD_LIBRARY,
    REACTOR_LIBRARY,
    WEAPON_BATTERY_LIBRARY,
    WEAPON_LOADOUTS,
    create_weapon_system,
    build_ship_systems,
)
from .ship_builder import ShipBuilder, quick_ship, randomized_ship
from .fleet_generator import (
    FleetGenerator,
    ShipClassTemplate,
    SHIP_CLASS_TEMPLATES,
    FLEET_COMPOSITIONS,
    quick_fleet,
    symmetric_fleets,
)

__all__ = [
    # Core models
    "Ship",
    "ShipSystem",
    "WeaponSystem",
    "WeaponBattery",
    # Legacy fleet setup
    "demo_fleets",
    "new_ship",
    "system_block",
    # Battle mechanics
    "BATTLE_ORDERS",
    "HAZARDS",
    "distance",
    "move_fleet",
    "in_arc",
    "in_range",
    "can_fire",
    # Ship components
    "EngineComponent",
    "ShieldComponent",
    "ReactorComponent",
    "ENGINE_LIBRARY",
    "SHIELD_LIBRARY",
    "REACTOR_LIBRARY",
    "WEAPON_BATTERY_LIBRARY",
    "WEAPON_LOADOUTS",
    "create_weapon_system",
    "build_ship_systems",
    # Ship builder
    "ShipBuilder",
    "quick_ship",
    "randomized_ship",
    # Fleet generator
    "FleetGenerator",
    "ShipClassTemplate",
    "SHIP_CLASS_TEMPLATES",
    "FLEET_COMPOSITIONS",
    "quick_fleet",
    "symmetric_fleets",
]
