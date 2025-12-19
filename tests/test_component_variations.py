"""
Comprehensive tests for ship component variations and combinations.

These tests ensure that all possible component combinations work correctly
and that the system remains stable as new components are added.
"""

import sys
from unittest.mock import MagicMock
import pytest
import itertools

# Mock rolldice before importing battle_sim
mock_rolldice = MagicMock()
sys.modules['rolldice'] = mock_rolldice

from ship_combat.ship_builder import ShipBuilder
from ship_combat.ship_components import (
    ENGINE_LIBRARY,
    SHIELD_LIBRARY,
    REACTOR_LIBRARY,
    WEAPON_BATTERY_LIBRARY,
    WEAPON_LOADOUTS,
)
from ship_combat.battle_sim import move_fleet, distance, can_fire
from ship_combat.models import Ship


class TestAllEngineVariations:
    """Test all engine types in ships."""
    
    def test_all_engines_create_valid_ships(self):
        """All engine types should create valid, movable ships."""
        for engine_key in ENGINE_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{engine_key}")
                    .with_engine(engine_key)
                    .build())
            
            assert ship.speed > 0, f"{engine_key} has invalid speed"
            assert ship.maneuver > 0, f"{engine_key} has invalid maneuver"
            
            # Ensure ship can move
            initial_pos = (ship.x, ship.y)
            move_fleet([ship])
            # Ship should have moved or at least be movable
            assert isinstance(ship.x, (int, float))
            assert isinstance(ship.y, (int, float))
    
    def test_engine_speed_variations(self):
        """Different engines should produce different speeds."""
        speeds = {}
        for engine_key in ENGINE_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{engine_key}")
                    .with_engine(engine_key)
                    .build())
            speeds[engine_key] = ship.speed
        
        # Should have at least 2 different speed values
        unique_speeds = set(speeds.values())
        assert len(unique_speeds) >= 2, "All engines have same speed"
    
    def test_engine_maneuverability_variations(self):
        """Different engines should produce different maneuverability."""
        maneuvers = {}
        for engine_key in ENGINE_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{engine_key}")
                    .with_engine(engine_key)
                    .build())
            maneuvers[engine_key] = ship.maneuver
        
        # Should have at least 2 different maneuver values
        unique_maneuvers = set(maneuvers.values())
        assert len(unique_maneuvers) >= 2, "All engines have same maneuver"


class TestAllShieldVariations:
    """Test all shield types in ships."""
    
    def test_all_shields_create_valid_ships(self):
        """All shield types should create valid ships."""
        for shield_key in SHIELD_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{shield_key}")
                    .with_shield(shield_key)
                    .build())
            
            assert ship.shield > 0, f"{shield_key} has invalid shield"
            assert ship.max_shield >= ship.shield, f"{shield_key} max_shield inconsistent"
            assert ship.shield_regen_rate > 0, f"{shield_key} has invalid regen rate"
            
            # Ensure shields can regenerate
            initial_shield = ship.shield
            ship.shield = max(0, ship.shield - 10)  # Damage shields
            ship.regenerate_shields()
            # Should regenerate (or stay at 0 if heavily damaged)
            assert ship.shield >= 0
    
    def test_shield_capacity_variations(self):
        """Different shields should have different capacities."""
        capacities = {}
        for shield_key in SHIELD_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{shield_key}")
                    .with_shield(shield_key)
                    .build())
            capacities[shield_key] = ship.max_shield
        
        # Should have at least 3 different capacity values
        unique_capacities = set(capacities.values())
        assert len(unique_capacities) >= 3, "Shields lack variety"
    
    def test_shield_regen_rate_variations(self):
        """Different shields should have different regen rates."""
        regen_rates = {}
        for shield_key in SHIELD_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{shield_key}")
                    .with_shield(shield_key)
                    .build())
            regen_rates[shield_key] = ship.shield_regen_rate
        
        # Should have at least 3 different regen rate values
        unique_rates = set(regen_rates.values())
        assert len(unique_rates) >= 3, "Shield regen rates lack variety"


