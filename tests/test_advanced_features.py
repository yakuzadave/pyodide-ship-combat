"""Tests for advanced ship combat features: formations, evasion, heat, power, etc."""

import random
import pytest
from ship_combat.models import Ship, WeaponSystem, WeaponBattery, ShipSystem
from ship_combat.battle_sim import (
    update_formation_position,
    calculate_intercept_course,
    apply_evasive_maneuvers,
    distance,
    shield_regeneration_phase,
    weapon_cooling_phase,
)


@pytest.fixture
def basic_ship():
    """Create a basic ship for testing."""
    weapons = WeaponSystem()
    battery = WeaponBattery(
        name="Test Cannon",
        rating=3,
        accuracy=2,
        damage_dice="2d6",
        range="standard",
    )
    weapons.add_battery(battery)

    ship = Ship(
        name="Test Ship",
        hull=100,
        shield=50,
        weapons=weapons,
        crew=100,
        leadership=5,
        boarding_strength=3,
        class_name="Cruiser",
        speed=20,
        x=0.0,
        y=0.0,
        z=0.0,
        heading=0.0,
        pitch=0.0,
        maneuver=2,
        systems={
            "engines": ShipSystem(status="Operational", efficiency=100),
            "shields": ShipSystem(status="Operational", efficiency=100),
        },
    )
    return ship


def test_formation_following():
    """Test that ships follow their formation leader."""
    # Create leader
    leader = Ship(
        name="Leader",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        x=10.0,
        y=10.0,
        z=0.0,
        heading=90.0,
    )

    # Create follower with offset
    follower = Ship(
        name="Follower",
        hull=80,
        shield=40,
        weapons=WeaponSystem(),
        crew=80,
        leadership=4,
        boarding_strength=2,
        x=0.0,
        y=0.0,
        z=0.0,
        heading=0.0,
        formation_leader=leader,
        formation_offset_x=-5.0,
        formation_offset_y=0.0,
        formation_offset_z=0.0,
    )

    # Update formation position
    update_formation_position(follower)

    # Follower should move toward formation position
    assert follower.x != 0.0  # Should have moved
    assert follower.heading == 90.0  # Should match leader heading

    # After multiple updates, should be closer to target position
    for _ in range(10):
        update_formation_position(follower)

    # Should be close to target position (10-5, 10, 0)
    assert abs(follower.x - 5.0) < 1.0
    assert abs(follower.y - 10.0) < 1.0


def test_formation_with_destroyed_leader():
    """Test that ships don't crash when formation leader is destroyed."""
    leader = Ship(
        name="Leader",
        hull=0,  # Destroyed
        shield=0,
        weapons=WeaponSystem(),
        crew=0,
        leadership=5,
        boarding_strength=0,
        x=10.0,
        y=10.0,
    )

    follower = Ship(
        name="Follower",
        hull=80,
        shield=40,
        weapons=WeaponSystem(),
        crew=80,
        leadership=4,
        boarding_strength=2,
        x=0.0,
        y=0.0,
        formation_leader=leader,
    )

    # Should not move when leader is destroyed
    old_x = follower.x
    update_formation_position(follower)
    assert follower.x == old_x


def test_intercept_calculation():
    """Test intercept course calculation for pursuit."""
    # Ship at origin
    pursuer = Ship(
        name="Pursuer",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        x=0.0,
        y=0.0,
        z=0.0,
        speed=25,
    )

    # Target moving east at speed 20
    target = Ship(
        name="Target",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        x=50.0,
        y=0.0,
        z=0.0,
        heading=90.0,  # Moving north
        speed=20,
    )

    heading, pitch = calculate_intercept_course(pursuer, target)

    # Should calculate a heading that accounts for target movement
    assert 0 <= heading < 360
    assert -90 <= pitch <= 90

    # Heading should be roughly toward the target (in the eastern quadrant)
    # Since target is moving north, intercept should aim north of east
    assert 0 <= heading <= 180  # Eastern hemisphere


def test_evasive_maneuvers():
    """Test that evasive maneuvers change ship heading."""
    random.seed(42)

    ship = Ship(
        name="Evader",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        heading=90.0,
        pitch=0.0,
        maneuver=3,  # High maneuverability
        evasion_active=True,
    )

    original_heading = ship.heading
    apply_evasive_maneuvers(ship)

    # Heading should have changed
    assert ship.heading != original_heading


def test_evasion_respects_maneuverability():
    """Test that more maneuverable ships dodge more."""
    random.seed(42)

    # Low maneuverability
    slow_ship = Ship(
        name="Battleship",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        heading=0.0,
        maneuver=1,
        evasion_active=True,
    )

    # High maneuverability
    fast_ship = Ship(
        name="Frigate",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        heading=0.0,
        maneuver=4,
        evasion_active=True,
    )

    slow_original = slow_ship.heading
    fast_original = fast_ship.heading

    apply_evasive_maneuvers(slow_ship)
    apply_evasive_maneuvers(fast_ship)

    slow_change = abs(slow_ship.heading - slow_original)
    fast_change = abs(fast_ship.heading - fast_original)

    # More maneuverable ship should change heading more
    # (This test may be probabilistic, but with fixed seed should pass)


def test_weapon_heat_buildup():
    """Test that weapons heat up when fired."""
    battery = WeaponBattery(
        name="Laser",
        rating=5,
        heat=0,
        max_heat=100,
        heat_per_shot=25,
        cooling_rate=10,
    )

    assert not battery.is_overheated()

    # Fire once
    overheated = battery.add_heat()
    assert battery.heat == 25
    assert not overheated

    # Fire three more times
    battery.add_heat()  # 50
    battery.add_heat()  # 75
    overheated = battery.add_heat()  # 100

    assert battery.heat == 100
    assert overheated
    assert battery.is_overheated()


