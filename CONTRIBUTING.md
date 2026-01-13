# Contributing to Pyodide Ship Combat

Thank you for your interest in contributing to the Battlefleet Gothic-inspired fleet simulator! This document provides guidelines for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Testing Guidelines](#testing-guidelines)
5. [Code Style & Standards](#code-style--standards)
6. [Pull Request Process](#pull-request-process)
7. [Documentation](#documentation)
8. [Project Constraints](#project-constraints)

---

## Code of Conduct

This project follows standard open-source community guidelines:
- Be respectful and constructive in discussions
- Focus on what is best for the project and community
- Use welcoming and inclusive language
- Accept constructive criticism gracefully

---

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- Modern web browser (for testing Pyodide compatibility)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yakuzadave/pyodide-ship-combat.git
   cd pyodide-ship-combat
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # OR
   poetry install
   ```

3. **Run tests to verify setup:**
   ```bash
   pytest
   ```

4. **Try the command-line simulator:**
   ```bash
   python -m ship_combat.battle_sim --rounds 3
   ```

5. **Test browser compatibility:**
   Open `battle.html` in your browser to verify PyScript integration works.

---

## Development Workflow

### Branching Strategy

- **main** - Stable, production-ready code
- **feature/** - New features (e.g., `feature/fleet-formations`)
- **fix/** - Bug fixes (e.g., `fix/damage-calculation`)
- **docs/** - Documentation improvements
- **copilot/** or **codex/** - AI-assisted development branches

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Keep commits small and focused
   - Write descriptive commit messages
   - Follow code style guidelines (see below)

3. **Test your changes:**
   ```bash
   pytest                    # Run all tests
   pytest tests/test_*.py   # Run specific test file
   ```

4. **Test browser compatibility:**
   - Open `battle.html` in your browser
   - Verify no console errors
   - Test with different browsers if possible

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add feature: description"
   git push origin feature/your-feature-name
   ```

---

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_battle_sim.py

# Run tests matching a pattern
pytest -k "test_weapon"
```

### Test Requirements

All new features and bug fixes must include tests:

1. **Deterministic Tests** - Mock `rolldice` at module level for predictable behavior:
   ```python
   import sys
   from unittest.mock import MagicMock
   
   # Mock rolldice BEFORE imports
   mock_rolldice = MagicMock()
   sys.modules['rolldice'] = mock_rolldice
   
   # Now import code under test
   from ship_combat.battle_sim import shooting_phase
   
   # Configure mock behavior
   mock_rolldice.roll_dice.return_value = (15, "mocked")
   ```

2. **Test Coverage** - Aim for high coverage of new code:
   - Unit tests for individual functions/classes
   - Integration tests for battle phases
   - End-to-end tests for complete simulations

3. **Test Organization:**
   - Place tests in `tests/` directory
   - Name test files `test_*.py`
   - Name test functions `test_*`
   - Group related tests in classes

### Current Test Status

As of the last check:
- **Total Tests:** 201
- **Passing:** 195 (97%)
- **Known Issues:** 6 tests with pre-existing dice API issues

---

## Code Style & Standards

### Python Style

- Follow **PEP 8** conventions
- Use **type hints** where beneficial
- Keep functions focused and modular
- Use descriptive names for classes and functions

### Critical Constraints

**DO NOT:**
- ❌ Use `input()` or any blocking I/O (breaks browser compatibility)
- ❌ Add dependencies that aren't Pyodide-compatible
- ❌ Use file system operations that won't work in the browser
- ❌ Import packages without checking Pyodide compatibility

**DO:**
- ✅ Use `random.choice()`, `random.randint()` for randomization
- ✅ Use `rolldice.roll_dice()` for all dice mechanics
- ✅ Return values or append to lists instead of printing (when practical)
- ✅ Make all logic deterministic when given a seed
- ✅ Use `micropip` for runtime dependencies in browser

### Code Examples

**Good - Browser Compatible:**
```python
import random
import rolldice

def calculate_damage(weapon_rating: int) -> int:
    """Calculate damage using dice rolls."""
    roll, _ = rolldice.roll_dice(f"{weapon_rating}d6")
    return roll

def select_target(ships: list) -> Ship:
    """Randomly select a target from available ships."""
    return random.choice(ships)
```

**Bad - Not Browser Compatible:**
```python
# DON'T: Blocks browser execution
user_choice = input("Enter command: ")

# DON'T: File I/O not available in browser
with open("battle_log.txt", "w") as f:
    f.write(log_data)

# DON'T: Not Pyodide-compatible
import numpy as np  # Unless explicitly verified compatible
```

### Package Management

**Two Modes:**

1. **Browser/Pyodide Runtime:**
   ```python
   import micropip
   await micropip.install("py-rolldice")
   ```

2. **Local Development:**
   - Use `requirements.txt` or `pyproject.toml`
   - These files are for dev/CI only

---

## Pull Request Process

### Before Submitting

1. **Run the test suite:**
   ```bash
   pytest
   ```

2. **Test browser compatibility:**
   - Open `battle.html` and verify it works
   - Check browser console for errors

3. **Review your changes:**
   - Remove debug code and comments
   - Ensure code follows style guidelines
   - Check for merge conflicts with main

4. **Update documentation:**
   - Update relevant .md files if APIs changed
   - Add examples if introducing new features
   - Update CHANGELOG.md if applicable

### PR Checklist

When submitting a pull request, ensure:

- [ ] All tests pass (`pytest`)
- [ ] No blocking I/O added (no `input()`)
- [ ] Dependencies are Pyodide-compatible
- [ ] Dice mechanics use `rolldice.roll_dice()`
- [ ] Tests mock rolldice at module level
- [ ] Code follows PEP 8 style
- [ ] Documentation updated if public API changed
- [ ] Browser compatibility tested (if applicable)
- [ ] PR description clearly explains changes

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- List of specific changes made
- Organized by category if multiple areas affected

## Testing
- How the changes were tested
- Any manual testing performed
- Browser compatibility verified: Yes/No

## Related Issues
Closes #123 (if applicable)

## Screenshots
(If UI changes were made)
```

### Review Process

1. **Automated Checks:**
   - CI runs test suite automatically
   - Must pass before review

2. **Code Review:**
   - At least one maintainer review required
   - Address feedback constructively
   - Push updates to the same branch

3. **Merge:**
   - PRs are merged via squash or merge commit
   - Branch deleted after merge

---

## Documentation

### Documentation Files

- **README.md** - Main project documentation and quickstart
- **AGENTS.md** - AI agent-specific guidance
- **DESIGN_CANVAS.md** - Design documentation and architecture
- **ADVANCED_FEATURES.md** - Detailed feature documentation
- **LOGGING.md** - Logging and visualization guide
- **SHIP_BUILDING.md** - Ship building system documentation
- **CONTRIBUTING.md** - This file

### Documentation Standards

When adding or updating documentation:

1. **Be Clear and Concise:**
   - Use simple language
   - Provide code examples
   - Include expected output where helpful

2. **Keep Examples Runnable:**
   - Test all code examples
   - Verify they work in both local and browser environments

3. **Cross-Reference:**
   - Link to related documentation
   - Reference specific files/functions

4. **Update When Changing APIs:**
   - Document breaking changes clearly
   - Provide migration examples
   - Update all affected documentation files

---

## Project Constraints

### Browser-First Design

This project is designed to run in **Pyodide** (browser Python environment):

- All code must be pure Python or Pyodide-compatible
- No file system access
- No blocking I/O operations
- Dependencies loaded via `micropip` at runtime

### Automated Simulation

The simulator is **fully automated**:

- No user input during battle execution
- All decisions are deterministic or randomized
- Reproducible with seeded random number generators

### Testing Requirements

Tests must be **deterministic**:

- Mock `rolldice` at module level
- Use consistent test data
- Avoid relying on random behavior in tests

---

## Getting Help

- **Issues:** Open an issue on GitHub for bugs or feature requests
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** Check existing .md files for guidance
- **Examples:** Review test files for usage patterns

---

## Common Tasks

### Adding a New Ship Class

1. Extend `Ship` model in `ship_combat/models.py`
2. Add to fleet setup in `ship_combat/fleet_setup.py`
3. Add tests in `tests/test_*.py`
4. Update `DESIGN_CANVAS.md` documentation

### Adding a New Battle Order

1. Add order to `BATTLE_ORDERS` list
2. Implement order logic in battle phase handler
3. Add tests with mocked dice rolls
4. Document in `ADVANCED_FEATURES.md`

### Adding New Features

1. Check Pyodide compatibility for dependencies
2. Write tests first (TDD approach)
3. Implement feature maintaining browser compatibility
4. Update relevant documentation
5. Test in browser via `battle.html`

---

## Recognition

Contributors will be recognized in:
- Git commit history
- GitHub contributor list
- Release notes (for significant contributions)

Thank you for contributing to Pyodide Ship Combat! 🚀
