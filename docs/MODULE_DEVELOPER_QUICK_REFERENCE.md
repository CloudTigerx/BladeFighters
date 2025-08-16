# Module Developer Quick Reference

## 🎯 Overview

This quick reference guide helps module developers understand the testing framework, documentation system, and development workflow.

## 📋 What Each Developer Should Do

### Developer 1 (Screen Module) ✅ COMPLETED
- **Status**: ✅ Completed - Ready for handoff
- **Focus**: Integration patterns with other modules
- **Needs**: Keep README.md updated with new features

### Developer 2 (Audio Module)
- **Status**: Integration guide available
- **Needs**: Complete module README.md using template
- **Focus**: API documentation and usage examples

### Developer 3 (Game State Module)
- **Status**: Migration guide available
- **Needs**: Create comprehensive README.md
- **Focus**: State management patterns and integration

### Developer 4 (Settings Module)
- **Status**: Migration guide available
- **Needs**: Create comprehensive README.md
- **Focus**: Configuration patterns and validation

## 🚀 Getting Started

### 1. Set Up Documentation

```bash
# Create your developer log
touch docs/developer_logs/[YOUR_NAME]_log.md

# Create technical notes
touch docs/technical_notes/[YOUR_MODULE]_notes.md

# Update your module README
# Use docs/MODULE_TEMPLATE.md as template
```

### 2. Set Up Testing

```bash
# Create test directory
mkdir -p modules/[your_module]/tests/

# Create test files using docs/TEST_TEMPLATE.md
touch modules/[your_module]/tests/__init__.py
touch modules/[your_module]/tests/test_[main_file].py
touch modules/[your_module]/tests/test_integration.py
touch modules/[your_module]/tests/test_performance.py
touch modules/[your_module]/tests/test_error_handling.py
```

### 3. Add to Makefile

Add your module to the Makefile:

```makefile
test-[your_module]:
	python -m pytest modules/[your_module]/tests/ -v
```

## 🧪 Testing Commands

### Basic Testing

```bash
# Run all tests
make test-all

# Run your module's tests
make test-[your_module]

# Run with coverage
make test-coverage

# Run with debugging
make debug-module MODULE=[your_module]
```

### Specific Test Commands

```bash
# Run specific test file
python -m pytest modules/[your_module]/tests/test_[file].py -v

# Run specific test class
python -m pytest modules/[your_module]/tests/test_[file].py::TestClass -v

# Run specific test method
python -m pytest modules/[your_module]/tests/test_[file].py::TestClass::test_method -v

# Run with print statements visible
python -m pytest modules/[your_module]/tests/ -v -s

# Run with debugger on failure
python -m pytest modules/[your_module]/tests/ -v --pdb
```

## 📚 Documentation Structure

### Required Files

```
modules/[your_module]/
├── README.md                    # Module documentation (use template)
├── MIGRATION_GUIDE.md          # Migration instructions
├── integration_example.py      # Working example
└── tests/
    ├── __init__.py
    ├── test_[main_file].py     # Main functionality tests
    ├── test_integration.py     # Integration tests
    ├── test_performance.py     # Performance tests
    └── test_error_handling.py  # Error handling tests

docs/
├── developer_logs/
│   └── [YOUR_NAME]_log.md      # Your development log
└── technical_notes/
    └── [YOUR_MODULE]_notes.md  # Technical insights
```

### Documentation Templates

- **Module README**: Use `docs/MODULE_TEMPLATE.md`
- **Test Template**: Use `docs/TEST_TEMPLATE.md`
- **Developer Log**: Use `docs/developer_logs/README.md`
- **Technical Notes**: Use `docs/technical_notes/README.md`

## 🔧 Integration Patterns

### GameStateManager Integration

```python
# Initialize with state manager
state_manager = GameStateManager()
module_instance = YourModule(state_manager)

# Set state
state_manager.set("[your_module].[field]", value, "source", "description")

# Get state
value = state_manager.get("[your_module].[field]")

# Register callbacks
state_manager.add_change_callback("[your_module].[field]", callback_function)
```

### Callback Pattern

