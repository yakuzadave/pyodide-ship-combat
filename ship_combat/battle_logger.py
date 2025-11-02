"""Battle event logging and visualization system."""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import math


@dataclass
class BattleEvent:
    """Single event during battle."""

    round: int
    phase: str
    event_type: str
    ship_name: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_text(self) -> str:
        """Convert to human-readable text."""
        details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
        return f"[Round {self.round}] {self.phase} - {self.event_type}: {self.ship_name} ({details_str})"


@dataclass
class RoundSummary:
    """Summary of a battle round."""

    round: int
    events: List[BattleEvent] = field(default_factory=list)
    ships_destroyed: List[str] = field(default_factory=list)
    total_damage_dealt: int = 0
    total_shots_fired: int = 0
    total_hits: int = 0
    total_misses: int = 0
    critical_hits: int = 0

    def accuracy(self) -> float:
        """Calculate hit accuracy for this round."""
        if self.total_shots_fired == 0:
            return 0.0
        return (self.total_hits / self.total_shots_fired) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "round": self.round,
            "events": [e.to_dict() for e in self.events],
            "ships_destroyed": self.ships_destroyed,
            "total_damage_dealt": self.total_damage_dealt,
            "total_shots_fired": self.total_shots_fired,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "critical_hits": self.critical_hits,
            "accuracy": self.accuracy(),
        }


