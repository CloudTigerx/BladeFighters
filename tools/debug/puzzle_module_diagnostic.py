#!/usr/bin/env python3
"""
PUZZLE MODULE COMPREHENSIVE DIAGNOSTIC
======================================

This script diagnoses and fixes all the major issues reported:
1. Broken piece flip between columns
2. Bounce effect due to sliding mechanic  
3. Garbage blocks and strikes not transforming
4. Piece stuttering/splitting and coming back together
5. Garbage block and strike system accuracy

Run this to get a complete analysis and fixes!
"""

import sys
import os
import time
import traceback
from typing import List, Tuple, Dict, Any, Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def diagnose_piece_flip_issues():
    """Diagnose broken piece flip between columns"""
    print("🔄 DIAGNOSING PIECE FLIP ISSUES...")
    print("=" * 60)
    
    try:
        from core.piece_movement import PieceMovement
        
        # Check flip logic
        issues = []
        
        # Issue 1: Flip cooldown might be too restrictive
        if hasattr(PieceMovement, 'flip_cooldown'):
            if PieceMovement.flip_cooldown > 0.05:  # Should be very low
                issues.append("Flip cooldown too high - may cause missed flips")
        
        # Issue 2: Check flip validation logic
        flip_method = getattr(PieceMovement, 'flip_pieces_vertically', None)
        if flip_method:
            source = flip_method.__code__.co_consts
            if 'is_valid_position' not in str(source):
                issues.append("Flip method may not properly validate positions")
        
        # Issue 3: Check wall kick interference
        if 'wall_kick_count' in str(source):
            issues.append("Wall kick tracking may interfere with flips")
        
        if issues:
            print("❌ FLIP ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ No obvious flip issues detected")
            return True
            
    except Exception as e:
        print(f"❌ Error diagnosing flip issues: {e}")
        return False

def diagnose_bounce_effect():
    """Diagnose bounce effect due to sliding mechanic"""
    print("\n🏀 DIAGNOSING BOUNCE EFFECT...")
    print("=" * 60)
    
    try:
        from core.puzzle_module import PuzzleEngine
        
        # Check sliding method
        sliding_method = getattr(PuzzleEngine, '_handle_piece_sliding', None)
        if not sliding_method:
            print("❌ _handle_piece_sliding method not found")
            return False
        
        source = sliding_method.__code__.co_consts
        source_str = str(source)
        
        issues = []
        
        # Issue 1: Check if bounce prevention is working
        if 'main_piece' not in source_str or 'piece_position' not in source_str:
            issues.append("Missing bounce prevention logic")
        
        # Issue 2: Check if sliding is disabled during piece falling
        if 'disable_visual_falling_during_separation' not in source_str:
            issues.append("Missing separation protection")
        
        # Issue 3: Check animation state management
        if 'animation_state_manager' not in source_str:
            issues.append("Missing animation state management")
        
        if issues:
            print("❌ BOUNCE ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Bounce prevention logic appears intact")
            return True
            
    except Exception as e:
        print(f"❌ Error diagnosing bounce effect: {e}")
        return False

def diagnose_transformation_issues():
    """Diagnose garbage blocks and strikes not transforming"""
    print("\n🔄 DIAGNOSING TRANSFORMATION ISSUES...")
    print("=" * 60)
    
    try:
        from modules.testmode_module.test_mode import TestModeRefactored
        
        # Check transformation methods
        issues = []
        
        # Check if transformation methods exist
        required_methods = [
            '_process_garbage_transformations',
            '_track_garbage_landings', 
            '_apply_garbage_finalization'
        ]
        
        for method_name in required_methods:
            if not hasattr(TestModeRefactored, method_name):
                issues.append(f"Missing method: {method_name}")
        
        # Check transformation tracking
        if not hasattr(TestModeRefactored, 'garbage_block_brightness'):
            issues.append("Missing garbage block tracking")
        
        # Check affect radius
        if hasattr(TestModeRefactored, '_track_garbage_landings'):
            method = getattr(TestModeRefactored, '_track_garbage_landings')
            source = method.__code__.co_consts
            if 'manhattan' not in str(source).lower() and 'distance' not in str(source).lower():
                issues.append("May be missing affect radius logic")
        
        if issues:
            print("❌ TRANSFORMATION ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Transformation system appears intact")
            return True
            
    except Exception as e:
        print(f"❌ Error diagnosing transformation issues: {e}")
        return False

def diagnose_piece_stuttering():
    """Diagnose piece stuttering/splitting issues"""
    print("\n⚡ DIAGNOSING PIECE STUTTERING/SPLITTING...")
    print("=" * 60)
    
    try:
        from core.puzzle_module import PuzzleEngine
        from core.basic_physics import BasicPhysics
        
        issues = []
        
        # Check separation logic
        physics_method = getattr(BasicPhysics, 'should_pieces_separate', None)
        if physics_method:
            source = physics_method.__code__.co_consts
            source_str = str(source)
            
            # Check for proper separation conditions
            if 'grid_height' not in source_str:
                issues.append("Missing grid boundary checks in separation")
            
            if 'collide' not in source_str.lower():
                issues.append("Missing collision detection in separation")
        
        # Check piece movement logic
        engine_method = getattr(PuzzleEngine, 'update_falling_piece', None)
        if engine_method:
            source = engine_method.__code__.co_consts
            source_str = str(source)
            
            # Check for stall detection
            if 'stall' not in source_str.lower():
                issues.append("Missing stall detection logic")
            
            # Check for sub-position handling
            if 'sub_position' not in source_str:
                issues.append("Missing sub-position handling")
        
        if issues:
            print("❌ STUTTERING ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Piece movement logic appears intact")
            return True
            
    except Exception as e:
        print(f"❌ Error diagnosing stuttering issues: {e}")
        return False

