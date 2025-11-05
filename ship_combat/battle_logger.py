"""Structured logging system for ship combat battles."""

from __future__ import annotations
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .models import Ship


@dataclass
class BattleEvent:
    """Single battle event record."""
    round_num: int
    phase: str
    timestamp: str
    event_type: str
    message: str
    ship: Optional[str] = None
    target: Optional[str] = None
    damage: int = 0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BattleStatistics:
    """Comprehensive battle statistics tracker."""

    # Round tracking
    rounds_fought: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    # Fleet A stats
    fleet_a_ships_destroyed: int = 0
    fleet_a_total_damage_dealt: int = 0
    fleet_a_total_damage_taken: int = 0
    fleet_a_shots_fired: int = 0
    fleet_a_shots_hit: int = 0
    fleet_a_critical_hits: int = 0
    fleet_a_missiles_fired: int = 0

    # Fleet B stats
    fleet_b_ships_destroyed: int = 0
    fleet_b_total_damage_dealt: int = 0
    fleet_b_total_damage_taken: int = 0
    fleet_b_shots_fired: int = 0
    fleet_b_shots_hit: int = 0
    fleet_b_critical_hits: int = 0
    fleet_b_missiles_fired: int = 0

    # Combat events
    boarding_attempts: int = 0
    boarding_successes: int = 0
    hazards_encountered: int = 0
    systems_repaired: int = 0
    weapons_overheated: int = 0

    # Per-ship tracking
    ship_damage_dealt: Dict[str, int] = field(default_factory=dict)
    ship_damage_taken: Dict[str, int] = field(default_factory=dict)
    ship_kills: Dict[str, int] = field(default_factory=dict)

    def get_accuracy(self, fleet: str = 'a') -> float:
        """Calculate accuracy percentage for a fleet."""
        if fleet.lower() == 'a':
            if self.fleet_a_shots_fired == 0:
                return 0.0
            return (self.fleet_a_shots_hit / self.fleet_a_shots_fired) * 100
        else:
            if self.fleet_b_shots_fired == 0:
                return 0.0
            return (self.fleet_b_shots_hit / self.fleet_b_shots_fired) * 100

    def get_critical_rate(self, fleet: str = 'a') -> float:
        """Calculate critical hit rate for a fleet."""
        if fleet.lower() == 'a':
            if self.fleet_a_shots_hit == 0:
                return 0.0
            return (self.fleet_a_critical_hits / self.fleet_a_shots_hit) * 100
        else:
            if self.fleet_b_shots_hit == 0:
                return 0.0
            return (self.fleet_b_critical_hits / self.fleet_b_shots_hit) * 100