class BattleLogger:
    """Comprehensive battle event logger."""

    def __init__(self, verbose: bool = True):
        self.events: List[BattleEvent] = []
        self.round_summaries: List[RoundSummary] = []
        self.current_round: Optional[RoundSummary] = None
        self.verbose = verbose
        self.start_time = datetime.now()

    def start_round(self, round_num: int) -> None:
        """Start a new round."""
        if self.current_round:
            self.round_summaries.append(self.current_round)
        self.current_round = RoundSummary(round=round_num)

    def log_event(self, phase: str, event_type: str, ship_name: str, **details) -> None:
        """Log a battle event."""
        if self.current_round is None:
            self.start_round(1)

        event = BattleEvent(
            round=self.current_round.round,
            phase=phase,
            event_type=event_type,
            ship_name=ship_name,
            details=details
        )

        self.events.append(event)
        self.current_round.events.append(event)

        if self.verbose:
            print(event.to_text())

    def log_order(self, ship_name: str, order: str) -> None:
        """Log order selection."""
        self.log_event("orders", "order_selected", ship_name, order=order)

    def log_movement(self, ship_name: str, old_x: float, old_y: float, new_x: float, new_y: float, heading: float) -> None:
        """Log ship movement."""
        distance = math.sqrt((new_x - old_x)**2 + (new_y - old_y)**2)
        self.log_event("movement", "ship_moved", ship_name,
                      from_x=round(old_x, 2), from_y=round(old_y, 2),
                      to_x=round(new_x, 2), to_y=round(new_y, 2),
                      distance=round(distance, 2), heading=round(heading, 1))

    def log_shot(self, attacker: str, target: str, weapon: str, hit: bool, damage: int = 0, critical: bool = False) -> None:
        """Log a weapon shot."""
        if self.current_round:
            self.current_round.total_shots_fired += 1
            if hit:
                self.current_round.total_hits += 1
                self.current_round.total_damage_dealt += damage
                if critical:
                    self.current_round.critical_hits += 1
            else:
                self.current_round.total_misses += 1

        event_type = "critical_hit" if critical else ("hit" if hit else "miss")
        self.log_event("shooting", event_type, attacker,
                      target=target, weapon=weapon, damage=damage)

    def log_missile(self, attacker: str, target: str, damage: int) -> None:
        """Log missile launch."""
        if self.current_round:
            self.current_round.total_shots_fired += 1
            self.current_round.total_hits += 1
            self.current_round.total_damage_dealt += damage

        self.log_event("missiles", "missile_hit", attacker, target=target, damage=damage)

    def log_boarding(self, attacker: str, target: str, success: bool, damage: int = 0) -> None:
        """Log boarding attempt."""
        event_type = "boarding_success" if success else "boarding_failed"
        self.log_event("boarding", event_type, attacker, target=target, damage=damage)

        if success and self.current_round:
            self.current_round.total_damage_dealt += damage

    def log_repair(self, ship_name: str, system: str, old_efficiency: int, new_efficiency: int) -> None:
        """Log system repair."""
        self.log_event("repairs", "system_repaired", ship_name,
                      system=system, old_efficiency=old_efficiency, new_efficiency=new_efficiency)

    def log_shield_regen(self, ship_name: str, old_shield: int, new_shield: int) -> None:
        """Log shield regeneration."""
        regen_amount = new_shield - old_shield
        self.log_event("shields", "shield_regenerated", ship_name,
                      old_shield=old_shield, new_shield=new_shield, regenerated=regen_amount)

    def log_heat(self, ship_name: str, weapon: str, heat: int, overheated: bool) -> None:
        """Log weapon heat status."""
        event_type = "weapon_overheated" if overheated else "weapon_heated"
        self.log_event("heat", event_type, ship_name, weapon=weapon, heat=heat)

    def log_critical_system_damage(self, ship_name: str, system: str, efficiency: int) -> None:
        """Log critical hit system damage."""
        self.log_event("critical", "system_damaged", ship_name, system=system, efficiency=efficiency)

    def log_destruction(self, ship_name: str, killed_by: Optional[str] = None) -> None:
        """Log ship destruction."""
        if self.current_round:
            self.current_round.ships_destroyed.append(ship_name)

        self.log_event("combat", "ship_destroyed", ship_name, killed_by=killed_by)

    def log_hazard(self, ship_name: str, hazard_type: str, effect: str) -> None:
        """Log environmental hazard."""
        self.log_event("hazards", hazard_type, ship_name, effect=effect)

    def end_round(self) -> None:
        """End the current round."""
        if self.current_round:
            self.round_summaries.append(self.current_round)
            self.current_round = None

    def get_summary(self) -> Dict[str, Any]:
        """Get overall battle summary."""
        if self.current_round:
            self.end_round()

        total_damage = sum(r.total_damage_dealt for r in self.round_summaries)
        total_shots = sum(r.total_shots_fired for r in self.round_summaries)
        total_hits = sum(r.total_hits for r in self.round_summaries)
        total_critical = sum(r.critical_hits for r in self.round_summaries)

        all_destroyed = []
        for r in self.round_summaries:
            all_destroyed.extend(r.ships_destroyed)

        return {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_rounds": len(self.round_summaries),
            "total_events": len(self.events),
            "total_damage_dealt": total_damage,
            "total_shots_fired": total_shots,
            "total_hits": total_hits,
            "total_misses": total_shots - total_hits,
            "overall_accuracy": (total_hits / total_shots * 100) if total_shots > 0 else 0,
            "critical_hits": total_critical,
            "ships_destroyed": all_destroyed,
            "round_summaries": [r.to_dict() for r in self.round_summaries],
        }

    def export_json(self, filepath: str) -> None:
        """Export battle log to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)

    def export_text(self, filepath: str) -> None:
        """Export battle log to text file."""
        with open(filepath, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("BATTLE LOG\n")
            f.write("=" * 80 + "\n\n")

            for event in self.events:
                f.write(event.to_text() + "\n")

            f.write("\n" + "=" * 80 + "\n")
            f.write("BATTLE SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            summary = self.get_summary()
            f.write(f"Total Rounds: {summary['total_rounds']}\n")
            f.write(f"Total Events: {summary['total_events']}\n")
            f.write(f"Total Damage: {summary['total_damage_dealt']}\n")
            f.write(f"Accuracy: {summary['overall_accuracy']:.1f}%\n")
            f.write(f"Critical Hits: {summary['critical_hits']}\n")
            f.write(f"Ships Destroyed: {', '.join(summary['ships_destroyed']) if summary['ships_destroyed'] else 'None'}\n")

    def print_summary(self) -> None:
        """Print battle summary to console."""
        summary = self.get_summary()

        print("\n" + "=" * 80)
        print("BATTLE SUMMARY")
        print("=" * 80)
        print(f"Duration: {summary['total_rounds']} rounds")
        print(f"Total Events: {summary['total_events']}")
        print(f"Total Damage Dealt: {summary['total_damage_dealt']}")
        print(f"Shots Fired: {summary['total_shots_fired']} (Hits: {summary['total_hits']}, Misses: {summary['total_misses']})")
        print(f"Overall Accuracy: {summary['overall_accuracy']:.1f}%")
        print(f"Critical Hits: {summary['critical_hits']}")

        if summary['ships_destroyed']:
            print(f"\nShips Destroyed: {', '.join(summary['ships_destroyed'])}")
        else:
            print("\nNo ships destroyed")

        print("\nRound-by-Round:")
        for r in self.round_summaries:
            print(f"  Round {r.round}: {r.total_damage_dealt} damage, {r.accuracy():.1f}% accuracy" +
                  (f", {len(r.ships_destroyed)} destroyed" if r.ships_destroyed else ""))

        print("=" * 80)
