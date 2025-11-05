"""Text-based battle map visualization for ship combat."""

from __future__ import annotations
import math
from typing import List, Tuple
from .models import Ship

__all__ = ['BattleMap', 'render_quick_status']


class BattleMap:
    """ASCII-based 3D battle space visualization."""

    def __init__(self, width: int = 80, height: int = 30, grid_size: float = 50.0):
        """
        Initialize battle map.

        Args:
            width: Character width of the map
            height: Character height of the map
            grid_size: Size of the space represented by the map (in game units)
        """
        self.width = width
        self.height = height
        self.grid_size = grid_size

    def _world_to_screen(self, x: float, y: float, center_x: float = 0, center_y: float = 0) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        # Center the map on given coordinates
        rel_x = x - center_x
        rel_y = y - center_y

        # Scale to screen size
        scale = min(self.width, self.height) / self.grid_size
        screen_x = int(self.width / 2 + rel_x * scale)
        screen_y = int(self.height / 2 - rel_y * scale)  # Invert Y for screen coords

        # Clamp to screen bounds
        screen_x = max(0, min(self.width - 1, screen_x))
        screen_y = max(0, min(self.height - 1, screen_y))

        return screen_x, screen_y

    def _get_heading_arrow(self, heading: float) -> str:
        """Get ASCII arrow character for heading direction."""
        # Normalize heading to 0-360
        h = heading % 360

        # 8-directional arrows
        if 337.5 <= h or h < 22.5:
            return '→'  # East
        elif h < 67.5:
            return '↗'  # Northeast
        elif h < 112.5:
            return '↑'  # North
        elif h < 157.5:
            return '↖'  # Northwest
        elif h < 202.5:
            return '←'  # West
        elif h < 247.5:
            return '↙'  # Southwest
        elif h < 292.5:
            return '↓'  # South
        else:  # 292.5 <= h < 337.5
            return '↘'  # Southeast

    def _get_elevation_marker(self, z: float, reference_z: float = 0.0) -> str:
        """Get elevation marker relative to reference plane."""
        diff = z - reference_z
        if diff > 5:
            return '^'  # Above
        elif diff < -5:
            return 'v'  # Below
        else:
            return '='  # At level

    def render_top_down(self, fleet_a: List[Ship], fleet_b: List[Ship],
                        show_heading: bool = True, show_range_rings: bool = False) -> str:
        """
        Render top-down (XY plane) view of battle.

        Args:
            fleet_a: First fleet
            fleet_b: Second fleet
            show_heading: Display heading arrows
            show_range_rings: Show range band indicators

        Returns:
            ASCII art string of battle map
        """
        # Calculate center point (average of all ship positions)
        all_ships = fleet_a + fleet_b
        if not all_ships:
            return "No ships to display"

        center_x = sum(s.x for s in all_ships) / len(all_ships)
        center_y = sum(s.y for s in all_ships) / len(all_ships)

        # Create empty grid
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw range rings if requested
        if show_range_rings:
            self._draw_range_rings(grid, center_x, center_y)

        # Draw ships from fleet A (represented as 'A', 'B', 'C', etc.)
        for idx, ship in enumerate(fleet_a):
            if ship.hull > 0:
                sx, sy = self._world_to_screen(ship.x, ship.y, center_x, center_y)
                marker = chr(ord('A') + idx) if idx < 26 else 'A'

                if show_heading:
                    arrow = self._get_heading_arrow(ship.heading)
                    grid[sy][sx] = arrow
                else:
                    grid[sy][sx] = marker

        # Draw ships from fleet B (represented as '1', '2', '3', etc.)
        for idx, ship in enumerate(fleet_b):
            if ship.hull > 0:
                sx, sy = self._world_to_screen(ship.x, ship.y, center_x, center_y)
                marker = str(idx + 1) if idx < 9 else '9'

                if show_heading:
                    arrow = self._get_heading_arrow(ship.heading)
                    # Use lowercase for fleet B to distinguish from fleet A
                    grid[sy][sx] = arrow.lower() if arrow.isalpha() else marker
                else:
                    grid[sy][sx] = marker

        # Draw border
        border_top = '┌' + '─' * (self.width) + '┐'
        border_bottom = '└' + '─' * (self.width) + '┘'

        # Convert grid to string
        lines = [border_top]
        for row in grid:
            lines.append('│' + ''.join(row) + '│')
        lines.append(border_bottom)

        return '\n'.join(lines)

    def _draw_range_rings(self, grid: List[List[str]], center_x: float, center_y: float) -> None:
        """Draw range band circles on the grid."""
        # Range bands: point (5), short (10), standard (20)
        ranges = [5, 10, 20]
        markers = ['.', '·', '°']

        for radius, marker in zip(ranges, markers):
            # Draw circle using parametric equations
            for angle in range(0, 360, 10):
                rad = math.radians(angle)
                x = center_x + radius * math.cos(rad)
                y = center_y + radius * math.sin(rad)
                sx, sy = self._world_to_screen(x, y, center_x, center_y)
                if 0 <= sy < self.height and 0 <= sx < self.width:
                    if grid[sy][sx] == ' ':
                        grid[sy][sx] = marker

    def render_side_view(self, fleet_a: List[Ship], fleet_b: List[Ship]) -> str:
        """
        Render side view (XZ plane) showing elevation.

        Args:
            fleet_a: First fleet
            fleet_b: Second fleet

        Returns:
            ASCII art string of side view
        """
        all_ships = fleet_a + fleet_b
        if not all_ships:
            return "No ships to display"

        center_x = sum(s.x for s in all_ships) / len(all_ships)
        center_z = sum(s.z for s in all_ships) / len(all_ships)

        # Create empty grid
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw horizontal reference line at z=0
        mid_y = self.height // 2
        for x in range(self.width):
            grid[mid_y][x] = '-'

        # Draw fleet A
        for idx, ship in enumerate(fleet_a):
            if ship.hull > 0:
                sx, sy = self._world_to_screen(ship.x, ship.z, center_x, center_z)
                marker = chr(ord('A') + idx) if idx < 26 else 'A'
                grid[sy][sx] = marker

        # Draw fleet B
        for idx, ship in enumerate(fleet_b):
            if ship.hull > 0:
                sx, sy = self._world_to_screen(ship.x, ship.z, center_x, center_z)
                marker = str(idx + 1) if idx < 9 else '9'
                grid[sy][sx] = marker

        # Draw border
        border_top = '┌' + '─' * (self.width) + '┐'
        border_bottom = '└' + '─' * (self.width) + '┘'

        # Convert grid to string
        lines = [border_top]
        for row in grid:
            lines.append('│' + ''.join(row) + '│')
        lines.append(border_bottom)

        return '\n'.join(lines)

    def render_legend(self, fleet_a: List[Ship], fleet_b: List[Ship]) -> str:
        """
        Generate legend showing ship names and status.

        Args:
            fleet_a: First fleet
            fleet_b: Second fleet

        Returns:
            Formatted legend string
        """
        lines = ["=" * 80]
        lines.append("FLEET A:")
        for idx, ship in enumerate(fleet_a):
            marker = chr(ord('A') + idx) if idx < 26 else 'A'
            status = "DESTROYED" if ship.hull <= 0 else f"Hull:{ship.hull} Shld:{ship.shield}/{ship.max_shield}"
            heading_arrow = self._get_heading_arrow(ship.heading)
            elev = self._get_elevation_marker(ship.z)
            lines.append(
                f"  [{marker}] {ship.name:20s} {status:20s} "
                f"Pos:({ship.x:6.1f},{ship.y:6.1f},{ship.z:6.1f}) "
                f"Hdg:{heading_arrow} Elv:{elev}"
            )

        lines.append("\nFLEET B:")
        for idx, ship in enumerate(fleet_b):
            marker = str(idx + 1) if idx < 9 else '9'
            status = "DESTROYED" if ship.hull <= 0 else f"Hull:{ship.hull} Shld:{ship.shield}/{ship.max_shield}"
            heading_arrow = self._get_heading_arrow(ship.heading)
            elev = self._get_elevation_marker(ship.z)
            lines.append(
                f"  [{marker}] {ship.name:20s} {status:20s} "
                f"Pos:({ship.x:6.1f},{ship.y:6.1f},{ship.z:6.1f}) "
                f"Hdg:{heading_arrow} Elv:{elev}"
            )

        lines.append("=" * 80)
        return '\n'.join(lines)

    def render_complete(self, fleet_a: List[Ship], fleet_b: List[Ship],
                       round_num: int = 0, show_range_rings: bool = False) -> str:
        """
        Render complete battle visualization with both views and legend.

        Args:
            fleet_a: First fleet
            fleet_b: Second fleet
            round_num: Current round number
            show_range_rings: Show range indicators

        Returns:
            Complete battle map visualization
        """
        lines = []

        if round_num > 0:
            lines.append(f"\n{'=' * 80}")
            lines.append(f"ROUND {round_num} - TACTICAL DISPLAY")
            lines.append('=' * 80)

        # Top-down view
        lines.append("\nTOP-DOWN VIEW (XY Plane):")
        lines.append(self.render_top_down(fleet_a, fleet_b, show_heading=True, show_range_rings=show_range_rings))

        # Legend
        lines.append("\n" + self.render_legend(fleet_a, fleet_b))

        return '\n'.join(lines)


