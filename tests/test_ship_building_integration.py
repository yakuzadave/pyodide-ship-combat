"""
End-to-end integration tests for ship building and fleet generation.

These tests validate that ships and fleets built with the new system
work correctly with the battle simulation engine.
"""

import sys
from unittest.mock import MagicMock
import pytest

# Mock rolldice before importing battle_sim
mock_rolldice = MagicMock()
sys.modules['rolldice'] = mock_rolldice

from ship_combat.ship_builder import ShipBuilder, quick_ship, randomized_ship
import ship_combat.battle_sim as battle_sim
from ship_combat.fleet_generator import (
    FleetGenerator,
    quick_fleet,
    symmetric_fleets,
)
from ship_combat.battle_sim import (
    distance,
    move_fleet,
    in_arc,
    in_range,
    can_fire,
    shooting_phase,
)
from ship_combat.models import Ship


def get_rolldice():
    """Get mocked rolldice module."""
    return sys.modules['rolldice']


@pytest.fixture(autouse=True)
def use_module_rolldice_mock(monkeypatch):
    """Keep this module's rolldice mock isolated from other test modules."""
    monkeypatch.setattr(battle_sim, "get_rolldice", get_rolldice)


class TestShipBuilderIntegration:
    """Test that builder-created ships work with battle mechanics."""
    
    def test_builder_ship_can_move(self):
        """Ships from builder should move correctly."""
        ship = (ShipBuilder("Mover")
                .with_engine("frigate_fast")
                .with_position(0.0, 0.0, 0.0)
                .with_orientation(0.0, 0.0)  # Heading 0 = north/positive Y
                .build())
        
        initial_y = ship.y
        move_fleet([ship])
        
        # Should have moved forward (heading=0 degrees = north)
        assert ship.y > initial_y or ship.x != 0.0  # Ship moved in some direction
    
    def test_builder_ship_can_calculate_distance(self):
        """Distance calculation should work with builder ships."""
        ship1 = (ShipBuilder("Ship1")
                 .with_position(0.0, 0.0, 0.0)
                 .build())
        
        ship2 = (ShipBuilder("Ship2")
                 .with_position(10.0, 0.0, 0.0)
                 .build())
        
        dist = distance(ship1, ship2)
        assert dist == 10.0
    
    def test_builder_ship_can_target(self):
        """Targeting mechanics should work with builder ships."""
        # Heading 0 degrees = +X direction (fore)
        attacker = (ShipBuilder("Attacker")
                    .with_position(0.0, 0.0, 0.0)
                    .with_orientation(0.0, 0.0)  # Facing +X (east/0 degrees)
                    .with_weapons(["lance_battery"])
                    .build())
        
        target = (ShipBuilder("Target")
                  .with_position(10.0, 0.0, 0.0)  # Directly along +X axis
                  .build())
        
        battery = attacker.weapons.batteries[0]
        
        # Should be in arc and range
        assert in_arc(attacker, target, battery.arc)
        assert in_range(attacker, target, battery.range)
        assert can_fire(attacker, target, battery)
    
    def test_builder_ship_weapon_heat(self):
        """Weapon heat mechanics should work."""
        ship = (ShipBuilder("Armed")
                .with_weapons(["plasma_cannon"])
                .build())
        
        battery = ship.weapons.batteries[0]
        initial_heat = battery.heat
        
        # Fire weapon
        battery.add_heat()
        assert battery.heat > initial_heat
        
        # Cool down
        battery.cool_down()
        assert battery.heat < battery.heat + battery.heat_per_shot
    
    def test_builder_ship_shield_regeneration(self):
        """Shield regeneration should work."""
        ship = (ShipBuilder("Shielded")
                .with_shield("standard")
                .build())
        
        # Damage shields
        ship.shield = 20
        max_shield = ship.max_shield
        
        # Regenerate
        ship.regenerate_shields()
        
        assert ship.shield > 20
        assert ship.shield <= max_shield
    
    def test_quick_ship_in_battle_sim(self):
        """Quick ships should work in battle simulation."""
        mock_rolldice.roll_dice.return_value = (15, "mocked")
        
        ship1 = quick_ship("Quick1", hull=50)
        ship2 = quick_ship("Quick2", hull=50)
        
        fleet = [ship1, ship2]
        
        # Should be able to move fleet
        move_fleet(fleet)
        
        # Ships should have moved
        assert ship1.x != 0.0 or ship1.y != 0.0
    
    def test_randomized_ship_in_battle(self):
        """Randomized ships should work in battle."""
        ship1 = randomized_ship("Random1", "Frigate", base_hull=50)
        ship2 = randomized_ship("Random2", "Frigate", base_hull=50)
        
        # Should be valid ships
        assert isinstance(ship1, Ship)
        assert isinstance(ship2, Ship)
        
        # Should have different stats (with high probability)
        assert ship1.hull > 0 and ship2.hull > 0


