"""Example battle simulation with logging and map visualization."""

import sys
sys.path.insert(0, '..')

from ship_combat.fleet_setup import demo_fleets
from ship_combat.battle_sim import battle
from ship_combat.battle_logger import BattleLogger
from ship_combat.battle_map import BattleMap


def run_logged_battle():
    """Run a battle with full logging and visualization."""

    print("=" * 80)
    print("BATTLE SIMULATOR WITH LOGGING AND VISUALIZATION")
    print("=" * 80)

    # Create logger and map
    logger = BattleLogger(verbose=False)  # Set verbose=False to reduce console spam
    battle_map = BattleMap(width=60, height=30, scale=3.0)

    # Get demo fleets
    fleet_a, fleet_b = demo_fleets()

    print("\nInitial Battlefield:")
    print(battle_map.render(fleet_a, fleet_b, show_grid=True))

    print("\nTactical Overview:")
    print(battle_map.render_tactical(fleet_a, fleet_b))

    # Run battle with logging
    print("\n" + "=" * 80)
    print("BATTLE BEGINS")
    print("=" * 80)

    battle(fleet_a, fleet_b, rounds=5, logger=logger, battle_map=battle_map, show_map=True)

    # Export logs
    logger.export_json("battle_log.json")
    logger.export_text("battle_log.txt")

    print("\n" + "=" * 80)
    print("Battle logs exported to:")
    print("  - battle_log.json (structured data)")
    print("  - battle_log.txt  (human readable)")
    print("=" * 80)

    # Get summary statistics
    summary = logger.get_summary()

    print("\n" + "=" * 80)
    print("DETAILED STATISTICS")
    print("=" * 80)
    print(f"\nTotal Rounds: {summary['total_rounds']}")
    print(f"Total Events: {summary['total_events']}")
    print(f"Total Damage: {summary['total_damage_dealt']}")
    print(f"Shots Fired: {summary['total_shots_fired']}")
    print(f"Hits: {summary['total_hits']}")
    print(f"Misses: {summary['total_misses']}")
    print(f"Accuracy: {summary['overall_accuracy']:.1f}%")
    print(f"Critical Hits: {summary['critical_hits']}")

    if summary['ships_destroyed']:
        print(f"\nShips Destroyed:")
        for ship in summary['ships_destroyed']:
            print(f"  - {ship}")

    print("\n" + "=" * 80)
    print("Round-by-Round Breakdown:")
    print("=" * 80)

    for round_data in summary['round_summaries']:
        round_num = round_data['round']
        damage = round_data['total_damage_dealt']
        shots = round_data['total_shots_fired']
        hits = round_data['total_hits']
        acc = round_data['accuracy']
        crits = round_data['critical_hits']
        destroyed = round_data['ships_destroyed']

        print(f"\nRound {round_num}:")
        print(f"  Damage: {damage}")
        print(f"  Shots: {shots} (Hits: {hits}, Accuracy: {acc:.1f}%)")
        if crits > 0:
            print(f"  Critical Hits: {crits}")
        if destroyed:
            print(f"  Ships Destroyed: {', '.join(destroyed)}")


def run_compact_visualization():
    """Run a battle with compact visualization only."""

    print("\n" + "=" * 80)
    print("COMPACT VISUALIZATION MODE")
    print("=" * 80)

    battle_map = BattleMap(width=60, height=25, scale=2.5)
    fleet_a, fleet_b = demo_fleets()

    print("\nBefore Battle:")
    print(battle_map.render_compact(fleet_a, fleet_b))

    # Run 3 rounds
    battle(fleet_a, fleet_b, rounds=3)

    print("\nAfter Battle:")
    print(battle_map.render_compact(fleet_a, fleet_b))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Battle simulator with logging example")
    parser.add_argument(
        "--mode",
        choices=["full", "compact"],
        default="full",
        help="Visualization mode (default: full)"
    )

    args = parser.parse_args()

    if args.mode == "full":
        run_logged_battle()
    else:
        run_compact_visualization()