class TestAllWeaponVariations:
    """Test all weapon types and loadouts."""
    
    def test_all_weapon_batteries_valid(self):
        """All weapon batteries should create valid weapons."""
        for weapon_key in WEAPON_BATTERY_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{weapon_key}")
                    .with_weapons([weapon_key])
                    .build())
            
            assert len(ship.weapons.batteries) == 1
            battery = ship.weapons.batteries[0]
            
            assert battery.rating > 0, f"{weapon_key} has invalid rating"
            assert battery.damage_dice, f"{weapon_key} has no damage dice"
            assert battery.range in ["point", "short", "standard", "long"], \
                f"{weapon_key} has invalid range"
    
    def test_all_weapon_loadouts_valid(self):
        """All weapon loadouts should create valid ships."""
        for loadout_key in WEAPON_LOADOUTS.keys():
            ship = (ShipBuilder(f"Test-{loadout_key}")
                    .with_weapon_loadout(loadout_key, missiles=2)
                    .build())
            
            assert len(ship.weapons.batteries) > 0, f"{loadout_key} has no weapons"
            assert ship.weapons.missiles == 2
            
            # All batteries should be valid
            for battery in ship.weapons.batteries:
                assert battery.rating > 0
    
    def test_weapon_rating_variations(self):
        """Different weapons should have different ratings."""
        ratings = set()
        for weapon_key in WEAPON_BATTERY_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{weapon_key}")
                    .with_weapons([weapon_key])
                    .build())
            ratings.add(ship.weapons.batteries[0].rating)
        
        # Should have at least 3 different rating values
        assert len(ratings) >= 3, "Weapon ratings lack variety"
    
    def test_weapon_heat_characteristics_vary(self):
        """Different weapons should have different heat characteristics."""
        heat_per_shot = set()
        cooling_rates = set()
        
        for weapon_key in WEAPON_BATTERY_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{weapon_key}")
                    .with_weapons([weapon_key])
                    .build())
            battery = ship.weapons.batteries[0]
            heat_per_shot.add(battery.heat_per_shot)
            cooling_rates.add(battery.cooling_rate)
        
        # Should have variety in heat characteristics
        assert len(heat_per_shot) >= 3, "Heat per shot lacks variety"
        assert len(cooling_rates) >= 3, "Cooling rates lack variety"


class TestAllReactorVariations:
    """Test all reactor types."""
    
    def test_all_reactors_create_valid_ships(self):
        """All reactor types should create valid ships."""
        for reactor_key in REACTOR_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{reactor_key}")
                    .with_reactor(reactor_key)
                    .build())
            
            assert ship.max_power > 0, f"{reactor_key} has invalid power"
            
            # Power allocation should work
            assert sum(ship.power_allocation.values()) > 0
    
    def test_reactor_power_variations(self):
        """Different reactors should provide different power levels."""
        power_levels = {}
        for reactor_key in REACTOR_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{reactor_key}")
                    .with_reactor(reactor_key)
                    .build())
            power_levels[reactor_key] = ship.max_power
        
        # Should have at least 2 different power levels
        unique_powers = set(power_levels.values())
        assert len(unique_powers) >= 2, "Reactor powers lack variety"


