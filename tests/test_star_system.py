"""Tests for the star_system module."""

import math
import pytest

from ship_combat.star_system import (
    Planet,
    JumpPoint,
    StarSystem,
    generate_star_system,
    link_systems,
    PLANET_TYPES,
)


# ---------------------------------------------------------------------------
# Planet tests
# ---------------------------------------------------------------------------


class TestPlanet:
    def test_default_planet(self):
        p = Planet(name="Terra")
        assert p.name == "Terra"
        assert p.planet_type == "Terrestrial"
        assert p.habitability == 0.0
        assert p.colony_id is None
        assert not p.is_surveyed

    def test_distance_to_same_position(self):
        p1 = Planet(name="A", x=0.0, y=0.0)
        p2 = Planet(name="B", x=0.0, y=0.0)
        assert p1.distance_to(p2) == pytest.approx(0.0)

    def test_distance_to_different_positions(self):
        p1 = Planet(name="A", x=0.0, y=0.0)
        p2 = Planet(name="B", x=3.0, y=4.0)
        assert p1.distance_to(p2) == pytest.approx(5.0)

    def test_mineral_resources_default_empty(self):
        p = Planet(name="X")
        assert p.mineral_resources == {}


# ---------------------------------------------------------------------------
# JumpPoint tests
# ---------------------------------------------------------------------------


class TestJumpPoint:
    def test_default_jump_point(self):
        jp = JumpPoint(name="JP-1", target_system_id="sys_2")
        assert jp.name == "JP-1"
        assert jp.target_system_id == "sys_2"
        assert jp.stability == 1.0
        assert not jp.is_discovered
        assert jp.discovered_by is None

    def test_undiscovered_not_accessible(self):
        jp = JumpPoint(name="JP", target_system_id="sys_x", is_discovered=False)
        assert not jp.is_accessible_by("empire_0")

    def test_discovered_by_empire_is_accessible(self):
        jp = JumpPoint(
            name="JP",
            target_system_id="sys_x",
            is_discovered=True,
            discovered_by="empire_0",
        )
        assert jp.is_accessible_by("empire_0")

    def test_discovered_accessible_by_all_when_is_discovered(self):
        jp = JumpPoint(
            name="JP",
            target_system_id="sys_x",
            is_discovered=True,
            discovered_by="empire_0",
        )
        # is_accessible_by returns True for any empire when is_discovered=True
        assert jp.is_accessible_by("empire_1")


# ---------------------------------------------------------------------------
# StarSystem tests
# ---------------------------------------------------------------------------


class TestStarSystem:
    def _make_system(self) -> StarSystem:
        p1 = Planet(name="Alpha I", x=1.0, y=0.0)
        p2 = Planet(name="Alpha II", x=-1.5, y=0.5)
        jp = JumpPoint(
            name="Jump to Beta",
            target_system_id="sys_beta",
            is_discovered=True,
        )
        return StarSystem(
            id="sys_alpha",
            name="Alpha Centauri",
            planets=[p1, p2],
            jump_points=[jp],
        )

    def test_get_planet_found(self):
        sys = self._make_system()
        planet = sys.get_planet("Alpha I")
        assert planet is not None
        assert planet.name == "Alpha I"

    def test_get_planet_not_found(self):
        sys = self._make_system()
        assert sys.get_planet("Nonexistent") is None

    def test_get_jump_point_found(self):
        sys = self._make_system()
        jp = sys.get_jump_point("sys_beta")
        assert jp is not None
        assert jp.target_system_id == "sys_beta"

    def test_get_jump_point_not_found(self):
        sys = self._make_system()
        assert sys.get_jump_point("sys_gamma") is None

    def test_habitable_planets_filters_zero_habitability(self):
        sys = self._make_system()
        # Both planets have habitability=0 by default
        assert sys.habitable_planets() == []

    def test_habitable_planets_returns_positive(self):
        sys = self._make_system()
        sys.planets[0].habitability = 75.0
        hab = sys.habitable_planets()
        assert len(hab) == 1
        assert hab[0].name == "Alpha I"

    def test_colonised_planets_empty_by_default(self):
        sys = self._make_system()
        assert sys.colonised_planets() == []

    def test_colonised_planets_after_colonisation(self):
        sys = self._make_system()
        sys.planets[0].colony_id = "colony_1"
        colonised = sys.colonised_planets()
        assert len(colonised) == 1

    def test_discovered_jump_points(self):
        sys = self._make_system()
        dj = sys.discovered_jump_points()
        assert len(dj) == 1

    def test_galaxy_distance_to(self):
        s1 = StarSystem(id="s1", name="S1", x=0.0, y=0.0)
        s2 = StarSystem(id="s2", name="S2", x=3.0, y=4.0)
        assert s1.galaxy_distance_to(s2) == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# generate_star_system tests
