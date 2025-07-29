# Battle Simulator for Pyodide and CLI
# Implements battle phases using dataclasses defined in models.py
# Runs headless with optional CLI arguments.

from __future__ import annotations

import argparse
import asyncio
import random
from typing import List

from models import Ship
from fleet_setup import demo_fleets

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
]


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
        print(f"{ship.name} selects order: {ship.order}")


def resolve_hazards(fleet: List[Ship]) -> None:
    """Randomly apply environmental hazards."""
    for ship in fleet:
        if not ship.systems:
            continue
        if random.random() < 0.1:  # 10% chance a system takes damage
            system_name = random.choice(list(ship.systems.keys()))
            ship.systems[system_name].damage(10)
            print(
                f"Hazard damages {ship.name}'s {system_name}, now {ship.systems[system_name].efficiency}%"
            )


def shooting_phase(attacking: List[Ship], defending: List[Ship]) -> None:
    """Resolve shooting between fleets."""
    if rolldice is None:
        raise RuntimeError("rolldice not loaded")
    for ship in attacking:
        targets = [t for t in defending if t.hull > 0]
        if not targets or ship.hull <= 0:
            continue
        target = random.choice(targets)
        roll, _ = rolldice.roll_dice("2d20")
        if roll > target.shield:
            dmg, _ = rolldice.roll_dice("2d6")
            target.hull = max(0, target.hull - int(dmg))
            print(f"{ship.name} hits {target.name} for {dmg} (hull {target.hull})")
            if target.hull == 0:
                print(f"{target.name} destroyed!")
        else:
            print(f"{ship.name} misses {target.name}")


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
        target = random.choice(targets)
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
            target = random.choice(targets)
            atk, _ = rolldice.roll_dice("1d20")
            if atk + ship.boarding_strength > target.boarding_strength:
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
        if damaged and random.random() < 0.5:
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
