"""Tests for fleet generator."""

import pytest
from ship_combat.fleet_generator import (
    FleetGenerator,
    ShipClassTemplate,
    SHIP_CLASS_TEMPLATES,
    FLEET_COMPOSITIONS,
    quick_fleet,
    symmetric_fleets,
)
from ship_combat.models import Ship


class TestShipClassTemplates:
    """Test ship class templates."""
    
    def test_templates_not_empty(self):
        """Should have multiple ship class templates."""
        assert len(SHIP_CLASS_TEMPLATES) > 0
        assert "Frigate" in SHIP_CLASS_TEMPLATES
        assert "Cruiser" in SHIP_CLASS_TEMPLATES
        assert "Battleship" in SHIP_CLASS_TEMPLATES
    
    def test_template_structure(self):
        """Templates should have required attributes."""
        for name, template in SHIP_CLASS_TEMPLATES.items():
            assert isinstance(template, ShipClassTemplate)
            assert template.class_name == name
            assert template.base_hull > 0
            assert len(template.crew_range) == 2
            assert template.crew_range[0] < template.crew_range[1]
            assert len(template.typical_engines) > 0
            assert len(template.typical_shields) > 0
            assert len(template.typical_weapons) > 0
    
    def test_battleship_stronger_than_frigate(self):
        """Battleship should have higher stats than frigate."""
        frigate = SHIP_CLASS_TEMPLATES["Frigate"]
        battleship = SHIP_CLASS_TEMPLATES["Battleship"]
        
        assert battleship.base_hull > frigate.base_hull
        assert battleship.crew_range[0] > frigate.crew_range[0]
        assert battleship.leadership_range[0] >= frigate.leadership_range[0]


class TestFleetCompositions:
    """Test fleet composition presets."""
    
    def test_compositions_not_empty(self):
        """Should have multiple composition types."""
        assert len(FLEET_COMPOSITIONS) > 0
        assert "balanced" in FLEET_COMPOSITIONS
        assert "strike_force" in FLEET_COMPOSITIONS
    
    def test_composition_ratios_sum_to_one(self):
        """Each composition's ratios should sum to approximately 1.0."""
        for name, comp in FLEET_COMPOSITIONS.items():
            total = sum(comp.values())
            assert 0.9 <= total <= 1.1, f"Composition {name} ratios sum to {total}"
    
    def test_composition_uses_valid_classes(self):
        """Compositions should reference valid ship classes."""
        for name, comp in FLEET_COMPOSITIONS.items():
            for ship_class in comp.keys():
                assert ship_class in SHIP_CLASS_TEMPLATES, \
                    f"{name} references unknown class {ship_class}"


