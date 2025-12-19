#!/usr/bin/env python3
"""
Demonstration of the ship building and fleet generation system.

This script shows various ways to create ships and fleets using the new
modular component system.
"""

from ship_combat.ship_builder import ShipBuilder, quick_ship, randomized_ship
from ship_combat.fleet_generator import (
    FleetGenerator,
    quick_fleet,
    symmetric_fleets,
)


def demo_ship_builder():
    """Demonstrate the fluent ShipBuilder API."""
    print("\n" + "=" * 70)
    print("SHIP BUILDER DEMONSTRATION")
    print("=" * 70)
    
    # Example 1: Simple ship with defaults
    print("\n1. Simple frigate with defaults:")
    frigate = ShipBuilder("Aurora").build()
    print(f"   {frigate.name} ({frigate.class_name})")
    print(f"   Hull: {frigate.hull}, Shield: {frigate.shield}/{frigate.max_shield}")
    print(f"   Speed: {frigate.speed}, Maneuver: {frigate.maneuver}")
    print(f"   Weapons: {len(frigate.weapons.batteries)} batteries, {frigate.weapons.missiles} missiles")
    
    # Example 2: Custom battleship with full configuration
    print("\n2. Custom battleship with full configuration:")
    battleship = (ShipBuilder("Eternal Vigilance")
        .with_class("Battleship")
        .with_hull(120)
        .with_shield("capital")
        .with_reactor("military")
        .with_engine("battleship_standard")
        .with_weapon_loadout("battleship_nova", missiles=10)
        .with_crew(500, leadership=10, boarding_strength=12)
        .with_position(0.0, 0.0, 0.0)
        .with_ai_personality("Calculating and methodical")
        .build())
    
    print(f"   {battleship.name} ({battleship.class_name})")
    print(f"   Hull: {battleship.hull}, Shield: {battleship.shield}/{battleship.max_shield}")
    print(f"   Power: {battleship.max_power}, Crew: {battleship.crew}")
    print(f"   Leadership: {battleship.leadership}, Boarding: {battleship.boarding_strength}")
    print(f"   AI: {battleship.ai}")
    for battery in battleship.weapons.batteries:
        print(f"   - {battery.name} (Rating {battery.rating}, {battery.range} range)")
    
    # Example 3: Quick ship creation
    print("\n3. Quick ship creation:")
    cruiser = quick_ship(
        "Vengeance",
        class_name="Cruiser",
        hull=90,
        shield_type="heavy",
        engine_type="cruiser_standard",
        weapon_loadout="cruiser_plasma",
        missiles=6
    )
    print(f"   {cruiser.name} ({cruiser.class_name})")
    print(f"   Hull: {cruiser.hull}, Shield: {cruiser.shield}")
    print(f"   Weapons: {len(cruiser.weapons.batteries)} batteries")
    
    # Example 4: Randomized ships with variance
    print("\n4. Randomized ships with 20% variance:")
    for i in range(3):
        ship = randomized_ship(f"Random-{i+1}", "Frigate", base_hull=50, variance=20)
        print(f"   {ship.name}: Hull {ship.hull}, Shield {ship.shield}, " +
              f"Crew {ship.crew}, Speed {ship.speed}")


def demo_fleet_generator():
    """Demonstrate fleet generation with various compositions."""
    print("\n" + "=" * 70)
    print("FLEET GENERATOR DEMONSTRATION")
    print("=" * 70)
    
    gen = FleetGenerator(seed=42)  # Use seed for reproducibility in demo
    
    # Example 1: Balanced fleet
    print("\n1. Balanced fleet composition (10 ships):")
    fleet = gen.generate_fleet(size=10, composition="balanced", variance=10)
    class_counts = {}
    for ship in fleet:
        class_counts[ship.class_name] = class_counts.get(ship.class_name, 0) + 1
    for class_name, count in sorted(class_counts.items()):
        print(f"   {class_name}: {count} ships")
    
    # Example 2: Strike force
    print("\n2. Strike force composition (6 ships):")
    strike_force = gen.generate_fleet(size=6, composition="strike_force", prefix="Strike")
    for ship in strike_force:
        print(f"   {ship.name} ({ship.class_name}): Hull {ship.hull}, Speed {ship.speed}")
    
    # Example 3: Capital fleet
    print("\n3. Capital fleet composition (5 ships):")
    capital_fleet = gen.generate_fleet(size=5, composition="capital_fleet", prefix="Capital")
    for ship in capital_fleet:
        weapons_rating = sum(b.rating for b in ship.weapons.batteries)
        print(f"   {ship.name} ({ship.class_name}): " +
              f"Hull {ship.hull}, Weapons Rating {weapons_rating}")
    
    # Example 4: Custom fleet composition
    print("\n4. Custom fleet composition:")
    custom_fleet = gen.generate_custom_fleet({
        "Frigate": 4,
        "Cruiser": 2,
        "Battleship": 1,
    }, prefix="Task Force")
    for ship in custom_fleet:
        print(f"   {ship.name} ({ship.class_name})")


