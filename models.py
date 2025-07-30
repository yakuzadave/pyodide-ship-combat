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
    maneuver: int = 1
    systems: Dict[str, ShipSystem] = field(default_factory=dict)
    ai: str = ""
    order: Optional[str] = None
    range: str = "standard"
    attack_mod: int = 0
    defense_mod: int = 0
    repair_priority: bool = False

    def __getitem__(self, item: str):
        return getattr(self, item)

    def __setitem__(self, key: str, value):
        setattr(self, key, value)
