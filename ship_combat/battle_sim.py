# Battle Simulator for Pyodide and CLI
# Implements battle phases using dataclasses defined in models.py
# Runs headless with optional CLI arguments.

from __future__ import annotations

import argparse
import asyncio
import random
import math
import logging
from typing import List, Optional

from .models import Ship
from .fleet_setup import demo_fleets
from .battle_logger import BattleLogger
from .battle_map import BattleMap, render_quick_status

try:
    import rolldice  # type: ignore
except Exception:  # rolldice may not be installed in Pyodide yet
    rolldice = None  # will be loaded dynamically


def get_rolldice():
    """Get rolldice module, checking sys.modules for mocked version."""
    global rolldice
    if rolldice is not None:
        return rolldice
    # Check if it's been mocked in tests
    import sys
    if "rolldice" in sys.modules:
        rolldice = sys.modules["rolldice"]
        return rolldice
    return None

BATTLE_ORDERS = [
    "Brace for Impact",
    "Lock On",
    "All Power to Shields",
    "Reload Ordnance",
    "Boarding Party",
    "Fire Everything",
    "Combat Repairs",
    "Disengage",
    "Offensive Maneuvers",
    "Run Silent",
    "Evasive Maneuvers",
    "Pursue Target",
    "Power to Weapons",
    "Power to Engines",
]

HAZARDS = {
    "System Failure": "Random system takes damage",
    "Gravity Well": "Attack and defense rolls suffer -1",
    "Minefield": "Ship suffers explosive hull damage",
    "Nebula": "Sensors obscured, -1 attack",
    "Radiation Burst": "All systems lose efficiency",
}

# simple mapping of range bands to maximum distance units
RANGE_BANDS = {
    "point": 5.0,
    "short": 10.0,
    "standard": 20.0,
    "long": 40.0,
}


# orientation helper functions
def yaw_to_target(ship: Ship, target: Ship) -> float:
    """Return yaw angle from ship to target in degrees."""
    return math.degrees(math.atan2(target.y - ship.y, target.x - ship.x)) % 360


def pitch_to_target(ship: Ship, target: Ship) -> float:
    """Return elevation angle from ship to target in degrees."""
    horiz = math.hypot(target.x - ship.x, target.y - ship.y)
    return math.degrees(math.atan2(target.z - ship.z, horiz))


def in_arc(ship: Ship, target: Ship, arc: str) -> bool:
    """Return True if target lies within the specified firing arc."""
    yaw = (yaw_to_target(ship, target) - ship.heading) % 360
    pitch = pitch_to_target(ship, target) - ship.pitch
    if arc == "omni":
        return True
    if arc == "fore":
        return yaw <= 45 or yaw >= 315
    if arc == "aft":
        return 135 <= yaw <= 225
    if arc == "port":
        return 45 <= yaw <= 135
    if arc == "starboard":
        return 225 <= yaw <= 315
    if arc == "dorsal":
        return pitch > 20
    if arc == "ventral":
        return pitch < -20
    return True


def in_range(ship: Ship, target: Ship, rng: str) -> bool:
    """Return True if target is within the range band."""
    max_dist = RANGE_BANDS.get(rng, RANGE_BANDS["standard"])
    return distance(ship, target) <= max_dist


def can_fire(ship: Ship, target: Ship, battery) -> bool:
    """Determine if a weapon battery can fire at the given target."""
    return in_range(ship, target, battery.range) and in_arc(ship, target, battery.arc)


def distance(a: Ship, b: Ship) -> float:
    """Euclidean distance between two ships."""
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def update_formation_position(ship: Ship) -> None:
    """Update ship position to maintain formation with leader."""
    if ship.formation_leader is None or ship.formation_leader.hull <= 0:
        return

    leader = ship.formation_leader
    # Calculate target position relative to leader
    target_x = leader.x + ship.formation_offset_x
    target_y = leader.y + ship.formation_offset_y
    target_z = leader.z + ship.formation_offset_z

    # Move toward formation position (interpolate for smooth movement)
    interp_factor = 0.3  # How quickly to adjust to formation
    ship.x += (target_x - ship.x) * interp_factor
    ship.y += (target_y - ship.y) * interp_factor
    ship.z += (target_z - ship.z) * interp_factor

    # Match leader's heading
    ship.heading = leader.heading
    ship.pitch = leader.pitch


