# Consolidated Test Suite

This directory contains all BladeFighters tests organized in a clean, structured manner to reduce clutter while maintaining full functionality.

## Structure

```
tests/consolidated/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests between modules
├── performance/    # Performance and benchmark tests
├── modules/        # Tests for specific modules
├── core/           # Core functionality tests
├── root/           # General application tests
├── run_all_tests.py # Comprehensive test runner
└── pytest.ini     # Pytest configuration
```

## Quick Start

### Run All Tests
```bash
python tests/consolidated/run_all_tests.py
```

### Run Specific Category
```bash
python tests/consolidated/run_all_tests.py --category unit
python tests/consolidated/run_all_tests.py --category integration
python tests/consolidated/run_all_tests.py --category performance
python tests/consolidated/run_all_tests.py --category modules
python tests/consolidated/run_all_tests.py --category core
python tests/consolidated/run_all_tests.py --category root
```

### Run Specific Test
```bash
python tests/consolidated/run_all_tests.py --test tests/consolidated/unit/test_audio_module.py
```

### List All Tests
```bash
python tests/consolidated/run_all_tests.py --list
```

### Filter Tests by Pattern
```bash
python tests/consolidated/run_all_tests.py --pattern "audio"
```

### Verbose Output
```bash
python tests/consolidated/run_all_tests.py --verbose
```

## Using pytest Directly

You can also use pytest directly with the consolidated structure:

```bash
# Run all tests
pytest tests/consolidated/

# Run specific category
pytest tests/consolidated/unit/
pytest tests/consolidated/integration/

# Run with markers
pytest -m unit
pytest -m integration
pytest -m performance
```

## Migration Notes

All tests have been moved from their original scattered locations:
- Root-level test files → `tests/consolidated/root/`
- Module test files → `tests/consolidated/modules/`
- Core test files → `tests/consolidated/core/`
- Existing test categories → their respective directories

Import paths have been preserved to maintain functionality. The test runner automatically handles path resolution.

## Benefits

1. **Reduced Clutter**: All tests in one organized location
2. **Easy Discovery**: Clear categorization of test types
3. **Unified Interface**: Single test runner for all tests
4. **Maintained Functionality**: All original test capabilities preserved
5. **Better Organization**: Logical grouping by test type and scope

## Test Categories

- **Unit**: Tests for individual functions and classes
- **Integration**: Tests for interactions between modules
- **Performance**: Benchmark and performance validation tests
- **Modules**: Tests specific to individual modules
- **Core**: Tests for core game functionality
- **Root**: General application and system tests

## Troubleshooting

If you encounter import errors, ensure that:
1. You're running tests from the project root directory
2. The Python path includes the project root
3. All dependencies are installed

The test runner automatically handles path setup, but manual pytest runs may require setting PYTHONPATH:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest tests/consolidated/
```
