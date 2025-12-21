"""
Ship component library for modular ship construction.

Provides pre-defined components (engines, shields, weapon systems) and variance
generators for creating diverse ship configurations with minimal boilerplate.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import random

from .models import ShipSystem, WeaponSystem, WeaponBattery


# ==================== Ship System Components ====================

@dataclass
class EngineComponent:
    """Engine system specification."""
    name: str
    speed: int
    maneuver: int
    efficiency: int = 100
    effect: str = "Speed halved when offline"


@dataclass
class ShieldComponent:
    """Shield system specification."""
    name: str
    shield: int
    max_shield: int
    regen_rate: int = 5
    efficiency: int = 100
    effect: str = "Hull exposed"


@dataclass
class ReactorComponent:
    """Power reactor specification."""
    name: str
    max_power: int = 100
    efficiency: int = 100
    effect: str = "Catastrophic explosion on failure"


# ==================== Component Libraries ====================

# Engine types by ship class
ENGINE_LIBRARY = {
    "frigate_standard": EngineComponent("Standard Frigate Drive", speed=25, maneuver=2),
    "frigate_fast": EngineComponent("Fast Attack Drive", speed=30, maneuver=3),
    "cruiser_standard": EngineComponent("Cruiser Drive Array", speed=20, maneuver=2),
    "cruiser_heavy": EngineComponent("Heavy Cruiser Drive", speed=18, maneuver=1),
    "battleship_standard": EngineComponent("Battleship Drive Core", speed=15, maneuver=1),
    "battleship_slow": EngineComponent("Dreadnought Drive", speed=12, maneuver=1),
    "destroyer_standard": EngineComponent("Destroyer Drive", speed=28, maneuver=2),
    "corvette_standard": EngineComponent("Corvette Drive", speed=32, maneuver=3),
}

# Shield types by capability
SHIELD_LIBRARY = {
    "light": ShieldComponent("Light Shield Grid", shield=20, max_shield=20, regen_rate=3),
    "standard": ShieldComponent("Standard Shields", shield=40, max_shield=40, regen_rate=5),
    "heavy": ShieldComponent("Heavy Shield Array", shield=65, max_shield=65, regen_rate=7),
    "capital": ShieldComponent("Capital Ship Shields", shield=80, max_shield=80, regen_rate=10),
    "reinforced": ShieldComponent("Reinforced Shields", shield=50, max_shield=50, regen_rate=8),
    "regenerative": ShieldComponent("Regenerative Shields", shield=35, max_shield=35, regen_rate=12),
}

# Reactor types
REACTOR_LIBRARY = {
    "compact": ReactorComponent("Compact Reactor", max_power=80),
    "standard": ReactorComponent("Standard Reactor", max_power=100),
    "enhanced": ReactorComponent("Enhanced Reactor", max_power=120),
    "military": ReactorComponent("Military Grade Reactor", max_power=150),
}

# Weapon battery presets
WEAPON_BATTERY_LIBRARY = {
    # Light weapons
    "light_laser": WeaponBattery(
        "Light Laser Battery", rating=2, accuracy=1, damage_dice="1d6+1", 
        range="standard", heat_per_shot=15, cooling_rate=12
    ),
    "autocannon": WeaponBattery(
        "Autocannon Battery", rating=2, accuracy=0, damage_dice="2d4", 
        range="short", heat_per_shot=10, cooling_rate=15
    ),
    
    # Medium weapons
    "lance_battery": WeaponBattery(
        "Lance Battery", rating=3, accuracy=1, damage_dice="2d6", 
        range="long", heat_per_shot=25, cooling_rate=10
    ),
    "macro_cannon": WeaponBattery(
        "Macro Cannon Battery", rating=2, accuracy=0, damage_dice="3d6",
        range="standard", heat_per_shot=20, cooling_rate=10
    ),
    "plasma_cannon": WeaponBattery(
        "Plasma Cannon", rating=3, accuracy=-1, damage_dice="3d6+2",
        range="standard", heat_per_shot=30, cooling_rate=8, special="piercing"
    ),
    
    # Heavy weapons
    "heavy_lance": WeaponBattery(
        "Heavy Lance Array", rating=4, accuracy=1, damage_dice="3d6+2",
        range="long", heat_per_shot=35, cooling_rate=8
    ),
    "plasma_broadside": WeaponBattery(
        "Plasma Broadside", rating=4, accuracy=-1, damage_dice="4d6",
        range="long", heat_per_shot=40, cooling_rate=5, special="area", arc="port"
    ),
    "nova_cannon": WeaponBattery(
        "Nova Cannon", rating=5, accuracy=-2, damage_dice="5d6",
        range="long", heat_per_shot=50, cooling_rate=5, special="explosive"
    ),
    
    # Specialized weapons
    "torpedo_launcher": WeaponBattery(
        "Torpedo Launcher", rating=3, accuracy=0, damage_dice="4d6",
        range="long", heat_per_shot=15, cooling_rate=20, special="seeking"
    ),
    "missile_pod": WeaponBattery(
        "Missile Pod", rating=2, accuracy=1, damage_dice="2d6",
        range="standard", heat_per_shot=10, cooling_rate=15, special="volley"
    ),
    "point_defense": WeaponBattery(
        "Point Defense Grid", rating=1, accuracy=2, damage_dice="1d6",
        range="short", heat_per_shot=5, cooling_rate=20, arc="omni"
    ),
}


# ==================== Weapon System Presets ====================

def create_weapon_system(batteries: List[str], missiles: int = 0) -> WeaponSystem:
    """
    Create a WeaponSystem from battery names.
    
    Args:
        batteries: List of battery names from WEAPON_BATTERY_LIBRARY
        missiles: Number of missiles
        
    Returns:
        Configured WeaponSystem
        
    Example:
        >>> weapons = create_weapon_system(["lance_battery", "macro_cannon"], missiles=4)
    """
    battery_objects = []
    for name in batteries:
        if name in WEAPON_BATTERY_LIBRARY:
            # Create a copy to avoid shared state
            battery = WEAPON_BATTERY_LIBRARY[name]
            battery_objects.append(WeaponBattery(
                name=battery.name,
                rating=battery.rating,
                accuracy=battery.accuracy,
                arc=battery.arc,
                damage_dice=battery.damage_dice,
                range=battery.range,
                special=battery.special,
                heat=0,
                max_heat=battery.max_heat,
                heat_per_shot=battery.heat_per_shot,
                cooling_rate=battery.cooling_rate,
            ))
    
    return WeaponSystem(batteries=battery_objects, missiles=missiles)


# Preset weapon loadouts
WEAPON_LOADOUTS = {
    "frigate_balanced": ["light_laser", "autocannon"],
    "frigate_long_range": ["lance_battery"],
    "frigate_brawler": ["autocannon", "autocannon"],
    
    "cruiser_standard": ["lance_battery", "macro_cannon"],
    "cruiser_heavy": ["heavy_lance", "macro_cannon"],
    "cruiser_plasma": ["plasma_cannon", "plasma_cannon"],
    
    "battleship_standard": ["heavy_lance", "plasma_broadside"],
    "battleship_nova": ["nova_cannon", "heavy_lance"],
    "battleship_balanced": ["heavy_lance", "macro_cannon", "point_defense"],
    
    "destroyer_torpedo": ["torpedo_launcher", "light_laser"],
    "destroyer_missile": ["missile_pod", "missile_pod"],
    
    "corvette_interceptor": ["light_laser", "point_defense"],
}


# ==================== Variance Generators ====================

def apply_variance(base_value: int, variance_percent: int = 10) -> int:
    """
    Apply random variance to a base value.
    
    Args:
        base_value: Starting value
        variance_percent: Percentage variance (e.g., 10 = ±10%)
        
    Returns:
        Value with random variance applied
    """
    variance = base_value * variance_percent / 100
    return int(base_value + random.uniform(-variance, variance))


def randomize_system_efficiency(base_eff: int = 100, variance: int = 5) -> int:
    """Generate random system efficiency with variance."""
    return max(50, min(100, apply_variance(base_eff, variance)))


# ==================== Ship System Builders ====================

def build_ship_systems(
    include_engines: bool = True,
    include_shields: bool = True,
    include_targeting: bool = True,
    include_reactor: bool = True,
    variance: int = 5
) -> Dict[str, ShipSystem]:
    """
    Build a standard set of ship systems with optional variance.
    
    Args:
        include_engines: Include engine system
        include_shields: Include shield system
        include_targeting: Include targeting system
        include_reactor: Include reactor system
        variance: Efficiency variance percentage
        
    Returns:
        Dictionary of ship systems
    """
    systems = {}
    
    if include_engines:
        systems["engines"] = ShipSystem(
            status="Operational",
            efficiency=randomize_system_efficiency(variance=variance),
            critical_threshold=50,
            effect="Speed halved when offline"
        )
    
    if include_shields:
        systems["shields"] = ShipSystem(
            status="Operational",
            efficiency=randomize_system_efficiency(variance=variance),
            critical_threshold=50,
            effect="Hull exposed"
        )
    
    if include_targeting:
        systems["targeting"] = ShipSystem(
            status="Operational",
            efficiency=randomize_system_efficiency(variance=variance),
            critical_threshold=50,
            effect="Attack penalty"
        )
    
    if include_reactor:
        systems["reactor"] = ShipSystem(
            status="Operational",
            efficiency=randomize_system_efficiency(variance=variance),
            critical_threshold=30,
            effect="Catastrophic explosion on failure"
        )
    
    return systems


# ==================== Utility Functions ====================

def get_random_engine(ship_class: str = "frigate") -> EngineComponent:
    """Get a random engine appropriate for ship class."""
    matching = [k for k in ENGINE_LIBRARY.keys() if k.startswith(ship_class)]
    if matching:
        key = random.choice(matching)
        return ENGINE_LIBRARY[key]
    return ENGINE_LIBRARY["frigate_standard"]


def get_random_shield(min_shield: int = 0) -> ShieldComponent:
    """Get a random shield system above minimum threshold."""
    suitable = [s for s in SHIELD_LIBRARY.values() if s.shield >= min_shield]
    return random.choice(suitable) if suitable else SHIELD_LIBRARY["light"]


def get_random_weapon_loadout(ship_class: str = "frigate") -> List[str]:
    """Get a random weapon loadout for ship class."""
    matching = [k for k, v in WEAPON_LOADOUTS.items() if k.startswith(ship_class)]
    if matching:
        key = random.choice(matching)
        return WEAPON_LOADOUTS[key]
    return WEAPON_LOADOUTS["frigate_balanced"]