def calculate_intercept_course(ship: Ship, target: Ship) -> tuple[float, float]:
    """Calculate heading and pitch to intercept a moving target."""
    # Predict where target will be
    time_to_intercept = distance(ship, target) / max(ship.speed, 1)

    # Predict target position
    target_yaw = math.radians(target.heading)
    target_pitch = math.radians(target.pitch)
    pred_x = target.x + math.cos(target_yaw) * math.cos(target_pitch) * target.speed * time_to_intercept
    pred_y = target.y + math.sin(target_yaw) * math.cos(target_pitch) * target.speed * time_to_intercept
    pred_z = target.z + math.sin(target_pitch) * target.speed * time_to_intercept

    # Calculate intercept heading
    intercept_heading = math.degrees(math.atan2(pred_y - ship.y, pred_x - ship.x)) % 360
    horiz = math.hypot(pred_x - ship.x, pred_y - ship.y)
    intercept_pitch = math.degrees(math.atan2(pred_z - ship.z, horiz))

    return intercept_heading, intercept_pitch


def apply_evasive_maneuvers(ship: Ship) -> None:
    """Apply random evasive heading changes."""
    if not ship.evasion_active:
        return

    # Random evasive adjustments based on maneuverability
    max_turn = ship.maneuver * 15  # More maneuverable ships can dodge better
    ship.heading = (ship.heading + random.uniform(-max_turn, max_turn)) % 360
    ship.pitch = max(-90, min(90, ship.pitch + random.uniform(-max_turn/2, max_turn/2)))


def move_fleet(fleet: List[Ship]) -> None:
    """Advance each ship based on its speed, heading, and navigation state."""
    for ship in fleet:
        # Power affects engine performance
        engine_power = ship.get_power_modifier("engines")
        effective_speed = ship.speed * engine_power

        # Handle pursuit mechanics
        if ship.pursuing_target and ship.pursuing_target.hull > 0:
            heading, pitch = calculate_intercept_course(ship, ship.pursuing_target)
            # Gradually adjust heading toward intercept course
            ship.heading = heading
            ship.pitch = pitch

        # Apply evasive maneuvers if active
        apply_evasive_maneuvers(ship)

        # Normal movement
        yaw_rad = math.radians(ship.heading)
        pitch_rad = math.radians(ship.pitch)
        ship.x += math.cos(yaw_rad) * math.cos(pitch_rad) * effective_speed
        ship.y += math.sin(yaw_rad) * math.cos(pitch_rad) * effective_speed
        ship.z += math.sin(pitch_rad) * effective_speed

        # Formation following overrides normal movement
        update_formation_position(ship)


async def install_dependencies() -> None:
    """Install runtime packages when running in Pyodide."""
    global rolldice
    if rolldice is not None:
        return
    try:
        import micropip  # type: ignore
    except Exception:
        return
    await micropip.install("py-rolldice")
    import rolldice as _rolldice  # type: ignore

    rolldice = _rolldice


# ---------------- Battle Phases -----------------


