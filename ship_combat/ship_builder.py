"""
Fluent ship builder for creating ships with modular components.

Provides a clean, chainable API for constructing ships with sensible defaults
and component-based customization.
"""

from __future__ import annotations
from typing import Dict, List, Optional
import random

from .models import Ship, ShipSystem, WeaponSystem
from .ship_components import (
    EngineComponent,
    ShieldComponent,
    ReactorComponent,
    ENGINE_LIBRARY,
    SHIELD_LIBRARY,
    REACTOR_LIBRARY,
    WEAPON_LOADOUTS,
    create_weapon_system,
    build_ship_systems,
    apply_variance,
)


class ShipBuilder:
    """
    Fluent builder for constructing Ship instances.
    
    Provides a chainable API for setting ship attributes and components
    with sensible defaults.
    
    Example:
        >>> ship = (ShipBuilder("Aurora")
        ...     .with_class("Light Cruiser")
        ...     .with_hull(80)
        ...     .with_engine("cruiser_standard")
        ...     .with_shield("heavy")
        ...     .with_weapons(["lance_battery", "macro_cannon"], missiles=4)
        ...     .build())
    """
    
    def __init__(self, name: str):
        """Initialize builder with ship name."""
        self.name = name
        self.class_name = "Frigate"
        self.hull = 50
        self.crew = 100
        self.leadership = 7
        self.boarding_strength = 5
        
        # Components (will be set to defaults if not specified)
        self._engine: Optional[EngineComponent] = None
        self._shield: Optional[ShieldComponent] = None
        self._reactor: Optional[ReactorComponent] = None
        self._weapon_batteries: List[str] = []
        self._missiles = 0
        
        # Position and orientation
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.heading = 0.0
        self.pitch = 0.0
        
        # Systems
        self._systems: Optional[Dict[str, ShipSystem]] = None
        
        # AI personality
        self.ai = ""
        
        # Variance for randomization
        self._variance = 0
    
    def with_class(self, class_name: str) -> ShipBuilder:
        """Set ship class (e.g., 'Frigate', 'Cruiser', 'Battleship')."""
        self.class_name = class_name
        return self
    
    def with_hull(self, hull: int) -> ShipBuilder:
        """Set hull points."""
        self.hull = hull
        return self
    
    def with_crew(self, crew: int, leadership: int = 7, boarding_strength: int = 5) -> ShipBuilder:
        """Set crew statistics."""
        self.crew = crew
        self.leadership = leadership
        self.boarding_strength = boarding_strength
        return self
    
    def with_engine(self, engine_key: str) -> ShipBuilder:
        """Set engine from ENGINE_LIBRARY."""
        if engine_key in ENGINE_LIBRARY:
            self._engine = ENGINE_LIBRARY[engine_key]
        return self
    
    def with_engine_component(self, engine: EngineComponent) -> ShipBuilder:
        """Set custom engine component."""
        self._engine = engine
        return self
    
    def with_shield(self, shield_key: str) -> ShipBuilder:
        """Set shield from SHIELD_LIBRARY."""
        if shield_key in SHIELD_LIBRARY:
            self._shield = SHIELD_LIBRARY[shield_key]
        return self
    
    def with_shield_component(self, shield: ShieldComponent) -> ShipBuilder:
        """Set custom shield component."""
        self._shield = shield
        return self
    
    def with_reactor(self, reactor_key: str) -> ShipBuilder:
        """Set reactor from REACTOR_LIBRARY."""
        if reactor_key in REACTOR_LIBRARY:
            self._reactor = REACTOR_LIBRARY[reactor_key]
        return self
    
    def with_reactor_component(self, reactor: ReactorComponent) -> ShipBuilder:
        """Set custom reactor component."""
        self._reactor = reactor
        return self
    
    def with_weapons(self, batteries: List[str], missiles: int = 0) -> ShipBuilder:
        """
        Set weapons from battery names.
        
        Args:
            batteries: List of battery names from WEAPON_BATTERY_LIBRARY
            missiles: Number of missiles
        """
        self._weapon_batteries = batteries
        self._missiles = missiles
        return self
    
    def with_weapon_loadout(self, loadout_key: str, missiles: int = 0) -> ShipBuilder:
        """
        Set weapons from a preset loadout.
        
        Args:
            loadout_key: Key from WEAPON_LOADOUTS
            missiles: Number of missiles
        """
        if loadout_key in WEAPON_LOADOUTS:
            self._weapon_batteries = WEAPON_LOADOUTS[loadout_key]
            self._missiles = missiles
        return self
    
    def with_position(self, x: float, y: float, z: float = 0.0) -> ShipBuilder:
        """Set initial position."""
        self.x = x
        self.y = y
        self.z = z
        return self
    
    def with_orientation(self, heading: float, pitch: float = 0.0) -> ShipBuilder:
        """Set initial orientation (degrees)."""
        self.heading = heading
        self.pitch = pitch
        return self
    
    def with_systems(self, systems: Dict[str, ShipSystem]) -> ShipBuilder:
        """Set custom ship systems dictionary."""
        self._systems = systems
        return self
    
    def with_ai_personality(self, ai: str) -> ShipBuilder:
        """Set AI personality description."""
        self.ai = ai
        return self
    
    def with_variance(self, variance_percent: int = 10) -> ShipBuilder:
        """
        Apply random variance to ship stats on build.
        
        Args:
            variance_percent: Percentage variance (e.g., 10 = ±10%)
        """
        self._variance = variance_percent
        return self
    
    def build(self) -> Ship:
        """
        Construct the Ship instance.
        
        Applies defaults for any unset components and builds the final ship.
        """
        # Apply variance if requested
        hull = self.hull
        crew = self.crew
        leadership = self.leadership
        boarding_strength = self.boarding_strength
        
        if self._variance > 0:
            hull = apply_variance(self.hull, self._variance)
            crew = apply_variance(self.crew, self._variance)
            leadership = max(1, min(10, apply_variance(self.leadership, self._variance)))
            boarding_strength = max(1, apply_variance(self.boarding_strength, self._variance))
        
        # Use defaults if components not specified
        engine = self._engine or ENGINE_LIBRARY["frigate_standard"]
        shield = self._shield or SHIELD_LIBRARY["standard"]
        reactor = self._reactor or REACTOR_LIBRARY["standard"]
        
        # Build weapon system
        weapons = create_weapon_system(
            self._weapon_batteries or ["light_laser"],
            missiles=self._missiles
        )
        
        # Build systems if not provided
        systems = self._systems
        if systems is None:
            systems = build_ship_systems(variance=self._variance)
        
        # Apply variance to shield values
        shield_value = shield.shield
        max_shield_value = shield.max_shield
        if self._variance > 0:
            shield_value = apply_variance(shield.shield, self._variance)
            max_shield_value = apply_variance(shield.max_shield, self._variance)
            # Ensure max_shield is always >= current shield
            max_shield_value = max(max_shield_value, shield_value)
        
        # Construct Ship
        return Ship(
            name=self.name,
            class_name=self.class_name,
            hull=hull,
            shield=shield_value,
            max_shield=max_shield_value,
            shield_regen_rate=shield.regen_rate,
            weapons=weapons,
            crew=crew,
            leadership=leadership,
            boarding_strength=boarding_strength,
            speed=engine.speed,
            maneuver=engine.maneuver,
            max_power=reactor.max_power,
            systems=systems,
            ai=self.ai,
            x=self.x,
            y=self.y,
            z=self.z,
            heading=self.heading,
            pitch=self.pitch,
        )


