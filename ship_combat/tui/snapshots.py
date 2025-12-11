"""Snapshot controller utilities for the Textual battle UI."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import AsyncIterator, Iterable, List, Optional, Sequence

from ..models import Ship


@dataclass
class BattleSnapshot:
    """Container describing the state of a battle phase for the UI."""

    round_number: int
    fleet_a: List[Ship]
    fleet_b: List[Ship]
    log_lines: Sequence[str] = field(default_factory=list)
    selected_ship: Optional[Ship] = None
    summary_lines: Sequence[str] = field(default_factory=list)

    def summary_text(self) -> str:
        """Return the summary as a newline separated string."""
        if not self.summary_lines:
            return "No summary available yet."
        return "\n".join(self.summary_lines)


class SnapshotFeed:
    """Abstract async iterable for supplying :class:`BattleSnapshot` objects."""

    def __aiter__(self) -> AsyncIterator[BattleSnapshot]:  # pragma: no cover - interface
        raise NotImplementedError


class StaticSnapshotFeed(SnapshotFeed):
    """Simple feed that replays a fixed collection of snapshots."""

    def __init__(self, snapshots: Iterable[BattleSnapshot], interval: float = 0.0) -> None:
        self._snapshots = list(snapshots)
        self._interval = interval

    async def __aiter__(self) -> AsyncIterator[BattleSnapshot]:
        for snapshot in self._snapshots:
            if self._interval:
                await asyncio.sleep(self._interval)
            yield snapshot


__all__ = ["BattleSnapshot", "SnapshotFeed", "StaticSnapshotFeed"]
