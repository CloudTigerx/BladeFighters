#!/usr/bin/env python3
"""
SIMPLE PUZZLE MODULE DIAGNOSTIC
===============================

Quick diagnostic for the major puzzle issues without complex imports.
"""

import os
import sys

def check_file_exists(filepath):
    """Check if a file exists and is readable"""
    return os.path.exists(filepath) and os.access(filepath, os.R_OK)

def analyze_piece_movement():
    """Analyze piece movement issues"""
    print("🔄 ANALYZING PIECE MOVEMENT...")
    
    issues = []
    
    # Check piece_movement.py
    if check_file_exists("core/piece_movement.py"):
        with open("core/piece_movement.py", "r") as f:
            content = f.read()
            
        # Check flip cooldown
        if "flip_cooldown = 0.1" in content:
            issues.append("Flip cooldown is 0.1 seconds - may be too high")
        
        # Check flip validation
        if "is_valid_position" not in content:
            issues.append("Missing position validation in flip logic")
        
        # Check wall kick interference
        if "wall_kick_count" in content and "flip" in content:
            issues.append("Wall kick tracking may interfere with flips")
    else:
        issues.append("piece_movement.py not found")
    
    return issues

def analyze_bounce_effect():
    """Analyze bounce effect issues"""
    print("🏀 ANALYZING BOUNCE EFFECT...")
    
    issues = []
    
    # Check puzzle_module.py
    if check_file_exists("core/puzzle_module.py"):
        with open("core/puzzle_module.py", "r") as f:
            content = f.read()
            
        # Check sliding method
        if "_handle_piece_sliding" not in content:
            issues.append("Missing _handle_piece_sliding method")
        else:
            # Check bounce prevention
            if "main_piece" not in content or "piece_position" not in content:
                issues.append("Missing bounce prevention logic")
            
            # Check separation protection
            if "disable_visual_falling_during_separation" not in content:
                issues.append("Missing separation protection")
    else:
        issues.append("puzzle_module.py not found")
    
    return issues

def analyze_transformation():
    """Analyze transformation issues"""
    print("🔄 ANALYZING TRANSFORMATION...")
    
    issues = []
    
    # Check test_mode.py
    if check_file_exists("modules/testmode_module/test_mode.py"):
        with open("modules/testmode_module/test_mode.py", "r") as f:
            content = f.read()
            
        # Check transformation methods
        required_methods = [
            "_process_garbage_transformations",
            "_track_garbage_landings",
            "_apply_garbage_finalization"
        ]
        
        for method in required_methods:
            if method not in content:
                issues.append(f"Missing method: {method}")
        
        # Check tracking
        if "garbage_block_brightness" not in content:
            issues.append("Missing garbage block tracking")
    else:
        issues.append("test_mode.py not found")
    
    return issues

def analyze_stuttering():
    """Analyze piece stuttering issues"""
    print("⚡ ANALYZING PIECE STUTTERING...")
    
    issues = []
    
    # Check basic_physics.py
    if check_file_exists("core/basic_physics.py"):
        with open("core/basic_physics.py", "r") as f:
            content = f.read()
            
        # Check separation logic
        if "should_pieces_separate" not in content:
            issues.append("Missing should_pieces_separate method")
        else:
            if "grid_height" not in content:
                issues.append("Missing grid boundary checks")
            
            if "collide" not in content.lower():
                issues.append("Missing collision detection")
    else:
        issues.append("basic_physics.py not found")
    
    # Check puzzle_module.py for stall detection
    if check_file_exists("core/puzzle_module.py"):
        with open("core/puzzle_module.py", "r") as f:
            content = f.read()
            
        if "stall" not in content.lower():
            issues.append("Missing stall detection logic")
        
        if "sub_position" not in content:
            issues.append("Missing sub-position handling")
    
    return issues

def analyze_attack_accuracy():
    """Analyze attack accuracy issues"""
    print("🎯 ANALYZING ATTACK ACCURACY...")
    
    issues = []
    
    # Check attack_calculator.py
    if check_file_exists("modules/attack_module/attack_calculator.py"):
        with open("modules/attack_module/attack_calculator.py", "r") as f:
            content = f.read()
            
        # Check formulas
        if "calculate_garbage_attack" not in content:
            issues.append("Missing garbage attack calculation")
        
        if "calculate_strike_attack" not in content:
            issues.append("Missing strike attack calculation")
        
        # Check for potential issues
        if "// 2" in content and "×" in content:
            # This is actually correct - garbage formula is (blocks × combo) ÷ 2
            pass
        
        if "cluster_size" in content and "chain_multiplier" in content:
            # This is actually correct - strike formula is cluster_size × combo
            pass
    else:
        issues.append("attack_calculator.py not found")
    
    return issues

def main():
    """Run comprehensive diagnostic"""
    print("🔍 SIMPLE PUZZLE MODULE DIAGNOSTIC")
    print("=" * 60)
    
    all_issues = {}
    
    # Run all diagnostics
    all_issues['piece_movement'] = analyze_piece_movement()
    all_issues['bounce_effect'] = analyze_bounce_effect()
    all_issues['transformation'] = analyze_transformation()
    all_issues['stuttering'] = analyze_stuttering()
    all_issues['attack_accuracy'] = analyze_attack_accuracy()
    
    # Report results
    print("\n🎯 DIAGNOSTIC RESULTS:")
    print("=" * 60)
    
    total_issues = 0
    for category, issues in all_issues.items():
        if issues:
            print(f"❌ {category.replace('_', ' ').title()}:")
            for issue in issues:
                print(f"   - {issue}")
            total_issues += len(issues)
        else:
            print(f"✅ {category.replace('_', ' ').title()}: No issues found")
    
    print(f"\n📊 SUMMARY: {total_issues} issues found")
    
    if total_issues > 0:
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("=" * 60)
        print("1. Fix piece flip cooldown in core/piece_movement.py")
        print("2. Improve bounce prevention in core/puzzle_module.py")
        print("3. Check transformation methods in modules/testmode_module/test_mode.py")
        print("4. Fix separation logic in core/basic_physics.py")
        print("5. Verify attack formulas in modules/attack_module/attack_calculator.py")
    
    return total_issues

if __name__ == "__main__":
    main()
