#!/usr/bin/env python3
"""
Comprehensive Transformation System Test Runner
Runs all transformation flow, weapon integration, and visual verification tests.
"""

import sys
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_transformation_flow_tests():
    """Run transformation flow tests."""
    print("\n" + "="*80)
    print("🚀 RUNNING TRANSFORMATION FLOW TESTS")
    print("="*80)
    
    try:
        from transformation_flow_test import TransformationFlowTest
        test_suite = TransformationFlowTest()
        results = test_suite.run_all_tests()
        return results
    except Exception as e:
        print(f"❌ Transformation flow tests failed: {e}")
        traceback.print_exc()
        return {}

def run_weapon_integration_tests():
    """Run weapon integration tests."""
    print("\n" + "="*80)
    print("🚀 RUNNING WEAPON INTEGRATION TESTS")
    print("="*80)
    
    try:
        from weapon_integration_test import WeaponIntegrationTest
        test_suite = WeaponIntegrationTest()
        results = test_suite.run_all_tests()
        return results
    except Exception as e:
        print(f"❌ Weapon integration tests failed: {e}")
        traceback.print_exc()
        return {}

def run_visual_verification_tests():
    """Run visual verification tests."""
    print("\n" + "="*80)
    print("🚀 RUNNING VISUAL VERIFICATION TESTS")
    print("="*80)
    
    try:
        from visual_verification_test import VisualVerificationTest
        test_suite = VisualVerificationTest()
        results = test_suite.run_all_tests()
        return results
    except Exception as e:
        print(f"❌ Visual verification tests failed: {e}")
        traceback.print_exc()
        return {}

def generate_comprehensive_report(all_results: Dict[str, Dict[str, bool]]):
    """Generate comprehensive test report."""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TRANSFORMATION SYSTEM TEST REPORT")
    print("="*80)
    
    # Calculate overall statistics
    total_tests = 0
    total_passed = 0
    test_suite_results = {}
    
    for suite_name, results in all_results.items():
        if results:
            suite_total = len(results)
            suite_passed = sum(1 for result in results.values() if result)
            test_suite_results[suite_name] = {
                'total': suite_total,
                'passed': suite_passed,
                'failed': suite_total - suite_passed,
                'success_rate': (suite_passed / suite_total) * 100 if suite_total > 0 else 0
            }
            total_tests += suite_total
            total_passed += suite_passed
    
    overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    # Print suite summaries
    print(f"\n🎯 TEST SUITE SUMMARIES:")
    for suite_name, stats in test_suite_results.items():
        status = "✅ PASS" if stats['failed'] == 0 else "❌ FAIL"
        print(f"  {status} {suite_name}: {stats['passed']}/{stats['total']} tests passed ({stats['success_rate']:.1f}%)")
    
    # Print overall results
    print(f"\n🎯 OVERALL RESULTS:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_tests - total_passed}")
    print(f"  Success Rate: {overall_success_rate:.1f}%")
    
    # Print detailed results
    print(f"\n📋 DETAILED TEST RESULTS:")
    for suite_name, results in all_results.items():
        if results:
            print(f"\n  📁 {suite_name.upper()}:")
            for test_name, result in results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"    {status} {test_name}")
    
    # Print recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if overall_success_rate == 100:
        print("  🎉 All tests passed! The transformation system is working perfectly.")
        print("  ✅ Weapon system integration is functional")
        print("  ✅ Attack delivery system is working")
        print("  ✅ Block transformation flow is correct")
        print("  ✅ Visual rendering is proper")
    elif overall_success_rate >= 80:
        print("  🟡 Most tests passed. Minor issues detected.")
        print("  ⚠️ Check failed tests for specific issues")
        print("  🔧 Consider addressing failed tests before production")
    else:
        print("  🚨 Significant issues detected. System needs attention.")
        print("  ❌ Multiple test failures indicate systemic problems")
        print("  🔧 Prioritize fixing failed tests")
        print("  🚨 Do not deploy until issues are resolved")
    
    return overall_success_rate == 100

def main():
    """Main function to run all comprehensive tests."""
    print("🚀 COMPREHENSIVE TRANSFORMATION SYSTEM TEST SUITE")
    print("Testing: Weapon System → Attack Delivery → Block Transformation → Visual Rendering")
    print("="*80)
    
    start_time = time.time()
    
    # Run all test suites
    all_results = {}
    
    # Test 1: Transformation Flow
    all_results['transformation_flow'] = run_transformation_flow_tests()
    
    # Test 2: Weapon Integration
    all_results['weapon_integration'] = run_weapon_integration_tests()
    
    # Test 3: Visual Verification
    all_results['visual_verification'] = run_visual_verification_tests()
    
    # Generate comprehensive report
    success = generate_comprehensive_report(all_results)
    
    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n⏱️ Test execution time: {execution_time:.2f} seconds")
    
    # Save comprehensive report
    report_filename = f"comprehensive_transformation_test_report_{int(time.time())}.txt"
    with open(report_filename, "w") as f:
        f.write("COMPREHENSIVE TRANSFORMATION SYSTEM TEST REPORT\n")
        f.write("="*80 + "\n\n")
        
        for suite_name, results in all_results.items():
            if results:
                f.write(f"{suite_name.upper()} RESULTS:\n")
                for test_name, result in results.items():
                    status = "PASS" if result else "FAIL"
                    f.write(f"  {status}: {test_name}\n")
                f.write("\n")
        
        f.write(f"Execution time: {execution_time:.2f} seconds\n")
        f.write(f"Overall success: {'YES' if success else 'NO'}\n")
    
    print(f"\n📝 Comprehensive report saved to: {report_filename}")
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Transformation system is fully functional.")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the detailed report above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