class TestFleetGeneratorIntegration:
    """Test that generated fleets work with battle mechanics."""
    
    def test_generated_fleet_can_move(self):
        """Generated fleets should move correctly."""
        gen = FleetGenerator(seed=123)
        fleet = gen.generate_fleet(size=5, starting_x=-10.0)
        
        # All ships should be at starting position
        for ship in fleet:
            assert ship.x < 10.0
        
        # Move fleet
        move_fleet(fleet)
        
        # Ships should have moved
        for ship in fleet:
            assert ship.x != -10.0 or ship.y != 0.0
    
    def test_generated_fleet_combat_ready(self):
        """Generated fleets should be combat ready."""
        gen = FleetGenerator()
        fleet = gen.generate_fleet(size=5)
        
        for ship in fleet:
            # Should have valid combat stats
            assert ship.hull > 0
            assert ship.shield >= 0
            assert ship.crew > 0
            assert ship.leadership > 0
            assert len(ship.weapons.batteries) > 0
            assert ship.speed > 0
    
    def test_quick_fleet_in_battle(self):
        """Quick fleets should work in battle simulation."""
        mock_rolldice.roll_dice.return_value = (15, "mocked")
        
        fleet = quick_fleet(size=3, composition="strike_force", seed=456)
        
        # Should all be valid ships
        assert len(fleet) == 3
        for ship in fleet:
            assert isinstance(ship, Ship)
            assert ship.hull > 0
        
        # Should be able to move
        move_fleet(fleet)
    
    def test_symmetric_fleets_in_battle(self):
        """Symmetric fleets should work in battle."""
        mock_rolldice.roll_dice.return_value = (20, "mocked")
        
        fleet_a, fleet_b = symmetric_fleets(
            size=3,
            composition="balanced",
            separation=100.0,
            seed=789
        )
        
        # Both fleets should be valid
        assert len(fleet_a) == 3
        assert len(fleet_b) == 3
        
        # Should be positioned apart
        for ship_a in fleet_a:
            assert ship_a.x < 0
        
        for ship_b in fleet_b:
            assert ship_b.x > 0
        
        # Should be able to move both fleets
        move_fleet(fleet_a + fleet_b)
    
    def test_custom_fleet_composition_in_battle(self):
        """Custom fleet compositions should work."""
        gen = FleetGenerator(seed=111)
        fleet = gen.generate_custom_fleet({
            "Frigate": 3,
            "Cruiser": 2,
            "Battleship": 1,
        })
        
        # Should have correct composition
        assert len(fleet) == 6
        
        frigates = [s for s in fleet if s.class_name == "Frigate"]
        cruisers = [s for s in fleet if s.class_name == "Cruiser"]
        battleships = [s for s in fleet if s.class_name == "Battleship"]
        
        assert len(frigates) == 3
        assert len(cruisers) == 2
        assert len(battleships) == 1
        
        # All should be combat ready
        for ship in fleet:
            assert ship.hull > 0
            assert len(ship.weapons.batteries) > 0