# ==================== Quick Builder Functions ====================

def quick_ship(
    name: str,
    class_name: str = "Frigate",
    hull: int = 50,
    shield_type: str = "standard",
    engine_type: str = "frigate_standard",
    weapon_loadout: str = "frigate_balanced",
    missiles: int = 0,
    crew: int = 100,
    leadership: int = 7,
    boarding_strength: int = 5,
) -> Ship:
    """
    Quick function to create a ship with common presets.
    
    Args:
        name: Ship name
        class_name: Ship class
        hull: Hull points
        shield_type: Key from SHIELD_LIBRARY
        engine_type: Key from ENGINE_LIBRARY
        weapon_loadout: Key from WEAPON_LOADOUTS
        missiles: Number of missiles
        crew: Crew count
        leadership: Leadership rating
        boarding_strength: Boarding strength
        
    Returns:
        Configured Ship
    """
    return (ShipBuilder(name)
            .with_class(class_name)
            .with_hull(hull)
            .with_shield(shield_type)
            .with_engine(engine_type)
            .with_weapon_loadout(weapon_loadout, missiles=missiles)
            .with_crew(crew, leadership, boarding_strength)
            .build())


def randomized_ship(
    name: str,
    class_name: str = "Frigate",
    base_hull: int = 50,
    variance: int = 15
) -> Ship:
    """
    Create a ship with randomized stats based on ship class.
    
    Args:
        name: Ship name
        class_name: Ship class (determines component selection)
        base_hull: Base hull points
        variance: Stat variance percentage
        
    Returns:
        Ship with randomized components
    """
    # Determine class-appropriate components
    class_lower = class_name.lower()
    
    # Select random components
    engine_keys = [k for k in ENGINE_LIBRARY.keys() if class_lower in k]
    engine_key = random.choice(engine_keys) if engine_keys else "frigate_standard"
    
    shield_key = random.choice(list(SHIELD_LIBRARY.keys()))
    
    weapon_keys = [k for k in WEAPON_LOADOUTS.keys() if class_lower in k]
    weapon_key = random.choice(weapon_keys) if weapon_keys else "frigate_balanced"
    
    missiles = random.randint(0, 8)
    crew = apply_variance(100, variance)
    leadership = random.randint(5, 9)
    boarding_strength = random.randint(3, 8)
    
    return (ShipBuilder(name)
            .with_class(class_name)
            .with_hull(base_hull)
            .with_engine(engine_key)
            .with_shield(shield_key)
            .with_weapon_loadout(weapon_key, missiles=missiles)
            .with_crew(crew, leadership, boarding_strength)
            .with_variance(variance)
            .build())