class TestFleetGenerator:
    """Test FleetGenerator class."""
    
    def test_generator_creation(self):
        """Should create fleet generator."""
        gen = FleetGenerator()
        assert isinstance(gen, FleetGenerator)
    
    def test_generator_with_seed(self):
        """Should create reproducible fleets with seed."""
        gen1 = FleetGenerator(seed=42)
        fleet1 = gen1.generate_fleet(size=3)
        
        gen2 = FleetGenerator(seed=42)
        fleet2 = gen2.generate_fleet(size=3)
        
        # Should have same ship classes in same order
        classes1 = [s.class_name for s in fleet1]
        classes2 = [s.class_name for s in fleet2]
        assert classes1 == classes2
    
    def test_generate_fleet_basic(self):
        """Should generate fleet with specified size."""
        gen = FleetGenerator()
        fleet = gen.generate_fleet(size=5)
        
        assert len(fleet) == 5
        for ship in fleet:
            assert isinstance(ship, Ship)
            assert ship.hull > 0
            assert ship.shield > 0
    
    def test_generate_fleet_balanced_composition(self):
        """Should generate balanced fleet."""
        gen = FleetGenerator(seed=123)
        fleet = gen.generate_fleet(size=10, composition="balanced")
        
        assert len(fleet) == 10
        # Should have variety of ship classes
        classes = [s.class_name for s in fleet]
        unique_classes = set(classes)
        assert len(unique_classes) >= 2
    
    def test_generate_fleet_strike_force(self):
        """Should generate strike force composition."""
        gen = FleetGenerator(seed=456)
        fleet = gen.generate_fleet(size=6, composition="strike_force")
        
        assert len(fleet) == 6
        # Strike force should have smaller ships
        for ship in fleet:
            assert ship.class_name in ["Frigate", "Destroyer", "Light Cruiser"]
    
    def test_generate_fleet_capital_fleet(self):
        """Should generate capital fleet composition."""
        gen = FleetGenerator(seed=789)
        fleet = gen.generate_fleet(size=6, composition="capital_fleet")
        
        assert len(fleet) == 6
        # Capital fleet should have larger ships
        for ship in fleet:
            assert ship.class_name in ["Light Cruiser", "Cruiser", "Battleship"]
    
    def test_generate_fleet_with_positions(self):
        """Should position ships in formation."""
        gen = FleetGenerator()
        fleet = gen.generate_fleet(
            size=5,
            starting_x=10.0,
            starting_y=20.0,
            formation_spread=15.0
        )
        
        # Ships should be positioned around starting point
        for ship in fleet:
            assert -20.0 <= ship.x <= 40.0
            assert 10.0 <= ship.y <= 50.0
    
    def test_generate_fleet_with_prefix(self):
        """Should use custom name prefix."""
        gen = FleetGenerator()
        fleet = gen.generate_fleet(size=3, prefix="Alpha")
        
        for ship in fleet:
            assert ship.name.startswith("Alpha")
    
    def test_generate_fleet_with_variance(self):
        """Should apply variance to ship stats."""
        gen = FleetGenerator(seed=111)
        fleet = gen.generate_fleet(size=5, variance=20)
        
        # With variance, ships should have different stats
        hulls = [s.hull for s in fleet]
        assert len(set(hulls)) > 1  # Should have variety
    
    def test_generate_custom_fleet(self):
        """Should generate fleet with custom ship counts."""
        gen = FleetGenerator()
        fleet = gen.generate_custom_fleet({
            "Frigate": 3,
            "Cruiser": 2,
            "Battleship": 1,
        })
        
        assert len(fleet) == 6
        
        # Count ship classes
        frigates = [s for s in fleet if s.class_name == "Frigate"]
        cruisers = [s for s in fleet if s.class_name == "Cruiser"]
        battleships = [s for s in fleet if s.class_name == "Battleship"]
        
        assert len(frigates) == 3
        assert len(cruisers) == 2
        assert len(battleships) == 1
    
    def test_generate_custom_fleet_with_positions(self):
        """Custom fleet should position ships correctly."""
        gen = FleetGenerator()
        fleet = gen.generate_custom_fleet(
            ship_counts={"Frigate": 2},
            starting_x=50.0,
            starting_y=100.0,
            formation_spread=20.0
        )
        
        assert len(fleet) == 2
        # Ships should be positioned around starting point
        for ship in fleet:
            assert 30.0 <= ship.x <= 70.0
            assert 90.0 <= ship.y <= 120.0
    
    def test_generate_fleet_unknown_composition(self):
        """Unknown composition should fallback to balanced."""
        gen = FleetGenerator()
        fleet = gen.generate_fleet(size=5, composition="nonexistent")
        
        assert len(fleet) == 5
        # Should still generate valid fleet
        for ship in fleet:
            assert isinstance(ship, Ship)


class TestQuickFleet:
    """Test quick fleet generation function."""
    
    def test_quick_fleet_defaults(self):
        """Should create fleet with defaults."""
        fleet = quick_fleet()
        
        assert len(fleet) == 5
        for ship in fleet:
            assert isinstance(ship, Ship)
    
    def test_quick_fleet_custom_size(self):
        """Should create fleet with custom size."""
        fleet = quick_fleet(size=10)
        assert len(fleet) == 10
    
    def test_quick_fleet_with_composition(self):
        """Should create fleet with specific composition."""
        fleet = quick_fleet(size=6, composition="strike_force")
        assert len(fleet) == 6
    
    def test_quick_fleet_with_seed(self):
        """Should create reproducible fleet with seed."""
        fleet1 = quick_fleet(size=4, seed=42)
        fleet2 = quick_fleet(size=4, seed=42)
        
        classes1 = [s.class_name for s in fleet1]
        classes2 = [s.class_name for s in fleet2]
        assert classes1 == classes2
    
    def test_quick_fleet_with_prefix(self):
        """Should use custom prefix."""
        fleet = quick_fleet(size=3, prefix="Omega")
        
        for ship in fleet:
            assert ship.name.startswith("Omega")


