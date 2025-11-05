"""Root-level re-export of battle_map module for Pyodide compatibility."""
from ship_combat.battle_map import *

# Re-export for clarity
__all__ = ['BattleMap', 'render_quick_status']