def select_orders(fleet: List[Ship], enemy_fleet: List[Ship] = None, logger: Optional[BattleLogger] = None) -> None:
    """Randomly assign orders to each ship."""
    for ship in fleet:
        ship.order = random.choice(BATTLE_ORDERS)
        ship.attack_mod = 0
        ship.defense_mod = 0
        ship.repair_priority = False
        ship.evasion_active = False

        # Reset power allocation to baseline
        ship.power_allocation = {
            "weapons": 33,
            "shields": 33,
            "engines": 34
        }

        if ship.order == "Lock On":
            ship.attack_mod += 2
        elif ship.order == "Brace for Impact":
            ship.defense_mod += 2
        elif ship.order == "Fire Everything":
            ship.attack_mod += 1
        elif ship.order == "All Power to Shields":
            ship.defense_mod += 1
        elif ship.order == "Combat Repairs":
            ship.repair_priority = True
            ship.defense_mod += 1
        elif ship.order == "Disengage":
            ship.attack_mod -= 2
            ship.defense_mod += 1
        elif ship.order == "Offensive Maneuvers":
            ship.attack_mod += 1
            ship.defense_mod -= 1
        elif ship.order == "Run Silent":
            ship.attack_mod -= 1
            ship.defense_mod += 1
        elif ship.order == "Evasive Maneuvers":
            ship.evasion_active = True
            ship.defense_mod += 2
        elif ship.order == "Pursue Target":
            # Find nearest enemy to pursue
            if enemy_fleet:
                enemies = [e for e in enemy_fleet if e.hull > 0]
                if enemies:
                    ship.pursuing_target = min(enemies, key=lambda e: distance(ship, e))
            ship.attack_mod += 1
        elif ship.order == "Power to Weapons":
            ship.power_allocation["weapons"] = 60
            ship.power_allocation["shields"] = 20
            ship.power_allocation["engines"] = 20
        elif ship.order == "Power to Engines":
            ship.power_allocation["weapons"] = 20
            ship.power_allocation["shields"] = 20
            ship.power_allocation["engines"] = 60

        if logger:
            logger.log_order_selection(ship, ship.order)
        else:
            print(f"{ship.name} selects order: {ship.order}")


def apply_hazard(ship: Ship, hazard: str, logger: Optional[BattleLogger] = None) -> None:
    """Apply a named hazard effect to a single ship."""
    rd = get_rolldice()
    if rd is None:
        raise RuntimeError("rolldice not loaded")

    effect = ""
    if hazard == "System Failure":
        system_name = random.choice(list(ship.systems.keys()))
        ship.systems[system_name].damage(10)
        effect = f"Damages {system_name}, now {ship.systems[system_name].efficiency}%"
        if not logger:
            print(f"Hazard damages {ship.name}'s {system_name}, now {ship.systems[system_name].efficiency}%")
    elif hazard == "Gravity Well":
        ship.attack_mod -= 1
        ship.defense_mod -= 1
        effect = "-1 attack and defense"
        if not logger:
            print(f"{ship.name} caught in gravity well: -1 attack and defense")
    elif hazard == "Minefield":
        dmg, _ = rd.roll_dice("1d6")
        ship.hull = max(0, ship.hull - int(dmg))
        effect = f"{dmg} hull damage"
        if not logger:
            print(f"{ship.name} strikes a mine for {dmg} damage (hull {ship.hull})")
    elif hazard == "Nebula":
        ship.attack_mod -= 1
        effect = "-1 attack this round"
        if not logger:
            print(f"{ship.name} enters nebula: -1 attack this round")
    elif hazard == "Radiation Burst":
        for system in ship.systems.values():
            system.damage(5)
        effect = "All systems degrade"
        if not logger:
            print(f"{ship.name} hit by radiation burst: all systems degrade")

    if logger:
        logger.log_hazard(ship, hazard, effect)


def resolve_hazards(fleet: List[Ship], logger: Optional[BattleLogger] = None) -> None:
    """Randomly apply environmental hazards."""
    for ship in fleet:
        if not ship.systems:
            continue
        if random.random() < 0.1:
            hazard = random.choice(list(HAZARDS.keys()))
            if not logger:
                print(f"{ship.name} encounters hazard: {hazard}")
            apply_hazard(ship, hazard, logger)


