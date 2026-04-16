"""
Campaign layer that connects the ship combat engine to a strategic star-system map.

Provides Empire, CampaignFleet, and CampaignManager which together implement
a lightweight Aurora 4X-inspired campaign mode on top of the existing battle
simulation engine.  Everything is plain Python so the module runs in Pyodide.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .models import Ship
from .star_system import (
    StarSystem,
    JumpPoint,
    generate_star_system,
    link_systems,
)


# ---------------------------------------------------------------------------
# Empire
# ---------------------------------------------------------------------------

@dataclass
class Empire:
    """A player or AI faction in the campaign."""

    id: str
    name: str
    # The star system where this empire started
    home_system_id: str
    # Resource stockpiles (resource_name -> quantity)
    resources: Dict[str, float] = field(default_factory=lambda: {
        "minerals": 500.0,
        "fuel_ice": 200.0,
        "credits": 1000.0,
    })
    # IDs of fleets belonging to this empire
    fleet_ids: List[str] = field(default_factory=list)
    # IDs of star systems this empire has surveyed
    surveyed_systems: List[str] = field(default_factory=list)
    # IDs of colonies this empire controls
    colony_ids: List[str] = field(default_factory=list)
    # Bonus to research output per turn (0 = no bonus)
    research_bonus: float = 0.0
    # Victory points accumulated so far
    victory_points: int = 0

    def is_hostile_to(self, other: "Empire") -> bool:
        """By default all empires are hostile to each other."""
        return self.id != other.id


# ---------------------------------------------------------------------------
# Colony
# ---------------------------------------------------------------------------

@dataclass
class Colony:
    """A settlement on a planet."""

    id: str
    name: str
    empire_id: str
    system_id: str
    planet_name: str
    population: int = 1_000
    # Per-turn resource production
    production: Dict[str, float] = field(default_factory=lambda: {
        "minerals": 5.0,
        "fuel_ice": 2.0,
        "credits": 10.0,
    })
    # Infrastructure level drives production multiplier
    infrastructure_level: int = 1

    def production_this_turn(self) -> Dict[str, float]:
        """Return resource yield for one turn, scaled by infrastructure."""
        mult = 1.0 + (self.infrastructure_level - 1) * 0.2
        return {k: round(v * mult, 2) for k, v in self.production.items()}


# ---------------------------------------------------------------------------
# Campaign fleet
# ---------------------------------------------------------------------------

@dataclass
class CampaignFleet:
    """
    A group of ships in the campaign, located in a specific star system.

    On the strategic map fleets move between star systems through jump points.
    When two hostile fleets are in the same system a tactical battle occurs.
    """

    id: str
    name: str
    empire_id: str
    # Current star system
    system_id: str
    # Combat-ready ship objects
    ships: List[Ship] = field(default_factory=list)
    # If the fleet is in transit, this holds the destination system id
    transit_destination: Optional[str] = None
    # Turns remaining until fleet arrives (1 = arrives next turn)
    transit_turns_remaining: int = 0

    @property
    def is_in_transit(self) -> bool:
        return self.transit_destination is not None

    @property
    def strength(self) -> int:
        """Rough combat power: sum of hull + shield for living ships."""
        return sum(s.hull + s.shield for s in self.ships if s.hull > 0)

    @property
    def ship_count(self) -> int:
        return sum(1 for s in self.ships if s.hull > 0)

    def remove_destroyed_ships(self) -> int:
        """Remove ships with hull <= 0 and return the count removed."""
        before = len(self.ships)
        self.ships = [s for s in self.ships if s.hull > 0]
        return before - len(self.ships)


# ---------------------------------------------------------------------------
# Campaign event log entry
# ---------------------------------------------------------------------------

@dataclass
class CampaignEvent:
    """A narrative event recorded during campaign turns."""

    turn: int
    event_type: str  # "combat", "discovery", "colonisation", "resource", "transit"
    description: str
    empire_id: Optional[str] = None
    system_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Campaign Manager
# ---------------------------------------------------------------------------

class CampaignManager:
    """
    Manages the strategic layer of a 4X campaign.

    Responsibilities:
    - Maintain the galaxy map (star systems + jump-point connections).
    - Track empires, fleets, and colonies.
    - Advance turns: process transit, resource collection, and combat triggers.
    - Record a turn-by-turn event log.
    """

    def __init__(self) -> None:
        self.star_systems: Dict[str, StarSystem] = {}
        self.empires: Dict[str, Empire] = {}
        self.fleets: Dict[str, CampaignFleet] = {}
        self.colonies: Dict[str, Colony] = {}
        self.turn: int = 0
        self.event_log: List[CampaignEvent] = []

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------

    def add_system(self, system: StarSystem) -> None:
        """Register a star system with the campaign."""
        self.star_systems[system.id] = system

    def add_empire(self, empire: Empire) -> None:
        """Register an empire and mark its home system as explored."""
        self.empires[empire.id] = empire
        if empire.home_system_id in self.star_systems:
            self.star_systems[empire.home_system_id].is_explored = True
            self.star_systems[empire.home_system_id].controlling_empire_id = empire.id
            if empire.home_system_id not in empire.surveyed_systems:
                empire.surveyed_systems.append(empire.home_system_id)

    def add_fleet(self, fleet: CampaignFleet) -> None:
        """Register a fleet and link it to its empire."""
        self.fleets[fleet.id] = fleet
        empire = self.empires.get(fleet.empire_id)
        if empire and fleet.id not in empire.fleet_ids:
            empire.fleet_ids.append(fleet.id)

    def add_colony(self, colony: Colony) -> None:
        """Register a colony and link it to its empire."""
        self.colonies[colony.id] = colony
        empire = self.empires.get(colony.empire_id)
        if empire and colony.id not in empire.colony_ids:
            empire.colony_ids.append(colony.id)
        # Mark the planet as colonised
        system = self.star_systems.get(colony.system_id)
        if system:
            planet = system.get_planet(colony.planet_name)
            if planet:
                planet.colony_id = colony.id

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def order_fleet_transit(
        self, fleet_id: str, destination_system_id: str, transit_turns: int = 1
    ) -> Tuple[bool, str]:
        """
        Order a fleet to transit to another star system via a jump point.

        Args:
            fleet_id: The fleet to move.
            destination_system_id: Target star system ID.
            transit_turns: Number of turns the journey takes.

        Returns:
            (success, message) tuple.
        """
        fleet = self.fleets.get(fleet_id)
        if fleet is None:
            return False, f"Fleet '{fleet_id}' not found."
        if fleet.is_in_transit:
            return False, f"Fleet '{fleet.name}' is already in transit."

        current_system = self.star_systems.get(fleet.system_id)
        if current_system is None:
            return False, "Fleet's current system not found."

        jp = current_system.get_jump_point(destination_system_id)
        if jp is None:
            return False, (
                f"No jump point from {current_system.name} "
                f"to system '{destination_system_id}'."
            )

        empire = self.empires.get(fleet.empire_id)
        if empire and not jp.is_accessible_by(fleet.empire_id):
            # Discover the jump point on first use by this empire
            jp.is_discovered = True
            jp.discovered_by = fleet.empire_id

        fleet.transit_destination = destination_system_id
        fleet.transit_turns_remaining = max(1, transit_turns)
        self._log(
            "transit",
            f"Fleet '{fleet.name}' begins transit to {destination_system_id}.",
            empire_id=fleet.empire_id,
            system_id=fleet.system_id,
        )
        return True, f"Fleet '{fleet.name}' is now in transit."

    # ------------------------------------------------------------------
    # Turn processing
    # ------------------------------------------------------------------

    def advance_turn(self) -> List[CampaignEvent]:
        """
        Advance the campaign by one turn.

        Processing order:
        1. Increment turn counter.
        2. Process fleet transits.
        3. Collect colony resources.
        4. Check for contested systems (triggers for tactical battles).
        5. Return events that occurred this turn.

        Returns:
            List of :class:`CampaignEvent` generated this turn.
        """
        self.turn += 1
        events_this_turn: List[CampaignEvent] = []

        # --- Transit resolution ---
        for fleet in list(self.fleets.values()):
            if not fleet.is_in_transit:
                continue
            fleet.transit_turns_remaining -= 1
            if fleet.transit_turns_remaining <= 0:
                evt = self._complete_transit(fleet)
                if evt:
                    events_this_turn.append(evt)

        # --- Colony resource production ---
        for colony in self.colonies.values():
            empire = self.empires.get(colony.empire_id)
            if empire is None:
                continue
            produced = colony.production_this_turn()
            for resource, amount in produced.items():
                empire.resources[resource] = (
                    empire.resources.get(resource, 0.0) + amount
                )
            self._log(
                "resource",
                (
                    f"{colony.name} produced "
                    + ", ".join(f"{v} {k}" for k, v in produced.items())
                ),
                empire_id=colony.empire_id,
                system_id=colony.system_id,
            )

        # --- Detect contested systems ---
        contested = self._find_contested_systems()
        for system_id, empire_fleets in contested.items():
            system = self.star_systems[system_id]
            evt = self._log(
                "combat",
                (
                    f"System '{system.name}' is contested by fleets from empires: "
                    + ", ".join(
                        set(self.fleets[fid].empire_id for fid in empire_fleets)
                    )
                ),
                system_id=system_id,
            )
            events_this_turn.append(evt)

        # Collect all events logged this turn
        turn_events = [e for e in self.event_log if e.turn == self.turn]
        return turn_events

    # ------------------------------------------------------------------
    # Colonisation
    # ------------------------------------------------------------------

    def colonise_planet(
        self,
        empire_id: str,
        system_id: str,
        planet_name: str,
        colony_name: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Establish a colony on an unoccupied, surveyed planet.

        Returns:
            (success, message) tuple.
        """
        empire = self.empires.get(empire_id)
        if empire is None:
            return False, f"Empire '{empire_id}' not found."

        system = self.star_systems.get(system_id)
        if system is None:
            return False, f"System '{system_id}' not found."

        planet = system.get_planet(planet_name)
        if planet is None:
            return False, f"Planet '{planet_name}' not found in {system.name}."
        if planet.colony_id is not None:
            return False, f"{planet_name} is already colonised."
        if not planet.is_surveyed:
            return False, f"{planet_name} has not been surveyed yet."

        # Cost to colonise
        colonisation_cost = {"minerals": 200.0, "credits": 300.0}
        for resource, cost in colonisation_cost.items():
            if empire.resources.get(resource, 0.0) < cost:
                return False, (
                    f"Insufficient {resource} to colonise "
                    f"(need {cost}, have {empire.resources.get(resource, 0):.0f})."
                )

        for resource, cost in colonisation_cost.items():
            empire.resources[resource] -= cost

        colony_id = f"colony_{empire_id}_{system_id}_{planet_name}"
        name = colony_name or f"{planet_name} Colony"
        colony = Colony(
            id=colony_id,
            name=name,
            empire_id=empire_id,
            system_id=system_id,
            planet_name=planet_name,
        )
        self.add_colony(colony)
        empire.victory_points += 10

        self._log(
            "colonisation",
            f"Empire '{empire.name}' colonised {planet_name} in {system.name}.",
            empire_id=empire_id,
            system_id=system_id,
        )
        return True, f"Colony '{name}' established on {planet_name}."

    # ------------------------------------------------------------------
    # Survey / exploration
    # ------------------------------------------------------------------

    def survey_system(self, empire_id: str, system_id: str) -> Tuple[bool, str]:
        """
        Survey a star system, revealing its planets and jump points.

        Requires a fleet from the empire to be present in the system.
        """
        empire = self.empires.get(empire_id)
        if empire is None:
            return False, f"Empire '{empire_id}' not found."

        system = self.star_systems.get(system_id)
        if system is None:
            return False, f"System '{system_id}' not found."

        # Check empire has a fleet in this system
        present = any(
            f.empire_id == empire_id and f.system_id == system_id and not f.is_in_transit
            for f in self.fleets.values()
        )
        if not present:
            return False, "No fleet present in system."

        system.is_explored = True
        for planet in system.planets:
            planet.is_surveyed = True

        # Discover all jump points from this system
        for jp in system.jump_points:
            if not jp.is_discovered:
                jp.is_discovered = True
                jp.discovered_by = empire_id

        if system_id not in empire.surveyed_systems:
            empire.surveyed_systems.append(system_id)
            empire.victory_points += 5

        self._log(
            "discovery",
            f"Empire '{empire.name}' surveyed {system.name}.",
            empire_id=empire_id,
            system_id=system_id,
        )
        return True, f"System '{system.name}' surveyed."

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def fleets_in_system(self, system_id: str) -> List[CampaignFleet]:
        """Return all fleets currently in the given system (not in transit)."""
        return [
            f for f in self.fleets.values()
            if f.system_id == system_id and not f.is_in_transit
        ]

    def empire_fleet_strength(self, empire_id: str) -> int:
        """Total combat strength across all fleets owned by the empire."""
        return sum(
            f.strength
            for f in self.fleets.values()
            if f.empire_id == empire_id
        )

    def systems_controlled_by(self, empire_id: str) -> List[StarSystem]:
        """Return all star systems controlled by the empire."""
        return [
            s for s in self.star_systems.values()
            if s.controlling_empire_id == empire_id
        ]

    # ------------------------------------------------------------------
    # Factory: generate a randomised galaxy
    # ------------------------------------------------------------------

    @classmethod
    def generate_galaxy(
        cls,
        num_systems: int = 5,
        num_empires: int = 2,
        seed: Optional[int] = None,
    ) -> "CampaignManager":
        """
        Generate a complete galaxy with star systems, jump-point links,
        empires, and starting fleets.

        Args:
            num_systems: Total number of star systems to generate.
            num_empires: Number of empires (must be <= num_systems).
            seed: RNG seed for reproducibility.

        Returns:
            A fully initialised :class:`CampaignManager`.
        """
        from .fleet_generator import quick_fleet

        rng = random.Random(seed)
        num_empires = min(num_empires, num_systems)
        manager = cls()

        # --- Generate systems ---
        system_names = _unique_system_names(num_systems, rng)
        positions = _distribute_positions(num_systems, rng)

        systems: List[StarSystem] = []
        for i, name in enumerate(system_names):
            sys_seed = rng.randint(0, 2**31)
            sys = generate_star_system(
                system_id=f"sys_{i}",
                name=name,
                x=positions[i][0],
                y=positions[i][1],
                seed=sys_seed,
            )
            systems.append(sys)
            manager.add_system(sys)

        # --- Link systems with jump points ---
        # Each system connects to at least one neighbour
        for i, sys in enumerate(systems):
            # Find nearest unlinked neighbour
            nearest_j = min(
                (j for j in range(len(systems)) if j != i),
                key=lambda j: sys.galaxy_distance_to(systems[j]),
            )
            if sys.get_jump_point(systems[nearest_j].id) is None:
                link_systems(
                    sys,
                    systems[nearest_j],
                    discovered=False,
                    stability=round(rng.uniform(0.7, 1.0), 2),
                )

        # --- Create empires with home systems ---
        empire_system_indices = rng.sample(range(num_systems), num_empires)
        empire_names = _unique_empire_names(num_empires, rng)

        for idx, sys_index in enumerate(empire_system_indices):
            home_system = systems[sys_index]
            empire_id = f"empire_{idx}"
            empire = Empire(
                id=empire_id,
                name=empire_names[idx],
                home_system_id=home_system.id,
            )
            manager.add_empire(empire)

            # Discover jump points in home system
            for jp in home_system.jump_points:
                jp.is_discovered = True
                jp.discovered_by = empire_id

            # Create a starting fleet in the home system
            fleet_ships = quick_fleet(
                size=rng.randint(2, 4),
                composition="patrol_group",
                variance=10,
                prefix=f"{empire.name} Ship",
                seed=rng.randint(0, 2**31),
            )
            fleet_id = f"fleet_{empire_id}_0"
            fleet = CampaignFleet(
                id=fleet_id,
                name=f"{empire.name} Home Fleet",
                empire_id=empire_id,
                system_id=home_system.id,
                ships=fleet_ships,
            )
            manager.add_fleet(fleet)

            # Colonise most habitable planet in home system if one exists
            habitable = sorted(
                home_system.habitable_planets(),
                key=lambda p: p.habitability,
                reverse=True,
            )
            if habitable:
                best = habitable[0]
                best.is_surveyed = True
                empire.resources["minerals"] += 1000.0  # grant extra for first colony
                empire.resources["credits"] += 500.0
                manager.colonise_planet(
                    empire_id=empire_id,
                    system_id=home_system.id,
                    planet_name=best.name,
                    colony_name=f"{empire.name} Capital",
                )

        return manager

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _complete_transit(self, fleet: CampaignFleet) -> Optional[CampaignEvent]:
        """Finalise a fleet's transit and return an event."""
        dest_id = fleet.transit_destination
        fleet.system_id = dest_id
        fleet.transit_destination = None
        fleet.transit_turns_remaining = 0

        dest = self.star_systems.get(dest_id)
        system_name = dest.name if dest else dest_id
        return self._log(
            "transit",
            f"Fleet '{fleet.name}' arrived in {system_name}.",
            empire_id=fleet.empire_id,
            system_id=dest_id,
        )

    def _find_contested_systems(self) -> Dict[str, List[str]]:
        """Return {system_id: [fleet_ids]} for systems with multiple empires."""
        system_empires: Dict[str, Dict[str, List[str]]] = {}
        for fleet in self.fleets.values():
            if fleet.is_in_transit or fleet.ship_count == 0:
                continue
            sys_id = fleet.system_id
            if sys_id not in system_empires:
                system_empires[sys_id] = {}
            emp_id = fleet.empire_id
            system_empires[sys_id].setdefault(emp_id, []).append(fleet.id)

        contested: Dict[str, List[str]] = {}
        for sys_id, empire_map in system_empires.items():
            if len(empire_map) > 1:
                all_fleets = [fid for fids in empire_map.values() for fid in fids]
                contested[sys_id] = all_fleets
        return contested

    def _log(
        self,
        event_type: str,
        description: str,
        empire_id: Optional[str] = None,
        system_id: Optional[str] = None,
    ) -> CampaignEvent:
        evt = CampaignEvent(
            turn=self.turn,
            event_type=event_type,
            description=description,
            empire_id=empire_id,
            system_id=system_id,
        )
        self.event_log.append(evt)
        return evt


