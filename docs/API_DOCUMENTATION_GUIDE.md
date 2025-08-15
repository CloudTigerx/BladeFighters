# API Documentation Guide

## Overview

This guide provides comprehensive standards and templates for documenting public APIs across all BladeFighters modules. It ensures consistent, clear, and complete API documentation that enables developers to effectively use and integrate modules.

## 🎯 Documentation Standards

### 1. Module-Level Documentation

Every module should have a comprehensive README.md that includes:

- **Overview** - Clear description of the module's purpose
- **Key Features** - Bullet points of main capabilities
- **Module Structure** - File organization and purpose
- **Quick Start** - Basic usage examples
- **API Reference** - Complete method documentation
- **Integration Examples** - Real-world usage patterns
- **Testing** - How to test the module
- **Related Documentation** - Links to related guides

### 2. Class Documentation

Each public class should be documented with:

```python
class ExampleClass:
    """
    Brief description of the class purpose.
    
    Longer description explaining when and how to use this class,
    including any important design decisions or constraints.
    
    Attributes:
        attribute_name (type): Description of the attribute
        
    Example:
        >>> example = ExampleClass()
        >>> result = example.do_something()
    """
```

### 3. Method Documentation

Each public method should follow this format:

```python
def method_name(self, param1: type, param2: type = default) -> return_type:
    """
    Brief description of what the method does.
    
    Longer description explaining the method's behavior, side effects,
    and important implementation details.
    
    Args:
        param1 (type): Description of the first parameter
        param2 (type, optional): Description of the second parameter. 
            Defaults to default_value.
            
    Returns:
        return_type: Description of what is returned
        
    Raises:
        ExceptionType: Description of when this exception is raised
        
    Example:
        >>> obj = ExampleClass()
        >>> result = obj.method_name("value1", "value2")
        >>> print(result)
        expected_output
    """
```

## 📋 API Documentation Templates

### 1. Core Module Template

```markdown
# Module Name

## Overview

Brief description of the module's purpose and main functionality.

## 🎯 Key Features

- **Feature 1** - Description of the first key feature
- **Feature 2** - Description of the second key feature
- **Feature 3** - Description of the third key feature

## 📁 Module Structure

```
module_name/
├── __init__.py                    # Module initialization and exports
├── README.md                      # This documentation file
├── main_class.py                  # Primary class implementation
├── utility_class.py               # Utility class implementation
├── integration_example.py         # Working integration example
└── tests/
    └── test_main_class.py         # Test suite
```

## 🚀 Quick Start

### Basic Usage

```python
from module_name.main_class import MainClass

# Initialize the module
instance = MainClass()

# Basic operation
result = instance.do_something()
```

### Advanced Usage

```python
from module_name.main_class import MainClass
from module_name.utility_class import UtilityClass

# Initialize with configuration
config = {"setting1": "value1", "setting2": "value2"}
instance = MainClass(config)

# Use utility functions
utility = UtilityClass()
helper_result = utility.helper_function()
```

## 📋 API Reference

### MainClass

The primary class for module functionality.

#### Constructor

```python
MainClass(config: dict = None, state_manager=None)
```

**Parameters:**
- `config` (dict, optional): Configuration dictionary
- `state_manager` (StateManager, optional): State manager for integration

**Returns:**
- `MainClass`: Initialized instance

#### Methods

##### `do_something(param1: str, param2: int = 0) -> bool`

Perform the main operation of the class.

**Parameters:**
- `param1` (str): Description of the first parameter
- `param2` (int, optional): Description of the second parameter. Defaults to 0.

**Returns:**
- `bool`: True if operation succeeded, False otherwise

**Raises:**
- `ValueError`: If param1 is empty or invalid
- `RuntimeError`: If the operation cannot be completed

**Example:**
```python
instance = MainClass()
result = instance.do_something("test_value", 42)
if result:
    print("Operation succeeded")
```

##### `get_status() -> dict`

Get the current status of the module.

**Returns:**
- `dict`: Status information including current state and statistics

**Example:**
```python
status = instance.get_status()
print(f"Current state: {status['state']}")
print(f"Operations completed: {status['operations']}")
```

### UtilityClass

Utility functions for common operations.

#### Constructor

```python
UtilityClass()
```

**Returns:**
- `UtilityClass`: Initialized utility instance

#### Methods

##### `helper_function(input_data: list) -> list`

Process input data and return processed results.

**Parameters:**
- `input_data` (list): List of items to process

**Returns:**
- `list`: Processed items

**Example:**
```python
utility = UtilityClass()
data = [1, 2, 3, 4, 5]
processed = utility.helper_function(data)
print(processed)  # [2, 4, 6, 8, 10]
```

## 🔧 Integration Examples

### Basic Integration

```python
from module_name.main_class import MainClass
from other_module.other_class import OtherClass

class IntegrationExample:
    def __init__(self):
        self.main_instance = MainClass()
        self.other_instance = OtherClass()
    
    def process_data(self, data):
        # Use main module
        result = self.main_instance.do_something(data)
        
        # Use other module with result
        if result:
            self.other_instance.process_result(result)
```

### Advanced Integration with State Management

```python
from module_name.main_class import MainClass
from modules.game_state_module.game_state_manager import GameStateManager

class StateIntegrationExample:
    def __init__(self):
        self.state_manager = GameStateManager()
        self.main_instance = MainClass(state_manager=self.state_manager)
    
    def handle_state_change(self, key, old_value, new_value):
        if key == "module.setting":
            # React to state changes
            self.main_instance.update_setting(new_value)
```

## 🧪 Testing

The module includes comprehensive tests:

```bash
# Run module tests
python -m pytest module_name/tests/ -v

