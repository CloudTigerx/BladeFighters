# Test Template for Module Developers

## Overview

This template provides a standardized structure for module tests. Use this as a starting point and customize it for your specific module needs.

## 📁 File Structure

Create the following test files in your module:

```
modules/[your_module]/
├── tests/
│   ├── __init__.py
│   ├── test_[main_file].py          # Main functionality tests
│   ├── test_integration.py          # Integration tests
│   ├── test_performance.py          # Performance tests
│   └── test_error_handling.py       # Error handling tests
```

## 🧪 Test File Templates

### 1. Main Functionality Tests (`test_[main_file].py`)

```python
"""
Tests for [Module Name] main functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from modules.[your_module].[main_file] import [MainClass]


class Test[MainClass]:
    """Test cases for [MainClass]."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.[instance] = [MainClass]()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, '[instance]'):
            del self.[instance]
    
    def test_initialization(self):
        """Test that the class initializes correctly."""
        assert self.[instance] is not None
        # Add specific initialization assertions
        assert hasattr(self.[instance], 'expected_attribute')
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        input_data = "test_input"
        expected_result = "expected_output"
        
        # Act
        result = self.[instance].[method_name](input_data)
        
        # Assert
        assert result == expected_result
    
    def test_method_with_parameters(self):
        """Test method with multiple parameters."""
        # Arrange
        param1 = "value1"
        param2 = "value2"
        expected_result = "expected_output"
        
        # Act
        result = self.[instance].[method_name](param1, param2)
        
        # Assert
        assert result == expected_result
    
    def test_method_returns_correct_type(self):
        """Test that method returns correct data type."""
        result = self.[instance].[method_name]()
        assert isinstance(result, expected_type)
    
    def test_method_with_default_parameters(self):
        """Test method with default parameters."""
        # Test with default parameters
        result1 = self.[instance].[method_name]()
        assert result1 == expected_default_result
        
        # Test with custom parameters
        result2 = self.[instance].[method_name](custom_param="value")
        assert result2 == expected_custom_result
    
    @pytest.mark.parametrize("input_value,expected_output", [
        ("test1", "result1"),
        ("test2", "result2"),
        ("test3", "result3"),
    ])
    def test_method_with_multiple_inputs(self, input_value, expected_output):
        """Test method with multiple input values."""
        result = self.[instance].[method_name](input_value)
        assert result == expected_output
```

### 2. Integration Tests (`test_integration.py`)

```python
"""
Integration tests for [Module Name] with GameStateManager.
"""

import pytest
from unittest.mock import patch, MagicMock
from modules.[your_module].[main_file] import [MainClass]
from modules.game_state_module.game_state_manager import GameStateManager


class Test[Module]Integration:
    """Integration tests for [Module] with GameStateManager."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.state_manager = GameStateManager()
        self.[module_instance] = [MainClass](self.state_manager)
    
    def teardown_method(self):
        """Clean up integration test fixtures."""
        if hasattr(self, '[module_instance]'):
            del self.[module_instance]
        if hasattr(self, 'state_manager'):
            del self.state_manager
    
    def test_state_manager_integration(self):
        """Test integration with GameStateManager."""
        # Arrange
        test_value = "test_value"
        field_path = "[your_module].[field]"
        
        # Act
        result = self.[module_instance].[integration_method](test_value)
        
        # Assert
        assert result is True
        
        # Verify state was updated
        state_value = self.state_manager.get(field_path)
        assert state_value == test_value
    
    def test_state_validation_integration(self):
        """Test that state validation works correctly."""
        # Arrange
        invalid_value = "invalid_value"
        
        # Act & Assert
        with pytest.raises(ValueError):
            self.[module_instance].[integration_method](invalid_value)
        
        # Verify state was not updated
        state_value = self.state_manager.get("[your_module].[field]")
        assert state_value != invalid_value
    
    def test_callback_integration(self):
        """Test callback integration."""
        # Arrange
        callback_called = False
        callback_data = None
        
        def test_callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data
        
        self.[module_instance].register_callback(test_callback)
        
        # Act
        test_value = "test_value"
        self.[module_instance].[trigger_method](test_value)
        
        # Assert
        assert callback_called is True
        assert callback_data == test_value
    
    def test_error_handling_integration(self):
        """Test error handling in integration."""
        # Arrange
        with patch.object(self.state_manager, 'set', side_effect=Exception("State error")):
            # Act & Assert
            with pytest.raises(Exception):
                self.[module_instance].[integration_method]("test_value")
    
    def test_state_history_integration(self):
        """Test that state changes are recorded in history."""
        # Arrange
        initial_changes = len(self.state_manager.history.changes)
        test_value = "test_value"
        
        # Act
        self.[module_instance].[integration_method](test_value)
        
        # Assert
        final_changes = len(self.state_manager.history.changes)
        assert final_changes > initial_changes
        
        # Verify the change was recorded
        recent_changes = self.state_manager.history.get_changes_for_field("[your_module].[field]")
        assert len(recent_changes) > 0
        assert recent_changes[-1].new_value == test_value
```

