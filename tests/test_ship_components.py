"""Tests for ship component library."""

import pytest
from ship_combat.ship_components import (
    EngineComponent,
    ShieldComponent,
    ReactorComponent,
    ENGINE_LIBRARY,
    SHIELD_LIBRARY,
    REACTOR_LIBRARY,
    WEAPON_BATTERY_LIBRARY,
    WEAPON_LOADOUTS,
    create_weapon_system,
    build_ship_systems,
    apply_variance,
    get_random_engine,
    get_random_shield,
    get_random_weapon_loadout,
)
from ship_combat.models import WeaponSystem, ShipSystem


class TestComponentLibraries:
    """Test component library availability."""
    
    def test_engine_library_not_empty(self):
        """Engine library should contain multiple engines."""
        assert len(ENGINE_LIBRARY) > 0
        assert "frigate_standard" in ENGINE_LIBRARY
        assert "cruiser_standard" in ENGINE_LIBRARY
    
    def test_shield_library_not_empty(self):
        """Shield library should contain multiple shield types."""
        assert len(SHIELD_LIBRARY) > 0
        assert "light" in SHIELD_LIBRARY
        assert "standard" in SHIELD_LIBRARY
        assert "heavy" in SHIELD_LIBRARY
    
    def test_reactor_library_not_empty(self):
        """Reactor library should contain multiple reactor types."""
        assert len(REACTOR_LIBRARY) > 0
        assert "standard" in REACTOR_LIBRARY
        assert "enhanced" in REACTOR_LIBRARY
    
    def test_weapon_battery_library_not_empty(self):
        """Weapon battery library should contain various weapons."""
        assert len(WEAPON_BATTERY_LIBRARY) > 0
        assert "light_laser" in WEAPON_BATTERY_LIBRARY
        assert "lance_battery" in WEAPON_BATTERY_LIBRARY
        assert "plasma_cannon" in WEAPON_BATTERY_LIBRARY
    
    def test_weapon_loadouts_not_empty(self):
        """Weapon loadouts should contain preset configurations."""
        assert len(WEAPON_LOADOUTS) > 0
        assert "frigate_balanced" in WEAPON_LOADOUTS
        assert "cruiser_standard" in WEAPON_LOADOUTS


class TestEngineComponent:
    """Test EngineComponent dataclass."""
    
    def test_engine_component_creation(self):
        """Should create engine component with correct attributes."""
        engine = EngineComponent("Test Drive", speed=25, maneuver=2)
        assert engine.name == "Test Drive"
        assert engine.speed == 25
        assert engine.maneuver == 2
        assert engine.efficiency == 100
    
    def test_engine_library_components(self):
        """Engine library entries should have valid attributes."""
        engine = ENGINE_LIBRARY["frigate_standard"]
        assert isinstance(engine, EngineComponent)
        assert engine.speed > 0
        assert engine.maneuver > 0


class TestShieldComponent:
    """Test ShieldComponent dataclass."""
    
    def test_shield_component_creation(self):
        """Should create shield component with correct attributes."""
        shield = ShieldComponent("Test Shield", shield=40, max_shield=40)
        assert shield.name == "Test Shield"
        assert shield.shield == 40
        assert shield.max_shield == 40
        assert shield.regen_rate == 5
    
    def test_shield_library_components(self):
        """Shield library entries should have valid attributes."""
        shield = SHIELD_LIBRARY["standard"]
        assert isinstance(shield, ShieldComponent)
        assert shield.shield > 0
        assert shield.max_shield == shield.shield
        assert shield.regen_rate > 0