# Run specific test
python -m pytest module_name/tests/test_main_class.py::test_do_something -v
```

### Test Coverage

The test suite covers:
- Basic functionality
- Error handling
- Edge cases
- Integration scenarios
- Performance benchmarks

## 📝 Notes

- Important implementation details
- Performance considerations
- Known limitations
- Future improvements

## 🔗 Related Documentation

- **[Module Integration Guide](MODULE_INTEGRATION_GUIDE.md)** - How to integrate with other modules
- **[State Management Guide](STATE_MANAGEMENT.md)** - State management patterns
- **[Testing Guide](TESTING.md)** - Testing strategies

*This module is part of the BladeFighters project. For project-wide documentation, see the [Documentation Index](README.md).*
```

### 2. Method Documentation Template

```python
def method_name(self, param1: type, param2: type = default) -> return_type:
    """
    Brief description of the method's purpose and behavior.
    
    Detailed description explaining:
    - What the method does
    - How it processes the parameters
    - What side effects it may have
    - Important implementation details
    - Performance characteristics
    
    Args:
        param1 (type): Description of the first parameter, including:
            - What it represents
            - Valid values or constraints
            - Default behavior if not provided
        param2 (type, optional): Description of the second parameter.
            Defaults to default_value. Include:
            - When to use this parameter
            - What happens if not provided
            - Valid value ranges
            
    Returns:
        return_type: Description of the return value, including:
            - What the value represents
            - Possible values or ranges
            - When None or empty values are returned
            
    Raises:
        ValueError: Description of when this exception is raised
        RuntimeError: Description of runtime error conditions
        CustomException: Description of custom exception scenarios
        
    Example:
        Basic usage:
        >>> obj = ExampleClass()
        >>> result = obj.method_name("test", 42)
        >>> print(result)
        expected_output
        
        Advanced usage with error handling:
        >>> try:
        ...     result = obj.method_name("", -1)
        ... except ValueError as e:
        ...     print(f"Invalid input: {e}")
        Invalid input: param1 cannot be empty
        
    Note:
        Important implementation notes, performance considerations,
        or usage warnings.
    """
```

### 3. Class Documentation Template

```python
class ExampleClass:
    """
    Brief description of the class and its primary purpose.
    
    Detailed description explaining:
    - What problems this class solves
    - When to use this class vs alternatives
    - Key design decisions and trade-offs
    - Thread safety and concurrency considerations
    - Memory management and resource handling
    
    The class provides functionality for:
    - Feature 1: Description
    - Feature 2: Description
    - Feature 3: Description
    
    Attributes:
        public_attr (type): Description of public attribute
        _private_attr (type): Description of private attribute (if documented)
        
    Example:
        Basic usage:
        >>> obj = ExampleClass()
        >>> obj.do_something()
        
        Advanced usage with configuration:
        >>> config = {"setting": "value"}
        >>> obj = ExampleClass(config)
        >>> result = obj.process_data([1, 2, 3])
        
    Note:
        Important usage notes, limitations, or warnings.
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize the ExampleClass instance.
        
        Args:
            config (dict, optional): Configuration dictionary. 
                If None, default configuration is used.
                
        Raises:
            ValueError: If config contains invalid settings
        """
```

## 🔧 Documentation Tools

### 1. Docstring Format

Use Google-style docstrings for consistency:

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """Brief description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 0.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: Description of when raised.
    """
```

### 2. Type Hints

Always include type hints for better IDE support:

```python
from typing import List, Dict, Optional, Union

def process_data(
    items: List[str], 
    config: Optional[Dict[str, Union[str, int]]] = None
) -> Dict[str, int]:
    """Process a list of items with optional configuration."""
```

### 3. Examples

Include practical examples in docstrings:

```python
def calculate_score(answers: List[bool], weights: List[float]) -> float:
    """Calculate weighted score from answers.
    
    Args:
        answers: List of boolean answers.
        weights: List of weights for each answer.
        
    Returns:
        Weighted score as float.
        
    Example:
        >>> calculate_score([True, False, True], [1.0, 2.0, 1.5])
        2.5
    """
```

## 📝 Documentation Checklist

### For Each Module

- [ ] **README.md** exists and is comprehensive
- [ ] **Overview** clearly explains module purpose
- [ ] **Key Features** lists main capabilities
- [ ] **Module Structure** shows file organization
- [ ] **Quick Start** provides basic usage examples
- [ ] **API Reference** documents all public methods
- [ ] **Integration Examples** show real-world usage
- [ ] **Testing** section explains how to test
- [ ] **Related Documentation** links to other guides

### For Each Public Class

- [ ] **Class docstring** explains purpose and usage
- [ ] **Attributes** are documented
- [ ] **Constructor** parameters are documented
- [ ] **All public methods** have complete docstrings
- [ ] **Examples** show typical usage patterns
- [ ] **Error conditions** are documented

### For Each Public Method

- [ ] **Brief description** explains what it does
- [ ] **Detailed description** covers behavior and side effects
- [ ] **Parameters** are documented with types and descriptions
- [ ] **Return value** is documented with type and description
- [ ] **Exceptions** are documented with conditions
- [ ] **Examples** show typical usage
- [ ] **Type hints** are included

## 🔗 Related Documentation

- **[Module Documentation Index](README.md)** - Complete module documentation
- **[Module Integration Guide](MODULE_INTEGRATION_GUIDE.md)** - Integration patterns
- **[Testing Guide](TESTING.md)** - Testing strategies
- **[Code Style Guide](CODE_STYLE.md)** - Coding standards

*This guide is part of the BladeFighters project. For project-wide documentation, see the [Documentation Index](README.md).*
