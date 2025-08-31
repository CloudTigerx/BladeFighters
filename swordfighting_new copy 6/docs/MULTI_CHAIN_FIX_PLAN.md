# Multi-Chain Breaker System Fix Plan

## Problem Statement

The current BreakerManager uses flood-fill clearing that removes ALL connected same-color blocks in one operation. This prevents proper puzzle fighter combo chains where each step should clear only one group, followed by gravity settlement and potential new matches.

**Current Behavior:** Red+Blue+Green blocks → 1 chain, 8 blocks cleared
**Expected Behavior:** Red → Gravity → Blue → Gravity → Green = 3 chains

## Root Cause Analysis

### Current Architecture Issues

1. **BreakerManager.apply_breakers()** uses `_find_connected_blocks()` flood-fill
2. **ChainRunner** expects progressive clearing but gets everything at once
3. **Attack generation** works correctly but receives wrong chain statistics
4. **Gravity** not enforced between combo steps

### Files Requiring Changes

```
swordfighting_new/mechanics/breaker.py          [MAJOR REWRITE]
swordfighting_new/mechanics/chain_runner.py     [INTEGRATION]
swordfighting_new/mechanics/gravity.py          [ENHANCE]
swordfighting_new/attacks/manager.py            [MINOR]
tests/test_breakers.py                          [NEW TESTS]
```

## Implementation Plan

### Phase 1: Core Breaker Logic Redesign
**Estimated Scope:** 2-3 hours, HIGH RISK

#### 1.1 Modify BreakerManager._find_triggered_breakers()
- **OLD:** Returns all connected blocks via flood-fill
- **NEW:** Returns only the first valid breaker group found
- **Risk:** May break existing rectangle detection logic

#### 1.2 Add Step-by-Step Clearing
```python
# New method
def apply_single_breaker_group(self) -> dict:
    """Clear only ONE breaker group, return stats"""

# Modified method
def apply_breakers(self) -> int:
    """Apply one step of breaker clearing"""
```

#### 1.3 Cascade State Management
- Add `has_pending_breakers()` method
- Modify `cascade_in_progress` logic to check for remaining breakers
- Ensure proper termination conditions

### Phase 2: Gravity Integration
**Estimated Scope:** 1-2 hours, MEDIUM RISK

#### 2.1 Enforce Gravity Between Steps
- ChainRunner must call `gravity.apply_gravity()` after each breaker step
- Add gravity completion detection before next breaker check
- Coordinate with timing system for proper frame delays

#### 2.2 Board State Validation
- Ensure settled state before breaker detection
- Add validation for floating blocks during chain resolution

### Phase 3: ChainRunner Coordination
**Estimated Scope:** 1-2 hours, MEDIUM RISK

#### 3.1 Modified Chain Resolution Loop
```python
# Current: One-shot clearing
while breaker_manager.cascade_in_progress:
    stats = breaker_manager.apply_breakers()

# New: Step-by-step with gravity
while breaker_manager.has_pending_breakers():
    stats = breaker_manager.apply_single_breaker_group()
    gravity.apply_gravity()  # Settle before next check
    gravity.wait_for_settlement()
```

#### 3.2 Statistics Collection
- Modify pass statistics to capture each individual clearing step
- Ensure attack generation receives proper per-chain data
- Maintain backward compatibility with existing interfaces

### Phase 4: Testing & Validation
**Estimated Scope:** 2-3 hours, CRITICAL

#### 4.1 Create Comprehensive Test Suite
```python
# Test scenarios needed:
test_single_breaker_group()           # Baseline
test_two_chain_vertical_combo()       # Red→Blue
test_three_chain_complex_combo()      # Red→Blue→Green
test_rectangle_formation_during_chain() # Gravity creates rectangles
test_mixed_breaker_rectangle_combo()  # Complex scenarios
```

#### 4.2 Regression Testing
- Verify existing attack generation still works
- Confirm rectangle detection not broken
- Test all debug scenarios from `/debug/` folder

### Phase 5: Integration & Polish
**Estimated Scope:** 1 hour, LOW RISK

#### 5.1 Attack Manager Coordination
- Verify attack generation receives correct chain statistics
- Test combo multiplier scaling with new multi-chain data
- Ensure sprinkle/strike formulas work with step-by-step data

#### 5.2 Debug Tools Update
- Update debug scripts to work with new architecture
- Add visualization for step-by-step chain progression

## Risk Assessment

### HIGH RISK Components
- **BreakerManager rewrite:** Core game logic, affects everything
- **Flood-fill removal:** May break rectangle detection edge cases
- **Cascade termination:** Infinite loops if logic incorrect

### MEDIUM RISK Components
- **Gravity coordination:** Timing-dependent, hard to debug
- **ChainRunner integration:** State management complexity
- **Statistics collection:** Attack generation dependency

### LOW RISK Components
- **Attack generation:** Already working, minimal changes needed
- **Debug tools:** Non-critical functionality

