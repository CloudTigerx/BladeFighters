#!/usr/bin/env python3
"""
Comprehensive Test Runner for BladeFighters

This script discovers and runs all tests in the consolidated test structure.
It maintains the original functionality while providing a unified interface.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set environment variable for pytest to find the correct configuration
os.environ['PYTHONPATH'] = str(project_root)

class ConsolidatedTestRunner:
    """Manages running all tests in the consolidated structure."""
    
    def __init__(self):
        self.test_dirs = {
            'unit': 'tests/consolidated/unit',
            'integration': 'tests/consolidated/integration', 
            'performance': 'tests/consolidated/performance',
            'modules': 'tests/consolidated/modules',
            'core': 'tests/consolidated/core',
            'root': 'tests/consolidated/root'
        }
        self.results = {}
    
    def discover_tests(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """Discover all test files in the specified category or all categories."""
        discovered = {}
        
        if category and category in self.test_dirs:
            categories = {category: self.test_dirs[category]}
        else:
            categories = self.test_dirs
        
        for cat, test_dir in categories.items():
            if os.path.exists(test_dir):
                test_files = []
                for root, dirs, files in os.walk(test_dir):
                    for file in files:
                        if file.startswith('test_') and file.endswith('.py'):
                            test_files.append(os.path.join(root, file))
                discovered[cat] = test_files
        
        return discovered
    
    def run_tests(self, category: Optional[str] = None, verbose: bool = False, 
                  pattern: Optional[str] = None) -> Dict[str, bool]:
        """Run tests in the specified category or all categories."""
        discovered = self.discover_tests(category)
        results = {}
        
        for cat, test_files in discovered.items():
            if not test_files:
                print(f"No tests found in {cat}")
                results[cat] = True
                continue
                
            print(f"\n{'='*50}")
            print(f"Running {cat} tests ({len(test_files)} files)")
            print(f"{'='*50}")
            
            success = True
            for test_file in test_files:
                if pattern and pattern not in test_file:
                    continue
                    
                print(f"\nRunning: {test_file}")
                try:
                    # Run the test file with pytest
                    cmd = [sys.executable, '-m', 'pytest', test_file, '--import-mode=importlib']
                    if verbose:
                        cmd.append('-v')
                    
                    # Set the working directory to the project root for proper module resolution
                    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
                    
                    if result.returncode == 0:
                        print(f"✅ PASSED: {test_file}")
                    else:
                        print(f"❌ FAILED: {test_file}")
                        print(f"Error: {result.stderr}")
                        success = False
                        
                except Exception as e:
                    print(f"❌ ERROR running {test_file}: {e}")
                    success = False
            
            results[cat] = success
            
        return results
    
    def run_specific_test(self, test_path: str, verbose: bool = False) -> bool:
        """Run a specific test file."""
        if not os.path.exists(test_path):
            print(f"Test file not found: {test_path}")
            return False
            
        print(f"Running specific test: {test_path}")
        try:
            cmd = [sys.executable, '-m', 'pytest', test_path, '--import-mode=importlib']
            if verbose:
                cmd.append('-v')
            
            # Set the working directory to the project root for proper module resolution
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
            
            if result.returncode == 0:
                print(f"✅ PASSED: {test_path}")
                return True
            else:
                print(f"❌ FAILED: {test_path}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ ERROR running {test_path}: {e}")
            return False
    
    def list_tests(self, category: Optional[str] = None) -> None:
        """List all available tests."""
        discovered = self.discover_tests(category)
        
        print("Available Tests:")
        print("=" * 50)
        
        for cat, test_files in discovered.items():
            print(f"\n{cat.upper()} Tests ({len(test_files)} files):")
            for test_file in test_files:
                print(f"  - {test_file}")
    
    def generate_report(self, results: Dict[str, bool]) -> None:
        """Generate a summary report of test results."""
        print("\n" + "="*50)
        print("TEST SUMMARY REPORT")
        print("="*50)
        
        total_categories = len(results)
        passed_categories = sum(1 for success in results.values() if success)
        
        for category, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{category:15} : {status}")
        
        print(f"\nOverall: {passed_categories}/{total_categories} categories passed")
        
        if passed_categories == total_categories:
            print("🎉 All test categories passed!")
        else:
            print("⚠️  Some test categories failed. Check the output above for details.")

def main():
    parser = argparse.ArgumentParser(description="Run BladeFighters consolidated tests")
    parser.add_argument('--category', '-c', choices=['unit', 'integration', 'performance', 'modules', 'core', 'root'],
                       help='Run tests from specific category only')
    parser.add_argument('--test', '-t', help='Run a specific test file')
    parser.add_argument('--list', '-l', action='store_true', help='List all available tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--pattern', '-p', help='Filter tests by pattern in filename')
    
    args = parser.parse_args()
    
    runner = ConsolidatedTestRunner()
    
    if args.list:
        runner.list_tests(args.category)
        return
    
    if args.test:
        success = runner.run_specific_test(args.test, args.verbose)
        sys.exit(0 if success else 1)
    
    # Run all tests or category-specific tests
    results = runner.run_tests(args.category, args.verbose, args.pattern)
    runner.generate_report(results)
    
    # Exit with appropriate code
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
