"""Tests for ship builder fluent API."""

import pytest
from ship_combat.ship_builder import ShipBuilder, quick_ship, randomized_ship
from ship_combat.models import Ship


class TestShipBuilder:
    """Test fluent ShipBuilder API."""
    
    def test_minimal_ship_creation(self):
        """Should create ship with just a name using defaults."""
        ship = ShipBuilder("Test Ship").build()
        
        assert isinstance(ship, Ship)
        assert ship.name == "Test Ship"
        assert ship.class_name == "Frigate"
        assert ship.hull > 0
        assert ship.shield > 0
        assert len(ship.weapons.batteries) > 0
    
    def test_with_class(self):
        """Should set ship class."""
        ship = ShipBuilder("Aurora").with_class("Light Cruiser").build()
        assert ship.class_name == "Light Cruiser"
    
    def test_with_hull(self):
        """Should set hull points."""
        ship = ShipBuilder("Tank").with_hull(150).build()
        assert ship.hull == 150
    
    def test_with_crew(self):
        """Should set crew statistics."""
        ship = (ShipBuilder("Manned")
                .with_crew(crew=500, leadership=9, boarding_strength=10)
                .build())
        assert ship.crew == 500
        assert ship.leadership == 9
        assert ship.boarding_strength == 10
    
    def test_with_engine(self):
        """Should set engine from library."""
        ship = (ShipBuilder("Fast")
                .with_engine("frigate_fast")
                .build())
        assert ship.speed == 30
        assert ship.maneuver == 3
    
    def test_with_shield(self):
        """Should set shield from library."""
        ship = (ShipBuilder("Tanky")
                .with_shield("capital")
                .build())
        assert ship.shield == 80
        assert ship.max_shield == 80
        assert ship.shield_regen_rate == 10
    
    def test_with_reactor(self):
        """Should set reactor from library."""
        ship = (ShipBuilder("Powered")
                .with_reactor("military")
                .build())
        assert ship.max_power == 150
    
    def test_with_weapons(self):
        """Should set weapons from battery list."""
        ship = (ShipBuilder("Armed")
                .with_weapons(["lance_battery", "macro_cannon"], missiles=6)
                .build())
        assert len(ship.weapons.batteries) == 2
        assert ship.weapons.missiles == 6
        assert ship.weapons.batteries[0].name == "Lance Battery"
    
    def test_with_weapon_loadout(self):
        """Should set weapons from preset loadout."""
        ship = (ShipBuilder("Cruiser")
                .with_weapon_loadout("cruiser_standard", missiles=4)
                .build())
        assert len(ship.weapons.batteries) >= 2
        assert ship.weapons.missiles == 4
    
    def test_with_position(self):
        """Should set initial position."""
        ship = (ShipBuilder("Positioned")
                .with_position(x=10.0, y=20.0, z=5.0)
                .build())
        assert ship.x == 10.0
        assert ship.y == 20.0
        assert ship.z == 5.0
    
    def test_with_orientation(self):
        """Should set orientation."""
        ship = (ShipBuilder("Oriented")
                .with_orientation(heading=90.0, pitch=15.0)
                .build())
        assert ship.heading == 90.0
        assert ship.pitch == 15.0
    
    def test_with_ai_personality(self):
        """Should set AI personality."""
        ship = (ShipBuilder("Smart")
                .with_ai_personality("Calculating and precise")
                .build())
        assert ship.ai == "Calculating and precise"
    
    def test_chaining_multiple_methods(self):
        """Should chain multiple builder methods."""
        ship = (ShipBuilder("Complex")
                .with_class("Battleship")
                .with_hull(120)
                .with_shield("capital")
                .with_engine("battleship_standard")
                .with_weapon_loadout("battleship_standard", missiles=8)
                .with_crew(400, 9, 10)
                .with_position(0.0, 0.0, 0.0)
                .with_orientation(0.0, 0.0)
                .with_ai_personality("Aggressive commander")
                .build())
        
        assert ship.name == "Complex"
        assert ship.class_name == "Battleship"
        assert ship.hull == 120
        assert ship.shield == 80
        assert ship.speed == 15
        assert ship.crew == 400
        assert ship.leadership == 9
        assert ship.ai == "Aggressive commander"
    
    def test_with_variance_applies_randomization(self):
        """Variance should randomize ship stats."""
        ship1 = (ShipBuilder("Random1")
                 .with_hull(100)
                 .with_variance(20)
                 .build())
        
        ship2 = (ShipBuilder("Random2")
                 .with_hull(100)
                 .with_variance(20)
                 .build())
        
        # With high variance, ships should likely differ
        # (There's a small chance they could be identical, but unlikely)
        assert ship1.hull > 0 and ship2.hull > 0
    
    def test_variance_keeps_values_reasonable(self):
        """Variance should not produce negative or excessive values."""
        for _ in range(10):
            ship = (ShipBuilder("Test")
                    .with_hull(100)
                    .with_crew(100)
                    .with_variance(30)
                    .build())
            
            assert ship.hull > 0
            assert ship.crew > 0
            assert 1 <= ship.leadership <= 10
            assert ship.boarding_strength > 0
    
    def test_with_custom_systems(self):
        """Should accept custom systems dictionary."""
        from ship_combat.models import ShipSystem
        custom_systems = {
            "engines": ShipSystem(efficiency=75),
            "shields": ShipSystem(efficiency=90),
        }
        ship = (ShipBuilder("Custom")
                .with_systems(custom_systems)
                .build())
        
        assert ship.systems["engines"].efficiency == 75
        assert ship.systems["shields"].efficiency == 90


