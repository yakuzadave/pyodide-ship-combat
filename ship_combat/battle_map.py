"""Text-based battlefield visualization."""

from __future__ import annotations
from typing import List, Tuple, Dict
import math
from .models import Ship


class BattleMap:
    """ASCII text-based battlefield visualization."""

    def __init__(self, width: int = 80, height: int = 40, scale: float = 2.0):
        """
        Initialize battle map.

        Args:
            width: Map width in characters
            height: Map height in characters
            scale: Units per character (higher = zoomed out)
        """
        self.width = width
        self.height = height
        self.scale = scale

    def world_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert world coordinates to screen coordinates.

        Args:
            x: World X coordinate
            y: World Y coordinate

        Returns:
            (screen_x, screen_y) tuple
        """
        # Center of screen
        center_x = self.width // 2
        center_y = self.height // 2

        # Scale and translate
        screen_x = int(center_x + (x / self.scale))
        screen_y = int(center_y - (y / self.scale))  # Y is inverted in screen coords

        return (screen_x, screen_y)

    def get_heading_char(self, heading: float) -> str:
        """
        Get character representing ship heading.

        Args:
            heading: Heading in degrees (0 = east, 90 = north)

        Returns:
            Character representing direction
        """
        # Normalize heading to 0-360
        heading = heading % 360

        # 8 directions
        if heading < 22.5 or heading >= 337.5:
            return '→'  # East
        elif heading < 67.5:
            return '↗'  # Northeast
        elif heading < 112.5:
            return '↑'  # North
        elif heading < 157.5:
            return '↖'  # Northwest
        elif heading < 202.5:
            return '←'  # West
        elif heading < 247.5:
            return '↙'  # Southwest
        elif heading < 292.5:
            return '↓'  # South
        else:
            return '↘'  # Southeast

    def render(self, fleet_a: List[Ship], fleet_b: List[Ship],
               show_grid: bool = True, show_range: bool = False) -> str:
        """
        Render the battlefield as ASCII text.

        Args:
            fleet_a: First fleet
            fleet_b: Second fleet
            show_grid: Show grid lines
            show_range: Show range circles

        Returns:
            ASCII map string
        """
        # Initialize grid
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw grid if enabled
        if show_grid:
            for y in range(self.height):
                for x in range(self.width):
                    if x % 10 == 0 and y % 5 == 0:
                        grid[y][x] = '+'
                    elif x % 10 == 0:
                        grid[y][x] = '|'
                    elif y % 5 == 0:
                        grid[y][x] = '-'

        # Draw range circles if enabled
        if show_range:
            self._draw_range_circles(grid)

        # Draw ships from fleet A (use numbers 1-9, then letters)
        for i, ship in enumerate(fleet_a):
            if ship.hull > 0:
                self._draw_ship(grid, ship, str(i + 1) if i < 9 else chr(65 + i - 9), 'A')

        # Draw ships from fleet B (use lowercase letters)
        for i, ship in enumerate(fleet_b):
            if ship.hull > 0:
                self._draw_ship(grid, ship, chr(97 + i), 'B')

        # Convert grid to string
        lines = [''.join(row) for row in grid]

        # Add legend
        legend = self._create_legend(fleet_a, fleet_b)

        return '\n'.join(lines) + '\n' + legend

    def _draw_ship(self, grid: List[List[str]], ship: Ship, symbol: str, fleet_id: str) -> None:
        """Draw a ship on the grid."""
        sx, sy = self.world_to_screen(ship.x, ship.y)

        # Check bounds
        if 0 <= sx < self.width and 0 <= sy < self.height:
            # Draw ship symbol
            grid[sy][sx] = symbol

            # Draw heading indicator if there's space
            heading_char = self.get_heading_char(ship.heading)
            if ship.evasion_active:
                heading_char = '~'  # Evading ships shown differently

            # Try to place heading indicator adjacent to ship
            dx, dy = self._get_heading_offset(ship.heading)
            hx, hy = sx + dx, sy + dy

            if 0 <= hx < self.width and 0 <= hy < self.height:
                if grid[hy][hx] == ' ' or grid[hy][hx] in '-|+':
                    grid[hy][hx] = heading_char

    def _get_heading_offset(self, heading: float) -> Tuple[int, int]:
        """Get screen offset for heading indicator."""
        heading = heading % 360

        if heading < 45 or heading >= 315:
            return (1, 0)  # East
        elif heading < 135:
            return (0, -1)  # North
        elif heading < 225:
            return (-1, 0)  # West
        else:
            return (0, 1)  # South

    def _draw_range_circles(self, grid: List[List[str]]) -> None:
        """Draw range circles centered on origin."""
        # Draw circles for standard ranges (20 units)
        center_x, center_y = self.world_to_screen(0, 0)
        radius_screen = int(20 / self.scale)

        # Simple circle drawing
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            x = int(center_x + radius_screen * math.cos(rad))
            y = int(center_y - radius_screen * math.sin(rad))

            if 0 <= x < self.width and 0 <= y < self.height:
                if grid[y][x] == ' ':
                    grid[y][x] = '·'

    def _create_legend(self, fleet_a: List[Ship], fleet_b: List[Ship]) -> str:
        """Create legend for the map."""
        lines = ["\n" + "=" * self.width]
        lines.append("LEGEND")
        lines.append("=" * self.width)

        # Fleet A
        lines.append("\nFleet A:")
        for i, ship in enumerate(fleet_a):
            symbol = str(i + 1) if i < 9 else chr(65 + i - 9)
            status = "DESTROYED" if ship.hull <= 0 else f"Hull:{ship.hull} Shield:{ship.shield}"
            heading = self.get_heading_char(ship.heading)
            evade = " [EVADING]" if ship.evasion_active else ""
            lines.append(f"  [{symbol}] {ship.name}: {status} {heading}{evade}")

        # Fleet B
        lines.append("\nFleet B:")
        for i, ship in enumerate(fleet_b):
            symbol = chr(97 + i)
            status = "DESTROYED" if ship.hull <= 0 else f"Hull:{ship.hull} Shield:{ship.shield}"
            heading = self.get_heading_char(ship.heading)
            evade = " [EVADING]" if ship.evasion_active else ""
            lines.append(f"  [{symbol}] {ship.name}: {status} {heading}{evade}")

        # Symbols explanation
        lines.append("\nSymbols: ↑↗→↘↓↙←↖ = heading, ~ = evading, · = range circle")
        lines.append(f"Scale: 1 char = {self.scale} units")
        lines.append("=" * self.width)

        return '\n'.join(lines)

    def render_compact(self, fleet_a: List[Ship], fleet_b: List[Ship]) -> str:
        """
        Render a compact version showing only ship positions and status.

        Args:
            fleet_a: First fleet
            fleet_b: Second fleet

        Returns:
            Compact status string
        """
        lines = ["BATTLEFIELD STATUS"]
        lines.append("-" * 60)

        lines.append("\nFleet A:")
        for i, ship in enumerate(fleet_a):
            symbol = str(i + 1) if i < 9 else chr(65 + i - 9)
            if ship.hull > 0:
                pos = f"({ship.x:.1f}, {ship.y:.1f}, {ship.z:.1f})"
                heading = f"{ship.heading:.0f}°"
                status = f"H:{ship.hull} S:{ship.shield}"
                lines.append(f"  [{symbol}] {ship.name:20s} {pos:25s} {heading:6s} {status}")
            else:
                lines.append(f"  [{symbol}] {ship.name:20s} [DESTROYED]")

        lines.append("\nFleet B:")
        for i, ship in enumerate(fleet_b):
            symbol = chr(97 + i)
            if ship.hull > 0:
                pos = f"({ship.x:.1f}, {ship.y:.1f}, {ship.z:.1f})"
                heading = f"{ship.heading:.0f}°"
                status = f"H:{ship.hull} S:{ship.shield}"
                lines.append(f"  [{symbol}] {ship.name:20s} {pos:25s} {heading:6s} {status}")
            else:
                lines.append(f"  [{symbol}] {ship.name:20s} [DESTROYED]")

        lines.append("-" * 60)

        return '\n'.join(lines)

    def render_tactical(self, fleet_a: List[Ship], fleet_b: List[Ship]) -> str:
        """
        Render tactical information about current state.

        Args:
            fleet_a: First fleet
            fleet_b: Second fleet

        Returns:
            Tactical information string
        """
        from .battle_sim import distance

        lines = ["TACTICAL OVERVIEW"]
        lines.append("=" * 80)

        # Fleet status
        a_alive = len([s for s in fleet_a if s.hull > 0])
        b_alive = len([s for s in fleet_b if s.hull > 0])

        lines.append(f"\nFleet A: {a_alive}/{len(fleet_a)} active")
        lines.append(f"Fleet B: {b_alive}/{len(fleet_b)} active")

        # Engagement distances
        lines.append("\nENGAGEMENT DISTANCES:")
        for ship_a in fleet_a:
            if ship_a.hull <= 0:
                continue
            for ship_b in fleet_b:
                if ship_b.hull <= 0:
                    continue

                dist = distance(ship_a, ship_b)
                range_band = "POINT" if dist <= 5 else "SHORT" if dist <= 10 else "STANDARD" if dist <= 20 else "LONG" if dist <= 40 else "EXTREME"

                lines.append(f"  {ship_a.name} → {ship_b.name}: {dist:.1f} units [{range_band}]")

        # Active orders
        lines.append("\nACTIVE ORDERS:")
        lines.append("Fleet A:")
        for ship in fleet_a:
            if ship.hull > 0 and ship.order:
                power_info = ""
                if ship.order in ["Power to Weapons", "Power to Engines"]:
                    power_info = f" (W:{ship.power_allocation['weapons']}% S:{ship.power_allocation['shields']}% E:{ship.power_allocation['engines']}%)"
                lines.append(f"  {ship.name}: {ship.order}{power_info}")

        lines.append("Fleet B:")
        for ship in fleet_b:
            if ship.hull > 0 and ship.order:
                power_info = ""
                if ship.order in ["Power to Weapons", "Power to Engines"]:
                    power_info = f" (W:{ship.power_allocation['weapons']}% S:{ship.power_allocation['shields']}% E:{ship.power_allocation['engines']}%)"
                lines.append(f"  {ship.name}: {ship.order}{power_info}")

        # Weapon heat status
        lines.append("\nWEAPON HEAT STATUS:")
        for fleet, name in [(fleet_a, "Fleet A"), (fleet_b, "Fleet B")]:
            any_heat = False
            for ship in fleet:
                if ship.hull <= 0:
                    continue
                for battery in ship.weapons.batteries:
                    if battery.heat > 0:
                        if not any_heat:
                            lines.append(f"{name}:")
                            any_heat = True
                        overheat = " [OVERHEATED]" if battery.is_overheated() else ""
                        lines.append(f"  {ship.name} - {battery.name}: {battery.heat}%{overheat}")

        lines.append("=" * 80)

        return '\n'.join(lines)
