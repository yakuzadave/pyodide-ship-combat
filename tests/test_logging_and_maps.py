"""Tests for battle logging and map visualization."""

import pytest
from ship_combat.models import Ship, WeaponSystem, WeaponBattery, ShipSystem
from ship_combat.battle_logger import BattleLogger, BattleEvent, RoundSummary
from ship_combat.battle_map import BattleMap


@pytest.fixture
def basic_ship():
    """Create a basic ship for testing."""
    weapons = WeaponSystem()
    battery = WeaponBattery(
        name="Test Cannon",
        rating=3,
        accuracy=2,
        damage_dice="2d6",
    )
    weapons.add_battery(battery)

    ship = Ship(
        name="Test Ship",
        hull=100,
        shield=50,
        weapons=weapons,
        crew=100,
        leadership=5,
        boarding_strength=3,
        x=10.0,
        y=5.0,
        z=0.0,
        heading=90.0,
    )
    return ship


@pytest.fixture
def logger():
    """Create a battle logger."""
    return BattleLogger(verbose=False)


@pytest.fixture
def battle_map():
    """Create a battle map."""
    return BattleMap(width=60, height=30, scale=2.0)


def test_battle_event_creation():
    """Test creating a battle event."""
    event = BattleEvent(
        round=1,
        phase="shooting",
        event_type="hit",
        ship_name="TestShip",
        details={"target": "EnemyShip", "damage": 10}
    )

    assert event.round == 1
    assert event.phase == "shooting"
    assert event.event_type == "hit"
    assert event.ship_name == "TestShip"
    assert event.details["damage"] == 10


def test_battle_event_to_text():
    """Test converting event to text."""
    event = BattleEvent(
        round=2,
        phase="missiles",
        event_type="missile_hit",
        ship_name="Attacker",
        details={"target": "Defender", "damage": 15}
    )

    text = event.to_text()
    assert "[Round 2]" in text
    assert "missiles" in text
    assert "Attacker" in text


def test_round_summary_accuracy():
    """Test round summary accuracy calculation."""
    summary = RoundSummary(round=1)
    summary.total_shots_fired = 10
    summary.total_hits = 7
    summary.total_misses = 3

    assert summary.accuracy() == 70.0


def test_round_summary_no_shots():
    """Test accuracy with no shots fired."""
    summary = RoundSummary(round=1)
    assert summary.accuracy() == 0.0


def test_logger_start_round(logger):
    """Test starting a new round."""
    logger.start_round(1)
    assert logger.current_round is not None
    assert logger.current_round.round == 1


def test_logger_log_order(logger):
    """Test logging order selection."""
    logger.start_round(1)
    logger.log_order("Ship1", "Lock On")

    assert len(logger.events) == 1
    assert logger.events[0].event_type == "order_selected"
    assert logger.events[0].details["order"] == "Lock On"


def test_logger_log_movement(logger):
    """Test logging ship movement."""
    logger.start_round(1)
    logger.log_movement("Ship1", 0.0, 0.0, 10.0, 5.0, 45.0)

    assert len(logger.events) == 1
    event = logger.events[0]
    assert event.event_type == "ship_moved"
    assert event.details["to_x"] == 10.0
    assert event.details["to_y"] == 5.0


def test_logger_log_shot_hit(logger):
    """Test logging a hit."""
    logger.start_round(1)
    logger.log_shot("Attacker", "Defender", "Cannon", hit=True, damage=10)

    assert logger.current_round.total_shots_fired == 1
    assert logger.current_round.total_hits == 1
    assert logger.current_round.total_damage_dealt == 10


def test_logger_log_shot_miss(logger):
    """Test logging a miss."""
    logger.start_round(1)
    logger.log_shot("Attacker", "Defender", "Cannon", hit=False)

    assert logger.current_round.total_shots_fired == 1
    assert logger.current_round.total_misses == 1
    assert logger.current_round.total_damage_dealt == 0


