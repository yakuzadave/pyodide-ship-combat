# PR_INVENTORY.md — Open Pull Requests Tracking

Complete enumeration of all open PRs in the pyodide-ship-combat repository, grouped by category.

Last Updated: 2026-01-11

---

## Summary Statistics

- **Total Open PRs**: 9
- **In Scope for Work**: To be determined
- **Code Quality PRs**: 5 (PRs #11-15)
- **Feature PRs**: 3 (PRs #18-20)
- **Documentation PRs**: 1 (PR #27 - current)

---

## Code Quality Improvements [5 PRs]

### PR #15 - Remove redundant condition checks in heading arrow logic [TODO]
- **Status**: DRAFT, Open
- **Author**: Copilot
- **Created**: 2025-11-05
- **Branch**: `copilot/sub-pr-10-one-more-time`
- **Base**: `claude/text-map-logging-pyodide-011CUiUrJowSSDjfGqhCvRq7`
- **Summary**: Addresses review feedback on PR #10 by removing redundant lower bound checks from `_get_heading_arrow` method
- **Files Changed**: `ship_combat/battle_map.py`
- **Impact**: Code simplification, no behavioral changes
- **Notes**: Related to PRs #11, #12, #14 - all fixing similar redundant conditions
- **Merge Conflicts**: Possible with PRs #11, #12 (same file, same method)

### PR #14 - Fix damage tracking, health display, and namespace pollution [TODO]
- **Status**: DRAFT, Open
- **Author**: Copilot
- **Created**: 2025-11-05
- **Branch**: `copilot/sub-pr-10-yet-again`
- **Base**: `claude/text-map-logging-pyodide-011CUiUrJowSSDjfGqhCvRq7`
- **Summary**: Multiple fixes:
  - Adds fleet-level damage_taken tracking for missiles
  - Adds statistics tracking for boarding damage
  - Changes health display from misleading combined format to separate hull/shield
  - Adds `__all__` to battle_logger.py and battle_map.py
  - Simplifies redundant range checks in heading arrow logic
- **Files Changed**: `ship_combat/battle_sim.py`, `ship_combat/battle_logger.py`, `ship_combat/battle_map.py`
- **Impact**: Bug fixes + code quality
- **Notes**: Most comprehensive of the related PRs
- **Merge Conflicts**: Overlaps with PRs #11, #12, #13, #15

### PR #13 - Fix misleading health calculation in battle legend [TODO]
- **Status**: DRAFT, Open, Labeled: codex
- **Author**: Copilot
- **Created**: 2025-11-05
- **Branch**: `copilot/sub-pr-10-another-one`
- **Base**: `claude/text-map-logging-pyodide-011CUiUrJowSSDjfGqhCvRq7`
- **Summary**: Fixes health display showing misleading denominator. Adds max_hull field to Ship model
- **Files Changed**: `ship_combat/models.py`, `ship_combat/battle_map.py`
- **Impact**: Bug fix - display accuracy
- **Notes**: Related to PR #14 which also fixes health display
- **Merge Conflicts**: Overlaps with PR #14

### PR #12 - Remove redundant condition checks in heading arrow logic [TODO]
- **Status**: DRAFT, Open
- **Author**: Copilot
- **Created**: 2025-11-05
- **Branch**: `copilot/sub-pr-10-again`
- **Base**: `claude/text-map-logging-pyodide-011CUiUrJowSSDjfGqhCvRq7`
- **Summary**: Removes redundant lower-bound checks from elif clauses in `_get_heading_arrow()`
- **Files Changed**: `ship_combat/battle_map.py`
- **Impact**: Code simplification
- **Notes**: Duplicate of PRs #11, #15
- **Merge Conflicts**: Overlaps with PRs #11, #14, #15

### PR #11 - Remove redundant lower-bound checks in heading arrow conditionals [TODO]
- **Status**: DRAFT, Open
- **Author**: Copilot
- **Created**: 2025-11-05
- **Branch**: `copilot/sub-pr-10`
- **Base**: `claude/text-map-logging-pyodide-011CUiUrJowSSDjfGqhCvRq7`
- **Summary**: Addresses feedback on PR #10 by removing redundant condition checks
- **Files Changed**: `ship_combat/battle_map.py`
- **Impact**: Code simplification
- **Notes**: Duplicate of PRs #12, #15
- **Merge Conflicts**: Overlaps with PRs #12, #14, #15

---

## Feature Enhancements [3 PRs]

### PR #20 - Add end-to-end battle simulation e2e suite [TODO]
- **Status**: Open, Labeled: codex
- **Author**: yakuzadave (owner)
- **Created**: 2025-12-07
- **Branch**: `codex/add-folder-for-end-to-end-battle-simulation`
- **Base**: `main`
- **Summary**: 
  - Adds dedicated `tests/e2e` suite for full battle simulations
  - Includes deterministic rolldice stubbing
  - Demo-fleet smoke test exercising battle loop
  - Updates README with e2e test documentation
- **Files Changed**: `tests/e2e/`, `README.md`
- **Impact**: Testing infrastructure improvement
- **Notes**: Important for validation, should be prioritized
- **Merge Conflicts**: Low risk - adds new directory

### PR #19 - Make phase snapshots JSON-serializable [TODO]
- **Status**: Open, Labeled: codex
- **Author**: yakuzadave (owner)
- **Created**: 2025-11-17
- **Branch**: `codex/add-battle-snapshot-controller-module-m82nqd`
- **Base**: `main`
- **Summary**:
  - Replaces MappingProxyType with immutable FrozenDict for JSON serialization
  - Maintains immutability while enabling UI consumption
  - Adds regression coverage for mutation resistance and JSON serializability
- **Files Changed**: Snapshot-related modules
- **Impact**: Feature enhancement for UI compatibility
- **Notes**: Depends on or builds upon PR #18
- **Merge Conflicts**: May conflict with PR #18

### PR #18 - Freeze battle snapshots [TODO]
- **Status**: Open, Labeled: codex
- **Author**: yakuzadave (owner)
- **Created**: 2025-11-16
- **Branch**: `codex/add-battle-snapshot-controller-module`
- **Base**: `main`
- **Summary**:
  - Makes ShipSnapshot, FleetSnapshot, PhaseSnapshot immutable
  - Uses tuples and mapping proxies for read-only data
  - Updates BattleSnapshotController.record_phase
  - Extends test suite with immutability coverage
- **Files Changed**: Snapshot and controller modules
- **Impact**: Feature enhancement - data integrity
- **Notes**: Foundation for PR #19
- **Merge Conflicts**: May conflict with PR #19

---

## Documentation [1 PR]

### PR #27 - [WIP] Update project documentation for better clarity [IN_PROGRESS]
- **Status**: DRAFT, Open (CURRENT BRANCH)
- **Author**: Copilot
- **Created**: 2026-01-11
- **Branch**: `copilot/improve-project-documentation`
- **Base**: `main`
- **Summary**: Work on open PRs and improvement items without merge conflicts using systematic tracking approach
- **Files Changed**: To be determined - adding tracking infrastructure
- **Impact**: Project management and documentation
- **Notes**: This is the current working PR
- **Merge Conflicts**: Should be designed to avoid conflicts

---

## Analysis & Recommendations

### Consolidation Opportunities

**Group 1: Redundant Condition Fixes (PRs #11, #12, #15)**
- All three PRs fix the exact same issue in the exact same file
- Should be consolidated into a single PR
- PR #14 also includes this fix along with other improvements
- **Recommendation**: Close #11, #12, #15 as duplicates; use PR #14 or create consolidated version

**Group 2: Health Display Fixes (PRs #13, #14)**
- Both address health display issues
- PR #14 is more comprehensive, including PR #13's fix
- **Recommendation**: Close #13 as duplicate; use PR #14

**Group 3: Snapshot Features (PRs #18, #19)**
- PR #19 builds upon PR #18
- Sequential dependency relationship
- **Recommendation**: Merge #18 first, then #19

### Priority Order

1. **PR #20 (E2E Tests)** - High priority, low conflict risk, improves validation
2. **PR #14 (Comprehensive Fixes)** - Consolidates multiple fixes, moderate conflict risk
3. **PR #18 (Freeze Snapshots)** - Foundation for #19, low conflict risk
4. **PR #19 (JSON Serialization)** - Depends on #18, low conflict risk
5. **PRs #11, #12, #13, #15** - Close as duplicates of #14

### Conflict-Free Work Areas

For PR #27 (current branch), focus on:
- Documentation improvements (orthogonal to all code PRs)
- Project tracking infrastructure (this file and related)
- Test documentation
- Contribution guidelines
- No code changes that would conflict with open PRs

---

## Next Actions

- [ ] Run test suite to establish baseline
- [ ] Review each PR's actual code changes in detail
- [ ] Create consolidation plan for duplicate PRs
- [ ] Identify documentation gaps to address in PR #27
- [ ] Define merge sequence for feature PRs
- [ ] Communicate with PR authors about consolidation