def shooting_phase(attacking: List[Ship], defending: List[Ship], logger: Optional[BattleLogger] = None) -> None:
    """Resolve shooting between fleets with heat and critical hit mechanics."""
    rd = get_rolldice()
    if rd is None:
        raise RuntimeError("rolldice not loaded")
    for ship in attacking:
        if ship.hull <= 0:
            continue

        # Power allocation affects weapon accuracy
        weapon_power_mod = ship.get_power_modifier("weapons")

        targets = [t for t in defending if t.hull > 0]
        targets.sort(key=lambda t: distance(ship, t))
        if not targets:
            continue
        chosen = None
        valid_batteries = []
        for tgt in targets:
            # Check for heat and range/arc
            bats = [b for b in ship.weapons.batteries
                    if can_fire(ship, tgt, b) and not b.is_overheated()]
            if bats:
                chosen = tgt
                valid_batteries = bats
                break
        if not chosen:
            continue

        for battery in valid_batteries:
            # Add heat from firing
            overheated = battery.add_heat()
            if overheated:
                if logger:
                    logger.log_overheat(ship, battery.name)
                else:
                    print(f"{ship.name}'s {battery.name} overheats!")

            roll, _ = rd.roll_dice("2d20")
            # Apply power modifier to accuracy
            power_accuracy_bonus = int((weapon_power_mod - 1.0) * 5)
            attack_total = roll + ship.attack_mod + battery.accuracy + power_accuracy_bonus

            # Evasion provides defense bonus
            evasion_bonus = chosen.maneuver * 5 if chosen.evasion_active else 0
            defense_target = chosen.shield + chosen.defense_mod + evasion_bonus

            if attack_total > defense_target:
                # Check for critical hit (natural 20s or very high roll)
                is_critical = roll >= 38 or (attack_total - defense_target) >= 20
                dmg, _ = rd.roll_dice(battery.damage_dice)
                damage = int(dmg)

                if is_critical:
                    damage = int(damage * 1.5)  # 50% bonus damage
                    chosen.critical_damage_taken += 1
                    # Critical hits can damage a random system
                    if chosen.systems:
                        system_name = random.choice(list(chosen.systems.keys()))
                        chosen.systems[system_name].damage(15)
                        if not logger:
                            print(
                                f"CRITICAL HIT! {ship.name} strikes {chosen.name}'s {system_name}!"
                            )

                chosen.hull = max(0, chosen.hull - damage)

                if logger:
                    logger.log_shot(ship, chosen, battery.name, True, damage, is_critical)
                else:
                    hit_type = "CRITICAL" if is_critical else "hits"
                    print(
                        f"{ship.name} {hit_type} {chosen.name} with {battery.name} for {damage} (hull {chosen.hull})"
                    )

                if chosen.hull == 0:
                    if logger:
                        logger.log_ship_destroyed(chosen, ship)
                    else:
                        print(f"{chosen.name} destroyed!")
                    break
            else:
                if logger:
                    logger.log_shot(ship, chosen, battery.name, False)
                else:
                    print(f"{ship.name} misses {chosen.name} with {battery.name}")


def missile_phase(attacking: List[Ship], defending: List[Ship], logger: Optional[BattleLogger] = None) -> None:
    """Fire missiles if available."""
    rd = get_rolldice()
    if rd is None:
        raise RuntimeError("rolldice not loaded")
    for ship in attacking:
        if ship.weapons.missiles <= 0 or ship.hull <= 0:
            continue
        targets = [t for t in defending if t.hull > 0]
        if not targets:
            continue
        target = min(targets, key=lambda t: distance(ship, t))
        if not in_range(ship, target, "long"):
            continue
        ship.weapons.missiles -= 1
        dmg, _ = rd.roll_dice("3d6")
        damage = int(dmg)
        target.hull = max(0, target.hull - damage)

        if logger:
            logger.log_missile_launch(ship, target, damage)
        else:
            print(
                f"{ship.name} launches missile at {target.name} for {damage} (hull {target.hull})"
            )

        if target.hull == 0:
            if logger:
                logger.log_ship_destroyed(target, ship)
            else:
                print(f"{target.name} destroyed by missile!")