def test_logger_log_critical_hit(logger):
    """Test logging a critical hit."""
    logger.start_round(1)
    logger.log_shot("Attacker", "Defender", "Cannon", hit=True, damage=15, critical=True)

    assert logger.current_round.critical_hits == 1
    assert logger.events[0].event_type == "critical_hit"


def test_logger_log_missile(logger):
    """Test logging missile launch."""
    logger.start_round(1)
    logger.log_missile("Attacker", "Defender", 12)

    assert logger.current_round.total_shots_fired == 1
    assert logger.current_round.total_hits == 1
    assert logger.current_round.total_damage_dealt == 12


def test_logger_log_boarding(logger):
    """Test logging boarding actions."""
    logger.start_round(1)
    logger.log_boarding("Attacker", "Defender", success=True, damage=8)

    event = logger.events[0]
    assert event.event_type == "boarding_success"
    assert logger.current_round.total_damage_dealt == 8


def test_logger_log_shield_regen(logger):
    """Test logging shield regeneration."""
    logger.start_round(1)
    logger.log_shield_regen("Ship1", 40, 45)

    event = logger.events[0]
    assert event.details["regenerated"] == 5


def test_logger_log_destruction(logger):
    """Test logging ship destruction."""
    logger.start_round(1)
    logger.log_destruction("VictimShip", killed_by="AttackerShip")

    assert "VictimShip" in logger.current_round.ships_destroyed
    assert logger.events[0].event_type == "ship_destroyed"


def test_logger_get_summary(logger):
    """Test getting overall summary."""
    logger.start_round(1)
    logger.log_shot("A", "B", "Gun", hit=True, damage=10)
    logger.log_shot("A", "B", "Gun", hit=False)
    logger.end_round()

    logger.start_round(2)
    logger.log_shot("B", "A", "Laser", hit=True, damage=15, critical=True)
    logger.end_round()

    summary = logger.get_summary()

    assert summary["total_rounds"] == 2
    assert summary["total_shots_fired"] == 3
    assert summary["total_hits"] == 2
    assert summary["total_misses"] == 1
    assert summary["total_damage_dealt"] == 25
    assert summary["critical_hits"] == 1


def test_logger_export_json(logger, tmp_path):
    """Test exporting to JSON."""
    logger.start_round(1)
    logger.log_shot("A", "B", "Gun", hit=True, damage=10)
    logger.end_round()

    filepath = tmp_path / "test_log.json"
    logger.export_json(str(filepath))

    assert filepath.exists()

    import json
    with open(filepath) as f:
        data = json.load(f)

    assert data["total_rounds"] == 1
    assert data["total_damage_dealt"] == 10


def test_logger_export_text(logger, tmp_path):
    """Test exporting to text."""
    logger.start_round(1)
    logger.log_order("Ship1", "Lock On")
    logger.end_round()

    filepath = tmp_path / "test_log.txt"
    logger.export_text(str(filepath))

    assert filepath.exists()

    with open(filepath) as f:
        content = f.read()

    assert "BATTLE LOG" in content
    assert "Lock On" in content


def test_map_world_to_screen(battle_map):
    """Test world to screen coordinate conversion."""
    # Center should map to middle of screen
    sx, sy = battle_map.world_to_screen(0, 0)
    assert sx == 30  # width // 2
    assert sy == 15  # height // 2

    # Positive X goes right
    sx, sy = battle_map.world_to_screen(10, 0)
    assert sx == 35  # 30 + 10/2

    # Positive Y goes up (but screen Y is inverted)
    sx, sy = battle_map.world_to_screen(0, 10)
    assert sy == 10  # 15 - 10/2


def test_map_get_heading_char(battle_map):
    """Test getting heading character."""
    assert battle_map.get_heading_char(0) == '→'    # East
    assert battle_map.get_heading_char(90) == '↑'   # North
    assert battle_map.get_heading_char(180) == '←'  # West
    assert battle_map.get_heading_char(270) == '↓'  # South
    assert battle_map.get_heading_char(45) == '↗'   # Northeast