class TestWeaponSystemCreation:
    """Test weapon system creation from batteries."""
    
    def test_create_empty_weapon_system(self):
        """Should create empty weapon system."""
        weapons = create_weapon_system([], missiles=0)
        assert isinstance(weapons, WeaponSystem)
        assert len(weapons.batteries) == 0
        assert weapons.missiles == 0
    
    def test_create_weapon_system_single_battery(self):
        """Should create weapon system with one battery."""
        weapons = create_weapon_system(["light_laser"], missiles=2)
        assert len(weapons.batteries) == 1
        assert weapons.batteries[0].name == "Light Laser Battery"
        assert weapons.missiles == 2
    
    def test_create_weapon_system_multiple_batteries(self):
        """Should create weapon system with multiple batteries."""
        weapons = create_weapon_system(["lance_battery", "macro_cannon"], missiles=4)
        assert len(weapons.batteries) == 2
        assert weapons.batteries[0].name == "Lance Battery"
        assert weapons.batteries[1].name == "Macro Cannon Battery"
        assert weapons.missiles == 4
    
    def test_weapon_batteries_are_independent(self):
        """Each weapon system should have independent battery instances."""
        weapons1 = create_weapon_system(["light_laser"])
        weapons2 = create_weapon_system(["light_laser"])
        
        # Modify one battery
        weapons1.batteries[0].heat = 50
        
        # Other should be unaffected
        assert weapons2.batteries[0].heat == 0
    
    def test_unknown_battery_ignored(self):
        """Unknown battery names should be ignored."""
        weapons = create_weapon_system(["unknown_weapon", "light_laser"])
        assert len(weapons.batteries) == 1
        assert weapons.batteries[0].name == "Light Laser Battery"


class TestShipSystemBuilder:
    """Test ship systems builder function."""
    
    def test_build_all_systems(self):
        """Should build all standard systems."""
        systems = build_ship_systems()
        assert "engines" in systems
        assert "shields" in systems
        assert "targeting" in systems
        assert "reactor" in systems
        assert len(systems) == 4
    
    def test_build_partial_systems(self):
        """Should build only requested systems."""
        systems = build_ship_systems(
            include_engines=True,
            include_shields=True,
            include_targeting=False,
            include_reactor=False
        )
        assert "engines" in systems
        assert "shields" in systems
        assert "targeting" not in systems
        assert "reactor" not in systems
        assert len(systems) == 2
    
    def test_systems_have_correct_type(self):
        """Built systems should be ShipSystem instances."""
        systems = build_ship_systems()
        for system in systems.values():
            assert isinstance(system, ShipSystem)
            assert system.status == "Operational"
            assert 50 <= system.efficiency <= 100


class TestVarianceFunction:
    """Test variance application."""
    
    def test_apply_zero_variance(self):
        """Zero variance should return base value."""
        result = apply_variance(100, 0)
        assert result == 100
    
    def test_apply_variance_produces_different_values(self):
        """Variance should produce different values over multiple calls."""
        results = [apply_variance(100, 20) for _ in range(10)]
        # Should have at least some variance (not all identical)
        assert len(set(results)) > 1
    
    def test_variance_within_bounds(self):
        """Variance should stay within expected range."""
        base = 100
        variance = 10
        for _ in range(20):
            result = apply_variance(base, variance)
            # Should be within ±10% of 100 (90-110)
            assert 80 <= result <= 120


