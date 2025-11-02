from dataclasses import dataclass, field
from typing import Dict, Optional, List

@dataclass
class ShipSystem:
    """Represents a single ship subsystem such as engines or shields."""

    status: str = "Operational"
    efficiency: int = 100
    critical_threshold: int = 50
    effect: str = ""

    def copy(self) -> "ShipSystem":
        return ShipSystem(self.status, self.efficiency, self.critical_threshold)

    def damage(self, amount: int) -> None:
        """Apply damage lowering efficiency and updating status."""
        self.efficiency = max(0, self.efficiency - amount)
        if self.efficiency == 0:
            self.status = "Offline"
        elif self.efficiency < self.critical_threshold:
            self.status = "Degraded"

    def repair(self, amount: int) -> None:
        """Repair the system towards full efficiency."""
        if self.status != "Offline":
            self.efficiency = min(100, self.efficiency + amount)
            if self.efficiency >= self.critical_threshold:
                self.status = "Operational"

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __setitem__(self, key: str, value):
        setattr(self, key, value)

@dataclass
class WeaponBattery:
    """Individual weapon battery entry."""

    name: str
    rating: int
    accuracy: int = 0
    arc: str = "fore"
    damage_dice: str = "1d6"
    range: str = "standard"
    special: Optional[str] = None
    heat: int = 0  # Current heat level (0-100)
    max_heat: int = 100  # Maximum heat before overheating
    heat_per_shot: int = 20  # Heat generated per shot
    cooling_rate: int = 10  # Heat dissipated per round

    def add_heat(self) -> bool:
        """Add heat from firing. Returns True if weapon overheats."""
        self.heat = min(self.max_heat, self.heat + self.heat_per_shot)
        return self.heat >= self.max_heat

    def cool_down(self) -> None:
        """Reduce heat by cooling rate."""
        self.heat = max(0, self.heat - self.cooling_rate)

    def is_overheated(self) -> bool:
        """Check if weapon is too hot to fire."""
        return self.heat >= self.max_heat


@dataclass
class WeaponSystem:
    batteries: List[WeaponBattery] = field(default_factory=list)
    missiles: int = 0

    @property
    def rating(self) -> int:
        """Aggregate rating of all weapon batteries."""
        return sum(b.rating for b in self.batteries)

    def add_battery(self, battery: WeaponBattery) -> None:
        self.batteries.append(battery)

@dataclass
class Ship:
    name: str
    hull: int
    shield: int
    weapons: WeaponSystem
    crew: int
    leadership: int
    boarding_strength: int
    class_name: str = "Frigate"
    speed: int = 20
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    heading: float = 0.0
    pitch: float = 0.0
    maneuver: int = 1
    systems: Dict[str, ShipSystem] = field(default_factory=dict)
    ai: str = ""
    order: Optional[str] = None
    range: str = "standard"
    attack_mod: int = 0
    defense_mod: int = 0
    repair_priority: bool = False

    # Navigation & Formation
    formation_leader: Optional["Ship"] = None  # Ship to follow in formation
    formation_offset_x: float = 0.0  # Relative position to leader
    formation_offset_y: float = 0.0
    formation_offset_z: float = 0.0
    evasion_active: bool = False  # Currently performing evasive maneuvers
    pursuing_target: Optional["Ship"] = None  # Ship being actively pursued

    # Power Management
    max_power: int = 100  # Total power available
    power_allocation: Dict[str, int] = field(default_factory=lambda: {
        "weapons": 33,
        "shields": 33,
        "engines": 34
    })

    # Shield Regeneration
    max_shield: int = 0  # Maximum shield capacity (set on init)
    shield_regen_rate: int = 5  # Shield points regenerated per round

    # Critical Hit Tracking
    critical_damage_taken: int = 0  # Count of critical hits sustained

    def __post_init__(self):
        """Initialize max_shield if not already set."""
        if self.max_shield == 0:
            self.max_shield = self.shield

    def regenerate_shields(self) -> None:
        """Regenerate shields based on power allocation and regen rate."""
        if self.shield < self.max_shield:
            power_mod = self.power_allocation.get("shields", 33) / 33.0
            regen = int(self.shield_regen_rate * power_mod)
            self.shield = min(self.max_shield, self.shield + regen)

    def get_power_modifier(self, system: str) -> float:
        """Get power modifier for a system (0.0 to 2.0+ range)."""
        allocation = self.power_allocation.get(system, 33)
        return allocation / 33.0  # 33% is baseline (1.0x)

    def __getitem__(self, item: str):
        return getattr(self, item)

    def __setitem__(self, key: str, value):
        setattr(self, key, value)