```python
def on_state_changed(field_path, old_value, new_value):
    # Handle state change
    pass

# Register callback
state_manager.add_change_callback("[your_module].[field]", on_state_changed)
```

### Error Handling Pattern

```python
try:
    result = state_manager.set("[your_module].[field]", value)
    if not result:
        # Handle validation failure
        pass
except Exception as e:
    # Handle error
    logger.error(f"Error setting state: {e}")
```

## 📊 Test Coverage Requirements

### Coverage Targets

- **Unit Tests**: >90% coverage for core functionality
- **Integration Tests**: >80% coverage for integration points
- **Error Handling**: 100% coverage for error paths
- **Performance Tests**: All critical paths tested

### Test Types

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test with GameStateManager
3. **Performance Tests**: Test performance and memory usage
4. **Error Handling Tests**: Test error scenarios and recovery

## 🔍 Debugging

### Common Issues

1. **Import Errors**: Check module paths and dependencies
2. **State Validation**: Check GameStateManager validation rules
3. **Callback Issues**: Verify callback registration and execution
4. **Performance Issues**: Check for memory leaks or slow operations

### Debugging Commands

```bash
# Run with verbose output
python -m pytest -v

# Run with print statements
python -m pytest -v -s

# Run with debugger
python -m pytest --pdb

# Run specific failing test
python -m pytest path/to/test.py::TestClass::test_method -v -s
```

## 📝 Daily Workflow

### Start of Day

1. **Update Developer Log**: Add new day entry
2. **Check Test Status**: Run `make test-[your_module]`
3. **Review Documentation**: Check for updates needed

### During Development

1. **Write Tests First**: Follow TDD approach
2. **Update Documentation**: Keep docs current
3. **Run Tests Frequently**: `make test-[your_module]`
4. **Check Integration**: `make test-modules`

### End of Day

1. **Update Developer Log**: Document progress and challenges
2. **Run Full Test Suite**: `make test-all`
3. **Update Technical Notes**: Document decisions and insights
4. **Commit Changes**: Include documentation updates

## 📞 Communication

### Questions for Documentation Specialist

Use your developer log to ask questions:

```markdown
### [Date] - [Question Topic]
**Question**: [Your specific question]

**Context**: [Why you need this information]

**Impact**: [How this affects your work]
```

### Support Channels

- **GitHub Issues**: For specific documentation needs
- **GitHub Discussions**: For general questions and ideas
- **Developer Logs**: For ongoing progress updates
- **Pull Requests**: Include documentation updates with code changes

## 🎯 Success Metrics

### Before Submitting

- [ ] All tests pass: `make test-[your_module]`
- [ ] Coverage requirements met: `make test-coverage`
- [ ] Integration tests pass: `make test-modules`
- [ ] Performance tests pass: `make test-performance`
- [ ] Error handling tested
- [ ] Documentation updated
- [ ] Code follows style guidelines: `make lint`

### Quality Checklist

- [ ] Tests are independent and can run in any order
- [ ] Tests clean up after themselves
- [ ] Tests use descriptive names
- [ ] Tests have clear assertions
- [ ] Tests cover edge cases
- [ ] Tests handle errors gracefully
- [ ] Tests are fast (<1 second each)
- [ ] Tests don't have side effects

## 🔗 Reference Links

### Documentation

- [Module Template](docs/MODULE_TEMPLATE.md)
- [Test Template](docs/TEST_TEMPLATE.md)
- [Testing Guide](docs/TESTING_GUIDE.md)
- [Developer Logs Guide](docs/developer_logs/README.md)
- [Technical Notes Guide](docs/technical_notes/README.md)

### Examples

- [Screen Module README](modules/screen_module/README.md)
- [Screen Module Tests](modules/screen_module/tests/)
- [Screen Integration Example](modules/screen_module/integration_example.py)

### Tools

- [Makefile](Makefile) - Test automation commands
- [pytest.ini](pytest.ini) - Test configuration
- [requirements-dev.txt](requirements-dev.txt) - Development dependencies

---

**Remember**: Good documentation and testing are investments in code quality and team collaboration! 📚✨
