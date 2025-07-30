
import random

from ship_combat.battle_sim import (
    select_orders,
    shooting_phase,
    apply_hazard,
    missile_phase,
    boarding_phase,
    repair_phase,
)
from ship_combat.fleet_setup import new_ship, system_block
from ship_combat.models import WeaponSystem, WeaponBattery
import os
import sys
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from BATTLE_SIM import select_orders, shooting_phase, apply_hazard
from fleet_setup import new_ship, system_block
from models import WeaponSystem, WeaponBattery


def dummy_ship(name):
    return new_ship(
        name,
        "Frigate",
        hull=10,
        shield=5,
        weapons=WeaponSystem([WeaponBattery("Gun", rating=1, damage_dice="1d6")]),
        missiles=0,
        crew=1,
        leadership=1,
        boarding_strength=1,
        speed=10,
        maneuver=1,
        systems={"engines": system_block()},
        ai="",
    )


def test_select_orders_seeded():
    random.seed(1)
    ships = [dummy_ship("A"), dummy_ship("B")]
    select_orders(ships)
    assert [s.order for s in ships] == ["All Power to Shields", "Run Silent"]


def test_shooting_damage_seeded():
    random.seed(2)
    attacker = dummy_ship("Attacker")
    defender = dummy_ship("Defender")
    shooting_phase([attacker], [defender])
    assert defender.hull == 10  # miss with this seed


def test_apply_hazard_minefield_seeded():
    random.seed(1)
    ship = dummy_ship("Hazard")
    apply_hazard(ship, "Minefield")
    assert ship.hull == 8


def test_missile_phase_seeded():
    random.seed(3)
    attacker = dummy_ship("A")
    attacker.weapons.missiles = 1
    defender = dummy_ship("B")
    missile_phase([attacker], [defender])
    assert defender.hull == 0
    assert attacker.weapons.missiles == 0


def test_boarding_phase_seeded():
    random.seed(1)
    attacker = dummy_ship("A")
    defender = dummy_ship("B")
    boarding_phase([attacker], [defender])
    assert defender.hull == 5


def test_repair_phase_priority():
    system = system_block(40)
    system.damage(0)
    ship = new_ship(
        "Repair",
        "Frigate",
        hull=10,
        shield=5,
        weapons=WeaponSystem(),
        missiles=0,
        crew=1,
        leadership=1,
        boarding_strength=1,
        speed=10,
        maneuver=1,
        systems={"engines": system},
        ai="",
    )
    ship.repair_priority = True
    repair_phase([ship])
    assert ship.systems["engines"].efficiency == 50
    assert ship.systems["engines"].status == "Operational"