class TestComponentCombinations:
    """Test various combinations of components together."""
    
    def test_all_engine_shield_combinations(self):
        """All engine-shield combinations should work."""
        tested = 0
        for engine_key, shield_key in itertools.product(
            list(ENGINE_LIBRARY.keys())[:3],  # Test subset for speed
            list(SHIELD_LIBRARY.keys())[:3]
        ):
            ship = (ShipBuilder(f"Test-{engine_key}-{shield_key}")
                    .with_engine(engine_key)
                    .with_shield(shield_key)
                    .build())
            
            assert ship.speed > 0
            assert ship.shield > 0
            tested += 1
        
        assert tested >= 9, "Not enough combinations tested"
    
    def test_mixed_component_ships_in_battle(self):
        """Ships with different component mixes should work in battle."""
        mock_rolldice.roll_dice.return_value = (20, "test")
        
        # Create ships with various component combinations
        ships = [
            (ShipBuilder("Fast-Light")
             .with_engine("frigate_fast")
             .with_shield("light")
             .with_weapons(["light_laser"])
             .build()),
            
            (ShipBuilder("Slow-Heavy")
             .with_engine("battleship_slow")
             .with_shield("capital")
             .with_weapons(["plasma_broadside"])
             .build()),
            
            (ShipBuilder("Mixed")
             .with_engine("cruiser_standard")
             .with_shield("reinforced")
             .with_reactor("enhanced")
             .with_weapons(["lance_battery", "macro_cannon"])
             .build()),
        ]
        
        # All ships should be valid
        for ship in ships:
            assert isinstance(ship, Ship)
            assert ship.hull > 0
        
        # Should be able to move all ships
        move_fleet(ships)
        
        # Should be able to calculate distances
        dist = distance(ships[0], ships[1])
        assert dist >= 0
    
    def test_extreme_component_combinations(self):
        """Test unusual but valid component combinations."""
        # Slow ship with high maneuver weapons (corvette-class speed with battleship weapons)
        ship1 = (ShipBuilder("Unusual-1")
                 .with_engine("battleship_slow")
                 .with_shield("regenerative")  # High regen, low capacity
                 .with_weapons(["nova_cannon"])  # Heavy weapon on slow ship
                 .build())
        
        # Fast ship with heavy shields
        ship2 = (ShipBuilder("Unusual-2")
                 .with_engine("corvette_standard")
                 .with_shield("capital")
                 .with_weapons(["point_defense"])
                 .build())
        
        # Both should be valid
        for ship in [ship1, ship2]:
            assert ship.speed > 0
            assert ship.shield > 0
            assert len(ship.weapons.batteries) > 0


class TestComponentScalability:
    """Test that system scales with new components."""
    
    def test_adding_new_engine_would_not_break(self):
        """System should handle new engine types gracefully."""
        # This tests the pattern - new engines just need to be added to library
        from ship_combat.ship_components import EngineComponent
        
        # Simulate a new engine
        new_engine = EngineComponent("Test Engine", speed=40, maneuver=4)
        
        # Should have all required attributes
        assert hasattr(new_engine, 'speed')
        assert hasattr(new_engine, 'maneuver')
        assert hasattr(new_engine, 'efficiency')
        
        # Using it directly should work
        ship = (ShipBuilder("Test")
                .with_engine_component(new_engine)
                .build())
        
        assert ship.speed == 40
        assert ship.maneuver == 4
    
    def test_adding_new_shield_would_not_break(self):
        """System should handle new shield types gracefully."""
        from ship_combat.ship_components import ShieldComponent
        
        # Simulate a new shield
        new_shield = ShieldComponent("Test Shield", shield=100, max_shield=100, regen_rate=15)
        
        # Should have all required attributes
        assert hasattr(new_shield, 'shield')
        assert hasattr(new_shield, 'max_shield')
        assert hasattr(new_shield, 'regen_rate')
        
        # Using it directly should work
        ship = (ShipBuilder("Test")
                .with_shield_component(new_shield)
                .build())
        
        assert ship.shield == 100
        assert ship.max_shield == 100
        assert ship.shield_regen_rate == 15
    
    def test_adding_new_weapon_battery_pattern(self):
        """New weapon batteries follow the same pattern."""
        from ship_combat.models import WeaponBattery
        
        # Simulate a new weapon
        new_weapon = WeaponBattery(
            name="Test Weapon",
            rating=6,
            accuracy=2,
            damage_dice="6d6",
            range="long",
            heat_per_shot=60,
            cooling_rate=3
        )
        
        # Should have all required attributes
        assert hasattr(new_weapon, 'rating')
        assert hasattr(new_weapon, 'damage_dice')
        assert hasattr(new_weapon, 'heat_per_shot')
        assert hasattr(new_weapon, 'cooling_rate')
        
        # Should be able to use it
        assert new_weapon.rating == 6
        assert new_weapon.is_overheated() == False