def boarding_phase(attacking: List[Ship], defending: List[Ship], logger: Optional[BattleLogger] = None) -> None:
    """Attempt boarding actions."""
    rd = get_rolldice()
    if rd is None:
        raise RuntimeError("rolldice not loaded")
    for ship in attacking:
        if ship.hull <= 0:
            continue
        if random.random() < 0.2:  # 20% chance to board
            targets = [t for t in defending if t.hull > 0]
            if not targets:
                continue
            target = min(targets, key=lambda t: distance(ship, t))
            if not in_range(ship, target, "point"):
                continue
            atk, _ = rd.roll_dice("1d20")
            attack_total = atk + ship.boarding_strength + ship.attack_mod
            defend_total = target.boarding_strength + target.defense_mod
            if attack_total > defend_total:
                dmg, _ = rd.roll_dice("1d10")
                damage = int(dmg)
                target.hull = max(0, target.hull - damage)

                if logger:
                    logger.log_boarding(ship, target, True, damage)
                else:
                    print(
                        f"{ship.name} boards {target.name} for {damage} damage (hull {target.hull})"
                    )

                if target.hull == 0:
                    if logger:
                        logger.log_ship_destroyed(target, ship)
                    else:
                        print(f"{target.name} captured and destroyed!")
            else:
                if logger:
                    logger.log_boarding(ship, target, False)
                else:
                    print(f"{ship.name} fails to board {target.name}")


def repair_phase(fleet: List[Ship], logger: Optional[BattleLogger] = None) -> None:
    """Attempt simple repairs on damaged systems."""
    rd = get_rolldice()
    if rd is None:
        raise RuntimeError("rolldice not loaded")
    for ship in fleet:
        damaged = [s for s in ship.systems.values() if s.status != "Operational"]
        chance = 1.0 if ship.repair_priority else 0.5
        if damaged and random.random() < chance:
            system = random.choice(damaged)
            system.repair(10)
            if logger:
                logger.log_repair(ship, system.effect or 'a system', system.efficiency)
            else:
                print(
                    f"{ship.name} repairs {system.effect or 'a system'} to {system.efficiency}%"
                )


def shield_regeneration_phase(fleet: List[Ship], logger: Optional[BattleLogger] = None) -> None:
    """Regenerate shields for all ships based on power allocation."""
    for ship in fleet:
        if ship.hull > 0:
            old_shield = ship.shield
            ship.regenerate_shields()
            if ship.shield > old_shield:
                if logger:
                    logger.log_shield_regen(ship, old_shield, ship.shield)
                else:
                    print(f"{ship.name} regenerates shields: {old_shield} -> {ship.shield}")


def weapon_cooling_phase(fleet: List[Ship], logger: Optional[BattleLogger] = None) -> None:
    """Cool down all weapons for all ships."""
    for ship in fleet:
        if ship.hull > 0:
            for battery in ship.weapons.batteries:
                if battery.heat > 0:
                    old_heat = battery.heat
                    battery.cool_down()
                    if old_heat >= battery.max_heat and battery.heat < battery.max_heat:
                        if not logger:
                            print(f"{ship.name}'s {battery.name} cooled down (heat: {battery.heat}%)")


# --------------- Simulation Runner ---------------