def render_quick_status(fleet_a: List[Ship], fleet_b: List[Ship]) -> str:
    """Quick status summary without full map."""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("FLEET STATUS")
    lines.append("=" * 80)

    # Fleet A
    a_alive = [s for s in fleet_a if s.hull > 0]
    a_total_hull = sum(s.hull for s in a_alive)
    lines.append(f"Fleet A: {len(a_alive)}/{len(fleet_a)} ships operational, Total Hull: {a_total_hull}")
    for ship in a_alive:
        shield_bar = '█' * int(ship.shield / 10) if ship.shield > 0 else ''
        hull_bar = '░' * int(ship.hull / 10)
        lines.append(f"  {ship.name:20s} H:[{hull_bar:10s}] S:[{shield_bar:10s}] ({ship.hull}HP/{ship.shield}SP)")

    # Fleet B
    b_alive = [s for s in fleet_b if s.hull > 0]
    b_total_hull = sum(s.hull for s in b_alive)
    lines.append(f"\nFleet B: {len(b_alive)}/{len(fleet_b)} ships operational, Total Hull: {b_total_hull}")
    for ship in b_alive:
        shield_bar = '█' * int(ship.shield / 10) if ship.shield > 0 else ''
        hull_bar = '░' * int(ship.hull / 10)
        lines.append(f"  {ship.name:20s} H:[{hull_bar:10s}] S:[{shield_bar:10s}] ({ship.hull}HP/{ship.shield}SP)")

    lines.append("=" * 80)
    return '\n'.join(lines)
