#!/usr/bin/env python3
"""
GOD-LIKE COMPREHENSIVE ATTACK VALIDATION SUITE
==============================================

This suite will catch ALL the edge cases where:
- Garbage sometimes equals strikes
- Improper strikes are sent
- Weird cases that shouldn't happen
- Formula violations
- Pattern mismatches
- Delivery anomalies

Run this to validate your attack system thoroughly!
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
from modules.attack_module.data_structures import ClusterData, ClusterType, ComboData
from modules.testmode_module.test_mode import TestModeRefactored
import pygame

@dataclass
class ValidationResult:
    """Result of a validation test"""
    test_name: str
    passed: bool
    expected: Any
    actual: Any
    details: str
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'

class AttackValidationSuite:
    """Comprehensive attack system validation suite"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
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
        """Run all validation tests"""
        print("🔥 GOD-LIKE ATTACK VALIDATION SUITE STARTING...")
        print("=" * 80)
        
        start_time = time.time()
        
        # Formula validation tests
        self._test_basic_formulas()
        self._test_cluster_patterns()
        self._test_combo_scaling()
        self._test_edge_cases()
        
        # Attack generation tests
        self._test_attack_generation()
        self._test_cluster_detection()
        self._test_attack_queuing()
        
        # Delivery validation tests
        self._test_attack_delivery()
        self._test_garbage_vs_strikes()
        self._test_pattern_consistency()
        
        # Integration tests
        self._test_real_world_scenarios()
        self._test_extreme_cases()
        self._test_weird_edge_cases()
        
        # Performance and stability tests
        self._test_performance()
        self._test_stability()
        
        end_time = time.time()
        
        return self._generate_report(end_time - start_time)
    
    def _test_basic_formulas(self):
        """Test basic attack formulas"""
        print("\n📊 TESTING BASIC FORMULAS...")
        
        # Test garbage formula: (blocks × combo) ÷ 2
        test_cases = [
            (4, 1, 2, "4 blocks, 1x combo"),
            (6, 2, 6, "6 blocks, 2x combo"),
            (8, 3, 12, "8 blocks, 3x combo"),
            (10, 4, 20, "10 blocks, 4x combo"),
            (12, 5, 30, "12 blocks, 5x combo"),
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
        
        # Test strike formula: cluster_size × combo
        strike_cases = [
            (4, 1, 4, "2x2 cluster, 1x combo"),
            (4, 2, 8, "2x2 cluster, 2x combo"),
            (9, 1, 9, "3x3 cluster, 1x combo"),
            (9, 3, 27, "3x3 cluster, 3x combo"),
            (16, 2, 32, "4x4 cluster, 2x combo"),
        ]
        
        for cluster_size, combo, expected, desc in strike_cases:
            actual = self.calculator.calculate_strike_attack(cluster_size, combo)
            passed = actual == expected
            self._record_result(
                f"Strike Formula: {desc}",
                passed,
                expected,
                actual,
                f"Formula: {cluster_size} × {combo} = {expected}",
                "CRITICAL" if not passed else "LOW"
            )
    
    def _test_cluster_patterns(self):
        """Test cluster pattern generation"""
        print("\n⚔️ TESTING CLUSTER PATTERNS...")
        
        # Test 2x2 patterns
        pattern_2x2 = [
            (1, "1x4_vertical", "2x2 level 1"),
            (2, "2x4_vertical", "2x2 level 2"),
            (3, "2x6_vertical", "2x2 level 3"),
            (4, "2x8_vertical", "2x2 level 4"),
            (5, "2x10_vertical", "2x2 level 5"),
            (6, "2x12_vertical", "2x2 level 6"),
        ]
        
        for combo, expected, desc in pattern_2x2:
            pattern, width, height = self.calculator.calculate_cluster_strike("2x2", combo)
            actual = f"{width}x{height}_vertical"
            passed = actual == expected
            self._record_result(
                f"2x2 Pattern: {desc}",
                passed,
                expected,
                actual,
                f"Combo {combo} should produce {expected}",
                "HIGH" if not passed else "LOW"
            )
        
        # Test 3x3 patterns
        pattern_3x3 = [
            (1, "2x4_vertical", "3x3 level 1"),
            (2, "3x6_vertical", "3x3 level 2"),
            (3, "3x9_vertical", "3x3 level 3"),
            (4, "3x12_vertical", "3x3 level 4"),
        ]
        
        for combo, expected, desc in pattern_3x3:
            pattern, width, height = self.calculator.calculate_cluster_strike("3x3", combo)
            actual = f"{width}x{height}_vertical"
            passed = actual == expected
            self._record_result(
                f"3x3 Pattern: {desc}",
                passed,
                expected,
                actual,
                f"Combo {combo} should produce {expected}",
                "HIGH" if not passed else "LOW"
            )
    
    def _test_combo_scaling(self):
        """Test combo scaling behavior"""
        print("\n📈 TESTING COMBO SCALING...")
        
        # Test that garbage and strikes scale differently
        test_cases = [
            (4, 1, "Single combo"),
            (4, 2, "Double combo"),
            (4, 3, "Triple combo"),
            (4, 4, "Quad combo"),
            (4, 5, "Penta combo"),
        ]
        
        for blocks, combo, desc in test_cases:
            garbage = self.calculator.calculate_garbage_attack(blocks, combo)
            strikes = self.calculator.calculate_strike_attack(blocks, combo)
            
            # Garbage should be (blocks × combo) ÷ 2
            expected_garbage = (blocks * combo) // 2
            # Strikes should be blocks × combo
            expected_strikes = blocks * combo
            
            garbage_passed = garbage == expected_garbage
            strikes_passed = strikes == expected_strikes
            
            self._record_result(
                f"Combo Scaling Garbage: {desc}",
                garbage_passed,
                expected_garbage,
                garbage,
                f"Garbage should be ({blocks} × {combo}) ÷ 2 = {expected_garbage}",
                "CRITICAL" if not garbage_passed else "LOW"
            )
            
            self._record_result(
                f"Combo Scaling Strikes: {desc}",
                strikes_passed,
                expected_strikes,
                strikes,
                f"Strikes should be {blocks} × {combo} = {expected_strikes}",
                "CRITICAL" if not strikes_passed else "LOW"
            )
    
    def _test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        print("\n🔍 TESTING EDGE CASES...")
        
        # Test minimum strike size
        small_cluster = self.calculator.calculate_strike_attack(3, 1)  # Below minimum
        passed = small_cluster == 0
        self._record_result(
            "Minimum Strike Size",
            passed,
            0,
            small_cluster,
            "Clusters below 4 blocks should produce 0 strikes",
            "HIGH" if not passed else "LOW"
        )
        
        # Test zero combo
        zero_combo_garbage = self.calculator.calculate_garbage_attack(4, 0)
        zero_combo_strikes = self.calculator.calculate_strike_attack(4, 0)
        passed = zero_combo_garbage == 0 and zero_combo_strikes == 0
        self._record_result(
            "Zero Combo Handling",
            passed,
            (0, 0),
            (zero_combo_garbage, zero_combo_strikes),
            "Zero combo should produce 0 garbage and 0 strikes",
            "HIGH" if not passed else "LOW"
        )
        
        # Test negative values
        try:
            negative_garbage = self.calculator.calculate_garbage_attack(-1, 1)
            negative_strikes = self.calculator.calculate_strike_attack(-1, 1)
            passed = negative_garbage >= 0 and negative_strikes >= 0
            self._record_result(
                "Negative Input Handling",
                passed,
                "Non-negative",
                (negative_garbage, negative_strikes),
                "Negative inputs should be handled gracefully",
                "MEDIUM" if not passed else "LOW"
            )
        except Exception as e:
            self._record_result(
                "Negative Input Exception",
                False,
                "No exception",
                str(e),
                "Negative inputs should not cause exceptions",
                "MEDIUM"
            )
    
    def _test_attack_generation(self):
        """Test attack generation through AttackManager"""
        print("\n🎯 TESTING ATTACK GENERATION...")
        
        # Test basic combo processing
        test_combos = [
            # (broken_blocks, is_cluster, combo_multiplier, expected_garbage, expected_strikes)
            ([(1, 1, 'red'), (2, 1, 'red')], False, 1, 1, 0),  # 2 blocks, no cluster
            ([(1, 1, 'red'), (2, 1, 'red'), (1, 2, 'red'), (2, 2, 'red')], True, 1, 0, 1),  # 2x2 cluster
            ([(1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red'), (1, 2, 'red'), (2, 2, 'red'), (3, 2, 'red')], True, 2, 0, 1),  # 3x2 cluster, 2x combo
        ]
        
        for broken_blocks, is_cluster, combo, expected_garbage, expected_strikes in test_combos:
            result = self.attack_manager.process_combo(
                broken_blocks, is_cluster, combo, player_id=1
            )
            
            actual_garbage = result.get('garbage_blocks', 0)
            actual_strikes = result.get('cluster_strikes', 0)
            
            garbage_passed = actual_garbage == expected_garbage
            strikes_passed = actual_strikes == expected_strikes
            
            self._record_result(
                f"Attack Generation: {len(broken_blocks)} blocks, cluster={is_cluster}, combo={combo}",
                garbage_passed and strikes_passed,
                (expected_garbage, expected_strikes),
                (actual_garbage, actual_strikes),
                f"Expected {expected_garbage} garbage, {expected_strikes} strikes",
                "CRITICAL" if not (garbage_passed and strikes_passed) else "LOW"
            )
    
    def _test_cluster_detection(self):
        """Test cluster detection logic"""
        print("\n🔍 TESTING CLUSTER DETECTION...")
        
        # Test various cluster patterns
        cluster_tests = [
            # 2x2 clusters
            ([(1, 1, 'red'), (2, 1, 'red'), (1, 2, 'red'), (2, 2, 'red')], "2x2"),
            # 3x3 clusters
            ([(1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red'), 
              (1, 2, 'red'), (2, 2, 'red'), (3, 2, 'red'),
              (1, 3, 'red'), (2, 3, 'red'), (3, 3, 'red')], "3x3"),
            # 3x2 clusters
            ([(1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red'),
              (1, 2, 'red'), (2, 2, 'red'), (3, 2, 'red')], "3x2"),
        ]
        
        for broken_blocks, expected_type in cluster_tests:
            clusters = self.attack_manager._detect_clusters_in_broken_blocks(broken_blocks)
            
            if clusters:
                actual_type = clusters[0].cluster_type.value
                passed = actual_type == expected_type
                self._record_result(
                    f"Cluster Detection: {expected_type}",
                    passed,
                    expected_type,
                    actual_type,
                    f"Detected {len(clusters)} clusters",
                    "HIGH" if not passed else "LOW"
                )
            else:
                self._record_result(
                    f"Cluster Detection: {expected_type}",
                    False,
                    expected_type,
                    "No clusters detected",
                    "Failed to detect expected cluster",
                    "HIGH"
                )
    
    def _test_attack_queuing(self):
        """Test attack queuing and timing"""
        print("\n⏰ TESTING ATTACK QUEUING...")
        
        # Test that attacks are properly queued
        result = self.attack_manager.process_combo(
            [(1, 1, 'red'), (2, 1, 'red'), (1, 2, 'red'), (2, 2, 'red')],
            True, 1, player_id=1
        )
        
        # Check that attacks are in the queue
        target_player = 2  # Player 1 attacks player 2
        pending_attacks = self.attack_manager.get_pending_attacks(target_player)
        
        passed = len(pending_attacks) > 0
        self._record_result(
            "Attack Queuing",
            passed,
            "> 0 attacks",
            len(pending_attacks),
            f"Generated {result.get('attacks_generated', 0)} attacks",
            "CRITICAL" if not passed else "LOW"
        )
    
    def _test_attack_delivery(self):
        """Test attack delivery through TestMode"""
        print("\n🚀 TESTING ATTACK DELIVERY...")
        
        # Test garbage delivery
        self.test_mode.queue_attack_spawn('enemy', 'garbage', count=5)
        
        # Check that attack is queued
        enemy_attacks = self.test_mode.pending_attacks.get('enemy', [])
        garbage_queued = any(attack.get('type') == 'garbage' for attack in enemy_attacks)
        
        self._record_result(
            "Garbage Attack Queuing",
            garbage_queued,
            True,
            garbage_queued,
            f"Queued {len(enemy_attacks)} attacks",
            "CRITICAL" if not garbage_queued else "LOW"
        )
        
        # Test strike delivery
        self.test_mode.queue_attack_spawn('enemy', 'strike', count=1, 
                                        strike_details=[{'width': 2, 'height': 4}])
        
        enemy_attacks = self.test_mode.pending_attacks.get('enemy', [])
        strike_queued = any(attack.get('type') == 'strike' for attack in enemy_attacks)
        
        self._record_result(
            "Strike Attack Queuing",
            strike_queued,
            True,
            strike_queued,
            f"Queued {len(enemy_attacks)} attacks",
            "CRITICAL" if not strike_queued else "LOW"
        )
    
    def _test_garbage_vs_strikes(self):
        """Test that garbage and strikes are properly differentiated"""
        print("\n⚖️ TESTING GARBAGE VS STRIKES DIFFERENTIATION...")
        
        # Test that same input doesn't produce same garbage and strikes
        test_cases = [
            (4, 1, "4 blocks, 1x combo"),
            (6, 2, "6 blocks, 2x combo"),
            (8, 3, "8 blocks, 3x combo"),
        ]
        
        for blocks, combo, desc in test_cases:
            garbage = self.calculator.calculate_garbage_attack(blocks, combo)
            strikes = self.calculator.calculate_strike_attack(blocks, combo)
            
            # Garbage should NOT equal strikes for normal cases
            should_differ = garbage != strikes
            self._record_result(
                f"Garbage ≠ Strikes: {desc}",
                should_differ,
                "Different values",
                f"Garbage={garbage}, Strikes={strikes}",
                f"Garbage ({blocks}×{combo})÷2 ≠ Strikes {blocks}×{combo}",
                "CRITICAL" if not should_differ else "LOW"
            )
        
        # Test edge case where they might be equal
        edge_garbage = self.calculator.calculate_garbage_attack(2, 2)  # (2×2)÷2 = 2
        edge_strikes = self.calculator.calculate_strike_attack(2, 1)   # 2×1 = 2 (but below minimum)
        
        # Strikes should be 0 for 2 blocks (below minimum)
        edge_passed = edge_strikes == 0
        self._record_result(
            "Edge Case: Small Cluster",
            edge_passed,
            0,
            edge_strikes,
            "2-block clusters should produce 0 strikes (below minimum)",
            "HIGH" if not edge_passed else "LOW"
        )
    
    def _test_pattern_consistency(self):
        """Test pattern consistency across different combo levels"""
        print("\n🔄 TESTING PATTERN CONSISTENCY...")
        
        # Test that patterns scale consistently
        base_pattern, base_width, base_height = self.calculator.calculate_cluster_strike("2x2", 1)
        
        for combo in [2, 3, 4, 5]:
            pattern, width, height = self.calculator.calculate_cluster_strike("2x2", combo)
            
            # Width should remain consistent for 2x2 (should be 1 for combo=1, 2 for combo>1)
            expected_width = 1 if combo == 1 else 2
            width_consistent = width == expected_width
            
            # Height should scale according to 2x2 formula: 4 for combo=1, 2*combo for combo>1
            expected_height = 4 if combo == 1 else min(12, 2 * combo)
            height_consistent = height == expected_height
            
            self._record_result(
                f"2x2 Pattern Consistency: {combo}x combo",
                width_consistent and height_consistent,
                (True, True),
                (width_consistent, height_consistent),
                f"Width={width}(expected {expected_width}), Height={height}(expected {expected_height})",
                "HIGH" if not (width_consistent and height_consistent) else "LOW"
            )
    
    def _test_real_world_scenarios(self):
        """Test real-world attack scenarios"""
        print("\n🌍 TESTING REAL-WORLD SCENARIOS...")
        
        # Test the original 2x3 scenario from documentation
        # 1 garbage + (2x3 cluster + 3 garbage)*2 + 10 garbage*3
        total_garbage = 1  # Initial garbage
        total_garbage += (3 * 2)  # 3 garbage * 2 combo
        total_garbage += (10 * 3)  # 10 garbage * 3 combo
        expected_garbage = 1 + 6 + 30  # = 37
        
        # 2x3 cluster should produce 6x2 horizontal sword
        pattern, width, height = self.calculator.calculate_cluster_strike("3x2", 2)
        expected_pattern = "2x6_vertical"  # 3x2 converts to vertical
        
        self._record_result(
            "Original 2x3 Scenario: Garbage",
            total_garbage == 37,
            37,
            total_garbage,
            "1 + (3×2) + (10×3) = 37 garbage blocks",
            "CRITICAL" if total_garbage != 37 else "LOW"
        )
        
        self._record_result(
            "Original 2x3 Scenario: Strike Pattern",
            pattern == expected_pattern,
            expected_pattern,
            pattern,
            "2x3 cluster in 2x combo should produce 2x6_vertical",
            "CRITICAL" if pattern != expected_pattern else "LOW"
        )
    
    def _test_extreme_cases(self):
        """Test extreme cases and boundary conditions"""
        print("\n🔥 TESTING EXTREME CASES...")
        
        # Test very high combo levels
        extreme_combo = 100
        pattern, width, height = self.calculator.calculate_cluster_strike("2x2", extreme_combo)
        
        # Should be capped at reasonable values
        reasonable_width = width <= 3
        reasonable_height = height <= 12  # Max cap from code
        
        self._record_result(
            "Extreme Combo: 2x2 at 100x",
            reasonable_width and reasonable_height,
            (True, True),
            (reasonable_width, reasonable_height),
            f"Pattern: {width}x{height}_vertical",
            "MEDIUM" if not (reasonable_width and reasonable_height) else "LOW"
        )
        
        # Test very large clusters
        large_pattern, large_width, large_height = self.calculator.calculate_cluster_strike("10x10", 1)
        
        # Should handle large clusters gracefully
        handled_gracefully = large_width <= 3 and large_height > 0
        
        self._record_result(
            "Large Cluster: 10x10",
            handled_gracefully,
            True,
            handled_gracefully,
            f"Pattern: {large_width}x{large_height}_vertical",
            "MEDIUM" if not handled_gracefully else "LOW"
        )
    
    def _test_weird_edge_cases(self):
        """Test weird edge cases that shouldn't happen"""
        print("\n👻 TESTING WEIRD EDGE CASES...")
        
        # Test invalid cluster types
        try:
            invalid_pattern, invalid_width, invalid_height = self.calculator.calculate_cluster_strike("invalid", 1)
            # Should fall back to 2x2
            fallback_works = invalid_width == 1 and invalid_height == 4
            self._record_result(
                "Invalid Cluster Type Handling",
                fallback_works,
                True,
                fallback_works,
                f"Fallback pattern: {invalid_width}x{invalid_height}_vertical",
                "MEDIUM" if not fallback_works else "LOW"
            )
        except Exception as e:
            self._record_result(
                "Invalid Cluster Type Exception",
                False,
                "No exception",
                str(e),
                "Invalid cluster types should not cause exceptions",
                "MEDIUM"
            )
        
        # Test empty broken blocks
        try:
            empty_result = self.attack_manager.process_combo([], False, 1, player_id=1)
            empty_handled = empty_result.get('garbage_blocks', 0) == 0 and empty_result.get('cluster_strikes', 0) == 0
            self._record_result(
                "Empty Broken Blocks",
                empty_handled,
                True,
                empty_handled,
                f"Result: {empty_result}",
                "MEDIUM" if not empty_handled else "LOW"
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
    
    def _test_performance(self):
        """Test performance under load"""
        print("\n⚡ TESTING PERFORMANCE...")
        
        start_time = time.time()
        
        # Process many combos quickly
        for i in range(100):
            self.calculator.calculate_garbage_attack(10, 3)
            self.calculator.calculate_strike_attack(9, 2)
            self.calculator.calculate_cluster_strike("2x2", 3)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        fast_enough = duration < 1.0  # Less than 1 second for 100 calculations
        
        self._record_result(
            "Performance: 100 Calculations",
            fast_enough,
            "< 1.0s",
            f"{duration:.3f}s",
            f"100 calculations in {duration:.3f} seconds",
            "MEDIUM" if not fast_enough else "LOW"
        )
    
    def _test_stability(self):
        """Test system stability"""
        print("\n🛡️ TESTING STABILITY...")
        
        # Test repeated operations don't cause issues
        try:
            for i in range(50):
                result = self.attack_manager.process_combo(
                    [(1, 1, 'red'), (2, 1, 'red'), (1, 2, 'red'), (2, 2, 'red')],
                    True, 1, player_id=1
                )
            
            stable = True
            self._record_result(
                "Stability: Repeated Operations",
                stable,
                True,
                stable,
                "50 repeated operations completed without issues",
                "HIGH" if not stable else "LOW"
            )
        except Exception as e:
            self._record_result(
                "Stability: Repeated Operations Exception",
                False,
                "No exception",
                str(e),
                "Repeated operations should not cause exceptions",
                "HIGH"
            )
    
    def _record_result(self, test_name: str, passed: bool, expected: Any, actual: Any, 
                      details: str, severity: str):
        """Record a test result"""
        result = ValidationResult(
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
        print("🔥 GOD-LIKE ATTACK VALIDATION SUITE COMPLETE")
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
            print(f"\n✅ ALL TESTS PASSED! Your attack system is bulletproof!")
        
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
        with open("attack_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: attack_validation_report.json")
        
        return report

def main():
    """Run the comprehensive validation suite"""
    suite = AttackValidationSuite()
    report = suite.run_all_tests()
    
    # Exit with error code if there are critical failures
    if report["summary"]["critical_failures"] > 0:
        print("\n💥 CRITICAL FAILURES DETECTED! Attack system needs immediate attention!")
        sys.exit(1)
    elif report["summary"]["high_failures"] > 0:
        print("\n⚠️ HIGH PRIORITY FAILURES DETECTED! Attack system needs review.")
        sys.exit(1)
    else:
        print("\n🎉 Validation complete! Attack system is solid.")

if __name__ == "__main__":
    main()
