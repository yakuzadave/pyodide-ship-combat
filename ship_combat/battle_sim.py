# Battle Simulator for Pyodide and CLI
# Implements battle phases using dataclasses defined in models.py
# Runs headless with optional CLI arguments.

from __future__ import annotations

import argparse
import asyncio
import random
import math
from typing import List

from .models import Ship
from .fleet_setup import demo_fleets

try:
    import rolldice  # type: ignore
except Exception:  # rolldice may not be installed in Pyodide yet
    rolldice = None  # will be loaded dynamically

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


def move_fleet(fleet: List[Ship]) -> None:
    """Advance each ship based on its speed and heading."""
    for ship in fleet:
        yaw_rad = math.radians(ship.heading)
        pitch_rad = math.radians(ship.pitch)
        ship.x += math.cos(yaw_rad) * math.cos(pitch_rad) * ship.speed
        ship.y += math.sin(yaw_rad) * math.cos(pitch_rad) * ship.speed
        ship.z += math.sin(pitch_rad) * ship.speed


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


def select_orders(fleet: List[Ship]) -> None:
    """Randomly assign orders to each ship."""
    for ship in fleet:
        ship.order = random.choice(BATTLE_ORDERS)
        ship.attack_mod = 0
        ship.defense_mod = 0
        ship.repair_priority = False
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
        print(f"{ship.name} selects order: {ship.order}")


def apply_hazard(ship: Ship, hazard: str) -> None:
    """Apply a named hazard effect to a single ship."""
    if rolldice is None:
        raise RuntimeError("rolldice not loaded")
    if hazard == "System Failure":
        system_name = random.choice(list(ship.systems.keys()))
        ship.systems[system_name].damage(10)
        print(
            f"Hazard damages {ship.name}'s {system_name}, now {ship.systems[system_name].efficiency}%"
        )
    elif hazard == "Gravity Well":
        ship.attack_mod -= 1
        ship.defense_mod -= 1
        print(f"{ship.name} caught in gravity well: -1 attack and defense")
    elif hazard == "Minefield":
        dmg, _ = rolldice.roll_dice("1d6")
        ship.hull = max(0, ship.hull - int(dmg))
        print(f"{ship.name} strikes a mine for {dmg} damage (hull {ship.hull})")
    elif hazard == "Nebula":
        ship.attack_mod -= 1
        print(f"{ship.name} enters nebula: -1 attack this round")
    elif hazard == "Radiation Burst":
        for system in ship.systems.values():
            system.damage(5)
        print(f"{ship.name} hit by radiation burst: all systems degrade")


def resolve_hazards(fleet: List[Ship]) -> None:
    """Randomly apply environmental hazards."""
    for ship in fleet:
        if not ship.systems:
            continue
        if random.random() < 0.1:
            hazard = random.choice(list(HAZARDS.keys()))
            print(f"{ship.name} encounters hazard: {hazard}")
            apply_hazard(ship, hazard)


def shooting_phase(attacking: List[Ship], defending: List[Ship]) -> None:
    """Resolve shooting between fleets."""
    if rolldice is None:
        raise RuntimeError("rolldice not loaded")
    for ship in attacking:
        if ship.hull <= 0:
            continue
        targets = [t for t in defending if t.hull > 0]
        targets.sort(key=lambda t: distance(ship, t))
        if not targets:
            continue
        chosen = None
        valid_batteries = []
        for tgt in targets:
            bats = [b for b in ship.weapons.batteries if can_fire(ship, tgt, b)]
            if bats:
                chosen = tgt
                valid_batteries = bats
                break
        if not chosen:
            continue
        for battery in valid_batteries:
            roll, _ = rolldice.roll_dice("2d20")
            attack_total = roll + ship.attack_mod + battery.accuracy
            defense_target = chosen.shield + chosen.defense_mod
            if attack_total > defense_target:
                dmg, _ = rolldice.roll_dice(battery.damage_dice)
                chosen.hull = max(0, chosen.hull - int(dmg))
                print(
                    f"{ship.name} hits {chosen.name} with {battery.name} for {dmg} (hull {chosen.hull})"
                )
                if chosen.hull == 0:
                    print(f"{chosen.name} destroyed!")
                    break
            else:
                print(f"{ship.name} misses {chosen.name} with {battery.name}")


