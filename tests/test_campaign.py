"""Tests for the campaign module."""

import pytest

from ship_combat.campaign import (
    Empire,
    Colony,
    CampaignFleet,
    CampaignEvent,
    CampaignManager,
)
from ship_combat.star_system import StarSystem, Planet, link_systems
from ship_combat.models import Ship, WeaponSystem


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ship(name: str = "Test Ship", hull: int = 50) -> Ship:
    return Ship(
        name=name,
        hull=hull,
        shield=20,
        weapons=WeaponSystem(),
        crew=50,
        leadership=5,
        boarding_strength=3,
    )


def _make_system(sys_id: str, name: str) -> StarSystem:
    return StarSystem(id=sys_id, name=name)


def _make_empire(empire_id: str, home_id: str) -> Empire:
    return Empire(id=empire_id, name=f"Empire {empire_id}", home_system_id=home_id)


def _make_fleet(
    fleet_id: str,
    empire_id: str,
    system_id: str,
    ships=None,
) -> CampaignFleet:
    if ships is None:
        ships = [_make_ship()]
    return CampaignFleet(
        id=fleet_id,
        name=f"Fleet {fleet_id}",
        empire_id=empire_id,
        system_id=system_id,
        ships=ships,
    )


# ---------------------------------------------------------------------------
# Empire tests
# ---------------------------------------------------------------------------


class TestEmpire:
    def test_defaults(self):
        e = Empire(id="e0", name="Test Empire", home_system_id="sys_0")
        assert e.id == "e0"
        assert e.victory_points == 0
        assert "minerals" in e.resources

    def test_is_hostile_to_different_empire(self):
        e1 = Empire(id="e1", name="E1", home_system_id="s1")
        e2 = Empire(id="e2", name="E2", home_system_id="s2")
        assert e1.is_hostile_to(e2)

    def test_not_hostile_to_self(self):
        e1 = Empire(id="e1", name="E1", home_system_id="s1")
        assert not e1.is_hostile_to(e1)


# ---------------------------------------------------------------------------
# Colony tests
# ---------------------------------------------------------------------------


class TestColony:
    def test_production_this_turn_infra_1(self):
        colony = Colony(
            id="c0",
            name="Test Colony",
            empire_id="e0",
            system_id="s0",
            planet_name="Planet I",
        )
        produced = colony.production_this_turn()
        assert produced == colony.production

    def test_production_scales_with_infrastructure(self):
        colony = Colony(
            id="c0",
            name="Test",
            empire_id="e0",
            system_id="s0",
            planet_name="P",
            infrastructure_level=3,
        )
        base = colony.production["minerals"]
        produced = colony.production_this_turn()
        expected = base * (1.0 + 2 * 0.2)
        assert produced["minerals"] == pytest.approx(expected, rel=1e-3)


# ---------------------------------------------------------------------------
# CampaignFleet tests
# ---------------------------------------------------------------------------


class TestCampaignFleet:
    def test_is_in_transit_false_by_default(self):
        f = _make_fleet("f0", "e0", "s0")
        assert not f.is_in_transit

    def test_is_in_transit_true_when_destination_set(self):
        f = _make_fleet("f0", "e0", "s0")
        f.transit_destination = "s1"
        assert f.is_in_transit

    def test_strength_includes_all_ships(self):
        ships = [_make_ship(hull=50), _make_ship(hull=30)]
        f = CampaignFleet(id="f0", name="F", empire_id="e", system_id="s", ships=ships)
        assert f.strength == (50 + 20) + (30 + 20)

    def test_ship_count_excludes_destroyed(self):
        ships = [_make_ship(hull=50), _make_ship(hull=0)]
        f = CampaignFleet(id="f0", name="F", empire_id="e", system_id="s", ships=ships)
        assert f.ship_count == 1

    def test_remove_destroyed_ships(self):
        ships = [_make_ship(hull=50), _make_ship(hull=0), _make_ship(hull=10)]
        f = CampaignFleet(id="f0", name="F", empire_id="e", system_id="s", ships=ships)
        removed = f.remove_destroyed_ships()
        assert removed == 1
        assert len(f.ships) == 2


# ---------------------------------------------------------------------------
# CampaignManager: registration
# ---------------------------------------------------------------------------


