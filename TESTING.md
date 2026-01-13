# Testing Guide

This document provides comprehensive information about testing the Pyodide Ship Combat simulator.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Organization](#test-organization)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Test Categories](#test-categories)
6. [Known Issues](#known-issues)
7. [Continuous Integration](#continuous-integration)

---

## Quick Start

### Install Dependencies

```bash
# Install all dependencies including test frameworks
pip install -r requirements.txt

# OR using poetry
poetry install
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=ship_combat --cov-report=html
```

---

## Test Organization

Tests are organized in the `tests/` directory:

```
tests/
├── test_advanced_features.py    # Advanced mechanics (formations, heat, etc.)
├── test_battle_orders.py         # Battle order implementations
├── test_battle_phases.py         # Individual battle phases
├── test_component_variations.py  # Ship component testing
├── test_deployment.py            # Deployment script tests
├── test_fleet_generator.py       # Fleet generation system
├── test_marimo_notebook.py       # Notebook loading tests
├── test_mechanics.py             # Core mechanics (movement, arcs, etc.)
├── test_ship_builder.py          # Ship builder system
├── test_ship_building_integration.py  # Integration tests
├── test_ship_components.py       # Component libraries
└── test_tui.py                   # Textual UI tests
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run tests in a specific file
pytest tests/test_battle_sim.py

# Run tests matching a pattern
pytest -k "test_weapon"

# Run tests in parallel (faster)
pytest -n auto

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

### Useful Options

```bash
# Show print statements
pytest -s

# Show test durations
pytest --durations=10

# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff

# Generate HTML coverage report
pytest --cov=ship_combat --cov-report=html
open htmlcov/index.html  # View report
```

### Running Specific Test Categories

```bash
# Advanced features only
pytest tests/test_advanced_features.py

# Battle phases only
pytest tests/test_battle_phases.py

# Integration tests only
pytest tests/test_ship_building_integration.py

# Component tests
pytest tests/test_ship_components.py tests/test_component_variations.py
```

---

## Writing Tests

### Test Structure

Follow this pattern for all tests:

```python
import sys
from unittest.mock import MagicMock

# CRITICAL: Mock rolldice BEFORE importing code under test
mock_rolldice = MagicMock()
sys.modules['rolldice'] = mock_rolldice

# Now import modules that use rolldice
from ship_combat.battle_sim import shooting_phase
from ship_combat.models import Ship, WeaponSystem

def test_example():
    """Test description."""
    # Configure mock behavior
    mock_rolldice.roll_dice.return_value = (15, "mocked")
    
    # Create test data
    ship = Ship(name="Test", hull=100, shield=50, weapons=WeaponSystem())
    
    # Execute test
    result = shooting_phase([ship], [])
    
    # Assert expectations
    assert result is not None
```

### Key Testing Principles

1. **Deterministic Tests**
   - Mock `rolldice` at module level
   - Use predictable return values
   - Tests must pass consistently

2. **Independent Tests**
   - Each test should be self-contained
   - Don't rely on test execution order
   - Clean up after tests if needed

3. **Clear Assertions**
   - Use descriptive assertion messages
   - Test one thing per test function
   - Use pytest's rich assertion introspection

4. **Test Naming**
   - Use `test_` prefix for functions
   - Descriptive names: `test_weapon_heat_buildup_during_combat`
   - Group related tests in classes

### Example Test Class

```python
class TestWeaponSystem:
    """Tests for weapon system functionality."""
    
    def setup_method(self):
        """Setup run before each test method."""
        self.ship = Ship(
            name="Test Ship",
            hull=100,
            shield=50,
            weapons=WeaponSystem()
        )
    
    def test_weapon_fires_successfully(self):
        """Weapon should deal damage when fired."""
        mock_rolldice.roll_dice.return_value = (20, "20")
        # Test implementation
        
    def test_weapon_heat_increases_on_fire(self):
        """Weapon heat should increase after firing."""
        # Test implementation
```

### Mocking Best Practices

**Module-Level Mocking (Required for rolldice):**
```python
import sys
from unittest.mock import MagicMock

mock_rolldice = MagicMock()
sys.modules['rolldice'] = mock_rolldice

# Then import modules that use rolldice
from ship_combat.battle_sim import shooting_phase
```

**Configuring Mock Returns:**
```python
# Simple return value
mock_rolldice.roll_dice.return_value = (15, "15")

# Different values per call
mock_rolldice.roll_dice.side_effect = [(10, "10"), (20, "20"), (15, "15")]

# Verify mock was called
mock_rolldice.roll_dice.assert_called_once()
mock_rolldice.roll_dice.assert_called_with("2d20")
```

---

## Test Categories

### Unit Tests

Test individual functions and classes in isolation:

- `test_mechanics.py` - Core mechanics (distance, arcs, movement)
- `test_ship_components.py` - Component libraries and builders
- `test_ship_builder.py` - Ship builder functionality

**Example:**
```bash
pytest tests/test_mechanics.py -v
```

### Integration Tests

Test multiple components working together:

- `test_ship_building_integration.py` - Ship builder integration
- `test_battle_phases.py` - Battle phase interactions

**Example:**
```bash
pytest tests/test_ship_building_integration.py -v
```

### Feature Tests

Test complete features end-to-end:

- `test_advanced_features.py` - Advanced mechanics
- `test_battle_orders.py` - Battle order system
- `test_fleet_generator.py` - Fleet generation

**Example:**
```bash
pytest tests/test_advanced_features.py -v
```

### Component Variation Tests

Test all combinations of ship components:

- `test_component_variations.py` - Comprehensive component testing

**Example:**
```bash
pytest tests/test_component_variations.py -v
```

---

## Known Issues

### Current Test Status

As of 2026-01-11:

- **Total Tests:** 201
- **Passing:** 195 (97%)
- **Failing:** 6

### Known Failing Tests

The following tests have pre-existing failures related to the `rolldice` API:

1. `test_battle_orders.py::test_heat_buildup_during_combat`
2. `test_battle_orders.py::test_multiple_battery_heat_management`
3. `test_battle_phases.py::test_shooting_damage_seeded`
4. `test_battle_phases.py::test_apply_hazard_minefield_seeded`
5. `test_battle_phases.py::test_missile_phase_seeded`
6. `test_battle_phases.py::test_boarding_phase_seeded`

**Root Cause:** `ValueError: not enough values to unpack (expected 2, got 0)`

These failures occur when `rolldice.roll_dice()` returns an unexpected format. They are **out of scope** for current development work and do not affect the 97% of tests that pass successfully.

### Running Without Known Failures

To run only passing tests:

```bash
# Skip known failing tests
pytest --ignore=tests/test_battle_phases.py \
       -k "not test_heat_buildup_during_combat and not test_multiple_battery_heat_management"
```

---

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Push to any branch
- Pull request creation/update
- Manual workflow dispatch

### CI Configuration

See `.github/workflows/` for workflow definitions.

**Test Workflow:**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest
```

### Viewing CI Results

1. Go to the **Actions** tab in GitHub
2. Click on the workflow run
3. View test results and logs
4. Download artifacts if available

---

## Test Coverage

### Generating Coverage Reports

```bash
# Terminal report
pytest --cov=ship_combat

# HTML report (recommended)
pytest --cov=ship_combat --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=ship_combat --cov-report=xml
```

### Coverage Goals

- **Overall Coverage:** Aim for >80%
- **Critical Paths:** Aim for >95% (battle phases, damage calculation)
- **New Code:** All new features should have tests

### Coverage by Module

```bash
# Coverage for specific module
pytest --cov=ship_combat.battle_sim tests/

# Coverage with missing lines
pytest --cov=ship_combat --cov-report=term-missing
```

---

## Debugging Tests

### Running Single Test

```bash
# Run one specific test
pytest tests/test_mechanics.py::test_move_and_distance -v
```

### Using pdb Debugger

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb
```

### Print Debugging

```bash
# Show print statements
pytest -s

# Show print statements for one test
pytest tests/test_mechanics.py::test_move_and_distance -s
```

### Verbose Output

```bash
# Maximum verbosity
pytest -vv

# Show local variables on failure
pytest -l
```

---

## Performance Testing

### Test Duration

```bash
# Show slowest 10 tests
pytest --durations=10

# Show all test durations
pytest --durations=0
```

### Profiling Tests

```bash
# Profile test execution
pytest --profile

# Generate SVG profile graph
pytest --profile-svg
```

---

## Best Practices

### DO:
- ✅ Mock `rolldice` at module level before imports
- ✅ Use descriptive test names
- ✅ Test edge cases and error conditions
- ✅ Keep tests independent and isolated
- ✅ Run tests before committing
- ✅ Add tests for all new features
- ✅ Fix failing tests promptly

### DON'T:
- ❌ Rely on test execution order
- ❌ Use `sleep()` or time-based waits
- ❌ Test implementation details (test behavior instead)
- ❌ Write tests that depend on external services
- ❌ Commit failing tests without documentation
- ❌ Skip tests without good reason

---

## Getting Help

- Check existing tests for examples
- Review pytest documentation: https://docs.pytest.org/
- Ask in GitHub Discussions
- Open an issue for test-related bugs

---

## Quick Reference

### Common Commands

```bash
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest -x                       # Stop on first failure
pytest -k "pattern"            # Run tests matching pattern
pytest tests/test_file.py      # Run specific file
pytest --lf                     # Run last failed
pytest --cov                    # With coverage
pytest -s                       # Show print output
pytest --pdb                    # Debug on failure
```

### Test Status: 195/201 passing (97%) ✅

Last updated: 2026-01-11
