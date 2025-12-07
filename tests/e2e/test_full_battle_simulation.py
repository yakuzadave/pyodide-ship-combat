"""End-to-end battle simulation smoke tests."""

from __future__ import annotations

import logging
import random

from ship_combat.battle_sim import battle
from ship_combat.fleet_setup import demo_fleets


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
