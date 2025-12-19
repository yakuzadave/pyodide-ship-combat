# Component Variation Testing

This document describes the comprehensive component variation tests that ensure system stability and prevent regressions as new components are added.

## Overview

The `test_component_variations.py` module contains 29 tests across 8 test classes that validate:
- All component types work correctly
- Component combinations are stable
- System can scale with new components
- Regressions are prevented
- Data integrity is maintained

## Test Categories

### 1. TestAllEngineVariations (3 tests)
Tests every engine type in the library to ensure:
- All engines create valid, movable ships
- Different engines produce different speeds
- Different engines provide varied maneuverability

**Coverage:** All 8 engine types (corvette to battleship)

### 2. TestAllShieldVariations (3 tests)
Tests every shield type to ensure:
- All shields create valid ships
- Shield capacities vary appropriately
- Regeneration rates differ between shield types

**Coverage:** All 6 shield types (light to capital)

### 3. TestAllWeaponVariations (4 tests)
Tests every weapon battery and loadout:
- All weapon batteries are valid
- All preset loadouts work correctly
- Weapon ratings vary appropriately
- Heat characteristics differ between weapons

**Coverage:** All 12 weapon batteries and 11 preset loadouts

### 4. TestAllReactorVariations (2 tests)
Tests every reactor type:
- All reactors create valid ships
- Power levels vary between reactor types

**Coverage:** All 4 reactor types

### 5. TestComponentCombinations (3 tests)
Tests component interactions:
- Engine-shield combinations work together
- Mixed component ships work in battle simulation
- Extreme/unusual combinations are valid

**Coverage:** Tests 9+ combinations of engines and shields, plus extreme cases

### 6. TestComponentScalability (3 tests)
Tests future extensibility:
- New engine types can be added without breaking
- New shield types can be added without breaking
- New weapon batteries follow consistent patterns

**Purpose:** Ensures system remains stable as components are added

### 7. TestRegressionPrevention (4 tests)
Prevents breaking changes:
- Engine speed ordering remains consistent (corvettes > battleships)
- Shield capacity ordering remains consistent (light < capital)
- Weapon heat balance stays reasonable
- Existing ships (demo_fleets) continue to work

**Purpose:** Catches breaking changes before they reach production

### 8. TestComponentDataIntegrity (4 tests)
Validates data consistency:
- No duplicate component names
- All required attributes present
- Loadouts reference valid weapons
- Values within reasonable bounds

**Purpose:** Ensures data quality and prevents configuration errors

### 9. TestCrossComponentInteractions (3 tests)
Tests system integration:
- Power allocation works with all component types
- Shield regeneration works for all shield types
- Weapon heat management works for all weapons

**Purpose:** Validates that game mechanics work across all component variations

## Test Statistics

```
Total Tests: 29
All Passing: ✓
Execution Time: ~0.12s

Component Coverage:
- Engines: 100% (8/8)
- Shields: 100% (6/6)
- Weapons: 100% (12/12)
- Reactors: 100% (4/4)
- Loadouts: 100% (11/11)

Component Combinations Tested: 15+
Regression Checks: 4
Scalability Tests: 3
Data Integrity Checks: 4
```

## Key Benefits

1. **Regression Prevention**: Tests catch breaking changes immediately
2. **Confidence**: All 41 components verified to work correctly
3. **Scalability**: Tests demonstrate how to add new components
4. **Documentation**: Tests serve as usage examples
5. **Quality**: Data integrity checks prevent configuration errors

## Running the Tests

```bash
# Run only component variation tests
pytest tests/test_component_variations.py -v

# Run all ship building tests
pytest tests/test_ship_*.py tests/test_fleet_*.py tests/test_component_*.py -v

# Run with coverage
pytest tests/test_component_variations.py --cov=ship_combat.ship_components
```

## Adding New Components

When adding new components, these tests will:

1. **Automatically validate** new entries in component libraries
2. **Ensure compatibility** with existing ships and mechanics
3. **Verify data integrity** (no duplicates, valid references)
4. **Test variations** (different values produce different results)

### Example: Adding a New Engine

```python
# 1. Add to ENGINE_LIBRARY in ship_components.py
ENGINE_LIBRARY["destroyer_fast"] = EngineComponent(
    "Fast Destroyer Drive", 
    speed=32, 
    maneuver=3
)

# 2. Run tests - they will automatically validate the new engine
pytest tests/test_component_variations.py::TestAllEngineVariations -v

# Tests will verify:
# - New engine creates valid ships ✓
# - Speed is within bounds (5-50) ✓
# - Maneuver is within bounds (1-5) ✓
# - No duplicate names ✓
# - All required attributes present ✓
```

## Test-Driven Development

The component variation tests support TDD for new features:

```python
# 1. Write test for new component type
def test_new_component_type_works():
    ship = ShipBuilder("Test").with_new_component("advanced").build()
    assert ship.new_attribute > 0

# 2. Implement new component type
NEW_COMPONENT_LIBRARY = {
    "advanced": NewComponent(...)
}

# 3. Run tests to validate
pytest tests/test_component_variations.py -v
```

## Continuous Integration

These tests should be run in CI/CD:

```yaml
# .github/workflows/test.yml
- name: Test component variations
  run: pytest tests/test_component_variations.py -v --cov
```

## Maintenance

### When to Update Tests

Update tests when:
- Adding new component types
- Modifying component attributes
- Changing component behavior
- Adding new game mechanics that use components

### What to Check

After changes, verify:
- All 29 tests still pass
- No regressions in existing functionality
- New components are validated
- Test execution time remains fast

## Related Documentation

- [SHIP_BUILDING.md](../SHIP_BUILDING.md) - Ship building guide
- [test_ship_components.py](test_ship_components.py) - Basic component tests
- [test_ship_builder.py](test_ship_builder.py) - Builder API tests
- [test_fleet_generator.py](test_fleet_generator.py) - Fleet generation tests

---

*Last updated: 2025-12-19*