def missile_phase(attacking: List[Ship], defending: List[Ship]) -> None:
    """Fire missiles if available."""
    if rolldice is None:
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
        dmg, _ = rolldice.roll_dice("3d6")
        target.hull = max(0, target.hull - int(dmg))
        print(
            f"{ship.name} launches missile at {target.name} for {dmg} (hull {target.hull})"
        )
        if target.hull == 0:
            print(f"{target.name} destroyed by missile!")


def boarding_phase(attacking: List[Ship], defending: List[Ship]) -> None:
    """Attempt boarding actions."""
    if rolldice is None:
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
            atk, _ = rolldice.roll_dice("1d20")
            attack_total = atk + ship.boarding_strength + ship.attack_mod
            defend_total = target.boarding_strength + target.defense_mod
            if attack_total > defend_total:
                dmg, _ = rolldice.roll_dice("1d10")
                target.hull = max(0, target.hull - int(dmg))
                print(
                    f"{ship.name} boards {target.name} for {dmg} damage (hull {target.hull})"
                )
                if target.hull == 0:
                    print(f"{target.name} captured and destroyed!")
            else:
                print(f"{ship.name} fails to board {target.name}")


def repair_phase(fleet: List[Ship]) -> None:
    """Attempt simple repairs on damaged systems."""
    if rolldice is None:
        raise RuntimeError("rolldice not loaded")
    for ship in fleet:
        damaged = [s for s in ship.systems.values() if s.status != "Operational"]
        chance = 1.0 if ship.repair_priority else 0.5
        if damaged and random.random() < chance:
            system = random.choice(damaged)
            system.repair(10)
            print(
                f"{ship.name} repairs {system.effect or 'a system'} to {system.efficiency}%"
            )


# --------------- Simulation Runner ---------------


def run_round(fleet_a: List[Ship], fleet_b: List[Ship], round_num: int) -> None:
    print(f"\n=== ROUND {round_num} ===")
    select_orders(fleet_a + fleet_b)
    resolve_hazards(fleet_a + fleet_b)
    move_fleet(fleet_a + fleet_b)
    shooting_phase(fleet_a, fleet_b)
    shooting_phase(fleet_b, fleet_a)
    missile_phase(fleet_a, fleet_b)
    missile_phase(fleet_b, fleet_a)
    boarding_phase(fleet_a, fleet_b)
    boarding_phase(fleet_b, fleet_a)
    repair_phase(fleet_a + fleet_b)


def battle(fleet_a: List[Ship], fleet_b: List[Ship], rounds: int = 3) -> None:
    for rnd in range(1, rounds + 1):
        if not fleet_a or not fleet_b:
            break
        run_round(fleet_a, fleet_b, rnd)
        fleet_a = [s for s in fleet_a if s.hull > 0]
        fleet_b = [s for s in fleet_b if s.hull > 0]
        if not fleet_a or not fleet_b:
            break
    print("\n--- Battle Over ---")
    for ship in fleet_a + fleet_b:
        status = "DESTROYED" if ship.hull <= 0 else f"Hull {ship.hull}"
        print(f"{ship.name}: {status}")


async def main_async(rounds: int) -> None:
    await install_dependencies()
    fleet_a, fleet_b = demo_fleets()
    battle(fleet_a, fleet_b, rounds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple fleet battle simulation")
    parser.add_argument(
        "--rounds", type=int, default=3, help="Number of rounds to simulate"
    )
    args = parser.parse_args()
    asyncio.run(main_async(args.rounds))


if __name__ == "__main__":
    main()
