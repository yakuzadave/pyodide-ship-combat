from ship_combat.battle_sim import distance, move_fleet, in_arc, in_range, can_fire
from ship_combat.fleet_setup import new_ship
from ship_combat.models import WeaponSystem, WeaponBattery


def dummy_ship(name, x=0.0, y=0.0, z=0.0, heading=0.0, pitch=0.0):
    return new_ship(
        name,
        "Frigate",
        hull=10,
        shield=5,
        weapons=WeaponSystem([WeaponBattery("Gun", rating=1, damage_dice="1d1")]),
        missiles=0,
        crew=1,
        leadership=1,
        boarding_strength=1,
        speed=10,
        maneuver=1,
        systems={},
        ai="",
        x=x,
        y=y,
        z=z,
        heading=heading,
        pitch=pitch,
    )


def test_move_and_distance():
    ship = dummy_ship("A")
    move_fleet([ship])
    assert ship.x == 10 and ship.y == 0 and ship.z == 0
    target = dummy_ship("B", x=10)
    assert distance(ship, target) == 0


def test_arc_and_range():
    ship = dummy_ship("A", heading=0)
    target = dummy_ship("T", x=5, y=0)
    battery = ship.weapons.batteries[0]
    assert in_arc(ship, target, battery.arc)
    assert in_range(ship, target, battery.range)
    assert can_fire(ship, target, battery)
    other = dummy_ship("O", x=-5, y=0)
    assert not in_arc(ship, other, battery.arc)


def test_dorsal_ventral_arcs():
    ship = dummy_ship("A", heading=0, pitch=0)
    above = dummy_ship("Up", z=5)
    below = dummy_ship("Down", z=-5)
    assert in_arc(ship, above, "dorsal")
    assert not in_arc(ship, above, "ventral")
    assert in_arc(ship, below, "ventral")
    assert not in_arc(ship, below, "dorsal")