class BattleLogger:
    """Comprehensive battle logging system."""

    def __init__(self, log_level: int = logging.INFO, log_to_file: bool = False,
                 filename: Optional[str] = None):
        """
        Initialize battle logger.

        Args:
            log_level: Python logging level (DEBUG, INFO, WARNING, ERROR)
            log_to_file: Whether to log to file in addition to stdout
            filename: Log file name (auto-generated if None)
        """
        self.log_level = log_level
        self.events: List[BattleEvent] = []
        self.stats = BattleStatistics()

        # Setup Python logging
        self.logger = logging.getLogger('ship_combat')
        self.logger.setLevel(log_level)

        # Clear existing handlers
        self.logger.handlers = []

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler (if requested)
        if log_to_file:
            if filename is None:
                filename = f"battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(filename)
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        # Fleet tracking
        self.fleet_a_names: List[str] = []
        self.fleet_b_names: List[str] = []

    def start_battle(self, fleet_a: List[Ship], fleet_b: List[Ship]) -> None:
        """Initialize battle logging."""
        self.stats.start_time = datetime.now().isoformat()
        self.fleet_a_names = [s.name for s in fleet_a]
        self.fleet_b_names = [s.name for s in fleet_b]

        self.logger.info("=" * 80)
        self.logger.info("BATTLE COMMENCED")
        self.logger.info("=" * 80)
        self.logger.info(f"Fleet A: {', '.join(self.fleet_a_names)}")
        self.logger.info(f"Fleet B: {', '.join(self.fleet_b_names)}")
        self.logger.info("=" * 80)

        # Initialize ship stats
        for ship in fleet_a + fleet_b:
            self.stats.ship_damage_dealt[ship.name] = 0
            self.stats.ship_damage_taken[ship.name] = 0
            self.stats.ship_kills[ship.name] = 0

    def end_battle(self) -> None:
        """Finalize battle logging."""
        self.stats.end_time = datetime.now().isoformat()
        self.logger.info("\n" + "=" * 80)
        self.logger.info("BATTLE CONCLUDED")
        self.logger.info("=" * 80)

    def log_round_start(self, round_num: int) -> None:
        """Log start of combat round."""
        self.stats.rounds_fought = round_num
        self.logger.info("\n" + "=" * 80)
        self.logger.info(f"ROUND {round_num}")
        self.logger.info("=" * 80)

    def log_phase(self, phase: str) -> None:
        """Log start of battle phase."""
        self.logger.debug(f"\n--- {phase} ---")

    def log_order_selection(self, ship: Ship, order: str) -> None:
        """Log ship order selection."""
        event = BattleEvent(
            round_num=self.stats.rounds_fought,
            phase="Order Selection",
            timestamp=datetime.now().isoformat(),
            event_type="order",
            message=f"{ship.name} selects order: {order}",
            ship=ship.name,
            details={"order": order}
        )
        self.events.append(event)
        self.logger.info(f"{ship.name} selects order: {order}")

    def log_movement(self, ship: Ship, old_x: float, old_y: float, old_z: float) -> None:
        """Log ship movement."""
        distance = ((ship.x - old_x)**2 + (ship.y - old_y)**2 + (ship.z - old_z)**2)**0.5
        self.logger.debug(
            f"{ship.name} moves {distance:.1f} units to ({ship.x:.1f}, {ship.y:.1f}, {ship.z:.1f})"
        )

    def log_shot(self, attacker: Ship, target: Ship, battery_name: str,
                 hit: bool, damage: int = 0, critical: bool = False) -> None:
        """Log weapon fire."""
        fleet = 'a' if attacker.name in self.fleet_a_names else 'b'

        # Update stats
        if fleet == 'a':
            self.stats.fleet_a_shots_fired += 1
            if hit:
                self.stats.fleet_a_shots_hit += 1
                self.stats.fleet_a_total_damage_dealt += damage
                if critical:
                    self.stats.fleet_a_critical_hits += 1
        else:
            self.stats.fleet_b_shots_fired += 1
            if hit:
                self.stats.fleet_b_shots_hit += 1
                self.stats.fleet_b_total_damage_dealt += damage
                if critical:
                    self.stats.fleet_b_critical_hits += 1

        # Update per-ship stats
        if hit:
            self.stats.ship_damage_dealt[attacker.name] = \
                self.stats.ship_damage_dealt.get(attacker.name, 0) + damage
            self.stats.ship_damage_taken[target.name] = \
                self.stats.ship_damage_taken.get(target.name, 0) + damage

            # Track fleet damage taken
            target_fleet = 'a' if target.name in self.fleet_a_names else 'b'
            if target_fleet == 'a':
                self.stats.fleet_a_total_damage_taken += damage
            else:
                self.stats.fleet_b_total_damage_taken += damage

        # Log event
        if hit:
            hit_type = "CRITICAL HIT" if critical else "hits"
            self.logger.info(
                f"{attacker.name} {hit_type} {target.name} with {battery_name} "
                f"for {damage} damage (Hull: {target.hull})"
            )
        else:
            self.logger.debug(f"{attacker.name} misses {target.name} with {battery_name}")

        event = BattleEvent(
            round_num=self.stats.rounds_fought,
            phase="Shooting",
            timestamp=datetime.now().isoformat(),
            event_type="shot_critical" if critical else ("shot_hit" if hit else "shot_miss"),
            message=f"{attacker.name} fires at {target.name}",
            ship=attacker.name,
            target=target.name,
            damage=damage,
            details={"battery": battery_name, "critical": critical}
        )
        self.events.append(event)

    def log_ship_destroyed(self, ship: Ship, killer: Optional[Ship] = None) -> None:
        """Log ship destruction."""
        fleet = 'a' if ship.name in self.fleet_a_names else 'b'

        if fleet == 'a':
            self.stats.fleet_a_ships_destroyed += 1
        else:
            self.stats.fleet_b_ships_destroyed += 1

        if killer:
            self.stats.ship_kills[killer.name] = self.stats.ship_kills.get(killer.name, 0) + 1

        self.logger.warning(f"*** {ship.name} DESTROYED ***")

        event = BattleEvent(
            round_num=self.stats.rounds_fought,
            phase="Combat",
            timestamp=datetime.now().isoformat(),
            event_type="ship_destroyed",
            message=f"{ship.name} destroyed",
            ship=ship.name,
            target=killer.name if killer else None
        )
        self.events.append(event)

    def log_missile_launch(self, attacker: Ship, target: Ship, damage: int) -> None:
        """Log missile launch."""
        fleet = 'a' if attacker.name in self.fleet_a_names else 'b'

        if fleet == 'a':
            self.stats.fleet_a_missiles_fired += 1
            self.stats.fleet_a_total_damage_dealt += damage
        else:
            self.stats.fleet_b_missiles_fired += 1
            self.stats.fleet_b_total_damage_dealt += damage

        # Update per-ship stats
        self.stats.ship_damage_dealt[attacker.name] = \
            self.stats.ship_damage_dealt.get(attacker.name, 0) + damage
        self.stats.ship_damage_taken[target.name] = \
            self.stats.ship_damage_taken.get(target.name, 0) + damage

        # Update fleet-level damage taken for the target fleet
        target_fleet = 'a' if target.name in self.fleet_a_names else 'b'
        if target_fleet == 'a':
            self.stats.fleet_a_total_damage_taken += damage
        else:
            self.stats.fleet_b_total_damage_taken += damage
        self.logger.info(
            f"{attacker.name} launches missile at {target.name} for {damage} damage (Hull: {target.hull})"
        )

        event = BattleEvent(
            round_num=self.stats.rounds_fought,
            phase="Missiles",
            timestamp=datetime.now().isoformat(),
            event_type="missile",
            message=f"{attacker.name} launches missile at {target.name}",
            ship=attacker.name,
            target=target.name,
            damage=damage
        )
        self.events.append(event)

    def log_boarding(self, attacker: Ship, target: Ship, success: bool, damage: int = 0) -> None:
        """Log boarding action."""
        self.stats.boarding_attempts += 1
        if success:
            self.stats.boarding_successes += 1
            # Track damage statistics for successful boarding
            if damage > 0:
                fleet = 'a' if attacker.name in self.fleet_a_names else 'b'
                if fleet == 'a':
                    self.stats.fleet_a_total_damage_dealt += damage
                else:
                    self.stats.fleet_b_total_damage_dealt += damage
                self.stats.ship_damage_dealt[attacker.name] = \
                    self.stats.ship_damage_dealt.get(attacker.name, 0) + damage
                self.stats.ship_damage_taken[target.name] = \
                    self.stats.ship_damage_taken.get(target.name, 0) + damage
            self.logger.info(f"{attacker.name} boards {target.name} for {damage} damage")
        else:
            self.logger.debug(f"{attacker.name} fails to board {target.name}")

        event = BattleEvent(
            round_num=self.stats.rounds_fought,
            phase="Boarding",
            timestamp=datetime.now().isoformat(),
            event_type="boarding_success" if success else "boarding_fail",
            message=f"{attacker.name} attempts to board {target.name}",
            ship=attacker.name,
            target=target.name,
            damage=damage
        )
        self.events.append(event)

    def log_hazard(self, ship: Ship, hazard: str, effect: str) -> None:
        """Log environmental hazard."""
        self.stats.hazards_encountered += 1
        self.logger.warning(f"{ship.name} encounters hazard: {hazard} - {effect}")

        event = BattleEvent(
            round_num=self.stats.rounds_fought,
            phase="Hazards",
            timestamp=datetime.now().isoformat(),
            event_type="hazard",
            message=f"{ship.name} encounters {hazard}",
            ship=ship.name,
            details={"hazard": hazard, "effect": effect}
        )
        self.events.append(event)

    def log_repair(self, ship: Ship, system: str, efficiency: int) -> None:
        """Log system repair."""
        self.stats.systems_repaired += 1
        self.logger.debug(f"{ship.name} repairs {system} to {efficiency}%")

    def log_overheat(self, ship: Ship, battery_name: str) -> None:
        """Log weapon overheat."""
        self.stats.weapons_overheated += 1
        self.logger.warning(f"{ship.name}'s {battery_name} overheats!")

    def log_shield_regen(self, ship: Ship, old_shield: int, new_shield: int) -> None:
        """Log shield regeneration."""
        self.logger.debug(f"{ship.name} regenerates shields: {old_shield} -> {new_shield}")

    def generate_report(self) -> str:
        """Generate comprehensive battle report."""
        lines = []

        lines.append("\n" + "=" * 80)
        lines.append("BATTLE REPORT")
        lines.append("=" * 80)

        # Battle summary
        lines.append(f"\nRounds Fought: {self.stats.rounds_fought}")
        lines.append(f"Duration: {self.stats.start_time} to {self.stats.end_time}")

        # Fleet A statistics
        lines.append("\n--- FLEET A STATISTICS ---")
        lines.append(f"Ships Destroyed (Fleet A): {self.stats.fleet_a_ships_destroyed}")
        lines.append(f"Total Damage Dealt: {self.stats.fleet_a_total_damage_dealt}")
        lines.append(f"Total Damage Taken: {self.stats.fleet_a_total_damage_taken}")
        lines.append(f"Accuracy: {self.stats.get_accuracy('a'):.1f}% ({self.stats.fleet_a_shots_hit}/{self.stats.fleet_a_shots_fired})")
        lines.append(f"Critical Hit Rate: {self.stats.get_critical_rate('a'):.1f}%")
        lines.append(f"Missiles Fired: {self.stats.fleet_a_missiles_fired}")

        # Fleet B statistics
        lines.append("\n--- FLEET B STATISTICS ---")
        lines.append(f"Ships Destroyed (Fleet B): {self.stats.fleet_b_ships_destroyed}")
        lines.append(f"Total Damage Dealt: {self.stats.fleet_b_total_damage_dealt}")
        lines.append(f"Total Damage Taken: {self.stats.fleet_b_total_damage_taken}")
        lines.append(f"Accuracy: {self.stats.get_accuracy('b'):.1f}% ({self.stats.fleet_b_shots_hit}/{self.stats.fleet_b_shots_fired})")
        lines.append(f"Critical Hit Rate: {self.stats.get_critical_rate('b'):.1f}%")
        lines.append(f"Missiles Fired: {self.stats.fleet_b_missiles_fired}")

        # Combat events
        lines.append("\n--- COMBAT EVENTS ---")
        lines.append(f"Boarding Attempts: {self.stats.boarding_attempts} (Success: {self.stats.boarding_successes})")
        lines.append(f"Hazards Encountered: {self.stats.hazards_encountered}")
        lines.append(f"Systems Repaired: {self.stats.systems_repaired}")
        lines.append(f"Weapons Overheated: {self.stats.weapons_overheated}")

        # Top performers
        lines.append("\n--- TOP PERFORMERS ---")
        if self.stats.ship_damage_dealt:
            top_damage = max(self.stats.ship_damage_dealt.items(), key=lambda x: x[1])
            lines.append(f"Most Damage Dealt: {top_damage[0]} ({top_damage[1]} HP)")

        if self.stats.ship_kills:
            top_kills = max(self.stats.ship_kills.items(), key=lambda x: x[1])
            lines.append(f"Most Kills: {top_kills[0]} ({top_kills[1]} ships)")

        lines.append("=" * 80)

        return '\n'.join(lines)

    def get_events_by_phase(self, phase: str) -> List[BattleEvent]:
        """Get all events from a specific phase."""
        return [e for e in self.events if e.phase == phase]

    def get_events_by_ship(self, ship_name: str) -> List[BattleEvent]:
        """Get all events involving a specific ship."""
        return [e for e in self.events if e.ship == ship_name or e.target == ship_name]
