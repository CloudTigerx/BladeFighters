# Test Automation Quick Reference

## 🚀 Essential Commands

### Run Tests
```bash
# Run all tests
make test-all

# Run specific module tests
make test-puzzle      # Puzzle engine integration
make test-audio       # Audio module
make test-input       # Input module  
make test-screen      # Screen module

# Run with coverage
make test-coverage

# Run specific test file
make test-file FILE=modules/game_state_module/tests/test_puzzle_integration.py
```

### Development Workflow
```bash
# Quick test during development
make quick-test

# Watch mode (re-runs on file changes)
make test-watch

# Debug mode (shows all output)
make test-debug
```

## 📝 Test Writing Patterns

### Basic Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from modules.your_module.your_component import YourComponent

class TestYourComponent:
    """Test suite for YourComponent."""
    
    @pytest.fixture
    def component(self):
        """Create a fresh instance for each test."""
        return YourComponent()
    
    def test_method_name(self, component):
        """Test method_name functionality."""
        # Arrange
        input_data = "test_input"
        expected_output = "expected_output"
        
        # Act
        result = component.method_name(input_data)
        
        # Assert
        assert result == expected_output
```

### Integration Test Pattern
```python
class TestModuleAWithModuleB:
    """Test integration between Module A and Module B."""
    
    @pytest.fixture
    def component_a(self):
        return ComponentA()
    
    @pytest.fixture
    def component_b(self):
        return ComponentB()
    
    def test_integration_scenario(self, component_a, component_b):
        """Test integration scenario."""
        # Arrange
        test_data = "integration_test_data"
        
        # Act
        result_a = component_a.method_a(test_data)
        result_b = component_b.method_b(result_a)
        
        # Assert
        assert result_b == "expected_integration_result"
```

### Mock Dependencies
```python
@patch('pygame.mixer.Sound')
def test_with_mock(self, mock_sound):
    """Test with mocked dependencies."""
    mock_sound.return_value = Mock()
    
    # Your test code here
    result = your_function()
    
    # Verify mock was called
    mock_sound.assert_called_once()
```

## 🧪 Test Examples by Module

### Game State Module
```python
# Test puzzle integration
def test_puzzle_state_integration():
    state_manager = GameStateManager()
    puzzle_engine = MockPuzzleEngine()
    integrator = PuzzleStateIntegrator(state_manager, puzzle_engine)
    
    integrator.start_integration()
    integrator.set_game_active(True)
    
    assert state_manager.get("puzzle.game_active") == True
```

### Audio Module
```python
# Test audio system
def test_audio_system():
    audio_system = AudioSystem()
    
    audio_system.set_master_volume(0.8)
    assert audio_system.master_volume == 0.8
    
    with pytest.raises(ValueError):
        audio_system.set_master_volume(1.5)  # Invalid value
```

### Input Module
```python
# Test input manager
def test_input_manager():
    input_manager = UnifiedInputManager()
    
    # Simulate key press
    event = Mock()
    event.type = "KEYDOWN"
    event.key = "SPACE"
    
    input_manager.process_event(event)
    assert "SPACE" in input_manager.keys_pressed
```

## 🔧 Common Patterns

### Error Testing
```python
def test_invalid_input(self, component):
    """Test handling of invalid input."""
    with pytest.raises(ValueError):
        component.method_name(None)
```

### State Testing
```python
def test_state_changes(self, component):
    """Test state changes."""
    initial_state = component.get_state()
    
    component.perform_action()
    
    new_state = component.get_state()
    assert new_state != initial_state
```

### Performance Testing
```python
@pytest.mark.timeout(5)  # 5 second timeout
def test_performance_critical_operation(self):
    """Test performance-critical operation."""
    start_time = time.time()
    
    result = component.performance_critical_method()
    
    duration = time.time() - start_time
    assert duration < 1.0  # Should complete in under 1 second
```

## 📊 Coverage and Reporting

### Coverage Commands
```bash
# Generate coverage report
make test-coverage

# View HTML coverage report
make coverage-html
# Then open htmlcov/index.html in browser

# Check coverage thresholds
make coverage-check
```

### Coverage Targets
- **Game State Module**: 90% ✅
- **Audio Module**: 85% ✅  
- **Input Module**: 85% ✅
- **Screen Module**: 85% ✅
- **Overall**: 80% ✅

## 🚨 Troubleshooting

### Common Issues

**Import Errors**
```python
# Add to test file
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
```

**Mock Dependencies**
```python
@patch('pygame.mixer.Sound')
@patch('pygame.mixer.music')
def test_with_mocks(self, mock_music, mock_sound):
    # Test implementation
    pass
```

**State Pollution**
```python
@pytest.fixture(autouse=True)
def cleanup_state():
    """Clean up state after each test."""
    yield
    # Cleanup code here
```

### Debug Commands
```bash
# Run with debug output
make test-debug

# Run specific failing test
make test-file FILE=path/to/failing_test.py

# Run with verbose output
pytest -v -s path/to/test.py
```

## 📋 Test Checklist

### Before Writing Tests
- [ ] Understand the component being tested
- [ ] Identify dependencies that need mocking
- [ ] Plan test scenarios (happy path, error cases, edge cases)
- [ ] Consider integration points with other modules

### While Writing Tests
- [ ] Follow AAA pattern (Arrange, Act, Assert)
- [ ] Use descriptive test names
- [ ] Test both success and failure cases
- [ ] Mock external dependencies
- [ ] Keep tests independent and isolated

### After Writing Tests
- [ ] Run tests locally
- [ ] Check test coverage
- [ ] Ensure tests pass consistently
- [ ] Update documentation if needed

## 🎯 Best Practices

### Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern
- Keep tests independent

### Test Data
- Use fixtures for common data
- Create realistic test data
- Clean up after tests
- Use factories for complex objects

### Mocking
- Mock external dependencies
- Don't mock the code you're testing
- Verify mock interactions when important
- Use appropriate mock levels

### Performance
- Set realistic performance targets
- Use appropriate timeouts
- Test under realistic load
- Monitor resource usage

## 📞 Getting Help

### Resources
1. **Test Automation Guide**: `docs/TEST_AUTOMATION_GUIDE.md`
2. **Existing Tests**: Look at `modules/*/tests/` for examples
3. **Team Discussions**: Ask questions in GitHub Discussions
4. **GitHub Issues**: Report test framework issues

### Quick Commands
```bash
# Get help
make test-help

# List available tests
make test-list

# Get test statistics
make test-stats

# Run quick validation
make validate
```

---

**Test Quick Reference**  
**Version**: 1.0.0  
**Last Updated**: 2024-01-XX

*For detailed information, see the [Test Automation Guide](TEST_AUTOMATION_GUIDE.md).*
