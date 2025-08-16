# Performance Testing Framework

## Overview

The BladeFighters Performance Testing Framework provides comprehensive performance benchmarking and regression detection for all game components. This framework ensures that the game maintains optimal performance across different systems and helps identify performance regressions early in development.

## Features

- **Comprehensive Benchmarking**: Tests performance of audio, input, game state, and puzzle engine systems
- **Load Testing**: Concurrent operation testing to identify bottlenecks
- **Regression Detection**: Automatic detection of performance degradations
- **Configurable Thresholds**: Adjustable performance limits for different components
- **Detailed Reporting**: JSON reports with statistics and recommendations
- **Real-time Monitoring**: Memory, CPU, and timing measurements

## Components

### 1. Performance Test Framework (`test_performance_framework.py`)

The main performance testing framework containing:

- **PerformanceBenchmark**: Base class for performance benchmarking
- **PerformanceMetrics**: Data structure for performance measurements
- **PerformanceThreshold**: Configuration for performance limits
- **Test Classes**:
  - `AudioPerformanceTests`: Audio system performance
  - `InputPerformanceTests`: Input system performance
  - `GameStatePerformanceTests`: Game state management performance
  - `PuzzleEnginePerformanceTests`: Puzzle engine performance
  - `LoadPerformanceTests`: Concurrent operation testing
  - `PerformanceRegressionTests`: Regression detection

### 2. Performance Configuration (`performance_config.json`)

Configuration file defining performance thresholds and settings.

### 3. Performance Test Runner (`simple_performance_runner.py`)

Command-line tool for running performance tests with reporting.

## Usage

### Running Performance Tests

#### Method 1: Using the Simple Runner (Recommended)

```bash
# Run all performance tests
python3 simple_performance_runner.py

# Run with custom configuration
python3 simple_performance_runner.py --config custom_config.json

# Save report to specific file
python3 simple_performance_runner.py --output my_report.json
```

#### Method 2: Using pytest directly

```bash
# Run from project root
python3 -m pytest tests/consolidated/performance/test_performance_framework.py -v
```

### Configuration

Each component has configurable performance thresholds:

- **max_duration_ms**: Maximum allowed duration for operations
- **max_memory_mb**: Maximum memory usage increase
- **max_cpu_percent**: Maximum CPU usage percentage
- **min_ops_per_second**: Minimum operations per second

## Test Categories

1. **Audio System Tests**: Audio initialization, sound loading, volume control
2. **Input System Tests**: Event processing, key state management, input repeat
3. **Game State Tests**: State updates and queries
4. **Puzzle Engine Tests**: Engine initialization and updates
5. **Load Tests**: Concurrent operations
6. **Regression Tests**: Performance regression detection

## Reports

Performance reports include comprehensive metrics and recommendations in JSON format.

## Troubleshooting

### Common Issues

1. **Import Errors**: Run tests from project root directory
2. **Threshold Violations**: Check if thresholds are realistic for your system
3. **Timeout Issues**: Increase timeout or optimize slow operations

## Best Practices

1. **Regular Testing**: Run performance tests before each release
2. **Threshold Management**: Set realistic thresholds based on target hardware
3. **Baseline Management**: Maintain performance baselines for different systems
4. **Performance Monitoring**: Monitor memory and CPU usage patterns

## Contributing

When adding new performance tests:

1. Create a new test class inheriting from `unittest.TestCase`
2. Implement test methods with appropriate performance measurements
3. Add configuration for new component in `performance_config.json`
4. Update documentation