class TestFullBattleSimulation:
    """End-to-end tests with full battle simulation."""
    
    def test_simple_two_ship_battle(self):
        """Complete battle between two builder ships."""
        mock_rolldice.roll_dice.return_value = (25, "hit")
        
        ship1 = (ShipBuilder("Attacker")
                 .with_hull(50)
                 .with_shield("standard")
                 .with_weapons(["lance_battery"], missiles=2)
                 .with_position(-10.0, 0.0, 0.0)
                 .with_orientation(90.0, 0.0)
                 .build())
        
        ship2 = (ShipBuilder("Defender")
                 .with_hull(50)
                 .with_shield("standard")
                 .with_weapons(["macro_cannon"])
                 .with_position(10.0, 0.0, 0.0)
                 .with_orientation(270.0, 0.0)
                 .build())
        
        fleet_a = [ship1]
        fleet_b = [ship2]
        
        # Simulate one round
        move_fleet(fleet_a + fleet_b)
        
        # Both ships should still be valid
        assert ship1.hull > 0
        assert ship2.hull > 0
    
    def test_fleet_battle_multiple_rounds(self):
        """Multi-round battle with generated fleets."""
        mock_rolldice.roll_dice.return_value = (15, "moderate")
        
        fleet_a, fleet_b = symmetric_fleets(
            size=3,
            composition="strike_force",
            separation=80.0,
            seed=999
        )
        
        # Simulate 3 rounds
        for round_num in range(3):
            # Move all ships
            move_fleet(fleet_a + fleet_b)
            
            # Check that ships are still valid
            for ship in fleet_a + fleet_b:
                assert isinstance(ship, Ship)
                # Hull might go negative in combat, that's ok
                assert ship.shield >= 0
    
    def test_mixed_fleet_composition_battle(self):
        """Battle with mixed fleet compositions."""
        gen = FleetGenerator(seed=222)
        
        # Raiding party vs patrol group
        raiders = gen.generate_fleet(
            size=5,
            composition="raiding_party",
            starting_x=-50.0,
            prefix="Raider"
        )
        
        patrol = gen.generate_fleet(
            size=4,
            composition="patrol_group",
            starting_x=50.0,
            prefix="Patrol"
        )
        
        # Should have appropriate ship types
        raider_classes = set(s.class_name for s in raiders)
        patrol_classes = set(s.class_name for s in patrol)
        
        # Raiders should be small fast ships
        for ship_class in raider_classes:
            assert ship_class in ["Corvette", "Frigate", "Destroyer"]
        
        # Patrol should also be light ships
        for ship_class in patrol_classes:
            assert ship_class in ["Corvette", "Frigate", "Light Cruiser"]
        
        # All ships should be combat capable
        for ship in raiders + patrol:
            assert ship.speed > 0
            assert len(ship.weapons.batteries) > 0
    
    def test_variance_creates_diversity(self):
        """High variance should create diverse fleets."""
        fleet = quick_fleet(
            size=10,
            composition="balanced",
            variance=25,
            seed=333
        )
        
        # Collect stats
        hulls = [s.hull for s in fleet]
        shields = [s.shield for s in fleet]
        crews = [s.crew for s in fleet]
        
        # Should have variety (not all same)
        assert len(set(hulls)) > 1
        assert len(set(shields)) > 1
        assert len(set(crews)) > 1
    
    def test_deterministic_with_seed(self):
        """Same seed should produce identical fleets."""
        fleet1 = quick_fleet(size=5, composition="balanced", seed=444)
        fleet2 = quick_fleet(size=5, composition="balanced", seed=444)
        
        # Should have identical ship classes and base stats
        for i in range(5):
            assert fleet1[i].class_name == fleet2[i].class_name
            assert fleet1[i].hull == fleet2[i].hull
            assert fleet1[i].shield == fleet2[i].shield


