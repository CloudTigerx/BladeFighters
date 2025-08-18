# Phase 4 Quick Reference Guide

**Senior Dev 1 - Phase 4 Support**

## Current Status

✅ **Phase 1**: Preparation & Analysis - COMPLETE
✅ **Phase 2**: Module Creation - COMPLETE  
✅ **Phase 3**: Integration Testing - COMPLETE
🔄 **Phase 4**: Gradual Migration - IN PROGRESS

## Phase 4 Tasks

### Task 4A - Import Updates (Senior Dev 2)
**Status**: [IN PROGRESS]

**What to do**:
1. Add import to `puzzle_module.py`:
   ```python
   from core.cluster_detection import ClusterDetector
   ```

2. Initialize in `PuzzleEngine.__init__`:
   ```python
   self.cluster_detector = ClusterDetector(
       grid_width=self.grid_width,
       grid_height=self.grid_height,
       total_grid_height=self.total_grid_height
   )
   ```

**Test**: Verify imports work without errors

### Task 4B - Method Replacement (Senior Dev 2 & 3)
**Status**: [IN PROGRESS]

**Senior Dev 2 - Replace these methods**:
- `detect_clusters()`
- `find_all_clusters()`
- `is_cluster_supported()`

**Senior Dev 3 - Replace these methods**:
- `find_rectangular_clusters_for_render()`
- `find_connected_pieces()`
- `_extend_cluster()` (internal)

**Template for each method**:
```python
def method_name(self, *args):
    """
    Backward compatibility wrapper for method_name.
    """
    return self.cluster_detector.method_name(*args, self.puzzle_grid)
```

### Task 4C - Renderer Integration (Senior Dev 2)
**Status**: [IN PROGRESS]

**What to do**:
1. Update `puzzle_renderer.py` to use new ClusterDetector
2. Test visual cluster highlighting
3. Test cluster glow effects
4. Verify no visual regressions

## Quick Test Commands

### Test Cluster Detection
```bash
python -c "from core.cluster_detection import ClusterDetector; detector = ClusterDetector(10, 20, 25); grid = [[None for _ in range(10)] for _ in range(25)]; grid[5][2] = 'red'; grid[5][3] = 'red'; grid[6][2] = 'red'; grid[6][3] = 'red'; clusters = detector.detect_clusters(grid); print(f'Clusters: {clusters}')"
```

### Test Support Detection
```bash
python -c "from core.cluster_detection import ClusterDetector; detector = ClusterDetector(10, 20, 25); grid = [[None for _ in range(10)] for _ in range(25)]; grid[5][2] = 'red'; grid[5][3] = 'red'; grid[6][2] = 'red'; grid[6][3] = 'red'; cluster = {(2, 5), (2, 6), (3, 5), (3, 6)}; supported = detector.is_cluster_supported(cluster, grid); print(f'Supported: {supported}')"
```

### Test Integration
```bash
python tests/cluster_gravity_integration_test.py
```

## Rollback Instructions

If any method replacement causes issues:

1. **Comment out wrapper method**
2. **Restore original method implementation**
3. **Test to verify fix**
4. **Debug the specific issue**
5. **Retry replacement after fix**

## Success Criteria

- [ ] All imports work without errors
- [ ] All cluster methods work identically to before
- [ ] Visual effects work correctly
- [ ] Gravity system works correctly
- [ ] No performance regressions
- [ ] All tests pass

## Next Phase Preview

**Phase 5**: Cleanup & Optimization
- **Task 5A**: Remove old cluster methods (Senior Dev 2)
- **Task 5B**: Performance optimization (Senior Dev 1)
- **Task 5C**: Documentation updates (Senior Dev 3)

## Support

For technical issues during Phase 4:
- Check the `docs/BACKWARD_COMPATIBILITY_GUIDE.md`
- Run the quick test commands above
- Use the rollback instructions if needed
- Senior Dev 1 is available for technical support

**Remember**: Gradual migration means one method at a time. Test each replacement thoroughly before moving to the next.
