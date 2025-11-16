"""Textual user interface for visualising ship combat."""
from __future__ import annotations

import asyncio
from dataclasses import replace
from typing import Dict, List, Optional

from textual import on
from textual.app import App, ComposeResult, ScreenStackError
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.events import ScreenResume
from textual.screen import Screen
from textual.widgets import Log, Static

from ..battle_map import BattleMap
from ..models import Ship
from .snapshots import BattleSnapshot, SnapshotFeed, StaticSnapshotFeed


class _ScreenBase(Screen):
    """Common functionality for screens that consume snapshots."""

    def update_snapshot(self, snapshot: BattleSnapshot) -> None:  # pragma: no cover - interface hook
        raise NotImplementedError

    def on_mount(self) -> None:
        self._refresh_from_app()

    @on(ScreenResume)
    def _on_resume(self, _: ScreenResume) -> None:
        self._refresh_from_app()

    def _refresh_from_app(self) -> None:
        snapshot = getattr(self.app, "latest_snapshot", None)
        if snapshot is not None:
            self.update_snapshot(snapshot)


class TacticalScreen(_ScreenBase):
    """Screen showing the ASCII map as well as the rendered legend."""

    def __init__(self) -> None:
        super().__init__()
        self._map_renderer = BattleMap(width=60, height=24)
        self._map_widget: Optional[Static] = None
        self._legend_widget: Optional[Static] = None

    def compose(self) -> ComposeResult:
        with Vertical(id="tactical-layout"):
            yield Static("Tactical Overview", id="tactical-title")
            self._map_widget = Static("Awaiting data…", id="battle-map")
            yield self._map_widget
            self._legend_widget = Static("Legend pending", id="battle-legend")
            yield self._legend_widget

    def update_snapshot(self, snapshot: BattleSnapshot) -> None:
        if not snapshot.fleet_a and not snapshot.fleet_b:
            placeholder = "No ships to display"
            if self._map_widget:
                self._map_widget.update(placeholder)
            if self._legend_widget:
                self._legend_widget.update(placeholder)
            return
        if self._map_widget:
            map_text = self._map_renderer.render_top_down(snapshot.fleet_a, snapshot.fleet_b)
            self._map_widget.update(map_text)
        if self._legend_widget:
            legend_text = self._map_renderer.render_legend(snapshot.fleet_a, snapshot.fleet_b)
            self._legend_widget.update(legend_text)


class ShipDetailScreen(_ScreenBase):
    """Screen focusing on statistics for a single ship."""

    def __init__(self) -> None:
        super().__init__()
        self._detail_widget: Optional[Static] = None

    def compose(self) -> ComposeResult:
        with Container(id="ship-detail"):
            yield Static("Ship Detail", id="ship-detail-title")
            self._detail_widget = Static("Select a ship to view details.", id="ship-detail-panel")
            yield self._detail_widget

    def _render_ship(self, ship: Ship) -> str:
        systems = ", ".join(f"{name}:{sys.status}" for name, sys in ship.systems.items()) or "No systems listed"
        return (
            f"Ship: {ship.name} ({ship.class_name})\n"
            f"Hull: {ship.hull}  Shield: {ship.shield}/{ship.max_shield}\n"
            f"Position: ({ship.x:.1f}, {ship.y:.1f}, {ship.z:.1f})\n"
            f"Heading: {ship.heading:.1f}°  Pitch: {ship.pitch:.1f}°\n"
            f"Crew: {ship.crew}  Leadership: {ship.leadership}\n"
            f"Systems: {systems}"
        )

    def update_snapshot(self, snapshot: BattleSnapshot) -> None:
        ship = snapshot.selected_ship
        if ship is None:
            # fall back to the first available operational ship
            operational = [s for s in snapshot.fleet_a + snapshot.fleet_b if s.hull > 0]
            ship = operational[0] if operational else None
        if self._detail_widget is None:
            return
        if ship is None:
            self._detail_widget.update("No operational ships available.")
        else:
            self._detail_widget.update(self._render_ship(ship))


class BattleLogScreen(_ScreenBase):
    """Screen showing the event log."""

    def __init__(self) -> None:
        super().__init__()
        self._log_widget: Optional[Log] = None

    def compose(self) -> ComposeResult:
        with Container(id="battle-log"):
            yield Static("Battle Log", id="battle-log-title")
            self._log_widget = Log(id="log-widget")
            yield self._log_widget

    def update_snapshot(self, snapshot: BattleSnapshot) -> None:
        if self._log_widget is None:
            return
        self._log_widget.clear()
        if not snapshot.log_lines:
            self._log_widget.write_line("No battle events reported yet.")
            return
        for line in snapshot.log_lines:
            self._log_widget.write_line(line)


class SummaryScreen(_ScreenBase):
    """Screen showing summary statistics."""

    def __init__(self) -> None:
        super().__init__()
        self._summary_widget: Optional[Static] = None

    def compose(self) -> ComposeResult:
        with Container(id="battle-summary"):
            yield Static("Battle Summary", id="summary-title")
            self._summary_widget = Static("Summary will appear here.", id="summary-panel")
            yield self._summary_widget

    def update_snapshot(self, snapshot: BattleSnapshot) -> None:
        if self._summary_widget is None:
            return
        round_info = f"Round {snapshot.round_number}" if snapshot.round_number else "Awaiting first round"
        summary = f"{round_info}\n\n{snapshot.summary_text()}"
        self._summary_widget.update(summary)


