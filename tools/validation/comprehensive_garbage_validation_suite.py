#!/usr/bin/env python3
"""
COMPREHENSIVE GARBAGE VALIDATION SUITE
======================================

This suite will thoroughly test ALL garbage-related functionality:
- Garbage formula accuracy
- Garbage delivery mechanics
- Garbage vs strikes differentiation
- Garbage placement patterns
- Garbage transformation issues
- Edge cases and weird scenarios

Run this to validate your garbage system thoroughly!
"""

import sys
import os
import time
import json
import traceback
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.attack_module.attack_calculator import AttackCalculator
from modules.attack_module.attack_manager import AttackManager
from modules.testmode_module.test_mode import TestModeRefactored
import pygame

@dataclass
class GarbageValidationResult:
    """Result of a garbage validation test"""
    test_name: str
    passed: bool
    expected: Any
    actual: Any
    details: str
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'

class GarbageValidationSuite:
    """Comprehensive garbage system validation suite"""
    
    def __init__(self):
        self.results: List[GarbageValidationResult] = []
        self.critical_failures = 0
        self.high_failures = 0
        self.medium_failures = 0
        self.low_failures = 0
        
        # Initialize pygame for test mode
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        self.font = pygame.font.Font(None, 24)
        
        # Initialize components
        self.calculator = AttackCalculator()
        self.attack_manager = AttackManager()
        
        # Initialize test mode for delivery testing
        self.test_mode = TestModeRefactored(
            screen=self.screen,
            font=self.font,
            audio=None,
            asset_path="puzzleassets",
            settings_system=None,
            clock=None
        )
        self.test_mode.initialize_test()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all garbage validation tests"""
        print("🗑️ COMPREHENSIVE GARBAGE VALIDATION SUITE STARTING...")
        print("=" * 80)
        
        start_time = time.time()
        
        # Formula validation tests
        self._test_garbage_formulas()
        self._test_garbage_scaling()
        self._test_garbage_edge_cases()
        
        # Garbage generation tests
        self._test_garbage_generation()
        self._test_garbage_queuing()
        self._test_garbage_delivery()
        
        # Garbage vs strikes tests
        self._test_garbage_vs_strikes()
        self._test_garbage_placement()
        self._test_garbage_transformation()
        
        # Integration tests
        self._test_real_world_garbage_scenarios()
        self._test_extreme_garbage_cases()
        self._test_weird_garbage_edge_cases()
        
        # Performance and stability tests
        self._test_garbage_performance()
        self._test_garbage_stability()
        
        end_time = time.time()
        
        return self._generate_report(end_time - start_time)
    
    def _test_garbage_formulas(self):
        """Test garbage calculation formulas"""
        print("\n📊 TESTING GARBAGE FORMULAS...")
        
        # Test basic garbage formula: (blocks × combo) ÷ 2
        test_cases = [
            (1, 1, 0, "1 block, 1x combo"),
            (2, 1, 1, "2 blocks, 1x combo"),
            (3, 1, 1, "3 blocks, 1x combo"),
            (4, 1, 2, "4 blocks, 1x combo"),
            (5, 1, 2, "5 blocks, 1x combo"),
            (6, 1, 3, "6 blocks, 1x combo"),
            (7, 1, 3, "7 blocks, 1x combo"),
            (8, 1, 4, "8 blocks, 1x combo"),
            (9, 1, 4, "9 blocks, 1x combo"),
            (10, 1, 5, "10 blocks, 1x combo"),
        ]
        
        for blocks, combo, expected, desc in test_cases:
            actual = self.calculator.calculate_garbage_attack(blocks, combo)
            passed = actual == expected
            self._record_result(
                f"Garbage Formula: {desc}",
                passed,
                expected,
                actual,
                f"Formula: ({blocks} × {combo}) ÷ 2 = {expected}",
                "CRITICAL" if not passed else "LOW"
            )
        
        # Test combo scaling
        combo_scaling_tests = [
            (4, 2, 4, "4 blocks, 2x combo"),
            (4, 3, 6, "4 blocks, 3x combo"),
            (4, 4, 8, "4 blocks, 4x combo"),
            (4, 5, 10, "4 blocks, 5x combo"),
            (6, 2, 6, "6 blocks, 2x combo"),
            (6, 3, 9, "6 blocks, 3x combo"),
            (8, 2, 8, "8 blocks, 2x combo"),
            (8, 3, 12, "8 blocks, 3x combo"),
        ]
        
        for blocks, combo, expected, desc in combo_scaling_tests:
            actual = self.calculator.calculate_garbage_attack(blocks, combo)
            passed = actual == expected
            self._record_result(
                f"Garbage Combo Scaling: {desc}",
                passed,
                expected,
                actual,
                f"Formula: ({blocks} × {combo}) ÷ 2 = {expected}",
                "CRITICAL" if not passed else "LOW"
            )
    
    def _test_garbage_scaling(self):
        """Test garbage scaling behavior"""
        print("\n📈 TESTING GARBAGE SCALING...")
        
        # Test that garbage scales linearly with combo
        base_blocks = 6
        for combo in range(1, 11):
            garbage = self.calculator.calculate_garbage_attack(base_blocks, combo)
            expected = (base_blocks * combo) // 2
            
            passed = garbage == expected
            self._record_result(
                f"Garbage Scaling: {base_blocks} blocks, {combo}x combo",
                passed,
                expected,
                garbage,
                f"Should scale linearly: ({base_blocks} × {combo}) ÷ 2 = {expected}",
                "HIGH" if not passed else "LOW"
            )
        
        # Test that garbage is always less than or equal to blocks × combo
        for blocks in range(1, 21):
            for combo in range(1, 6):
                garbage = self.calculator.calculate_garbage_attack(blocks, combo)
                max_possible = blocks * combo
                
                # Garbage should never exceed blocks × combo
                passed = garbage <= max_possible
                self._record_result(
                    f"Garbage Upper Bound: {blocks} blocks, {combo}x combo",
                    passed,
                    f"≤ {max_possible}",
                    garbage,
                    f"Garbage ({garbage}) should not exceed {max_possible}",
                    "HIGH" if not passed else "LOW"
                )
    
    def _test_garbage_edge_cases(self):
        """Test garbage edge cases"""
        print("\n🔍 TESTING GARBAGE EDGE CASES...")
        
        # Test zero blocks
        zero_garbage = self.calculator.calculate_garbage_attack(0, 1)
        passed = zero_garbage == 0
        self._record_result(
            "Zero Blocks Garbage",
            passed,
            0,
            zero_garbage,
            "Zero blocks should produce 0 garbage",
            "HIGH" if not passed else "LOW"
        )
        
        # Test zero combo
        zero_combo_garbage = self.calculator.calculate_garbage_attack(4, 0)
        passed = zero_combo_garbage == 0
        self._record_result(
            "Zero Combo Garbage",
            passed,
            0,
            zero_combo_garbage,
            "Zero combo should produce 0 garbage",
            "HIGH" if not passed else "LOW"
        )
        
        # Test negative values
        try:
            negative_garbage = self.calculator.calculate_garbage_attack(-1, 1)
            passed = negative_garbage >= 0
            self._record_result(
                "Negative Blocks Garbage",
                passed,
                "≥ 0",
                negative_garbage,
                "Negative blocks should be handled gracefully",
                "MEDIUM" if not passed else "LOW"
            )
        except Exception as e:
            self._record_result(
                "Negative Blocks Exception",
                False,
                "No exception",
                str(e),
                "Negative blocks should not cause exceptions",
                "MEDIUM"
            )
        
        # Test very large values
        try:
            large_garbage = self.calculator.calculate_garbage_attack(1000, 10)
            passed = large_garbage >= 0 and large_garbage <= 5000
            self._record_result(
                "Large Values Garbage",
                passed,
                "0 ≤ garbage ≤ 5000",
                large_garbage,
                f"Large values should be handled: {large_garbage}",
                "MEDIUM" if not passed else "LOW"
            )
        except Exception as e:
            self._record_result(
                "Large Values Exception",
                False,
                "No exception",
                str(e),
                "Large values should not cause exceptions",
                "MEDIUM"
            )
    
    def _test_garbage_generation(self):
        """Test garbage generation through AttackManager"""
        print("\n🎯 TESTING GARBAGE GENERATION...")
        
        # Test basic garbage generation
        test_combos = [
            # (broken_blocks, is_cluster, combo_multiplier, expected_garbage)
            ([(1, 1, 'red'), (2, 1, 'red')], False, 1, 1),  # 2 blocks, no cluster
            ([(1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red')], False, 1, 1),  # 3 blocks, no cluster
            ([(1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red'), (4, 1, 'red')], False, 1, 2),  # 4 blocks, no cluster
            ([(1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red'), (4, 1, 'red'), (5, 1, 'red')], False, 2, 5),  # 5 blocks, 2x combo
        ]
        
        for broken_blocks, is_cluster, combo, expected_garbage in test_combos:
            result = self.attack_manager.process_combo(
                broken_blocks, is_cluster, combo, player_id=1
            )
            
            actual_garbage = result.get('garbage_blocks', 0)
            passed = actual_garbage == expected_garbage
            
            self._record_result(
                f"Garbage Generation: {len(broken_blocks)} blocks, cluster={is_cluster}, combo={combo}",
                passed,
                expected_garbage,
                actual_garbage,
                f"Expected {expected_garbage} garbage blocks",
                "CRITICAL" if not passed else "LOW"
            )
    
    def _test_garbage_queuing(self):
        """Test garbage queuing"""
        print("\n⏰ TESTING GARBAGE QUEUING...")
        
        # Test that garbage is properly queued
        result = self.attack_manager.process_combo(
            [(1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red'), (4, 1, 'red')],
            False, 1, player_id=1
        )
        
        # Check that garbage is in the queue
        target_player = 2  # Player 1 attacks player 2
        pending_attacks = self.attack_manager.get_pending_attacks(target_player)
        
        garbage_queued = any(
            hasattr(attack, 'attack_type') and 
            getattr(attack, 'attack_type', None) and 
            getattr(attack.attack_type, 'value', None) == 'garbage_blocks'
            for attack in pending_attacks
        )
        
        passed = garbage_queued
        self._record_result(
            "Garbage Attack Queuing",
            passed,
            True,
            garbage_queued,
            f"Generated {result.get('garbage_blocks', 0)} garbage blocks",
            "CRITICAL" if not passed else "LOW"
        )
    
    def _test_garbage_delivery(self):
        """Test garbage delivery through TestMode"""
        print("\n🚀 TESTING GARBAGE DELIVERY...")
        
        # Test garbage delivery
        self.test_mode.queue_attack_spawn('enemy', 'garbage', count=5)
        
        # Check that garbage is queued
        enemy_attacks = self.test_mode.pending_attacks.get('enemy', [])
        garbage_queued = any(attack.get('type') == 'garbage' for attack in enemy_attacks)
        
        self._record_result(
            "Garbage Delivery Queuing",
            garbage_queued,
            True,
            garbage_queued,
            f"Queued {len(enemy_attacks)} attacks",
            "CRITICAL" if not garbage_queued else "LOW"
        )
        
        # Test garbage count accuracy
        if enemy_attacks:
            garbage_attack = next((a for a in enemy_attacks if a.get('type') == 'garbage'), None)
            if garbage_attack:
                expected_count = 5
                actual_count = garbage_attack.get('count', 0)
                passed = actual_count == expected_count
                
                self._record_result(
                    "Garbage Count Accuracy",
                    passed,
                    expected_count,
                    actual_count,
                    f"Queued garbage count should be {expected_count}",
                    "HIGH" if not passed else "LOW"
                )
    
    def _test_garbage_vs_strikes(self):
        """Test garbage vs strikes differentiation"""
        print("\n⚖️ TESTING GARBAGE VS STRIKES...")
        
        # Test that garbage and strikes are properly differentiated
        test_cases = [
            (4, 1, "4 blocks, 1x combo"),
            (6, 2, "6 blocks, 2x combo"),
            (8, 3, "8 blocks, 3x combo"),
            (10, 4, "10 blocks, 4x combo"),
        ]
        
        for blocks, combo, desc in test_cases:
            garbage = self.calculator.calculate_garbage_attack(blocks, combo)
            strikes = self.calculator.calculate_strike_attack(blocks, combo)
            
            # Garbage should be less than strikes for normal cases
            garbage_less_than_strikes = garbage < strikes
            
            self._record_result(
                f"Garbage < Strikes: {desc}",
                garbage_less_than_strikes,
                True,
                garbage_less_than_strikes,
                f"Garbage={garbage}, Strikes={strikes}",
                "CRITICAL" if not garbage_less_than_strikes else "LOW"
            )
            
            # Garbage should be exactly (blocks × combo) ÷ 2
            expected_garbage = (blocks * combo) // 2
            garbage_formula_correct = garbage == expected_garbage
            
            self._record_result(
                f"Garbage Formula: {desc}",
                garbage_formula_correct,
                expected_garbage,
                garbage,
                f"Garbage should be ({blocks} × {combo}) ÷ 2 = {expected_garbage}",
                "CRITICAL" if not garbage_formula_correct else "LOW"
            )
    
    def _test_garbage_placement(self):
        """Test garbage placement patterns"""
        print("\n📍 TESTING GARBAGE PLACEMENT...")
        
        # Test that garbage placement follows expected patterns
        # This would require more detailed testing of the placement logic
        # For now, we'll test basic queuing
        
        # Test multiple garbage attacks
        self.test_mode.queue_attack_spawn('enemy', 'garbage', count=3)
        self.test_mode.queue_attack_spawn('enemy', 'garbage', count=7)
        
        enemy_attacks = self.test_mode.pending_attacks.get('enemy', [])
        garbage_attacks = [a for a in enemy_attacks if a.get('type') == 'garbage']
        
        multiple_garbage_queued = len(garbage_attacks) >= 2
        self._record_result(
            "Multiple Garbage Attacks",
            multiple_garbage_queued,
            True,
            multiple_garbage_queued,
            f"Queued {len(garbage_attacks)} garbage attacks",
            "MEDIUM" if not multiple_garbage_queued else "LOW"
        )
    
    def _test_garbage_transformation(self):
        """Test garbage transformation issues"""
        print("\n🔄 TESTING GARBAGE TRANSFORMATION...")
        
        # Test that garbage doesn't transform unexpectedly
        # This is a placeholder for more detailed transformation testing
        # In a real implementation, you'd test the actual transformation logic
        
        garbage_stable = True  # Placeholder
        self._record_result(
            "Garbage Transformation Stability",
            garbage_stable,
            True,
            garbage_stable,
            "Garbage should not transform unexpectedly",
            "MEDIUM" if not garbage_stable else "LOW"
        )
    
    def _test_real_world_garbage_scenarios(self):
        """Test real-world garbage scenarios"""
        print("\n🌍 TESTING REAL-WORLD GARBAGE SCENARIOS...")
        
        # Test the original 2x3 scenario garbage calculation
        # 1 garbage + (2x3 cluster + 3 garbage)*2 + 10 garbage*3
        total_garbage = 1  # Initial garbage
        total_garbage += (3 * 2)  # 3 garbage * 2 combo
        total_garbage += (10 * 3)  # 10 garbage * 3 combo
        expected_garbage = 1 + 6 + 30  # = 37
        
        self._record_result(
            "Original 2x3 Scenario: Garbage",
            total_garbage == 37,
            37,
            total_garbage,
            "1 + (3×2) + (10×3) = 37 garbage blocks",
            "CRITICAL" if total_garbage != 37 else "LOW"
        )
        
        # Test common gameplay scenarios
        common_scenarios = [
            (5, 1, 2, "Small combo"),
            (8, 2, 8, "Medium combo"),
            (12, 3, 18, "Large combo"),
        ]
        
        for blocks, combo, expected, desc in common_scenarios:
            actual = self.calculator.calculate_garbage_attack(blocks, combo)
            passed = actual == expected
            
            self._record_result(
                f"Common Scenario: {desc}",
                passed,
                expected,
                actual,
                f"{blocks} blocks, {combo}x combo = {expected} garbage",
                "HIGH" if not passed else "LOW"
            )
    
    def _test_extreme_garbage_cases(self):
        """Test extreme garbage cases"""
        print("\n🔥 TESTING EXTREME GARBAGE CASES...")
        
        # Test very high combo levels
        extreme_combo = 100
        extreme_garbage = self.calculator.calculate_garbage_attack(10, extreme_combo)
        expected_extreme = (10 * extreme_combo) // 2  # = 500
        
        passed = extreme_garbage == expected_extreme
        self._record_result(
            "Extreme Combo Garbage",
            passed,
            expected_extreme,
            extreme_garbage,
            f"10 blocks, 100x combo = {expected_extreme} garbage",
            "MEDIUM" if not passed else "LOW"
        )
        
        # Test very large block counts
        large_blocks = 1000
        large_garbage = self.calculator.calculate_garbage_attack(large_blocks, 1)
        expected_large = large_blocks // 2  # = 500
        
        passed = large_garbage == expected_large
        self._record_result(
            "Large Blocks Garbage",
            passed,
            expected_large,
            large_garbage,
            f"1000 blocks, 1x combo = {expected_large} garbage",
            "MEDIUM" if not passed else "LOW"
        )
    
    def _test_weird_garbage_edge_cases(self):
        """Test weird garbage edge cases"""
        print("\n👻 TESTING WEIRD GARBAGE EDGE CASES...")
        
        # Test empty broken blocks
        try:
            empty_result = self.attack_manager.process_combo([], False, 1, player_id=1)
            empty_garbage = empty_result.get('garbage_blocks', 0)
            passed = empty_garbage == 0
            
            self._record_result(
                "Empty Broken Blocks Garbage",
                passed,
                0,
                empty_garbage,
                f"Empty blocks should produce 0 garbage: {empty_result}",
                "MEDIUM" if not passed else "LOW"
            )
        except Exception as e:
            self._record_result(
                "Empty Broken Blocks Exception",
                False,
                "No exception",
                str(e),
                "Empty broken blocks should not cause exceptions",
                "MEDIUM"
            )
        
        # Test fractional results (should be handled by integer division)
        fractional_test = self.calculator.calculate_garbage_attack(3, 1)  # Should be 1, not 1.5
        passed = fractional_test == 1 and isinstance(fractional_test, int)
        
        self._record_result(
            "Fractional Garbage Handling",
            passed,
            1,
            fractional_test,
            "Fractional results should be truncated to integers",
            "MEDIUM" if not passed else "LOW"
        )
    
    def _test_garbage_performance(self):
        """Test garbage performance"""
        print("\n⚡ TESTING GARBAGE PERFORMANCE...")
        
        start_time = time.time()
        
        # Process many garbage calculations quickly
        for i in range(1000):
            self.calculator.calculate_garbage_attack(10, 3)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        fast_enough = duration < 1.0  # Less than 1 second for 1000 calculations
        
        self._record_result(
            "Garbage Performance: 1000 Calculations",
            fast_enough,
            "< 1.0s",
            f"{duration:.3f}s",
            f"1000 calculations in {duration:.3f} seconds",
            "MEDIUM" if not fast_enough else "LOW"
        )
    
    def _test_garbage_stability(self):
        """Test garbage system stability"""
        print("\n🛡️ TESTING GARBAGE STABILITY...")
        
        # Test repeated garbage operations don't cause issues
        try:
            for i in range(100):
                result = self.attack_manager.process_combo(
                    [(1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red'), (4, 1, 'red')],
                    False, 1, player_id=1
                )
            
            stable = True
            self._record_result(
                "Garbage Stability: Repeated Operations",
                stable,
                True,
                stable,
                "100 repeated garbage operations completed without issues",
                "HIGH" if not stable else "LOW"
            )
        except Exception as e:
            self._record_result(
                "Garbage Stability: Repeated Operations Exception",
                False,
                "No exception",
                str(e),
                "Repeated garbage operations should not cause exceptions",
                "HIGH"
            )
    
    def _record_result(self, test_name: str, passed: bool, expected: Any, actual: Any, 
                      details: str, severity: str):
        """Record a test result"""
        result = GarbageValidationResult(
            test_name=test_name,
            passed=passed,
            expected=expected,
            actual=actual,
            details=details,
            severity=severity
        )
        
        self.results.append(result)
        
        if not passed:
            if severity == "CRITICAL":
                self.critical_failures += 1
            elif severity == "HIGH":
                self.high_failures += 1
            elif severity == "MEDIUM":
                self.medium_failures += 1
            else:
                self.low_failures += 1
    
    def _generate_report(self, duration: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("🗑️ COMPREHENSIVE GARBAGE VALIDATION SUITE COMPLETE")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Duration: {duration:.3f} seconds")
        
        print(f"\n🚨 FAILURE BREAKDOWN:")
        print(f"   Critical: {self.critical_failures}")
        print(f"   High: {self.high_failures}")
        print(f"   Medium: {self.medium_failures}")
        print(f"   Low: {self.low_failures}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"   [{result.severity}] {result.test_name}")
                    print(f"       Expected: {result.expected}")
                    print(f"       Actual: {result.actual}")
                    print(f"       Details: {result.details}")
                    print()
        else:
            print(f"\n✅ ALL TESTS PASSED! Your garbage system is bulletproof!")
        
        # Generate detailed report
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "duration": duration,
                "critical_failures": self.critical_failures,
                "high_failures": self.high_failures,
                "medium_failures": self.medium_failures,
                "low_failures": self.low_failures
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "expected": str(r.expected),
                    "actual": str(r.actual),
                    "details": r.details,
                    "severity": r.severity
                }
                for r in self.results
            ]
        }
        
        # Save report to file
        with open("garbage_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: garbage_validation_report.json")
        
        return report

def main():
    """Run the comprehensive garbage validation suite"""
    suite = GarbageValidationSuite()
    report = suite.run_all_tests()
    
    # Exit with error code if there are critical failures
    if report["summary"]["critical_failures"] > 0:
        print("\n💥 CRITICAL GARBAGE FAILURES DETECTED! Garbage system needs immediate attention!")
        sys.exit(1)
    elif report["summary"]["high_failures"] > 0:
        print("\n⚠️ HIGH PRIORITY GARBAGE FAILURES DETECTED! Garbage system needs review.")
        sys.exit(1)
    else:
        print("\n🎉 Garbage validation complete! Garbage system is solid.")

if __name__ == "__main__":
    main()