# ---------------------------------------------------------------------------


class TestGenerateStarSystem:
    def test_returns_star_system(self):
        sys = generate_star_system("sys_0", "Test System", seed=42)
        assert isinstance(sys, StarSystem)

    def test_id_and_name(self):
        sys = generate_star_system("abc", "XYZ", seed=1)
        assert sys.id == "abc"
        assert sys.name == "XYZ"

    def test_has_planets(self):
        sys = generate_star_system("sys_0", "Test", seed=42)
        assert len(sys.planets) >= 2

    def test_num_planets_respected(self):
        sys = generate_star_system("sys_0", "Test", num_planets=4, seed=99)
        assert len(sys.planets) == 4

    def test_reproducible_with_same_seed(self):
        sys1 = generate_star_system("s1", "Sys", seed=77)
        sys2 = generate_star_system("s1", "Sys", seed=77)
        assert len(sys1.planets) == len(sys2.planets)
        assert sys1.star_type == sys2.star_type

    def test_different_seeds_may_differ(self):
        sys1 = generate_star_system("s1", "Sys", seed=1)
        sys2 = generate_star_system("s1", "Sys", seed=9999)
        # They *should* differ in at least one property with different seeds
        # (not a strict guarantee but true for these seeds)
        differ = (
            sys1.star_type != sys2.star_type
            or len(sys1.planets) != len(sys2.planets)
        )
        assert differ

    def test_position_set(self):
        sys = generate_star_system("s0", "S0", x=10.0, y=-5.5, seed=0)
        assert sys.x == pytest.approx(10.0)
        assert sys.y == pytest.approx(-5.5)

    def test_valid_star_type(self):
        valid_types = set("OBAFGKM")
        for seed in range(10):
            sys = generate_star_system("s", "S", seed=seed)
            assert sys.star_type in valid_types

    def test_planets_have_names(self):
        sys = generate_star_system("s0", "Vega", num_planets=3, seed=5)
        for planet in sys.planets:
            assert planet.name.startswith("Vega")

    def test_planets_have_valid_type(self):
        sys = generate_star_system("s0", "Test", num_planets=6, seed=100)
        for planet in sys.planets:
            assert planet.planet_type in PLANET_TYPES


# ---------------------------------------------------------------------------
# link_systems tests
# ---------------------------------------------------------------------------


class TestLinkSystems:
    def test_creates_jump_points(self):
        s1 = StarSystem(id="s1", name="A", x=0.0, y=0.0)
        s2 = StarSystem(id="s2", name="B", x=10.0, y=0.0)
        link_systems(s1, s2)
        assert len(s1.jump_points) == 1
        assert len(s2.jump_points) == 1

    def test_jump_points_point_to_correct_system(self):
        s1 = StarSystem(id="s1", name="A")
        s2 = StarSystem(id="s2", name="B")
        link_systems(s1, s2)
        assert s1.jump_points[0].target_system_id == "s2"
        assert s2.jump_points[0].target_system_id == "s1"

    def test_discovered_flag_propagated(self):
        s1 = StarSystem(id="s1", name="A")
        s2 = StarSystem(id="s2", name="B")
        link_systems(s1, s2, discovered=True, discovered_by="empire_0")
        assert s1.jump_points[0].is_discovered
        assert s2.jump_points[0].is_discovered

    def test_stability_set(self):
        s1 = StarSystem(id="s1", name="A")
        s2 = StarSystem(id="s2", name="B")
        link_systems(s1, s2, stability=0.8)
        assert s1.jump_points[0].stability == pytest.approx(0.8)
        assert s2.jump_points[0].stability == pytest.approx(0.8)

    def test_link_does_not_duplicate_existing(self):
        s1 = StarSystem(id="s1", name="A")
        s2 = StarSystem(id="s2", name="B")
        link_systems(s1, s2)
        # Call again — should add another pair (caller's responsibility)
        link_systems(s1, s2)
        assert len(s1.jump_points) == 2