class BattleApp(App):
    """Textual UI application wiring multiple screens together."""

    CSS = """
    #tactical-layout {
        padding: 1 2;
        height: 1fr;
        overflow: auto;
    }

    #battle-map {
        min-height: 10;
        padding: 1;
        border: round #666;
        overflow: auto;
    }

    #battle-legend {
        min-height: 5;
        padding: 1;
        border: round #444;
        overflow: auto;
    }

    #ship-detail, #battle-summary, #battle-log {
        padding: 1;
    }

    #ship-detail-panel, #summary-panel {
        border: solid #555;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("t", "show_tactical", "Tactical"),
        Binding("s", "show_ship_detail", "Ship Detail"),
        Binding("l", "show_log", "Battle Log"),
        Binding("m", "show_summary", "Summary"),
        Binding("]", "select_next_ship", "Next Ship", show=False),
        Binding("[", "select_previous_ship", "Previous Ship", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, snapshot_feed: Optional[SnapshotFeed] = None) -> None:
        super().__init__()
        self.snapshot_feed = snapshot_feed or StaticSnapshotFeed([])
        self._snapshot_task: Optional[asyncio.Task[None]] = None
        self.latest_snapshot: Optional[BattleSnapshot] = None
        self._latest_raw_snapshot: Optional[BattleSnapshot] = None
        self._screens: Dict[str, _ScreenBase] = {}
        self._has_active_screen = False
        self._selected_ship_name: Optional[str] = None

    def on_mount(self) -> None:
        self._screens = {
            "tactical": TacticalScreen(),
            "ship-detail": ShipDetailScreen(),
            "battle-log": BattleLogScreen(),
            "summary": SummaryScreen(),
        }
        for name, screen in self._screens.items():
            self.install_screen(screen, name=name)
        self._activate_screen("tactical")
        self._snapshot_task = asyncio.create_task(self._consume_snapshots())

    async def _consume_snapshots(self) -> None:
        async for snapshot in self.snapshot_feed:
            self._latest_raw_snapshot = snapshot
            self._sync_selection_from_snapshot(snapshot)
            self.latest_snapshot = self._apply_selection(snapshot)
            self._update_screens_with_snapshot(self.latest_snapshot)

    def _sync_selection_from_snapshot(self, snapshot: BattleSnapshot) -> None:
        if snapshot.selected_ship is not None:
            self._selected_ship_name = snapshot.selected_ship.name
            return
        if self._selected_ship_name is not None:
            if not any(
                ship.name == self._selected_ship_name and ship.hull > 0
                for ship in snapshot.fleet_a + snapshot.fleet_b
            ):
                self._selected_ship_name = None

    def _update_screens_with_snapshot(self, snapshot: BattleSnapshot) -> None:
        for screen in self._screens.values():
            if screen.is_mounted:
                screen.update_snapshot(snapshot)

    def _resolve_selected_ship(self, snapshot: BattleSnapshot) -> Optional[Ship]:
        ships: List[Ship] = snapshot.fleet_a + snapshot.fleet_b
        if self._selected_ship_name:
            for ship in ships:
                if ship.name == self._selected_ship_name and ship.hull > 0:
                    return ship
        if snapshot.selected_ship and snapshot.selected_ship.hull > 0:
            return snapshot.selected_ship
        for ship in ships:
            if ship.hull > 0:
                return ship
        return None

    def _apply_selection(self, snapshot: BattleSnapshot) -> BattleSnapshot:
        selected = self._resolve_selected_ship(snapshot)
        if selected is snapshot.selected_ship:
            return snapshot
        if selected is None and snapshot.selected_ship is None:
            return snapshot
        return replace(snapshot, selected_ship=selected)

    def _select_ship_by_offset(self, offset: int) -> None:
        if self._latest_raw_snapshot is None:
            return
        ships = [
            ship
            for ship in self._latest_raw_snapshot.fleet_a + self._latest_raw_snapshot.fleet_b
            if ship.hull > 0
        ]
        if not ships:
            self._selected_ship_name = None
            return
        names = [ship.name for ship in ships]
        if self._selected_ship_name in names:
            idx = names.index(self._selected_ship_name)
        else:
            idx = 0 if offset >= 0 else len(names) - 1
        idx = (idx + offset) % len(names)
        self._selected_ship_name = names[idx]
        self.latest_snapshot = self._apply_selection(self._latest_raw_snapshot)
        self._update_screens_with_snapshot(self.latest_snapshot)

    def _activate_screen(self, name: str) -> None:
        if not self._has_active_screen:
            self.push_screen(name)
            self._has_active_screen = True
            return
        try:
            self.switch_screen(name)
        except ScreenStackError:
            self.push_screen(name)

    def on_unmount(self) -> None:
        if self._snapshot_task and not self._snapshot_task.done():
            self._snapshot_task.cancel()

    def action_show_tactical(self) -> None:
        self._activate_screen("tactical")

    def action_show_ship_detail(self) -> None:
        self._activate_screen("ship-detail")

    def action_show_log(self) -> None:
        self._activate_screen("battle-log")

    def action_show_summary(self) -> None:
        self._activate_screen("summary")

    def action_select_next_ship(self) -> None:
        self._select_ship_by_offset(1)

    def action_select_previous_ship(self) -> None:
        self._select_ship_by_offset(-1)


__all__ = [
    "BattleApp",
    "BattleLogScreen",
    "ShipDetailScreen",
    "SummaryScreen",
    "TacticalScreen",
]
