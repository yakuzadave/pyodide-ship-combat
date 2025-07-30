import random

from ship_combat.battle_sim import select_orders, shooting_phase, apply_hazard
from ship_combat.fleet_setup import new_ship, system_block
from ship_combat.models import WeaponSystem, WeaponBattery


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

