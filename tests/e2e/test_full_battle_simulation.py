"""End-to-end battle simulation smoke tests."""

from __future__ import annotations

import logging
import random

from ship_combat.battle_sim import battle
from ship_combat.fleet_setup import demo_fleets, new_ship, system_block
from ship_combat.models import WeaponBattery, WeaponSystem


def _close_range_missile_fleets():
    """Two frigates that immediately trade missiles at short range."""

    def make_ship(name: str, x: float) -> list:
        weapons = WeaponSystem(
            [
                WeaponBattery(
                    "Assault Cannons",
                    rating=4,
                    accuracy=3,
                    damage_dice="2d6",
                    range="short",
                    arc="omni",
                )
            ],
            missiles=2,
        )
        systems = {
            "engines": system_block(90),
            "shields": system_block(85),
        }
        return [
            new_ship(
                name,
                "Frigate",
                hull=60,
                shield=40,
                weapons=weapons,
                missiles=2,
                crew=3,
                leadership=8,
                boarding_strength=2,
                speed=18,
                maneuver=3,
                systems=systems,
                ai="Direct",
                x=x,
                y=0.0,
                z=0.0,
                heading=90.0 if x < 0 else 270.0,
            )
        ]

    return make_ship("Red Comet", -5.0), make_ship("Azure Pike", 5.0)


def _armored_duel_fleets():
    """Durable cruisers that can survive a multi-round slugfest."""

    def make_ship(name: str, heading: float) -> list:
        weapons = WeaponSystem(
            [
                WeaponBattery(
                    "Heavy Lance",
                    rating=5,
                    accuracy=4,
                    damage_dice="2d8",
                    range="standard",
                    arc="omni",
                )
            ],
            missiles=1,
        )
        systems = {
            "engines": system_block(95),
            "reactor": system_block(100),
            "shields": system_block(90),
        }
        return [
            new_ship(
                name,
                "Armored Cruiser",
                hull=180,
                shield=120,
                weapons=weapons,
                missiles=1,
                crew=6,
                leadership=9,
                boarding_strength=4,
                speed=0,
                maneuver=2,
                systems=systems,
                ai="Steady",
                x=0.0,
                y=0.0,
                z=0.0,
                heading=heading,
            )
        ]

    return make_ship("Iron Halberd", 90.0), make_ship("Gilded Bulwark", 270.0)


def test_demo_fleets_complete_battle_without_errors():
    random.seed(2024)
    fleet_a, fleet_b = demo_fleets()

    logger = battle(
        fleet_a,
        fleet_b,
        rounds=2,
        log_level=logging.WARNING,
        show_map=False,
        show_stats=False,
    )

    assert logger is not None
    assert logger.stats.rounds_fought >= 1
    assert logger.stats.end_time is not None
    assert (
        logger.stats.fleet_a_shots_fired + logger.stats.fleet_b_shots_fired
    ) > 0
    assert logger.events, "Battle should record at least one event"


def test_close_range_missile_exchange_tracks_stats():
    random.seed(99)
    fleet_a, fleet_b = _close_range_missile_fleets()

    logger = battle(
        fleet_a,
        fleet_b,
        rounds=2,
        log_level=logging.WARNING,
        show_map=False,
        show_stats=False,
    )

    assert logger is not None
    assert logger.stats.fleet_a_missiles_fired == 2
    assert logger.stats.fleet_b_missiles_fired == 2
    assert logger.stats.ship_damage_taken.get("Red Comet", 0) > 0
    assert logger.stats.ship_damage_taken.get("Azure Pike", 0) > 0

    missile_events = [evt for evt in logger.events if evt.event_type == "missile"]
    assert len(missile_events) >= 2


def test_multi_round_armored_duel_runs_full_length():
    random.seed(1337)
    fleet_a, fleet_b = _armored_duel_fleets()

    logger = battle(
        fleet_a,
        fleet_b,
        rounds=3,
        log_level=logging.WARNING,
        show_map=False,
        show_stats=False,
    )

    assert logger is not None
    assert logger.stats.rounds_fought == 3
    assert logger.stats.fleet_a_shots_fired > 0
    assert logger.stats.fleet_b_shots_fired > 0
    assert logger.events, "Armored duel should emit battle events"
