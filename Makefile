# BladeFighters Makefile
# Includes comprehensive test automation

.PHONY: help test test-all test-performance test-regression test-modules test-audio test-screen test-input clean install dev-install run test-expanded test-unit test-integration

# Default target
help:
	@echo "BladeFighters - Available Commands:"
	@echo ""
	@echo "Game Commands:"
	@echo "  run              - Run the game"
	@echo "  run-mac          - Run the game on macOS"
	@echo ""
	@echo "Test Commands:"
	@echo "  test             - Run basic tests"
	@echo "  test-all         - Run comprehensive test suite"
	@echo "  test-performance - Run performance benchmarks only"
	@echo "  test-regression  - Run regression tests only"
	@echo "  test-modules     - Run module integration tests only"
	@echo "  test-audio       - Run audio module tests only"
	@echo "  test-screen      - Run screen module tests only"
	@echo "  test-input       - Run input module tests only"
	@echo ""
	@echo "Expanded Testing Infrastructure:"
	@echo "  test-expanded    - Run complete expanded test suite"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-performance-expanded - Run performance tests with detailed reporting"
	@echo ""
	@echo "Development Commands:"
	@echo "  install          - Install production dependencies"
	@echo "  dev-install      - Install development dependencies"
	@echo "  clean            - Clean build artifacts"
	@echo "  validate         - Validate module imports and dependencies"

# Game Commands
run:
	@echo "🎮 Starting BladeFighters..."
	python game_client.py

run-mac:
	@echo "🍎 Starting BladeFighters on macOS..."
	./run_mac.sh

# Basic Test Commands
test:
	@echo "🧪 Running basic tests..."
	python -m pytest tests/ -v

test-all:
	@echo "🧪 Running comprehensive test suite..."
	python tests/run_comprehensive_tests.py

test-performance:
	@echo "⚡ Running performance benchmarks..."
	python tests/run_comprehensive_tests.py --performance-only

test-regression:
	@echo "🔄 Running regression tests..."
	python tests/run_comprehensive_tests.py --regression-only

test-modules:
	@echo "📦 Running module integration tests..."
	python tests/run_comprehensive_tests.py --modules-only

test-audio:
	@echo "🎵 Running audio module tests..."
	python tests/run_comprehensive_tests.py --audio-only

test-screen:
	@echo "🖥️  Running screen module tests..."
	python tests/run_comprehensive_tests.py --screen-only

test-input:
	@echo "⌨️  Running input module tests..."
	python tests/run_comprehensive_tests.py --input-only

# Expanded Testing Infrastructure Commands
test-expanded:
	@echo "🚀 Running Expanded Test Suite..."
	@echo "This includes unit tests, performance tests, and end-to-end tests"
	python tests/run_expanded_test_suite.py --save-results --generate-report

test-unit:
	@echo "📋 Running Unit Tests..."
	python tests/run_expanded_test_suite.py --unit-only --save-results

test-integration:
	@echo "🔄 Running Integration Tests..."
	python tests/run_expanded_test_suite.py --integration-only --save-results

test-performance-expanded:
	@echo "⚡ Running Performance Tests with Detailed Reporting..."
	python tests/run_expanded_test_suite.py --performance-only --save-results --generate-report

test-quick:
	@echo "⚡ Running Quick Test Suite (Unit Tests Only)..."
	python tests/run_expanded_test_suite.py --unit-only --no-performance --no-integration

test-full:
	@echo "🎯 Running Full Test Suite with All Categories..."
	python tests/run_expanded_test_suite.py --save-results --generate-report --output-dir=test_results_full

# Development Commands
install:
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt

