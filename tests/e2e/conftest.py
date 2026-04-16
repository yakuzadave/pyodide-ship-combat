"""Test fixtures for end-to-end battle simulations."""

from __future__ import annotations

import random
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

# Ensure the repository root is available on sys.path so the simulator package
# can be imported when running the end-to-end suite directly.
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Use a dedicated RNG so dice rolls stay deterministic without affecting the
# global random state used elsewhere in the simulation.
_dice_rng = random.Random(1337)


def _roll_dice(dice_str: str):
    """Minimal deterministic dice roller for e2e tests.

    Supports expressions in the form "XdY" and defaults to a single d6 when the
    format is unexpected. Returns the total and its string representation to
    mirror ``py-rolldice``.
    """

    try:
        count_str, sides_str = dice_str.lower().split("d", maxsplit=1)
        count = int(count_str)
        sides = int(sides_str)
    except (ValueError, AttributeError):
        count, sides = 1, 6

    total = sum(_dice_rng.randint(1, sides) for _ in range(max(count, 1)))
    return total, str(total)


# Ensure the rolldice stub exists before importing the simulator so module-level
# imports succeed during test collection.
rolldice_stub = SimpleNamespace(roll_dice=_roll_dice)
sys.modules.setdefault("rolldice", rolldice_stub)


@pytest.fixture(autouse=True)
def inject_rolldice(monkeypatch):
    """Provide a deterministic rolldice replacement for end-to-end runs."""

    monkeypatch.setattr("ship_combat.battle_sim.rolldice", rolldice_stub, raising=False)
    monkeypatch.setattr("ship_combat.battle_sim.get_rolldice", lambda: rolldice_stub)
    yield
