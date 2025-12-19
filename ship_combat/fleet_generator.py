"""
Fleet generator for creating diverse fleets with various compositions.

Provides tools for generating fleets with different strategies, ship class
distributions, and randomization levels.
"""

from __future__ import annotations
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import random

from .models import Ship
from .ship_builder import ShipBuilder, randomized_ship, quick_ship


@dataclass
class ShipClassTemplate:
    """Template defining base stats for a ship class."""
    class_name: str
    base_hull: int
    crew_range: Tuple[int, int]
    leadership_range: Tuple[int, int]
    boarding_range: Tuple[int, int]
    typical_engines: List[str]
    typical_shields: List[str]
    typical_weapons: List[str]
    missile_range: Tuple[int, int]


# ==================== Ship Class Templates ====================

SHIP_CLASS_TEMPLATES = {
    "Corvette": ShipClassTemplate(
        class_name="Corvette",
        base_hull=30,
        crew_range=(40, 60),
        leadership_range=(5, 7),
        boarding_range=(2, 4),
        typical_engines=["corvette_standard"],
        typical_shields=["light"],
        typical_weapons=["corvette_interceptor"],
        missile_range=(0, 2),
    ),
    "Frigate": ShipClassTemplate(
        class_name="Frigate",
        base_hull=50,
        crew_range=(80, 120),
        leadership_range=(6, 8),
        boarding_range=(4, 6),
        typical_engines=["frigate_standard", "frigate_fast"],
        typical_shields=["light", "standard"],
        typical_weapons=["frigate_balanced", "frigate_long_range", "frigate_brawler"],
        missile_range=(0, 4),
    ),
    "Destroyer": ShipClassTemplate(
        class_name="Destroyer",
        base_hull=60,
        crew_range=(100, 150),
        leadership_range=(7, 8),
        boarding_range=(5, 7),
        typical_engines=["destroyer_standard"],
        typical_shields=["standard", "reinforced"],
        typical_weapons=["destroyer_torpedo", "destroyer_missile"],
        missile_range=(4, 8),
    ),
    "Light Cruiser": ShipClassTemplate(
        class_name="Light Cruiser",
        base_hull=80,
        crew_range=(150, 250),
        leadership_range=(7, 9),
        boarding_range=(6, 8),
        typical_engines=["cruiser_standard"],
        typical_shields=["standard", "heavy"],
        typical_weapons=["cruiser_standard"],
        missile_range=(2, 6),
    ),
    "Cruiser": ShipClassTemplate(
        class_name="Cruiser",
        base_hull=90,
        crew_range=(200, 300),
        leadership_range=(7, 9),
        boarding_range=(7, 9),
        typical_engines=["cruiser_standard", "cruiser_heavy"],
        typical_shields=["heavy", "reinforced"],
        typical_weapons=["cruiser_standard", "cruiser_heavy", "cruiser_plasma"],
        missile_range=(4, 8),
    ),
    "Battleship": ShipClassTemplate(
        class_name="Battleship",
        base_hull=100,
        crew_range=(300, 500),
        leadership_range=(8, 10),
        boarding_range=(8, 12),
        typical_engines=["battleship_standard", "battleship_slow"],
        typical_shields=["capital", "heavy"],
        typical_weapons=["battleship_standard", "battleship_nova", "battleship_balanced"],
        missile_range=(4, 10),
    ),
}


# ==================== Fleet Composition Presets ====================

FLEET_COMPOSITIONS = {
    "balanced": {
        "Corvette": 0.1,
        "Frigate": 0.3,
        "Destroyer": 0.2,
        "Light Cruiser": 0.2,
        "Cruiser": 0.15,
        "Battleship": 0.05,
    },
    "strike_force": {
        "Frigate": 0.4,
        "Destroyer": 0.4,
        "Light Cruiser": 0.2,
    },
    "capital_fleet": {
        "Light Cruiser": 0.3,
        "Cruiser": 0.4,
        "Battleship": 0.3,
    },
    "raiding_party": {
        "Corvette": 0.3,
        "Frigate": 0.5,
        "Destroyer": 0.2,
    },
    "heavy_assault": {
        "Cruiser": 0.5,
        "Battleship": 0.5,
    },
    "patrol_group": {
        "Corvette": 0.2,
        "Frigate": 0.6,
        "Light Cruiser": 0.2,
    },
}


# ==================== Fleet Generator ====================

