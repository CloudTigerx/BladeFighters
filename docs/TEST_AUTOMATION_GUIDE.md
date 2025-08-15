# Test Automation Guide for Module Developers

## Overview

This guide explains how to use the comprehensive test automation framework for BladeFighters modules. The framework provides integration testing, performance benchmarking, regression testing, and automated reporting capabilities.

## 🎯 Quick Start

### Running Tests

```bash
# Run all tests
make test-all

# Run specific module tests
make test-audio
make test-screen
make test-input

# Run performance tests only
make test-performance

# Run regression tests only
make test-regression

# Run module integration tests only
make test-modules
```

### Development Workflow

```bash
# Quick test during development
make test-quick

# Watch mode for continuous testing
make test-watch

# Run with coverage
make test-coverage

# Debug tests
make debug-test
```

## 📋 Test Automation Framework

### Architecture

The test automation framework consists of several components:

```
tests/
├── integration/                    # Integration test suites
│   ├── test_suite_framework.py    # Core test framework
│   ├── test_audio_module_integration.py
│   ├── test_screen_module_integration.py
│   └── test_input_module_integration.py
├── run_comprehensive_tests.py     # Main test runner
├── fixtures/                      # Test data and fixtures
└── reactor_blackbox/             # Blackbox testing
```

### Core Components

1. **BladeFightersTestSuite** - Base class for all module tests
2. **TestAutomationRunner** - Orchestrates test execution
3. **PerformanceMonitor** - Tracks performance metrics
4. **TestDataManager** - Manages test data and fixtures
5. **ComprehensiveTestRunner** - Runs all test suites

## 🧪 Writing Module Tests

### Basic Test Structure

```python
from tests.integration.test_suite_framework import BladeFightersTestSuite

class YourModuleTests(BladeFightersTestSuite):
    """Integration tests for your module."""
    
    def setUp(self):
        super().setUp()
        try:
            from modules.your_module.your_system import YourSystem
            self.YourSystem = YourSystem
        except ImportError as e:
            self.skipTest(f"Your module not available: {e}")
    
    def test_basic_functionality(self):
        """Test basic module functionality."""
        # Your test code here
        pass
    
    def test_integration_with_state_manager(self):
        """Test integration with game state manager."""
        # Test state management integration
        pass
    
    def test_performance_under_load(self):
        """Test performance under heavy load."""
        # Performance testing
        pass
```

### State Management Integration Tests

For modules that integrate with the unified state management system:

```python
def test_state_manager_integration(self):
    """Test integration with GameStateManager."""
    # Initialize your module with state manager
    your_module = self.YourSystem(state_manager=self.state_manager)
    
    # Test state changes
    self.state_manager.set("your_module.some_field", "new_value", source="test")
    
    # Verify your module reflects the change
    self.assertEqual(your_module.get_some_field(), "new_value")

def test_state_change_tracking(self):
    """Test that state changes are properly tracked."""
    your_module = self.YourSystem(state_manager=self.state_manager)
    
    # Make state changes
    your_module.set_some_field("test_value")
    
    # Check that changes were tracked
    changes = self.state_manager.history.get_changes_for_field("your_module.some_field")
    self.assertGreater(len(changes), 0)
```

### Performance Testing

```python
def test_performance_benchmarking(self):
    """Benchmark module performance."""
    your_module = self.YourSystem()
    
    # Benchmark operations
    start_time = time.time()
    for i in range(1000):
        your_module.some_operation()
    
    duration = time.time() - start_time
    operations_per_second = 1000 / duration
    
    # Assert performance requirements
    self.assertGreater(operations_per_second, 100, 
                      f"Performance: {operations_per_second:.1f} ops/sec")

def test_memory_usage(self):
    """Test memory usage."""
    initial_memory = self.performance_monitor._get_memory_usage()
    
    # Create multiple instances
    instances = []
    for i in range(10):
        instance = self.YourSystem()
        instances.append(instance)
    
    final_memory = self.performance_monitor._get_memory_usage()
    memory_increase = final_memory - initial_memory
    
    # Assert reasonable memory usage
    self.assertLess(memory_increase, 50.0, 
                   f"Memory usage: {memory_increase:.1f}MB")
```

### Error Handling Tests

```python
def test_error_handling(self):
    """Test error handling and recovery."""
    your_module = self.YourSystem()
    
    # Test invalid inputs
    try:
        your_module.some_method("invalid_input")
    except Exception as e:
        # Verify appropriate error handling
        self.assertIsInstance(e, ExpectedExceptionType)
    
    # Test recovery from errors
    result = your_module.some_method("valid_input")
    self.assertIsNotNone(result)
```

## 🔧 Test Patterns and Best Practices

### 1. Use the Base Test Suite

Always inherit from `BladeFightersTestSuite`:

```python
class YourModuleTests(BladeFightersTestSuite):
    def setUp(self):
        super().setUp()  # Important: call parent setUp
        # Your setup code
```

### 2. Handle Import Errors Gracefully

```python
def setUp(self):
    super().setUp()
    try:
        from modules.your_module.your_system import YourSystem
        self.YourSystem = YourSystem
    except ImportError as e:
        self.skipTest(f"Your module not available: {e}")
```

### 3. Test State Management Integration

For modules with state management:

```python
def test_state_integration(self):
    """Test state management integration."""
    your_module = self.YourSystem(state_manager=self.state_manager)
    
    # Test state synchronization
    self.state_manager.set("your_module.field", "value", source="test")
    self.assertEqual(your_module.get_field(), "value")
    
    # Test state validation
    success = your_module.set_field("new_value")
    self.assertTrue(success)
    self.assertEqual(self.state_manager.get("your_module.field"), "new_value")
```

### 4. Test Performance Characteristics

