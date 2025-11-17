import json
from dataclasses import FrozenInstanceError, asdict

import pytest

from ship_combat.controller import BattleSnapshotController
from ship_combat.fleet_setup import new_ship, system_block
from ship_combat.models import WeaponSystem, WeaponBattery


def make_test_ship(name: str):
    weapons = WeaponSystem([WeaponBattery("Test Battery", rating=1)])
    return new_ship(
        name,
        "Frigate",
        hull=10,
        shield=5,
        weapons=weapons,
        missiles=0,
        crew=5,
        leadership=6,
        boarding_strength=2,
        speed=10,
        maneuver=2,
        systems={"engines": system_block()},
        ai="test",
    )


def test_controller_creates_immutable_snapshots():
    alpha = [make_test_ship("Alpha-1")]
    controller = BattleSnapshotController()
    controller.begin_turn(1)
    first_phase = controller.record_phase("Orders", {"Alpha": alpha}, ["Orders issued"])
    # Mutate the ship to ensure we captured a copy in the snapshot
    alpha[0].hull = 0
    second_phase = controller.record_phase("Shooting", {"Alpha": alpha}, ["Alpha-1 destroyed"])
    finished_turn = controller.end_turn()

    assert first_phase.fleets["Alpha"].ships[0].hull == 10
    assert second_phase.fleets["Alpha"].ships[0].hull == 0
    assert finished_turn.latest_events() == ["Orders issued", "Alpha-1 destroyed"]


def test_controller_requires_turn_boundaries():
    alpha = [make_test_ship("Alpha-1")]
    controller = BattleSnapshotController()
    controller.begin_turn(1)
    controller.record_phase("Orders", {"Alpha": alpha})
    controller.end_turn()

    # After finishing a turn we can start a new one
    controller.begin_turn(2)
    controller.record_phase("Orders", {"Alpha": alpha})
    controller.end_turn()

    assert [turn.turn for turn in controller.iter_history()] == [1, 2]


def test_phase_and_ship_snapshots_are_immutable():
    alpha = [make_test_ship("Alpha-1")]
    controller = BattleSnapshotController()
    controller.begin_turn(1)
    phase = controller.record_phase("Orders", {"Alpha": alpha}, ["Orders issued"])

    ship_snapshot = phase.fleets["Alpha"].ships[0]
    assert ship_snapshot.status == "Operational"

    with pytest.raises(FrozenInstanceError):
        ship_snapshot.hull = 3

    with pytest.raises(TypeError):
        phase.new_events[0] = "Overwritten"

    with pytest.raises(TypeError):
        phase.fleets["Alpha"] = phase.fleets["Alpha"]

    with pytest.raises(TypeError):
        phase.fleets.update({"Alpha": phase.fleets["Alpha"]})


def test_phase_snapshot_is_json_serializable():
    alpha = [make_test_ship("Alpha-1")]
    controller = BattleSnapshotController()
    controller.begin_turn(1)
    phase = controller.record_phase("Orders", {"Alpha": alpha}, ["Orders issued"])

    # dataclasses.asdict should produce plain dicts/lists suitable for JSON
    phase_dict = asdict(phase)
    assert isinstance(phase_dict["fleets"], dict)
    serialized = json.dumps(phase_dict)
    assert "Alpha" in serialized
