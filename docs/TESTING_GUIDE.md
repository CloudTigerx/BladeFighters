# Testing Guide for Module Developers

## Overview

This guide provides comprehensive instructions for module developers to understand and use the test automation framework. It covers how to write tests, run them, and integrate with the existing testing infrastructure.

## 🎯 Quick Start

### Basic Testing Commands

```bash
# Run all tests
make test-all

# Run tests for specific modules
make test-audio      # Audio module tests
make test-screen     # Screen module tests  
make test-input      # Input module tests

# Run basic tests only
make test

# Run with coverage
make test-coverage
```

### For Your Module

Replace `[YOUR_MODULE]` with your module name (e.g., `audio`, `screen`, `input`):

```bash
# Run your module's tests
make test-[YOUR_MODULE]

# Run your module's tests with debugging
make debug-module MODULE=[YOUR_MODULE]
```

## 📁 Test Structure

### Module Test Organization

```
modules/[your_module]/
├── tests/
│   ├── test_[main_file].py          # Main functionality tests
│   ├── test_[supporting_file].py    # Supporting functionality tests
│   ├── test_integration.py          # Integration tests
│   └── test_[specific_feature].py   # Feature-specific tests
```

### Integration Test Structure

```
tests/integration/
├── test_[module]_module_integration.py  # Module integration tests
├── test_suite_framework.py             # Test framework utilities
└── fixtures/                           # Test data and fixtures
```

## 🧪 Writing Tests

### Basic Test Structure

```python
import pytest
from modules.[your_module].[main_file] import [MainClass]

class Test[MainClass]:
    """Test cases for [MainClass]."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.[instance] = [MainClass]()
    
    def test_initialization(self):
        """Test that the class initializes correctly."""
        assert self.[instance] is not None
        # Add more specific assertions
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = self.[instance].[method_name]()
        assert result == expected_value
    
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ExpectedException):
            self.[instance].[method_name](invalid_input)
```

### Integration Test Example

```python
import pytest
from modules.[your_module].[main_file] import [MainClass]
from modules.game_state_module.game_state_manager import GameStateManager

class Test[Module]Integration:
    """Integration tests for [Module] with GameStateManager."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.state_manager = GameStateManager()
        self.[module_instance] = [MainClass](self.state_manager)
    
    def test_state_integration(self):
        """Test integration with state manager."""
        # Test that your module properly integrates with GameStateManager
        result = self.[module_instance].[integration_method]()
        assert result is True
        
        # Verify state changes
        state_value = self.state_manager.get("[your_module].[field]")
        assert state_value == expected_value
    
    def test_callback_integration(self):
        """Test callback integration."""
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        self.[module_instance].register_callback(test_callback)
        self.[module_instance].[trigger_method]()
        
        assert callback_called is True
```

### Performance Test Example

```python
import time
import pytest
from modules.[your_module].[main_file] import [MainClass]

class Test[Module]Performance:
    """Performance tests for [Module]."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        self.[instance] = [MainClass]()
    
    def test_operation_performance(self):
        """Test that operations complete within acceptable time."""
        start_time = time.time()
        
        # Perform the operation
        result = self.[instance].[performance_critical_method]()
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Assert performance requirements
        assert duration < 100  # Should complete in less than 100ms
        assert result == expected_value
    
    def test_memory_usage(self):
        """Test memory usage is within acceptable limits."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform memory-intensive operation
        self.[instance].[memory_intensive_method]()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Assert memory usage is reasonable (e.g., less than 10MB increase)
        assert memory_increase < 10 * 1024 * 1024  # 10MB
```

## 🔧 Test Framework Features

### Test Data Management

```python
from tests.integration.test_suite_framework import TestDataManager

class Test[Module]WithData:
    """Tests using test data management."""
    
    def setup_method(self):
        """Set up test data."""
        self.data_manager = TestDataManager()
        self.test_data = self.data_manager.load_fixture('test_fixture')
    
    def test_with_fixture_data(self):
        """Test using fixture data."""
        result = self.[instance].[method_name](self.test_data)
        assert result == expected_result
```

### Performance Monitoring

```python
from tests.integration.test_suite_framework import PerformanceMonitor

class Test[Module]Performance:
    """Performance tests with monitoring."""
    
    def test_performance_monitoring(self):
        """Test with performance monitoring."""
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # Perform operation
        self.[instance].[performance_critical_method]()
        
        metrics = monitor.stop_monitoring()
        
        # Assert performance metrics
        assert metrics['cpu_usage'] < 50  # Less than 50% CPU
        assert metrics['memory_usage'] < 100  # Less than 100MB
```

### Error Handling Tests

```python
class Test[Module]ErrorHandling:
    """Error handling tests."""
    
    def test_invalid_input(self):
        """Test handling of invalid input."""
        with pytest.raises(ValueError):
            self.[instance].[method_name](invalid_input)
    
    def test_graceful_degradation(self):
        """Test graceful degradation when dependencies fail."""
        # Mock dependency failure
        with patch('dependency.module.function', side_effect=Exception("Dependency failed")):
            result = self.[instance].[method_name]()
            assert result == fallback_value
    
    def test_logging_on_error(self):
        """Test that errors are properly logged."""
        with patch('modules.logging_module.logger.get_logger') as mock_logger:
            with pytest.raises(Exception):
                self.[instance].[method_name](invalid_input)
            
            # Verify error was logged
            mock_logger.assert_called_with('error')
```

