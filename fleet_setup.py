from __future__ import annotations
from models import Ship, ShipSystem, WeaponSystem, WeaponBattery


def system_block(eff: int = 100, thresh: int = 50, effect: str = "") -> ShipSystem:
    """Create a ShipSystem instance with common defaults."""
    return ShipSystem(efficiency=eff, critical_threshold=thresh, effect=effect)


def new_ship(
    name: str,
    class_name: str,
    hull: int,
    shield: int,
    weapons: WeaponSystem,
    missiles: int,
    crew: int,
    leadership: int,
    boarding_strength: int,
    speed: int,
    maneuver: int,
    systems: dict[str, ShipSystem],
    ai: str,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    heading: float = 0.0,
    pitch: float = 0.0,
) -> Ship:
    """Instantiate a Ship dataclass with supplied parameters."""
    weapons.missiles = missiles
    return Ship(
        name=name,
        hull=hull,
        shield=shield,
        weapons=weapons,
        crew=crew,
        leadership=leadership,
        boarding_strength=boarding_strength,
        speed=speed,
        maneuver=maneuver,
        systems=systems,
        ai=ai,
        x=x,
        y=y,
        z=z,
        heading=heading,
        pitch=pitch,
        class_name=class_name,
    )


def demo_fleets() -> tuple[list[Ship], list[Ship]]:
    """Return two small demo fleets used by the CLI and HTML sample."""
    aurora_weapons = WeaponSystem(
        [
            WeaponBattery(
                "Lance Battery", rating=3, accuracy=1, damage_dice="2d6", range="long"
            ),
            WeaponBattery("Macro Cannon", rating=2, accuracy=0, damage_dice="3d6"),
        ],
        missiles=4,
    )

    aurora = new_ship(
        "Aurora Huntress",
        "Light Cruiser",
        80,
        65,
        aurora_weapons,
        4,
        2,
        7,
        1,
        25,
        2,
        {
            "engines": system_block(85, effect="Speed halved when offline"),
            "shields": system_block(70, effect="Hull exposed"),
            "targeting": system_block(90, effect="Attack penalty"),
        },
        "Efficient and sarcastic",
        x=-10.0,
        y=0.0,
        z=0.0,
        heading=90.0,
        pitch=0.0,
    )

    warden_weapons = WeaponSystem(
        [
            WeaponBattery(
                "Plasma Broadside",
                rating=4,
                accuracy=-1,
                damage_dice="4d6",
                range="long",
                special="area",
            ),
        ],
        missiles=6,
    )

    warden = new_ship(
        "Celestial Warden",
        "Battleship",
        100,
        80,
        warden_weapons,
        6,
        4,
        9,
        3,
        18,
        1,
        {
            "engines": system_block(90, effect="Ship immobilised"),
            "shields": system_block(80, effect="Hull exposed"),
            "reactor": system_block(100, effect="Catastrophic explosion on failure"),
        },
        "Formal and calculating",
        x=10.0,
        y=0.0,
        z=0.0,
        heading=270.0,
        pitch=0.0,
    )

    return [aurora], [warden]