## Testing Strategy

### Validation Checkpoints
1. **After Phase 1:** Single breaker clearing works correctly
2. **After Phase 2:** Gravity properly settles between steps
3. **After Phase 3:** Multi-chain scenarios produce correct statistics
4. **After Phase 4:** All existing functionality preserved
5. **After Phase 5:** Attack generation scaling verified

### Critical Test Scenarios
```python
# Scenario 1: Simple two-chain
Red breaker + Red block (bottom)
Blue breaker + Blue block (floating above)
Expected: 2 chains, not 1

# Scenario 2: Rectangle formation during chain
Breakers clear → Gravity → New rectangle forms → Strike generated
Expected: Proper attack scaling through multiple steps

# Scenario 3: Complex cascade
Multiple colors, multiple breaker groups, rectangles forming mid-chain
Expected: Proper step-by-step progression with correct statistics
```

## Implementation Order

1. **START:** Create backup branch of current working code
2. **Phase 1:** Rewrite BreakerManager (expect things to break)
3. **Phase 2:** Add gravity coordination
4. **Phase 3:** Fix ChainRunner integration
5. **Phase 4:** Extensive testing and debugging
6. **Phase 5:** Final integration and validation

## Rollback Plan

If implementation fails or becomes too complex:
1. **Immediate:** Revert to backed-up working code
2. **Alternative:** Implement "quick fix" that limits flood-fill scope instead of full rewrite
3. **Compromise:** Add configuration flag to switch between old/new behaviors

## Success Criteria

- [ ] Multi-chain scenarios produce correct chain counts
- [ ] Gravity properly settles between combo steps
- [ ] Attack generation receives accurate per-chain statistics
- [ ] Combo multipliers scale correctly through multi-step chains
- [ ] Rectangle detection still works during complex cascades
- [ ] No regression in existing functionality
- [ ] Performance remains acceptable (no significant slowdown)

---

**CRITICAL NOTE:** This is a fundamental architecture change affecting core game mechanics. Expect 6-8 hours of focused work with high probability of debugging challenges. Consider implementing in isolated branch with comprehensive testing before integration.

---

## PHASE 1 IMPLEMENTATION NOTES

### STARTING PHASE 1: Core Breaker Logic Redesign
**Date:** August 30, 2025
**Status:** IN PROGRESS

#### Pre-Implementation Analysis
- Current `BreakerManager.apply_breakers()` uses flood-fill via `_find_connected_blocks()`
- Need to modify to clear only ONE breaker group per call
- Must preserve rectangle detection logic
- Key files: `swordfighting_new/mechanics/breaker.py`

#### Changes Made:
1. **[DONE]** Added `_find_first_triggered_breaker_group()` method
2. **[DONE]** Added `_find_connected_breaker_group()` helper method
3. **[DONE]** Added `has_pending_breakers()` method
4. **[DONE]** Modified `apply_breakers()` to use single-group logic
5. **[DONE]** Updated `apply_breaker_chain()` termination logic
6. **[IN PROGRESS]** Fix cascade state management issue

#### Testing Checkpoints:
- [✅] Single breaker group detected correctly (finds first group only)
- [✅] Multi-chain scenarios produce correct chain counts (3 chains vs 1 chain)
- [✅] Rectangle detection still works (debug shows proper rectangle detection)
- [✅] Cascade termination works properly (no infinite loops)
- [✅] Attack generation gets proper per-chain statistics

#### Issues Encountered:
1. **~~Progressive clearing scope~~** ✅ FIXED: Now processes single breaker groups
2. **~~Cascade state management~~** ✅ FIXED: Proper state transitions between groups
3. **~~Chain termination~~** ✅ FIXED: `has_pending_breakers()` works correctly

#### Phase 1 Results - **SUCCESS!**
- **Before:** `1 chains, 13 total, per_pass=[13]` (flood-fill clearing all at once)
- **After:** `3 chains, 9 total, per_pass=[3, 3, 3]` (proper multi-chain progression!)
- **Behavior:** Green→gravity→Blue→gravity→Red = correct puzzle fighter mechanics

#### Phase 1 Status: **COMPLETE** ✅
Single breaker group clearing is working correctly. Each breaker group now clears
independently, enabling proper multi-chain combos. Ready for Phase 2 (gravity coordination).

#### Next Steps After Phase 1:
**Phase 1 COMPLETE ✅** - Core breaker logic successfully redesigned!

**Key Achievement:** Multi-chain combos now work correctly:
- Original problem: `1 chain, 8 blocks` (flood-fill clearing)
- Phase 1 solution: `3 chains, per_pass=[3,3,3]` (proper puzzle fighter mechanics)

**Ready for Phase 2:** Gravity integration between steps is the next logical enhancement.
The current system already calls `cascade_manager.apply_full()` between breaker passes,
so Phase 2 will focus on ensuring proper timing and settlement detection.