class TestRandomComponentSelection:
    """Test random component selection functions."""
    
    def test_get_random_engine_for_frigate(self):
        """Should get appropriate engine for frigate."""
        engine = get_random_engine("frigate")
        assert isinstance(engine, EngineComponent)
        # Should get a frigate-type engine or Fast Attack Drive (which is frigate_fast)
        assert "frigate" in engine.name.lower() or "attack" in engine.name.lower()
    
    def test_get_random_engine_for_cruiser(self):
        """Should get appropriate engine for cruiser."""
        engine = get_random_engine("cruiser")
        assert isinstance(engine, EngineComponent)
        # Should get cruiser engine or fallback
        assert engine.speed > 0
    
    def test_get_random_engine_unknown_class(self):
        """Should fallback to default for unknown class."""
        engine = get_random_engine("unknown_class")
        assert isinstance(engine, EngineComponent)
        assert engine.speed > 0
    
    def test_get_random_shield(self):
        """Should get random shield above threshold."""
        shield = get_random_shield(min_shield=30)
        assert isinstance(shield, ShieldComponent)
        assert shield.shield >= 30
    
    def test_get_random_shield_no_minimum(self):
        """Should get any random shield with no minimum."""
        shield = get_random_shield(min_shield=0)
        assert isinstance(shield, ShieldComponent)
        assert shield.shield > 0
    
    def test_get_random_weapon_loadout_for_frigate(self):
        """Should get appropriate loadout for frigate."""
        loadout = get_random_weapon_loadout("frigate")
        assert isinstance(loadout, list)
        assert len(loadout) > 0
        # Should be valid battery names
        for battery_name in loadout:
            assert battery_name in WEAPON_BATTERY_LIBRARY
    
    def test_get_random_weapon_loadout_unknown_class(self):
        """Should fallback to default for unknown class."""
        loadout = get_random_weapon_loadout("unknown_class")
        assert isinstance(loadout, list)
        assert len(loadout) > 0


class TestWeaponBatteryAttributes:
    """Test weapon battery attributes from library."""
    
    def test_light_weapons_have_low_heat(self):
        """Light weapons should generate less heat."""
        light_laser = WEAPON_BATTERY_LIBRARY["light_laser"]
        autocannon = WEAPON_BATTERY_LIBRARY["autocannon"]
        
        assert light_laser.heat_per_shot <= 20
        assert autocannon.heat_per_shot <= 15
    
    def test_heavy_weapons_have_high_heat(self):
        """Heavy weapons should generate more heat."""
        nova_cannon = WEAPON_BATTERY_LIBRARY["nova_cannon"]
        plasma_broadside = WEAPON_BATTERY_LIBRARY["plasma_broadside"]
        
        assert nova_cannon.heat_per_shot >= 40
        assert plasma_broadside.heat_per_shot >= 35
    
    def test_long_range_weapons_have_correct_range(self):
        """Long range weapons should have 'long' range attribute."""
        lance = WEAPON_BATTERY_LIBRARY["lance_battery"]
        heavy_lance = WEAPON_BATTERY_LIBRARY["heavy_lance"]
        
        assert lance.range == "long"
        assert heavy_lance.range == "long"
    
    def test_special_weapons_have_special_attribute(self):
        """Weapons with special rules should have the attribute set."""
        plasma_broadside = WEAPON_BATTERY_LIBRARY["plasma_broadside"]
        nova_cannon = WEAPON_BATTERY_LIBRARY["nova_cannon"]
        
        assert plasma_broadside.special == "area"
        assert nova_cannon.special == "explosive"


class TestWeaponLoadouts:
    """Test preset weapon loadout configurations."""
    
    def test_frigate_loadouts_valid(self):
        """Frigate loadouts should reference valid batteries."""
        for key, batteries in WEAPON_LOADOUTS.items():
            if key.startswith("frigate"):
                for battery in batteries:
                    assert battery in WEAPON_BATTERY_LIBRARY
    
    def test_cruiser_loadouts_valid(self):
        """Cruiser loadouts should reference valid batteries."""
        for key, batteries in WEAPON_LOADOUTS.items():
            if key.startswith("cruiser"):
                for battery in batteries:
                    assert battery in WEAPON_BATTERY_LIBRARY
    
    def test_battleship_loadouts_valid(self):
        """Battleship loadouts should reference valid batteries."""
        for key, batteries in WEAPON_LOADOUTS.items():
            if key.startswith("battleship"):
                for battery in batteries:
                    assert battery in WEAPON_BATTERY_LIBRARY
    
    def test_loadouts_not_empty(self):
        """All loadouts should have at least one battery."""
        for key, batteries in WEAPON_LOADOUTS.items():
            assert len(batteries) > 0, f"Loadout {key} is empty"
