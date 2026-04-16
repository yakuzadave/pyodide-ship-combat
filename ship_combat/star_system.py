"""
Star system models for a 4X campaign layer.

Provides Planet, JumpPoint, and StarSystem dataclasses that represent
the strategic map, inspired by Aurora 4X.  All models use plain Python
dataclasses so they remain Pyodide-compatible.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Planet types
# ---------------------------------------------------------------------------

PLANET_TYPES = [
    "Terrestrial",
    "Gas Giant",
    "Ice",
    "Barren",
    "Volcanic",
    "Ocean",
    "Desert",
]


@dataclass
class Planet:
    """A planet or significant body within a star system."""

    name: str
    planet_type: str = "Terrestrial"
    # Physical properties (Earth units)
    mass: float = 1.0
    radius: float = 1.0
    # Orbital distance from the star in AU
    orbital_distance: float = 1.0
    # Habitability rating 0–100
    habitability: float = 0.0
    # Known mineral deposits (resource_name -> relative abundance 0–1)
    mineral_resources: Dict[str, float] = field(default_factory=dict)
    # If colonised, the ID of the owning colony
    colony_id: Optional[str] = None
    is_surveyed: bool = False
    # 2-D position on the system map (AU, computed on generation)
    x: float = 0.0
    y: float = 0.0

    def distance_to(self, other: "Planet") -> float:
        """Euclidean distance to another body in AU."""
        return math.hypot(self.x - other.x, self.y - other.y)


@dataclass
class JumpPoint:
    """
    A navigable wormhole connecting this star system to another.

    Jump points allow fleets to travel between star systems without
    traversing interstellar distances at sub-light speed.
    """

    name: str
    # ID of the destination star system
    target_system_id: str
    # Position within this system (AU)
    x: float = 0.0
    y: float = 0.0
    # Stability: 1.0 = perfectly stable, lower values add travel risk
    stability: float = 1.0
    # Whether any empire has found this jump point yet
    is_discovered: bool = False
    # Empire ID that first discovered this jump point
    discovered_by: Optional[str] = None

    def is_accessible_by(self, empire_id: str) -> bool:
        """Return True if the empire may use this jump point."""
        if not self.is_discovered:
            return False
        return self.discovered_by == empire_id or self.is_discovered


@dataclass
class StarSystem:
    """A complete star system with planets and jump points."""

    id: str
    name: str
    # Spectral class: O B A F G K M (hottest to coolest)
    star_type: str = "G"
    # Position on the galaxy map (arbitrary units)
    x: float = 0.0
    y: float = 0.0
    # Inhabited planets / significant bodies
    planets: List[Planet] = field(default_factory=list)
    # FTL navigation connections
    jump_points: List[JumpPoint] = field(default_factory=list)
    # Discovery state
    is_explored: bool = False
    controlling_empire_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_planet(self, name: str) -> Optional[Planet]:
        """Return the named planet, or None."""
        for planet in self.planets:
            if planet.name == name:
                return planet
        return None

    def get_jump_point(self, target_system_id: str) -> Optional[JumpPoint]:
        """Return the jump point leading to ``target_system_id``, or None."""
        for jp in self.jump_points:
            if jp.target_system_id == target_system_id:
                return jp
        return None

    def habitable_planets(self) -> List[Planet]:
        """Return planets with a habitability score above zero."""
        return [p for p in self.planets if p.habitability > 0]

    def colonised_planets(self) -> List[Planet]:
        """Return planets that have an active colony."""
        return [p for p in self.planets if p.colony_id is not None]

    def discovered_jump_points(self) -> List[JumpPoint]:
        """Return jump points that have been discovered."""
        return [jp for jp in self.jump_points if jp.is_discovered]

    def galaxy_distance_to(self, other: "StarSystem") -> float:
        """Straight-line distance to another star system on the galaxy map."""
        return math.hypot(self.x - other.x, self.y - other.y)


# ---------------------------------------------------------------------------
# Procedural generation helpers
# ---------------------------------------------------------------------------

_STAR_TYPES = ["O", "B", "A", "F", "G", "K", "M"]
_STAR_TYPE_WEIGHTS = [1, 2, 5, 10, 20, 30, 50]

_MINERAL_NAMES = ["iron", "titanium", "crystals", "rare_earth", "fuel_ice"]


def _generate_planet(
    system_name: str,
    index: int,
    orbital_distance: float,
    rng: random.Random,
) -> Planet:
    """Create a randomly generated planet."""
    planet_type = rng.choice(PLANET_TYPES)
    habitability = 0.0
    if planet_type == "Terrestrial":
        # Rough habitability based on orbital distance (0.7–1.5 AU is ideal)
        ideal = 1.0
        deviation = abs(orbital_distance - ideal)
        habitability = max(0.0, 100.0 - deviation * 80.0)
        habitability = round(habitability * rng.uniform(0.5, 1.0), 1)

    minerals: Dict[str, float] = {}
    for mineral in _MINERAL_NAMES:
        if rng.random() < 0.4:
            minerals[mineral] = round(rng.uniform(0.1, 1.0), 2)

    angle = rng.uniform(0, 2 * math.pi)
    x = round(orbital_distance * math.cos(angle), 3)
    y = round(orbital_distance * math.sin(angle), 3)

    return Planet(
        name=f"{system_name} {_roman(index + 1)}",
        planet_type=planet_type,
        mass=round(rng.uniform(0.1, 10.0), 2),
        radius=round(rng.uniform(0.3, 3.0), 2),
        orbital_distance=orbital_distance,
        habitability=habitability,
        mineral_resources=minerals,
        x=x,
        y=y,
    )


def _roman(n: int) -> str:
    """Convert small positive integer to Roman numeral string."""
    vals = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    result = ""
    for value, numeral in vals:
        while n >= value:
            result += numeral
            n -= value
    return result


def generate_star_system(
    system_id: str,
    name: str,
    x: float = 0.0,
    y: float = 0.0,
    num_planets: Optional[int] = None,
    seed: Optional[int] = None,
) -> StarSystem:
    """
    Procedurally generate a star system.

    Args:
        system_id: Unique string identifier.
        name: Human-readable name.
        x: Galaxy-map X coordinate.
        y: Galaxy-map Y coordinate.
        num_planets: Number of planets to generate (2–6 if None).
        seed: RNG seed for reproducibility.

    Returns:
        A populated :class:`StarSystem`.
    """
    rng = random.Random(seed)

    star_type = rng.choices(_STAR_TYPES, weights=_STAR_TYPE_WEIGHTS, k=1)[0]
    if num_planets is None:
        num_planets = rng.randint(2, 6)

    planets: List[Planet] = []
    for i in range(num_planets):
        orbital_distance = round(rng.uniform(0.3, 5.0), 2)
        planet = _generate_planet(name, i, orbital_distance, rng)
        planets.append(planet)

    return StarSystem(
        id=system_id,
        name=name,
        star_type=star_type,
        x=x,
        y=y,
        planets=planets,
        jump_points=[],
    )


def link_systems(
    system_a: StarSystem,
    system_b: StarSystem,
    discovered: bool = False,
    discovered_by: Optional[str] = None,
    stability: float = 1.0,
) -> None:
    """
    Create a bidirectional jump-point link between two star systems.

    Each system gains a :class:`JumpPoint` pointing to the other.
    """
    jp_a = JumpPoint(
        name=f"Jump to {system_b.name}",
        target_system_id=system_b.id,
        x=round((system_b.x - system_a.x) * 0.1, 3),
        y=round((system_b.y - system_a.y) * 0.1, 3),
        stability=stability,
        is_discovered=discovered,
        discovered_by=discovered_by,
    )
    jp_b = JumpPoint(
        name=f"Jump to {system_a.name}",
        target_system_id=system_a.id,
        x=round((system_a.x - system_b.x) * 0.1, 3),
        y=round((system_a.y - system_b.y) * 0.1, 3),
        stability=stability,
        is_discovered=discovered,
        discovered_by=discovered_by,
    )
    system_a.jump_points.append(jp_a)
    system_b.jump_points.append(jp_b)