# ---------------------------------------------------------------------------
# Name generation helpers
# ---------------------------------------------------------------------------

_SYSTEM_PREFIXES = [
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
    "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi",
    "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega",
]
_SYSTEM_SUFFIXES = [
    "Centauri", "Eridani", "Cygni", "Draconis", "Leonis", "Orionis",
    "Persei", "Tauri", "Ursae", "Virginis", "Aquarii", "Bootis",
]


def _unique_system_names(n: int, rng: random.Random) -> List[str]:
    pool = [
        f"{p} {s}" for p in _SYSTEM_PREFIXES for s in _SYSTEM_SUFFIXES
    ]
    rng.shuffle(pool)
    return pool[:n]


_EMPIRE_ADJECTIVES = [
    "United", "Grand", "Stellar", "Ancient", "New", "Old",
    "Imperial", "Federal", "Free", "Democratic",
]
_EMPIRE_NOUNS = [
    "Terran", "Solarian", "Venusian", "Martian", "Jovian",
    "Hegemony", "Republic", "Confederation", "Alliance", "Dominion",
]


def _unique_empire_names(n: int, rng: random.Random) -> List[str]:
    pool = [f"{a} {b}" for a in _EMPIRE_ADJECTIVES for b in _EMPIRE_NOUNS]
    rng.shuffle(pool)
    return pool[:n]


def _distribute_positions(
    n: int, rng: random.Random, spread: float = 100.0
) -> List[Tuple[float, float]]:
    """Return n (x, y) positions spread across a field."""
    positions = []
    for _ in range(n):
        x = round(rng.uniform(-spread, spread), 1)
        y = round(rng.uniform(-spread, spread), 1)
        positions.append((x, y))
    return positions