## 🚀 Running Tests

### Individual Test Files

```bash
# Run a specific test file
python -m pytest modules/[your_module]/tests/test_[file].py -v

# Run with coverage
python -m pytest modules/[your_module]/tests/ --cov=modules.[your_module] -v

# Run with debugging
python -m pytest modules/[your_module]/tests/ -v -s --pdb
```

### Integration Tests

```bash
# Run integration tests
python -m pytest tests/integration/test_[your_module]_module_integration.py -v

# Run all integration tests
make test-modules
```

### Performance Tests

```bash
# Run performance tests only
make test-performance

# Run with performance profiling
make test-profile

# Run with memory profiling
make test-memory
```

## 📊 Test Coverage

### Coverage Requirements

- **Unit Tests**: >90% coverage for core functionality
- **Integration Tests**: >80% coverage for integration points
- **Error Handling**: 100% coverage for error paths
- **Performance Tests**: All critical paths tested

### Coverage Commands

```bash
# Generate coverage report
make test-coverage

# View coverage in browser
open htmlcov/index.html

# Generate coverage for your module only
python -m pytest modules/[your_module]/tests/ --cov=modules.[your_module] --cov-report=html --cov-report=term
```

## 🔍 Debugging Tests

### Common Debugging Commands

```bash
# Run with verbose output
python -m pytest modules/[your_module]/tests/ -v

# Run with print statements visible
python -m pytest modules/[your_module]/tests/ -v -s

# Run with debugger on failure
python -m pytest modules/[your_module]/tests/ -v --pdb

# Run specific test
python -m pytest modules/[your_module]/tests/test_[file].py::TestClass::test_method -v
```

### Debugging Tips

1. **Use `-s` flag**: Shows print statements and logging output
2. **Use `--pdb` flag**: Drops into debugger on test failure
3. **Use `-x` flag**: Stops on first failure
4. **Use `-k` flag**: Run only tests matching pattern
5. **Use `--tb=short`**: Shorter traceback output

## 📋 Test Checklist

### Before Submitting

- [ ] All tests pass: `make test-[your_module]`
- [ ] Coverage requirements met: `make test-coverage`
- [ ] Integration tests pass: `make test-modules`
- [ ] Performance tests pass: `make test-performance`
- [ ] Error handling tested
- [ ] Documentation updated
- [ ] Code follows style guidelines: `make lint`

### Test Quality Checklist

- [ ] Tests are independent and can run in any order
- [ ] Tests clean up after themselves
- [ ] Tests use descriptive names
- [ ] Tests have clear assertions
- [ ] Tests cover edge cases
- [ ] Tests handle errors gracefully
- [ ] Tests are fast (<1 second each)
- [ ] Tests don't have side effects

## 🛠️ Test Utilities

### Test Helpers

```python
# Common test utilities
from tests.integration.test_suite_framework import (
    TestDataManager,
    PerformanceMonitor,
    MockGameStateManager,
    create_test_fixture
)

# Mock utilities
from unittest.mock import patch, MagicMock, Mock

# Assertion utilities
import pytest
from pytest import raises, approx
```

### Creating Test Fixtures

```python
# Create a test fixture
fixture_data = {
    'test_case_1': {'input': 'value1', 'expected': 'result1'},
    'test_case_2': {'input': 'value2', 'expected': 'result2'}
}

TestDataManager().save_fixture('my_module_fixture', fixture_data)

# Load the fixture in tests
test_data = TestDataManager().load_fixture('my_module_fixture')
```

## 📞 Getting Help

### When Tests Fail

1. **Check the error message**: Look for specific failure details
2. **Run with verbose output**: `python -m pytest -v`
3. **Use debugger**: `python -m pytest --pdb`
4. **Check dependencies**: Ensure all required packages are installed
5. **Check test data**: Verify test fixtures are correct

### Common Issues

- **Import errors**: Check module paths and dependencies
- **State pollution**: Ensure tests clean up after themselves
- **Performance issues**: Check for memory leaks or slow operations
- **Flaky tests**: Ensure tests are deterministic

### Support Resources

- **Documentation**: Check module README for specific testing instructions
- **Integration Examples**: Review existing integration examples
- **Test Framework**: Check `tests/integration/test_suite_framework.py`
- **GitHub Issues**: Report test framework issues
- **Team Discussion**: Ask questions in GitHub Discussions

## 🎯 Best Practices

### Test Design

1. **Arrange-Act-Assert**: Structure tests clearly
2. **One assertion per test**: Keep tests focused
3. **Descriptive names**: Use clear, descriptive test names
4. **Test isolation**: Each test should be independent
5. **Fast execution**: Tests should run quickly

### Test Maintenance

1. **Keep tests updated**: Update tests when code changes
2. **Remove obsolete tests**: Delete tests for removed functionality
3. **Refactor common code**: Extract common test utilities
4. **Monitor test performance**: Keep tests fast
5. **Review test coverage**: Ensure adequate coverage

---

**Remember**: Good tests are an investment in code quality and maintainability. Take the time to write comprehensive, well-structured tests! 🧪✨