def run_round(fleet_a: List[Ship], fleet_b: List[Ship], round_num: int,
              logger: Optional[BattleLogger] = None,
              battle_map: Optional[BattleMap] = None,
              show_map: bool = False) -> None:
    if logger:
        logger.log_round_start(round_num)
    else:
        print(f"\n=== ROUND {round_num} ===")

    # Order selection phase (pass enemy fleets for pursuit targeting)
    if logger:
        logger.log_phase("Order Selection")
    select_orders(fleet_a, fleet_b, logger)
    select_orders(fleet_b, fleet_a, logger)

    # Environmental effects
    if logger:
        logger.log_phase("Hazard Resolution")
    resolve_hazards(fleet_a + fleet_b, logger)

    # Movement phase (includes formations, pursuit, evasion)
    if logger:
        logger.log_phase("Movement")
    move_fleet(fleet_a + fleet_b)

    # Show battle map if requested
    if show_map and battle_map:
        print(battle_map.render_complete(fleet_a, fleet_b, round_num, show_range_rings=False))

    # Combat phases
    if logger:
        logger.log_phase("Shooting")
    shooting_phase(fleet_a, fleet_b, logger)
    shooting_phase(fleet_b, fleet_a, logger)

    if logger:
        logger.log_phase("Missiles")
    missile_phase(fleet_a, fleet_b, logger)
    missile_phase(fleet_b, fleet_a, logger)

    if logger:
        logger.log_phase("Boarding")
    boarding_phase(fleet_a, fleet_b, logger)
    boarding_phase(fleet_b, fleet_a, logger)

    # Maintenance phases
    if logger:
        logger.log_phase("Repairs")
    repair_phase(fleet_a + fleet_b, logger)

    if logger:
        logger.log_phase("Shield Regeneration")
    shield_regeneration_phase(fleet_a + fleet_b, logger)

    if logger:
        logger.log_phase("Weapon Cooling")
    weapon_cooling_phase(fleet_a + fleet_b, logger)


def battle(fleet_a: List[Ship], fleet_b: List[Ship], rounds: int = 3,
          log_level: int = logging.INFO,
          show_map: bool = False,
          show_stats: bool = True) -> Optional[BattleLogger]:
    """
    Run a battle simulation.

    Args:
        fleet_a: First fleet
        fleet_b: Second fleet
        rounds: Number of rounds to simulate
        log_level: Logging level (logging.DEBUG, INFO, WARNING, ERROR)
        show_map: Display tactical map each round
        show_stats: Display battle statistics at end

    Returns:
        BattleLogger instance with battle statistics
    """
    # Initialize logger and battle map
    logger = BattleLogger(log_level=log_level)
    battle_map = BattleMap(width=60, height=20, grid_size=50.0) if show_map else None

    # Start battle
    logger.start_battle(fleet_a, fleet_b)

    # Show initial positions if map enabled
    if show_map and battle_map:
        print(battle_map.render_complete(fleet_a, fleet_b, 0, show_range_rings=True))

    # Run rounds
    for rnd in range(1, rounds + 1):
        if not fleet_a or not fleet_b:
            break
        run_round(fleet_a, fleet_b, rnd, logger, battle_map, show_map)
        fleet_a = [s for s in fleet_a if s.hull > 0]
        fleet_b = [s for s in fleet_b if s.hull > 0]
        if not fleet_a or not fleet_b:
            break

    # End battle
    logger.end_battle()

    # Final status
    print(render_quick_status(fleet_a, fleet_b))

    # Show statistics
    if show_stats:
        print(logger.generate_report())

    return logger


async def main_async(rounds: int = 3, log_level: int = logging.INFO,
                    show_map: bool = False, show_stats: bool = True) -> None:
    await install_dependencies()
    fleet_a, fleet_b = demo_fleets()
    battle(fleet_a, fleet_b, rounds, log_level, show_map, show_stats)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple fleet battle simulation")
    parser.add_argument(
        "--rounds", type=int, default=3, help="Number of rounds to simulate"
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "--show-map", action="store_true", help="Display tactical map each round"
    )
    parser.add_argument(
        "--no-stats", action="store_true", help="Don't display battle statistics"
    )
    args = parser.parse_args()

    log_level = getattr(logging, args.log_level)
    asyncio.run(main_async(args.rounds, log_level, args.show_map, not args.no_stats))


if __name__ == "__main__":
    main()