**Handoff Notes for Phase 2:**
- Core breaker system is stable and working
- Attack generation receives correct per-chain statistics
- `has_pending_breakers()` method enables proper chain termination
- Rectangle detection preserved throughout changes

## PHASE 2 IMPLEMENTATION NOTES

### PHASE 2 COMPLETE: Gravity Integration
**Date:** August 30, 2025
**Status:** ✅ COMPLETE

#### Phase 2 Objectives - All Achieved:
1. **✅ Better gravity settlement detection** - Added `_is_board_stable()` method to ChainRunner
2. **✅ Ensure proper timing between steps** - Added `wait_for_settlement()` coordination
3. **✅ Add validation for floating blocks** - Enhanced stability checks throughout cascade process
4. **✅ Enhance step-by-step coordination** - Improved cascade state management

#### Phase 2 Changes Made:

**ChainRunner Enhancements (`chain_runner.py`):**
- Added `_is_board_stable()` method with fallback manual stability checking
- Added `wait_for_settlement()` method for proper gravity coordination
- Enhanced cascade state management with better settlement detection
- Improved logging for gravity settlement tracking
- Added instability detection and forced additional gravity steps

**BreakerManager Enhancements (`breaker.py`):**
- Added `ensure_gravity_settled()` method for gravity coordination
- Added `wait_for_settlement()` method with safety limits
- Enhanced coordination with cascade manager stability checks

#### Phase 2 Results:
- **Before:** Basic gravity coordination between breaker passes
- **After:** Enhanced settlement detection with stability validation
- **Multi-chain behavior:** Preserved and improved (2-3 chains working correctly)
- **Both cascade modes:** Fast and step modes both enhanced

#### Phase 2 Testing Results:
- ✅ Simple two-chain scenario: `2 chains, 8 total, per_pass=[3, 5]`
- ✅ Complex three-chain scenario: `3 chains, 10 total, per_pass=[3, 2, 5]`
- ✅ Enhanced stability detection working in both fast and step modes
- ✅ Floating block validation preventing premature breaker detection
- ✅ All Phase 1 functionality preserved

#### Phase 2 Status: **COMPLETE** ✅
Gravity integration has been significantly enhanced with better settlement detection,
proper timing coordination, floating block validation, and improved step-by-step
coordination. The system now provides robust gravity settlement between breaker passes.

## PHASE 3 IMPLEMENTATION NOTES

### PHASE 3 COMPLETE: ChainRunner Coordination
**Date:** August 30, 2025
**Status:** ✅ COMPLETE

#### Phase 3 Objectives - All Achieved:
1. **✅ Enhanced Statistics Collection** - Separated breaker and cascade clearing statistics
2. **✅ Improved Step-by-Step Coordination** - Better tracking of each pass phase
3. **✅ Legacy Compatibility** - Maintained backward compatibility with existing interfaces
4. **✅ Enhanced Results Format** - Rich statistics for detailed analysis

#### Phase 3 Changes Made:

**ChainRunner Enhanced Statistics (`chain_runner.py`):**
- Added separate tracking for `per_pass_breaker` and `per_pass_cascade` statistics
- Enhanced `results` property to return comprehensive statistics dictionary
- Added `current_pass_breaker_clear` and `current_pass_cascade_clear` tracking
- Added `get_legacy_results()` method for backward compatibility
- Improved pass completion coordination with proper statistics finalization

**Statistics Breakdown:**
- **Breaker clearing**: Only the initial breaker group clearing per pass
- **Cascade clearing**: Additional blocks cleared during gravity settlement per pass
- **Combined totals**: Traditional per-pass totals for legacy compatibility
- **Pass stats**: Detailed rectangles, sprinkles, and other statistics per pass

#### Phase 3 Results:
- **Before:** Simple per-pass totals mixed breaker and cascade clearing
- **After:** Detailed separation of breaker vs cascade statistics
- **Enhanced format:** `{chains: 3, total_cleared: 13, per_pass_breaker: [3,3,3], per_pass_cascade: [0,2,2], per_pass_combined: [3,5,5]}`
- **Legacy support:** Old `(chains, total, per_pass)` format still available

#### Phase 3 Testing Results:
- ✅ Multi-chain scenarios: Clear separation of breaker (3,3,3) vs cascade (0,2,2) clearing
- ✅ Enhanced statistics: Comprehensive pass-by-pass breakdown available
- ✅ Legacy compatibility: `get_legacy_results()` returns expected format
- ✅ Rectangle detection: Works correctly with enhanced statistics
- ✅ Both cascade modes: 'fast' and 'step' modes both enhanced

#### Phase 3 Status: **COMPLETE** ✅
ChainRunner coordination has been significantly enhanced with detailed statistics
separation, improved step-by-step coordination, maintained legacy compatibility,
and comprehensive results formatting. The system now provides detailed insights
into both breaker clearing and cascade clearing phases.

**Ready for Phase 4:** Testing & Validation - comprehensive test suite creation
and regression testing to ensure all functionality works correctly together.
