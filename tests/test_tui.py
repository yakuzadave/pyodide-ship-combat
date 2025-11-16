import asyncio

from ship_combat.models import Ship, WeaponSystem
from ship_combat.tui import BattleApp, BattleSnapshot, StaticSnapshotFeed
from textual.widgets import Static


def make_ship(name: str) -> Ship:
    return Ship(
        name=name,
        hull=40,
        shield=30,
        weapons=WeaponSystem(),
        crew=90,
        leadership=8,
        boarding_strength=5,
    )


def test_battle_app_renders_snapshot() -> None:
    alpha = make_ship("Alpha")
    beta = make_ship("Beta")
    snapshot = BattleSnapshot(
        round_number=1,
        fleet_a=[alpha],
        fleet_b=[beta],
        log_lines=["Alpha fires on Beta"],
        selected_ship=alpha,
        summary_lines=["Alpha draws first blood"],
    )
    feed = StaticSnapshotFeed([snapshot])

    async def _run() -> None:
        async with BattleApp(feed).run_test() as pilot:
            await pilot.pause()
            tactical = pilot.app.get_screen("tactical")
            legend = tactical.query_one("#battle-legend", Static)
            assert "Alpha" in str(legend.render())

            pilot.app.action_show_summary()
            await pilot.pause()
            summary_screen = pilot.app.get_screen("summary")
            summary = summary_screen.query_one("#summary-panel", Static)
            assert "Round 1" in str(summary.render())

    asyncio.run(_run())