class TestCampaignManagerRegistration:
    def test_add_system(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        mgr.add_system(sys)
        assert "s0" in mgr.star_systems

    def test_add_empire_marks_home_explored(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        mgr.add_system(sys)
        empire = _make_empire("e0", "s0")
        mgr.add_empire(empire)
        assert mgr.star_systems["s0"].is_explored

    def test_add_fleet_links_to_empire(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        empire = _make_empire("e0", "s0")
        mgr.add_system(sys)
        mgr.add_empire(empire)
        fleet = _make_fleet("f0", "e0", "s0")
        mgr.add_fleet(fleet)
        assert "f0" in mgr.empires["e0"].fleet_ids

    def test_add_colony_sets_planet_colony_id(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        planet = Planet(name="Sol I", is_surveyed=True, habitability=80.0)
        sys.planets.append(planet)
        empire = _make_empire("e0", "s0")
        empire.resources = {"minerals": 9999, "fuel_ice": 9999, "credits": 9999}
        mgr.add_system(sys)
        mgr.add_empire(empire)
        colony = Colony(
            id="col0",
            name="Base",
            empire_id="e0",
            system_id="s0",
            planet_name="Sol I",
        )
        mgr.add_colony(colony)
        assert sys.get_planet("Sol I").colony_id == "col0"


# ---------------------------------------------------------------------------
# CampaignManager: transit
# ---------------------------------------------------------------------------


class TestCampaignManagerTransit:
    def _setup_two_systems(self):
        mgr = CampaignManager()
        s1 = _make_system("s1", "Alpha")
        s2 = _make_system("s2", "Beta")
        link_systems(s1, s2, discovered=True, discovered_by="e0")
        empire = _make_empire("e0", "s1")
        mgr.add_system(s1)
        mgr.add_system(s2)
        mgr.add_empire(empire)
        fleet = _make_fleet("f0", "e0", "s1")
        mgr.add_fleet(fleet)
        return mgr

    def test_order_transit_success(self):
        mgr = self._setup_two_systems()
        ok, msg = mgr.order_fleet_transit("f0", "s2", transit_turns=1)
        assert ok
        assert mgr.fleets["f0"].is_in_transit

    def test_order_transit_no_jump_point(self):
        mgr = CampaignManager()
        s1 = _make_system("s1", "Alpha")
        s2 = _make_system("s2", "Beta")
        empire = _make_empire("e0", "s1")
        mgr.add_system(s1)
        mgr.add_system(s2)
        mgr.add_empire(empire)
        fleet = _make_fleet("f0", "e0", "s1")
        mgr.add_fleet(fleet)
        ok, msg = mgr.order_fleet_transit("f0", "s2")
        assert not ok

    def test_order_transit_unknown_fleet(self):
        mgr = CampaignManager()
        ok, msg = mgr.order_fleet_transit("nonexistent", "s2")
        assert not ok

    def test_transit_completes_after_turns(self):
        mgr = self._setup_two_systems()
        mgr.order_fleet_transit("f0", "s2", transit_turns=2)
        mgr.advance_turn()
        assert mgr.fleets["f0"].is_in_transit  # still in transit
        mgr.advance_turn()
        assert not mgr.fleets["f0"].is_in_transit
        assert mgr.fleets["f0"].system_id == "s2"

    def test_transit_in_transit_rejected(self):
        mgr = self._setup_two_systems()
        mgr.order_fleet_transit("f0", "s2", transit_turns=3)
        ok, msg = mgr.order_fleet_transit("f0", "s2")
        assert not ok


# ---------------------------------------------------------------------------
# CampaignManager: colonisation
# ---------------------------------------------------------------------------


class TestCampaignManagerColonisation:
    def _setup(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        planet = Planet(name="Sol I", is_surveyed=True, habitability=80.0)
        sys.planets.append(planet)
        empire = _make_empire("e0", "s0")
        empire.resources = {"minerals": 9999, "fuel_ice": 9999, "credits": 9999}
        mgr.add_system(sys)
        mgr.add_empire(empire)
        return mgr

    def test_colonise_success(self):
        mgr = self._setup()
        ok, msg = mgr.colonise_planet("e0", "s0", "Sol I")
        assert ok
        assert any(c.planet_name == "Sol I" for c in mgr.colonies.values())

    def test_colonise_awards_victory_points(self):
        mgr = self._setup()
        before = mgr.empires["e0"].victory_points
        mgr.colonise_planet("e0", "s0", "Sol I")
        assert mgr.empires["e0"].victory_points > before

    def test_colonise_unsurveyed_fails(self):
        mgr = self._setup()
        mgr.star_systems["s0"].planets[0].is_surveyed = False
        ok, msg = mgr.colonise_planet("e0", "s0", "Sol I")
        assert not ok

    def test_colonise_already_colonised_fails(self):
        mgr = self._setup()
        mgr.colonise_planet("e0", "s0", "Sol I")
        ok, msg = mgr.colonise_planet("e0", "s0", "Sol I")
        assert not ok

    def test_colonise_insufficient_resources_fails(self):
        mgr = self._setup()
        mgr.empires["e0"].resources["minerals"] = 0
        mgr.empires["e0"].resources["credits"] = 0
        ok, msg = mgr.colonise_planet("e0", "s0", "Sol I")
        assert not ok

    def test_colonise_unknown_planet_fails(self):
        mgr = self._setup()
        ok, msg = mgr.colonise_planet("e0", "s0", "NonExistent IV")
        assert not ok


# ---------------------------------------------------------------------------
# CampaignManager: survey
# ---------------------------------------------------------------------------


class TestCampaignManagerSurvey:
    def test_survey_requires_fleet_in_system(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        empire = _make_empire("e0", "s0")
        mgr.add_system(sys)
        mgr.add_empire(empire)
        ok, msg = mgr.survey_system("e0", "s0")
        assert not ok

    def test_survey_marks_system_explored(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        planet = Planet(name="Sol I")
        sys.planets.append(planet)
        empire = _make_empire("e0", "s0")
        mgr.add_system(sys)
        mgr.add_empire(empire)
        fleet = _make_fleet("f0", "e0", "s0")
        mgr.add_fleet(fleet)
        ok, msg = mgr.survey_system("e0", "s0")
        assert ok
        assert mgr.star_systems["s0"].is_explored
        assert mgr.star_systems["s0"].planets[0].is_surveyed

    def test_survey_awards_victory_points(self):
        mgr = CampaignManager()
        home = _make_system("s0", "Sol")
        new_sys = _make_system("s1", "Vega")
        empire = _make_empire("e0", "s0")
        mgr.add_system(home)
        mgr.add_system(new_sys)
        mgr.add_empire(empire)
        # Place a fleet in the new (unsurveyed) system
        fleet = _make_fleet("f0", "e0", "s1")
        mgr.add_fleet(fleet)
        before = empire.victory_points
        mgr.survey_system("e0", "s1")
        assert empire.victory_points > before


# ---------------------------------------------------------------------------
# CampaignManager: turn advancement
# ---------------------------------------------------------------------------


class TestCampaignManagerTurns:
    def test_turn_increments(self):
        mgr = CampaignManager()
        mgr.advance_turn()
        assert mgr.turn == 1

    def test_colony_resources_collected_each_turn(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        planet = Planet(name="Sol I", is_surveyed=True)
        sys.planets.append(planet)
        empire = _make_empire("e0", "s0")
        empire.resources = {"minerals": 0.0, "fuel_ice": 0.0, "credits": 0.0}
        mgr.add_system(sys)
        mgr.add_empire(empire)
        colony = Colony(
            id="col0",
            name="Test",
            empire_id="e0",
            system_id="s0",
            planet_name="Sol I",
            production={"minerals": 10.0},
        )
        mgr.add_colony(colony)
        # Link planet to colony directly
        planet.colony_id = "col0"
        mgr.advance_turn()
        assert mgr.empires["e0"].resources["minerals"] == pytest.approx(10.0)

    def test_advance_turn_returns_events(self):
        mgr = CampaignManager()
        events = mgr.advance_turn()
        assert isinstance(events, list)

    def test_contested_system_detected(self):
        mgr = CampaignManager()
        s1 = _make_system("s1", "Alpha")
        e1 = _make_empire("e1", "s1")
        e2 = _make_empire("e2", "s1")
        mgr.add_system(s1)
        mgr.add_empire(e1)
        mgr.add_empire(e2)
        f1 = _make_fleet("f1", "e1", "s1")
        f2 = _make_fleet("f2", "e2", "s1")
        mgr.add_fleet(f1)
        mgr.add_fleet(f2)
        events = mgr.advance_turn()
        combat_events = [e for e in events if e.event_type == "combat"]
        assert len(combat_events) >= 1


# ---------------------------------------------------------------------------
# CampaignManager: generate_galaxy
# ---------------------------------------------------------------------------


class TestGenerateGalaxy:
    def test_returns_campaign_manager(self):
        mgr = CampaignManager.generate_galaxy(num_systems=3, num_empires=2, seed=42)
        assert isinstance(mgr, CampaignManager)

    def test_correct_number_of_systems(self):
        mgr = CampaignManager.generate_galaxy(num_systems=5, num_empires=2, seed=1)
        assert len(mgr.star_systems) == 5

    def test_correct_number_of_empires(self):
        mgr = CampaignManager.generate_galaxy(num_systems=4, num_empires=2, seed=2)
        assert len(mgr.empires) == 2

    def test_each_empire_has_fleet(self):
        mgr = CampaignManager.generate_galaxy(num_systems=4, num_empires=2, seed=3)
        for empire in mgr.empires.values():
            assert len(empire.fleet_ids) >= 1

    def test_systems_have_jump_points(self):
        mgr = CampaignManager.generate_galaxy(num_systems=4, num_empires=2, seed=4)
        total_jump_points = sum(
            len(s.jump_points) for s in mgr.star_systems.values()
        )
        assert total_jump_points >= 2

    def test_reproducible_with_seed(self):
        mgr1 = CampaignManager.generate_galaxy(num_systems=4, num_empires=2, seed=99)
        mgr2 = CampaignManager.generate_galaxy(num_systems=4, num_empires=2, seed=99)
        names1 = sorted(s.name for s in mgr1.star_systems.values())
        names2 = sorted(s.name for s in mgr2.star_systems.values())
        assert names1 == names2

    def test_more_empires_than_systems_clamped(self):
        mgr = CampaignManager.generate_galaxy(num_systems=2, num_empires=5, seed=0)
        assert len(mgr.empires) <= 2

    def test_home_systems_explored(self):
        mgr = CampaignManager.generate_galaxy(num_systems=3, num_empires=2, seed=7)
        for empire in mgr.empires.values():
            home = mgr.star_systems[empire.home_system_id]
            assert home.is_explored


# ---------------------------------------------------------------------------
# CampaignManager: query helpers
# ---------------------------------------------------------------------------


class TestCampaignManagerQueries:
    def test_fleets_in_system(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        empire = _make_empire("e0", "s0")
        mgr.add_system(sys)
        mgr.add_empire(empire)
        f1 = _make_fleet("f1", "e0", "s0")
        f2 = _make_fleet("f2", "e0", "s0")
        f2.transit_destination = "s1"  # in transit, should not appear
        mgr.add_fleet(f1)
        mgr.add_fleet(f2)
        present = mgr.fleets_in_system("s0")
        assert len(present) == 1
        assert present[0].id == "f1"

    def test_empire_fleet_strength(self):
        mgr = CampaignManager()
        sys = _make_system("s0", "Sol")
        empire = _make_empire("e0", "s0")
        mgr.add_system(sys)
        mgr.add_empire(empire)
        ships = [_make_ship(hull=50), _make_ship(hull=30)]
        fleet = CampaignFleet(
            id="f0", name="F", empire_id="e0", system_id="s0", ships=ships
        )
        mgr.add_fleet(fleet)
        strength = mgr.empire_fleet_strength("e0")
        assert strength > 0

    def test_systems_controlled_by(self):
        mgr = CampaignManager()
        s1 = _make_system("s1", "Alpha")
        s2 = _make_system("s2", "Beta")
        s1.controlling_empire_id = "e0"
        mgr.add_system(s1)
        mgr.add_system(s2)
        controlled = mgr.systems_controlled_by("e0")
        assert len(controlled) == 1
        assert controlled[0].id == "s1"