class TestSymmetricFleets:
    """Test symmetric fleet generation."""
    
    def test_symmetric_fleets_basic(self):
        """Should create two opposing fleets."""
        fleet_a, fleet_b = symmetric_fleets()
        
        assert len(fleet_a) == 3
        assert len(fleet_b) == 3
        
        for ship in fleet_a + fleet_b:
            assert isinstance(ship, Ship)
    
    def test_symmetric_fleets_custom_size(self):
        """Should create fleets with custom size."""
        fleet_a, fleet_b = symmetric_fleets(size=5)
        
        assert len(fleet_a) == 5
        assert len(fleet_b) == 5
    
    def test_symmetric_fleets_positioned_apart(self):
        """Fleets should be positioned apart."""
        fleet_a, fleet_b = symmetric_fleets(separation=200.0)
        
        # Fleet A should be on left side (negative x)
        for ship in fleet_a:
            assert ship.x < 0
        
        # Fleet B should be on right side (positive x)
        for ship in fleet_b:
            assert ship.x > 0
    
    def test_symmetric_fleets_facing_each_other(self):
        """Fleet B should face Fleet A."""
        fleet_a, fleet_b = symmetric_fleets()
        
        # Fleet B should have heading around 180 degrees
        for ship in fleet_b:
            assert 150 <= ship.heading <= 210
    
    def test_symmetric_fleets_with_prefixes(self):
        """Should use custom prefixes."""
        fleet_a, fleet_b = symmetric_fleets(
            fleet_a_prefix="Red",
            fleet_b_prefix="Blue"
        )
        
        for ship in fleet_a:
            assert ship.name.startswith("Red")
        
        for ship in fleet_b:
            assert ship.name.startswith("Blue")
    
    def test_symmetric_fleets_with_seed(self):
        """Should create reproducible fleets with seed."""
        fleet_a1, fleet_b1 = symmetric_fleets(size=4, seed=99)
        fleet_a2, fleet_b2 = symmetric_fleets(size=4, seed=99)
        
        classes_a1 = [s.class_name for s in fleet_a1]
        classes_a2 = [s.class_name for s in fleet_a2]
        assert classes_a1 == classes_a2
        
        classes_b1 = [s.class_name for s in fleet_b1]
        classes_b2 = [s.class_name for s in fleet_b2]
        assert classes_b1 == classes_b2
    
    def test_symmetric_fleets_same_composition(self):
        """Both fleets should have same composition."""
        fleet_a, fleet_b = symmetric_fleets(
            size=6,
            composition="capital_fleet",
            seed=555
        )
        
        # Both should follow capital_fleet composition
        for fleet in [fleet_a, fleet_b]:
            for ship in fleet:
                assert ship.class_name in ["Light Cruiser", "Cruiser", "Battleship"]


class TestFleetGeneratorEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_generate_single_ship_fleet(self):
        """Should handle fleet of size 1."""
        gen = FleetGenerator()
        fleet = gen.generate_fleet(size=1)
        
        assert len(fleet) == 1
        assert isinstance(fleet[0], Ship)
    
    def test_generate_large_fleet(self):
        """Should handle large fleets."""
        gen = FleetGenerator()
        fleet = gen.generate_fleet(size=50)
        
        assert len(fleet) == 50
        for ship in fleet:
            assert isinstance(ship, Ship)
    
    def test_custom_fleet_empty_dict(self):
        """Empty ship counts should produce empty fleet."""
        gen = FleetGenerator()
        fleet = gen.generate_custom_fleet({})
        
        assert len(fleet) == 0
    
    def test_custom_fleet_unknown_class(self):
        """Unknown ship class should fallback to Frigate."""
        gen = FleetGenerator()
        fleet = gen.generate_custom_fleet({"UnknownClass": 2})
        
        # Should still create 2 ships (probably frigates as fallback)
        assert len(fleet) == 2
    
    def test_zero_variance_produces_consistent_stats(self):
        """Zero variance should produce ships with same base stats for same class."""
        gen = FleetGenerator(seed=777)
        fleet = gen.generate_fleet(size=3, composition="patrol_group", variance=0)
        
        # Ships of same class should have identical hulls (no variance)
        frigates = [s for s in fleet if s.class_name == "Frigate"]
        if len(frigates) >= 2:
            hulls = [s.hull for s in frigates]
            assert len(set(hulls)) == 1  # All same
    
    def test_high_variance_produces_variety(self):
        """High variance should produce varied stats."""
        gen = FleetGenerator(seed=888)
        fleet = gen.generate_fleet(size=10, variance=30)
        
        hulls = [s.hull for s in fleet]
        # Should have variety
        assert len(set(hulls)) > 1