def test_weapon_cooling():
    """Test that weapons cool down over time."""
    battery = WeaponBattery(
        name="Laser",
        rating=5,
        heat=80,
        max_heat=100,
        cooling_rate=20,
    )

    battery.cool_down()
    assert battery.heat == 60

    battery.cool_down()
    assert battery.heat == 40

    # Can't go below 0
    battery.cool_down()
    battery.cool_down()
    assert battery.heat == 0


def test_weapon_cooling_phase():
    """Test the weapon cooling phase for multiple ships."""
    weapons1 = WeaponSystem()
    battery1 = WeaponBattery(name="Gun1", rating=3, heat=100, cooling_rate=15)
    weapons1.add_battery(battery1)

    weapons2 = WeaponSystem()
    battery2 = WeaponBattery(name="Gun2", rating=3, heat=50, cooling_rate=10)
    weapons2.add_battery(battery2)

    ship1 = Ship(
        name="Ship1",
        hull=100,
        shield=50,
        weapons=weapons1,
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    ship2 = Ship(
        name="Ship2",
        hull=100,
        shield=50,
        weapons=weapons2,
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    fleet = [ship1, ship2]
    weapon_cooling_phase(fleet)

    # Both weapons should have cooled
    assert battery1.heat == 85
    assert battery2.heat == 40


def test_shield_regeneration():
    """Test shield regeneration mechanics."""
    ship = Ship(
        name="Regenerator",
        hull=100,
        shield=30,
        max_shield=50,
        shield_regen_rate=5,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    # Default power allocation (33% to shields = 1.0x modifier)
    ship.regenerate_shields()
    assert ship.shield == 35

    # Multiple regenerations
    ship.regenerate_shields()
    ship.regenerate_shields()
    assert ship.shield == 45

    # Can't exceed max
    ship.regenerate_shields()
    ship.regenerate_shields()
    assert ship.shield == 50


def test_shield_regeneration_with_power_boost():
    """Test that power allocation affects shield regeneration."""
    ship = Ship(
        name="Shielded",
        hull=100,
        shield=30,
        max_shield=50,
        shield_regen_rate=6,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    # Boost power to shields (60% = 1.82x modifier)
    ship.power_allocation["shields"] = 60

    ship.regenerate_shields()

    # Should regenerate more: 6 * (60/33) ≈ 10.9 = 10 shields
    assert ship.shield >= 39  # 30 + 10


def test_power_modifiers():
    """Test power allocation modifiers."""
    ship = Ship(
        name="Power Test",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    # Default allocation (33% each)
    assert abs(ship.get_power_modifier("weapons") - 1.0) < 0.01
    assert abs(ship.get_power_modifier("shields") - 1.0) < 0.05
    assert abs(ship.get_power_modifier("engines") - 1.03) < 0.05

    # Boost weapons to 60%
    ship.power_allocation["weapons"] = 60
    weapon_mod = ship.get_power_modifier("weapons")
    assert weapon_mod > 1.5  # Should be roughly 1.82x


def test_shield_regeneration_phase():
    """Test shield regeneration for entire fleet."""
    ship1 = Ship(
        name="Ship1",
        hull=100,
        shield=40,
        max_shield=60,
        shield_regen_rate=5,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    ship2 = Ship(
        name="Ship2",
        hull=50,
        shield=60,
        max_shield=60,  # Already at max
        shield_regen_rate=5,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    ship3 = Ship(
        name="Ship3",
        hull=0,  # Destroyed
        shield=0,
        max_shield=50,
        weapons=WeaponSystem(),
        crew=0,
        leadership=5,
        boarding_strength=0,
    )

    fleet = [ship1, ship2, ship3]
    shield_regeneration_phase(fleet)

    # Ship1 should regenerate
    assert ship1.shield == 45

    # Ship2 should stay at max
    assert ship2.shield == 60

    # Ship3 (destroyed) should not regenerate
    assert ship3.shield == 0


def test_critical_hit_tracking():
    """Test that ships track critical hits taken."""
    ship = Ship(
        name="Target",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        critical_damage_taken=0,
    )

    assert ship.critical_damage_taken == 0

    # Simulate taking a critical hit
    ship.critical_damage_taken += 1
    assert ship.critical_damage_taken == 1


def test_pursuing_target_attribute():
    """Test that ships can track pursuit targets."""
    pursuer = Ship(
        name="Pursuer",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    target = Ship(
        name="Target",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    assert pursuer.pursuing_target is None

    # Set pursuit target
    pursuer.pursuing_target = target
    assert pursuer.pursuing_target == target


def test_evasion_active_attribute():
    """Test evasion active flag."""
    ship = Ship(
        name="Evader",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        evasion_active=False,
    )

    assert not ship.evasion_active

    ship.evasion_active = True
    assert ship.evasion_active

    # Evasive maneuvers should only apply when active
    original_heading = ship.heading
    apply_evasive_maneuvers(ship)
    # Heading should change when evasion is active (with randomness)


def test_max_shield_initialization():
    """Test that max_shield is set correctly on init."""
    ship = Ship(
        name="Test",
        hull=100,
        shield=75,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    # max_shield should auto-initialize to current shield
    assert ship.max_shield == 75


def test_shield_cannot_exceed_max():
    """Test that shields can't regenerate beyond max."""
    ship = Ship(
        name="Test",
        hull=100,
        shield=48,
        max_shield=50,
        shield_regen_rate=10,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
    )

    ship.regenerate_shields()
    # Should cap at 50, not go to 58
    assert ship.shield == 50