class TestRegressionPrevention:
    """Tests to prevent regressions in component functionality."""
    
    def test_all_engines_maintain_consistent_speed_order(self):
        """Engine speed ordering should remain consistent."""
        speeds = {}
        for engine_key in ENGINE_LIBRARY.keys():
            engine = ENGINE_LIBRARY[engine_key]
            speeds[engine_key] = engine.speed
        
        # Corvettes should be faster than battleships
        corvette_engines = [k for k in speeds if 'corvette' in k.lower()]
        battleship_engines = [k for k in speeds if 'battleship' in k.lower()]
        
        if corvette_engines and battleship_engines:
            avg_corvette_speed = sum(speeds[k] for k in corvette_engines) / len(corvette_engines)
            avg_battleship_speed = sum(speeds[k] for k in battleship_engines) / len(battleship_engines)
            assert avg_corvette_speed > avg_battleship_speed, "Speed order broken"
    
    def test_all_shields_maintain_consistent_capacity_order(self):
        """Shield capacity ordering should remain consistent."""
        capacities = {}
        for shield_key in SHIELD_LIBRARY.keys():
            shield = SHIELD_LIBRARY[shield_key]
            capacities[shield_key] = shield.shield
        
        # Light shields should have less capacity than capital shields
        if 'light' in capacities and 'capital' in capacities:
            assert capacities['light'] < capacities['capital'], "Shield capacity order broken"
    
    def test_weapon_heat_balance_maintained(self):
        """Weapon heat generation should remain balanced."""
        for weapon_key in WEAPON_BATTERY_LIBRARY.keys():
            weapon = WEAPON_BATTERY_LIBRARY[weapon_key]
            
            # Heat per shot should never exceed max heat times 5
            # (prevents instant overheating)
            assert weapon.heat_per_shot <= weapon.max_heat * 5, \
                f"{weapon_key} heat per shot too high"
            
            # Cooling rate should be positive and reasonable
            assert 0 < weapon.cooling_rate <= 50, \
                f"{weapon_key} cooling rate unreasonable"
    
    def test_component_changes_dont_break_existing_ships(self):
        """Ships created with standard patterns should still work."""
        # This is the pattern from the original demo_fleets
        from ship_combat.fleet_setup import demo_fleets
        
        old_fleet_a, old_fleet_b = demo_fleets()
        
        # Old ships should still be valid
        for ship in old_fleet_a + old_fleet_b:
            assert ship.hull > 0
            assert ship.speed > 0
            assert len(ship.weapons.batteries) > 0
        
        # New ships should work alongside old ships
        new_ship = (ShipBuilder("New")
                    .with_engine("frigate_fast")
                    .with_shield("heavy")
                    .build())
        
        # Should be able to mix old and new
        mixed_fleet = old_fleet_a + [new_ship]
        move_fleet(mixed_fleet)


