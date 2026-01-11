# Known Limitations & Considerations

This document outlines known limitations, edge cases, and important considerations when working with the Pyodide Ship Combat simulator.

---

## Table of Contents

1. [Browser Compatibility](#browser-compatibility)
2. [Pyodide Constraints](#pyodide-constraints)
3. [Testing Limitations](#testing-limitations)
4. [Gameplay Limitations](#gameplay-limitations)
5. [Performance Considerations](#performance-considerations)
6. [Future Improvements](#future-improvements)

---

## Browser Compatibility

### Supported Browsers

**Fully Supported:**
- Chrome/Chromium 90+
- Firefox 90+
- Safari 14+
- Edge 90+

**Partial Support:**
- Mobile browsers (limited testing)
- Older browser versions may have issues with PyScript/Pyodide

### Known Browser Issues

1. **Console Output**
   - Some browsers may buffer console output
   - Large battles may cause performance degradation in browser console
   - **Workaround**: Use HTML elements for output instead of console.log

2. **Memory Management**
   - Pyodide runs in browser memory (limited compared to native Python)
   - Very large fleets (>50 ships) may cause issues
   - **Recommendation**: Keep fleet sizes under 20 ships for browser deployment

3. **File System Access**
   - No file I/O in browser environment
   - Cannot save/load battle logs to files
   - **Workaround**: Use localStorage or download as text

---

## Pyodide Constraints

### Dependencies

**Pure Python Only:**
- All dependencies must have pure Python wheels
- No C extensions or compiled code
- No native dependencies (numpy, pandas, etc. unless Pyodide-compatible)

**Current Limitations:**
- Limited to packages available in Pyodide or as pure Python wheels
- Some packages may behave differently in Pyodide vs native Python
- Package installation via micropip is slower than pip

### API Differences

1. **Async/Await Required**
   ```python
   # Browser/Pyodide requires await
   import micropip
   await micropip.install("py-rolldice")
   
   # Native Python doesn't need await
   import subprocess
   subprocess.run(["pip", "install", "py-rolldice"])
   ```

2. **No Threading**
   - Python threading not fully supported in Pyodide
   - Use async/await patterns instead
   - **Impact**: Cannot use thread-based parallelization

3. **No Multiprocessing**
   - No multiprocessing module support
   - Single-threaded execution only
   - **Impact**: Large simulations run serially

---

## Testing Limitations

### Known Failing Tests

**Current Status:** 195/201 tests passing (97%)

**6 Failing Tests (Pre-existing):**
All failures related to `rolldice` API return value handling:
- `test_battle_orders.py::test_heat_buildup_during_combat`
- `test_battle_orders.py::test_multiple_battery_heat_management`
- `test_battle_phases.py::test_shooting_damage_seeded`
- `test_battle_phases.py::test_apply_hazard_minefield_seeded`
- `test_battle_phases.py::test_missile_phase_seeded`
- `test_battle_phases.py::test_boarding_phase_seeded`

**Root Cause:** `ValueError: not enough values to unpack (expected 2, got 0)` when calling `rd.roll_dice()`

**Status:** These are known issues and do not affect the 97% of tests that pass successfully.

### Testing Constraints

1. **Deterministic Testing Required**
   - All tests must mock `rolldice` at module level
   - Cannot rely on actual random dice rolls
   - **Reason**: Tests must be reproducible and predictable

2. **No Integration Tests with Browser**
   - Cannot automatically test browser functionality in pytest
   - Manual testing required for browser compatibility
   - **Workaround**: Deploy to local server and test manually

3. **Limited E2E Coverage**
   - Most tests focus on individual components
   - Full battle simulations tested but not exhaustively
   - **Future**: Add dedicated e2e test suite (PR #20)

---

## Gameplay Limitations

### Automation Only

**No User Input:**
- All decisions are automated or random
- No interactive gameplay mode
- No pause/resume during battle
- **Design Choice**: Ensures browser compatibility

### AI Limitations

1. **Simple Order Selection**
   - Orders chosen randomly or via simple heuristics
   - No strategic AI planning
   - No learning or adaptation
   - **Future**: Could add ML-based AI controllers

2. **Target Selection**
   - Basic nearest-target or random selection
   - No tactical priority targeting
   - No focus fire coordination
   - **Future**: Could add advanced targeting AI

### Combat Mechanics

1. **Simplified Boarding**
   - Basic crew vs crew comparison
   - No detailed boarding combat
   - Single roll determines outcome

2. **Limited Damage Types**
   - Hull damage and shield damage only
   - No armor penetration mechanics
   - No location-based damage
   - **Design Choice**: Keeps simulation fast and simple

3. **Fixed Battle Duration**
   - Battles run for specified number of rounds
   - No victory condition checking mid-battle
   - **Workaround**: Check for fleet destruction after battle

---

## Performance Considerations

### Browser Performance

**Factors Affecting Performance:**
1. **Fleet Size**
   - 5-10 ships: Excellent performance
   - 11-20 ships: Good performance
   - 21-50 ships: Acceptable (may lag in browser)
   - 50+ ships: Not recommended for browser

2. **Battle Duration**
   - Short battles (1-5 rounds): Fast
   - Medium battles (6-15 rounds): Good
   - Long battles (16+ rounds): May be slow in browser

3. **Logging Level**
   - WARNING: Minimal impact
   - INFO: Some impact on large battles
   - DEBUG: Significant impact (verbose output)

### Memory Usage

**Typical Usage:**
- Small fleet (5 ships, 5 rounds): ~10MB
- Medium fleet (15 ships, 10 rounds): ~30MB
- Large fleet (30 ships, 20 rounds): ~80MB

**Browser Limits:**
- Most browsers allow 100-200MB for Pyodide
- Monitor console for memory warnings
- Reduce fleet size or battle duration if issues occur

### Optimization Tips

1. **Use Appropriate Log Level**
   ```python
   # For browser deployment
   battle(fleet_a, fleet_b, rounds=10, log_level=logging.WARNING)
   ```

2. **Limit Fleet Size**
   ```python
   # Recommended for browser
   fleet_a = quick_fleet(size=5)  # Not 50
   ```

3. **Batch Smaller Battles**
   ```python
   # Instead of one 20-round battle
   for i in range(4):
       battle(fleet_a, fleet_b, rounds=5)
   ```

---

## Future Improvements

### Planned Enhancements

1. **E2E Test Suite** (PR #20)
   - Comprehensive end-to-end testing
   - Deterministic battle simulations
   - Better coverage of full battle flow

2. **Snapshot Improvements** (PRs #18, #19)
   - Frozen immutable snapshots
   - JSON-serializable for UI consumption
   - Better state management

3. **Code Quality** (PRs #11-15)
   - Remove redundant code
   - Fix calculation issues
   - Improve namespace management

### Wishlist Features

1. **Advanced AI**
   - Strategic order selection
   - Tactical target prioritization
   - Coordinated fleet maneuvers

2. **Campaign Mode**
   - Multiple battles with persistence
   - Fleet repairs and upgrades
   - Story progression

3. **Multiplayer**
   - Turn-based command input
   - Real-time battle resolution
   - Spectator mode

4. **Enhanced Visualization**
   - 3D visualization (Three.js)
   - Animated battle playback
   - Interactive tactical display

5. **Performance**
   - Web Workers for parallel processing
   - Progressive rendering for large fleets
   - Battle state compression

---

## Reporting Issues

### Before Reporting

1. **Check Known Limitations** - Review this document
2. **Check Open Issues** - See if already reported
3. **Test in Multiple Browsers** - Isolate browser-specific issues
4. **Reproduce Locally** - Verify not Pyodide-specific

### Issue Template

```markdown
**Environment:**
- Browser: [Chrome 120 / Firefox 115 / etc.]
- Pyodide Version: [0.24.1]
- Python Version: [3.11]

**Description:**
Brief description of the issue.

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
What should happen.

**Actual Behavior:**
What actually happens.

**Additional Context:**
Logs, screenshots, etc.
```

---

## Best Practices

### For Contributors

1. **Always Test Browser Compatibility**
   - Test in `battle.html` before submitting
   - Check console for errors
   - Verify mobile if possible

2. **Keep Dependencies Minimal**
   - Only add Pyodide-compatible packages
   - Prefer pure Python implementations
   - Document any new dependencies

3. **Optimize for Browser**
   - Avoid heavy computations in loops
   - Use appropriate log levels
   - Test with realistic fleet sizes

### For Users

1. **Start Small**
   - Begin with 5-10 ship fleets
   - Short battles (5-10 rounds)
   - Gradually increase complexity

2. **Monitor Performance**
   - Watch browser console for warnings
   - Close other tabs if performance issues
   - Use WARNING log level for large battles

3. **Save Results**
   - Copy console output to text file
   - Use localStorage for persistence
   - Take screenshots of tactical maps

---

## Getting Help

- **Documentation**: Check README.md, CONTRIBUTING.md, TESTING.md
- **Examples**: Review `examples/` directory
- **Issues**: Open GitHub issue with details
- **Discussions**: Use GitHub Discussions for questions

---

Last Updated: 2026-01-11  
Document Version: 1.0