dev-install:
	@echo "🔧 Installing development dependencies..."
	pip install -r requirements-dev.txt

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf __pycache__/
	rm -rf */__pycache__/
	rm -rf */*/__pycache__/
	rm -rf .pytest_cache/
	rm -rf test_results/
	rm -rf test_results_full/
	rm -f *.pyc
	rm -f */*.pyc
	rm -f */*/*.pyc
	rm -f expanded_test_results.json
	rm -f expanded_test_report.txt
	rm -f performance_baseline.json

validate:
	@echo "🔍 Validating module imports and dependencies..."
	@python -c "import sys; sys.path.insert(0, '.'); from modules.audio_module import AudioSystem; print('✅ Audio module imports successfully')"
	@python -c "import sys; sys.path.insert(0, '.'); from modules.input_module import InputManager; print('✅ Input module imports successfully')"
	@python -c "import sys; sys.path.insert(0, '.'); from modules.screen_module import ScreenManager; print('✅ Screen module imports successfully')"
	@python -c "import sys; sys.path.insert(0, '.'); from modules.game_state_module.game_state_manager import GameStateManager; print('✅ Game state module imports successfully')"
	@python -c "import sys; sys.path.insert(0, '.'); from core.puzzle_module import PuzzleEngine; print('✅ Puzzle engine imports successfully')"
	@echo "✅ All core modules validate successfully!"

# CI/CD Commands
ci-test:
	@echo "🤖 Running CI Test Suite..."
	python tests/run_expanded_test_suite.py --unit-only --save-results --output-dir=ci_results

ci-full:
	@echo "🤖 Running Full CI Test Suite..."
	python tests/run_expanded_test_suite.py --save-results --generate-report --output-dir=ci_results

# Documentation Commands
docs-test:
	@echo "📚 Generating test documentation..."
	@echo "Test documentation is available in tests/EXPANDED_TESTING_INFRASTRUCTURE.md"
	@echo "Run 'make test-expanded' to generate current test reports"

# Utility Commands
test-report:
	@echo "📊 Generating test report..."
	@if [ -f "test_results/expanded_test_results.json" ]; then \
		echo "📋 Test Results Summary:"; \
		python -c "import json; data=json.load(open('test_results/expanded_test_results.json')); print(f'Total Tests: {data[\"summary\"][\"total_tests\"]}'); print(f'Passed: {data[\"summary\"][\"passed\"]}'); print(f'Failed: {data[\"summary\"][\"failed\"]}'); print(f'Errors: {data[\"summary\"][\"errors\"]}'); print(f'Duration: {data[\"summary\"][\"total_duration\"]:.2f}s')"; \
	else \
		echo "❌ No test results found. Run 'make test-expanded' first."; \
	fi

test-status:
	@echo "📈 Test Status Check..."
	@if [ -f "test_results/expanded_test_results.json" ]; then \
		python -c "import json; data=json.load(open('test_results/expanded_test_results.json')); summary=data['summary']; pass_rate=(summary['passed']/summary['total_tests']*100) if summary['total_tests'] > 0 else 0; print(f'Pass Rate: {pass_rate:.1f}%'); print('✅ All good!' if summary['failed'] == 0 and summary['errors'] == 0 else '⚠️  Issues detected')"; \
	else \
		echo "❌ No test results found. Run 'make test-expanded' first."; \
	fi

# Helpers
.PHONY: test-help
test-help:
	@echo "🧪 Testing Infrastructure Help:"
	@echo ""
	@echo "Quick Start:"
	@echo "  make test-quick      - Run unit tests only (fastest)"
	@echo "  make test-expanded   - Run complete test suite"
	@echo "  make test-full       - Run all tests with detailed reporting"
	@echo ""
	@echo "Specific Test Types:"
	@echo "  make test-unit       - Unit tests only"
	@echo "  make test-integration - Integration tests only"
	@echo "  make test-performance-expanded - Performance tests with reporting"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci-test         - CI-friendly test suite"
	@echo "  make ci-full         - Full CI test suite"
	@echo ""
	@echo "Utilities:"
	@echo "  make test-report     - Show test results summary"
	@echo "  make test-status     - Check test pass/fail status"
	@echo "  make docs-test       - Show test documentation info"
	@echo ""
	@echo "For detailed information, see tests/EXPANDED_TESTING_INFRASTRUCTURE.md"