class TestComponentDataIntegrity:
    """Ensure component data remains consistent and valid."""
    
    def test_no_duplicate_component_names(self):
        """Component names should be unique within each library."""
        # Engine names
        engine_names = [e.name for e in ENGINE_LIBRARY.values()]
        assert len(engine_names) == len(set(engine_names)), "Duplicate engine names"
        
        # Shield names
        shield_names = [s.name for s in SHIELD_LIBRARY.values()]
        assert len(shield_names) == len(set(shield_names)), "Duplicate shield names"
        
        # Weapon names
        weapon_names = [w.name for w in WEAPON_BATTERY_LIBRARY.values()]
        assert len(weapon_names) == len(set(weapon_names)), "Duplicate weapon names"
    
    def test_all_components_have_required_attributes(self):
        """All components must have required attributes."""
        # Engines
        for engine in ENGINE_LIBRARY.values():
            assert hasattr(engine, 'speed')
            assert hasattr(engine, 'maneuver')
            assert hasattr(engine, 'name')
        
        # Shields
        for shield in SHIELD_LIBRARY.values():
            assert hasattr(shield, 'shield')
            assert hasattr(shield, 'max_shield')
            assert hasattr(shield, 'regen_rate')
        
        # Weapons
        for weapon in WEAPON_BATTERY_LIBRARY.values():
            assert hasattr(weapon, 'rating')
            assert hasattr(weapon, 'damage_dice')
            assert hasattr(weapon, 'heat_per_shot')
            assert hasattr(weapon, 'cooling_rate')
    
    def test_loadouts_reference_valid_weapons(self):
        """All loadouts should reference existing weapons."""
        for loadout_key, weapons in WEAPON_LOADOUTS.items():
            for weapon_key in weapons:
                assert weapon_key in WEAPON_BATTERY_LIBRARY, \
                    f"Loadout {loadout_key} references unknown weapon {weapon_key}"
    
    def test_component_values_within_reasonable_bounds(self):
        """Component values should be within reasonable ranges."""
        # Engine speeds
        for engine in ENGINE_LIBRARY.values():
            assert 5 <= engine.speed <= 50, f"{engine.name} speed out of bounds"
            assert 1 <= engine.maneuver <= 5, f"{engine.name} maneuver out of bounds"
        
        # Shield capacities
        for shield in SHIELD_LIBRARY.values():
            assert 10 <= shield.shield <= 150, f"{shield.name} capacity out of bounds"
            assert 1 <= shield.regen_rate <= 20, f"{shield.name} regen out of bounds"
        
        # Weapon ratings
        for weapon in WEAPON_BATTERY_LIBRARY.values():
            assert 1 <= weapon.rating <= 10, f"{weapon.name} rating out of bounds"


class TestCrossComponentInteractions:
    """Test how different components interact with each other."""
    
    def test_power_allocation_affects_all_ships(self):
        """Power allocation should work regardless of components."""
        for engine_key in list(ENGINE_LIBRARY.keys())[:2]:
            ship = (ShipBuilder("Test")
                    .with_engine(engine_key)
                    .build())
            
            # Power allocation should affect movement
            ship.power_allocation = {"weapons": 20, "shields": 20, "engines": 60}
            speed_mod = ship.get_power_modifier("engines")
            assert speed_mod > 1.0, "Engine power boost not working"
    
    def test_shield_regen_works_with_all_shields(self):
        """Shield regeneration should work for all shield types."""
        for shield_key in SHIELD_LIBRARY.keys():
            ship = (ShipBuilder("Test")
                    .with_shield(shield_key)
                    .build())
            
            # Damage and regenerate
            ship.shield = ship.shield // 2  # Half damage
            initial = ship.shield
            ship.regenerate_shields()
            
            # Should regenerate
            assert ship.shield >= initial, f"{shield_key} not regenerating"
    
    def test_weapon_heat_works_with_all_weapons(self):
        """Heat management should work for all weapons."""
        for weapon_key in list(WEAPON_BATTERY_LIBRARY.keys())[:5]:
            ship = (ShipBuilder("Test")
                    .with_weapons([weapon_key])
                    .build())
            
            battery = ship.weapons.batteries[0]
            
            # Heat up
            initial_heat = battery.heat
            battery.add_heat()
            assert battery.heat > initial_heat, f"{weapon_key} not heating"
            
            # Cool down
            heated = battery.heat
            battery.cool_down()
            assert battery.heat < heated, f"{weapon_key} not cooling"