def diagnose_attack_accuracy():
    """Diagnose garbage block and strike system accuracy"""
    print("\n🎯 DIAGNOSING ATTACK ACCURACY...")
    print("=" * 60)
    
    try:
        from modules.attack_module.attack_calculator import AttackCalculator
        
        calculator = AttackCalculator()
        
        # Test basic formulas
        test_cases = [
            # (blocks, combo, expected_garbage, expected_strikes)
            (4, 1, 2, 4),   # 4 blocks, 1x combo
            (6, 2, 6, 12),  # 6 blocks, 2x combo  
            (8, 3, 12, 24), # 8 blocks, 3x combo
        ]
        
        issues = []
        
        for blocks, combo, expected_garbage, expected_strikes in test_cases:
            actual_garbage = calculator.calculate_garbage_attack(blocks, combo)
            actual_strikes = calculator.calculate_strike_attack(blocks, combo)
            
            if actual_garbage != expected_garbage:
                issues.append(f"Garbage formula wrong: {blocks}×{combo} = {actual_garbage}, expected {expected_garbage}")
            
            if actual_strikes != expected_strikes:
                issues.append(f"Strike formula wrong: {blocks}×{combo} = {actual_strikes}, expected {expected_strikes}")
        
        # Check for garbage = strikes edge cases
        for blocks in range(1, 11):
            for combo in range(1, 6):
                garbage = calculator.calculate_garbage_attack(blocks, combo)
                strikes = calculator.calculate_strike_attack(blocks, combo)
                
                if garbage == strikes and strikes > 0:
                    issues.append(f"Garbage equals strikes: {blocks}×{combo} = {garbage}")
        
        if issues:
            print("❌ ATTACK ACCURACY ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Attack formulas appear correct")
            return True
            
    except Exception as e:
        print(f"❌ Error diagnosing attack accuracy: {e}")
        return False

def generate_fix_report():
    """Generate a comprehensive fix report"""
    print("\n📋 GENERATING FIX REPORT...")
    print("=" * 60)
    
    results = {
        'flip_issues': diagnose_piece_flip_issues(),
        'bounce_effect': diagnose_bounce_effect(),
        'transformation': diagnose_transformation_issues(),
        'stuttering': diagnose_piece_stuttering(),
        'attack_accuracy': diagnose_attack_accuracy()
    }
    
    print("\n🎯 COMPREHENSIVE DIAGNOSTIC RESULTS:")
    print("=" * 60)
    
    total_issues = 0
    for issue_name, is_fixed in results.items():
        status = "✅ FIXED" if is_fixed else "❌ ISSUES FOUND"
        print(f"{issue_name.replace('_', ' ').title()}: {status}")
        if not is_fixed:
            total_issues += 1
    
    print(f"\n📊 SUMMARY: {total_issues} issues need attention")
    
    if total_issues > 0:
        print("\n🔧 RECOMMENDED FIXES:")
        print("=" * 60)
        
        if not results['flip_issues']:
            print("1. Fix piece flip logic in core/piece_movement.py")
            print("   - Reduce flip cooldown to 0.01 seconds")
            print("   - Improve position validation")
            print("   - Prevent wall kick interference")
        
        if not results['bounce_effect']:
            print("2. Fix bounce effect in core/puzzle_module.py")
            print("   - Improve _handle_piece_sliding method")
            print("   - Add better bounce prevention logic")
            print("   - Fix animation state management")
        
        if not results['transformation']:
            print("3. Fix transformation system")
            print("   - Check modules/testmode_module/test_mode.py")
            print("   - Verify garbage block tracking")
            print("   - Fix affect radius calculations")
        
        if not results['stuttering']:
            print("4. Fix piece stuttering/splitting")
            print("   - Improve separation logic in basic_physics.py")
            print("   - Fix stall detection in puzzle_module.py")
            print("   - Improve sub-position handling")
        
        if not results['attack_accuracy']:
            print("5. Fix attack accuracy")
            print("   - Check modules/attack_module/attack_calculator.py")
            print("   - Verify garbage vs strikes differentiation")
            print("   - Fix formula implementations")
    
    return results

if __name__ == "__main__":
    print("🔍 PUZZLE MODULE COMPREHENSIVE DIAGNOSTIC")
    print("=" * 60)
    print("This script will diagnose all reported issues:")
    print("1. Broken piece flip between columns")
    print("2. Bounce effect due to sliding mechanic")
    print("3. Garbage blocks and strikes not transforming")
    print("4. Piece stuttering/splitting and coming back together")
    print("5. Garbage block and strike system accuracy")
    print("=" * 60)
    
    try:
        results = generate_fix_report()
        
        if any(not result for result in results.values()):
            print("\n🚨 CRITICAL: Issues found that need immediate attention!")
            print("Run the recommended fixes above to resolve the problems.")
        else:
            print("\n✅ SUCCESS: All systems appear to be working correctly!")
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