### 3. Performance Tests (`test_performance.py`)

```python
"""
Performance tests for [Module Name].
"""

import time
import pytest
from modules.[your_module].[main_file] import [MainClass]


class Test[Module]Performance:
    """Performance tests for [Module]."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        self.[instance] = [MainClass]()
    
    def teardown_method(self):
        """Clean up performance test fixtures."""
        if hasattr(self, '[instance]'):
            del self.[instance]
    
    def test_operation_performance(self):
        """Test that operations complete within acceptable time."""
        # Arrange
        max_duration_ms = 100  # Maximum acceptable duration in milliseconds
        
        # Act
        start_time = time.time()
        result = self.[instance].[performance_critical_method]()
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        
        # Assert
        assert duration_ms < max_duration_ms, f"Operation took {duration_ms:.2f}ms, expected < {max_duration_ms}ms"
        assert result == expected_result
    
    def test_memory_usage(self):
        """Test memory usage is within acceptable limits."""
        try:
            import psutil
            import os
            
            # Arrange
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            max_memory_increase_mb = 10  # Maximum acceptable memory increase in MB
            
            # Act
            self.[instance].[memory_intensive_method]()
            
            # Measure memory after operation
            final_memory = process.memory_info().rss
            memory_increase_bytes = final_memory - initial_memory
            memory_increase_mb = memory_increase_bytes / (1024 * 1024)
            
            # Assert
            assert memory_increase_mb < max_memory_increase_mb, \
                f"Memory increased by {memory_increase_mb:.2f}MB, expected < {max_memory_increase_mb}MB"
                
        except ImportError:
            pytest.skip("psutil not available for memory testing")
    
    def test_concurrent_operations(self):
        """Test performance under concurrent operations."""
        import threading
        import queue
        
        # Arrange
        num_threads = 10
        num_operations = 100
        results_queue = queue.Queue()
        errors_queue = queue.Queue()
        
        def worker():
            try:
                for _ in range(num_operations):
                    result = self.[instance].[thread_safe_method]()
                    results_queue.put(result)
            except Exception as e:
                errors_queue.put(e)
        
        # Act
        start_time = time.time()
        
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Assert
        assert errors_queue.empty(), f"Errors occurred: {[errors_queue.get() for _ in range(errors_queue.qsize())]}"
        assert results_queue.qsize() == num_threads * num_operations
        assert duration_ms < 5000  # Should complete within 5 seconds
    
    def test_large_data_performance(self):
        """Test performance with large data sets."""
        # Arrange
        large_data = ["item" + str(i) for i in range(10000)]
        max_duration_ms = 1000  # 1 second for large data
        
        # Act
        start_time = time.time()
        result = self.[instance].[large_data_method](large_data)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        
        # Assert
        assert duration_ms < max_duration_ms, f"Large data operation took {duration_ms:.2f}ms, expected < {max_duration_ms}ms"
        assert result == expected_result
```

### 4. Error Handling Tests (`test_error_handling.py`)