def demo_symmetric_fleets():
    """Demonstrate symmetric fleet generation for battles."""
    print("\n" + "=" * 70)
    print("SYMMETRIC FLEETS FOR BATTLE")
    print("=" * 70)
    
    # Generate two opposing fleets
    fleet_a, fleet_b = symmetric_fleets(
        size=5,
        composition="balanced",
        fleet_a_prefix="Imperial",
        fleet_b_prefix="Rebel",
        separation=100.0,
        seed=123
    )
    
    print("\nFleet A (Imperial):")
    total_hull_a = 0
    for ship in fleet_a:
        print(f"   {ship.name} ({ship.class_name}): " +
              f"Hull {ship.hull}, Position ({ship.x:.1f}, {ship.y:.1f})")
        total_hull_a += ship.hull
    print(f"   Total Fleet Hull: {total_hull_a}")
    
    print("\nFleet B (Rebel):")
    total_hull_b = 0
    for ship in fleet_b:
        print(f"   {ship.name} ({ship.class_name}): " +
              f"Hull {ship.hull}, Position ({ship.x:.1f}, {ship.y:.1f})")
        total_hull_b += ship.hull
    print(f"   Total Fleet Hull: {total_hull_b}")
    
    # Calculate average separation
    avg_x_a = sum(s.x for s in fleet_a) / len(fleet_a)
    avg_x_b = sum(s.x for s in fleet_b) / len(fleet_b)
    separation = avg_x_b - avg_x_a
    print(f"\nAverage fleet separation: {separation:.1f} units")


def demo_quick_functions():
    """Demonstrate quick convenience functions."""
    print("\n" + "=" * 70)
    print("QUICK CONVENIENCE FUNCTIONS")
    print("=" * 70)
    
    # Quick fleet with defaults
    print("\n1. Quick fleet with defaults:")
    fleet = quick_fleet(size=3, seed=456)
    for ship in fleet:
        print(f"   {ship.name} ({ship.class_name})")
    
    # Quick fleet with custom parameters
    print("\n2. Quick raiding party:")
    raiders = quick_fleet(
        size=5,
        composition="raiding_party",
        variance=15,
        prefix="Raider",
        seed=789
    )
    for ship in raiders:
        print(f"   {ship.name} ({ship.class_name}): Speed {ship.speed}")


def demo_variance_comparison():
    """Demonstrate the effect of variance on fleet diversity."""
    print("\n" + "=" * 70)
    print("VARIANCE COMPARISON")
    print("=" * 70)
    
    print("\n1. Low variance (5%):")
    gen_low = FleetGenerator(seed=999)
    fleet_low = gen_low.generate_fleet(size=5, composition="strike_force", variance=5)
    hulls = [s.hull for s in fleet_low]
    print(f"   Hull values: {hulls}")
    print(f"   Range: {min(hulls)} - {max(hulls)}")
    
    print("\n2. High variance (25%):")
    gen_high = FleetGenerator(seed=999)
    fleet_high = gen_high.generate_fleet(size=5, composition="strike_force", variance=25)
    hulls = [s.hull for s in fleet_high]
    print(f"   Hull values: {hulls}")
    print(f"   Range: {min(hulls)} - {max(hulls)}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print(" PYODIDE SHIP COMBAT - SHIP BUILDING SYSTEM DEMONSTRATION")
    print("=" * 70)
    print("\nThis demo shows the new modular ship building and fleet generation")
    print("system with components, builders, and fleet generators.")
    
    demo_ship_builder()
    demo_fleet_generator()
    demo_symmetric_fleets()
    demo_quick_functions()
    demo_variance_comparison()
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nFor more examples, see SHIP_BUILDING.md documentation.")
    print()


if __name__ == "__main__":
    main()