```python
def test_performance(self):
    """Test performance characteristics."""
    your_module = self.YourSystem()
    
    # Test operation speed
    start_time = time.time()
    for i in range(100):
        your_module.fast_operation()
    duration = time.time() - start_time
    
    # Assert performance requirements
    self.assertLess(duration, 1.0, f"Operation took {duration:.3f}s")
```

### 5. Test Memory Usage

```python
def test_memory_usage(self):
    """Test memory usage patterns."""
    initial_memory = self.performance_monitor._get_memory_usage()
    
    # Create and destroy instances
    for i in range(10):
        instance = self.YourSystem()
        del instance
    
    final_memory = self.performance_monitor._get_memory_usage()
    memory_increase = final_memory - initial_memory
    
    # Assert reasonable memory usage
    self.assertLess(memory_increase, 10.0, 
                   f"Memory leak: {memory_increase:.1f}MB")
```

## 📊 Test Categories

### 1. Integration Tests

Test how your module integrates with other components:

```python
def test_integration_with_other_modules(self):
    """Test integration with other modules."""
    # Test interaction with other modules
    pass
```

### 2. Performance Tests

Test performance under various conditions:

```python
def test_performance_under_load(self):
    """Test performance under heavy load."""
    # Test with high load
    pass

def test_performance_scaling(self):
    """Test performance scaling."""
    # Test with different data sizes
    pass
```

### 3. Regression Tests

Test that existing functionality still works:

```python
def test_regression_functionality(self):
    """Test that existing functionality still works."""
    # Test existing features
    pass
```

### 4. State Management Tests

Test state management integration:

```python
def test_state_management(self):
    """Test state management integration."""
    # Test state synchronization
    # Test state validation
    # Test state history
    pass
```

## 🚀 Advanced Testing Features

### 1. Test Data Management

```python
def test_with_fixtures(self):
    """Test using fixtures."""
    # Load test data
    test_data = self.test_data_manager.load_fixture("your_module_test_data")
    
    # Use test data
    your_module = self.YourSystem(test_data)
    result = your_module.process_data()
    
    # Verify results
    self.assertEqual(result, test_data["expected_result"])
```

### 2. Performance Monitoring

```python
def test_with_performance_monitoring(self):
    """Test with performance monitoring."""
    self.performance_monitor.start_monitoring()
    
    # Your test operations
    your_module = self.YourSystem()
    your_module.expensive_operation()
    
    metrics = self.performance_monitor.stop_monitoring()
    
    # Assert performance metrics
    self.assertLess(metrics['duration'], 1.0)
    self.assertLess(metrics['memory_delta'], 10.0)
```

### 3. Custom Test Suites

```python
class YourModulePerformanceTests(BladeFightersTestSuite):
    """Performance-specific tests for your module."""
    
    def test_load_testing(self):
        """Test under high load."""
        # Load testing implementation
        pass
    
    def test_stress_testing(self):
        """Test under stress conditions."""
        # Stress testing implementation
        pass
```

## 📈 Test Reporting

### Running Tests with Reports

```bash
# Generate HTML coverage report
make test-coverage

# Run with detailed reporting
python -m pytest tests/integration/test_your_module_integration.py -v --tb=long

# Run with performance profiling
make test-profile
```

### Understanding Test Results

The test automation framework provides:

1. **Test Results Summary** - Overall pass/fail statistics
2. **Performance Metrics** - Operation speed and memory usage
3. **Coverage Reports** - Code coverage information
4. **Detailed Logs** - Comprehensive test execution logs

### Test Result Files

After running tests, check these files:

- `test_results/comprehensive_test_report.txt` - Detailed test report
- `test_results/comprehensive_test_results.json` - Machine-readable results
- `htmlcov/` - HTML coverage reports
- `.coverage` - Coverage data file

## 🔧 Configuration

### Test Configuration

Configure test behavior in `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### Environment Variables

Set environment variables for testing:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export TEST_ENVIRONMENT=development
export TEST_VERBOSITY=verbose
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Test Failures**
   ```bash
   # Run with debug information
   make debug-test
   
   # Run specific test with more detail
   python -m pytest tests/integration/test_your_module_integration.py::TestClass::test_method -v -s
   ```

3. **Performance Test Failures**
   ```bash
   # Check system resources
   make perf-monitor
   
   # Run with reduced load
   python -m pytest tests/integration/test_your_module_integration.py -k "not performance"
   ```

### Debugging Tests

```bash
# Run with debugger
make debug-test

# Run specific module tests with debugger
make debug-module MODULE=your_module

# Run with print statements
python -m pytest tests/integration/test_your_module_integration.py -v -s
```

## 📋 Test Checklist

Before submitting your module tests:

- [ ] All tests inherit from `BladeFightersTestSuite`
- [ ] Tests handle import errors gracefully
- [ ] State management integration is tested (if applicable)
- [ ] Performance characteristics are tested
- [ ] Error handling is tested
- [ ] Memory usage is tested
- [ ] Tests run successfully with `make test-your-module`
- [ ] Tests are included in comprehensive test suite
- [ ] Documentation is updated with test examples

## 🎯 Example: Audio Module Tests

See `tests/integration/test_audio_module_integration.py` for a complete example of:

- Basic functionality testing
- State management integration
- Performance benchmarking
- Error handling
- Memory usage testing
- Settings integration
- Callback system testing

## 📞 Getting Help

For test automation questions:

1. **Check this guide** - Review this documentation
2. **Review examples** - Look at existing module tests
3. **Run test examples** - Use the provided test commands
4. **Create an issue** - Report test automation problems

---

**Test Automation Guide**  
**Version**: 1.0.0  
**Last Updated**: 2024-01-XX  
**Maintainer**: Test Automation Team
