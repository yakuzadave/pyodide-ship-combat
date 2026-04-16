"""Battle snapshot controller for incremental updates.

This module provides lightweight dataclasses that capture the state of a
battle after each phase.  The resulting snapshots are designed to be sent to
front-end clients (e.g., a Pyodide UI) without exposing mutable `Ship`
instances.  Instead, a turn is represented by a :class:`BattleSnapshot` that
contains a series of :class:`PhaseSnapshot` entries produced by the
:class:`BattleSnapshotController`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple

from .models import Ship


class FrozenDict(dict):
    """JSON-serializable immutable mapping used inside snapshots."""

    def __init__(self, mapping: Mapping | None = None):
        super().__init__(mapping or {})

    def _immutable(self, *args: object, **kwargs: object) -> None:
        raise TypeError("FrozenDict is immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable


@dataclass(frozen=True)
class ShipSnapshot:
    """Immutable view of a single ship used for serialization."""

    name: str
    class_name: str
    hull: int
    shield: int
    crew: int
    leadership: int
    position: Tuple[float, float, float]
    heading: float
    pitch: float
    order: Optional[str]
    status: str

    @classmethod
    def from_ship(cls, ship: Ship) -> "ShipSnapshot":
        status = "Destroyed" if ship.hull <= 0 else "Operational"
        if ship.shield <= 0 and ship.hull > 0:
            status = "Shields Down"
        return cls(
            name=ship.name,
            class_name=ship.class_name,
            hull=ship.hull,
            shield=ship.shield,
            crew=ship.crew,
            leadership=ship.leadership,
            position=(ship.x, ship.y, ship.z),
            heading=ship.heading,
            pitch=ship.pitch,
            order=ship.order,
            status=status,
        )


@dataclass(frozen=True)
class FleetSnapshot:
    """Collection of ship snapshots for a single fleet."""

    name: str
    ships: Tuple[ShipSnapshot, ...] = field(default_factory=tuple)

    @classmethod
    def from_fleet(cls, name: str, ships: Sequence[Ship]) -> "FleetSnapshot":
        return cls(
            name=name,
            ships=tuple(ShipSnapshot.from_ship(ship) for ship in ships),
        )


@dataclass(frozen=True)
class PhaseSnapshot:
    """Snapshot produced after a specific battle phase."""

    turn: int
    phase_name: str
    fleets: Mapping[str, FleetSnapshot] = field(default_factory=FrozenDict)
    new_events: Tuple[str, ...] = field(default_factory=tuple)

    def summary(self) -> Dict[str, int]:
        """Return lightweight counts that UI layers can display quickly."""
        return {name: len(fleet.ships) for name, fleet in self.fleets.items()}


@dataclass
class BattleSnapshot:
    """Container storing all phase snapshots for a turn."""

    turn: int
    phases: List[PhaseSnapshot] = field(default_factory=list)

    def add_phase(self, phase: PhaseSnapshot) -> None:
        if phase.turn != self.turn:
            raise ValueError("Phase snapshot turn does not match battle snapshot")
        self.phases.append(phase)

    def latest_events(self) -> List[str]:
        """Return the concatenation of phase events for this turn."""
        events: List[str] = []
        for phase in self.phases:
            events.extend(phase.new_events)
        return events


class BattleSnapshotController:
    """Controller that generates incremental battle updates."""

    def __init__(self) -> None:
        self.turn_history: List[BattleSnapshot] = []
        self._current_turn: Optional[BattleSnapshot] = None

    def begin_turn(self, turn: int) -> BattleSnapshot:
        """Start a new turn and reset the current turn snapshot."""
        if self._current_turn is not None:
            raise RuntimeError("Previous turn not finalized")
        self._current_turn = BattleSnapshot(turn=turn)
        return self._current_turn

    def record_phase(
        self,
        phase_name: str,
        fleets: Mapping[str, Sequence[Ship]],
        events: Optional[Iterable[str]] = None,
    ) -> PhaseSnapshot:
        """Record the outcome of a phase for the active turn."""
        if self._current_turn is None:
            raise RuntimeError("No active turn. Call begin_turn first.")
        fleet_snapshots = FrozenDict(
            {
                name: FleetSnapshot.from_fleet(name, list(fleet))
                for name, fleet in fleets.items()
            }
        )
        phase_snapshot = PhaseSnapshot(
            turn=self._current_turn.turn,
            phase_name=phase_name,
            fleets=fleet_snapshots,
            new_events=tuple(events or ()),
        )
        self._current_turn.add_phase(phase_snapshot)
        return phase_snapshot

    def end_turn(self) -> BattleSnapshot:
        """Finalize the current turn and store it in the history."""
        if self._current_turn is None:
            raise RuntimeError("No active turn to finalize")
        finished_turn = self._current_turn
        self.turn_history.append(finished_turn)
        self._current_turn = None
        return finished_turn

    def iter_history(self) -> Iterator[BattleSnapshot]:
        """Iterate over the finished turns in chronological order."""
        return iter(self.turn_history)

    def latest_turn(self) -> Optional[BattleSnapshot]:
        """Return the most recently finalized turn, if any."""
        return self.turn_history[-1] if self.turn_history else None
