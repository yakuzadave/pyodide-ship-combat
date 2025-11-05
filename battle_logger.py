"""Root-level re-export of battle_logger module for Pyodide compatibility."""
from ship_combat.battle_logger import *

# Re-export for clarity
__all__ = ['BattleEvent', 'BattleStatistics', 'BattleLogger']