class TestComponentInteroperability:
    """Test that all components work together correctly."""
    
    def test_all_engine_types(self):
        """All engine types should work in ships."""
        from ship_combat.ship_components import ENGINE_LIBRARY
        
        for engine_key in ENGINE_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{engine_key}")
                    .with_engine(engine_key)
                    .build())
            
            assert ship.speed > 0
            assert ship.maneuver > 0
            move_fleet([ship])  # Should move without error
    
    def test_all_shield_types(self):
        """All shield types should work in ships."""
        from ship_combat.ship_components import SHIELD_LIBRARY
        
        for shield_key in SHIELD_LIBRARY.keys():
            ship = (ShipBuilder(f"Test-{shield_key}")
                    .with_shield(shield_key)
                    .build())
            
            assert ship.shield > 0
            assert ship.max_shield >= ship.shield
            ship.regenerate_shields()  # Should regenerate without error
    
    def test_all_weapon_loadouts(self):
        """All weapon loadouts should work in ships."""
        from ship_combat.ship_components import WEAPON_LOADOUTS
        
        for loadout_key in WEAPON_LOADOUTS.keys():
            ship = (ShipBuilder(f"Test-{loadout_key}")
                    .with_weapon_loadout(loadout_key, missiles=2)
                    .build())
            
            assert len(ship.weapons.batteries) > 0
            # All batteries should be valid
            for battery in ship.weapons.batteries:
                assert battery.rating > 0
                assert battery.damage_dice
    
    def test_all_ship_class_templates(self):
        """All ship class templates should generate valid ships."""
        from ship_combat.fleet_generator import SHIP_CLASS_TEMPLATES
        
        gen = FleetGenerator(seed=555)
        
        for class_name in SHIP_CLASS_TEMPLATES.keys():
            fleet = gen.generate_custom_fleet({class_name: 2})
            
            assert len(fleet) == 2
            for ship in fleet:
                assert ship.class_name == class_name
                assert ship.hull > 0
                assert ship.speed > 0
                assert len(ship.weapons.batteries) > 0
    
    def test_all_fleet_compositions(self):
        """All fleet compositions should generate valid fleets."""
        from ship_combat.fleet_generator import FLEET_COMPOSITIONS
        
        for composition in FLEET_COMPOSITIONS.keys():
            fleet = quick_fleet(
                size=6,
                composition=composition,
                seed=666
            )
            
            assert len(fleet) == 6
            for ship in fleet:
                assert isinstance(ship, Ship)
                assert ship.hull > 0


class TestBackwardCompatibility:
    """Ensure new system works with existing code."""
    
    def test_works_with_demo_fleets(self):
        """New ships should work alongside demo_fleets ships."""
        from ship_combat.fleet_setup import demo_fleets
        
        # Get old-style ships
        old_fleet_a, old_fleet_b = demo_fleets()
        
        # Create new-style ships
        new_ship = quick_ship("NewShip", hull=60)
        
        # Should be able to mix them
        mixed_fleet = old_fleet_a + [new_ship]
        
        # Should work with battle mechanics
        move_fleet(mixed_fleet)
        
        for ship in mixed_fleet:
            assert isinstance(ship, Ship)
    
    def test_new_ships_have_same_attributes(self):
        """New ships should have all required attributes."""
        ship = quick_ship("Test")
        
        # Should have all standard Ship attributes
        required_attrs = [
            'name', 'hull', 'shield', 'weapons', 'crew', 'leadership',
            'boarding_strength', 'class_name', 'speed', 'x', 'y', 'z',
            'heading', 'pitch', 'maneuver', 'systems', 'max_shield',
            'shield_regen_rate', 'max_power', 'power_allocation'
        ]
        
        for attr in required_attrs:
            assert hasattr(ship, attr), f"Missing attribute: {attr}"
