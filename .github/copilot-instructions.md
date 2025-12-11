# GitHub Copilot Instructions for Pyodide Ship Combat

## Project Overview

This is a browser-compatible, fully automated Python fleet battle simulator inspired by Battlefleet Gothic. The project is designed to run in Pyodide (browser/JupyterLite environments) using `py-rolldice` for dice mechanics.

**Key Characteristics:**
- **Browser-first**: Runs in Pyodide/JupyterLite with zero npm/build step
- **Fully automated**: No user input (`input()`) - all actions are deterministic or randomized
- **Pure Python**: All dependencies must be Pyodide-compatible
- **Test-driven**: Uses pytest with deterministic dice mocking

## Repository Structure

```
/
├── ship_combat/              # Main package
│   ├── battle_sim.py        # Core simulation engine
│   ├── models.py            # Ship, WeaponSystem, Fleet models
│   ├── battle_logger.py     # Structured logging system
│   ├── battle_map.py        # ASCII tactical maps
│   ├── fleet_setup.py       # Fleet configuration
│   └── tui/                 # Textual-based terminal UI
│       ├── app.py           # TUI application
│       └── snapshots.py     # Battle snapshot feed
├── tests/                   # Test suite
├── BATTLE_SIM.py            # Legacy root module (maintained for compatibility)
├── battle.html              # PyScript browser demo
├── deploy.py                # Deployment script
└── *.md                     # Documentation files
```

## Development Workflow

### Setting Up Development Environment

**Local Development:**
```bash
pip install -r requirements.txt
# OR
poetry install
```

**Browser/Pyodide:**
Dependencies are installed at runtime via `micropip`:
```python
import micropip
await micropip.install("py-rolldice")
```

### Running Tests

```bash
pytest                    # Run all tests
pytest tests/test_*.py   # Run specific test file
pytest -v                # Verbose output
```

### Running the Simulator

**Command Line:**
```bash
python -m ship_combat.battle_sim --rounds 3
```

**Browser:**
Open `battle.html` in a modern browser - it will automatically run a PyScript simulation.

### Testing Locally Before Deployment

```bash
python deploy.py --test    # Run tests only
python deploy.py --build   # Build deployment package
cd build && python -m http.server 8000  # Test locally
```

## Coding Standards

### Python Style
- Follow PEP 8 conventions
- Use type hints where beneficial
- Keep functions focused and modular
- Classes use clear, descriptive names (e.g., `Ship`, `WeaponSystem`, `BattleSnapshot`)

### Critical Constraints

**DO NOT:**
- Use `input()` or any blocking I/O - breaks browser compatibility
- Add dependencies that aren't Pyodide-compatible
- Use file system operations that won't work in browser
- Import packages without checking Pyodide compatibility

**DO:**
- Use `random.choice()`, `random.randint()` for randomization
- Use `rolldice.roll_dice()` for all dice mechanics
- Return values or append to lists instead of printing (when practical)
- Make all logic deterministic when given a seed

### Testing Practices

**Critical: Deterministic Dice Rolling**

All tests use module-level `rolldice` mocking for predictable behavior:

```python
import sys
from unittest.mock import MagicMock

# Mock rolldice at module level BEFORE imports
mock_rolldice = MagicMock()
sys.modules['rolldice'] = mock_rolldice

# Now import code under test
from ship_combat.battle_sim import ...

# Configure mock behavior
mock_rolldice.roll_dice.return_value = (15, "mocked")
```

**Helper Pattern:**
```python
def get_rolldice():
    """Get the mocked rolldice module for verification."""
    return sys.modules['rolldice']
```

**Why:** Tests must be deterministic. Direct imports of rolldice create race conditions with mocking.

### Package Management

**Two modes of operation:**

1. **Browser/Pyodide Runtime:**
   - Use `micropip` to install packages at runtime
   - All runtime deps must be pure Python wheels
   - Example: `await micropip.install("py-rolldice")`

2. **Local Development:**
   - Use `requirements.txt` or `pyproject.toml`
   - These files are for dev/CI only, not browser runtime

### Snapshot Systems

**Two distinct BattleSnapshot classes exist:**

1. **`ship_combat.controller.BattleSnapshot`** (if it exists)
   - JSON-serializable phase snapshots
   - Used for battle state tracking

2. **`ship_combat.tui.snapshots.BattleSnapshot`**
   - Async UI feed dataclass
   - Used by Textual TUI app
   - Contains: `round_number`, `fleet_a`, `fleet_b`, `log_lines`, `summary_lines`

Keep these separate - they serve different purposes.

## Key Features & Systems

### Battle Simulation Flow

1. **Order Selection**: Ships choose random orders each round
2. **Environmental Hazards**: Random events affect ships
3. **Shooting Phase**: Ships fire weapons at targets
4. **Ordnance Phase**: Missiles, torpedoes
5. **Boarding Actions**: Close combat between ships
6. **End Phase**: Repairs, system checks

### Advanced Features (v2.0+)

- Fleet formations with leader-following
- Evasive maneuvers with defense bonuses
- Weapon heat management
- Power allocation (weapons/shields/engines)
- Shield regeneration
- Critical hit system
- 14 battle orders including tactical options

See `ADVANCED_FEATURES.md` for detailed documentation.

### Logging & Visualization

- Structured logging with configurable levels
- ASCII tactical maps showing positions and ranges
- Battle statistics and analytics
- Post-battle reports
- Textual TUI for interactive visualization

See `LOGGING.md` for complete guide.

## Common Tasks

### Adding a New Ship Class

1. Extend `Ship` model in `ship_combat/models.py`
2. Add to fleet setup in `ship_combat/fleet_setup.py`
3. Add corresponding tests in `tests/test_*.py`
4. Update documentation in `DESIGN_CANVAS.md`

### Adding a New Battle Order

1. Add order to `BATTLE_ORDERS` list in relevant module
2. Implement order logic in battle phase handler
3. Add tests with mocked dice rolls
4. Document in `ADVANCED_FEATURES.md` or `DESIGN_CANVAS.md`

### Adding New Features

1. Check Pyodide compatibility for any new dependencies
2. Write tests first (TDD approach)
3. Implement feature maintaining browser compatibility
4. Update relevant documentation
5. Test in browser via `battle.html` or local server

## Documentation Files

- **README.md**: Main project documentation, quickstart, examples
- **AGENTS.md**: AI agent-specific guidance (complementary to this file)
- **DESIGN_CANVAS.md**: Design documentation, flow, modular planning
- **ADVANCED_FEATURES.md**: Detailed feature documentation
- **LOGGING.md**: Logging and visualization guide

## Deployment

The project includes a deployment script (`deploy.py`) for packaging and deploying to static hosting:

```bash
python deploy.py --full          # Test, build, and deploy
python deploy.py --target netlify     # Deploy to Netlify
python deploy.py --target github-pages  # Deploy to GitHub Pages
```

## Testing Checklist for Changes

Before submitting changes:

- [ ] All tests pass (`pytest`)
- [ ] No blocking I/O added (no `input()`, file operations safe)
- [ ] Dependencies are Pyodide-compatible
- [ ] Dice mechanics use `rolldice.roll_dice()`
- [ ] Tests mock rolldice at module level
- [ ] Documentation updated if public API changed
- [ ] Code follows PEP 8 style
- [ ] Browser compatibility tested (if applicable)

## Getting Help

- Check existing documentation in `*.md` files
- Review test files for usage examples
- Look at `battle.html` for browser integration patterns
- Refer to `AGENTS.md` for architecture details