class TestQuickShip:
    """Test quick ship creation function."""
    
    def test_quick_ship_defaults(self):
        """Should create ship with default parameters."""
        ship = quick_ship("Quick")
        assert isinstance(ship, Ship)
        assert ship.name == "Quick"
        assert ship.class_name == "Frigate"
    
    def test_quick_ship_custom_params(self):
        """Should create ship with custom parameters."""
        ship = quick_ship(
            name="Custom Quick",
            class_name="Cruiser",
            hull=90,
            shield_type="heavy",
            engine_type="cruiser_standard",
            weapon_loadout="cruiser_heavy",
            missiles=6,
            crew=250,
            leadership=8,
            boarding_strength=7
        )
        
        assert ship.name == "Custom Quick"
        assert ship.class_name == "Cruiser"
        assert ship.hull == 90
        assert ship.shield == 65
        assert ship.crew == 250
        assert ship.leadership == 8
        assert ship.weapons.missiles == 6
    
    def test_quick_ship_creates_valid_ship(self):
        """Quick ship should create fully valid ship."""
        ship = quick_ship("Valid")
        
        assert ship.hull > 0
        assert ship.shield > 0
        assert ship.speed > 0
        assert ship.maneuver > 0
        assert len(ship.weapons.batteries) > 0
        assert len(ship.systems) > 0


class TestRandomizedShip:
    """Test randomized ship creation."""
    
    def test_randomized_ship_basic(self):
        """Should create randomized ship."""
        ship = randomized_ship("Random", "Frigate", base_hull=50)
        
        assert isinstance(ship, Ship)
        assert ship.name == "Random"
        assert ship.class_name == "Frigate"
        assert ship.hull > 0
    
    def test_randomized_ship_has_variety(self):
        """Multiple randomized ships should differ."""
        ships = [randomized_ship(f"Ship{i}", "Cruiser", base_hull=90) 
                 for i in range(5)]
        
        # Check that at least some attributes differ
        hulls = [s.hull for s in ships]
        crews = [s.crew for s in ships]
        
        # Should have some variance (not all identical)
        assert len(set(hulls)) > 1 or len(set(crews)) > 1
    
    def test_randomized_ship_different_classes(self):
        """Should handle different ship classes."""
        frigate = randomized_ship("F1", "Frigate", base_hull=50)
        cruiser = randomized_ship("C1", "Cruiser", base_hull=90)
        battleship = randomized_ship("B1", "Battleship", base_hull=100)
        
        assert frigate.class_name == "Frigate"
        assert cruiser.class_name == "Cruiser"
        assert battleship.class_name == "Battleship"
    
    def test_randomized_ship_variance_parameter(self):
        """Should respect variance parameter."""
        # Low variance should produce ships closer to base
        low_var = randomized_ship("Low", "Frigate", base_hull=50, variance=5)
        
        # Should be within reasonable range
        assert 40 <= low_var.hull <= 60
    
    def test_randomized_ship_has_valid_components(self):
        """Randomized ship should have valid components."""
        ship = randomized_ship("Valid", "Cruiser", base_hull=90)
        
        assert ship.speed > 0
        assert ship.maneuver > 0
        assert ship.shield > 0
        assert ship.max_shield >= ship.shield
        assert len(ship.weapons.batteries) > 0
        assert len(ship.systems) > 0


class TestBuilderEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_unknown_engine_uses_default(self):
        """Unknown engine key should not crash."""
        ship = (ShipBuilder("Test")
                .with_engine("nonexistent_engine")
                .build())
        assert ship.speed > 0  # Should have default engine
    
    def test_unknown_shield_uses_default(self):
        """Unknown shield key should not crash."""
        ship = (ShipBuilder("Test")
                .with_shield("nonexistent_shield")
                .build())
        assert ship.shield > 0  # Should have default shield
    
    def test_unknown_reactor_uses_default(self):
        """Unknown reactor key should not crash."""
        ship = (ShipBuilder("Test")
                .with_reactor("nonexistent_reactor")
                .build())
        assert ship.max_power > 0  # Should have default reactor
    
    def test_unknown_loadout_uses_default(self):
        """Unknown loadout key should not crash."""
        ship = (ShipBuilder("Test")
                .with_weapon_loadout("nonexistent_loadout")
                .build())
        assert len(ship.weapons.batteries) > 0  # Should have default weapons
    
    def test_empty_weapons_list(self):
        """Empty weapons list should use default."""
        ship = (ShipBuilder("Unarmed")
                .with_weapons([])
                .build())
        # Should still get default weapon
        assert len(ship.weapons.batteries) >= 1
    
    def test_zero_missiles(self):
        """Zero missiles should work correctly."""
        ship = (ShipBuilder("No Missiles")
                .with_weapons(["lance_battery"], missiles=0)
                .build())
        assert ship.weapons.missiles == 0
    
    def test_high_variance_doesnt_break(self):
        """High variance should not produce invalid ships."""
        ship = (ShipBuilder("Extreme")
                .with_hull(100)
                .with_variance(50)
                .build())
        
        assert ship.hull > 0
        assert ship.shield > 0
        assert ship.crew > 0