```python
"""
Error handling tests for [Module Name].
"""

import pytest
from unittest.mock import patch, MagicMock
from modules.[your_module].[main_file] import [MainClass]


class Test[Module]ErrorHandling:
    """Error handling tests for [Module]."""
    
    def setup_method(self):
        """Set up error handling test fixtures."""
        self.[instance] = [MainClass]()
    
    def teardown_method(self):
        """Clean up error handling test fixtures."""
        if hasattr(self, '[instance]'):
            del self.[instance]
    
    def test_invalid_input_handling(self):
        """Test handling of invalid input."""
        # Arrange
        invalid_inputs = [
            None,
            "",
            -1,
            999999,
            "invalid_string",
            [],
            {},
        ]
        
        # Act & Assert
        for invalid_input in invalid_inputs:
            with pytest.raises((ValueError, TypeError, AttributeError)):
                self.[instance].[method_name](invalid_input)
    
    def test_missing_dependencies(self):
        """Test graceful handling of missing dependencies."""
        # Arrange
        with patch('dependency.module.function', side_effect=ImportError("Module not found")):
            # Act
            result = self.[instance].[method_name]()
            
            # Assert
            assert result == fallback_value
    
    def test_network_errors(self):
        """Test handling of network-related errors."""
        # Arrange
        with patch('requests.get', side_effect=Exception("Network error")):
            # Act & Assert
            with pytest.raises(Exception):
                self.[instance].[network_method]()
    
    def test_file_io_errors(self):
        """Test handling of file I/O errors."""
        # Arrange
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            # Act & Assert
            with pytest.raises(FileNotFoundError):
                self.[instance].[file_method]("nonexistent_file.txt")
    
    def test_logging_on_error(self):
        """Test that errors are properly logged."""
        # Arrange
        with patch('modules.logging_module.logger.get_logger') as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.return_value = mock_logger_instance
            
            # Act
            with pytest.raises(Exception):
                self.[instance].[method_name](invalid_input)
            
            # Assert
            mock_logger_instance.error.assert_called()
    
    def test_graceful_degradation(self):
        """Test graceful degradation when features are unavailable."""
        # Arrange
        with patch.object(self.[instance], 'advanced_feature', side_effect=Exception("Feature unavailable")):
            # Act
            result = self.[instance].[method_name]()
            
            # Assert
            assert result == basic_result  # Should fall back to basic functionality
    
    def test_resource_cleanup_on_error(self):
        """Test that resources are cleaned up even when errors occur."""
        # Arrange
        cleanup_called = False
        
        def cleanup():
            nonlocal cleanup_called
            cleanup_called = True
        
        self.[instance].register_cleanup(cleanup)
        
        # Act
        with pytest.raises(Exception):
            self.[instance].[method_name](invalid_input)
        
        # Assert
        assert cleanup_called is True
    
    def test_error_recovery(self):
        """Test that the system can recover from errors."""
        # Arrange
        call_count = 0
        
        def failing_method():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary error")
            return "success"
        
        with patch.object(self.[instance], 'method_name', side_effect=failing_method):
            # Act
            result = self.[instance].[recovery_method]()
            
            # Assert
            assert result == "success"
            assert call_count == 2  # Should have retried once
```

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)

Add this to your module's test directory:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    performance: marks tests as performance tests
    error_handling: marks tests as error handling tests
```

### Test Dependencies

Add these to your module's requirements or test requirements:

```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-parametrize>=0.0.1
psutil>=5.9.0  # For performance testing
```

## 📊 Test Coverage Configuration

### Coverage Configuration (`.coveragerc`)

```ini
[run]
source = modules/[your_module]
omit = 
    */tests/*
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

## 🚀 Running Your Tests

### Basic Commands

```bash
# Run all tests for your module
python -m pytest modules/[your_module]/tests/ -v

# Run specific test file
python -m pytest modules/[your_module]/tests/test_[file].py -v

# Run with coverage
python -m pytest modules/[your_module]/tests/ --cov=modules.[your_module] -v

# Run specific test class
python -m pytest modules/[your_module]/tests/test_[file].py::TestClass -v

# Run specific test method
python -m pytest modules/[your_module]/tests/test_[file].py::TestClass::test_method -v
```

### Using Makefile Commands

```bash
# Add your module to the Makefile
# Edit Makefile and add:
test-[your_module]:
	python -m pytest modules/[your_module]/tests/ -v

# Then run:
make test-[your_module]
```

## 📋 Customization Checklist

- [ ] Replace `[your_module]` with your actual module name
- [ ] Replace `[MainClass]` with your actual class name
- [ ] Replace `[method_name]` with your actual method names
- [ ] Replace `[instance]` with appropriate variable name
- [ ] Add specific test cases for your module's functionality
- [ ] Update expected values and assertions
- [ ] Add module-specific error handling tests
- [ ] Configure performance thresholds for your module
- [ ] Add integration tests with GameStateManager
- [ ] Update coverage configuration for your module

---

**Remember**: This template is a starting point. Customize it to match your module's specific needs and requirements! 🧪✨