class FleetGenerator:
    """
    Generator for creating diverse fleets.
    
    Supports various fleet compositions, randomization levels, and naming schemes.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize fleet generator.
        
        Args:
            seed: Random seed for reproducible fleets
        """
        if seed is not None:
            random.seed(seed)
    
    def generate_fleet(
        self,
        size: int,
        composition: str = "balanced",
        variance: int = 15,
        prefix: str = "Ship",
        starting_x: float = 0.0,
        starting_y: float = 0.0,
        formation_spread: float = 10.0,
    ) -> List[Ship]:
        """
        Generate a fleet with specified composition.
        
        Args:
            size: Number of ships in fleet
            composition: Fleet composition type (from FLEET_COMPOSITIONS)
            variance: Stat variance percentage
            prefix: Name prefix for ships
            starting_x: Starting X coordinate
            starting_y: Starting Y coordinate
            formation_spread: Spacing between ships
            
        Returns:
            List of Ship instances
        """
        if composition not in FLEET_COMPOSITIONS:
            composition = "balanced"
        
        comp = FLEET_COMPOSITIONS[composition]
        fleet = []
        
        # Determine ship classes based on composition
        ship_classes = []
        for ship_class, ratio in comp.items():
            count = max(1, int(size * ratio))
            ship_classes.extend([ship_class] * count)
        
        # Trim or pad to exact size
        if len(ship_classes) > size:
            ship_classes = ship_classes[:size]
        elif len(ship_classes) < size:
            # Fill remaining with most common class
            most_common = max(comp.items(), key=lambda x: x[1])[0]
            ship_classes.extend([most_common] * (size - len(ship_classes)))
        
        # Shuffle for variety
        random.shuffle(ship_classes)
        
        # Generate ships
        for i, ship_class in enumerate(ship_classes):
            name = f"{prefix} {i+1}"
            
            # Position ships in formation
            row = i // 3
            col = i % 3
            x = starting_x + (col - 1) * formation_spread
            y = starting_y + row * formation_spread
            
            ship = self._create_ship_from_template(
                name=name,
                ship_class=ship_class,
                variance=variance,
                x=x,
                y=y,
            )
            fleet.append(ship)
        
        return fleet
    
    def generate_custom_fleet(
        self,
        ship_counts: Dict[str, int],
        variance: int = 15,
        prefix: str = "Ship",
        starting_x: float = 0.0,
        starting_y: float = 0.0,
        formation_spread: float = 10.0,
    ) -> List[Ship]:
        """
        Generate a fleet with custom ship class counts.
        
        Args:
            ship_counts: Dictionary of {ship_class: count}
            variance: Stat variance percentage
            prefix: Name prefix for ships
            starting_x: Starting X coordinate
            starting_y: Starting Y coordinate
            formation_spread: Spacing between ships
            
        Returns:
            List of Ship instances
            
        Example:
            >>> gen = FleetGenerator()
            >>> fleet = gen.generate_custom_fleet({
            ...     "Frigate": 3,
            ...     "Cruiser": 2,
            ...     "Battleship": 1,
            ... })
        """
        fleet = []
        ship_num = 1
        
        for ship_class, count in ship_counts.items():
            for i in range(count):
                name = f"{prefix} {ship_num}"
                ship_num += 1
                
                # Position ships
                idx = len(fleet)
                row = idx // 3
                col = idx % 3
                x = starting_x + (col - 1) * formation_spread
                y = starting_y + row * formation_spread
                
                ship = self._create_ship_from_template(
                    name=name,
                    ship_class=ship_class,
                    variance=variance,
                    x=x,
                    y=y,
                )
                fleet.append(ship)
        
        return fleet
    
    def _create_ship_from_template(
        self,
        name: str,
        ship_class: str,
        variance: int,
        x: float,
        y: float,
    ) -> Ship:
        """Create a ship from a class template."""
        if ship_class not in SHIP_CLASS_TEMPLATES:
            ship_class = "Frigate"
        
        template = SHIP_CLASS_TEMPLATES[ship_class]
        
        # Randomize within template ranges
        crew = random.randint(*template.crew_range)
        leadership = random.randint(*template.leadership_range)
        boarding = random.randint(*template.boarding_range)
        missiles = random.randint(*template.missile_range)
        
        # Select random components from typical options
        engine = random.choice(template.typical_engines)
        shield = random.choice(template.typical_shields)
        weapons = random.choice(template.typical_weapons)
        
        # Random heading
        heading = random.uniform(0, 360)
        
        return (ShipBuilder(name)
                .with_class(template.class_name)
                .with_hull(template.base_hull)
                .with_engine(engine)
                .with_shield(shield)
                .with_weapon_loadout(weapons, missiles=missiles)
                .with_crew(crew, leadership, boarding)
                .with_position(x, y, 0.0)
                .with_orientation(heading, 0.0)
                .with_variance(variance)
                .build())


# ==================== Convenience Functions ====================

def quick_fleet(
    size: int = 5,
    composition: str = "balanced",
    variance: int = 15,
    prefix: str = "Ship",
    seed: Optional[int] = None,
) -> List[Ship]:
    """
    Quick function to generate a fleet.
    
    Args:
        size: Number of ships
        composition: Fleet composition type
        variance: Stat variance percentage
        prefix: Name prefix
        seed: Random seed for reproducibility
        
    Returns:
        List of Ship instances
    """
    gen = FleetGenerator(seed=seed)
    return gen.generate_fleet(
        size=size,
        composition=composition,
        variance=variance,
        prefix=prefix,
    )


def symmetric_fleets(
    size: int = 3,
    composition: str = "balanced",
    variance: int = 10,
    fleet_a_prefix: str = "Alpha",
    fleet_b_prefix: str = "Bravo",
    separation: float = 100.0,
    seed: Optional[int] = None,
) -> Tuple[List[Ship], List[Ship]]:
    """
    Generate two opposing fleets positioned symmetrically.
    
    Args:
        size: Ships per fleet
        composition: Fleet composition type
        variance: Stat variance percentage
        fleet_a_prefix: Fleet A name prefix
        fleet_b_prefix: Fleet B name prefix
        separation: Distance between fleets
        seed: Random seed
        
    Returns:
        Tuple of (fleet_a, fleet_b)
    """
    gen = FleetGenerator(seed=seed)
    
    fleet_a = gen.generate_fleet(
        size=size,
        composition=composition,
        variance=variance,
        prefix=fleet_a_prefix,
        starting_x=-separation / 2,
        starting_y=0.0,
    )
    
    fleet_b = gen.generate_fleet(
        size=size,
        composition=composition,
        variance=variance,
        prefix=fleet_b_prefix,
        starting_x=separation / 2,
        starting_y=0.0,
    )
    
    # Orient fleet B towards fleet A
    for ship in fleet_b:
        ship.heading = 180.0
    
    return fleet_a, fleet_b