def test_map_render_basic(battle_map, basic_ship):
    """Test basic map rendering."""
    fleet_a = [basic_ship]
    fleet_b = []

    map_str = battle_map.render(fleet_a, fleet_b, show_grid=False)

    assert isinstance(map_str, str)
    assert "Fleet A:" in map_str
    assert "Test Ship" in map_str
    assert "[1]" in map_str  # Ship symbol


def test_map_render_with_grid(battle_map, basic_ship):
    """Test map rendering with grid."""
    fleet_a = [basic_ship]
    fleet_b = []

    map_str = battle_map.render(fleet_a, fleet_b, show_grid=True)

    # Grid characters should be present
    assert '+' in map_str or '-' in map_str or '|' in map_str


def test_map_render_two_fleets(battle_map):
    """Test rendering two fleets."""
    ship_a = Ship(
        name="Ship A",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        x=10.0,
        y=0.0,
    )

    ship_b = Ship(
        name="Ship B",
        hull=80,
        shield=40,
        weapons=WeaponSystem(),
        crew=80,
        leadership=4,
        boarding_strength=2,
        x=-10.0,
        y=0.0,
    )

    map_str = battle_map.render([ship_a], [ship_b])

    assert "Ship A" in map_str
    assert "Ship B" in map_str
    assert "Fleet A:" in map_str
    assert "Fleet B:" in map_str


def test_map_render_compact(battle_map, basic_ship):
    """Test compact rendering."""
    fleet_a = [basic_ship]
    fleet_b = []

    compact = battle_map.render_compact(fleet_a, fleet_b)

    assert "BATTLEFIELD STATUS" in compact
    assert "Test Ship" in compact
    assert "H:100" in compact  # Hull display
    assert "S:50" in compact   # Shield display


def test_map_render_destroyed_ship(battle_map):
    """Test rendering destroyed ships."""
    destroyed_ship = Ship(
        name="Destroyed",
        hull=0,  # Destroyed
        shield=0,
        weapons=WeaponSystem(),
        crew=0,
        leadership=5,
        boarding_strength=0,
    )

    compact = battle_map.render_compact([destroyed_ship], [])

    assert "[DESTROYED]" in compact


def test_map_render_tactical(battle_map):
    """Test tactical overview rendering."""
    ship_a = Ship(
        name="Cruiser",
        hull=100,
        shield=50,
        weapons=WeaponSystem(),
        crew=100,
        leadership=5,
        boarding_strength=3,
        x=0.0,
        y=0.0,
        order="Lock On",
    )

    ship_b = Ship(
        name="Frigate",
        hull=80,
        shield=40,
        weapons=WeaponSystem(),
        crew=80,
        leadership=4,
        boarding_strength=2,
        x=15.0,
        y=0.0,
        order="Evasive Maneuvers",
    )

    tactical = battle_map.render_tactical([ship_a], [ship_b])

    assert "TACTICAL OVERVIEW" in tactical
    assert "Lock On" in tactical
    assert "Evasive Maneuvers" in tactical
    assert "ENGAGEMENT DISTANCES" in tactical
    assert "units" in tactical


def test_map_heading_char_wrapping(battle_map):
    """Test heading character with angle wrapping."""
    # Test angle wrapping (360 degrees = 0 degrees)
    assert battle_map.get_heading_char(360) == battle_map.get_heading_char(0)
    assert battle_map.get_heading_char(450) == battle_map.get_heading_char(90)


def test_logger_multiple_rounds(logger):
    """Test logging multiple rounds."""
    for i in range(1, 4):
        logger.start_round(i)
        logger.log_shot("A", "B", "Gun", hit=True, damage=5 * i)
        logger.end_round()

    summary = logger.get_summary()
    assert len(summary["round_summaries"]) == 3
    assert summary["total_damage_dealt"] == 5 + 10 + 15  # Sum of damages
